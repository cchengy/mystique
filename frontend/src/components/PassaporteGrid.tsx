import type { Passaporte } from "../lib/aguiClient";
import { AgenteCard } from "./AgenteCard";

export function PassaporteGrid({ passaporte }: { passaporte: Passaporte | null }) {
  if (!passaporte) return <p className="carregando">Connecting to the world…</p>;
  return (
    <div className="passaporte-grid">
      {passaporte.agentes.map((agente) => (
        <AgenteCard key={agente.id} agente={agente} modo={passaporte.modo} />
      ))}
    </div>
  );
}
