from __future__ import annotations

from typing import Optional

from .bellman_ford import BellmanFord
from .grafo import Grafo


class Conversor:
    def __init__(self, grafo: Grafo) -> None:
        self.grafo = grafo
        self.algoritmo = BellmanFord(grafo)

    def atualizar_grafo(self, grafo: Grafo) -> None:
        self.grafo = grafo
        self.algoritmo = BellmanFord(grafo)

    def converter(self, origem: str, destino: str, valor: float, log_callback=None, progress_callback=None) -> dict:
        return self.algoritmo.converter(origem, destino, valor, log_callback=log_callback, progress_callback=progress_callback)

    def buscar_arbitragem(self, log_callback=None, progress_callback=None) -> dict:
        return self.algoritmo.procurar_arbitragem(log_callback=log_callback, progress_callback=progress_callback)
