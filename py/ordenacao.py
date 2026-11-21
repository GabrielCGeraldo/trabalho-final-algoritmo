"""
Merge Sort implementado do zero (comando RANKING e ordenacao do tamanho
das comunidades).
"""


def merge_sort(lista, vem_antes):
    """
    Ordena uma lista com Merge Sort e devolve uma NOVA lista ordenada
    (a original nao e alterada).

    Parametros:
        lista (list): elementos a ordenar.
        vem_antes (funcao): vem_antes(a, b) e True se "a" deve aparecer
            antes de "b" no resultado.
    Retorno:
        list: nova lista ordenada.
    Complexidade: O(n log n) em TODOS os casos (melhor, medio e pior),
        com O(n) de memoria extra. E estavel: elementos "empatados"
        mantem a ordem original.
    """
    copia = []
    for elemento in lista:
        copia.append(elemento)
    if len(copia) <= 1:
        return copia
    auxiliar = [None] * len(copia)
    _ordenar(copia, auxiliar, 0, len(copia) - 1, vem_antes)
    return copia


def _ordenar(v, aux, inicio, fim, vem_antes):
    """
    Divide o intervalo v[inicio..fim] ao meio, ordena cada metade
    recursivamente e intercala as duas. A recursao tem profundidade
    log2(n) e cada nivel faz O(n) de trabalho na intercalacao.
    """
    if inicio >= fim:
        return
    meio = (inicio + fim) // 2
    _ordenar(v, aux, inicio, meio, vem_antes)
    _ordenar(v, aux, meio + 1, fim, vem_antes)
    _intercalar(v, aux, inicio, meio, fim, vem_antes)


def _intercalar(v, aux, inicio, meio, fim, vem_antes):
    """
    Intercala as metades ja ordenadas v[inicio..meio] e v[meio+1..fim].

    Copia o trecho para o vetor auxiliar e vai escolhendo, a cada passo,
    o menor entre o primeiro da metade esquerda (i) e o primeiro da metade
    direita (j). So pega da direita quando ela vem ESTRITAMENTE antes;
    em empate pega da esquerda, o que torna a ordenacao estavel.
    """
    for k in range(inicio, fim + 1):
        aux[k] = v[k]
    i = inicio
    j = meio + 1
    k = inicio
    while i <= meio and j <= fim:
        if vem_antes(aux[j], aux[i]):
            v[k] = aux[j]
            j += 1
        else:
            v[k] = aux[i]
            i += 1
        k += 1
    # Sobrou algo em uma das metades: ja esta ordenado, so copiar.
    while i <= meio:
        v[k] = aux[i]
        i += 1
        k += 1
    while j <= fim:
        v[k] = aux[j]
        j += 1
        k += 1
