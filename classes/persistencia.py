from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .aresta import Aresta
from .grafo import Grafo
from .moeda import Moeda


class Persistencia:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent / "dados"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.arquivo_moedas = self.base_dir / "moedas.json"
        self.arquivo_taxas = self.base_dir / "taxas.json"

    def carregar(self) -> Grafo:
        grafo = Grafo()
        dados = {
            "moedas": self._carregar_json(self.arquivo_moedas, self._dados_padrao_moedas()),
            "taxas": self._carregar_json(self.arquivo_taxas, self._dados_padrao_taxas()),
        }
        grafo.carregar_dict({
            "moedas": dados["moedas"],
            "taxas": dados["taxas"],
            "ultima_atualizacao": grafo.ultima_atualizacao,
        })
        return grafo

    def salvar(self, grafo: Grafo) -> None:
        self._salvar_json(self.arquivo_moedas, [moeda.to_dict() for moeda in grafo.listar_moedas()])
        self._salvar_json(self.arquivo_taxas, [aresta.to_dict() for aresta in grafo.listar_taxas()])

    def _salvar_json(self, arquivo: Path, dados) -> None:
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    def _carregar_json(self, arquivo: Path, valor_padrao):
        if not arquivo.exists():
            self._salvar_json(arquivo, valor_padrao)
            return valor_padrao
        try:
            conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
            if not conteudo:
                return valor_padrao
            return conteudo
        except json.JSONDecodeError:
            return valor_padrao

    def _dados_padrao_moedas(self):
        return [
            {"nome": "Real Brasileiro", "sigla": "BRL"},
            {"nome": "Dolar Americano", "sigla": "USD"},
            {"nome": "Euro", "sigla": "EUR"},
            {"nome": "Libra Esterlina", "sigla": "GBP"},
            {"nome": "Iene Japonês", "sigla": "JPY"},
        ]

    def _dados_padrao_taxas(self):
        return [
            {"origem": "BRL", "destino": "USD", "taxa": 0.18},
            {"origem": "USD", "destino": "BRL", "taxa": 5.5555555556},
            {"origem": "BRL", "destino": "EUR", "taxa": 0.16},
            {"origem": "EUR", "destino": "BRL", "taxa": 6.25},
            {"origem": "BRL", "destino": "GBP", "taxa": 0.14},
            {"origem": "GBP", "destino": "BRL", "taxa": 7.1428571429},
            {"origem": "BRL", "destino": "JPY", "taxa": 28.0},
            {"origem": "JPY", "destino": "BRL", "taxa": 0.0357142857},
            {"origem": "USD", "destino": "EUR", "taxa": 0.8888888889},
            {"origem": "EUR", "destino": "USD", "taxa": 1.125},
            {"origem": "USD", "destino": "GBP", "taxa": 0.7777777778},
            {"origem": "GBP", "destino": "USD", "taxa": 1.2857142857},
            {"origem": "EUR", "destino": "GBP", "taxa": 0.875},
            {"origem": "GBP", "destino": "EUR", "taxa": 1.1428571429},
            {"origem": "USD", "destino": "JPY", "taxa": 155.5555555556},
            {"origem": "JPY", "destino": "USD", "taxa": 0.0064285714},
            {"origem": "EUR", "destino": "JPY", "taxa": 175.0},
            {"origem": "JPY", "destino": "EUR", "taxa": 0.0057142857},
            {"origem": "GBP", "destino": "JPY", "taxa": 200.0},
            {"origem": "JPY", "destino": "GBP", "taxa": 0.005},
        ]
