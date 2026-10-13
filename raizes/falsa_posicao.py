def falsa_posicao(f, xl, xu, es, max_iter=100):
    """Calcula uma raiz de f em [xl, xu] pelo método da falsa posição.

    Parâmetros
        f        : função de uma variável
        xl, xu   : extremos do intervalo, com f(xl) * f(xu) <= 0
        es       : tolerância (critério de parada) em porcentagem, εs > 0
        max_iter : limite de iterações

    Devolve um dicionário com
        "raiz"       : última aproximação xr
        "iteracoes"  : lista de linhas {iter, xl, xu, xr, f_xr, ea}
        "convergiu"  : True se εa < εs ou f(xr) == 0
        "motivo"     : texto explicando o critério de parada
    """
    if es <= 0:
        raise ValueError("a tolerância deve ser positiva")
    fl, fu = f(xl), f(xu)
    if fl * fu > 0:
        raise ValueError("f(xl) e f(xu) têm o mesmo sinal; não há raiz garantida")

    iteracoes = []
    xr = None
    convergiu = False
    motivo = f"limite de {max_iter} iterações atingido"

    # Raiz exatamente em um dos extremos
    if fl == 0 or fu == 0:
        if fl == 0:
            xr = xl
        else:
            xr = xu
        convergiu = True
        motivo = "f é exatamente zero em um extremo do intervalo"

    it = 0

    while it < max_iter and not convergiu:
        it += 1
        xr_anterior = xr
        xr = xu - fu * (xl - xu) / (fl - fu)
        fr = f(xr)

        ea = None
        if xr_anterior is not None and xr != 0:
            ea = abs((xr - xr_anterior) / xr) * 100

        iteration_log = {
                "iter": it,
                "xl": xl,
                "xu": xu,
                "xr": xr,
                "f_xr": fr,
                "ea": ea,
        }

        iteracoes.append(iteration_log)

        if fr == 0:
            convergiu = True
            motivo = "f(xr) = 0 (raiz exata)"
            break

        if ea is not None and ea < es:
            convergiu = True
            motivo = f"εa = {ea:.3g}% < εs = {es:g}%"
            break

        if fl * fr > 0:
            xl, fl = xr, fr
        else:
            xu, fu = xr, fr

    output = {
        "raiz": xr,
        "iteracoes": iteracoes,
        "convergiu": convergiu,
        "motivo": motivo
        }

    return output


def tabela_falsa_posicao(iteracoes):
    """Tabela de iterações: iteração, xl, xu, xr, f(xr) e εa."""
    cabecalho = (f"{'Iter':>4} | {'xl':>16} | {'xu':>16} | {'xr':>16}"
                 f" | {'f(xr)':>13} | {'εa (%)':>12}")
    linhas = [cabecalho, "-" * len(cabecalho)]
    for r in iteracoes:
        ea = "—" if r["ea"] is None else f"{r['ea']:.6f}"
        linhas.append(f"{r['iter']:>4} | {r['xl']:>16.10g} | {r['xu']:>16.10g}"
                      f" | {r['xr']:>16.10g} | {r['f_xr']:>13.6e} | {ea:>12}")
    return "\n".join(linhas)
