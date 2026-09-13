/** The guided tour of the interface.
 *
 * Two short panels introduce her, then the card leaves the middle of the screen
 * and travels to each control it is talking about, which lights up through the
 * dimmed app. The card only ever moves by transform, so the travel is cheap and
 * the reduced-motion path is a straight cut.
 *
 * Every word here already exists in the product - the empty state, the Compare
 * ledgers, the account gate, the Exa card. The tour explains what is there; it
 * does not invent a second story about it.
 */
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'

/** Which control each step points at. `null` means the middle of the screen. */
export type PassoGuia =
  | { id: 'intro-1' | 'intro-2'; alvo: null }
  | { id: 'good' | 'evil' | 'replay' | 'live' | 'compare' | 'compose'; alvo: string }

export const PASSOS: PassoGuia[] = [
  { id: 'intro-1', alvo: null },
  { id: 'intro-2', alvo: null },
  { id: 'good', alvo: 'good' },
  { id: 'evil', alvo: 'evil' },
  { id: 'replay', alvo: 'replay' },
  { id: 'live', alvo: 'live' },
  { id: 'compare', alvo: 'compare' },
  { id: 'compose', alvo: 'compose' },
]

type Conteudo = { titulo: string; corpo: string[] }

/** The last card knows what is already connected, so it asks for the next real
 *  thing instead of repeating setup the person has done. */
function conteudo(id: PassoGuia['id'], chave: boolean, exa: boolean): Conteudo {
  switch (id) {
    case 'intro-1':
      return {
        titulo: 'She is born with nothing.',
        corpo: [
          'Mystique arrives with one power: she changes form. No terminal, no files, no web.',
          'Everything else she can do, she earned by talking to another agent.',
        ],
      }
    case 'intro-2':
      return {
        titulo: 'She has to work it out.',
        corpo: [
          'She never sees what an agent can do. She only sees it happen, describes what she saw, and a judge decides whether she got it right.',
          'Give her a mission — she decides who to approach.',
        ],
      }
    case 'good':
      return {
        titulo: 'Good: she asks',
        corpo: ['The agent keeps its ability. She earns a copy, with consent.'],
      }
    case 'evil':
      return {
        titulo: 'Evil: she takes',
        corpo: ['She takes the ability. The agent is left with nothing.'],
      }
    case 'replay':
      return {
        titulo: 'Guided replay',
        corpo: [
          'A recorded run, built from the engine’s real messages. Press play and step through it.',
          'It needs no account and no connection at all.',
        ],
      }
    case 'live':
      return {
        titulo: 'Live chat',
        corpo: [
          'The real engine, working through AG-UI on your own key.',
          'What she learns here is yours, kept apart from everyone else’s.',
        ],
      }
    case 'compare':
      return {
        titulo: 'Compare endings',
        corpo: [
          'Both profiles meet the same agents with the same abilities. What separates them is what each one leaves behind.',
          'Your real runs, side by side, with the reasoning she kept from each.',
        ],
      }
    case 'compose':
      return {
        titulo: 'Give Mystique a mission',
        corpo: !chave
          ? [
              'Connect a model key first — she runs on your OpenRouter account, not ours.',
              'Then type what you need and she goes looking for whoever has the ability.',
            ]
          : exa
            ? ['Type what you need. She decides who to approach, and shows you every step.']
            : [
                'Type what you need. She decides who to approach, and shows you every step.',
                'Optional: connect Exa in the rail and the Good profile can search the web with sources.',
              ],
      }
  }
}

type Rect = { top: number; left: number; width: number; height: number }

export function Guia({ t, passo, total, indice, aoAvancar, aoFechar, chave, exa }: {
  t: (s: string) => string
  passo: PassoGuia
  total: number
  indice: number
  aoAvancar: () => void
  aoFechar: () => void
  chave: boolean
  exa: boolean
}) {
  const [alvo, setAlvo] = useState<Rect | null>(null)
  // The card is placed against its own measured height: a guessed one leaves it
  // overlapping the very control it is pointing at when the copy runs long.
  const carta = useRef<HTMLDivElement>(null)
  const [altura, setAltura] = useState(200)

  const medir = useCallback(() => {
    if (!passo.alvo) return setAlvo(null)
    const el = document.querySelector<HTMLElement>(`[data-guia="${passo.alvo}"]`)
    if (!el) return setAlvo(null)
    const r = el.getBoundingClientRect()
    setAlvo({ top: r.top, left: r.left, width: r.width, height: r.height })
  }, [passo.alvo])

  // The control itself is the highlight: it is raised through the veil and stays
  // usable, so the tour points at the real thing rather than at a picture of it.
  useLayoutEffect(() => {
    const el = passo.alvo ? document.querySelector<HTMLElement>(`[data-guia="${passo.alvo}"]`) : null
    el?.setAttribute('data-aceso', 'true')
    return () => el?.removeAttribute('data-aceso')
  }, [passo.alvo])

  useLayoutEffect(() => {
    const h = carta.current?.offsetHeight
    if (h && Math.abs(h - altura) > 1) setAltura(h)
  })

  // Measured after paint, and again whenever the page moves under it.
  useLayoutEffect(() => {
    medir()
    window.addEventListener('resize', medir)
    window.addEventListener('scroll', medir, true)
    return () => {
      window.removeEventListener('resize', medir)
      window.removeEventListener('scroll', medir, true)
    }
  }, [medir])

  useEffect(() => {
    const aoTeclar = (event: KeyboardEvent) => {
      if (event.key === 'Escape') aoFechar()
    }
    document.addEventListener('keydown', aoTeclar)
    return () => document.removeEventListener('keydown', aoTeclar)
  }, [aoFechar])

  const anterior = useRef<{ x: number; y: number } | null>(null)
  const { titulo, corpo } = conteudo(passo.id, chave, exa)
  const ultimo = indice === total - 1

  // The card is placed by transform only: it glides from the middle of the
  // screen to the control, and from one control to the next.
  const largura = Math.min(24 * 16, window.innerWidth - 32)
  let x = (window.innerWidth - largura) / 2
  let y = Math.max((window.innerHeight - altura) / 2, 16)
  let seta: 'cima' | 'baixo' | null = null
  if (alvo) {
    x = Math.min(Math.max(alvo.left + alvo.width / 2 - largura / 2, 16), window.innerWidth - largura - 16)
    const abaixo = alvo.top + alvo.height + 14
    const cabe = abaixo + altura + 16 < window.innerHeight
    y = cabe ? abaixo : Math.max(alvo.top - altura - 14, 16)
    seta = cabe ? 'cima' : 'baixo'
  }

  // How far it just travelled, capped so a long jump does not smear the screen.
  const veio = anterior.current
  const limite = (n: number) => Math.max(-28, Math.min(28, n * -0.14))
  const rastro = veio ? { x: limite(x - veio.x), y: limite(y - veio.y) } : { x: 0, y: 0 }
  anterior.current = { x, y }

  return (
    <div className="guia" role="dialog" aria-modal="true" aria-label={t('Guided tour')}>
      <div className="guia-veu" onClick={aoFechar} />
      <div
        key={passo.id}
        ref={carta}
        className="guia-carta"
        data-seta={seta ?? undefined}
        style={{
          width: `${largura}px`,
          transform: `translate3d(${x}px, ${y}px, 0)`,
          // The trail points back the way it came, so the colour reads as
          // something the card dragged with it rather than a glow it wears.
          ['--rastro-x' as string]: `${rastro.x}px`,
          ['--rastro-y' as string]: `${rastro.y}px`,
        }}
      >
        <p className="guia-passo">
          {indice + 1} / {total}
        </p>
        <h2>{t(titulo)}</h2>
        {corpo.map((linha) => (
          <p key={linha}>{t(linha)}</p>
        ))}
        <div className="guia-acoes">
          <button type="button" className="guia-pular" onClick={aoFechar}>
            {t('Skip')}
          </button>
          <button type="button" className="portao-primario" autoFocus onClick={ultimo ? aoFechar : aoAvancar}>
            {t(ultimo ? 'Got it' : 'Next')}
          </button>
        </div>
      </div>
    </div>
  )
}
