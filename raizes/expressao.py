"""Leitura da expressão digitada pelo usuário e conversão para função Python.

O SymPy é usado só para interpretar o texto (cálculo simbólico): ele
transforma "x^2 - 2" em uma expressão matemática e depois em uma função
comum do módulo `math`. Nenhum cálculo de raiz é feito aqui.
"""

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

X = sp.Symbol("x")

# Permite escrever "x^2" (em vez de x**2) e "2x" (em vez de 2*x).
_TRANSFORMACOES = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

# Nomes aceitos na expressão além de x.
_NOMES = {
    "x": X,
    "e": sp.E,
    "pi": sp.pi,
    "ln": sp.log,
    "log": sp.log,
    "log10": lambda arg: sp.log(arg, 10),
    "sen": sp.sin,
    "tg": sp.tan,
}


def ler_funcao(texto):
    """Converte o texto em (expressão simbólica, função f(x)).

    f recebe um número (float) e devolve um float. Fora do domínio
    (ex.: log(-1), 1/0, sqrt(-1)) devolve float("nan") em vez de dar erro.
    Lança ValueError se a expressão for inválida ou depender de outra variável.
    """
    try:
        expr = parse_expr(texto, local_dict=_NOMES, transformations=_TRANSFORMACOES)
    except Exception as erro:
        raise ValueError(f"expressão inválida: {erro}") from erro

    if not isinstance(expr, sp.Expr):
        raise ValueError("a entrada não é uma expressão matemática")
    extras = expr.free_symbols - {X}
    if extras:
        nomes = ", ".join(sorted(str(s) for s in extras))
        raise ValueError(f"a expressão deve depender apenas de x (encontrado: {nomes})")

    f_math = sp.lambdify(X, expr, modules="math")

    def f(x):
        try:
            valor = f_math(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            return float("nan")
        # Ex.: (-1)**0.5 em Python dá um número complexo: fora do domínio real.
        if isinstance(valor, complex):
            return float("nan")
        return float(valor)

    return expr, f
