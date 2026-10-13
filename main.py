"""Programa interativo da Parte I (métodos intervalares).

Item 1: varredura incremental. Itens 2, 3 e 5: bisseção, falsa posição e falsa
posição modificada, executados um de cada vez. Item 4: comparação gráfica
bisseção × falsa posição.

Uso:
    .venv/bin/python main.py
"""

import matplotlib
import matplotlib.pyplot as plt

from raizes.bissecao import bissecao, tabela_bissecao
from raizes.comparacao import comparar, plotar_comparacao, tabela_resumo
from raizes.expressao import ler_funcao
from raizes.falsa_posicao import falsa_posicao, tabela_falsa_posicao
from raizes.falsa_posicao_modificada import (
    falsa_posicao_modificada,
    tabela_falsa_posicao_modificada,
)
from raizes.plot_varredura import plotar_varredura
from raizes.varredura import tabela_varredura, varredura

PASTA_FIGURAS = "figuras"
MAX_ITER_PADRAO = 100

# Opção do menu -> (nome, função do método, função que monta a tabela)
METODOS = {
    "1": ("Bisseção", bissecao, tabela_bissecao),
    "2": ("Falsa posição", falsa_posicao, tabela_falsa_posicao),
    "3": ("Falsa posição modificada", falsa_posicao_modificada,
          tabela_falsa_posicao_modificada),
}


def perguntar(mensagem, converter=str, validar=None, padrao=None):
    """Lê uma entrada do usuário até que ela seja válida.

    `converter` transforma o texto (ex.: float, int); `validar` devolve uma
    mensagem de erro ou None. Se `padrao` for dado, Enter vazio o aceita.
    """
    while True:
        sufixo = f" [{padrao}]" if padrao is not None else ""
        texto = input(f"{mensagem}{sufixo}: ").strip()
        if not texto and padrao is not None:
            texto = str(padrao)
        try:
            valor = converter(texto)
        except ValueError as erro:
            print(f"  Entrada inválida: {erro}")
            continue
        erro = validar(valor) if validar else None
        if erro:
            print(f"  {erro}")
            continue
        return valor


def numero(texto):
    """Converte texto em float aceitando vírgula decimal (ex.: 0,5)."""
    return float(texto.replace(",", "."))


def sim_ou_nao(mensagem, padrao="s"):
    resposta = perguntar(mensagem + " (s/n)", padrao=padrao,
                         validar=lambda r: None if r.lower() in ("s", "n")
                         else "Responda 's' ou 'n'.")
    return resposta.lower() == "s"


def mostrar_figura(fig):
    """Exibe a figura sem bloquear o terminal (se houver interface gráfica)."""
    if matplotlib.get_backend().lower() != "agg":
        plt.show(block=False)
        plt.pause(0.1)
    else:
        plt.close(fig)


def etapa_varredura():
    """Item 1: lê f, [a, b] e N; repete a varredura até o usuário prosseguir."""
    expr, f = perguntar("Digite f(x) (ex.: x^3 - 2x - 5, sin(x) - x/2)", ler_funcao)
    print(f"  f(x) = {expr}")

    a = perguntar("Extremo inferior a", numero)
    b = perguntar("Extremo superior b", numero,
                  validar=lambda v: None if v > a else "b deve ser maior que a.")

    n = perguntar("Número de subdivisões N", int,
                  validar=lambda v: None if v >= 1 else "N deve ser >= 1.")
    while True:
        detectados = varredura(f, a, b, n)
        imprimir_varredura(detectados, n)

        arquivo = f"{PASTA_FIGURAS}/varredura_N{n}.png"
        fig = plotar_varredura(f, expr, a, b, n, detectados, arquivo)
        print(f"  Gráfico salvo em {arquivo}")
        mostrar_figura(fig)

        print("\nO que deseja fazer?")
        print("  [r] Refinar o rastreamento com outro valor de N")
        print("  [c] Prosseguir para o cálculo das raízes detectadas")
        opcao = perguntar("Opção", validar=lambda o: None if o.lower() in ("r", "c")
                          else "Escolha 'r' ou 'c'.").lower()
        if opcao == "c":
            return expr, f, detectados
        n = perguntar("Novo valor de N", int,
                      validar=lambda v: None if v >= 1 else "N deve ser >= 1.")


def imprimir_varredura(detectados, n):
    print(f"\n=== Varredura com N = {n} ===")
    if not detectados:
        print("Nenhuma mudança de sinal ou zero detectado. "
              "Tente aumentar N ou mudar o intervalo.")
        return
    print(tabela_varredura(detectados))


def ler_tolerancia():
    """Lê εs (%) e o limite de iterações, com valores padrão."""
    es = perguntar("Tolerância εs (%)", numero, padrao=0.5,
                   validar=lambda v: None if v > 0 else "A tolerância deve ser > 0.")
    max_iter = perguntar("Limite de iterações", int, padrao=MAX_ITER_PADRAO,
                         validar=lambda v: None if v >= 1 else "Deve ser >= 1.")
    return es, max_iter


def etapa_metodo(f, detectados, nome, metodo, tabela):
    """Itens 2, 3 e 5: aplica um método em cada subintervalo detectado."""
    print(f"\n##### {nome} #####")
    es, max_iter = ler_tolerancia()

    raizes = []
    for k, sub in enumerate(detectados, start=1):
        print(f"\n=== {nome} — raiz {k} de {len(detectados)} — intervalo "
              f"[{sub['xl']:.6g}, {sub['xu']:.6g}] ===")
        resultado = metodo(f, sub["xl"], sub["xu"], es, max_iter)
        if resultado["iteracoes"]:
            print(tabela(resultado["iteracoes"]))
        print(f"Raiz ≈ {resultado['raiz']:.10g}  "
              f"(f = {f(resultado['raiz']):.3e}; {resultado['motivo']})")
        if not resultado["convergiu"]:
            print("  Atenção: a tolerância não foi atingida.")
        # Numa assíntota (ex.: tan x em π/2) f troca de sinal sem ter raiz, e
        # |f(xr)| cresce em vez de diminuir.
        if abs(f(resultado["raiz"])) > max(abs(sub["f_xl"]), abs(sub["f_xu"])):
            print("  Atenção: |f(xr)| aumentou em relação aos extremos — "
                  "possível descontinuidade (polo), não uma raiz.")
        raizes.append(resultado["raiz"])

        if k < len(detectados) and not sim_ou_nao(
                "Deseja repetir o processo para a próxima raiz?"):
            break

    print(f"\n=== Resumo das raízes calculadas ({nome}) ===")
    for k, r in enumerate(raizes, start=1):
        print(f"  x{k} ≈ {r:.10g}")


def etapa_comparacao(f, expr, detectados):
    """Item 4: compara bisseção e falsa posição em um subintervalo escolhido."""
    print("\n##### Comparação gráfica: bisseção × falsa posição #####")
    if len(detectados) == 1:
        k = 1
    else:
        k = perguntar(f"Qual subintervalo comparar (1 a {len(detectados)})", int,
                      validar=lambda v: None if 1 <= v <= len(detectados)
                      else "Número fora da lista.")
    sub = detectados[k - 1]
    es, max_iter = ler_tolerancia()

    raiz, resultados = comparar(f, sub["xl"], sub["xu"], es, max_iter)
    print(f"\nRaiz de referência (precisão de máquina): {raiz:.15g}")
    print(tabela_resumo(f, raiz, resultados))

    arquivo = f"{PASTA_FIGURAS}/comparacao_raiz{k}.png"
    fig = plotar_comparacao(expr, sub["xl"], sub["xu"], es, raiz, resultados, arquivo)
    print(f"  Gráfico salvo em {arquivo}")
    mostrar_figura(fig)


def menu_metodos(f, expr, detectados):
    """Menu principal após a varredura. Devolve True para fazer nova varredura."""
    opcoes = {**{k: v[0] for k, v in METODOS.items()},
              "4": "Comparação gráfica bisseção × falsa posição",
              "v": "Nova varredura (outra função ou intervalo)",
              "s": "Sair"}
    while True:
        print("\nEscolha o método:")
        for chave, texto in opcoes.items():
            print(f"  [{chave}] {texto}")
        opcao = perguntar("Opção", validar=lambda o: None if o.lower() in opcoes
                          else "Opção inválida.").lower()
        if opcao == "s":
            return False
        if opcao == "v":
            return True
        if not detectados:
            print("Não há subintervalos detectados. Faça uma nova varredura.")
        elif opcao == "4":
            etapa_comparacao(f, expr, detectados)
        else:
            etapa_metodo(f, detectados, *METODOS[opcao])


def main():
    print("TRABALHO 1 — RAÍZES DE EQUAÇÕES")
    print("Parte I: métodos intervalares\n")
    while True:
        expr, f, detectados = etapa_varredura()
        if not menu_metodos(f, expr, detectados):
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")
