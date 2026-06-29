from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from classes.conversor import Conversor
from classes.persistencia import Persistencia

from .componentes import CORES, configurar_tema
from .tela_arbitragem import TelaArbitragem
from .tela_cadastro import TelaCadastro
from .tela_conversao import TelaConversao
from .tela_grafo import TelaGrafo
from .tela_inicio import TelaInicio


class SistemaMoedasApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema Inteligente de Conversao de Moedas")
        self.geometry("1480x900")
        self.minsize(1280, 780)
        configurar_tema(self)

        self.persistencia = Persistencia()
        self.grafo = self.persistencia.carregar()
        self.conversor = Conversor(self.grafo)
        self.last_result = {}

        self._montar_layout()
        self._registrar_atalhos()
        self.ao_mudar_dados(salvar=False)

    def _montar_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        cabecalho = ttk.Frame(self, padding=(18, 16))
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        ttk.Label(cabecalho, text="Sistema Inteligente de Conversao de Moedas", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")

        sidebar = ttk.Frame(self, style="Painel.TFrame", padding=12)
        sidebar.grid(row=1, column=0, sticky="nsw")
        sidebar.rowconfigure(10, weight=1)

        ttk.Label(sidebar, text="Menu", style="CardTitulo.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))
        botoes = [
            ("🏠 Início", lambda: self.abrir_tab("inicio")),
            ("💰 Moedas", lambda: self.abrir_tab("moedas")),
            ("🔄 Conversões", lambda: self.abrir_tab("conversao")),
            ("📈 Arbitragem", lambda: self.abrir_tab("arbitragem")),
            ("🌐 Grafo", lambda: self.abrir_tab("grafo")),
            ("💾 Salvar", self.salvar_dados),
            ("📂 Carregar", self.carregar_dados),
            ("❌ Sair", self.destroy),
        ]
        for indice, (texto, comando) in enumerate(botoes, start=1):
            ttk.Button(sidebar, text=texto, command=comando).grid(row=indice, column=0, sticky="ew", pady=4)

        self.area_principal = ttk.Frame(self, padding=(12, 0, 18, 18))
        self.area_principal.grid(row=1, column=1, sticky="nsew")
        self.area_principal.rowconfigure(0, weight=1)
        self.area_principal.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.area_principal)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.telas = {
            "inicio": TelaInicio(self.notebook, self),
            "moedas": TelaCadastro(self.notebook, self),
            "conversao": TelaConversao(self.notebook, self),
            "arbitragem": TelaArbitragem(self.notebook, self),
            "grafo": TelaGrafo(self.notebook, self),
        }
        self.notebook.add(self.telas["inicio"], text="Início")
        self.notebook.add(self.telas["moedas"], text="Moedas")
        self.notebook.add(self.telas["conversao"], text="Conversões")
        self.notebook.add(self.telas["arbitragem"], text="Arbitragem")
        self.notebook.add(self.telas["grafo"], text="Grafo")

        self.status_var = tk.StringVar(value="Pronto.")
        status = ttk.Label(self, textvariable=self.status_var, padding=(18, 0, 18, 10), style="Subtitulo.TLabel")
        status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def _registrar_atalhos(self) -> None:
        self.bind("<Control-s>", lambda _e: self.salvar_dados())
        self.bind("<Control-l>", lambda _e: self.carregar_dados())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Control-1>", lambda _e: self.abrir_tab("inicio"))
        self.bind("<Control-2>", lambda _e: self.abrir_tab("moedas"))
        self.bind("<Control-3>", lambda _e: self.abrir_tab("conversao"))
        self.bind("<Control-4>", lambda _e: self.abrir_tab("arbitragem"))
        self.bind("<Control-5>", lambda _e: self.abrir_tab("grafo"))

    def abrir_tab(self, nome: str) -> None:
        ordem = ["inicio", "moedas", "conversao", "arbitragem", "grafo"]
        indice = ordem.index(nome)
        self.notebook.select(indice)
        self.status_var.set(f"Aba aberta: {nome.title()}")

    def ao_mudar_dados(self, salvar: bool = True) -> None:
        self.conversor.atualizar_grafo(self.grafo)
        self.telas["inicio"].atualizar()
        self.telas["moedas"].atualizar()
        self.telas["conversao"].atualizar()
        self.telas["arbitragem"].update_idletasks()
        self.telas["grafo"].atualizar()
        self.status_var.set("Dados atualizados.")
        if salvar:
            self.salvar_dados(silencioso=True)

    def registrar_resultado(self, resultado: dict) -> None:
        self.last_result = resultado
        self.telas["grafo"].atualizar()
        self.status_var.set(resultado.get("mensagem", "Execucao concluida."))

    def salvar_dados(self, silencioso: bool = False) -> None:
        self.persistencia.salvar(self.grafo)
        self.status_var.set("Dados salvos em JSON.")
        if not silencioso:
            messagebox.showinfo("Salvar", "Dados salvos com sucesso.")

    def carregar_dados(self) -> None:
        self.grafo = self.persistencia.carregar()
        self.ao_mudar_dados(salvar=False)
        messagebox.showinfo("Carregar", "Dados carregados com sucesso.")
