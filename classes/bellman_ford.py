from __future__ import annotations

from collections import deque
from math import inf, log as math_log
from time import perf_counter
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from .grafo import Grafo

LogCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int], None]
EPSILON = 1e-9


class BellmanFord:
    def __init__(self, grafo: Grafo) -> None:
        self.grafo = grafo

    def converter(
        self,
        origem: str,
        destino: str,
        valor_inicial: float,
        log_callback: Optional[LogCallback] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> dict:
        origem = origem.strip().upper()
        destino = destino.strip().upper()
        valor_inicial = float(valor_inicial)

        if origem not in self.grafo.moedas:
            raise ValueError("Moeda de origem não cadastrada.")
        if destino not in self.grafo.moedas:
            raise ValueError("Moeda de destino não cadastrada.")
        if valor_inicial <= 0:
            raise ValueError("Informe um valor maior que zero.")

        vertices = self.grafo.vertices()
        dist: Dict[str, float] = {vertice: inf for vertice in vertices}
        pred: Dict[str, Optional[str]] = {vertice: None for vertice in vertices}
        dist[origem] = 0.0
        relaxamentos = 0
        relaxamentos_detalhados: List[Tuple[str, str]] = []
        registrar_log = self._registrar_log(log_callback)
        inicio = perf_counter()

        registrar_log(f"Iniciando Bellman-Ford de {origem} para {destino}.")
        total_iteracoes = max(0, len(vertices) - 1)
        for indice in range(total_iteracoes):
            registrar_log(f"Iteracao {indice + 1}")
            alterou = False
            for aresta in self.grafo.listar_taxas():
                if dist[aresta.origem] == inf:
                    continue
                peso = -math_log(aresta.taxa)
                novo_valor = dist[aresta.origem] + peso
                if novo_valor < dist[aresta.destino] - EPSILON:
                    dist[aresta.destino] = novo_valor
                    pred[aresta.destino] = aresta.origem
                    relaxamentos += 1
                    relaxamentos_detalhados.append((aresta.origem, aresta.destino))
                    alterou = True
                    registrar_log(f"Relaxando {aresta.origem} -> {aresta.destino}")
                    registrar_log("Atualizando distancia")
            if progress_callback:
                progress_callback(indice + 1, max(1, total_iteracoes))
            if not alterou:
                break

        ciclo = self._identificar_ciclo_negativo(dist, pred)
        ciclo_afeta_destino = False
        if ciclo:
            ciclo_afeta_destino = self._ciclo_alcanca_destino(ciclo, destino)

        caminho = self._reconstruir_caminho(pred, origem, destino)
        caminho_edges = self._caminho_para_arestas(caminho)
        valor_final = None
        valores_caminho: List[Tuple[str, float]] = []
        if caminho and not ciclo_afeta_destino:
            valor_final = self._valor_do_caminho(caminho, valor_inicial)
            valores_caminho = self._valores_no_caminho(caminho, valor_inicial)

        elapsed = perf_counter() - inicio
        registrar_log("Fim da execução")

        return {
            "tipo": "conversao",
            "sucesso": caminho is not None and not ciclo_afeta_destino,
            "origem": origem,
            "destino": destino,
            "valor_inicial": valor_inicial,
            "valor_final": valor_final,
            "caminho": caminho or [],
            "caminho_arestas": caminho_edges,
            "valores_caminho": valores_caminho,
            "relaxamentos": relaxamentos,
            "relaxamentos_detalhados": relaxamentos_detalhados,
            "tempo_execucao": elapsed,
            "quantidade_moedas_visitadas": sum(1 for valor in dist.values() if valor != inf),
            "distancias": dist,
            "predecessores": pred,
            "ciclo_negativo": ciclo,
            "ciclo_afeta_destino": ciclo_afeta_destino,
            "mensagem": (
                "Conversão concluída com sucesso."
                if caminho and not ciclo_afeta_destino
                else "Nao foi possivel calcular uma rota valida para este destino."
            ),
            "log": [],
        }

    def procurar_arbitragem(self, log_callback: Optional[LogCallback] = None, progress_callback: Optional[ProgressCallback] = None) -> dict:
        vertices = self.grafo.vertices()
        if not vertices:
            raise ValueError("Cadastre moedas antes de procurar arbitragem.")
        if not self.grafo.taxas:
            raise ValueError("Cadastre taxas antes de procurar arbitragem.")

        dist: Dict[str, float] = {vertice: 0.0 for vertice in vertices}
        pred: Dict[str, Optional[str]] = {vertice: None for vertice in vertices}
        relaxamentos = 0
        registrar_log = self._registrar_log(log_callback)
        inicio = perf_counter()
        total_iteracoes = max(0, len(vertices) - 1)

        registrar_log("Procurando oportunidades de arbitragem.")
        for indice in range(total_iteracoes):
            registrar_log(f"Iteracao {indice + 1}")
            alterou = False
            for aresta in self.grafo.listar_taxas():
                peso = -math_log(aresta.taxa)
                novo_valor = dist[aresta.origem] + peso
                if novo_valor < dist[aresta.destino] - EPSILON:
                    dist[aresta.destino] = novo_valor
                    pred[aresta.destino] = aresta.origem
                    relaxamentos += 1
                    alterou = True
                    registrar_log(f"Relaxando {aresta.origem} -> {aresta.destino}")
            if progress_callback:
                progress_callback(indice + 1, max(1, total_iteracoes))
            if not alterou:
                break

        vertice_ciclo = None
        for aresta in self.grafo.listar_taxas():
            peso = -math_log(aresta.taxa)
            if dist[aresta.origem] + peso < dist[aresta.destino] - EPSILON:
                vertice_ciclo = aresta.destino
                pred[aresta.destino] = aresta.origem
                break

        ciclo = self._extrair_ciclo(pred, vertice_ciclo) if vertice_ciclo else []
        ciclo_edges = self._caminho_para_arestas(ciclo)
        valor_inicial = 100.0
        valor_final = self._valor_do_caminho(ciclo, valor_inicial) if ciclo else None
        lucro = None if valor_final is None else valor_final - valor_inicial
        percentual = None if valor_final is None else ((valor_final / valor_inicial) - 1.0) * 100.0
        registrar_log("Fim da execução")
        return {
            "tipo": "arbitragem",
            "sucesso": bool(ciclo),
            "ciclo": ciclo,
            "ciclo_arestas": ciclo_edges,
            "valor_inicial": valor_inicial,
            "valor_final": valor_final,
            "lucro": lucro,
            "percentual": percentual,
            "relaxamentos": relaxamentos,
            "tempo_execucao": perf_counter() - inicio,
            "ciclo_negativo": ciclo,
            "mensagem": "Oportunidade encontrada." if ciclo else "Nenhuma oportunidade encontrada.",
        }

    def _registrar_log(self, callback: Optional[LogCallback]) -> LogCallback:
        def log(msg: str) -> None:
            if callback:
                callback(msg)

        return log

    def _valor_do_caminho(self, caminho: List[str], valor_inicial: float) -> float:
        valor = float(valor_inicial)
        for origem, destino in zip(caminho, caminho[1:]):
            aresta = self.grafo.taxas.get((origem, destino))
            if aresta is None:
                raise ValueError(f"Taxa inexistente em {origem} -> {destino}.")
            valor *= aresta.taxa
        return valor

    def _valores_no_caminho(self, caminho: List[str], valor_inicial: float) -> List[Tuple[str, float]]:
        valores = [(caminho[0], float(valor_inicial))]
        valor = float(valor_inicial)
        for origem, destino in zip(caminho, caminho[1:]):
            aresta = self.grafo.taxas.get((origem, destino))
            if aresta is None:
                break
            valor *= aresta.taxa
            valores.append((destino, valor))
        return valores

    def _reconstruir_caminho(self, pred: Dict[str, Optional[str]], origem: str, destino: str) -> Optional[List[str]]:
        if origem == destino:
            return [origem]
        if pred.get(destino) is None:
            return None

        caminho = [destino]
        atual = destino
        vistos = set()
        while atual != origem:
            atual = pred.get(atual)
            if atual is None or atual in vistos:
                return None
            vistos.add(atual)
            caminho.append(atual)
        caminho.reverse()
        return caminho

    def _caminho_para_arestas(self, caminho: Optional[List[str]]) -> List[Tuple[str, str]]:
        if not caminho or len(caminho) < 2:
            return []
        return list(zip(caminho, caminho[1:]))

    def _identificar_ciclo_negativo(self, dist: Dict[str, float], pred: Dict[str, Optional[str]]) -> List[str]:
        candidato = None
        for aresta in self.grafo.listar_taxas():
            peso = -math_log(aresta.taxa)
            if dist[aresta.origem] != inf and dist[aresta.origem] + peso < dist[aresta.destino] - EPSILON:
                candidato = aresta.destino
                pred[aresta.destino] = aresta.origem
                break
        if candidato is None:
            return []
        return self._extrair_ciclo(pred, candidato)

    def _extrair_ciclo(self, pred: Dict[str, Optional[str]], vertice: Optional[str]) -> List[str]:
        if vertice is None:
            return []
        atual = vertice
        for _ in range(len(pred)):
            atual = pred.get(atual)
            if atual is None:
                return []
        ciclo = [atual]
        prox = pred.get(atual)
        vistos = {atual}
        while prox is not None and prox not in vistos:
            ciclo.append(prox)
            vistos.add(prox)
            prox = pred.get(prox)
        if prox is not None:
            ciclo.append(prox)
        ciclo.reverse()
        if ciclo and ciclo[0] != ciclo[-1]:
            ciclo.append(ciclo[0])
        return ciclo

    def _ciclo_alcanca_destino(self, ciclo: List[str], destino: str) -> bool:
        if not ciclo:
            return False
        alvos = set()
        fila = deque(ciclo)
        adj = self.grafo.adjacencias()
        visitados = set(ciclo)
        while fila:
            origem = fila.popleft()
            for aresta in adj.get(origem, []):
                if aresta.destino not in visitados:
                    visitados.add(aresta.destino)
                    fila.append(aresta.destino)
                    alvos.add(aresta.destino)
        return destino in alvos or destino in ciclo
