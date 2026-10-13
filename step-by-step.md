# Passo a passo — Parte I: métodos intervalares

Este documento explica o código das tarefas da **Pessoa 1** e da **Pessoa 2** do guia:

| Pessoa | Item | Assunto | Situação |
|---|---|---|---|
| 1 | 1 | Varredura incremental | implementado |
| 1 | 2 | Bisseção | implementado |
| 2 | 3 | Falsa posição | implementado |
| 2 | 4 | Comparação gráfica bisseção × falsa posição | implementado |
| 2 | 5 | Falsa posição modificada | implementado |
| 2 | 7 | Testes de consistência | implementado |
| 1 | 6 | Integração dos três métodos | **planejado** (seção 12) |
| 1 | 8 | Exercícios 5.1–5.5 e 5.13 | ainda não |

## 1. Ambiente e execução

```bash
python -m venv .venv                          # cria o ambiente virtual
.venv/bin/pip install -r dependencies.txt     # instala as dependências
.venv/bin/python main.py                      # programa interativo (itens 1–5)
.venv/bin/python testes_consistencia.py       # bateria de testes (item 7)
```

No Windows, use `.venv\Scripts\python` no lugar de `.venv/bin/python`.

### Bibliotecas

Todo o cálculo (varredura, bisseção, falsa posição, erros, tabelas) é feito em **Python puro**, só com a linguagem e o módulo padrão `math`. Duas bibliotecas externas são usadas:

| Biblioteca | Para quê | Por que não dá para tirar |
|---|---|---|
| `sympy` | interpretar o texto digitado pelo usuário (ver seção 4) | a alternativa seria `eval()`, que é insegura e exige `x**2` e `2*x` |
| `matplotlib` | gráficos | os itens 1.3 e 4 exigem gráficos |

As demais linhas de `dependencies.txt` (inclusive `numpy`) são dependências internas do matplotlib e do sympy. **Nenhum arquivo do projeto importa numpy.**

## 2. Arquitetura do projeto

```
met_num/
├── main.py                         # programa interativo (interface)
├── testes_consistencia.py          # item 7: roteiro de testes não interativo
├── raizes/                         # pacote com a matemática
│   ├── __init__.py
│   ├── expressao.py                # texto digitado -> função f(x)
│   ├── varredura.py                # item 1: busca incremental + tabela + gráfico
│   ├── bissecao.py                 # item 2  ┐
│   ├── falsa_posicao.py            # item 3  ├ métodos INDEPENDENTES
│   ├── falsa_posicao_modificada.py # item 5  ┘
│   └── comparacao.py               # item 4: comparação gráfica entre métodos
├── figuras/                        # gráficos gerados (criada automaticamente)
├── dependencies.txt
└── step-by-step.md
```

### Dependências entre arquivos

```
          main.py                 testes_consistencia.py
             │                              │
   ┌─────────┼──────────────┬───────────────┤
   ▼         ▼              ▼               ▼
expressao  varredura    comparacao ──► bissecao, falsa_posicao
                                 
main.py e testes_consistencia.py também importam diretamente:
   bissecao.py   falsa_posicao.py   falsa_posicao_modificada.py
```

**Os três arquivos de métodos não importam nada do projeto.** Cada um contém sua própria validação, seu cálculo de εa, seu critério de parada e sua tabela. A pequena repetição entre eles é intencional: cada método pode ser lido, testado e apresentado sozinho.

### Convenção comum (sem código compartilhado)

Embora independentes, os três métodos seguem **a mesma assinatura** e devolvem **o mesmo formato**:

```python
resultado = metodo(f, xl, xu, es, max_iter=100)
# resultado = {
#     "raiz": float,
#     "iteracoes": [{"iter", "xl", "xu", "xr", "f_xr", "ea"}, ...],
#     "convergiu": bool,
#     "motivo": str,
# }
```

(A falsa posição modificada acrescenta `"obs"` em cada iteração.)

A varredura devolve uma lista de `{"xl", "xu", "f_xl", "f_xu", "tipo"}`, exatamente os extremos que os métodos recebem.

Essa convenção é o que permite à comparação (item 4), aos testes (item 7) e ao futuro item 6 chamarem qualquer método da mesma forma.

## 3. Fluxo do programa interativo (`main.py`)

```
início
  │
  ├─ usuário digita f(x), a, b, N
  ├─► varredura ──► tabela + gráfico ──► [r] novo N (volta) | [c] prosseguir
  │
  └─► MENU (repete até [s]):
        [1] Bisseção ─────────────┐
        [2] Falsa posição ────────┼─► lê εs e limite ─► para cada subintervalo:
        [3] Falsa posição modif. ─┘      tabela de iterações + raiz
                                         "repetir para a próxima raiz?" (s/n)
        [4] Comparação gráfica ──► escolhe 1 subintervalo, lê εs
                                    ─► resumo + gráfico εt/εa × iteração
        [v] Nova varredura (volta ao início)
        [s] Sair
```

## 4. `raizes/expressao.py` e o cálculo simbólico

### O que é cálculo simbólico

- **Cálculo numérico** trabalha com números: f(2) = 2² − 2 = **2**. Sai um número, e a fórmula se perde.
- **Cálculo simbólico** trabalha com a **fórmula**. O texto `"x^2 - 2"` vira uma estrutura (uma árvore: *soma de [potência(x, 2)] e [−2]*) que o programa pode manipular como faríamos no papel: simplificar, expandir, derivar, e também transformar em uma função calculável.

Neste trabalho o SymPy é usado **só para ler o texto** digitado. Ele não calcula nenhuma raiz: quem calcula são os nossos métodos, em Python puro.

### `ler_funcao(texto)`

1. `parse_expr` (SymPy) lê o texto. Duas transformações extras deixam a digitação mais natural:
   - `convert_xor`: aceita `x^2` como potência (em Python, `^` é outra operação);
   - `implicit_multiplication_application`: aceita `2x` como `2*x` e `sin x` como `sin(x)`.
2. O dicionário `_NOMES` define os nomes reconhecidos: `x`, `e`, `pi`, `ln`/`log` (logaritmo natural), `log10`, e os apelidos em português `sen` e `tg`.
3. Verifica se a expressão depende **só** de `x`; senão, dá erro com mensagem clara.
4. `sp.lambdify(X, expr, modules="math")` transforma a expressão em uma função Python comum que usa o módulo `math` (`math.sin`, `math.log`, …).
5. A função interna `f(x)` protege contra pontos fora do domínio: `math.log(-1)` (ValueError), `1/0` (ZeroDivisionError), `exp(1000)` (OverflowError) e potências que dão número complexo, como `(-1)**0.5`, devolvem `float("nan")` em vez de quebrar o programa.

Retorna `(expr, f)`: `expr` é usado nos títulos dos gráficos e `f` nos cálculos.

## 5. `raizes/varredura.py` — item 1 (Python puro)

Baseado na seção 5.4 de Chapra & Canale (2008): divide o intervalo em pedaços pequenos e procura trocas de sinal entre as extremidades de cada pedaço.

| Função | O que faz |
|---|---|
| `gerar_malha(a, b, n)` | lista com os n + 1 pontos `a + i·h`, com h = (b − a)/n. O último ponto é exatamente `b`, sem erro de arredondamento |
| `sinal(valor)` | −1, 0 ou +1; `None` se o valor não for finito (`math.isfinite`), para pontos fora do domínio ou em assíntotas |
| `calcular_sinais(f, a, b, n)` | **item 1.3, "rotina que calcule o sinal"**: devolve `(pontos, valores, sinais)` |
| `varredura(f, a, b, n)` | **itens 1.2/1.3**: percorre cada [xᵢ, xᵢ₊₁] e devolve os subintervalos detectados (ver abaixo) |
| `tabela_varredura(detectados)` | tabela em texto (f-strings): #, xl, xu, f(xl), f(xu), tipo |
| `percentil(valores, p)` | percentil por ordenação (`sorted`), usado para limitar o eixo y |
| `plotar_varredura(...)` | **gráfico do item 1.3** |

### Regras da `varredura`

1. Valida `a < b` e `n ≥ 1`.
2. Para cada subintervalo:
   - se algum extremo tem sinal `None`, pula;
   - se `sinal(xᵢ) · sinal(xᵢ₊₁) < 0`, há **mudança de sinal**, então existe raiz no subintervalo (Teorema do Valor Intermediário, para f contínua);
   - se f(xᵢ₊₁) = 0, há um **zero exato** no ponto da malha.
3. **Evitar duplicatas:** um zero em xᵢ pertence a dois subintervalos. Ele só é reportado onde é o extremo **direito**, exceto x₀ = a.

### O gráfico (`plotar_varredura`)

- curva de f em uma malha fina de ≥ 2000 pontos (valores não finitos viram `nan`, e o matplotlib interrompe a linha ali);
- subintervalos detectados pintados de **laranja** (`axvspan`);
- subdivisões em cinza (omitidas se N > 200);
- pontos da malha: **verde** f > 0, **vermelho** f < 0, losango **preto** f = 0;
- eixo y limitado a 1,5 × o percentil 95 de |f|, para assíntotas não achatarem o gráfico;
- salvo em `figuras/varredura_N{N}.png`.

## 6. `raizes/bissecao.py` — item 2

### `bissecao(f, xl, xu, es, max_iter=100)`

Implementa o pseudocódigo da **Figura 5.10** do livro.

1. **Validação:** εs > 0 e f(xl)·f(xu) ≤ 0. Se f já é zero num extremo, devolve esse extremo sem iterar.
2. **Laço** até `max_iter`:
   1. `xr = (xl + xu) / 2` (ponto médio);
   2. εa = |(xr_novo − xr_anterior)/xr_novo| × 100 %. Na 1ª iteração não existe valor anterior, então εa fica `None` ("—" na tabela), como no livro;
   3. registra a linha (iter, xl, xu, xr, f(xr), εa);
   4. **para** se f(xr) = 0 ou εa < εs;
   5. se f(xl)·f(xr) < 0, a raiz está em [xl, xr], então `xu = xr`; senão `xl = xr` (e f(xl) é atualizado).
3. Se o limite for atingido, `convergiu = False`.

### `tabela_bissecao(iteracoes)` — item 2.3

Tabela com f-strings: iteração, xl, xu, xr (ponto médio), f(xr) e εa.

## 7. `raizes/falsa_posicao.py` — item 3

### Ideia

Em vez do ponto médio, traça a reta entre (xl, f(xl)) e (xu, f(xu)) e usa onde ela corta o eixo x (Eq. 5.7):

    xr = xu − f(xu)·(xl − xu) / (f(xl) − f(xu))

Se |f(xl)| é bem menor que |f(xu)|, a raiz provavelmente está mais perto de xl, e a reta aproveita essa informação. A bisseção ignora os valores de f.

### `falsa_posicao(f, xl, xu, es, max_iter=100)`

Mesma estrutura da bisseção (validação, εa, critério de parada, atualização do intervalo); muda só a fórmula de xr. Guarda `fl` e `fu` para não recalcular f nos extremos.

### `tabela_falsa_posicao(iteracoes)`

Mesmas colunas da bisseção.

**Problema conhecido:** em funções muito curvas, um extremo fica **preso** por muitas iterações (o método é "unilateral") e a convergência fica lenta (Exemplo 5.6). Isso motiva o item 5.

## 8. `raizes/falsa_posicao_modificada.py` — item 5

### `falsa_posicao_modificada(f, xl, xu, es, max_iter=100)`

Implementa a **Figura 5.15**. É a falsa posição com dois contadores:

- `il`: quantas iterações seguidas `xl` ficou parado;
- `iu`: o mesmo para `xu`.

Depois de cada atualização:
- se a raiz está em [xl, xr]: `xu` se move (`iu = 0`, `il += 1`). Se `il ≥ 2`, faz **`fl /= 2`**;
- senão: `xl` se move (`il = 0`, `iu += 1`). Se `iu ≥ 2`, faz **`fu /= 2`**.

Dividir f do extremo preso por 2 inclina a reta, e o próximo xr cai mais perto desse extremo, destravando o método. Por isso xr é sempre calculado com os `fl`/`fu` **guardados**, que podem já ter sido divididos, e não com f(xl)/f(xu) recalculados.

Cada iteração em que houve divisão recebe `"obs"` (ex.: `xu parado: f(xu) ÷ 2`).

### `tabela_falsa_posicao_modificada(iteracoes)`

Colunas da falsa posição + **Obs.**

### Validação com o livro

f(x) = x¹⁰ − 1 em [0; 1,3] (Exemplo 5.6):
- as 5 primeiras iterações da falsa posição dão 0,09430; 0,18176; 0,26287; 0,33811; 0,40788, idênticas à tabela do livro;
- com εs = 0,01 %: bisseção **14**, falsa posição **39**, modificada **12** iterações, os mesmos números das págs. 111–112.

## 9. `raizes/comparacao.py` — item 4

Reproduz a **Figura 5.13** do livro: erro relativo verdadeiro εt (escala log) contra o número de iterações.

| Função | O que faz |
|---|---|
| `METODOS_ITEM4` | `{"Bisseção": bissecao, "Falsa posição": falsa_posicao}`, os dois pedidos no item 4 |
| `raiz_referencia(f, xl, xu)` | εt exige a raiz exata. Esta função roda uma bisseção **sem tolerância** até o ponto médio não mudar mais em ponto flutuante, o que dá a raiz com precisão de máquina |
| `erro_verdadeiro(xr, raiz)` | εt = \|(raiz − xr)/raiz\| × 100 % (erro absoluto se a raiz for 0) |
| `comparar(f, xl, xu, es, max_iter, metodos)` | roda cada método do dicionário no mesmo intervalo; devolve `(raiz_ref, {nome: resultado})` |
| `tabela_resumo(f, raiz, resultados)` | uma linha por método: iterações, raiz, f(raiz), εa final, εt final, convergiu. Se **εt > εa**, o critério de parada "enganou" |
| `plotar_comparacao(...)` | dois gráficos: **εt × iteração** (como a Fig. 5.13) e **εa × iteração**, com linha tracejada em εs. Erros iguais a zero são omitidos (log 0 não existe) |

## 10. `main.py` — interface interativa

| Função | O que faz |
|---|---|
| `METODOS` | menu: opção → (nome, função do método, função da tabela) |
| `perguntar(mensagem, converter, validar, padrao)` | lê uma entrada e repete até ser válida |
| `numero(texto)` | `float` aceitando vírgula decimal (`0,5`) |
| `sim_ou_nao(mensagem)` | pergunta s/n |
| `mostrar_figura(fig)` | abre o gráfico sem travar o terminal; sem interface gráfica, só fecha (o arquivo já foi salvo) |
| `etapa_varredura()` | **item 1**: lê f, a, b, N; varre; imprime; plota; [r] refinar / [c] prosseguir |
| `imprimir_varredura(detectados, n)` | imprime `tabela_varredura` ou avisa que nada foi detectado |
| `ler_tolerancia()` | lê εs (padrão 0,5 %) e o limite de iterações (padrão 100) |
| `etapa_metodo(f, detectados, nome, metodo, tabela)` | **itens 2, 3, 5**: roda o método escolhido em cada subintervalo, imprime a tabela e a raiz, e pergunta se continua (item 2.3). Alerta se a tolerância não foi atingida e se \|f(xr)\| cresceu (sinal de **polo**) |
| `etapa_comparacao(f, expr, detectados)` | **item 4**: escolhe um subintervalo, compara e salva `figuras/comparacao_raiz{k}.png` |
| `menu_metodos(...)` / `main()` | menu e laço principal |

## 11. `testes_consistencia.py` — item 7

Roteiro **não interativo** que demonstra vantagens e limitações dos métodos com funções elementares. Os gráficos vão para `figuras/testes/`.

| Função | O que faz |
|---|---|
| `TODOS_OS_METODOS` | os três métodos |
| `CASOS_COMPARATIVOS` | casos com troca de sinal: os três métodos são comparados |
| `CASOS_VARREDURA` | casos em que o problema está na varredura |
| `executar_caso_comparativo` | `comparar` + `tabela_resumo` + `plotar_comparacao` + conclusão |
| `executar_caso_varredura` | varre com vários N, salva os gráficos e tenta a bisseção no intervalo inteiro |

### Resultados (εs = 0,01 %, salvo indicação)

| # | f(x) | Intervalo | Bisseção | Falsa pos. | F. P. modif. | O que mostra |
|---|---|---|---|---|---|---|
| 1 | x − 1 | [0, 3] | 15 | **1** | **1** | falsa posição é exata para funções lineares |
| 2 | e⁻ˣ − x | [0, 1] | 15 | **5** | **5** | caso típico: falsa posição mais rápida |
| 3 | cos x − x (εs = 10⁻⁶ %) | [0, 1] | 28 | 8 | **6** | com tolerância pequena a diferença aumenta |
| 4 | x¹⁰ − 1 | [0; 1,3] | 14 | 39 | **12** | falsa posição unilateral; εa final (0,0095 %) < εt final (0,031 %) |
| 5 | eˣ − 1000 | [0, 10] | 14 | 58 | **9** | f(xu) ≈ 21 000 domina a reta; a modificada corrige |
| 6 | tan x | [1, 2] | 13 | 23 | 23 | todos "convergem" para o polo π/2: é preciso verificar f(raiz) |
| 7 | sen 10x + cos 3x | [3, 5] | — | — | — | varredura: N = 10 acha 2 subintervalos, N = 100 acha 6 |
| 8 | (x − 1)² | [0, 3] | — | — | — | raiz dupla: sem troca de sinal; só achada se a malha cair em x = 1 (N = 12) |

**Resumo:**
- **Bisseção:** sempre converge se houver troca de sinal; o número de iterações quase não depende de f (13–15 nos casos 1, 2, 4–6). Lenta, mas previsível.
- **Falsa posição:** em geral bem mais rápida (casos 1–3), mas pode ficar muito lenta com curvatura forte (casos 4–5), e aí εa subestima o erro real.
- **Falsa posição modificada:** rápida nos casos bons e corrige os ruins. Foi a mais rápida ou empatada em todos os casos com raiz.
- **Todos:** exigem f contínua com troca de sinal; não acham raízes duplas e confundem polos com raízes.

## 12. Item 6 — plano (ainda não implementado)

> 6.1: rotina que tome como entrada todos os intervalos detectados na varredura, calcule todas as raízes com os três métodos, construa uma tabela por raiz por método e mostre qual método exigiu menos iterações.

### Como vai funcionar

Arquivo futuro `raizes/integracao.py`, com uma função:

```python
calcular_todas_raizes(f, detectados, es, max_iter)
```

1. Recebe a lista `detectados` que a varredura já devolve.
2. Para cada subintervalo, chama os três métodos, cada um importado do **seu próprio arquivo**. Como todos seguem a convenção da seção 2, a chamada é igual para os três:
   ```python
   METODOS = {"Bisseção": (bissecao, tabela_bissecao),
              "Falsa posição": (falsa_posicao, tabela_falsa_posicao),
              "Falsa posição modificada": (falsa_posicao_modificada,
                                           tabela_falsa_posicao_modificada)}
   for nome, (metodo, tabela) in METODOS.items():
       resultado = metodo(f, sub["xl"], sub["xu"], es, max_iter)
       print(tabela(resultado["iteracoes"]))
   ```
3. Compara `len(resultado["iteracoes"])` dos três e informa o vencedor (em empate, lista todos).
4. No fim, um quadro-resumo de todas as raízes.

No `main.py` entraria como opção **[5] Todos os métodos em todas as raízes (item 6)**.

### Exemplo de execução esperado

f(x) = x² − 2 em [−3, 3], N = 6, εs = 0,5 % (números reais, obtidos com os métodos atuais):

```
Opção: 5
Tolerância εs (%) [0.5]:
Limite de iterações [100]:

=== Raiz 2 de 2 — intervalo [1, 2] ===

--- Bisseção ---
Iter |   xl      |   xu     | xr (ponto médio) |     f(xr)     |  εa (%)
   1 |         1 |        2 |              1.5 |  2.500000e-01 |         —
   2 |         1 |      1.5 |             1.25 | -4.375000e-01 | 20.000000
 ...
   8 | 1.4140625 | 1.421875 |       1.41796875 |  1.063538e-02 |  0.275482

--- Falsa posição ---
Iter |   xl         |   xu |     xr       |     f(xr)     |  εa (%)
   1 |            1 |    2 | 1.333333333  | -2.222222e-01 |        —
   2 |  1.333333333 |    2 | 1.4          | -4.000000e-02 | 4.761905
   3 |  1.4         |    2 | 1.411764706  | -6.920415e-03 | 0.833333
   4 |  1.411764706 |    2 | 1.413793103  | -1.189061e-03 | 0.143472

--- Falsa posição modificada ---
   (5 iterações; na iteração 2, "xu parado: f(xu) ÷ 2")

Menos iterações nesta raiz: Falsa posição (4)

=== Resumo (item 6) ===
Raiz | Intervalo | Bisseção | Falsa pos. | F.P. modif. | Mais rápido
   1 | [-2, -1]  |        8 |          4 |           5 | Falsa posição
   2 | [1, 2]    |        8 |          4 |           5 | Falsa posição
```

Este exemplo também mostra que a versão modificada **nem sempre** é a mais rápida: aqui a divisão por 2 fez xr "passar" da raiz na iteração 3, gastando uma iteração a mais.

## 13. Mapa requisito → código

| Requisito | Onde está |
|---|---|
| 1.1 busca incremental | `varredura.varredura` |
| 1.2 entrada de f, intervalo e N | `main.etapa_varredura`, `expressao.ler_funcao` |
| 1.3 sinal por subdivisão e subintervalos detectados | `varredura.calcular_sinais`, `varredura.sinal`, `varredura.varredura` |
| 1.3 gráfico destacando subdivisões | `varredura.plotar_varredura` |
| 1.4 refinar N ou prosseguir | laço em `main.etapa_varredura` |
| 2.1 bisseção | `bissecao.bissecao` |
| 2.2 tolerância do usuário | `main.ler_tolerancia` |
| 2.3 tabela de iterações | `bissecao.tabela_bissecao` |
| 2.3 perguntar pela próxima raiz | `main.etapa_metodo` |
| 3.1 falsa posição | `falsa_posicao.falsa_posicao` (+ menu opção 2) |
| 4.1 comparação gráfica (Fig. 5.13) | `comparacao.comparar`, `comparacao.plotar_comparacao` (+ menu opção 4) |
| 5.1 falsa posição modificada | `falsa_posicao_modificada.falsa_posicao_modificada` (+ menu opção 3) |
| 6.1 integração | planejado: `integracao.calcular_todas_raizes` (seção 12) |
| 7.1 testes de consistência | `testes_consistencia.py` |
