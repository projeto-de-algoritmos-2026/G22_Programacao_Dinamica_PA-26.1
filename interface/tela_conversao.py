from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .componentes import CORES, anexar_texto, formatar_caminho, formatar_valor, abrir_relatorio


class TelaConversao(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=18)
        self.app = app

        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 16))
        ttk.Label(topo, text="Conversao de moedas", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="Execute Bellman-Ford para encontrar o melhor caminho entre as moedas.", style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))

        principal = ttk.Frame(self)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(0, weight=1)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(1, weight=1)

        formulario = ttk.LabelFrame(principal, text="Parametros da conversao", padding=14)
        formulario.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 16))
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        ttk.Label(formulario, text="Moeda origem").grid(row=0, column=0, sticky="w")
        self.combo_origem = ttk.Combobox(formulario, state="readonly", width=18)
        self.combo_origem.grid(row=0, column=1, sticky="w", padx=(8, 18), pady=4)
        ttk.Label(formulario, text="Moeda destino").grid(row=0, column=2, sticky="w")
        self.combo_destino = ttk.Combobox(formulario, state="readonly", width=18)
        self.combo_destino.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=4)
        ttk.Label(formulario, text="Valor").grid(row=1, column=0, sticky="w")
        self.entrada_valor = ttk.Entry(formulario, width=18)
        self.entrada_valor.grid(row=1, column=1, sticky="w", padx=(8, 18), pady=4)
        ttk.Button(formulario, text="Converter", style="Sucesso.TButton", command=self.converter).grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))

        resultado = ttk.LabelFrame(principal, text="Resultado", padding=14)
        resultado.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 16))
        resultado.columnconfigure(1, weight=1)
        self.rotulo_caminho = ttk.Label(resultado, text="Caminho: -", wraplength=360, justify="left")
        self.rotulo_caminho.grid(row=0, column=0, columnspan=2, sticky="w")
        self.rotulo_valor = ttk.Label(resultado, text="Valor final: -")
        self.rotulo_valor.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.rotulo_metricas = ttk.Label(resultado, text="Tempo de execucao: -")
        self.rotulo_metricas.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.tabela_valores = ttk.Treeview(resultado, columns=("Moeda", "Valor"), show="headings", height=6)
        self.tabela_valores.heading("Moeda", text="Moeda")
        self.tabela_valores.heading("Valor", text="Valor acumulado")
        self.tabela_valores.column("Moeda", width=100, anchor="center")
        self.tabela_valores.column("Valor", width=140, anchor="center")
        self.tabela_valores.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        barra = ttk.Scrollbar(resultado, orient="vertical", command=self.tabela_valores.yview)
        barra.grid(row=3, column=2, sticky="ns", pady=(12, 0))
        self.tabela_valores.configure(yscrollcommand=barra.set)

        log_frame = ttk.LabelFrame(principal, text="Log da execucao", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log = tk.Text(log_frame, bg="#0b1220", fg=CORES["texto"], insertbackground=CORES["texto"], relief="flat", height=12)
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll_log = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scroll_log.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll_log.set)
        self.log.configure(state="disabled")

        painel_direito = ttk.Frame(principal)
        painel_direito.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        painel_direito.rowconfigure(1, weight=1)
        painel_direito.columnconfigure(0, weight=1)

        resumo = ttk.LabelFrame(painel_direito, text="Indicadores", padding=14)
        resumo.grid(row=0, column=0, sticky="ew")
        resumo.columnconfigure(0, weight=1)
        self.label_relaxamentos = ttk.Label(resumo, text="Numero de relaxamentos: 0")
        self.label_relaxamentos.pack(anchor="w")
        self.label_visitadas = ttk.Label(resumo, text="Quantidade de moedas visitadas: 0")
        self.label_visitadas.pack(anchor="w", pady=(8, 0))
        self.progresso = ttk.Progressbar(resumo, mode="determinate", maximum=100)
        self.progresso.pack(fill="x", pady=(12, 0))

        dicas = ttk.LabelFrame(painel_direito, text="Leitura da rota", padding=14)
        dicas.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        self.label_dicas = ttk.Label(dicas, text="O melhor caminho e o valor acumulado aparecerão aqui após a execução.", wraplength=340, justify="left")
        self.label_dicas.pack(anchor="w")

        self._atualizar_combos()

    def _atualizar_combos(self) -> None:
        siglas = [moeda.sigla for moeda in self.app.grafo.listar_moedas()]
        self.combo_origem["values"] = siglas
        self.combo_destino["values"] = siglas
        if siglas:
            if not self.combo_origem.get():
                self.combo_origem.current(0)
            if not self.combo_destino.get():
                self.combo_destino.current(min(1, len(siglas) - 1))

    def converter(self) -> None:
        try:
            self.log.config(state="normal")
            self.log.delete("1.0", tk.END)
            self.log.config(state="disabled")
            self.progresso["value"] = 0
            resultado = self.app.conversor.converter(
                self.combo_origem.get(),
                self.combo_destino.get(),
                self.entrada_valor.get(),
                log_callback=self._log,
                progress_callback=self._progresso,
            )
            self._exibir_resultado(resultado)
            self.app.registrar_resultado(resultado)
            abrir_relatorio(self, resultado)
            if not resultado.get("sucesso"):
                messagebox.showwarning("Atenção", resultado.get("mensagem", "Nao foi possivel concluir a conversao."))
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def _log(self, mensagem: str) -> None:
        anexar_texto(self.log, mensagem)
        self.update_idletasks()

    def _progresso(self, atual: int, total: int) -> None:
        self.progresso["value"] = (atual / total) * 100
        self.update_idletasks()

    def _exibir_resultado(self, resultado: dict) -> None:
        caminho = resultado.get("caminho", [])
        self.rotulo_caminho.configure(text=f"Caminho: {formatar_caminho(caminho)}")
        self.rotulo_valor.configure(
            text=(
                f"Valor final: {formatar_valor(resultado.get('valor_final'))}"
                if resultado.get("valor_final") is not None
                else "Valor final: -"
            )
        )
        self.rotulo_metricas.configure(
            text=f"Tempo de execucao: {resultado.get('tempo_execucao', 0.0):.6f} s | Complexidade: O(V x E)"
        )
        self.label_relaxamentos.configure(text=f"Numero de relaxamentos: {resultado.get('relaxamentos', 0)}")
        self.label_visitadas.configure(text=f"Quantidade de moedas visitadas: {resultado.get('quantidade_moedas_visitadas', 0)}")
        self.label_dicas.configure(
            text=(
                "Valor inicial: "
                + formatar_valor(resultado.get("valor_inicial"))
                + " | Resultado: "
                + formatar_valor(resultado.get("valor_final"))
            )
        )
        for item in self.tabela_valores.get_children():
            self.tabela_valores.delete(item)
        for moeda, valor in resultado.get("valores_caminho", []):
            self.tabela_valores.insert("", tk.END, values=(moeda, formatar_valor(valor)))

    def atualizar(self) -> None:
        self._atualizar_combos()
