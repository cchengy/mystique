import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

test('reconnects the live stream after Auth0 supplies an access token', () => {
  const source = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  assert.match(source, /connectLive\([\s\S]*?\[authExigida, liberado, token, sessionId, refreshSessions, t\],\s*\)/)
  assert.match(readFileSync(new URL('./live.ts', import.meta.url), 'utf8'), /Authorization: `Bearer \$\{handlers\.token\}`/)
})

test('shows and saves an OpenRouter model selection', () => {
  const source = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  assert.match(source, /list="openrouter-models"/)
  assert.match(source, /selecionarModelo\(/)
  assert.match(source, /Type to search every model/)
})

test('discloses both retention windows and Exa BYOK before use', () => {
  const source = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  assert.match(source, /erased after 24 hours/)
  assert.match(source, /60 days without using Mystique/)
  // The claim must never be made, and the honest statement must exist somewhere a
  // person reads - the privacy notice - rather than as VPS trivia on the gate.
  assert.match(source, /not a zero-knowledge one/)
  assert.doesNotMatch(source, /server operator could technically access/)
  assert.match(source, /guardarExa\(/)
})

test('the single-use OpenRouter code is exchanged once, not raced', () => {
  // Two effect runs used to exchange and read in parallel, so the panel could
  // report "no key" over a connection that had just succeeded.
  const source = readFileSync(new URL('./conta.ts', import.meta.url), 'utf8')
  assert.match(source, /let troca: Promise<[\s\S]*?> \| null = null/)
  assert.match(source, /if \(!troca\) troca = _concluirOpenRouter\(token\)/)
})

test('a failed OpenRouter return is stated, not swallowed', () => {
  const source = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  assert.doesNotMatch(source, /concluirOpenRouter\(token\)\.catch/)
  assert.match(source, /The OpenRouter authorisation could not be completed/)
})

test('the conversation rail stays on screen, locked, while the gate is up', () => {
  const source = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  assert.match(source, /const travada = Boolean\(authExigida && !liberado\)/)
  assert.match(source, /data-locked=\{travada \? 'true' : undefined\}/)
  assert.match(readFileSync(new URL('./styles.css', import.meta.url), 'utf8'), /\.session-list\.is-locked/)
})

test('every string ships in English and the language choice persists', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  const gate = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  // Portuguese belongs in pt.ts, keyed by the English source - never inline in a
  // component, or the other language has nothing to fall back to.
  const inline = [...ui.matchAll(/[>'"`][^<>'"`\n]*[áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ][^<>'"`\n]*['"`<]/g)]
    .map((m) => m[0])
    .filter((m) => !m.includes('Você'))   // legacy transcript migration, matched by value
  assert.deepEqual(inline, [], `translate these into pt.ts: ${inline.join(' | ')}`)
  assert.doesNotMatch(gate, /t\('[^']*[áàâãéêíóôõúç]/)
  assert.match(ui, /localStorage\.setItem\('mystique\.lang', lang\)/)
  assert.match(ui, /aria-checked=\{lang === code\}/)
})

test('the privacy notice can be reopened after it is accepted', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  assert.match(ui, /className="privacy-link"/)
  assert.match(ui, /setPrivacidadeAberta\(true\)/)
  assert.match(readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8'), /export function aceitouPrivacidade/)
})

test('the gate is a modal scene that plays out before it lets go', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  const css = readFileSync(new URL('./styles.css', import.meta.url), 'utf8')
  assert.match(ui, /className="portao-cena"/)
  assert.match(ui, /aria-modal="true"/)
  // It must not simply disappear the instant the account unlocks.
  assert.match(ui, /setPortaoSaindo\(true\)/)
  assert.match(css, /@keyframes carta-morfa/)
  // Every spatial animation needs its reduced-motion path.
  assert.match(css, /prefers-reduced-motion: reduce\)\s*\{\s*\.portao-fundo/)
})

test('the gate keeps the keyboard inside it, and gives focus back', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  assert.match(ui, /function useFocoPreso/)
  assert.match(ui, /const focoPortao = useFocoPreso/)
  assert.match(ui, /ref=\{focoPortao\}/)
  assert.match(ui, /anterior\?\.focus\?\.\(\)/)
})

test('a new account inherits nothing from the browser', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  const api = readFileSync(new URL('./live.ts', import.meta.url), 'utf8')
  // The pre-accounts transcript must never become a new account's first session.
  assert.doesNotMatch(ui, /importSession/)
  assert.doesNotMatch(api, /importSession/)
  assert.match(ui, /localStorage\.removeItem\('mystique\.live\.v1\.messages'\)/)
})

test('the tour covers every control, in order, and is translated', () => {
  const guia = readFileSync(new URL('./Guia.tsx', import.meta.url), 'utf8')
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  const pt = readFileSync(new URL('./pt.ts', import.meta.url), 'utf8')

  const inicio = guia.indexOf('= [', guia.indexOf('export const PASSOS'))
  const lista = guia.slice(inicio, guia.indexOf(']', inicio))
  const ordem = [...lista.matchAll(/\{ id: '([^']+)'/g)].map((m) => m[1])
  assert.deepEqual(ordem,
    ['intro-1', 'intro-2', 'good', 'evil', 'replay', 'live', 'compare', 'modelo', 'busca', 'compose'])
  // Compare comes before the composer: you are told what the endings are before
  // you are asked to produce one.
  assert.ok(ordem.indexOf('compare') < ordem.indexOf('compose'))

  // Every control the tour points at must actually be marked in the interface.
  // good/evil come from the mode list, so they are marked by expression.
  assert.match(ui, /data-guia=\{m\}/)
  for (const alvo of ['replay', 'live', 'compare', 'compose']) {
    assert.match(ui, new RegExp(`data-guia="${alvo}"`), `no control marked ${alvo}`)
  }
  // and the two that live inside the rail drawer
  assert.match(ui, /data-guia="modelo"/)
  assert.match(readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8'), /data-guia="busca"/)
  // and every line it says must have a Portuguese counterpart
  for (const [, linha] of guia.matchAll(/^\s+'([A-Z][^']{20,})',?$/gm)) {
    assert.ok(pt.includes(`'${linha}'`), `untranslated tour line: ${linha}`)
  }
})

test('the tour is remembered on the account, and can be replayed', () => {
  const ui = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  const api = readFileSync(new URL('./conta.ts', import.meta.url), 'utf8')
  assert.match(api, /api\/conta\/onboarding/)
  assert.match(ui, /if \(!dados\.onboarding_visto\) setGuia\(0\)/)
  assert.match(ui, /className="theme guia-botao" onClick=\{abrirGuia\}/)
})
