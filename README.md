# Sistema Inteligente de Conversão de Moedas utilizando Bellman-Ford

**Número da Lista:** 22  
**Disciplina:** Estruturas de Dados

## Alunos

| Matrícula | Aluno |
|-----------|--------|
| 211061903 | Isaque Santos |
| 200023985 | Maria Eduarda dos Santos Marques |

## Sobre

Sistema desenvolvido em **Python**  para simular um mercado de câmbio usando o algoritmo **Bellman-Ford**.

O projeto permite cadastrar moedas, cadastrar e alterar taxas de conversão, realizar conversões entre moedas, detectar oportunidades de arbitragem e visualizar o grafo de relações entre as moedas. O algoritmo Bellman-Ford é implementado manualmente para encontrar o melhor caminho de conversão e identificar ciclos negativos.

A principal motivação para a escolha do Bellman-Ford foi sua capacidade de resolver o problema de menor caminho em grafos com pesos negativos, além de permitir a detecção de arbitragem em cenários de câmbio.

---

## Screenshots

Inclua aqui capturas de tela da aplicação, como:

- Tela inicial do programa
- Tela de cadastro de moedas
- Tela de conversão e arbitragem
- Tela de visualização do grafo

### Vídeo do trabalho

[Clique aqui para assistir à demonstração](link)

---

## Instalação

### Pré-requisitos

- Python 3.x
- Terminal ou Prompt de Comando

### Execução

Na raiz do projeto:

```bash
python main.py
```

---


## Algoritmo Utilizado

### Bellman-Ford

O algoritmo Bellman-Ford é usado para encontrar o melhor caminho entre moedas e para detectar ciclos negativos que representam oportunidades de arbitragem.


## Observações

- O sistema utiliza dados em JSON para persistência automática.
- O grafo exibe os caminhos encontrados e destaca conversões e ciclos negativos quando o algoritmo é executado.

---
