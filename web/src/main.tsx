import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Auth0Provider } from '@auth0/auth0-react'
import './styles.css'
import Simulation from './Simulation.tsx'
import { lerConfig, type AuthConfig } from './conta'

/** The tenant is read from the server, not hardcoded, so switching the API
 *  audience is one environment variable and no rebuild.
 *
 *  `audience` is not optional: without it Auth0 returns an opaque access token
 *  and the server, which verifies a JWT against the tenant JWKS, rejects every
 *  request. The symptom is a successful login that the API refuses.
 *
 *  With no tenant configured the app renders unwrapped: local development and the
 *  guided replay both work with no account at all. */
function Raiz() {
  const [auth, setAuth] = useState<AuthConfig | null>(null)
  const [pronto, setPronto] = useState(false)

  useEffect(() => {
    lerConfig()
      .then((c) => setAuth(c.auth))
      .catch(() => setAuth(null))
      .finally(() => setPronto(true))
  }, [])

  if (!pronto) return null
  if (!auth?.exigida || !auth.dominio || !auth.cliente) return <Simulation />

  return (
    <Auth0Provider
      domain={auth.dominio}
      clientId={auth.cliente}
      authorizationParams={{
        redirect_uri: window.location.origin,
        ...(auth.audiencia ? { audience: auth.audiencia } : {}),
      }}
      useRefreshTokens
      cacheLocation="localstorage"
    >
      <Simulation />
    </Auth0Provider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Raiz />
  </StrictMode>,
)
