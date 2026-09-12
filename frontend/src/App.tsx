import { useEffect, useState } from "react";
import "./styles.css";
import { CartaoDeRecibo } from "./components/CartaoDeRecibo";
import { PassaporteGrid } from "./components/PassaporteGrid";
import {
  buscarConfig,
  conectarAgui,
  iniciarMissao,
  type Passaporte,
  type ReciboPendente,
} from "./lib/aguiClient";

export function App() {
  const [passaporte, setPassaporte] = useState<Passaporte | null>(null);
  const [recibos, setRecibos] = useState<ReciboPendente[]>([]);
  const [conectado, setConectado] = useState(false);
  const [modo, setModo] = useState<"good" | "evil" | null>(null);
  const [missao, setMissao] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    buscarConfig().then((c) => setModo(c.modo)).catch(() => undefined);
    return conectarAgui({
      onSnapshot: setPassaporte,
      onReciboPendente: (recibo) => setRecibos((atual) => [...atual, recibo]),
      onReciboResolvido: (resolvido) =>
        setRecibos((atual) => atual.filter((r) => r.recibo_id !== resolvido.recibo_id)),
      onConexao: setConectado,
    });
  }, []);

  async function enviarMissao(evento: React.FormEvent) {
    evento.preventDefault();
    if (!missao.trim()) return;
    setEnviando(true);
    try {
      await iniciarMissao(missao.trim());
      setMissao("");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🪞 Mystique — Trust Broker</h1>
        <span className={`badge badge--modo badge--${modo ?? "carregando"}`}>{modo ?? "…"}</span>
        <span className={`indicador ${conectado ? "indicador--ok" : "indicador--off"}`}>
          {conectado ? "live" : "reconnecting…"}
        </span>
      </header>

      <form className="missao-form" onSubmit={enviarMissao}>
        <input
          value={missao}
          onChange={(e) => setMissao(e.target.value)}
          placeholder="Give Mystique a mission…"
        />
        <button type="submit" disabled={enviando || !missao.trim()}>
          {enviando ? "Starting…" : "Send"}
        </button>
      </form>

      <CartaoDeRecibo recibos={recibos} />
      <PassaporteGrid passaporte={passaporte} />
    </div>
  );
}
