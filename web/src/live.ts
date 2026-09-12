export const API_BASE =
  import.meta.env.VITE_API_BASE ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : window.location.origin)

export type LiveAgent = {
  id: string
  nome: string
  apresentacao: string
  capacidades: { id: string; estado: string; motivo: string | null }[]
  descartado: boolean
  progresso: { feitos: number; total: number }
}

export type LiveSnapshot = {
  modo: 'good' | 'evil'
  agentes: LiveAgent[]
}

export type LiveReceipt = {
  recibo_id: string
  agente_id: string
  descricao_alegada: string
  evidencia: string
  veredito: { aprovado: boolean; motivo: string }
}

type LiveHandlers = {
  snapshot: (value: LiveSnapshot) => void
  receipt: (value: LiveReceipt) => void
  resolved: (id: string) => void
  connected: (value: boolean) => void
  narration: (value: string) => void
  mission: (running: boolean, message?: string) => void
}

export function connectLive(handlers: LiveHandlers): () => void {
  const source = new EventSource(`${API_BASE}/agui/stream`)
  source.onopen = () => handlers.connected(true)
  source.onerror = () => handlers.connected(false)
  source.onmessage = (message) => {
    const event = JSON.parse(message.data) as {
      type: string
      name?: string
      value?: unknown
      snapshot?: unknown
    }
    if (event.type === 'STATE_SNAPSHOT') handlers.snapshot(event.snapshot as LiveSnapshot)
    if (event.type === 'CUSTOM' && event.name === 'recibo_pendente') handlers.receipt(event.value as LiveReceipt)
    if (event.type === 'CUSTOM' && event.name === 'recibo_resolvido') {
      handlers.resolved((event.value as { recibo_id: string }).recibo_id)
    }
    if (event.type === 'CUSTOM' && event.name === 'narracao') {
      handlers.narration((event.value as { texto: string }).texto)
    }
    if (event.type === 'CUSTOM' && event.name === 'missao_iniciada') {
      handlers.mission(true, (event.value as { mensagem: string }).mensagem)
    }
    if (event.type === 'CUSTOM' && event.name === 'missao_finalizada') handlers.mission(false)
  }
  return () => source.close()
}

export async function startLiveMission(message: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/missoes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mensagem: message }),
  })
  if (!response.ok) throw new Error(`Mission could not start (${response.status})`)
}

export async function resolveLiveReceipt(id: string, decision: 'aprovar' | 'rejeitar'): Promise<void> {
  const response = await fetch(`${API_BASE}/api/recibos/${id}/decisao`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decisao: decision }),
  })
  if (!response.ok) throw new Error(`Decision was refused (${response.status})`)
}
