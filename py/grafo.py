"""
Grafo dirigido da rede social ("quem segue quem"), representado por
listas de adjacencia. Usado em SUGERIR, COMUNIDADES e TOP_SEGUIDOS.
"""


class Grafo:
    """
    Grafo dirigido com n vertices numerados de 0 a n-1 (o indice interno
    de cada usuario).

    Guardamos DUAS listas de adjacencia:
      - seguindo[v]:   vertices que v segue        (arestas que saem de v)
      - seguidores[v]: vertices que seguem v       (arestas que chegam em v)

    Com as duas listas, "quantos seguidores" e len(seguidores[v]) em O(1)
    e, para tratar o grafo como NAO dirigido (comunidades), basta olhar
    as duas listas de cada vertice.

    Memoria: O(V + E). Uma matriz de adjacencia gastaria V^2 = 4 milhoes
    de posicoes para apenas 15 mil arestas.
    """

    def __init__(self, n):
        """
        Cria o grafo sem arestas.

        Parametros:
            n (int): numero de vertices.
        Complexidade: O(n).
        """
        self.n = n
        self.quantidade_arestas = 0
        self.seguindo = [[] for _ in range(n)]
        self.seguidores = [[] for _ in range(n)]

    def adicionar_aresta(self, origem, destino):
        """
        Adiciona a aresta origem -> destino ("origem segue destino").
        A verificacao de duplicatas e feita antes, na RedeSocial.

        Complexidade: O(1) amortizado.
        """
        self.seguindo[origem].append(destino)
        self.seguidores[destino].append(origem)
        self.quantidade_arestas += 1

    def grau_saida(self, v):
        """Quantas pessoas v segue. O(1)."""
        return len(self.seguindo[v])

    def grau_entrada(self, v):
        """Quantos seguidores v tem. O(1)."""
        return len(self.seguidores[v])

    def amigos_de_amigos(self, u):
        """
        Encontra os candidatos a sugestao para u: vertices a distancia 2
        (seguidos por alguem que u segue), excluindo o proprio u e quem u
        ja segue. Para cada candidato conta as "conexoes em comum":
        quantas pessoas que u segue tambem seguem o candidato.

        Como funciona:
          1. Marca em um vetor quem u ja segue (para excluir em O(1)).
          2. Para cada amigo a que u segue, e para cada c que a segue,
             soma 1 em contador[c]. Ao fim, contador[c] e exatamente o
             numero de amigos de u que seguem c.
          3. A lista "tocados" guarda quem recebeu contagem, para nao
             precisar varrer o vetor inteiro no final.

        Parametros:
            u (int): vertice do usuario.
        Retorno:
            list: pares [candidato, conexoes_em_comum] (sem ordem).
        Complexidade: O(n + soma dos graus de saida dos amigos de u).
            O O(n) e so para criar os vetores auxiliares.
        """
        ja_segue = [False] * self.n
        for amigo in self.seguindo[u]:
            ja_segue[amigo] = True

        contador = [0] * self.n
        tocados = []
        for amigo in self.seguindo[u]:
            for candidato in self.seguindo[amigo]:
                if candidato == u or ja_segue[candidato]:
                    continue
                if contador[candidato] == 0:
                    tocados.append(candidato)
                contador[candidato] += 1

        resultado = []
        for candidato in tocados:
            resultado.append([candidato, contador[candidato]])
        return resultado

    def componentes_conexos(self):
        """
        Encontra os componentes conexos tratando cada aresta como NAO
        dirigida (se a segue b, a e b estao ligados), usando BFS.

        A fila da BFS e uma lista com um ponteiro "inicio": em vez de
        remover do comeco da lista (pop(0) custa O(n)), avancamos o
        ponteiro, entao cada vertice entra e sai da fila em O(1).

        Retorno:
            list: [tamanhos, componente_de]
              - tamanhos: lista com o tamanho de cada componente
                (inclui componentes de 1 vertice, os isolados);
              - componente_de: vetor com o numero do componente de cada
                vertice.
        Complexidade: O(V + E): cada vertice entra na fila uma vez e cada
            aresta e examinada duas vezes (uma por ponta).
        """
        componente_de = [-1] * self.n
        tamanhos = []
        for inicial in range(self.n):
            if componente_de[inicial] != -1:
                continue
            numero = len(tamanhos)
            componente_de[inicial] = numero
            fila = [inicial]
            inicio = 0
            while inicio < len(fila):
                v = fila[inicio]
                inicio += 1
                # Vizinhos no grafo nao dirigido = quem v segue + quem segue v.
                for vizinho in self.seguindo[v]:
                    if componente_de[vizinho] == -1:
                        componente_de[vizinho] = numero
                        fila.append(vizinho)
                for vizinho in self.seguidores[v]:
                    if componente_de[vizinho] == -1:
                        componente_de[vizinho] = numero
                        fila.append(vizinho)
            tamanhos.append(len(fila))
        return [tamanhos, componente_de]
