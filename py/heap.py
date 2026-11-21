"""
Heap binaria implementada sobre um vetor (lista simples) e a funcao
top_k, usada em SUGERIR, TOP_SEGUIDOS e TOP_CURTIDOS.
"""


class HeapBinaria:
    """
    Heap binaria guardada em um vetor. Para o elemento na posicao i:
        pai      = (i - 1) // 2
        filho esq = 2 * i + 1
        filho dir = 2 * i + 2

    A heap e generica: recebe uma funcao prioridade_maior(a, b) que
    devolve True quando "a" deve ficar mais perto da raiz do que "b".
      - Se a funcao for "a < b", temos uma heap de MINIMO.
      - Se a funcao for "a > b", temos uma heap de MAXIMO.
    """

    def __init__(self, prioridade_maior):
        """
        Cria a heap vazia.

        Parametros:
            prioridade_maior (funcao): compara dois elementos e diz se o
                primeiro deve ficar acima do segundo.
        """
        self.dados = []
        self.prioridade_maior = prioridade_maior

    def tamanho(self):
        """Retorna quantos elementos existem na heap. O(1)."""
        return len(self.dados)

    def vazia(self):
        """Retorna True se a heap nao tem elementos. O(1)."""
        return len(self.dados) == 0

    def topo(self):
        """
        Retorna (sem remover) o elemento da raiz, ou None se vazia.
        Complexidade: O(1).
        """
        if len(self.dados) == 0:
            return None
        return self.dados[0]

    def inserir(self, elemento):
        """
        Insere um elemento: coloca no fim do vetor e faz sift-up.

        Complexidade: O(log n), pois sobe no maximo a altura da arvore.
        """
        self.dados.append(elemento)
        self._subir(len(self.dados) - 1)

    def remover_topo(self):
        """
        Remove e devolve a raiz. O ultimo elemento vai para a raiz e
        desce (sift-down) ate o lugar certo.

        Retorno:
            O elemento removido, ou None se a heap estava vazia.
        Complexidade: O(log n).
        """
        if len(self.dados) == 0:
            return None
        raiz = self.dados[0]
        ultimo = self.dados.pop()
        if len(self.dados) > 0:
            self.dados[0] = ultimo
            self._descer(0)
        return raiz

    def substituir_topo(self, elemento):
        """
        Troca a raiz por um novo elemento e reorganiza (sift-down).
        Equivale a remover_topo + inserir, mas com uma descida so.

        Complexidade: O(log n).
        """
        self.dados[0] = elemento
        self._descer(0)

    def _subir(self, i):
        """
        Sift-up: enquanto o elemento tiver prioridade maior que o pai,
        troca os dois. Para quando chega na raiz ou quando o pai ja tem
        prioridade maior/igual (propriedade de heap restaurada).
        """
        while i > 0:
            pai = (i - 1) // 2
            if self.prioridade_maior(self.dados[i], self.dados[pai]):
                self.dados[i], self.dados[pai] = self.dados[pai], self.dados[i]
                i = pai
            else:
                break

    def _descer(self, i):
        """
        Sift-down: compara o elemento com os dois filhos e troca com o
        filho de MAIOR prioridade, se esse filho tiver prioridade maior
        que ele. Repete ate virar folha ou ate nenhum filho ser "maior".
        Trocar com o melhor filho garante que o novo pai fica acima do
        outro filho tambem.
        """
        n = len(self.dados)
        while True:
            esquerdo = 2 * i + 1
            direito = 2 * i + 2
            melhor = i
            if esquerdo < n and self.prioridade_maior(self.dados[esquerdo], self.dados[melhor]):
                melhor = esquerdo
            if direito < n and self.prioridade_maior(self.dados[direito], self.dados[melhor]):
                melhor = direito
            if melhor == i:
                break
            self.dados[i], self.dados[melhor] = self.dados[melhor], self.dados[i]
            i = melhor


def top_k(elementos, k, melhor_que):
    """
    Seleciona os k melhores elementos usando uma heap de MINIMO de
    tamanho k (o "pior dos melhores" fica na raiz).

    Ideia: percorremos os elementos mantendo na heap so os k melhores
    vistos ate agora. Se um elemento novo for melhor que a raiz (o pior
    entre os guardados), ele substitui a raiz. No fim, a heap tem
    exatamente os k melhores. Retiramos todos (sai do pior para o
    melhor) e invertemos.

    Parametros:
        elementos (list): candidatos.
        k (int): quantos queremos (se k > len, devolve todos).
        melhor_que (funcao): melhor_que(a, b) e True se a e melhor que b.
    Retorno:
        list: os k melhores, do melhor para o pior.
    Complexidade: O(n log k) de tempo e O(k) de memoria extra.
    """
    if k <= 0:
        return []

    # Heap de minimo em relacao a "melhor_que": a raiz e o PIOR elemento,
    # ou seja, "a sobe" quando b e melhor que a.
    def pior_primeiro(a, b):
        return melhor_que(b, a)

    heap = HeapBinaria(pior_primeiro)
    for elemento in elementos:
        if heap.tamanho() < k:
            heap.inserir(elemento)
        elif melhor_que(elemento, heap.topo()):
            heap.substituir_topo(elemento)

    # Os elementos saem do pior para o melhor; preenchemos de tras pra frente.
    resultado = [None] * heap.tamanho()
    posicao = heap.tamanho() - 1
    while not heap.vazia():
        resultado[posicao] = heap.remover_topo()
        posicao -= 1
    return resultado
