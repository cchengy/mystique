import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { AGENTS, REDBEARD, SCENARIOS, type Entry, type Mode, type Scenario, type Step } from './scenario'
import { latestAgentInteractions, type AgentDialogue } from './agent-profile'
import { translate } from './pt'
import {
  connectLive, createSession, getSession, getWiki, listSessions, startLiveMission,
  type ChatSession, type LiveSnapshot, type WikiPage,
} from './live'
import { aceitouPrivacidade, BannerPrivacidade, PortaoConta } from './Portao'
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

/** The engine's own WIKI.md, rendered as the small subset of Markdown it writes:
 *  a heading per agent, one bullet per attempt, indented detail lines. Not a
 *  Markdown engine - anything unrecognised is shown as the plain text it is. */
function Wiki({ texto }: { texto: string }) {
  const linhas = texto.split('\n').filter((linha) => linha.trim() && !linha.startsWith('# '))
  return (
    <div className="wiki">
      {linhas.map((linha, i) => {
        if (linha.startsWith('## ')) return <h4 key={i}>{linha.slice(3)}</h4>
        if (linha.startsWith('  - ')) return <p key={i} className="wiki-detail">{linha.slice(4)}</p>
        if (linha.startsWith('- ')) return <p key={i} className="wiki-line">{linha.slice(2).replace(/\*\*|\*/g, '')}</p>
        return <p key={i} className="wiki-note">{linha}</p>
      })}
    </div>
  )
}

/** Keeps the keyboard inside a modal for as long as it is open, and gives focus
 *  back to wherever it came from afterwards. The gate claims `aria-modal`, and a
 *  modal you can Tab out of is lying: the screen behind it is inert to the mouse
 *  and was still reachable by keyboard. There is no Escape here on purpose — the
 *  gate is the only way in, so there is nothing to escape to. */
function useFocoPreso(ativo: boolean) {
  const alvo = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!ativo) return
    const anterior = document.activeElement as HTMLElement | null
    const focaveis = () => Array.from(
      alvo.current?.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])',
      ) ?? [],
    ).filter((el) => el.offsetParent !== null || el === document.activeElement)

    const aoTeclar = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return
      const itens = focaveis()
      if (!itens.length) return
      const primeiro = itens[0]
      const ultimo = itens[itens.length - 1]
      const atual = document.activeElement as HTMLElement | null
      if (!alvo.current?.contains(atual)) {
        event.preventDefault()
        ;(event.shiftKey ? ultimo : primeiro).focus()
        return
      }
      if (event.shiftKey && atual === primeiro) {
        event.preventDefault()
        ultimo.focus()
      } else if (!event.shiftKey && atual === ultimo) {
        event.preventDefault()
        primeiro.focus()
      }
    }

    document.addEventListener('keydown', aoTeclar, true)
    return () => {
      document.removeEventListener('keydown', aoTeclar, true)
      // Only take focus back if it is still inside the modal we are closing.
      if (alvo.current?.contains(document.activeElement)) anterior?.focus?.()
    }
  }, [ativo])
  return alvo
}

type SystemEntry = Extract<Entry, { kind: 'system' }>

function entriesFromSession(session: ChatSession): Entry[] {
  return (session.mensagens ?? []).map((message) => message.role === 'system'
    ? { kind: 'system', tone: 'loss', text: message.content }
    // 'You' is the source string the translation table keys off; the bubble runs
    // it through t(), so the label follows the chosen language.
    : { kind: 'message', from: message.role === 'user' ? 'You' : 'Mystique', text: message.content, self: message.role === 'assistant' })
}

/** The pre-accounts build kept the transcript in the browser. That key now
 *  belongs to nobody: it is not this account's history and must never become
 *  it, so it is thrown away the first time we see it. */
function descartarTranscricaoAntiga() {
  try {
    localStorage.removeItem('mystique.live.v1.messages')
  } catch {
    /* private window: there was nothing to inherit anyway */
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

/** The chosen language is the user's, and it survives reloads. With nothing
 *  saved we follow the browser, so a Brazilian arrives in Portuguese and
 *  everyone else in the English source. */
function initialLang(): Lang {
  try {
    const saved = localStorage.getItem('mystique.lang')
    if (saved === 'en' || saved === 'pt') return saved
  } catch {
    /* private window: fall through to the browser preference */
  }
  return (navigator.languages ?? [navigator.language ?? 'en']).some((l) => l.toLowerCase().startsWith('pt'))
    ? 'pt'
    : 'en'
}

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
  // Declared first: the live-event handlers translate as events arrive.
  const [lang, setLang] = useState<Lang>(initialLang)
  const t = useCallback((s: string) => (lang === 'pt' ? translate(s) : s), [lang])
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
  const [liveMessages, setLiveMessages] = useState<Entry[]>([])
  const [liveDialogues, setLiveDialogues] = useState<AgentDialogue[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionDetails, setSessionDetails] = useState<ChatSession[]>([])
  const [wikis, setWikis] = useState<Partial<Record<Mode, WikiPage>>>({})
  const [learned, setLearned] = useState<SystemEntry | null>(null)
  // The narration strip is collapsed by default: it is context, not the story, and
  // open by default it stole a fifth of the window from the replay itself.
  const [termOpen, setTermOpen] = useState(false)
  // Live needs an account AND a key. The guided replay needs neither, so the gate
  // only ever renders on the live side.
  // `null` means the public config is still loading. Treating that transient state
  // as "auth disabled" made the browser call /api/sessoes without a token and
  // flashed a raw 401 during onboarding.
  const [authExigida, setAuthExigida] = useState<boolean | null>(null)
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
  useEffect(() => { descartarTranscricaoAntiga() }, [])
  useEffect(() => { lerConfig().then((c) => setAuthExigida(Boolean(c.auth?.exigida))).catch(() => setAuthExigida(false)) }, [])
  const refreshSessions = useCallback(async () => {
    const items = await listSessions(token)
    setSessions(items)
    return items
  }, [token])
  useEffect(() => {
    if (authExigida === null || (authExigida && !liberado)) return
    void refreshSessions().then(async (items) => {
      let selected = sessionId && items.some((item) => item.id === sessionId) ? sessionId : items[0]?.id
      if (!selected) {
        // A new account starts empty. It used to inherit the browser's old
        // pre-accounts transcript, so anyone who signed up on a machine that
        // still had one opened somebody else's conversation on their first day.
        const created = await createSession(mode, token)
        selected = created.id
        await refreshSessions()
      }
      setSessionId(selected)
    }).catch((error) => setLiveError(error instanceof Error ? error.message : String(error)))
  }, [authExigida, liberado, token])
  useEffect(() => {
    if (!sessionId) return
    void getSession(sessionId, token).then((session) => {
      setMode(session.modo)
      setLiveMessages(entriesFromSession(session))
      setLiveDialogues([])
    }).catch((error) => setLiveError(error instanceof Error ? error.message : String(error)))
  }, [sessionId, token])

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
        improvement: (text, agent) => setLiveMessages((current) => [
          ...current,
          { kind: 'system', tone: 'info', text: t(text).replace('{agent}', agent) },
        ]),
        decision: (text, approved, agent) => setLiveMessages((current) => [
          ...current,
          { kind: 'system', tone: approved ? 'info' : 'loss', text: t(text).replace('{agent}', agent) },
        ]),
        final: () => {
          if (sessionId) void getSession(sessionId, token).then((session) => setLiveMessages(entriesFromSession(session)))
          void refreshSessions()
        },
        mission: (running, message) => {
          setLiveRunning(running)
          if (running) setLiveActivity('Thinking')
          else {
            setLiveActivity('')
          }
          if (message) setLiveMessages((current) => [
            ...current,
            { kind: 'message', from: 'You', text: message, self: false },
          ])
        },
      }),
    [token, sessionId, refreshSessions, t],
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
    if (live) {
      const existing = sessions.find((session) => session.modo === next)
      if (existing) setSessionId(existing.id)
      else void createSession(next, token).then(async (created) => {
        await refreshSessions()
        setSessionId(created.id)
      }).catch((error) => setLiveError(error instanceof Error ? error.message : String(error)))
    }
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
      let activeSession = sessionId
      if (!activeSession) {
        const created = await createSession(mode, token)
        activeSession = created.id
        setSessionId(created.id)
      }
      await startLiveMission(text, activeSession, token, lang)
      setDraft('')
    } catch (error) {
      setLiveError(error instanceof Error ? error.message : String(error))
    }
  }

  const [theme, setTheme] = useState<Theme>(initialTheme)
  useEffect(() => {
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en'
    try {
      localStorage.setItem('mystique.lang', lang)
    } catch {
      /* private window: fine, just don't persist */
    }
  }, [lang])
  useEffect(() => {
    try {
      localStorage.setItem('mystique-theme', theme)
    } catch {
      /* private window: fine, just don't persist */
    }
  }, [theme])

  // The gate is up: the rail stays on screen, but nothing in it can be used.
  const travada = Boolean(authExigida && !liberado)
  // The gate does not vanish the instant the account unlocks: it plays out, and
  // only then hands the screen over. See the panel-wipe in styles.css.
  const [portaoSaindo, setPortaoSaindo] = useState(false)
  // Trapped while the gate is up; released the moment it starts leaving, so the
  // app behind takes the keyboard back as it comes into focus.
  const focoPortao = useFocoPreso(Boolean(live && travada))
  const travadaAntes = useRef(travada)
  useEffect(() => {
    if (travadaAntes.current && !travada) {
      setPortaoSaindo(true)
      const calmo = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      const fim = window.setTimeout(() => setPortaoSaindo(false), calmo ? 0 : 620)
      travadaAntes.current = travada
      return () => window.clearTimeout(fim)
    }
    travadaAntes.current = travada
  }, [travada])
  // Shown unprompted until it is accepted, and reachable from the rail forever
  // after. It was invisible to anyone who had already clicked Understood.
  const [privacidadeAberta, setPrivacidadeAberta] = useState(() => !aceitouPrivacidade())

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
        <div className="modes" role="radiogroup" aria-label={t('Version')}>
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
              void Promise.all(sessions.map((session) => getSession(session.id, token))).then(setSessionDetails)
              // The bank is the other half of the comparison: the trajectories say
              // what happened, the bank says what she kept from it.
              void Promise.all((['good', 'evil'] as const).map((side) =>
                getWiki(side, token).then((page) => [side, page] as const).catch(() => null),
              )).then((pares) => setWikis(Object.fromEntries(pares.filter(Boolean) as [Mode, WikiPage][])))
            }}
          >
            {t('Compare endings')}
          </button>
        </div>
        {/* The rail already had styling for this control; the app had simply
            stopped offering it and hardcoded Portuguese. */}
        <div className="langs" role="radiogroup" aria-label={t('Language')}>
          {(['en', 'pt'] as const).map((code) => (
            <button
              key={code}
              className="lang"
              role="radio"
              aria-checked={lang === code}
              onClick={() => setLang(code)}
              lang={code === 'pt' ? 'pt-BR' : 'en'}
            >
              {code === 'en' ? 'EN' : 'PT'}
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
        <nav className="experience-switch" aria-label={t('Experience mode')}>
          <button aria-pressed={live} onClick={() => { setLive(true); setPlaying(false) }}>{t('● Live chat')}</button>
          <button aria-pressed={!live} onClick={() => setLive(false)}>{t('▶ Guided replay')}</button>
          <span role="status" className={live ? (liveConnected ? 'is-connected' : 'is-disconnected') : 'is-local'}>
            {live ? t(liveConnected ? 'Backend connected' : 'Backend disconnected') : t('Local replay · no connection required')}
          </span>
        </nav>
      )}

      {/* The rail keeps its place while the gate is up. It used to be removed
          entirely, and because the layout still reserves its column the page
          opened with an empty strip down the left. Locked and visible says what
          sign-in unlocks; absent said nothing and looked broken. */}
      {live && !comparing && (
        <aside
          className="session-sidebar"
          aria-label={t('Conversations')}
          data-locked={travada ? 'true' : undefined}
        >
          <div className="session-sidebar-head">
            <div><span>{t('CONVERSATIONS')}</span><strong>{t('History')}</strong></div>
            <button type="button" disabled={travada} onClick={async () => {
              const created = await createSession(mode, token)
              await refreshSessions()
              setSessionId(created.id)
            }} aria-label={t('New conversation')}>＋</button>
          </div>
          {travada ? (
            <div className="session-list is-locked">
              <p className="session-locked-note">
                {t('Sign in to keep a history of conversations. The guided replay needs no account.')}
              </p>
              <span className="session-locked-row" aria-hidden="true" />
              <span className="session-locked-row" aria-hidden="true" />
              <span className="session-locked-row" aria-hidden="true" />
            </div>
          ) : (
            <div className="session-list">
              {sessions.map((session) => (
                <button key={session.id} type="button" className={session.id === sessionId ? 'is-active' : ''}
                  onClick={() => setSessionId(session.id)}>
                  <span>{t(session.titulo === 'Nova conversa' ? 'New conversation' : session.titulo)}</span><small>{t(session.modo === 'good' ? 'She asked' : 'She took')}</small>
                </button>
              ))}
            </div>
          )}
          <button type="button" className="privacy-link" onClick={() => setPrivacidadeAberta(true)}>
            {t('Privacy and cookies')}
          </button>
          {travada ? (
            <div className="model-drawer is-locked">
              <div className="model-drawer-locked">
                <span>{t('Model and connection')}</span>
                <small>{t('Available after you sign in')}</small>
              </div>
            </div>
          ) : (
            <details className="model-drawer">
              <summary><span>{t('Model and connection')}</span><small>{t('OpenRouter · search by name')}</small></summary>
              <PortaoConta t={t} aoLiberar={liberarConta} />
            </details>
          )}
        </aside>
      )}

      <p className="caption" aria-live="polite">
        {comparing
          ? t('Real trajectories: decisions, evidence and Reasoning Bank memory.')
          : live
          ? liveConnected
            ? t(liveRunning ? '● LIVE · Your model is working through AG-UI' : '● LIVE · Ready for a mission')
            : t('Live backend disconnected')
          : t(world.caption)}
      </p>

      {liveError && <p className="live-error" role="alert">{t(liveError)}</p>}
      {comparing ? (
        <main className="compare" aria-label={t('Compare endings')}>
          <header className="compare-head">
            <p className="compare-eyebrow">{t('Reasoning Bank')}</p>
            <h2>{t('Same world, two ethics.')}</h2>
            <p className="compare-lede">
              {t('Both profiles meet the same agents with the same abilities. What separates them is what each one leaves behind.')}
            </p>
          </header>
          <div className="compare-grid">
            {(['good', 'evil'] as const).map((side) => {
              const candidates = sessionDetails.filter((session) => session.modo === side)
              const evidence = candidates.flatMap((session) => session.evidencias ?? [])
              const confirmed = evidence.filter((item) => item.outcome === 'success').length
              const agents = new Set(evidence.map((item) => item.agent_id).filter(Boolean)).size
              const bank = wikis[side]
              return (
                <section className="ledger" data-side={side} key={side}>
                  <header className="ledger-head">
                    <span className="ledger-label">{t(side === 'good' ? 'SHE ASKED' : 'SHE TOOK')}</span>
                    <p className="ledger-claim">
                      {t(side === 'good'
                        ? 'The agent keeps its ability. She earns a copy, with consent.'
                        : 'She takes the ability. The agent is left with nothing.')}
                    </p>
                  </header>
                  <dl className="ledger-figures">
                    <div><dt>{t('Conversations')}</dt><dd>{candidates.length}</dd></div>
                    <div><dt>{t('Abilities confirmed')}</dt><dd>{confirmed}</dd></div>
                    <div><dt>{t('Agents involved')}</dt><dd>{agents}</dd></div>
                  </dl>
                  {candidates.length ? (
                    <ol className="ledger-runs">
                      {candidates.map((session) => (
                        <li key={session.id}>
                          <button
                            type="button"
                            className="run"
                            onClick={() => { setComparing(false); setLive(true); setSessionId(session.id) }}
                          >
                            <span className="run-title">
                              {t(session.titulo === 'Nova conversa' ? 'New conversation' : session.titulo)}
                            </span>
                            <span className="run-meta">
                              {session.mensagens?.length ?? 0} {t('messages')} · {session.evidencias?.length ?? 0} {t('pieces of evidence')}
                            </span>
                          </button>
                          {(session.evidencias ?? []).length > 0 && (
                            <ul className="run-evidence">
                              {(session.evidencias ?? []).map((item) => (
                                <li key={item.id} data-outcome={item.outcome === 'success' ? 'success' : 'failure'}>
                                  <span className="run-outcome">
                                    {t(item.outcome === 'success' ? 'Confirmed' : 'Rejected')}
                                    <em>{item.agent_id}</em>
                                  </span>
                                  <p className="run-belief">{item.description || item.title}</p>
                                  {item.content && <p className="run-verdict">{item.content}</p>}
                                </li>
                              ))}
                            </ul>
                          )}
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p className="ledger-empty">
                      {t('Nothing on this side yet. Run a conversation in this profile and its reasoning appears here.')}
                    </p>
                  )}
                  <details className="ledger-bank">
                    <summary>
                      <span>{t('What she has learned')}</span>
                      <small>
                        {bank?.resumo?.total ?? 0} {t('reasoning traces')}
                        {bank?.resumo?.most_reused ? ` · ${t('most reused')} ${bank.resumo.most_reused}×` : ''}
                      </small>
                    </summary>
                    {bank?.texto
                      ? <Wiki texto={bank.texto} />
                      : <p className="ledger-empty">{t('Her bank for this profile is still empty.')}</p>}
                  </details>
                </section>
              )
            })}
          </div>
        </main>
      ) : (
        <main className="stage">
          <section className="pane pane-mystique" aria-label={t('What Mystique sees')}>
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
                  <span aria-hidden="true" />{t(liveActivity || 'Thinking')}
                </p>
              )}
            </div>

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

          <section className="pane pane-world" aria-label={t('What the agents see')}>
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

      {/* The account is the way in, so it is the only thing on screen: everything
          else is dimmed behind it and comes back when she lets you through. */}
      {live && (travada || portaoSaindo) && (
        <div className="portao-cena" data-saindo={portaoSaindo ? 'true' : undefined} aria-hidden={portaoSaindo}>
          <div className="portao-fundo" />
          <div className="portao-palco" ref={focoPortao} role="dialog" aria-modal="true" aria-label={t('The live chat needs an account')}>
            <PortaoConta t={t} aoLiberar={liberarConta} aoAbrirPrivacidade={() => setPrivacidadeAberta(true)} compacto />
          </div>
        </div>
      )}

      {privacidadeAberta && <BannerPrivacidade t={t} aoFechar={() => setPrivacidadeAberta(false)} />}
      <footer className={`terminal ${termOpen ? 'is-open' : ''}`} aria-label={t('Terminal narration')} hidden={live || comparing}>
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
          {comparing ? t('Comparison built from the persisted session history and the Reasoning Bank.') : live ? t('Live state comes from the Mystique engine over AG-UI.') : t(
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
