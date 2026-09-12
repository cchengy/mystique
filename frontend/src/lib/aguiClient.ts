// Thin AG-UI client: consumes the SSE stream published by servidor/app.py (`GET /agui/stream`,
// encoded with the ag-ui-protocol Python package) and wraps the companion REST actions.
// Plain EventSource + fetch — no @ag-ui/client dependency, see specs/001-corretora-de-confianca.

export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export type EstadoCapacidade = "nao_observada" | "observada_pendente" | "confirmada" | "rejeitada";

export interface Capacidade {
  id: string;
  estado: EstadoCapacidade;
  motivo: string | null;
}

export interface AgenteSnapshot {
  id: string;
  nome: string;
  apresentacao: string;
  externo: boolean;
  capacidades: Capacidade[];
  descartado: boolean;
  essencia_absorvida: boolean;
  progresso: { feitos: number; total: number };
}

export interface AbsorcaoSnapshot {
  agente_id: string;
  nome: string;
  perfil: Record<string, unknown> | null;
  poderes: { id: string; descricao: string }[];
  protocolo: Record<string, unknown> | null;
  descartado: boolean;
}

export interface Passaporte {
  modo: "good" | "evil";
  agentes: AgenteSnapshot[];
  absorcoes: Record<string, AbsorcaoSnapshot>;
}

export interface ReciboPendente {
  recibo_id: string;
  agente_id: string;
  descricao_alegada: string;
  evidencia: string;
  veredito: { aprovado: boolean; motivo: string };
}

export interface ReciboResolvido {
  recibo_id: string;
  decisao: "aprovar" | "rejeitar" | "rejeitado_pelo_juiz";
}

export interface CapacidadeObservada {
  agente_id: string;
  capacidade_id: string;
}

export interface AgenteDescartado {
  agente_id: string;
}

type Manipuladores = {
  onSnapshot: (snapshot: Passaporte) => void;
  onReciboPendente: (recibo: ReciboPendente) => void;
  onReciboResolvido: (recibo: ReciboResolvido) => void;
  onCapacidadeObservada?: (evento: CapacidadeObservada) => void;
  onAgenteDescartado?: (evento: AgenteDescartado) => void;
  onConexao?: (conectado: boolean) => void;
};

export function conectarAgui(manipuladores: Manipuladores): () => void {
  const origem = new EventSource(`${API_BASE}/agui/stream`);

  origem.onopen = () => manipuladores.onConexao?.(true);
  origem.onerror = () => manipuladores.onConexao?.(false);

  origem.onmessage = (mensagem) => {
    const evento = JSON.parse(mensagem.data) as { type: string; name?: string; value?: unknown; snapshot?: unknown };
    if (evento.type === "STATE_SNAPSHOT") {
      manipuladores.onSnapshot(evento.snapshot as Passaporte);
      return;
    }
    if (evento.type !== "CUSTOM") return;
    switch (evento.name) {
      case "recibo_pendente":
        manipuladores.onReciboPendente(evento.value as ReciboPendente);
        break;
      case "recibo_resolvido":
        manipuladores.onReciboResolvido(evento.value as ReciboResolvido);
        break;
      case "capacidade_observada":
        manipuladores.onCapacidadeObservada?.(evento.value as CapacidadeObservada);
        break;
      case "agente_descartado":
        manipuladores.onAgenteDescartado?.(evento.value as AgenteDescartado);
        break;
    }
  };

  return () => origem.close();
}

export async function decidirRecibo(reciboId: string, decisao: "aprovar" | "rejeitar"): Promise<void> {
  const resposta = await fetch(`${API_BASE}/api/recibos/${reciboId}/decisao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decisao }),
  });
  if (!resposta.ok) throw new Error(`decision refused (${resposta.status})`);
}

export async function iniciarMissao(mensagem: string, orcamento?: number): Promise<void> {
  const resposta = await fetch(`${API_BASE}/api/missoes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensagem, orcamento }),
  });
  if (!resposta.ok) throw new Error(`could not start mission (${resposta.status})`);
}

export async function buscarConfig(): Promise<{ modo: "good" | "evil" }> {
  const resposta = await fetch(`${API_BASE}/api/config`);
  return resposta.json();
}
