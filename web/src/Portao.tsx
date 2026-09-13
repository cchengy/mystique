/** The gate in front of the live chat, and the screen that connects a key.
 *
 * The guided replay never renders this: it needs no account, no key and no
 * cookies, and that stays true.
 */
import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import {
  apagarConta, concluirOpenRouter, esquecerChave, esquecerExa, estadoDaChave, guardarChave, guardarExa, iniciarOpenRouter,
  lerEu, selecionarModelo, type EstadoChave, type Eu,
} from './conta'

const MODELOS = 'https://openrouter.ai/api/v1/models'

export function aceitouPrivacidade(): boolean {
  try { return localStorage.getItem('mystique.privacidade') === 'v1' } catch { return false }
}

/** The notice. Accepting it is remembered, but it must stay reachable
 *  afterwards: a consent notice you cannot read again is not a notice. The
 *  caller owns "is it open", so a Privacy link can bring it back. */
export function BannerPrivacidade({ t, aoFechar }: { t: (s: string) => string; aoFechar: () => void }) {
  return (
    <div className="privacidade" role="region" aria-label={t('Privacy notice')}>
      <div>
        <strong>{t('Cookies and personal data')}</strong>
        <p>
          {t('Auth0 keeps your login session. Provider keys are encrypted in a separate credential container and erased after 24 hours. Conversations and memory are retained for up to 60 inactive days. No analytics or advertising trackers.')}
        </p>
        <p>
          {t('Under the LGPD you may delete Mystique data at any time. Signing out does not delete data; disconnecting a provider erases its key. The guided replay needs none of it.')}
        </p>
      </div>
      <button
        type="button"
        onClick={() => {
          try { localStorage.setItem('mystique.privacidade', 'v1') } catch { /* ignore */ }
          aoFechar()
        }}
      >
        {t('Understood')}
      </button>
    </div>
  )
}

export function PortaoConta({ t, aoLiberar }: { t: (s: string) => string; aoLiberar: (ok: boolean, token?: string) => void }) {
  const { isLoading, isAuthenticated, loginWithRedirect, logout, user, getAccessTokenSilently, error: erroAuth0 } = useAuth0()
  const [eu, setEu] = useState<Eu | null>(null)
  const [estado, setEstado] = useState<EstadoChave | null>(null)
  const [colada, setColada] = useState('')
  const [exa, setExa] = useState('')
  const [modelo, setModelo] = useState('openrouter/auto')
  const [modelos, setModelos] = useState<string[]>([])
  const [erro, setErro] = useState<string | null>(null)
  const [ocupado, setOcupado] = useState(false)
  const [confirmacao, setConfirmacao] = useState('')

  useEffect(() => {
    if (!isAuthenticated) { aoLiberar(false); return }
    let vivo = true
    ;(async () => {
      try {
        const token = await getAccessTokenSilently()
        // Coming back from OpenRouter. Swallowing this failure is what made a
        // broken exchange look like the page simply doing nothing: say it.
        try {
          await concluirOpenRouter(token)
        } catch (e) {
          if (vivo) setErro(`${t('The OpenRouter authorisation could not be completed')}: ${String(e).slice(0, 200)}`)
        }
        const dados = await lerEu(token)
        if (!vivo) return
        setEu(dados)
        setModelo(dados.modelo)
        // The token goes up with the verdict: Simulation must never call useAuth0
        // itself, because outside a provider that hook throws and the open,
        // no-tenant deployment would stop rendering at all.
        aoLiberar(dados.chave.tem, token)
        if (dados.chave.tem) setEstado(await estadoDaChave(token).catch(() => null))
      } catch (e) {
        if (vivo) setErro(String(e).slice(0, 200))
      }
    })()
    return () => { vivo = false }
  }, [isAuthenticated, getAccessTokenSilently, aoLiberar])

  useEffect(() => {
    if (!eu?.chave.tem) return
    fetch(MODELOS)
      .then((r) => r.ok ? r.json() : Promise.reject(new Error(String(r.status))))
      .then((body: { data?: { id?: string }[] }) =>
        setModelos((body.data ?? []).flatMap((item) => item.id ? [item.id] : [])))
      .catch(() => setModelos([]))
  }, [eu?.chave.tem])

  const comToken = async (fn: (token: string) => Promise<unknown>) => {
    setErro(null); setOcupado(true)
    try { await fn(await getAccessTokenSilently()) } catch (e) { setErro(String(e).slice(0, 200)) }
    finally { setOcupado(false) }
  }

  if (isLoading) return <div className="portao"><p>{t('Checking your session…')}</p></div>

  if (!isAuthenticated) {
    return (
      <div className="portao">
        <h2>{t('The live chat needs an account')}</h2>
        {/* Without this the tenant refusing - sign-ups disabled, a URL not on the
            allow list - looks like the page simply reloading and doing nothing. */}
        {erroAuth0 && <p className="portao-erro" role="alert">{erroAuth0.message}</p>}
        <p className="portao-sub">
          {t('So that what she learns is yours, kept apart from everyone else, and so the model runs on your key rather than ours.')}
        </p>
        <div className="security-brief" role="note">
          <strong>{t('Before you continue')}</strong>
          <ul>
            <li>{t('Provider keys are encrypted in a separate credential container and erased after 24 hours.')}</li>
            <li>{t('Conversations and Mystique memory are erased after 60 days without a successful sign-in.')}</li>
            <li>{t('This is defense in depth on a standard VPS, not zero-knowledge: the server operator could technically access running systems.')}</li>
          </ul>
        </div>
        <div className="portao-acoes">
          <button className="portao-primario" onClick={() => loginWithRedirect()}>{t('Sign in with a passkey')}</button>
          <button onClick={() => loginWithRedirect({ authorizationParams: { screen_hint: 'signup' } })}>
            {t('Create an account')}
          </button>
        </div>
        <p className="portao-nota">{t('The guided replay needs none of this — it is open to everyone.')}</p>
      </div>
    )
  }

  return (
    <div className="portao">
      <div className="portao-quem">
        <span>{t('Signed in as')} <strong>{eu?.email ?? user?.email ?? eu?.sub}</strong></span>
        <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>{t('Sign out')}</button>
      </div>

      {eu?.chave.tem ? (
        <>
          <h2>{t('Your key is connected')}</h2>
          <p className="credential-deadline"><span>{t('Temporary credential')}</span> {t('Automatically erased')}: <strong>{eu.chave.expira_em ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(eu.chave.expira_em)) : t('within 24 hours')}</strong></p>
          <dl className="portao-estado">
            <dt>{t('Source')}</dt>
            <dd>{eu.chave.origem === 'openrouter-oauth' ? t('authorised on OpenRouter') : t('pasted by you')}</dd>
            {estado?.chave?.label && (<><dt>{t('Label')}</dt><dd>{estado.chave.label}</dd></>)}
            {estado?.chave?.limit != null && (<><dt>{t('Limit')}</dt><dd>{estado.chave.limit}</dd></>)}
            {estado?.chave?.usage != null && (<><dt>{t('Used')}</dt><dd>{estado.chave.usage}</dd></>)}
            {estado?.creditos?.total_credits != null && (
              <><dt>{t('Credits')}</dt><dd>{estado.creditos.total_credits}</dd></>
            )}
          </dl>
          <label className="model-search-label" htmlFor="openrouter-model-search">
            {t('Conversation model')}
            <small>{t('Type to search every model available on OpenRouter.')}</small>
          </label>
          <div className="portao-colar-row">
            <input
              id="openrouter-model-search"
              list="openrouter-models"
              value={modelo}
              aria-label={t('OpenRouter model')}
              onChange={(e) => setModelo(e.target.value)}
              autoComplete="off"
              spellCheck={false}
            />
            <datalist id="openrouter-models">
              {modelos.map((id) => <option key={id} value={id} />)}
            </datalist>
            <button disabled={ocupado || !modelo.trim() || modelo === eu.modelo} onClick={() => comToken(async (tk) => {
              await selecionarModelo(modelo.trim(), tk)
              setEu({ ...eu, modelo: modelo.trim() })
            })}>{t('Use model')}</button>
          </div>
          <p className="portao-nota">
            <a href={MODELOS} target="_blank" rel="noreferrer">{t('See every model the key can reach')}</a>
          </p>
          <button disabled={ocupado} onClick={() => comToken(async (tk) => {
            await esquecerChave(tk); setEu({ ...eu, chave: { tem: false } }); setEstado(null); aoLiberar(false, tk)
          })}>{t('Disconnect and erase my key')}</button>
        </>
      ) : (
        <>
          <h2>{t('Connect a model key')}</h2>
          <p className="portao-sub">
            {t('She runs on your OpenRouter account, not ours. Authorise and a key is created scoped to you — you never paste a secret.')}
          </p>
          <p className="credential-policy">{t('For your protection, the credential expires exactly 24 hours after you connect it. Using Mystique does not extend that deadline; you will need to reconnect.')}</p>
          <button className="portao-primario" disabled={ocupado} onClick={() => iniciarOpenRouter()}>
            {t('Authorise on OpenRouter')}
          </button>
          <details className="portao-colar">
            <summary>{t('Or paste a key instead')}</summary>
            <p className="portao-nota">{t('Works with any OpenRouter key. It is encrypted inside the isolated credential container and erased within 24 hours or immediately when you disconnect it.')}</p>
            <div className="portao-colar-row">
              <input
                type="password" value={colada} placeholder="sk-or-v1-…"
                onChange={(e) => setColada(e.target.value)} autoComplete="off" spellCheck={false}
              />
              <button disabled={ocupado || !colada.trim()} onClick={() => comToken(async (tk) => {
                const r = await guardarChave({ chave: colada.trim() }, tk)
                setColada(''); setEstado(r.estado); setEu(await lerEu(tk)); aoLiberar(true, tk)
              })}>{t('Save')}</button>
            </div>
          </details>
        </>
      )}

      <section className="provider-card" aria-labelledby="exa-provider-title">
        <div>
          <p className="eyebrow">BYOK · EXA</p>
          <h3 id="exa-provider-title">{t('Web retrieval')}</h3>
          <p>{t('Optional. Exa gives the Good profile current web retrieval with sources. The Evil profile remains blocked from real-world tools.')}</p>
        </div>
        {eu?.exa?.tem ? (
          <div className="provider-connected">
            <p><strong>{t('Connected until')}</strong> {eu.exa.expira_em ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(eu.exa.expira_em)) : t('within 24 hours')}</p>
            <button disabled={ocupado} onClick={() => comToken(async (tk) => { await esquecerExa(tk); setEu({ ...eu, exa: { tem: false } }) })}>{t('Disconnect Exa')}</button>
          </div>
        ) : (
          <div>
            <label htmlFor="exa-key">{t('Exa API key')}</label>
            <div className="portao-colar-row">
              <input id="exa-key" type="password" value={exa} placeholder="exa-…" onChange={(e) => setExa(e.target.value)} autoComplete="off" spellCheck={false} />
              <button disabled={ocupado || !exa.trim()} onClick={() => comToken(async (tk) => {
                const saved = await guardarExa(exa.trim(), tk); setExa(''); setEu({ ...eu!, exa: saved })
              })}>{t('Connect for 24 hours')}</button>
            </div>
          </div>
        )}
      </section>

      {(erro || erroAuth0) && <p className="portao-erro" role="alert">{erro ?? erroAuth0?.message}</p>}

      <section className="account-lifecycle" aria-labelledby="account-lifecycle-title">
        <h3 id="account-lifecycle-title">{t('Your data lifecycle')}</h3>
        <p>{t('Mystique permanently deletes conversations, Reasoning Bank history, learned profiles and settings after 60 days without a successful sign-in. Provider keys follow the shorter 24-hour rule above.')}</p>
        {eu?.ciclo?.apagar_em && <p className="deletion-date">
          {t('Current deletion deadline')}: <strong>{new Intl.DateTimeFormat(undefined, { dateStyle: 'long' }).format(new Date(eu.ciclo.apagar_em))}</strong>
        </p>}
        <details className="danger-zone">
          <summary>{t('Delete my Mystique data now')}</summary>
          <p>{t('This permanently removes your provider credentials, conversations, memory and settings. It does not delete your Auth0 identity. This cannot be undone.')}</p>
          <label htmlFor="delete-account-confirmation">{t('Type APAGAR MINHA CONTA to confirm')}</label>
          <div className="portao-colar-row">
            <input id="delete-account-confirmation" value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} autoComplete="off" />
            <button className="danger-button" disabled={ocupado || confirmacao !== 'APAGAR MINHA CONTA'} onClick={() => comToken(async (tk) => {
              await apagarConta(confirmacao, tk)
              logout({ logoutParams: { returnTo: window.location.origin } })
            })}>{t('Delete permanently')}</button>
          </div>
        </details>
      </section>
    </div>
  )
}
