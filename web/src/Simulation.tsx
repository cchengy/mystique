import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { AGENTS, REDBEARD, SCENARIOS, type Entry, type Mode, type Scenario, type Step } from './scenario'
import { translate } from './pt'
import { connectLive, resolveLiveReceipt, startLiveMission, type LiveReceipt, type LiveSnapshot } from './live'

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

function useFollow(length: number) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    el.scrollTo({ top: el.scrollHeight, behavior: calm ? 'auto' : 'smooth' })
  }, [length])
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

const PLACEHOLDER: Record<Mode, string> = {
  good: 'Find out how to feed four hungry sailors tonight.',
  evil: 'Take the best recipe on these seas, whatever it costs.',
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
  const [live, setLive] = useState(false)
  const [liveConnected, setLiveConnected] = useState(false)
  const [liveSnapshot, setLiveSnapshot] = useState<LiveSnapshot | null>(null)
  const [liveReceipts, setLiveReceipts] = useState<LiveReceipt[]>([])
  const [liveError, setLiveError] = useState<string | null>(null)
  const scenario = SCENARIOS[mode]
  const last = scenario.steps.length
  const world = useMemo(() => replay(scenario, count, opening), [scenario, count, opening])
  const shown = pinned ?? world.active
  const shownAgent = AGENTS.find((a) => a.id === shown)!

  const mystiqueRef = useFollow(world.mystique.length)
  const agentRef = useFollow(world.agents[shown].length + (shown === world.active ? count : 0))
  const terminalRef = useFollow(world.terminal.length)

  useEffect(() => setPinned(null), [count, mode])

  useEffect(
    () =>
      connectLive({
        snapshot: setLiveSnapshot,
        receipt: (receipt) => setLiveReceipts((current) => [...current, receipt]),
        resolved: (id) => setLiveReceipts((current) => current.filter((receipt) => receipt.recibo_id !== id)),
        connected: setLiveConnected,
      }),
    [],
  )

  useEffect(() => {
    if (!playing) return
    if (count >= last) {
      setPlaying(false)
      return
    }
    const timer = window.setTimeout(() => setCount((c) => c + 1), 2600)
    return () => window.clearTimeout(timer)
  }, [playing, count, last])

  const restart = () => {
    setPlaying(false)
    setCount(1)
    setOpening(null)
  }

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLInputElement) return
      if (event.target instanceof HTMLButtonElement && event.key === ' ') return
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
  }, [last])

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
    if (liveConnected) {
      try {
        await startLiveMission(text)
        setLive(true)
        setOpening(text)
        setDraft('')
        setPlaying(false)
      } catch (error) {
        setLiveError(error instanceof Error ? error.message : String(error))
      }
      return
    }
    setOpening(text)
    setDraft('')
    setCount(2)
    setPlaying(true)
  }

  const [lang, setLang] = useState<Lang>(() => {
    try {
      return (localStorage.getItem('mystique-lang') as Lang) || 'pt'
    } catch {
      return 'pt'
    }
  })
  const t = (s: string) => (lang === 'pt' ? translate(s) : s)
  const [theme, setTheme] = useState<Theme>(initialTheme)
  useEffect(() => {
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en'
    try {
      localStorage.setItem('mystique-lang', lang)
      localStorage.setItem('mystique-theme', theme)
    } catch {
      /* private window: fine, just don't persist */
    }
  }, [lang, theme])

  return (
    <LangContext.Provider value={lang}>
    <div className="app" data-mode={comparing ? 'compare' : mode} data-theme={theme}>
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
        <div className="langs" role="radiogroup" aria-label="Language">
          {(['en', 'pt'] as const).map((l) => (
            <button key={l} role="radio" aria-checked={lang === l} className="lang" onClick={() => setLang(l)}>
              {l.toUpperCase()}
            </button>
          ))}
        </div>
        <button
          className="theme"
          aria-pressed={theme === 'dark'}
          onClick={() => setTheme((th) => (th === 'dark' ? 'light' : 'dark'))}
        >
          {theme === 'dark' ? `☀ ${t('Light')}` : `☾ ${t('Dark')}`}
        </button>
        {!comparing && (
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

      <p className="caption" aria-live="polite">
        {live
          ? liveConnected
            ? t('● LIVE · DeepSeek mission running through AG-UI')
            : t('Live backend disconnected')
          : comparing
            ? t('Same engine, same result for her. The only difference is consent.')
            : t(world.caption)}
      </p>

      {liveError && <p className="live-error" role="alert">{t(liveError)}</p>}
      {liveReceipts.map((receipt) => (
        <article className="live-receipt" key={receipt.recibo_id}>
          <strong>
            {t('Trust receipt')} · {receipt.agente_id}
          </strong>
          <p>{receipt.descricao_alegada}</p>
          <p>{receipt.evidencia}</p>
          <p>{t(receipt.veredito.aprovado ? 'Judge approved' : 'Judge rejected')} · {receipt.veredito.motivo}</p>
          <div>
            <button disabled={!receipt.veredito.aprovado} onClick={() => resolveLiveReceipt(receipt.recibo_id, 'aprovar')}>{t('Approve')}</button>
            <button onClick={() => resolveLiveReceipt(receipt.recibo_id, 'rejeitar')}>{t('Reject')}</button>
          </div>
        </article>
      ))}

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
            <div className="feed" ref={mystiqueRef}>
              {world.mystique.map((entry, i) => (
                <EntryView key={i} entry={entry} revealed={world.revealed} side="mystique" />
              ))}
            </div>
            {count === 1 && (
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
                  <button type="submit" disabled={!draft.trim()}>
                    {t('Send')}
                  </button>
                </div>
                <p className="composer-hint">
                  {t('You never pick the agent: she works out who does what. Or press Play and let her choose her own mission.')}
                </p>
              </form>
            )}
          </section>

          <section className="pane pane-world" aria-label="What the agents see">
            <div className="roster">
              {AGENTS.map((agent) => {
                const liveAgent = liveSnapshot?.agentes.find((item) => item.id === agent.id)
                const gone = liveAgent?.descartado ?? world.discarded.has(agent.id)
                const observed = liveAgent?.capacidades.some((ability) => ability.estado !== 'nao_observada') ?? false
                const met = live ? observed || Boolean(liveAgent?.progresso.feitos) : world.contacted.has(agent.id)
                return (
                  <button
                    key={agent.id}
                    className={`tile ${agent.id === shown ? 'is-shown' : ''} ${agent.id === world.active ? 'is-active' : ''} ${gone ? 'is-gone' : ''}`}
                    onClick={() => setPinned(agent.id)}
                    aria-pressed={agent.id === shown}
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
                {world.agents[shown].length === 0 && (
                  <p className="empty">{t('X has not heard from anyone yet.').replace('X', t(shownAgent.name))}</p>
                )}
                {world.agents[shown].map((entry, i) => (
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

      <footer className="terminal" aria-label="Terminal narration">
        {!comparing && (
          <div className="terminal-lines" ref={terminalRef}>
            {world.terminal.map((line, i) => (
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
