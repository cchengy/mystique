import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

test('reconnects the live stream after Auth0 supplies an access token', () => {
  const source = readFileSync(new URL('./Simulation.tsx', import.meta.url), 'utf8')
  assert.match(source, /connectLive\([\s\S]*?\),\s*\[token, sessionId, refreshSessions\],\s*\)/)
  assert.match(readFileSync(new URL('./live.ts', import.meta.url), 'utf8'), /Authorization: `Bearer \$\{handlers\.token\}`/)
})

test('shows and saves an OpenRouter model selection', () => {
  const source = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  assert.match(source, /list="openrouter-models"/)
  assert.match(source, /selecionarModelo\(/)
  assert.match(source, /Digite para pesquisar/)
})

test('discloses both retention windows and Exa BYOK before use', () => {
  const source = readFileSync(new URL('./Portao.tsx', import.meta.url), 'utf8')
  assert.match(source, /erased after 24 hours/)
  assert.match(source, /60 days without a successful sign-in/)
  assert.match(source, /not zero-knowledge/)
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
