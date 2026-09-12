import type { Capacidade } from "../lib/aguiClient";

const RÓTULOS: Record<Capacidade["estado"], string> = {
  nao_observada: "not observed",
  observada_pendente: "observed · pending",
  confirmada: "confirmed",
  rejeitada: "rejected",
};

export function CapacidadeChip({ capacidade }: { capacidade: Capacidade }) {
  const titulo = capacidade.estado === "rejeitada" && capacidade.motivo ? capacidade.motivo : undefined;
  return (
    <span className={`chip chip--${capacidade.estado}`} title={titulo}>
      {RÓTULOS[capacidade.estado]}
    </span>
  );
}
