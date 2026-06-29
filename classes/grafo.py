from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from .aresta import Aresta
from .moeda import Moeda


class Grafo:
    def __init__(self) -> None:
        self.moedas: Dict[str, Moeda] = {}
        self.taxas: Dict[Tuple[str, str], Aresta] = {}
        self.ultima_atualizacao = self._agora()

    def _agora(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _marcar_atualizacao(self) -> None:
        self.ultima_atualizacao = self._agora()

    @staticmethod
    def _sigla(sigla: str) -> str:
        return sigla.strip().upper()

    def limpar(self) -> None:
        self.moedas.clear()
        self.taxas.clear()
        self._marcar_atualizacao()

    def adicionar_moeda(self, nome: str, sigla: str) -> None:
        moeda = Moeda(nome=nome, sigla=sigla)
        if not moeda.nome:
            raise ValueError("Informe o nome da moeda.")
        if not moeda.sigla:
            raise ValueError("Informe a sigla da moeda.")
        if moeda.sigla in self.moedas:
            raise ValueError(f"A moeda {moeda.sigla} já existe.")
        self.moedas[moeda.sigla] = moeda
        self._marcar_atualizacao()

    def editar_moeda(self, sigla_antiga: str, novo_nome: str, nova_sigla: str) -> None:
        sigla_antiga = self._sigla(sigla_antiga)
        nova_sigla = self._sigla(nova_sigla)
        if sigla_antiga not in self.moedas:
            raise ValueError("Moeda não encontrada.")
        if not novo_nome.strip():
            raise ValueError("Informe o nome da moeda.")
        if not nova_sigla:
            raise ValueError("Informe a sigla da moeda.")
        if nova_sigla != sigla_antiga and nova_sigla in self.moedas:
            raise ValueError(f"A moeda {nova_sigla} já existe.")

        moeda = self.moedas.pop(sigla_antiga)
        moeda.nome = novo_nome.strip()
        moeda.sigla = nova_sigla
        self.moedas[nova_sigla] = moeda

        novas_taxas: Dict[Tuple[str, str], Aresta] = {}
        for (origem, destino), aresta in self.taxas.items():
            novo_origem = nova_sigla if origem == sigla_antiga else origem
            novo_destino = nova_sigla if destino == sigla_antiga else destino
            aresta.origem = novo_origem
            aresta.destino = novo_destino
            novas_taxas[(novo_origem, novo_destino)] = aresta
        self.taxas = novas_taxas
        self._marcar_atualizacao()

    def excluir_moeda(self, sigla: str) -> None:
        sigla = self._sigla(sigla)
        if sigla not in self.moedas:
            raise ValueError("Moeda não encontrada.")
        self.moedas.pop(sigla)
        self.taxas = {
            chave: aresta
            for chave, aresta in self.taxas.items()
            if aresta.origem != sigla and aresta.destino != sigla
        }
        self._marcar_atualizacao()

    def adicionar_taxa(self, origem: str, destino: str, taxa: float) -> None:
        origem = self._sigla(origem)
        destino = self._sigla(destino)
        taxa = float(taxa)
        self._validar_taxa(origem, destino, taxa)
        self.taxas[(origem, destino)] = Aresta(origem, destino, taxa)
        self._marcar_atualizacao()

    def editar_taxa(self, origem: str, destino: str, nova_taxa: float) -> None:
        origem = self._sigla(origem)
        destino = self._sigla(destino)
        chave = (origem, destino)
        if chave not in self.taxas:
            raise ValueError("Taxa não encontrada.")
        nova_taxa = float(nova_taxa)
        self._validar_taxa(origem, destino, nova_taxa, permitir_existente=True)
        self.taxas[chave].taxa = nova_taxa
        self._marcar_atualizacao()

    def excluir_taxa(self, origem: str, destino: str) -> None:
        chave = (self._sigla(origem), self._sigla(destino))
        if chave not in self.taxas:
            raise ValueError("Taxa não encontrada.")
        self.taxas.pop(chave)
        self._marcar_atualizacao()

    def taxa_entre(self, origem: str, destino: str) -> float | None:
        aresta = self.taxas.get((self._sigla(origem), self._sigla(destino)))
        return None if aresta is None else aresta.taxa

    def existe_moeda(self, sigla: str) -> bool:
        return self._sigla(sigla) in self.moedas

    def listar_moedas(self) -> List[Moeda]:
        return sorted(self.moedas.values(), key=lambda moeda: moeda.sigla)

    def listar_taxas(self) -> List[Aresta]:
        return sorted(self.taxas.values(), key=lambda aresta: (aresta.origem, aresta.destino))

    def contar_moedas(self) -> int:
        return len(self.moedas)

    def contar_taxas(self) -> int:
        return len(self.taxas)

    def vertices(self) -> List[str]:
        return [moeda.sigla for moeda in self.listar_moedas()]

    def adjacencias(self) -> Dict[str, List[Aresta]]:
        mapa: Dict[str, List[Aresta]] = {sigla: [] for sigla in self.moedas}
        for aresta in self.listar_taxas():
            mapa.setdefault(aresta.origem, []).append(aresta)
        return mapa

    def para_dict(self) -> dict:
        return {
            "moedas": [moeda.to_dict() for moeda in self.listar_moedas()],
            "taxas": [aresta.to_dict() for aresta in self.listar_taxas()],
            "ultima_atualizacao": self.ultima_atualizacao,
        }

    def carregar_dict(self, dados: dict) -> None:
        self.limpar()
        for moeda_dados in dados.get("moedas", []):
            moeda = Moeda.from_dict(moeda_dados)
            if moeda.sigla:
                self.moedas[moeda.sigla] = moeda
        for taxa_dados in dados.get("taxas", []):
            aresta = Aresta.from_dict(taxa_dados)
            if aresta.origem and aresta.destino:
                self.taxas[(aresta.origem, aresta.destino)] = aresta
        self.ultima_atualizacao = dados.get("ultima_atualizacao", self._agora())

    def _validar_taxa(self, origem: str, destino: str, taxa: float, permitir_existente: bool = False) -> None:
        if origem == destino:
            raise ValueError("A moeda de origem e destino deve ser diferente.")
        if origem not in self.moedas:
            raise ValueError(f"Moeda de origem {origem} não cadastrada.")
        if destino not in self.moedas:
            raise ValueError(f"Moeda de destino {destino} não cadastrada.")
        if taxa <= 0:
            raise ValueError("A taxa deve ser maior que zero.")
        if not permitir_existente and (origem, destino) in self.taxas:
            raise ValueError("Essa taxa já existe.")
