"""Capability catalog and deterministic first-pass agent routing."""

import re
from dataclasses import dataclass

from .poderes import PODERES

_PALAVRAS_VAZIAS = {
    "a", "an", "and", "as", "at", "by", "do", "for", "from", "in", "of", "on",
    "or", "the", "to", "with", "uma", "um", "de", "da", "do", "e", "em", "para",
}


def _termos(texto: str) -> set[str]:
    return {
        termo for termo in re.findall(r"[a-z0-9]+", texto.casefold())
        if len(termo) > 1 and termo not in _PALAVRAS_VAZIAS
    }


@dataclass(frozen=True)
class Candidato:
    agent_id: str
    nome: str
    capacidades: tuple[str, ...]
    score: float
    motivo: str


class Roteador:
    def __init__(self, mundo) -> None:
        self.mundo = mundo

    def capacidades(self, agente) -> tuple[str, ...]:
        return tuple(PODERES[p].descricao for p in agente.poderes if p in PODERES)

    def ranquear(self, tarefa: str) -> list[Candidato]:
        procurados = _termos(tarefa)
        historico = [
            t for t in self.mundo.banco.todos()
            if t.get("source_kind") == "roteamento"
        ]
        ranking = []
        for agente in self.mundo.agentes.values():
            _, erro = self.mundo._agente(agente.id)
            if erro:
                continue
            capacidades = self.capacidades(agente)
            texto = " ".join((agente.nome, agente.apresentacao, *capacidades))
            correspondencias = sorted(procurados & _termos(texto))
            score_capacidade = float(len(correspondencias))
            tracos = [
                t for t in historico
                if t.get("agent_id") == agente.id
                and procurados & _termos(" ".join((t.get("description", ""), *t.get("tags", []))))
            ]
            sucessos = sum(t.get("outcome") == "success" for t in tracos)
            falhas = sum(t.get("outcome") == "failure" for t in tracos)
            score = score_capacidade + (1.5 * sucessos) - falhas
            motivo = (
                "matched: " + ", ".join(correspondencias)
                if correspondencias else "no direct capability match"
            )
            if tracos:
                motivo += f"; Reasoning Bank: {sucessos} success, {falhas} failure"
            ranking.append(Candidato(agente.id, agente.nome, capacidades, score, motivo))
        return sorted(ranking, key=lambda item: (-item.score, item.agent_id))
