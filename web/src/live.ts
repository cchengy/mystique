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

export type SessionMessage = { role: 'user' | 'assistant' | 'system' | 'dialogo'; content: string; de?: string; para?: string }
export type ReasoningEvidence = {
  id: string; agent_id?: string; outcome?: string; title?: string; description?: string;
  content?: string; source_kind?: string; usage_count?: number
}
export type ChatSession = {
  id: string; titulo: string; modo: 'good' | 'evil'; created_at: string; updated_at: string;
  mensagens?: SessionMessage[]; evidencias?: ReasoningEvidence[]
}

type LiveHandlers = {
  snapshot: (value: LiveSnapshot) => void
  receipt: (value: LiveReceipt) => void
  resolved: (id: string) => void
  connected: (value: boolean) => void
  status: (value: string) => void
  dialogue: (from: string, to: string, text: string) => void
  token?: string
  // The server sends the English source string as the key plus the agent name,
  // so the browser translates and only then fills the name in.
  sessionId?: string
  steer: (value: string) => void
  improvement: (value: string, agent: string) => void
  decision: (value: string, approved: boolean, agent: string) => void
  final: (value: string, error: boolean) => void
  mission: (running: boolean, message?: string) => void
}

export function connectLive(handlers: LiveHandlers): () => void {
  const controller = new AbortController()
  const dispatch = (data: string) => {
    const event = JSON.parse(data) as {
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
    if (event.type === 'CUSTOM' && event.name === 'status') {
      handlers.status((event.value as { texto: string }).texto)
    }
    if (event.type === 'CUSTOM' && event.name === 'dialogo') {
      const value = event.value as { de: string; para: string; texto: string }
      handlers.dialogue(value.de, value.para, value.texto)
    }
    // Steering: what the person typed while she was working, echoed back so it
    // appears in the transcript the moment the run accepts it.
    if (event.type === 'CUSTOM' && event.name === 'orientacao') {
      handlers.steer((event.value as { texto: string }).texto)
    }
    if (event.type === 'CUSTOM' && event.name === 'melhoria') {
      const value = event.value as { texto: string; agente?: string }
      handlers.improvement(value.texto, value.agente ?? '')
    }
    if (event.type === 'CUSTOM' && event.name === 'decisao_automatica') {
      const value = event.value as { texto: string; aprovado: boolean; agente?: string }
      handlers.decision(value.texto, value.aprovado, value.agente ?? '')
    }
    if (event.type === 'CUSTOM' && event.name === 'resposta_final') {
      const value = event.value as { texto: string; erro?: boolean }
      handlers.final(value.texto, Boolean(value.erro))
    }
    if (event.type === 'CUSTOM' && event.name === 'missao_iniciada') {
      // On reconnect the server sends this without a message: it is telling us
      // this conversation is already working, not that a new mission started.
      handlers.mission(true, (event.value as { mensagem?: string }).mensagem)
    }
    if (event.type === 'CUSTOM' && event.name === 'missao_finalizada') handlers.mission(false)
  }
  void (async () => {
    try {
      // The stream belongs to one conversation: without this, a run started in
      // another chat of the same account arrived here.
      const alvo = handlers.sessionId
        ? `${API_BASE}/agui/stream?sessao=${encodeURIComponent(handlers.sessionId)}`
        : `${API_BASE}/agui/stream`
      const response = await fetch(alvo, {
        headers: handlers.token ? { Authorization: `Bearer ${handlers.token}` } : {},
        signal: controller.signal,
      })
      if (!response.ok || !response.body) throw new Error(`stream ${response.status}`)
      handlers.connected(true)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() ?? ''
        for (const frame of frames) {
          const data = frame.split('\n').filter((line) => line.startsWith('data:')).map((line) => line.slice(5).trim()).join('')
          if (data) dispatch(data)
        }
      }
    } catch (error) {
      if (!controller.signal.aborted) handlers.connected(false)
    }
  })()
  return () => controller.abort()
}

function authHeaders(token?: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function listSessions(token?: string): Promise<ChatSession[]> {
  const response = await fetch(`${API_BASE}/api/sessoes`, { headers: authHeaders(token) })
  if (!response.ok) throw new Error(`Sessions could not load (${response.status})`)
  return response.json()
}

export async function createSession(mode: 'good' | 'evil', token?: string): Promise<ChatSession> {
  const response = await fetch(`${API_BASE}/api/sessoes`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ titulo: 'New conversation', modo: mode }),
  })
  if (!response.ok) throw new Error(`Session could not be created (${response.status})`)
  return response.json()
}

export async function getSession(id: string, token?: string): Promise<ChatSession> {
  const response = await fetch(`${API_BASE}/api/sessoes/${id}`, { headers: authHeaders(token) })
  if (!response.ok) throw new Error(`Session could not load (${response.status})`)
  return response.json()
}

export async function startLiveMission(message: string, sessionId: string, token?: string, idioma: 'en' | 'pt' = 'en'): Promise<void> {
  const response = await fetch(`${API_BASE}/api/missoes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    // She answers in the language the person is reading the app in.
    body: JSON.stringify({ mensagem: message, sessao_id: sessionId, idioma }),
  })
  if (!response.ok) throw new Error(`Mission could not start (${response.status})`)
}

export async function stopLiveMission(sessionId: string, token?: string): Promise<void> {
  await fetch(`${API_BASE}/api/missoes/${sessionId}`, {
    method: 'DELETE',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
}

export async function resolveLiveReceipt(id: string, decision: 'aprovar' | 'rejeitar'): Promise<void> {
  const response = await fetch(`${API_BASE}/api/recibos/${id}/decisao`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decisao: decision }),
  })
  if (!response.ok) throw new Error(`Decision was refused (${response.status})`)
}

export type WikiPage = {
  modo: string
  texto: string
  resumo: { total?: number; outcomes?: Record<string, number>; most_reused?: number; unreadable?: number }
}

/** What she has learned, as the engine itself writes it: one page per profile.
 *  Read-only, and only ever this account's own bank. */
export async function getWiki(modo: 'good' | 'evil', token?: string): Promise<WikiPage> {
  const response = await fetch(`${API_BASE}/api/wiki?modo=${modo}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  if (!response.ok) throw new Error(String(response.status))
  return response.json()
}
