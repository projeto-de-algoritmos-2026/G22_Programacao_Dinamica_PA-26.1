from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable, List, Sequence


CORES = {
    "fundo": "#0f172a",
    "painel": "#111827",
    "painel_claro": "#1f2937",
    "texto": "#e5e7eb",
    "texto_secundario": "#94a3b8",
    "primaria": "#38bdf8",
    "secundaria": "#22c55e",
    "alerta": "#f59e0b",
    "erro": "#ef4444",
    "sucesso": "#10b981",
    "linha": "#334155",
}


def configurar_tema(root: tk.Tk) -> None:
    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=CORES["fundo"])

    estilo.configure("TFrame", background=CORES["fundo"])
    estilo.configure("Painel.TFrame", background=CORES["painel"])
    estilo.configure("Card.TFrame", background=CORES["painel_claro"], relief="flat")
    estilo.configure("TLabel", background=CORES["fundo"], foreground=CORES["texto"])
    estilo.configure("Titulo.TLabel", font=("Segoe UI", 18, "bold"), foreground=CORES["texto"], background=CORES["fundo"])
    estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 10), foreground=CORES["texto_secundario"], background=CORES["fundo"])
    estilo.configure("CardTitulo.TLabel", font=("Segoe UI", 11, "bold"), foreground=CORES["texto"], background=CORES["painel_claro"])
    estilo.configure("CardValor.TLabel", font=("Segoe UI", 18, "bold"), foreground=CORES["primaria"], background=CORES["painel_claro"])
    estilo.configure("CardRodape.TLabel", font=("Segoe UI", 9), foreground=CORES["texto_secundario"], background=CORES["painel_claro"])
    estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
    estilo.configure("Primario.TButton", background=CORES["primaria"], foreground="#0f172a")
    estilo.map("Primario.TButton", background=[("active", "#7dd3fc")])
    estilo.configure("Sucesso.TButton", background=CORES["secundaria"], foreground="#052e16")
    estilo.configure("Perigo.TButton", background=CORES["erro"], foreground="#ffffff")
    estilo.configure("TNotebook", background=CORES["fundo"], borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(16, 10), background=CORES["painel_claro"], foreground=CORES["texto"])
    estilo.map("TNotebook.Tab", background=[("selected", CORES["primaria"]), ("active", CORES["linha"])])
    estilo.configure("Treeview", background=CORES["painel"], foreground=CORES["texto"], fieldbackground=CORES["painel"], rowheight=28, bordercolor=CORES["linha"])
    estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=CORES["painel_claro"], foreground=CORES["texto"])
    estilo.map("Treeview", background=[("selected", CORES["primaria"])])
    estilo.configure("TCombobox", padding=6)
    estilo.configure("Horizontal.TProgressbar", troughcolor=CORES["painel_claro"], background=CORES["primaria"], bordercolor=CORES["painel_claro"], lightcolor=CORES["primaria"], darkcolor=CORES["primaria"])


def criar_card(parent, titulo: str, valor: str, rodape: str = "") -> ttk.Frame:
    frame = ttk.Frame(parent, style="Card.TFrame", padding=16)
    frame.columnconfigure(0, weight=1)
    ttk.Label(frame, text=titulo, style="CardTitulo.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text=valor, style="CardValor.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 2))
    ttk.Label(frame, text=rodape, style="CardRodape.TLabel", wraplength=260, justify="left").grid(row=2, column=0, sticky="w")
    return frame


def configurar_treeview(tree: ttk.Treeview, colunas: Sequence[str], larguras: Sequence[int]) -> None:
    tree["columns"] = colunas
    tree["show"] = "headings"
    for coluna, largura in zip(colunas, larguras):
        tree.heading(coluna, text=coluna)
        tree.column(coluna, width=largura, anchor="center")


def limpar_treeview(tree: ttk.Treeview) -> None:
    for item in tree.get_children():
        tree.delete(item)


def atualizar_texto(widget: tk.Text, texto: str) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, texto)
    widget.configure(state="disabled")


def anexar_texto(widget: tk.Text, texto: str) -> None:
    widget.configure(state="normal")
    widget.insert(tk.END, texto + "\n")
    widget.see(tk.END)
    widget.configure(state="disabled")


def formatar_valor(valor: float | None) -> str:
    if valor is None:
        return "-"
    return f"{valor:,.6f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")


def formatar_caminho(caminho: List[str]) -> str:
    if not caminho:
        return "-"
    return " \u2192 ".join(caminho)


def abrir_relatorio(parent: tk.Widget, resultado: dict) -> None:
    janela = tk.Toplevel(parent)
    janela.title("Relatorio da Conversao")
    janela.configure(bg=CORES["fundo"])
    janela.geometry("560x520")
    janela.transient(parent)
    janela.grab_set()

    frame = ttk.Frame(janela, padding=18)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)

    titulo = "RELATORIO"
    ttk.Label(frame, text=titulo, style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text="Bellman-Ford aplicado a conversao de moedas.", style="Subtitulo.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 16))

    texto = tk.Text(frame, height=20, wrap="word", bg="#0b1220", fg=CORES["texto"], insertbackground=CORES["texto"], relief="flat")
    texto.grid(row=2, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
    scrollbar.grid(row=2, column=1, sticky="ns")
    texto.configure(yscrollcommand=scrollbar.set)

    caminho = formatar_caminho(resultado.get("caminho", []))
    valor_inicial = resultado.get("valor_inicial")
    valor_final = resultado.get("valor_final")
    relatorio = [
        "==============================",
        "RELATORIO",
        "==============================",
        f"Origem: {resultado.get('origem', '-')}",
        f"Destino: {resultado.get('destino', '-')}",
        f"Valor inicial: {formatar_valor(valor_inicial)}",
        f"Valor final: {formatar_valor(valor_final)}",
        f"Melhor caminho: {caminho}",
        f"Quantidade de relaxamentos: {resultado.get('relaxamentos', 0)}",
        f"Tempo de execucao: {resultado.get('tempo_execucao', 0.0):.6f} s",
        "Complexidade: O(V x E)",
    ]
    if resultado.get("ciclo"):
        relatorio.extend([
            "",
            f"Ciclo negativo: {formatar_caminho(resultado.get('ciclo', []))}",
        ])
    atualizar_texto(texto, "\n".join(relatorio))

    ttk.Button(frame, text="Fechar", style="Primario.TButton", command=janela.destroy).grid(row=3, column=0, sticky="e", pady=(16, 0))
