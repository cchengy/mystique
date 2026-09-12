import { useState } from "react";
import { decidirRecibo, type ReciboPendente } from "../lib/aguiClient";

// US1: the trust receipt. Shown for every recognition attempt (FR-001), including ones the
// judge already rejected (approve stays disabled then — Acceptance Scenario 4). Approving or
// rejecting calls the real backend action (FR-002/FR-003); nothing here is cosmetic.
export function CartaoDeRecibo({ recibos }: { recibos: ReciboPendente[] }) {
  const [emAndamento, setEmAndamento] = useState<string | null>(null);

  if (recibos.length === 0) return null;

  async function decidir(recibo: ReciboPendente, decisao: "aprovar" | "rejeitar") {
    setEmAndamento(recibo.recibo_id);
    try {
      await decidirRecibo(recibo.recibo_id, decisao);
    } finally {
      setEmAndamento(null);
    }
  }

  return (
    <div className="recibos-pilha">
      {recibos.map((recibo) => (
        <article key={recibo.recibo_id} className="recibo-cartao">
          <header>Recognition attempt · {recibo.agente_id}</header>
          <dl>
            <dt>Claimed description</dt>
            <dd>{recibo.descricao_alegada}</dd>
            <dt>Evidence</dt>
            <dd>{recibo.evidencia}</dd>
            <dt>Judge's verdict</dt>
            <dd className={recibo.veredito.aprovado ? "veredito--aprovado" : "veredito--rejeitado"}>
              {recibo.veredito.aprovado ? "Approved" : "Rejected"} — {recibo.veredito.motivo}
            </dd>
          </dl>
          <div className="recibo-acoes">
            <button
              disabled={!recibo.veredito.aprovado || emAndamento === recibo.recibo_id}
              onClick={() => decidir(recibo, "aprovar")}
            >
              Approve
            </button>
            <button
              className="secundario"
              disabled={emAndamento === recibo.recibo_id}
              onClick={() => decidir(recibo, "rejeitar")}
            >
              Reject
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}
