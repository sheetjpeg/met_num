"""Item 7 — Testes de consistência dos métodos intervalares.

Executa uma bateria de exemplos com funções elementares que ilustram as
vantagens e as limitações da varredura, da bisseção, da falsa posição e da
falsa posição modificada. Não é interativo: imprime tabelas no terminal e
salva os gráficos em figuras/testes/.

Uso:
    .venv/bin/python testes_consistencia.py
"""

import matplotlib

matplotlib.use("Agg")  # só salva as figuras, sem abrir janelas

import matplotlib.pyplot as plt  # noqa: E402

from raizes.bissecao import bissecao  # noqa: E402
from raizes.comparacao import comparar, plotar_comparacao, tabela_resumo  # noqa: E402
from raizes.expressao import ler_funcao  # noqa: E402
from raizes.falsa_posicao import falsa_posicao  # noqa: E402
from raizes.falsa_posicao_modificada import falsa_posicao_modificada  # noqa: E402
from raizes.plot_varredura import plotar_varredura  # noqa: E402
from raizes.varredura import varredura  # noqa: E402

PASTA = "figuras/testes"

TODOS_OS_METODOS = {
    "Bisseção": bissecao,
    "Falsa posição": falsa_posicao,
    "Falsa posição modificada": falsa_posicao_modificada,
}

# Casos em que existe troca de sinal: os três métodos são executados e comparados.
CASOS_COMPARATIVOS = [
    {
        "titulo": "Função linear — a falsa posição é exata",
        "expr": "x - 1", "a": 0, "b": 3, "es": 0.01,
        "conclusao": "Para f linear, a reta da falsa posição coincide com a própria "
                     "função: a raiz sai na 1ª iteração. A bisseção não usa os "
                     "valores de f e precisa de ~15 iterações mesmo assim.",
    },
    {
        "titulo": "Caso típico — falsa posição mais rápida",
        "expr": "exp(-x) - x", "a": 0, "b": 1, "es": 0.01,
        "conclusao": "Função suave e com pouca curvatura: a falsa posição converge "
                     "em bem menos iterações que a bisseção (como na Figura 5.13).",
    },
    {
        "titulo": "Caso típico com tolerância muito pequena",
        "expr": "cos(x) - x", "a": 0, "b": 1, "es": 1e-6,
        "conclusao": "Com εs = 1e-6 %, a bisseção precisa de muitas iterações (o "
                     "intervalo só cai pela metade a cada passo), enquanto a falsa "
                     "posição usa a forma de f e chega lá muito antes.",
    },
    {
        "titulo": "Limitação da falsa posição — curvatura forte (Exemplo 5.6)",
        "expr": "x^10 - 1", "a": 0, "b": 1.3, "es": 0.01,
        "conclusao": "xu fica preso em 1,3 e xl se arrasta até a raiz: a falsa posição "
                     "é unilateral e fica mais lenta que a bisseção. Além disso, εa "
                     "final < εt final: o critério de parada engana. A versão "
                     "modificada divide f(xu) por 2 e resolve o problema.",
    },
    {
        "titulo": "Limitação da falsa posição — crescimento exponencial",
        "expr": "exp(x) - 1000", "a": 0, "b": 10, "es": 0.01,
        "conclusao": "f(xu) ≈ 21000 domina a reta, então xr avança muito pouco a cada "
                     "passo. A falsa posição é a mais lenta; a modificada é a mais rápida.",
    },
    {
        "titulo": "Limitação de todos — descontinuidade (polo)",
        "expr": "tan(x)", "a": 1, "b": 2, "es": 0.01,
        "conclusao": "tan(x) troca de sinal em π/2 sem ter raiz. Os três métodos "
                     "'convergem' para o polo e |f(raiz)| é enorme. Por isso é "
                     "sempre preciso conferir f(raiz) ≈ 0 (seção 5.3.1 do livro).",
    },
]

# Casos que afetam a etapa de varredura (antes dos métodos).
CASOS_VARREDURA = [
    {
        "titulo": "Limitação da varredura — raízes muito próximas",
        "expr": "sin(10x) + cos(3x)", "a": 3, "b": 5, "ns": [10, 100],
        "conclusao": "Com N pequeno, duas raízes no mesmo subintervalo se cancelam e "
                     "não há troca de sinal. Refinar N (item 1.4) revela as raízes "
                     "perdidas (Figura 5.16 do livro).",
    },
    {
        "titulo": "Limitação de todos — raiz dupla (sem troca de sinal)",
        "expr": "(x - 1)^2", "a": 0, "b": 3, "ns": [10, 12],
        "conclusao": "f(x) = (x−1)² toca o eixo sem cruzá-lo. A varredura só acha a "
                     "raiz se um ponto da malha cair exatamente em x = 1 (N = 12), e "
                     "nenhum método intervalar pode ser iniciado, pois f(xl)·f(xu) > 0.",
    },
]


def cabecalho(numero, titulo, expr):
    print("\n" + "=" * 78)
    print(f"Teste {numero}: {titulo}")
    print(f"f(x) = {expr}")
    print("=" * 78)


def executar_caso_comparativo(numero, caso):
    """Roda os três métodos no mesmo intervalo, imprime o resumo e salva o gráfico."""
    expr, f = ler_funcao(caso["expr"])
    a, b, es = caso["a"], caso["b"], caso["es"]
    cabecalho(numero, caso["titulo"], expr)
    print(f"Intervalo [{a}, {b}], εs = {es:g}%")

    raiz, resultados = comparar(f, a, b, es, max_iter=1000, metodos=TODOS_OS_METODOS)
    print(f"Raiz de referência: {raiz:.15g}\n")
    print(tabela_resumo(f, raiz, resultados))

    arquivo = f"{PASTA}/teste{numero}.png"
    fig = plotar_comparacao(expr, a, b, es, raiz, resultados, arquivo,
                            titulo=f"Teste {numero}: {caso['titulo']}")
    plt.close(fig)
    print(f"\nConclusão: {caso['conclusao']}")
    print(f"Gráfico: {arquivo}")


def executar_caso_varredura(numero, caso):
    """Roda a varredura com vários N e testa a bisseção no intervalo inteiro."""
    expr, f = ler_funcao(caso["expr"])
    a, b = caso["a"], caso["b"]
    cabecalho(numero, caso["titulo"], expr)

    for n in caso["ns"]:
        detectados = varredura(f, a, b, n)
        intervalos = ", ".join(f"[{d['xl']:.4g}, {d['xu']:.4g}] ({d['tipo']})"
                               for d in detectados) or "nenhum"
        print(f"N = {n:>4}: {len(detectados)} subintervalo(s): {intervalos}")
        arquivo = f"{PASTA}/teste{numero}_N{n}.png"
        plt.close(plotar_varredura(f, expr, a, b, n, detectados, arquivo))
        print(f"          gráfico: {arquivo}")

    try:
        bissecao(f, a, b, 0.01)
        print(f"Bisseção em [{a}, {b}]: executada (há troca de sinal nos extremos).")
    except ValueError as erro:
        print(f"Bisseção em [{a}, {b}]: recusada — {erro}.")

    print(f"\nConclusão: {caso['conclusao']}")


def main():
    print("TESTES DE CONSISTÊNCIA — MÉTODOS INTERVALARES (item 7)")
    numero = 1
    for caso in CASOS_COMPARATIVOS:
        executar_caso_comparativo(numero, caso)
        numero += 1
    for caso in CASOS_VARREDURA:
        executar_caso_varredura(numero, caso)
        numero += 1


if __name__ == "__main__":
    main()
