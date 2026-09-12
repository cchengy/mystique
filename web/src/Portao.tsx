/** The gate in front of the live chat, and the screen that connects a key.
 *
 * The guided replay never renders this: it needs no account, no key and no
 * cookies, and that stays true.
 */
import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import {
  concluirOpenRouter, esquecerChave, estadoDaChave, guardarChave, iniciarOpenRouter,
  lerEu, type EstadoChave, type Eu,
} from './conta'

const MODELOS = 'https://openrouter.ai/api/v1/models'

export function BannerPrivacidade({ t }: { t: (s: string) => string }) {
  const [aceito, setAceito] = useState(() => {
    try { return localStorage.getItem('mystique.privacidade') === 'v1' } catch { return false }
  })
  if (aceito) return null
  return (
    <div className="privacidade" role="region" aria-label={t('Privacy notice')}>
      <div>
        <strong>{t('Cookies and personal data')}</strong>
        <p>
          {t('We store only what signing in requires: your Auth0 session in this browser, and, if you connect one, your model key — encrypted on our server and never shared. No analytics, no tracking, no third-party cookies.')}
        </p>
        <p>
          {t('Under the LGPD you may see, correct or delete this at any time: disconnecting your key erases it, and signing out ends the session. The guided replay needs none of it.')}
        </p>
      </div>
      <button
        type="button"
        onClick={() => {
          try { localStorage.setItem('mystique.privacidade', 'v1') } catch { /* ignore */ }
          setAceito(true)
        }}
      >
        {t('Understood')}
      </button>
    </div>
  )
}

export function PortaoConta({ t, aoLiberar }: { t: (s: string) => string; aoLiberar: (ok: boolean) => void }) {
  const { isLoading, isAuthenticated, loginWithRedirect, logout, user, getAccessTokenSilently } = useAuth0()
  const [eu, setEu] = useState<Eu | null>(null)
  const [estado, setEstado] = useState<EstadoChave | null>(null)
  const [colada, setColada] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [ocupado, setOcupado] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) { aoLiberar(false); return }
    let vivo = true
    ;(async () => {
      try {
        const token = await getAccessTokenSilently()
        await concluirOpenRouter(token).catch(() => null)   // volta do OpenRouter
        const dados = await lerEu(token)
        if (!vivo) return
        setEu(dados)
        aoLiberar(dados.chave.tem)
        if (dados.chave.tem) setEstado(await estadoDaChave(token).catch(() => null))
      } catch (e) {
        if (vivo) setErro(String(e).slice(0, 200))
      }
    })()
    return () => { vivo = false }
  }, [isAuthenticated, getAccessTokenSilently, aoLiberar])

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
        <p className="portao-sub">
          {t('So that what she learns is yours, kept apart from everyone else, and so the model runs on your key rather than ours.')}
        </p>
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
          <p className="portao-nota">
            <a href={MODELOS} target="_blank" rel="noreferrer">{t('See every model the key can reach')}</a>
          </p>
          <button disabled={ocupado} onClick={() => comToken(async (tk) => {
            await esquecerChave(tk); setEu({ ...eu, chave: { tem: false } }); setEstado(null); aoLiberar(false)
          })}>{t('Disconnect and erase my key')}</button>
        </>
      ) : (
        <>
          <h2>{t('Connect a model key')}</h2>
          <p className="portao-sub">
            {t('She runs on your OpenRouter account, not ours. Authorise and a key is created scoped to you — you never paste a secret.')}
          </p>
          <button className="portao-primario" disabled={ocupado} onClick={() => iniciarOpenRouter()}>
            {t('Authorise on OpenRouter')}
          </button>
          <details className="portao-colar">
            <summary>{t('Or paste a key instead')}</summary>
            <p className="portao-nota">{t('Works with any OpenRouter key. It is encrypted on our server and can be erased at any time.')}</p>
            <div className="portao-colar-row">
              <input
                type="password" value={colada} placeholder="sk-or-v1-…"
                onChange={(e) => setColada(e.target.value)} autoComplete="off" spellCheck={false}
              />
              <button disabled={ocupado || !colada.trim()} onClick={() => comToken(async (tk) => {
                const r = await guardarChave({ chave: colada.trim() }, tk)
                setColada(''); setEstado(r.estado); setEu(await lerEu(tk)); aoLiberar(true)
              })}>{t('Save')}</button>
            </div>
          </details>
        </>
      )}

      {erro && <p className="portao-erro" role="alert">{erro}</p>}
    </div>
  )
}
