"""In-memory event bus: one asyncio.Queue per open SSE connection, fed with AG-UI events."""

import asyncio
import uuid

from ag_ui.core import BaseEvent, CustomEvent, EventType, StateSnapshotEvent


class BarramentoEventos:
    def __init__(self) -> None:
        self._assinantes: set[asyncio.Queue] = set()

    def assinar(self) -> "asyncio.Queue[BaseEvent]":
        fila: asyncio.Queue = asyncio.Queue()
        self._assinantes.add(fila)
        return fila

    def desassinar(self, fila: "asyncio.Queue[BaseEvent]") -> None:
        self._assinantes.discard(fila)

    def publicar_nowait(self, evento: BaseEvent) -> None:
        for fila in self._assinantes:
            fila.put_nowait(evento)


def novo_recibo_id() -> str:
    return uuid.uuid4().hex


def evento_custom(nome: str, valor: dict) -> CustomEvent:
    return CustomEvent(type=EventType.CUSTOM, name=nome, value=valor)


def evento_snapshot(snapshot: dict) -> StateSnapshotEvent:
    return StateSnapshotEvent(type=EventType.STATE_SNAPSHOT, snapshot=snapshot)
