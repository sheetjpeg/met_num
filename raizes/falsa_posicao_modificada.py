def falsa_posicao_modificada(f, xl, xu, es, max_iter=100):
    """Calcula uma raiz de f em [xl, xu] pela falsa posição modificada.

    Parâmetros
        f        : função de uma variável
        xl, xu   : extremos do intervalo, com f(xl) * f(xu) <= 0
        es       : tolerância (critério de parada) em porcentagem, εs > 0
        max_iter : limite de iterações

    Devolve um dicionário com
        "raiz"       : última aproximação xr
        "iteracoes"  : lista de linhas {iter, xl, xu, xr, f_xr, ea, obs}
                       ("obs" indica quando f(xl) ou f(xu) foi dividido por 2)
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

    il = iu = 0  # quantas iterações seguidas xl / xu ficaram parados
    it = 0

    while it < max_iter and not convergiu:
        it += 1
        xr_anterior = xr
        # fl e fu são os valores guardados (podem já ter sido divididos por 2).
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
                "obs": "",
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
            # Raiz em [xr, xu]: xl se move, xu fica parado.
            xl, fl = xr, fr
            il, iu = 0, iu + 1
            if iu >= 2:
                fu /= 2
                iteration_log["obs"] = "xu parado: f(xu) ÷ 2"
        else:
            # Raiz em [xl, xr]: xu se move, xl fica parado.
            xu, fu = xr, fr
            iu, il = 0, il + 1
            if il >= 2:
                fl /= 2
                iteration_log["obs"] = "xl parado: f(xl) ÷ 2"

    output = {
        "raiz": xr,
        "iteracoes": iteracoes,
        "convergiu": convergiu,
        "motivo": motivo
        }

    return output


def tabela_falsa_posicao_modificada(iteracoes):
    """Tabela de iterações com a coluna Obs. (quando f foi dividido por 2)."""
    cabecalho = (f"{'Iter':>4} | {'xl':>16} | {'xu':>16} | {'xr':>16}"
                 f" | {'f(xr)':>13} | {'εa (%)':>12} | Obs.")
    linhas = [cabecalho, "-" * (len(cabecalho) + 18)]
    for r in iteracoes:
        ea = "—" if r["ea"] is None else f"{r['ea']:.6f}"
        linhas.append(f"{r['iter']:>4} | {r['xl']:>16.10g} | {r['xu']:>16.10g}"
                      f" | {r['xr']:>16.10g} | {r['f_xr']:>13.6e} | {ea:>12}"
                      f" | {r['obs']}")
    return "\n".join(linhas)
