# relatorio de desenvolvimento do trabalho 1 (parte 1)

## varedura de possiveis raizes:

1. o usuario define a funcao de interesse, foi utilizada a funcao sympy para fazer o parse dos caracteres da funcao para o codigo

2. junto com a funcao, o usuario define arbitrariamente um intervalo de busca e a resolucao (N), com o numero de subdivisoes que seram verificadas ao decorrer do intervalo

3. inicialmente o programa define o "passo" entre os pontos de busca, e se inicia um processo de iteracoes continuas onde xl(ponto inferior) e xu(ponto superior), que dentro da funcao de varredura sao determinados como vizinhos portanto xi e xi+1. o funcionamento do loop eh basico, onde o sinal dos vizinhos eh verificado, caso haja mudanca de sinal o intervalo eh salvo como um dicionario de tuplas, contendo a possivel raiz. <DESCREVER O CASO DOS ZEROS das funcoes>.

4. apos as iteracoes e determinacao dos possiveis intervalos o codigo por meio de recursividade questiona se o usuario quer buscar em um intervalo diferente(intervalos estes qeu serao utilizados posteriormente para o calculo das raizes)

## implementacao do metodo da bissecao

1. o metodo implemtenta o pseudocodigo proposto no livro base onde temos como os componentes da funcao os parametros:
 - f : que descreve a funcao proposta, ja detedzada??
 - xl: determinando o intervalo minimo
 - xu: intervalo maximo
 - es: contendo a taxa de 
 - n: o numero de iteracoes maximas no processo de busca

### pipeline do algoritmo

1. a funcao f(xl) e f(xu) sao calculadas, e tem seus sinais verificados, se forem opsotos, temos a atualizacao da variavel temporaria <NAO LEMBRO O NOME>

2. o valor da variavel contendo o ponto medio entre xl e xl eh calculada (f(c)), apartrid dos sinais a variavel toma a posicao do ponto superior ou inferios
 - se sign(f(c)) == sign(f(xu)), entao xu = c
 - <caso contrario ae>

<codigo das condicionais>
<foto da troca de posicao com uma setinha no grafico apon tando algo do tipo, novo valor de xu e mostrando onde estava antes>

3. eh verificado a tolerancia em relacao ao novo valor mais proximo da raiz, para saber se o loop ja pode ser interrompoido, em conjunto com a verificacao do numero de iteracoes realizas, ainda foi implementado uma medida de seguranca onde se o valor de f(c) nao mudar mais que uma determinada taxa durante um periodo de iteracoes o metodo para para economizar poder computacional


