import type { AgenteSnapshot, Passaporte } from "../lib/aguiClient";
import { CapacidadeChip } from "./CapacidadeChip";

export function AgenteCard({ agente, modo }: { agente: AgenteSnapshot; modo: Passaporte["modo"] }) {
  const { feitos, total } = agente.progresso;
  const percentual = total > 0 ? Math.round((100 * feitos) / total) : 0;
  const completo = feitos >= total;

  return (
    <article className={`agente-card ${agente.descartado ? "agente-card--descartado" : ""}`}>
      <header>
        <h3>{agente.nome}</h3>
        {agente.externo && <span className="badge badge--externo">external</span>}
        {agente.descartado && <span className="badge badge--descartado">DISCARDED</span>}
        {!agente.descartado && completo && modo === "good" && (
          <span className="badge badge--completo">ADAPTER COMPLETE</span>
        )}
      </header>
      <p className="apresentacao">{agente.apresentacao}</p>
      <div className="barra" role="progressbar" aria-valuenow={percentual} aria-valuemin={0} aria-valuemax={100}>
        <div className="barra__preenchimento" style={{ width: `${percentual}%` }} />
      </div>
      <p className="progresso-texto">
        {feitos}/{total} ({percentual}%){agente.essencia_absorvida ? " · essence absorbed" : ""}
      </p>
      <div className="chips">
        {agente.capacidades.map((c) => (
          <CapacidadeChip key={c.id} capacidade={c} />
        ))}
      </div>
    </article>
  );
}
