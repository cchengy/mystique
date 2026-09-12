import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import Simulation from './Simulation.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Simulation />
  </StrictMode>,
)
