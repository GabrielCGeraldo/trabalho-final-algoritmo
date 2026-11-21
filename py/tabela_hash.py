"""
Tabela hash com encadeamento separado (separate chaining).

Usada no comando BUSCAR (@usuario -> indice do usuario) e tambem para
detectar conexoes repetidas no arquivo seguidores.csv.
"""


def proximo_primo(n):
    """
    Devolve o menor numero primo maior ou igual a n.

    Parametros:
        n (int): valor inicial.
    Retorno:
        int: primo >= n.
    Complexidade: O(k * sqrt(p)), onde k e a distancia ate o primo p.
    Na pratica e instantaneo para os tamanhos usados aqui.
    """
    if n <= 2:
        return 2
    candidato = n if n % 2 == 1 else n + 1
    while True:
        divisor = 3
        eh_primo = True
        while divisor * divisor <= candidato:
            if candidato % divisor == 0:
                eh_primo = False
                break
            divisor += 2
        if eh_primo:
            return candidato
        candidato += 2


class TabelaHash:
    """
    Tabela hash implementada do zero, com tratamento de colisoes por
    encadeamento: cada posicao (balde) do vetor guarda uma lista de pares
    [chave, valor]. Chaves que caem na mesma posicao ficam na mesma lista.

    Aceita chaves do tipo str (ex.: "@ana_silva") ou int.

    Atributos:
        capacidade (int): numero de baldes (sempre um numero primo).
        tamanho (int): quantos pares estao guardados.
        baldes (list): vetor de listas de pares [chave, valor].
    """

    FATOR_CARGA_MAXIMO = 0.75

    def __init__(self, capacidade_inicial=101):
        """
        Cria a tabela vazia.

        Parametros:
            capacidade_inicial (int): numero minimo de baldes. E
                arredondado para o proximo primo.
        Complexidade: O(capacidade).
        """
        self.capacidade = proximo_primo(capacidade_inicial)
        self.tamanho = 0
        self.baldes = [[] for _ in range(self.capacidade)]

    # ------------------------------------------------------------------
    # Funcao de hash
    # ------------------------------------------------------------------
    def _hash(self, chave):
        """
        Calcula a posicao (indice do balde) de uma chave.

        - Strings: hash polinomial pelo metodo de Horner,
          h = (h * 31 + codigo_do_caractere) mod capacidade.
          Assim a ordem dos caracteres importa ("ab" != "ba") e todos os
          caracteres contribuem. O "mod" a cada passo evita numeros
          gigantes. 31 e primo e tem boa dispersao para texto.
        - Inteiros: hash multiplicativo de Knuth. Multiplicar pela
          constante 2654435761 (proxima de 2^32 / phi) espalha valores
          sequenciais (1, 2, 3...) por toda a tabela antes do mod.

        Parametros:
            chave (str | int): chave a ser posicionada.
        Retorno:
            int: indice entre 0 e capacidade - 1.
        Complexidade: O(L) para strings de tamanho L; O(1) para inteiros.
        """
        if isinstance(chave, int):
            return ((chave * 2654435761) % 4294967296) % self.capacidade
        h = 0
        for caractere in chave:
            h = (h * 31 + ord(caractere)) % self.capacidade
        return h

    # ------------------------------------------------------------------
    # Operacoes principais
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        """
        Insere o par (chave, valor). Se a chave ja existir, o valor e
        substituido.

        Parametros:
            chave (str | int): chave.
            valor (qualquer): valor associado.
        Complexidade: O(1) em media (fator de carga <= 0.75);
            O(n) no pior caso (todas as chaves no mesmo balde).
        """
        balde = self.baldes[self._hash(chave)]
        for par in balde:
            if par[0] == chave:
                par[1] = valor
                return
        balde.append([chave, valor])
        self.tamanho += 1
        # Se a tabela ficou cheia demais, as listas comecam a crescer e a
        # busca deixa de ser O(1). Nesse caso dobramos a capacidade.
        if self.tamanho / self.capacidade > self.FATOR_CARGA_MAXIMO:
            self._redimensionar()

    def buscar(self, chave):
        """
        Procura uma chave.

        Parametros:
            chave (str | int): chave procurada.
        Retorno:
            O valor associado, ou None se a chave nao existir.
        Complexidade: O(1) em media; O(n) no pior caso.
        """
        balde = self.baldes[self._hash(chave)]
        for par in balde:
            if par[0] == chave:
                return par[1]
        return None

    def contem(self, chave):
        """
        Diz se a chave esta na tabela.

        Retorno:
            bool: True se existe.
        Complexidade: O(1) em media.
        """
        balde = self.baldes[self._hash(chave)]
        for par in balde:
            if par[0] == chave:
                return True
        return False

    def _redimensionar(self):
        """
        Rehash: cria um vetor com o dobro de baldes (arredondado para
        primo) e reinsere todos os pares, porque a posicao de cada chave
        depende da capacidade.

        Complexidade: O(n + capacidade). Como acontece poucas vezes
        (a cada duplicacao), o custo amortizado por insercao e O(1).
        """
        baldes_antigos = self.baldes
        self.capacidade = proximo_primo(self.capacidade * 2)
        self.baldes = [[] for _ in range(self.capacidade)]
        for balde in baldes_antigos:
            for par in balde:
                self.baldes[self._hash(par[0])].append(par)

    # ------------------------------------------------------------------
    # Estatisticas (usadas no relatorio)
    # ------------------------------------------------------------------
    def estatisticas(self):
        """
        Calcula numeros sobre a distribuicao das chaves.

        Retorno:
            list: [capacidade, tamanho, fator_de_carga, baldes_vazios,
                   maior_lista, chaves_que_colidiram]
        Complexidade: O(capacidade).
        """
        vazios = 0
        maior = 0
        colisoes = 0
        for balde in self.baldes:
            qtd = len(balde)
            if qtd == 0:
                vazios += 1
            if qtd > maior:
                maior = qtd
            if qtd > 1:
                colisoes += qtd - 1
        return [self.capacidade, self.tamanho, self.tamanho / self.capacidade,
                vazios, maior, colisoes]
