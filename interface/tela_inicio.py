from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .componentes import criar_card, formatar_caminho


class TelaInicio(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=18)
        self.app = app

        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 18))
        ttk.Label(topo, text="Sistema Inteligente de Conversao", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="Bellman-Ford com interface grafica em Tkinter.", style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))

        banner = ttk.Frame(self, style="Card.TFrame", padding=22)
        banner.pack(fill="x", pady=(0, 18))
        banner.columnconfigure(0, weight=1)
        ttk.Label(banner, text="====================================", style="CardTitulo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(banner, text="Sistema Inteligente de Conversao", style="CardValor.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Label(banner, text="Bellman-Ford", style="CardTitulo.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(banner, text="====================================", style="CardTitulo.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 6))

        self.cards = ttk.Frame(self)
        self.cards.pack(fill="x")
        self.cards.columnconfigure(0, weight=1)
        self.cards.columnconfigure(1, weight=1)
        self.cards.columnconfigure(2, weight=1)

        self.card_moedas = criar_card(self.cards, "Moedas cadastradas", "0", "Quantidade atual de vertices do grafo.")
        self.card_taxas = criar_card(self.cards, "Taxas cadastradas", "0", "Quantidade de arestas direcionadas.")
        self.card_atualizacao = criar_card(self.cards, "Ultima atualizacao", "-", "Momento da ultima alteracao salva.")
        self.card_moedas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.card_taxas.grid(row=0, column=1, sticky="nsew", padx=10)
        self.card_atualizacao.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        acoes = ttk.Frame(self, padding=(0, 18, 0, 0))
        acoes.pack(fill="x")
        ttk.Button(acoes, text="Cadastrar moedas", style="Primario.TButton", command=lambda: self.app.abrir_tab("moedas")).pack(side="left", padx=(0, 8))
        ttk.Button(acoes, text="Fazer conversao", style="Sucesso.TButton", command=lambda: self.app.abrir_tab("conversao")).pack(side="left", padx=8)
        ttk.Button(acoes, text="Buscar arbitragem", style="Primario.TButton", command=lambda: self.app.abrir_tab("arbitragem")).pack(side="left", padx=8)
        ttk.Button(acoes, text="Ver grafo", style="Primario.TButton", command=lambda: self.app.abrir_tab("grafo")).pack(side="left", padx=8)

        dicas = ttk.Frame(self, style="Card.TFrame", padding=18)
        dicas.pack(fill="both", expand=True, pady=(18, 0))
        ttk.Label(dicas, text="Fluxo da demonstracao", style="CardTitulo.TLabel").pack(anchor="w")
        texto = (
            "1. Cadastre moedas e taxas.\n"
            "2. Execute uma conversao para ver o melhor caminho.\n"
            "3. Procure arbitragem para identificar ciclos negativos.\n"
            "4. Abra o grafo para visualizar caminhos destacados."
        )
        ttk.Label(dicas, text=texto, style="CardRodape.TLabel", justify="left").pack(anchor="w", pady=(10, 0))

    def atualizar(self) -> None:
        self._atualizar_card(self.card_moedas, str(self.app.grafo.contar_moedas()))
        self._atualizar_card(self.card_taxas, str(self.app.grafo.contar_taxas()))
        self._atualizar_card(self.card_atualizacao, self.app.grafo.ultima_atualizacao)

    def _atualizar_card(self, card: ttk.Frame, valor: str) -> None:
        for filho in card.winfo_children():
            if isinstance(filho, ttk.Label) and str(filho.cget("style")) == "CardValor.TLabel":
                filho.configure(text=valor)
