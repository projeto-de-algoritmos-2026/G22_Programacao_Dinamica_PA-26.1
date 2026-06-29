from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .componentes import atualizar_texto, configurar_treeview, limpar_treeview


class TelaCadastro(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=18)
        self.app = app
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.frame_moedas = FrameMoedas(self.notebook, app)
        self.frame_taxas = FrameTaxas(self.notebook, app)
        self.notebook.add(self.frame_moedas, text="Moedas")
        self.notebook.add(self.frame_taxas, text="Taxas")

    def atualizar(self) -> None:
        self.frame_moedas.atualizar()
        self.frame_taxas.atualizar()


class FrameMoedas(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=4)
        self.app = app
        self.moeda_selecionada = None

        conteudo = ttk.Frame(self)
        conteudo.pack(fill="both", expand=True)
        conteudo.columnconfigure(1, weight=1)
        conteudo.rowconfigure(1, weight=1)

        formulario = ttk.LabelFrame(conteudo, text="Cadastro de moedas", padding=14)
        formulario.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        formulario.columnconfigure(1, weight=1)

        ttk.Label(formulario, text="Nome da moeda").grid(row=0, column=0, sticky="w")
        self.entrada_nome = ttk.Entry(formulario, width=42)
        self.entrada_nome.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        ttk.Label(formulario, text="Sigla").grid(row=1, column=0, sticky="w")
        self.entrada_sigla = ttk.Entry(formulario, width=18)
        self.entrada_sigla.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=4)

        botoes = ttk.Frame(formulario)
        botoes.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(botoes, text="Adicionar", style="Primario.TButton", command=self.adicionar).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text="Editar", style="Primario.TButton", command=self.editar).pack(side="left", padx=8)
        ttk.Button(botoes, text="Excluir", style="Perigo.TButton", command=self.excluir).pack(side="left", padx=8)
        ttk.Button(botoes, text="Limpar", command=self.limpar).pack(side="left", padx=8)

        tabela_frame = ttk.LabelFrame(conteudo, text="Moedas cadastradas", padding=8)
        tabela_frame.grid(row=1, column=0, sticky="nsew")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)

        self.tree_moedas = ttk.Treeview(tabela_frame, height=12)
        configurar_treeview(self.tree_moedas, ["Nome", "Sigla"], [240, 110])
        self.tree_moedas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree_moedas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree_moedas.configure(yscrollcommand=scroll.set)
        self.tree_moedas.bind("<<TreeviewSelect>>", self.selecionar)

        painel_lateral = ttk.LabelFrame(conteudo, text="Ajuda rápida", padding=14)
        painel_lateral.grid(row=1, column=1, sticky="nsew", padx=(16, 0))
        conteudo.columnconfigure(0, weight=2)
        conteudo.columnconfigure(1, weight=1)
        ttk.Label(painel_lateral, text="Use siglas curtas em caixa alta, por exemplo BRL, USD e EUR.", wraplength=220, justify="left").pack(anchor="w")
        ttk.Label(painel_lateral, text="As taxas cadastradas alimentam o Bellman-Ford e o grafo.", wraplength=220, justify="left", padding=(0, 12, 0, 0)).pack(anchor="w")

    def adicionar(self) -> None:
        try:
            self.app.grafo.adicionar_moeda(self.entrada_nome.get(), self.entrada_sigla.get())
            self.app.ao_mudar_dados()
            self.limpar()
            messagebox.showinfo("Sucesso", "Moeda adicionada com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def editar(self) -> None:
        if not self.moeda_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma moeda na tabela.")
            return
        try:
            self.app.grafo.editar_moeda(self.moeda_selecionada, self.entrada_nome.get(), self.entrada_sigla.get())
            self.app.ao_mudar_dados()
            self.limpar()
            messagebox.showinfo("Sucesso", "Moeda atualizada com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def excluir(self) -> None:
        if not self.moeda_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma moeda na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta moeda?"):
            return
        try:
            self.app.grafo.excluir_moeda(self.moeda_selecionada)
            self.app.ao_mudar_dados()
            self.limpar()
            messagebox.showinfo("Sucesso", "Moeda excluida com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def limpar(self) -> None:
        self.moeda_selecionada = None
        self.entrada_nome.delete(0, tk.END)
        self.entrada_sigla.delete(0, tk.END)
        self.tree_moedas.selection_remove(self.tree_moedas.selection())

    def selecionar(self, _event=None) -> None:
        selecionados = self.tree_moedas.selection()
        if not selecionados:
            return
        item = self.tree_moedas.item(selecionados[0], "values")
        if not item:
            return
        self.moeda_selecionada = item[1]
        self.entrada_nome.delete(0, tk.END)
        self.entrada_nome.insert(0, item[0])
        self.entrada_sigla.delete(0, tk.END)
        self.entrada_sigla.insert(0, item[1])

    def atualizar(self) -> None:
        limpar_treeview(self.tree_moedas)
        for moeda in self.app.grafo.listar_moedas():
            self.tree_moedas.insert("", tk.END, values=(moeda.nome, moeda.sigla))


class FrameTaxas(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=4)
        self.app = app
        self.taxa_selecionada = None

        conteudo = ttk.Frame(self)
        conteudo.pack(fill="both", expand=True)
        conteudo.columnconfigure(1, weight=1)
        conteudo.rowconfigure(1, weight=1)

        formulario = ttk.LabelFrame(conteudo, text="Cadastro de taxas", padding=14)
        formulario.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        ttk.Label(formulario, text="Moeda origem").grid(row=0, column=0, sticky="w")
        self.combo_origem = ttk.Combobox(formulario, state="readonly", width=18)
        self.combo_origem.grid(row=0, column=1, sticky="w", padx=(8, 18), pady=4)
        ttk.Label(formulario, text="Moeda destino").grid(row=0, column=2, sticky="w")
        self.combo_destino = ttk.Combobox(formulario, state="readonly", width=18)
        self.combo_destino.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=4)

        ttk.Label(formulario, text="Taxa de conversao").grid(row=1, column=0, sticky="w")
        self.entrada_taxa = ttk.Entry(formulario, width=18)
        self.entrada_taxa.grid(row=1, column=1, sticky="w", padx=(8, 18), pady=4)

        botoes = ttk.Frame(formulario)
        botoes.grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))
        ttk.Button(botoes, text="Adicionar", style="Primario.TButton", command=self.adicionar).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text="Editar", style="Primario.TButton", command=self.editar).pack(side="left", padx=8)
        ttk.Button(botoes, text="Excluir", style="Perigo.TButton", command=self.excluir).pack(side="left", padx=8)

        tabela_frame = ttk.LabelFrame(conteudo, text="Taxas cadastradas", padding=8)
        tabela_frame.grid(row=1, column=0, sticky="nsew")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)

        self.tree_taxas = ttk.Treeview(tabela_frame, height=12)
        configurar_treeview(self.tree_taxas, ["Origem", "Destino", "Taxa"], [130, 130, 120])
        self.tree_taxas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree_taxas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree_taxas.configure(yscrollcommand=scroll.set)
        self.tree_taxas.bind("<<TreeviewSelect>>", self.selecionar)

        painel_lateral = ttk.LabelFrame(conteudo, text="Orientacao", padding=14)
        painel_lateral.grid(row=1, column=1, sticky="nsew", padx=(16, 0))
        ttk.Label(painel_lateral, text="Cadastre pares de conversao no formato origem -> destino.", wraplength=220, justify="left").pack(anchor="w")
        ttk.Label(painel_lateral, text="Exemplo: BRL -> USD com taxa 0,18.", wraplength=220, justify="left", padding=(0, 12, 0, 0)).pack(anchor="w")
        ttk.Label(painel_lateral, text="Use taxas positivas e mantenha os dados atualizados para a visualizacao do grafo.", wraplength=220, justify="left", padding=(0, 12, 0, 0)).pack(anchor="w")
        self._atualizar_combos()

    def _atualizar_combos(self) -> None:
        siglas = [moeda.sigla for moeda in self.app.grafo.listar_moedas()]
        self.combo_origem["values"] = siglas
        self.combo_destino["values"] = siglas
        if siglas and not self.combo_origem.get():
            self.combo_origem.current(0)
        if siglas and not self.combo_destino.get():
            self.combo_destino.current(min(1, len(siglas) - 1))

    def adicionar(self) -> None:
        try:
            self.app.grafo.adicionar_taxa(self.combo_origem.get(), self.combo_destino.get(), self.entrada_taxa.get())
            self.app.ao_mudar_dados()
            self.limpar_campos()
            messagebox.showinfo("Sucesso", "Taxa adicionada com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def editar(self) -> None:
        if not self.taxa_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma taxa na tabela.")
            return
        try:
            self.app.grafo.editar_taxa(self.taxa_selecionada[0], self.taxa_selecionada[1], self.entrada_taxa.get())
            self.app.ao_mudar_dados()
            self.limpar_campos()
            messagebox.showinfo("Sucesso", "Taxa atualizada com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def excluir(self) -> None:
        if not self.taxa_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma taxa na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta taxa?"):
            return
        try:
            self.app.grafo.excluir_taxa(self.taxa_selecionada[0], self.taxa_selecionada[1])
            self.app.ao_mudar_dados()
            self.limpar_campos()
            messagebox.showinfo("Sucesso", "Taxa excluida com sucesso.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def limpar_campos(self) -> None:
        self.taxa_selecionada = None
        self.entrada_taxa.delete(0, tk.END)
        self.tree_taxas.selection_remove(self.tree_taxas.selection())

    def selecionar(self, _event=None) -> None:
        selecionados = self.tree_taxas.selection()
        if not selecionados:
            return
        item = self.tree_taxas.item(selecionados[0], "values")
        if not item:
            return
        self.taxa_selecionada = (item[0], item[1])
        self.combo_origem.set(item[0])
        self.combo_destino.set(item[1])
        self.entrada_taxa.delete(0, tk.END)
        self.entrada_taxa.insert(0, item[2].replace(",", "."))

    def atualizar(self) -> None:
        self._atualizar_combos()
        limpar_treeview(self.tree_taxas)
        for aresta in self.app.grafo.listar_taxas():
            self.tree_taxas.insert("", tk.END, values=(aresta.origem, aresta.destino, f"{aresta.taxa:.6f}".rstrip("0").rstrip(".")))
