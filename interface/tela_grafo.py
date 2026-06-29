from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from .componentes import CORES, formatar_valor


class TelaGrafo(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=18)
        self.app = app
        self.posicoes = {}
        self.canvas_width = 1100
        self.canvas_height = 720

        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 16))
        ttk.Label(topo, text="Visualizacao do grafo", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="Arestas em azul representam relaxamentos, o caminho final fica em verde e ciclos negativos em vermelho.", style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))

        painel = ttk.Frame(self)
        painel.pack(fill="both", expand=True)
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)

        moldura = ttk.LabelFrame(painel, text="Grafo de conversao", padding=8)
        moldura.grid(row=0, column=0, sticky="nsew")
        moldura.rowconfigure(0, weight=1)
        moldura.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(moldura, width=self.canvas_width, height=self.canvas_height, bg="#0b1220", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        barra_x = ttk.Scrollbar(moldura, orient="horizontal", command=self.canvas.xview)
        barra_x.grid(row=1, column=0, sticky="ew")
        barra_y = ttk.Scrollbar(moldura, orient="vertical", command=self.canvas.yview)
        barra_y.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
        self.canvas.bind("<Configure>", lambda _e: self.desenhar())

        legenda = ttk.LabelFrame(self, text="Legenda", padding=12)
        legenda.pack(fill="x", pady=(16, 0))
        ttk.Label(legenda, text="Verde = melhor caminho | Azul = relaxamento | Vermelho = ciclo negativo | Cinza = arestas neutras").pack(anchor="w")

    def atualizar(self) -> None:
        self.desenhar()

    def desenhar(self) -> None:
        self.canvas.delete("all")
        moedas = self.app.grafo.listar_moedas()
        if not moedas:
            self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2, text="Nenhuma moeda cadastrada.", fill=CORES["texto"], font=("Segoe UI", 16, "bold"))
            self.canvas.configure(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
            return

        largura = max(self.canvas.winfo_width(), self.canvas_width)
        altura = max(self.canvas.winfo_height(), self.canvas_height)
        self._calcular_posicoes([moeda.sigla for moeda in moedas], largura, altura)
        resultado = self.app.last_result or {}
        caminho_arestas = set(tuple(par) for par in resultado.get("caminho_arestas", []))
        ciclo_arestas = set(tuple(par) for par in resultado.get("ciclo_arestas", []))
        relaxadas = set(tuple(par) for par in resultado.get("relaxamentos_detalhados", []))

        for aresta in self.app.grafo.listar_taxas():
            self._desenhar_aresta(aresta.origem, aresta.destino, aresta.taxa, caminho_arestas, ciclo_arestas, relaxadas)
        for moeda in moedas:
            self._desenhar_no(moeda.sigla, moeda.nome, resultado)

        bbox = self.canvas.bbox("all")
        if bbox:
            margem = 70
            self.canvas.configure(
                scrollregion=(
                    bbox[0] - margem,
                    bbox[1] - margem,
                    bbox[2] + margem,
                    bbox[3] + margem,
                )
            )
        else:
            self.canvas.configure(scrollregion=(0, 0, largura, altura))

    def _calcular_posicoes(self, siglas, largura: float, altura: float) -> None:
        total = len(siglas)
        centro_x = largura / 2
        centro_y = altura / 2
        raio = max(180, min(largura, altura) * 0.34)
        self.posicoes = {}
        for indice, sigla in enumerate(siglas):
            angulo = (2 * math.pi * indice / total) - math.pi / 2
            x = centro_x + raio * math.cos(angulo)
            y = centro_y + raio * math.sin(angulo)
            self.posicoes[sigla] = (x, y)

    def _cor_aresta(self, aresta, caminho_arestas, ciclo_arestas, relaxadas):
        chave = (aresta.origem, aresta.destino)
        if chave in ciclo_arestas:
            return CORES["erro"]
        if chave in caminho_arestas:
            return CORES["secundaria"]
        if chave in relaxadas:
            return CORES["primaria"]
        return CORES["linha"]

    def _desenhar_aresta(self, origem, destino, taxa, caminho_arestas, ciclo_arestas, relaxadas) -> None:
        if origem not in self.posicoes or destino not in self.posicoes:
            return
        x1, y1 = self.posicoes[origem]
        x2, y2 = self.posicoes[destino]
        cor = self._cor_aresta(type("A", (), {"origem": origem, "destino": destino})(), caminho_arestas, ciclo_arestas, relaxadas)
        dx = x2 - x1
        dy = y2 - y1
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            return
        margem = 42
        x1 = x1 + margem * dx / distancia
        y1 = y1 + margem * dy / distancia
        x2 = x2 - margem * dx / distancia
        y2 = y2 - margem * dy / distancia
        self.canvas.create_line(x1, y1, x2, y2, fill=cor, width=3, arrow=tk.LAST, arrowshape=(12, 14, 6))
        meio_x = (x1 + x2) / 2
        meio_y = (y1 + y2) / 2
        self.canvas.create_text(meio_x, meio_y - 10, text=f"{taxa:.4f}".rstrip("0").rstrip("."), fill=CORES["texto"], font=("Segoe UI", 9, "bold"), anchor="s")

    def _desenhar_no(self, sigla: str, nome: str, resultado: dict) -> None:
        x, y = self.posicoes[sigla]
        raio = 34
        cor = CORES["painel_claro"]
        if sigla == resultado.get("origem"):
            cor = CORES["primaria"]
        if sigla == resultado.get("destino"):
            cor = CORES["secundaria"]
        if sigla in resultado.get("ciclo", []):
            cor = CORES["erro"]
        self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor, outline="#ffffff", width=2)
        self.canvas.create_text(x, y - 4, text=sigla, fill="#0f172a", font=("Segoe UI", 13, "bold"))
        self.canvas.create_text(x, y + 18, text=nome, fill=CORES["texto"], font=("Segoe UI", 8), width=90)
