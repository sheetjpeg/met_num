"""Item 1.3 — Gráfico da varredura.

Mostra f em [a, b], todas as N subdivisões e destaca os subintervalos
detectados pela varredura (varredura.py).
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt


def plotar_varredura(f, expr, a, b, n, detectados, arquivo=None):
    """Plota f em [a, b], as n subdivisões e os subintervalos detectados.

    Se `arquivo` for informado, a figura também é salva nesse caminho.
    """
    h = (b - a) / n
    pontos = []
    for i in range(n + 1):
        pontos.append(a + i * h)
    pontos[-1] = b
    valores = [f(x) for x in pontos]

    # Curva de f numa malha bem mais fina que a da varredura. Valores não
    # finitos viram nan, e o matplotlib interrompe a linha nesses pontos.
    m = max(2000, 20 * n)
    x_curva, y_curva = [], []
    for i in range(m + 1):
        x = a + i * (b - a) / m
        y = f(x)
        x_curva.append(x)
        y_curva.append(y if math.isfinite(y) else float("nan"))

    fig, ax = plt.subplots(figsize=(11, 5.5))

    for k, sub in enumerate(detectados):
        ax.axvspan(sub["xl"], sub["xu"], color="tab:orange", alpha=0.3,
                   label="subintervalo com raiz" if k == 0 else None)

    # Linhas verticais finas marcam as subdivisões (omitidas se forem muitas).
    if n <= 200:
        for x in pontos:
            ax.axvline(x, color="gray", lw=0.5, alpha=0.5)

    ax.axhline(0, color="black", lw=0.8)
    ax.plot(x_curva, y_curva, color="tab:blue", lw=1.6, label=f"f(x) = {expr}")

    # Pontos da malha coloridos pelo sinal de f.
    positivos = [(x, y) for x, y in zip(pontos, valores) if math.isfinite(y) and y > 0]
    negativos = [(x, y) for x, y in zip(pontos, valores) if math.isfinite(y) and y < 0]
    zeros = [(x, y) for x, y in zip(pontos, valores) if y == 0]
    for grupo, marcador, cor, tamanho, rotulo in [
            (positivos, "o", "tab:green", 4, "f(xᵢ) > 0"),
            (negativos, "o", "tab:red", 4, "f(xᵢ) < 0"),
            (zeros, "D", "black", 6, "f(xᵢ) = 0")]:
        if grupo:
            ax.plot([x for x, _ in grupo], [y for _, y in grupo],
                    marcador, color=cor, ms=tamanho, label=rotulo)

    # Limita o eixo y para que uma assíntota não esmague o gráfico: usa o
    # valor que fica a 95% da lista ordenada de |f(xᵢ)|.
    modulos = sorted(abs(y) for y in valores if math.isfinite(y))
    if modulos:
        limite = modulos[round(0.95 * (len(modulos) - 1))] * 1.5 or 1.0
        ax.set_ylim(-limite, limite)

    ax.set_xlim(a, b)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(f"Varredura incremental — N = {n} subdivisões, "
                 f"{len(detectados)} subintervalo(s) detectado(s)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if arquivo:
        Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(arquivo, dpi=150)
    return fig
