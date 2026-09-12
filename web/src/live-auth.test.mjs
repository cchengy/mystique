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
