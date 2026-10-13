"""Item 1 — Varredura (busca incremental) de possíveis raízes.

Baseado na seção 5.4 de Chapra & Canale (2008): o intervalo [a, b] é dividido
em N subintervalos e f é avaliada em cada ponto, da esquerda para a direita.
Um subintervalo é guardado quando f troca de sinal entre suas extremidades
ou quando f vale exatamente zero em uma delas.

O gráfico da varredura fica em plot_varredura.py.
"""

import math


def varredura(f, a, b, n):
    """Devolve a lista de subintervalos de [a, b] que podem conter raiz.

    Cada subintervalo é um dicionário {"xl", "xu", "f_xl", "f_xu", "tipo"},
    em que "tipo" é "mudança de sinal" ou "zero exato".
    """
    if a >= b:
        raise ValueError("o intervalo deve satisfazer a < b")
    if n < 1:
        raise ValueError("N deve ser um inteiro positivo")

    h = (b - a) / n
    detectados = []
    x_esq = a
    f_esq = f(x_esq)

    for i in range(1, n + 1):
        if i == n:
            x_dir = b  # evita erro de arredondamento no último ponto
        else:
            x_dir = a + i * h
        f_dir = f(x_dir)

        # Pula pontos fora do domínio ou em assíntotas (f = nan ou inf).
        if math.isfinite(f_esq) and math.isfinite(f_dir):
            tipo = None
            if f_esq < 0 < f_dir or f_dir < 0 < f_esq:
                tipo = "mudança de sinal"
            # Um zero em x_esq já foi guardado no passo anterior; só o zero
            # em x = a precisa ser testado à esquerda.
            elif f_dir == 0 or (f_esq == 0 and i == 1):
                tipo = "zero exato"
            if tipo is not None:
                detectados.append({"xl": x_esq, "xu": x_dir,
                                   "f_xl": f_esq, "f_xu": f_dir, "tipo": tipo})

        x_esq = x_dir  # o ponto da direita vira o da esquerda
        f_esq = f_dir

    return detectados


def tabela_varredura(detectados):
    """Tabela dos subintervalos detectados: xl, xu, f(xl), f(xu) e tipo."""
    cabecalho = (f"{'#':>3} | {'xl':>12} | {'xu':>12} | {'f(xl)':>12}"
                 f" | {'f(xu)':>12} | Tipo")
    linhas = [cabecalho, "-" * (len(cabecalho) + 14)]
    for k, s in enumerate(detectados, start=1):
        linhas.append(f"{k:>3} | {s['xl']:>12.6g} | {s['xu']:>12.6g}"
                      f" | {s['f_xl']:>12.4e} | {s['f_xu']:>12.4e} | {s['tipo']}")
    return "\n".join(linhas)
