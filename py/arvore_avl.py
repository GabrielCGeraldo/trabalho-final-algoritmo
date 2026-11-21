"""
Arvore AVL usada para indexar os posts por data (comando POSTS_ENTRE).

As datas estao no formato "AAAA-MM-DD". Nesse formato a comparacao de
strings ja coincide com a ordem cronologica ("2025-01-31" < "2025-02-01"),
entao a propria string e usada como chave.
"""


class NoAVL:
    """
    No da arvore AVL.

    Atributos:
        chave (str): data "AAAA-MM-DD".
        valores (list): todos os posts com essa data (varios posts podem
            ter a mesma data, entao guardamos uma lista no mesmo no em vez
            de criar chaves repetidas).
        esquerda, direita (NoAVL | None): filhos.
        altura (int): altura da subarvore com raiz neste no (folha = 1).
    """

    def __init__(self, chave, valor):
        self.chave = chave
        self.valores = [valor]
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVL:
    """
    Arvore binaria de busca auto-balanceada (AVL). Depois de cada
    insercao, verifica o fator de balanceamento (altura da esquerda menos
    altura da direita) de cada no no caminho e, se ele sair de [-1, 1],
    aplica rotacoes. Isso garante altura O(log n).
    """

    def __init__(self):
        """Cria a arvore vazia."""
        self.raiz = None
        self.quantidade_chaves = 0   # datas distintas (nos)
        self.quantidade_valores = 0  # posts guardados

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _altura(self, no):
        """Altura de um no (0 para None). O(1)."""
        if no is None:
            return 0
        return no.altura

    def _atualizar_altura(self, no):
        """Recalcula a altura de um no a partir dos filhos. O(1)."""
        alt_esq = self._altura(no.esquerda)
        alt_dir = self._altura(no.direita)
        no.altura = 1 + (alt_esq if alt_esq > alt_dir else alt_dir)

    def _fator_balanceamento(self, no):
        """altura(esquerda) - altura(direita). AVL exige valor em [-1, 1]."""
        return self._altura(no.esquerda) - self._altura(no.direita)

    def altura(self):
        """Altura da arvore inteira. O(1)."""
        return self._altura(self.raiz)

    # ------------------------------------------------------------------
    # Rotacoes
    # ------------------------------------------------------------------
    def _rotacao_direita(self, y):
        """
        Rotacao simples a direita em torno de y (caso Esquerda-Esquerda).

                y                x
               / \\             /  \\
              x   C    -->     A    y
             / \\                   / \\
            A   B                 B   C

        x sobe e vira a nova raiz da subarvore; a subarvore B (que estava
        entre x e y na ordem) passa a ser filha esquerda de y. A ordem
        A < x < B < y < C se mantem.

        Retorno: a nova raiz da subarvore (x). Complexidade: O(1).
        """
        x = y.esquerda
        b = x.direita
        x.direita = y
        y.esquerda = b
        # y agora esta embaixo de x, entao a altura de y e atualizada primeiro.
        self._atualizar_altura(y)
        self._atualizar_altura(x)
        return x

    def _rotacao_esquerda(self, x):
        """
        Rotacao simples a esquerda em torno de x (caso Direita-Direita).
        E o espelho da rotacao a direita.

              x                    y
             / \\                 /  \\
            A   y      -->       x    C
               / \\             / \\
              B   C           A   B

        Retorno: a nova raiz da subarvore (y). Complexidade: O(1).
        """
        y = x.direita
        b = y.esquerda
        y.esquerda = x
        x.direita = b
        self._atualizar_altura(x)
        self._atualizar_altura(y)
        return y

    def _balancear(self, no):
        """
        Corrige o no se ele estiver desbalanceado. Quatro casos:
          - Esquerda-Esquerda (fb > 1 e filho esq. com fb >= 0):
                rotacao a direita.
          - Esquerda-Direita (fb > 1 e filho esq. com fb < 0):
                rotacao a esquerda no filho, depois a direita no no.
          - Direita-Direita (fb < -1 e filho dir. com fb <= 0):
                rotacao a esquerda.
          - Direita-Esquerda (fb < -1 e filho dir. com fb > 0):
                rotacao a direita no filho, depois a esquerda no no.

        Retorno: a raiz (possivelmente nova) da subarvore. O(1).
        """
        self._atualizar_altura(no)
        fb = self._fator_balanceamento(no)
        if fb > 1:
            if self._fator_balanceamento(no.esquerda) < 0:
                no.esquerda = self._rotacao_esquerda(no.esquerda)
            return self._rotacao_direita(no)
        if fb < -1:
            if self._fator_balanceamento(no.direita) > 0:
                no.direita = self._rotacao_direita(no.direita)
            return self._rotacao_esquerda(no)
        return no

    # ------------------------------------------------------------------
    # Insercao
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        """
        Insere um valor (post) na chave (data). Se a data ja existir, o
        post e adicionado a lista daquele no.

        Parametros:
            chave (str): data "AAAA-MM-DD".
            valor (qualquer): o post.
        Complexidade: O(log n), n = numero de datas distintas.
        """
        self.raiz = self._inserir(self.raiz, chave, valor)
        self.quantidade_valores += 1

    def _inserir(self, no, chave, valor):
        """
        Insercao recursiva: desce como numa BST comum e, na volta da
        recursao, rebalanceia cada no do caminho.
        """
        if no is None:
            self.quantidade_chaves += 1
            return NoAVL(chave, valor)
        if chave < no.chave:
            no.esquerda = self._inserir(no.esquerda, chave, valor)
        elif chave > no.chave:
            no.direita = self._inserir(no.direita, chave, valor)
        else:
            no.valores.append(valor)
            return no  # nenhum no novo: alturas nao mudam
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Consulta por intervalo
    # ------------------------------------------------------------------
    def buscar_intervalo(self, inicio, fim):
        """
        Devolve todos os valores com inicio <= chave <= fim, em ordem
        crescente de chave (ordem cronologica).

        So desce pelos ramos que podem ter chaves no intervalo:
          - so vai para a esquerda se chave do no > inicio
            (senao tudo a esquerda e menor que o inicio);
          - so vai para a direita se chave do no < fim
            (senao tudo a direita e maior que o fim).

        Parametros:
            inicio, fim (str): datas "AAAA-MM-DD" (inclusivas).
        Retorno:
            list: valores encontrados, em ordem cronologica.
        Complexidade: O(log n + m), m = quantidade de resultados.
        """
        resultado = []
        self._buscar_intervalo(self.raiz, inicio, fim, resultado)
        return resultado

    def _buscar_intervalo(self, no, inicio, fim, resultado):
        """Percurso em ordem (esq, no, dir) podado pelos limites."""
        if no is None:
            return
        if no.chave > inicio:
            self._buscar_intervalo(no.esquerda, inicio, fim, resultado)
        if inicio <= no.chave <= fim:
            for valor in no.valores:
                resultado.append(valor)
        if no.chave < fim:
            self._buscar_intervalo(no.direita, inicio, fim, resultado)

    def contar_nos_visitados(self, inicio, fim):
        """
        Conta quantos nos a consulta por intervalo visita. Usado so para
        mostrar no relatorio que a consulta nao percorre a arvore toda.
        """
        contador = [0]

        def visitar(no):
            if no is None:
                return
            contador[0] += 1
            if no.chave > inicio:
                visitar(no.esquerda)
            if no.chave < fim:
                visitar(no.direita)

        visitar(self.raiz)
        return contador[0]

    def esta_balanceada(self):
        """
        Verifica (para testes) se todos os nos respeitam |fb| <= 1 e se a
        ordem de BST esta correta. O(n).
        """
        def verificar(no, minimo, maximo):
            if no is None:
                return True
            if (minimo is not None and no.chave <= minimo) or \
               (maximo is not None and no.chave >= maximo):
                return False
            fb = self._fator_balanceamento(no)
            if fb < -1 or fb > 1:
                return False
            return verificar(no.esquerda, minimo, no.chave) and \
                verificar(no.direita, no.chave, maximo)

        return verificar(self.raiz, None, None)
