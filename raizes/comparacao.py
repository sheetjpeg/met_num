"""Item 4 — Comparação gráfica entre métodos intervalares.

Reproduz a ideia da Figura 5.13 de Chapra & Canale (2008): o erro relativo
percentual verdadeiro εt de cada método é plotado (em escala log) contra o
número de iterações. Como a raiz exata em geral não é conhecida, ela é
estimada com precisão de máquina por `raiz_referencia`.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from .bissecao import bissecao
from .falsa_posicao import falsa_posicao

# Métodos pedidos no item 4. Outros dicionários podem ser passados a `comparar`.
METODOS_ITEM4 = {"Bisseção": bissecao, "Falsa posição": falsa_posicao}


def raiz_referencia(f, xl, xu):
    """Estima a raiz em [xl, xu] com precisão de máquina (bisseção sem tolerância).

    Para quando o ponto médio não difere mais dos extremos em ponto flutuante.
    """
    fl, fu = f(xl), f(xu)
    if fl == 0:
        return xl
    if fu == 0:
        return xu
    for _ in range(2000):
        xm = (xl + xu) / 2
        if xm in (xl, xu):
            break
        fm = f(xm)
        if fm == 0:
            return xm
        if fl * fm < 0:
            xu = xm
        else:
            xl, fl = xm, fm
    return (xl + xu) / 2


def erro_verdadeiro(xr, raiz):
    """εt = |(raiz - xr) / raiz| * 100 %; erro absoluto se a raiz for 0."""
    if raiz == 0:
        return abs(xr)
    return abs((raiz - xr) / raiz) * 100


def comparar(f, xl, xu, es, max_iter=100, metodos=METODOS_ITEM4):
    """Executa cada método no mesmo intervalo.

    Devolve (raiz_ref, {nome: resultado}).
    """
    raiz = raiz_referencia(f, xl, xu)
    resultados = {nome: metodo(f, xl, xu, es, max_iter)
                  for nome, metodo in metodos.items()}
    return raiz, resultados


def tabela_resumo(f, raiz, resultados):
    """Tabela com iterações, raiz obtida, f(raiz), εa e εt finais de cada método.

    Comparar εa com εt mostra se o critério de parada foi confiável: se
    εt > εa, o método parou achando estar mais perto da raiz do que estava.
    """
    cabecalho = (f"{'Método':<26} | {'Iterações':>9} | {'Raiz':>16} | {'f(raiz)':>10}"
                 f" | {'εa final (%)':>12} | {'εt final (%)':>12} | Convergiu")
    linhas = [cabecalho, "-" * (len(cabecalho) + 2)]
    for nome, res in resultados.items():
        ea = res["iteracoes"][-1]["ea"] if res["iteracoes"] else None
        ea_txt = "—" if ea is None else f"{ea:.3e}"
        et = erro_verdadeiro(res["raiz"], raiz)
        linhas.append(f"{nome:<26} | {len(res['iteracoes']):>9} | {res['raiz']:>16.10g}"
                      f" | {f(res['raiz']):>10.3e} | {ea_txt:>12} | {et:>12.3e}"
                      f" | {'sim' if res['convergiu'] else 'não'}")
    return "\n".join(linhas)


def plotar_comparacao(expr, xl, xu, es, raiz, resultados, arquivo=None, titulo=None):
    """Gráfico de εt e εa por iteração para cada método (escala log em y).

    Iterações com erro exatamente zero não são desenhadas (log de 0).
    """
    fig, (ax_t, ax_a) = plt.subplots(1, 2, figsize=(12, 5))
    marcadores = ["o", "s", "^", "D"]

    for k, (nome, res) in enumerate(resultados.items()):
        its = [r["iter"] for r in res["iteracoes"]]
        et = [erro_verdadeiro(r["xr"], raiz) for r in res["iteracoes"]]
        ea = [r["ea"] if r["ea"] is not None else 0 for r in res["iteracoes"]]
        et = [e if e > 0 else float("nan") for e in et]
        ea = [e if e > 0 else float("nan") for e in ea]
        rotulo = f"{nome} ({len(its)} iter.)"
        m = marcadores[k % len(marcadores)]
        ax_t.semilogy(its, et, marker=m, ms=4, label=rotulo)
        ax_a.semilogy(its, ea, marker=m, ms=4, label=rotulo)

    ax_a.axhline(es, color="black", ls="--", lw=1, label=f"εs = {es:g}%")

    ax_t.set_title("Erro relativo percentual verdadeiro εt")
    ax_a.set_title("Erro relativo percentual aproximado εa")
    for ax in (ax_t, ax_a):
        ax.set_xlabel("Iterações")
        ax.set_ylabel("Erro (%)")
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=9)
        ax.xaxis.get_major_locator().set_params(integer=True)

    fig.suptitle(titulo or f"f(x) = {expr} em [{xl:g}, {xu:g}] — raiz ≈ {raiz:.10g}")
    fig.tight_layout()

    if arquivo:
        Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(arquivo, dpi=150)
    return fig
