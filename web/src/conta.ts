/** Account: who is signed in, and the key that answers for them.
 *
 * Identity comes from Auth0 (passkey through Universal Login). The model key does
 * NOT: Token Vault holds federated OAuth tokens, not a key the user brings, so the
 * server keeps it encrypted under the Auth0 `sub`.
 *
 * The key itself is obtained through OpenRouter's own PKCE flow, so the user
 * authorises on openrouter.ai and never pastes a secret. Pasting stays available
 * for people who prefer it.
 */
import { API_BASE } from './live'

export type AuthConfig = {
  exigida: boolean
  dominio: string | null
  audiencia: string | null
  cliente: string | null
}

export type Config = { modo: string; auth: AuthConfig; cofre: boolean }

export type EstadoChave = {
  chave?: { label?: string; usage?: number; limit?: number | null; is_free_tier?: boolean }
  creditos?: { total_credits?: number; total_usage?: number } | null
}

export type Eu = {
  sub: string
  email?: string
  nome?: string
  chave: Credencial
  exa: Credencial
  modelo: string
  ciclo?: { ultimo_acesso?: string; apagar_em?: string; dias_inatividade: number }
}

export type Credencial = { tem: boolean; expirada?: boolean; origem?: string; criada_em?: string; expira_em?: string }

export async function apagarConta(confirmacao: string, token?: string): Promise<void> {
  const r = await fetch(`${API_BASE}/api/conta`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', ...(comToken(token) ?? {}) },
    body: JSON.stringify({ confirmacao }),
  })
  if (!r.ok) throw new Error((await r.text()).slice(0, 200))
}

export async function lerConfig(): Promise<Config> {
  const r = await fetch(`${API_BASE}/api/config`)
  if (!r.ok) throw new Error('config')
  return r.json()
}

const comToken = (token?: string) =>
  token ? { Authorization: `Bearer ${token}` } : undefined

export async function lerEu(token?: string): Promise<Eu> {
  const r = await fetch(`${API_BASE}/api/eu`, { headers: comToken(token) })
  if (!r.ok) throw new Error(String(r.status))
  return r.json()
}

export async function estadoDaChave(token?: string): Promise<EstadoChave> {
  const r = await fetch(`${API_BASE}/api/openrouter/estado`, { headers: comToken(token) })
  if (!r.ok) throw new Error(String(r.status))
  return r.json()
}

export async function guardarChave(
  corpo: { chave?: string; codigo?: string; verificador?: string },
  token?: string,
): Promise<{ estado: EstadoChave }> {
  const r = await fetch(`${API_BASE}/api/openrouter/chave`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(comToken(token) ?? {}) },
    body: JSON.stringify(corpo),
  })
  if (!r.ok) throw new Error((await r.text()).slice(0, 200))
  return r.json()
}

export async function esquecerChave(token?: string): Promise<void> {
  await fetch(`${API_BASE}/api/openrouter/chave`, { method: 'DELETE', headers: comToken(token) })
}

export async function guardarExa(chave: string, token?: string): Promise<Credencial> {
  const r = await fetch(`${API_BASE}/api/exa/chave`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json', ...(comToken(token) ?? {}) },
    body: JSON.stringify({ chave }),
  })
  if (!r.ok) throw new Error((await r.text()).slice(0, 200))
  return r.json()
}

export async function esquecerExa(token?: string): Promise<void> {
  const r = await fetch(`${API_BASE}/api/exa/chave`, { method: 'DELETE', headers: comToken(token) })
  if (!r.ok) throw new Error((await r.text()).slice(0, 200))
}

export async function selecionarModelo(modelo: string, token?: string): Promise<void> {
  const r = await fetch(`${API_BASE}/api/openrouter/modelo`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...(comToken(token) ?? {}) },
    body: JSON.stringify({ modelo }),
  })
  if (!r.ok) throw new Error((await r.text()).slice(0, 200))
}

// --- OpenRouter PKCE ---------------------------------------------------------
// The verifier must survive the redirect, so it goes to sessionStorage: it is
// single-use, scoped to this tab, and gone when the tab closes.

const VERIF = 'mystique.or.verifier'

const base64url = (b: ArrayBuffer) =>
  btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')

export async function iniciarOpenRouter(): Promise<void> {
  const verificador = base64url(crypto.getRandomValues(new Uint8Array(32)).buffer)
  const desafio = base64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verificador)))
  try {
    sessionStorage.setItem(VERIF, verificador)
  } catch {
    /* storage blocked: the exchange below will simply fail and say so */
  }
  const url = new URL('https://openrouter.ai/auth')
  url.searchParams.set('callback_url', window.location.origin)
  url.searchParams.set('code_challenge', desafio)
  url.searchParams.set('code_challenge_method', 'S256')
  window.location.assign(url.toString())
}

/** Call on load: if OpenRouter sent us back with a code, finish the exchange. */
export async function concluirOpenRouter(token?: string): Promise<{ estado: EstadoChave } | null> {
  const params = new URLSearchParams(window.location.search)
  const codigo = params.get('code')
  if (!codigo) return null

  // Auth0 comes back on the same URL with ?code=&state=, so a bare `code` is not
  // proof the code is ours. Two tells: Auth0 always sends `state`, and only our
  // own flow leaves a verifier behind. Touching Auth0's code - or worse, clearing
  // the URL before its SDK reads it - makes the login silently do nothing.
  if (params.get('state')) return null

  let verificador: string | null = null
  try {
    verificador = sessionStorage.getItem(VERIF)
  } catch {
    /* ignore */
  }
  if (!verificador) return null

  try { sessionStorage.removeItem(VERIF) } catch { /* ignore */ }
  // Only now is the URL ours to clean, so a refresh cannot retry a spent code.
  window.history.replaceState({}, '', window.location.pathname)
  return guardarChave({ codigo, verificador }, token)
}
