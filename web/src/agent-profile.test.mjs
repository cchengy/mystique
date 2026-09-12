import assert from 'node:assert/strict'
import test from 'node:test'

import { latestAgentInteractions } from './agent-profile.ts'

test('seleciona apenas as interações recentes entre a Mystique e o agente', () => {
  const result = latestAgentInteractions([
    { from: 'Mystique', to: 'Byte', text: 'Pode revisar este código?' },
    { from: 'Byte', to: 'Mystique', text: 'Posso. Envie o erro.' },
    { from: 'Mystique', to: 'Dona Cida', text: 'Preciso de um conselho.' },
    { from: 'Mystique', to: 'Byte', text: 'Aqui está o traceback.' },
  ], ['byte', 'Byte'], 2)

  assert.deepEqual(result.map(({ text }) => text), [
    'Posso. Envie o erro.',
    'Aqui está o traceback.',
  ])
})
