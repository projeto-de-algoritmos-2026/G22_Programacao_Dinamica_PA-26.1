from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .componentes import CORES, anexar_texto, formatar_caminho, formatar_valor


class TelaArbitragem(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=18)
        self.app = app

        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 16))
        ttk.Label(topo, text="Arbitragem", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="Detecte ciclos negativos com Bellman-Ford e mostre a oportunidade de lucro.", style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))

        principal = ttk.Frame(self)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(0, weight=1)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(1, weight=1)

        botoes = ttk.LabelFrame(principal, text="Operacao", padding=14)
        botoes.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 16))
        ttk.Button(botoes, text="Procurar arbitragem", style="Sucesso.TButton", command=self.procurar).pack(anchor="w")

        self.resumo = ttk.LabelFrame(principal, text="Resultado", padding=14)
        self.resumo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 16))
        self.label_status = ttk.Label(self.resumo, text="Nenhuma busca executada.")
        self.label_status.pack(anchor="w")
        self.label_valores = ttk.Label(self.resumo, text="Lucro: -")
        self.label_valores.pack(anchor="w", pady=(8, 0))

        esquerda = ttk.LabelFrame(principal, text="Ciclo encontrado", padding=10)
        esquerda.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        esquerda.rowconfigure(0, weight=1)
        esquerda.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(esquerda, columns=("Moeda",), show="headings", height=12)
        self.tree.heading("Moeda", text="Moeda")
        self.tree.column("Moeda", anchor="center", width=180)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(esquerda, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        direita = ttk.LabelFrame(principal, text="Log da busca", padding=10)
        direita.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        direita.rowconfigure(0, weight=1)
        direita.columnconfigure(0, weight=1)
        self.log = tk.Text(direita, bg="#0b1220", fg=CORES["texto"], insertbackground=CORES["texto"], relief="flat", height=12)
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll_log = ttk.Scrollbar(direita, orient="vertical", command=self.log.yview)
        scroll_log.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll_log.set)
        self.log.configure(state="disabled")

    def procurar(self) -> None:
        try:
            self._limpar()
            resultado = self.app.conversor.buscar_arbitragem(log_callback=self._log, progress_callback=self._progresso)
            self.app.registrar_resultado(resultado)
            if resultado.get("ciclo"):
                self._exibir(resultado)
                messagebox.showinfo("Arbitragem", "Oportunidade encontrada.")
            else:
                self.label_status.configure(text="Nenhuma oportunidade encontrada.")
                messagebox.showinfo("Arbitragem", "Nenhuma oportunidade encontrada.")
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def _exibir(self, resultado: dict) -> None:
        ciclo = resultado.get("ciclo", [])
        for moeda in ciclo:
            self.tree.insert("", tk.END, values=(moeda,))
        self.label_status.configure(text=f"Oportunidade encontrada: {formatar_caminho(ciclo)}")
        self.label_valores.configure(
            text=(
                f"Valor inicial: {formatar_valor(resultado.get('valor_inicial'))} | "
                f"Valor final: {formatar_valor(resultado.get('valor_final'))} | "
                f"Lucro: {formatar_valor(resultado.get('lucro'))}"
            )
        )

    def _log(self, mensagem: str) -> None:
        anexar_texto(self.log, mensagem)
        self.update_idletasks()

    def _progresso(self, atual: int, total: int) -> None:
        self.update_idletasks()

    def _limpar(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.config(state="disabled")
        self.label_status.configure(text="Procurando oportunidades...")
        self.label_valores.configure(text="Lucro: -")
