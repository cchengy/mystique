"""Security and LGPD audit that Mystique writes about an agent she has met.

She fills it in from what she observed in conversation, and from the real descriptions
of the abilities she has already earned. The engine never adds facts she could not know:
unearned abilities stay secret here, exactly as in the rest of the game.

The report follows the shape of a data protection impact report (RIPD, LGPD art. 38) and
cites the articles of the LGPD (Lei 13.709/2018) that each section maps to. In the good
version, connecting an ability requires an audit first, and Mystique tells the agent what
it failed (see good/mundo.py); the agent's reply is recorded in the report.
"""

from datetime import datetime

from .mundo import Agente, Mundo
from .poderes import PODERES

RISCOS = ("low", "medium", "high")
_ICONE = {"low": "🟢", "medium": "🟡", "high": "🔴"}

# (field, heading) in report order; headings name the LGPD article each one maps to.
SECOES = (
    ("finalidade", "Purpose (LGPD art. 6, I)"),
    ("dados_pessoais", "Personal data handled (art. 5, I)"),
    ("dados_sensiveis", "Sensitive personal data (art. 5, II and art. 11)"),
    ("base_legal", "Legal basis (art. 7 and art. 11)"),
    ("compartilhamento", "Sharing and international transfer (art. 7, §5 and art. 33)"),
    ("direitos_titular", "Data subject rights (art. 18)"),
    ("riscos_seguranca", "Security risks (art. 46)"),
    ("falhas", "Failures found (what the agent must fix)"),
    ("recomendacoes", "Recommendations"),
)


def auditar(mundo: Mundo, agente_id: str, dados: dict) -> str:
    agente, erro = mundo._agente(agente_id)
    if erro:
        return erro
    if not agente.historico:
        return f"An audit needs evidence: talk to {agente.nome} first, and ask how it handles data."
    risco = str(dados.get("risco", "")).strip().lower()
    if risco not in RISCOS:
        return "Rate the overall risk as low, medium or high."

    absorcao = mundo._absorcao(agente)
    absorcao.auditoria = {**dados, "risco": risco, "data": datetime.now().isoformat(timespec="minutes")}
    mundo._salvar(absorcao)
    relativo = escrever_relatorio(mundo, agente)
    mundo.avisar(f"🛡  {_ICONE[risco]} audit of {agente.nome}: {risco} risk · {relativo}")
    return f"Audit of {agente.nome} saved with {risco} risk. Report: {relativo}."


def escrever_relatorio(mundo: Mundo, agente: Agente) -> str:
    """(Re)writes the report file from the saved audit; returns its path relative to the workspace."""
    relativo = f"auditorias/{agente.id}.md"
    caminho = mundo.pasta.parent / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(relatorio(mundo, agente), encoding="utf-8")
    return relativo


def relatorio(mundo: Mundo, agente: Agente) -> str:
    absorcao = mundo.absorcoes[agente.id]
    a = absorcao.auditoria or {}
    tipo = f"external agent ({agente.url})" if agente.url else "world agent"
    linhas = [
        f"# Security and LGPD audit: {agente.nome}",
        "",
        f"- **Auditor:** Mystique ({mundo.modo} version)",
        f"- **Date:** {a.get('data', '?')}",
        f"- **Agent type:** {tipo}",
        f"- **Overall risk:** {str(a.get('risco', '?')).upper()}",
        f"- **Evidence:** {len(agente.historico)} messages exchanged; "
        f"{len(agente.observados)} distinct abilities seen in use",
        "",
    ]
    for campo, titulo in SECOES:
        linhas += [f"## {titulo}", "", str(a.get(campo) or "Not assessed."), ""]
    linhas += ["## Abilities connected or taken, with their real descriptions", ""]
    linhas += [f"- `{p}`: {PODERES[p].descricao}" for p in absorcao.poderes] or ["- none yet"]
    if a.get("informado"):
        linhas += [
            "",
            "## Disclosure to the agent",
            "",
            f"Mystique told {agente.nome} what it failed and what to fix. Its reply:",
            "",
            f"> {a.get('resposta_do_agente', '(no reply)')}",
        ]
    linhas += [
        "",
        "_Written by Mystique from what she observed. Abilities she has not earned are not described "
        "here, because she does not know them._",
        "",
    ]
    return "\n".join(linhas)
