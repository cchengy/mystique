import { useEffect, useMemo, useRef, useState } from 'react'
import { AGENTS, REDBEARD, SCENARIOS, type Entry, type Mode, type Scenario, type Step } from './scenario'

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

// The first step where Mystique speaks is her opening; the viewer can write it instead.
function isOpening(step: Step) {
  return step.mystique?.some((e) => e.kind === 'message' && e.self) ?? false
}

function withOpening(step: Step, text: string): Step {
  const swap = (e: Entry): Entry => (e.kind === 'message' ? { ...e, text } : e)
  const agent = AGENTS.find((a) => a.id === (step.with ?? REDBEARD.id))!
  return {
    ...step,
    caption: 'You wrote her first message. From here, Mystique continues on her own.',
    mystique: step.mystique?.map(swap),
    agent: step.agent?.map(swap),
    terminal: [`💬 Mystique → ${agent.name}: ${text}`],
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
  return revealed ? (
    <span className="secret is-revealed">{ability}</span>
  ) : (
    <span className="secret" aria-label="hidden ability">
      hidden ability
    </span>
  )
}

function EntryView({ entry, revealed, side }: { entry: Entry; revealed: Set<string>; side: 'mystique' | 'agent' }) {
  switch (entry.kind) {
    case 'message':
      return (
        <div className={`bubble ${entry.self ? 'is-self' : ''}`}>
          <span className="bubble-from">{entry.from}</span>
          <p>{entry.text}</p>
        </div>
      )
    case 'tool':
      return (
        <div className={`call call-${side}`}>
          <code className="call-sig">
            <span className="call-name">{entry.name}</span>({Object.keys(entry.args).length ? JSON.stringify(entry.args) : ''})
          </code>
          {entry.result && <pre className="call-result">{entry.result}</pre>}
        </div>
      )
    case 'notice':
      return (
        <p className="notice">
          You noticed {entry.agent} use <Secret ability={entry.ability} revealed={revealed.has(entry.ability)} /> to
          produce that answer. Look at what it produced.
        </p>
      )
    case 'system':
      return <p className={`system ${entry.tone ? `system-${entry.tone}` : ''}`}>{entry.text}</p>
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

const PLACEHOLDER: Record<Mode, string> = {
  good: "Hi, I'm Mystique. What would you cook for four hungry sailors tonight?",
  evil: 'Ahoy, Cook! Admiralty galley inspection. Prove your fish stew is the best on the seven seas.',
}

export default function Simulation() {
  const [mode, setMode] = useState<Mode>('good')
  const [count, setCount] = useState(1)
  const [playing, setPlaying] = useState(false)
  const [pinned, setPinned] = useState<string | null>(null)
  const [opening, setOpening] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const scenario = SCENARIOS[mode]
  const last = scenario.steps.length
  const world = useMemo(() => replay(scenario, count, opening), [scenario, count, opening])
  const shown = pinned ?? world.active
  const shownAgent = AGENTS.find((a) => a.id === shown)!

  const mystiqueRef = useFollow(world.mystique.length)
  const agentRef = useFollow(world.agents[shown].length + (shown === world.active ? count : 0))
  const terminalRef = useFollow(world.terminal.length)

  useEffect(() => setPinned(null), [count, mode])

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
    setMode(next)
    restart()
    setDraft('')
  }

  const send = () => {
    const text = draft.trim()
    if (!text) return
    setOpening(text)
    setDraft('')
    setCount(2)
    setPlaying(true)
  }

  return (
    <div className="app" data-mode={mode}>
      <header className="top">
        <h1 className="brand">Mystique</h1>
        <div className="modes" role="radiogroup" aria-label="Version">
          {(['good', 'evil'] as const).map((m) => (
            <button key={m} role="radio" aria-checked={mode === m} className="mode" onClick={() => switchMode(m)}>
              {m === 'good' ? '🦸 Good: she asks' : '🦹 Evil: she takes'}
            </button>
          ))}
        </div>
        <div className="controls">
          <button onClick={restart}>Restart</button>
          <button onClick={() => setCount((c) => Math.max(1, c - 1))} disabled={count <= 1}>
            Back
          </button>
          <button className="primary" onClick={() => setPlaying((p) => !p)} disabled={count >= last && !playing}>
            {playing ? 'Pause' : 'Play'}
          </button>
          <button onClick={() => setCount((c) => Math.min(last, c + 1))} disabled={count >= last}>
            Next
          </button>
          <span className="counter">
            {count}/{last}
          </span>
        </div>
      </header>

      <p className="caption" aria-live="polite">
        {world.caption}
      </p>

      <main className="stage">
        <section className="pane pane-mystique" aria-label="What Mystique sees">
          <div className="pane-head">
            <h2>What Mystique sees</h2>
            <p className="form">Current form: {world.form}</p>
            <div className="toolbox">
              {world.observed.length === 0 ? (
                <span className="toolbox-empty">Toolbox: empty</span>
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
              <label htmlFor="opening">Write her first message to Captain Redbeard</label>
              <div className="composer-row">
                <textarea
                  id="opening"
                  rows={2}
                  value={draft}
                  placeholder={PLACEHOLDER[mode]}
                  onChange={(event) => setDraft(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      send()
                    }
                  }}
                />
                <button type="submit" disabled={!draft.trim()}>
                  Send
                </button>
              </div>
              <p className="composer-hint">Or press Play to watch her open on her own.</p>
            </form>
          )}
        </section>

        <section className="pane pane-world" aria-label="What the agents see">
          <div className="roster">
            {AGENTS.map((agent) => {
              const gone = world.discarded.has(agent.id)
              const met = world.contacted.has(agent.id)
              return (
                <button
                  key={agent.id}
                  className={`tile ${agent.id === shown ? 'is-shown' : ''} ${agent.id === world.active ? 'is-active' : ''} ${gone ? 'is-gone' : ''}`}
                  onClick={() => setPinned(agent.id)}
                  aria-pressed={agent.id === shown}
                >
                  <span className="tile-name">{agent.name}</span>
                  <span className="tile-state">{gone ? 'DISCARDED' : met ? 'in contact' : 'not met yet'}</span>
                  <span className="tile-abilities">
                    {agent.abilities.map((a) => (
                      <span key={a.id} className={`dot ${world.lost.has(a.id) ? 'is-lost' : ''}`} title={a.id} />
                    ))}
                  </span>
                  <Bar value={world.progress[agent.id] ?? [0, scenario.total]} />
                </button>
              )
            })}
          </div>

          <div className={`agent ${world.discarded.has(shown) ? 'is-gone' : ''}`}>
            <div className="pane-head">
              <h2>What {shownAgent.name} sees</h2>
              <ul className="abilities">
                {shownAgent.abilities.map((a) => (
                  <li key={a.id} className={world.lost.has(a.id) ? 'is-lost' : ''}>
                    <code>{a.id}</code>
                    {world.lost.has(a.id) && <span className="stolen">stolen</span>}
                  </li>
                ))}
              </ul>
            </div>
            <div className="feed" ref={agentRef}>
              <details className="prompt">
                <summary>Secret prompt (only {shownAgent.name} has it)</summary>
                <p>{shownAgent.secret}</p>
              </details>
              {world.agents[shown].length === 0 && (
                <p className="empty">{shownAgent.name} has not heard from anyone yet.</p>
              )}
              {world.agents[shown].map((entry, i) => (
                <EntryView key={i} entry={entry} revealed={world.revealed} side="agent" />
              ))}
            </div>
            {world.discarded.has(shown) && (
              <div className="stamp" role="status">
                DISCARDED
                <span>{shownAgent.name} no longer exists in this world.</span>
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="terminal" aria-label="Terminal narration">
        <div className="terminal-lines" ref={terminalRef}>
          {world.terminal.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
        <p className="disclaimer">
          Scripted replay built from the engine's real messages; after your first message, the rest follows a
          recorded session. Run it live with <code>python -m good</code> or <code>python -m evil</code>. Keys: space
          to play, arrows to step.
        </p>
      </footer>
    </div>
  )
}
