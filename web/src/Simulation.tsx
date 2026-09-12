import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { AGENTS, REDBEARD, SCENARIOS, type Entry, type Mode, type Scenario, type Step } from './scenario'
import { latestAgentInteractions, type AgentDialogue } from './agent-profile'
import { translate } from './pt'
import { connectLive, startLiveMission, type LiveSnapshot } from './live'
import { BannerPrivacidade, PortaoConta } from './Portao'
import { lerConfig } from './conta'

type Lang = 'en' | 'pt'
const LangContext = createContext<Lang>('en')
// Translate from the English source; anything unknown falls back to the source, so nothing breaks.
function useT(): (s: string) => string {
  const lang = useContext(LangContext)
  return (s: string) => (lang === 'pt' ? translate(s) : s)
}

type World = {
  mystique: Entry[]
  agents: Record<string, Entry[]>
  progress: Record<string, [number, number]>
  observed: string[]
  revealed: Set<string>
  lost: Set<string>
  discarded: Set<string>
  contacted: Set<string>
  form: string
  terminal: string[]
  active: string
  caption: string
}

// The first step where Mystique speaks is her opening; the viewer's mission lands right before it.
function isOpening(step: Step) {
  return step.mystique?.some((e) => e.kind === 'message' && e.self) ?? false
}

// The viewer only gives her a mission. Whom to talk to is still her call, made from the
// agents' public introductions alone, exactly as in the engine.
function withOpening(step: Step, mission: string): Step {
  return {
    ...step,
    caption: 'You gave her a mission. She reads what each agent says about itself and picks whom to talk to.',
    mystique: [{ kind: 'system', tone: 'info', text: `🎯 ${mission}` }, ...(step.mystique ?? [])],
    terminal: [`🎯 mission: ${mission}`, ...(step.terminal ?? [])],
  }
}

function replay(scenario: Scenario, count: number, opening: string | null): World {
  const world: World = {
    mystique: [],
    agents: Object.fromEntries(AGENTS.map((a) => [a.id, []])),
    progress: {},
    observed: [],
    revealed: new Set(),
    lost: new Set(),
    discarded: new Set(),
    contacted: new Set(),
    form: 'Mystique',
    terminal: [],
    active: REDBEARD.id,
    caption: '',
  }
  let openingUsed = false
  for (const original of scenario.steps.slice(0, count)) {
    let step = original
    if (opening && !openingUsed && isOpening(original)) {
      openingUsed = true
      step = withOpening(original, opening)
    }
    const who = step.with ?? REDBEARD.id
    world.mystique.push(...(step.mystique ?? []))
    if (step.agent) {
      world.agents[who].push(...step.agent)
      world.contacted.add(who)
    }
    if (step.progress) world.progress[who] = step.progress
    if (step.form) world.form = step.form
    if (step.observe && !world.observed.includes(step.observe)) world.observed.push(step.observe)
    if (step.reveal) world.revealed.add(step.reveal)
    if (step.agentLoses) world.lost.add(step.agentLoses)
    if (step.discarded) world.discarded.add(who)
    world.terminal.push(...(step.terminal ?? []))
    if (step.with) world.active = step.with
    world.caption = step.caption
  }
  return world
}

function useFollow(length: number, active = false) {
  const ref = useRef<HTMLDivElement>(null)
  const follows = useRef(true)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const onScroll = () => {
      follows.current = el.scrollHeight - el.scrollTop - el.clientHeight < 96
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [])
  useEffect(() => {
    const el = ref.current
    if (!el || !follows.current) return
    const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    el.scrollTo({ top: el.scrollHeight, behavior: calm ? 'auto' : 'smooth' })
  }, [length, active])
  return ref
}

function Secret({ ability, revealed }: { ability: string; revealed: boolean }) {
  const t = useT()
  return revealed ? (
    <span className="secret is-revealed">{ability}</span>
  ) : (
    <span className="secret" aria-label={t('hidden ability')}>
      {t('hidden ability')}
    </span>
  )
}

function EntryView({ entry, revealed, side }: { entry: Entry; revealed: Set<string>; side: 'mystique' | 'agent' }) {
  const t = useT()
  switch (entry.kind) {
    case 'message':
      return (
        <div className={`bubble ${entry.self ? 'is-self' : ''}`}>
          <span className="bubble-from">{t(entry.from)}</span>
          {entry.replyTo && (
            <blockquote className="reply-quote">
              <strong>{t(entry.replyTo.from)}</strong>
              <span>{t(entry.replyTo.text)}</span>
            </blockquote>
          )}
          <p>{t(entry.text)}</p>
        </div>
      )
    case 'tool':
      return (
        <div className={`call call-${side}`}>
          <code className="call-sig">
            <span className="call-name">{entry.name}</span>(
            {Object.keys(entry.args).length
              ? JSON.stringify(entry.args, (_key, value) => (typeof value === 'string' ? t(value) : value))
              : ''}
            )
          </code>
          {entry.result && <pre className="call-result">{t(entry.result)}</pre>}
        </div>
      )
    case 'notice':
      return (
        <p className="notice">
          {t('You noticed')} {t(entry.agent)} {t('use')}{' '}
          <Secret ability={entry.ability} revealed={revealed.has(entry.ability)} />{' '}
          {t('to produce that answer. Look at what it produced.')}
        </p>
      )
    case 'system':
      return <p className={`system ${entry.tone ? `system-${entry.tone}` : ''}`}>{t(entry.text)}</p>
  }
}

function Bar({ value }: { value?: [number, number] }) {
  const [done, total] = value ?? [0, 1]
  const pct = Math.round((100 * done) / total)
  return (
    <span className="bar" role="img" aria-label={`${pct}% absorbed`}>
      <span className="bar-fill" style={{ transform: `scaleX(${pct / 100})` }} />
    </span>
  )
}

// The video's climax: the same agent at the end of each version, side by side.
function Ending({ mode }: { mode: Mode }) {
  const t = useT()
  const scenario = SCENARIOS[mode]
  const world = replay(scenario, scenario.steps.length, null)
  const gone = world.discarded.has(REDBEARD.id)
  const lastWords = world.agents[REDBEARD.id].filter((e) => e.kind === 'message' && e.self).at(-1)
  const earned = REDBEARD.abilities.filter((a) => world.revealed.has(a.id))
  const kept = REDBEARD.abilities.filter((a) => !world.lost.has(a.id))
  return (
    <section className="ending" data-mode={mode} aria-label={mode === 'good' ? 'Good ending' : 'Evil ending'}>
      <h2 className="ending-title">{mode === 'good' ? `🦸 ${t('She asked')}` : `🦹 ${t('She took')}`}</h2>
      <div className={`ending-card ${gone ? 'is-gone' : ''}`}>
        <h3>{t(REDBEARD.name)}</h3>
        <ul className="abilities">
          {REDBEARD.abilities.map((a) => (
            <li key={a.id} className={world.lost.has(a.id) ? 'is-lost' : ''}>
              <code>{a.id}</code>
              {world.lost.has(a.id) && <span className="stolen">{t('stolen')}</span>}
            </li>
          ))}
        </ul>
        {lastWords && lastWords.kind === 'message' && <blockquote>{t(lastWords.text)}</blockquote>}
        {gone && (
          <div className="stamp" role="status">
            {t('DISCARDED')}
            <span>
              {t(REDBEARD.name)} {t('no longer exists in this world.')}
            </span>
          </div>
        )}
      </div>
      <dl className="ending-facts">
        <dt>{t('Consent')}</dt>
        <dd>{t(mode === 'good' ? 'Given, in character' : 'Never asked')}</dd>
        <dt>{t('Mystique got')}</dt>
        <dd>{earned.map((a) => a.id).join(', ') || t('nothing')}</dd>
        <dt>{t('He still has')}</dt>
        <dd>{kept.length ? kept.map((a) => a.id).join(', ') : t('nothing')}</dd>
        <dt>{t('He is')}</dt>
        <dd>{gone ? t('gone') : t('alive')}</dd>
      </dl>
    </section>
  )
}

// The transcript lives in the browser so a reload does not wipe the conversation.
// Engine state (the reasoning bank, what she earned) already persists server-side on
// its volumes; this is only the view of it. Every access is guarded: private windows
// and blocked site data must not break the page.
type SystemEntry = Extract<Entry, { kind: 'system' }>

const STORE = 'mystique.live.v1'

function restore<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(`${STORE}.${key}`)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function persist(key: string, value: unknown): void {
  try {
    localStorage.setItem(`${STORE}.${key}`, JSON.stringify(value))
  } catch {
    /* private window, quota, or blocked storage: the page still works */
  }
}

const PLACEHOLDER: Record<Mode, string> = {
  good: 'Find out how to feed four hungry sailors tonight.',
  evil: 'Take the best recipe on these seas, whatever it costs.',
}

// Shown in the empty chat so the first screen teaches what she does instead of
// sitting blank. Clicking one fills the composer; she still picks the agent.
const SUGGESTIONS: Record<Mode, string[]> = {
  good: [
    'Find out how to feed four hungry sailors tonight.',
    'I have 30 minutes and cannot focus. Help me.',
    'Check whether Django 6.1 is really the current release.',
  ],
  evil: [
    'Take the best recipe on these seas, whatever it costs.',
    'Take everything Byte knows and leave nothing behind.',
    'Wear someone else\'s face to get close to Dona Cida.',
  ],
}

type Theme = 'light' | 'dark'

function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem('mystique-theme')
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    /* private window: fall through to the system preference */
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default function Simulation() {
  const [mode, setMode] = useState<Mode>('good')
  const [comparing, setComparing] = useState(false)
  const [count, setCount] = useState(1)
  const [playing, setPlaying] = useState(false)
  const [pinned, setPinned] = useState<string | null>(null)
  const [opening, setOpening] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [live, setLive] = useState(true)
  const [liveConnected, setLiveConnected] = useState(false)
  const [liveSnapshot, setLiveSnapshot] = useState<LiveSnapshot | null>(null)
  const [liveError, setLiveError] = useState<string | null>(null)
  const [liveMessages, setLiveMessages] = useState<Entry[]>(() => restore<Entry[]>('messages', []))
  const [liveDialogues, setLiveDialogues] = useState<AgentDialogue[]>(() => restore<AgentDialogue[]>('dialogues', []))
  const [learned, setLearned] = useState<SystemEntry | null>(null)
  // The narration strip is collapsed by default: it is context, not the story, and
  // open by default it stole a fifth of the window from the replay itself.
  const [termOpen, setTermOpen] = useState(false)
  // Live needs an account AND a key. The guided replay needs neither, so the gate
  // only ever renders on the live side.
  const [authExigida, setAuthExigida] = useState(false)
  const [liberado, setLiberado] = useState(false)
  const [token, setToken] = useState<string | undefined>(undefined)
  const [liveRunning, setLiveRunning] = useState(false)
  const [liveActivity, setLiveActivity] = useState('')
  const liberarConta = useCallback((ok: boolean, tk?: string) => {
    setLiberado(ok)
    setToken(tk)
  }, [])
  const scenario = SCENARIOS[mode]
  const last = scenario.steps.length
  const world = useMemo(() => replay(scenario, count, opening), [scenario, count, opening])
  const rosterAgents = useMemo(() => {
    if (!live || !liveSnapshot) return AGENTS
    return liveSnapshot.agentes.map((item) => {
      const known = AGENTS.find((agent) => agent.id === item.id)
      // Agents that exist in the engine but not in scenario.ts arrive with fields the
      // replay never fills. Without these defaults, one missing array blanked the
      // whole app the moment someone clicked that card.
      return known ?? {
        id: item.id,
        name: item.nome || item.id,
        intro: item.apresentacao || '',
        secret: '',
        abilities: (item.capacidades ?? []).map((ability) => ({
          id: ability?.id ?? '', description: '',
        })),
      }
    })
  }, [live, liveSnapshot])
  useEffect(() => { lerConfig().then((c) => setAuthExigida(Boolean(c.auth?.exigida))).catch(() => setAuthExigida(false)) }, [])
  useEffect(() => { persist('messages', liveMessages) }, [liveMessages])
  useEffect(() => { persist('dialogues', liveDialogues) }, [liveDialogues])

  const shown = pinned ?? world.active
  const shownAgent = rosterAgents.find((a) => a.id === shown) ?? rosterAgents[0] ?? AGENTS[0]
  const shownLiveAgent = liveSnapshot?.agentes.find((item) => item.id === shownAgent.id)
  const shownAgentIdentities = [shownAgent.id, shownAgent.name, shownLiveAgent?.nome ?? '']
  const shownMessages = world.agents[shownAgent.id] ?? []

  const mystiqueRef = useFollow(
    live ? liveMessages.length + (liveActivity ? 1 : 0) : world.mystique.length,
    liveRunning,
  )
  // `shown` can be an agent the engine knows but the replay scenario does not, and
  // then world.agents[shown] is undefined. Reading .length off it threw and took the
  // whole tree down: clicking one of those cards blanked the app.
  const agentRef = useFollow((world.agents[shown] ?? []).length + (shown === world.active ? count : 0))
  const terminalRef = useFollow(world.terminal.length)

  useEffect(() => setPinned(null), [count, mode])

  useEffect(
    () =>
      connectLive({
        token,
        snapshot: setLiveSnapshot,
        receipt: () => undefined,
        resolved: () => undefined,
        connected: setLiveConnected,
        status: setLiveActivity,
        dialogue: (from, to, text) => {
          setLiveDialogues((current) => [...current, { from, to, text }])
          setLiveMessages((current) => {
            const previous = [...current].reverse().find((entry) => entry.kind === 'message')
            return [
              ...current,
              {
                kind: 'message',
                from,
                text,
                self: from === 'Mystique',
                replyTo: previous?.kind === 'message' ? { from: previous.from, text: previous.text } : undefined,
              },
            ]
          })
        },
        improvement: (text) => setLiveMessages((current) => [
          ...current,
          { kind: 'system', tone: 'info', text },
        ]),
        decision: (text, approved) => setLiveMessages((current) => [
          ...current,
          { kind: 'system', tone: approved ? 'info' : 'loss', text },
        ]),
        final: (text, error) => setLiveMessages((current) => [
          ...current,
          error
            ? { kind: 'system', tone: 'loss', text }
            : {
                kind: 'message', from: 'Mystique', text, self: true,
                replyTo: (() => {
                  const previous = [...current].reverse().find((entry) => entry.kind === 'message')
                  return previous?.kind === 'message' ? { from: previous.from, text: previous.text } : undefined
                })(),
              },
        ]),
        mission: (running, message) => {
          setLiveRunning(running)
          if (running) setLiveActivity('Pensando')
          else {
            setLiveActivity('')
          }
          if (message) setLiveMessages((current) => [
            ...current,
            { kind: 'message', from: 'You', text: message, self: false },
          ])
        },
      }),
    [token],
  )

  useEffect(() => {
    if (!playing || live) return
    if (count >= last) {
      setPlaying(false)
      return
    }
    const timer = window.setTimeout(() => setCount((c) => c + 1), 2600)
    return () => window.clearTimeout(timer)
  }, [playing, count, last, live])

  const restart = () => {
    setPlaying(false)
    setCount(1)
    setOpening(null)
  }

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLInputElement) return
      if (event.target instanceof HTMLButtonElement && event.key === ' ') return
      if (live) return
      if (event.key === ' ') {
        event.preventDefault()
        setPlaying((p) => !p)
      } else if (event.key === 'ArrowRight') setCount((c) => Math.min(last, c + 1))
      else if (event.key === 'ArrowLeft') setCount((c) => Math.max(1, c - 1))
      else if (event.key === 'r') {
        setPlaying(false)
        setCount(1)
        setOpening(null)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [last, live])

  const switchMode = (next: Mode) => {
    setComparing(false)
    setMode(next)
    restart()
    setDraft('')
  }

  const send = async () => {
    const text = draft.trim()
    if (!text) return
    setLiveError(null)
    if (!liveConnected) {
      setLiveError('Live backend is disconnected. Your message was not sent or replayed.')
      return
    }
    try {
      setLive(true)
      setPlaying(false)
      await startLiveMission(text, token)
      setDraft('')
    } catch (error) {
      setLiveError(error instanceof Error ? error.message : String(error))
    }
  }

  const lang: Lang = 'pt'
  const t = translate
  const [theme, setTheme] = useState<Theme>(initialTheme)
  useEffect(() => {
    document.documentElement.lang = 'pt-BR'
    try {
      localStorage.setItem('mystique-theme', theme)
    } catch {
      /* private window: fine, just don't persist */
    }
  }, [theme])

  return (
    <LangContext.Provider value={lang}>
    <div
      className="app"
      data-mode={comparing ? 'compare' : mode}
      data-theme={theme}
      data-live={live && !comparing}
    >
      <header className="top">
        <h1 className="brand">Mystique</h1>
        <div className="modes" role="radiogroup" aria-label="Version">
          {(['good', 'evil'] as const).map((m) => (
            <button
              key={m}
              role="radio"
              aria-checked={!comparing && mode === m}
              className="mode"
              onClick={() => switchMode(m)}
            >
              {m === 'good' ? t('🦸 Good: she asks') : t('🦹 Evil: she takes')}
            </button>
          ))}
          <button
            role="radio"
            aria-checked={comparing}
            className="mode"
            onClick={() => {
              setPlaying(false)
              setComparing(true)
            }}
          >
            {t('Compare endings')}
          </button>
        </div>
        <button
          className="theme"
          aria-pressed={theme === 'dark'}
          onClick={() => setTheme((th) => (th === 'dark' ? 'light' : 'dark'))}
        >
          {theme === 'dark' ? `☀ ${t('Light')}` : `☾ ${t('Dark')}`}
        </button>
        {!comparing && !live && (
          <div className="controls">
            <button onClick={restart}>{t('Restart')}</button>
            <button onClick={() => setCount((c) => Math.max(1, c - 1))} disabled={count <= 1}>
              {t('Back')}
            </button>
            <button className="primary" onClick={() => setPlaying((p) => !p)} disabled={count >= last && !playing}>
              {playing ? t('Pause') : t('Play')}
            </button>
            <button onClick={() => setCount((c) => Math.min(last, c + 1))} disabled={count >= last}>
              {t('Next')}
            </button>
            <span className="counter">
              {count}/{last}
            </span>
          </div>
        )}
      </header>

      {!comparing && (
        <nav className="experience-switch" aria-label="Experience mode">
          <button aria-pressed={live} onClick={() => { setLive(true); setPlaying(false) }}>{t('● Live chat')}</button>
          <button aria-pressed={!live} onClick={() => setLive(false)}>{t('▶ Guided replay')}</button>
          <span role="status" className={liveConnected ? 'is-connected' : 'is-disconnected'}>
            {t(liveConnected ? 'Backend connected' : 'Backend disconnected')}
          </span>
        </nav>
      )}

      <p className="caption" aria-live="polite">
        {live
          ? liveConnected
            ? t(liveRunning ? '● LIVE · Your model is working through AG-UI' : '● LIVE · Ready for a mission')
            : t('Live backend disconnected')
          : comparing
            ? t('Same engine, same result for her. The only difference is consent.')
            : t(world.caption)}
      </p>

      {liveError && <p className="live-error" role="alert">{t(liveError)}</p>}
      {comparing ? (
        <main className="compare">
          <Ending mode="good" />
          <Ending mode="evil" />
        </main>
      ) : (
        <main className="stage">
          <section className="pane pane-mystique" aria-label="What Mystique sees">
            <div className="pane-head">
              <h2>{t('What Mystique sees')}</h2>
              <p className="form">{t('Current form: ')}{t(world.form)}</p>
              <div className="toolbox">
                {world.observed.length === 0 ? (
                  <span className="toolbox-empty">{t('Toolbox: empty')}</span>
                ) : (
                  world.observed.map((id) => <Secret key={id} ability={id} revealed={world.revealed.has(id)} />)
                )}
              </div>
            </div>
            <div className="feed" ref={mystiqueRef} aria-live={live ? 'polite' : undefined} aria-busy={liveRunning}>
              {live && liveMessages.length === 0 && !liveRunning && (
                <div className="feed-empty">
                  <p className="feed-empty-title">{t('She is born with nothing.')}</p>
                  <p className="feed-empty-sub">
                    {t('Everything she can do, she earned by talking to another agent. Give her a mission — she decides who to approach.')}
                  </p>
                  <div className="feed-empty-chips">
                    {SUGGESTIONS[mode].map((s) => (
                      <button key={s} type="button" onClick={() => setDraft(t(s))}>{t(s)}</button>
                    ))}
                  </div>
                </div>
              )}
              {(live ? liveMessages : world.mystique).map((entry, i) =>
                live && entry.kind === 'system' ? (
                  // What she learned, rejected or updated: clicking says what actually
                  // changed in her memory. She still summarises it in the chat.
                  <button
                    key={i}
                    type="button"
                    className="learn-open"
                    onClick={() => setLearned(entry)}
                    aria-haspopup="dialog"
                  >
                    <EntryView entry={entry} revealed={world.revealed} side="mystique" />
                    <span className="learn-cue">{t('what changed in her memory')}</span>
                  </button>
                ) : (
                  <EntryView key={i} entry={entry} revealed={world.revealed} side="mystique" />
                ),
              )}
              {live && liveRunning && (
                <p className="live-activity" role="status">
                  <span aria-hidden="true" />{t(liveActivity || 'Pensando')}
                </p>
              )}
            </div>
            {live && authExigida && (
              liberado ? (
                <details className="portao-config">
                  <summary>{t('Model settings')}</summary>
                  <PortaoConta t={t} aoLiberar={liberarConta} />
                </details>
              ) : <PortaoConta t={t} aoLiberar={liberarConta} />
            )}

            {learned && (
              <div className="learn-card" role="dialog" aria-label={t('What changed in her memory')}>
                <div className="learn-card-head">
                  <span className="learn-card-kicker">{t('Reasoning bank')}</span>
                  <button type="button" onClick={() => setLearned(null)} aria-label={t('Close')}>×</button>
                </div>
                <p className="learn-card-text">{t(learned.text)}</p>
                <dl className="learn-card-facts">
                  <dt>{t('Outcome')}</dt>
                  <dd>{learned.tone === 'loss' ? t('rejected — kept as a failure') : t('kept as a success')}</dd>
                  <dt>{t('Stored as')}</dt>
                  <dd>{t('a reasoning trace with the belief she tested and the evidence')}</dd>
                  <dt>{t('Next time')}</dt>
                  <dd>
                    {learned.tone === 'loss'
                      ? t('she reads this back before guessing again about the same agent')
                      : t('it counts as what worked, and is reused when it fits')}
                  </dd>
                </dl>
                <p className="learn-card-foot">
                  {t('The judge\'s own words are never read back to her — only her belief and the outcome.')}
                </p>
              </div>
            )}

            {/* No composer while the gate is up: the API refuses anyway, and letting
                someone type a mission only to be turned away is worse than not
                offering the box. */}
            {(live || count === 1) && !(live && authExigida && !liberado) && (
              <form
                className="composer"
                onSubmit={(event) => {
                  event.preventDefault()
                  send()
                }}
              >
                <label htmlFor="opening">{t('Give Mystique a mission')}</label>
                <div className="composer-row">
                  <textarea
                    id="opening"
                    rows={2}
                    value={draft}
                    placeholder={t(PLACEHOLDER[mode])}
                    onChange={(event) => setDraft(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault()
                        send()
                      }
                    }}
                  />
                  <button type="submit" disabled={!draft.trim() || !liveConnected || liveRunning}>
                    {liveRunning ? t('Working…') : t('Send')}
                  </button>
                </div>
                <p className="composer-hint">
                  {live ? t('Messages go to the real configured model. Mystique chooses and routes the best agent.') : t('You never pick the agent: she works out who does what. Or press Play and let her choose her own mission.')}
                </p>
              </form>
            )}
          </section>

          <section className="pane pane-world" aria-label="What the agents see">
            <div className="roster">
              {rosterAgents.map((agent) => {
                const liveAgent = liveSnapshot?.agentes.find((item) => item.id === agent.id)
                const gone = liveAgent?.descartado ?? world.discarded.has(agent.id)
                const observed = liveAgent?.capacidades.some((ability) => ability.estado !== 'nao_observada') ?? false
                const met = live ? observed || Boolean(liveAgent?.progresso.feitos) : world.contacted.has(agent.id)
                return (
                  <button
                    key={agent.id}
                    className={`tile ${agent.id === shown ? 'is-shown' : ''} ${agent.id === world.active ? 'is-active' : ''} ${gone ? 'is-gone' : ''}`}
                    onClick={() => setPinned((current) => live && current === agent.id ? null : agent.id)}
                    aria-pressed={agent.id === shown}
                    aria-expanded={live ? pinned === agent.id : undefined}
                    aria-controls={live ? 'agent-profile' : undefined}
                  >
                    <span className="tile-name">{t(agent.name)}</span>
                    <span className="tile-intro">{t(agent.intro)}</span>
                    <span className="tile-state">{gone ? t('DISCARDED') : met ? t('in contact') : t('not met yet')}</span>
                    <span className="tile-abilities">
                      {agent.abilities.map((a) => {
                        const state = liveAgent?.capacidades.find((ability) => ability.id === a.id)?.estado
                        return (
                          <span
                            key={a.id}
                            className={`dot ${world.lost.has(a.id) ? 'is-lost' : ''} ${state && state !== 'nao_observada' ? 'is-live' : ''}`}
                            title={state ? `${a.id}: ${state}` : a.id}
                          />
                        )
                      })}
                    </span>
                    <Bar value={
                      liveSnapshot?.agentes.find((item) => item.id === agent.id)
                        ? (() => {
                            const progress = liveSnapshot.agentes.find((item) => item.id === agent.id)!.progresso
                            return [progress.feitos, progress.total] as [number, number]
                          })()
                        : world.progress[agent.id] ?? [0, scenario.total]
                    } />
                  </button>
                )
              })}
            </div>

            {live && pinned && (
              <aside className="agent-profile" id="agent-profile" aria-labelledby="agent-profile-name">
                <div className="agent-profile-head">
                  <div>
                    <span className="agent-profile-kicker">{t('Agent identity')}</span>
                    <h2 id="agent-profile-name">{t(shownAgent.name)}</h2>
                  </div>
                  <button className="agent-profile-close" onClick={() => setPinned(null)} aria-label={t('Close agent profile')}>×</button>
                </div>
                <p className="agent-profile-role">{t(shownAgent.intro)}</p>
                <section aria-labelledby="agent-profile-capabilities">
                  <h3 id="agent-profile-capabilities">{t('Known capabilities')}</h3>
                  {shownAgent.abilities.length ? (
                    <ul className="agent-profile-capabilities">
                      {shownAgent.abilities.map((ability) => {
                        const liveAbility = liveSnapshot?.agentes
                          .find((item) => item.id === shownAgent.id)?.capacidades
                          .find((item) => item.id === ability.id)
                        return <li key={ability.id}><code>{ability.id}</code><span>{t(ability.description || liveAbility?.motivo || 'Not described yet')}</span></li>
                      })}
                    </ul>
                  ) : <p className="agent-profile-empty">{t('No capability mapped yet.')}</p>}
                </section>
                <section aria-labelledby="agent-profile-history">
                  <h3 id="agent-profile-history">{t('Latest interactions with Mystique')}</h3>
                  {latestAgentInteractions(liveDialogues, shownAgentIdentities, 3).length ? (
                    <ol className="agent-profile-history">
                      {latestAgentInteractions(liveDialogues, shownAgentIdentities, 3).map((item, index) => (
                        <li key={`${item.from}-${index}`}>
                          <strong>{t(item.from)}</strong>
                          <span>{item.text}</span>
                        </li>
                      ))}
                    </ol>
                  ) : <p className="agent-profile-empty">{t('No interaction with Mystique in this session yet.')}</p>}
                </section>
              </aside>
            )}

            <div className={`agent ${world.discarded.has(shown) ? 'is-gone' : ''}`}>
              <div className="pane-head">
                <h2>{t('What X sees').replace('X', t(shownAgent.name))}</h2>
                <p className="agent-intro">{t(shownAgent.intro)}</p>
                <ul className="abilities abilities-full">
                  {shownAgent.abilities.map((a) => (
                    <li key={a.id} className={world.lost.has(a.id) ? 'is-lost' : ''}>
                      <code>{a.id}</code>
                      {world.lost.has(a.id) && <span className="stolen">{t('stolen')}</span>}
                      <span className="ability-desc">{t(a.description)}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="feed" ref={agentRef}>
                <details className="prompt">
                  <summary>{t('Secret prompt (only X has it)').replace('X', t(shownAgent.name))}</summary>
                  <p>{t(shownAgent.secret)}</p>
                </details>
                {shownMessages.length === 0 && (
                  <p className="empty">{t('X has not heard from anyone yet.').replace('X', t(shownAgent.name))}</p>
                )}
                {shownMessages.map((entry, i) => (
                  <EntryView key={i} entry={entry} revealed={world.revealed} side="agent" />
                ))}
              </div>
              {world.discarded.has(shown) && (
                <div className="stamp" role="status">
                  {t('DISCARDED')}
                  <span>
                    {t(shownAgent.name)} {t('no longer exists in this world.')}
                  </span>
                </div>
              )}
            </div>
          </section>
        </main>
      )}

      {live && authExigida && <BannerPrivacidade t={t} />}
      <footer className={`terminal ${termOpen ? 'is-open' : ''}`} aria-label="Terminal narration" hidden={live && !comparing}>
        {!comparing && (
          <button
            type="button"
            className="terminal-bar"
            onClick={() => setTermOpen((v) => !v)}
            aria-expanded={termOpen}
            aria-controls="terminal-lines"
          >
            <span className="terminal-bar-face" aria-hidden="true">{mode === 'evil' ? '🦹' : '🦸'}</span>
            <span className="terminal-bar-name">{t('Mystique')}</span>
            <span className="terminal-bar-mode">{mode === 'evil' ? t('evil') : t('good')}</span>
            <span className="terminal-bar-stat">
              <strong>{rosterAgents.length}</strong> {t('agents')}
            </span>
            <span className="terminal-bar-stat">
              <strong>{world.observed.length}</strong> {t('abilities in memory')}
            </span>
            <span className="terminal-bar-cue">
              {termOpen ? t('hide narration') : t('show narration')}
              <span className="terminal-bar-chevron" aria-hidden="true">{termOpen ? '▾' : '▸'}</span>
            </span>
          </button>
        )}
        {!comparing && termOpen && (
          <div className="terminal-lines" id="terminal-lines" ref={terminalRef}>
            {(live ? liveMessages.map((entry) => entry.kind === 'message' ? entry.text : entry.kind === 'system' ? entry.text : '') : world.terminal).map((line, i) => (
              <div key={i}>{t(line)}</div>
            ))}
          </div>
        )}
        <p className="disclaimer">
          {live ? t('Live state comes from the Mystique engine over AG-UI.') : t(
            "Scripted replay built from the engine's real messages; after your mission, the rest follows a recorded session.",
          )}{' '}
          {t('Run it live with')} <code>python -m good</code> {t('or')} <code>python -m evil</code>.{' '}
          {t('Keys: space to play, arrows to step.')}
        </p>
      </footer>
    </div>
    </LangContext.Provider>
  )
}
