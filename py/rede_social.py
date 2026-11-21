"""
Camada de dominio: monta todas as estruturas a partir dos dados lidos
e oferece as consultas (BUSCAR, SUGERIR, COMUNIDADES, POSTS_ENTRE,
TOP_SEGUIDOS, TOP_CURTIDOS e RANKING).

Esta camada NAO imprime nada: devolve os resultados para a interface
(menu interativo ou API de linha de comando) formatar como texto ou JSON.
"""

from tabela_hash import TabelaHash
from heap import top_k
from arvore_avl import ArvoreAVL
from grafo import Grafo
from ordenacao import merge_sort


class Usuario:
    """
    Registro de um usuario.

    Atributos:
        indice (int): posicao interna (0..n-1), usada como vertice do grafo.
        id (int): id do arquivo usuarios.csv.
        usuario (str): "@nome_de_usuario" (unico).
        nome (str): nome completo.
        data_cadastro (str): "AAAA-MM-DD".
        quantidade_posts (int): posts publicados.
        total_curtidas (int): soma das curtidas dos posts dele.
    """

    def __init__(self, indice, id_usuario, usuario, nome, data_cadastro):
        self.indice = indice
        self.id = id_usuario
        self.usuario = usuario
        self.nome = nome
        self.data_cadastro = data_cadastro
        self.quantidade_posts = 0
        self.total_curtidas = 0


class Post:
    """
    Registro de um post.

    Atributos:
        id (int), autor (Usuario), data (str "AAAA-MM-DD"),
        curtidas (int), texto (str).
    """

    def __init__(self, id_post, autor, data, curtidas, texto):
        self.id = id_post
        self.autor = autor
        self.data = data
        self.curtidas = curtidas
        self.texto = texto


def data_valida(texto):
    """
    Verifica se o texto e uma data real no formato AAAA-MM-DD
    (inclusive dias por mes e ano bissexto).

    Parametros:
        texto (str): data a validar.
    Retorno:
        bool: True se valida.
    Complexidade: O(1).
    """
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        return False
    partes = [texto[0:4], texto[5:7], texto[8:10]]
    for parte in partes:
        if not parte.isdigit():
            return False
    ano = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
    if mes < 1 or mes > 12 or dia < 1:
        return False
    dias_no_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    bissexto = (ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0
    limite = dias_no_mes[mes - 1]
    if mes == 2 and bissexto:
        limite = 29
    return dia <= limite


class RedeSocial:
    """
    Fachada que guarda e conecta todas as estruturas:
      - usuarios (list): vetor de Usuario, por indice interno;
      - indice_por_id (list): vetor id -> indice interno (-1 se nao existe);
      - tabela_usuarios (TabelaHash): "@usuario" -> Usuario  (BUSCAR);
      - grafo (Grafo): quem segue quem  (SUGERIR, COMUNIDADES, TOP_SEGUIDOS);
      - posts (list): todos os posts  (TOP_CURTIDOS);
      - arvore_posts (ArvoreAVL): data -> posts  (POSTS_ENTRE).
    """

    def __init__(self, linhas_usuarios, linhas_seguidores, linhas_posts):
        """
        Constroi tudo a partir das linhas devolvidas por
        aedlib.social_carregar_dados().

        Linhas invalidas (campos faltando, id desconhecido), conexoes
        repetidas e "auto-seguir" sao ignoradas e contadas em
        self.ignorados = [usuarios, conexoes, posts].

        Complexidade: O(U + S + P log D), com U usuarios, S conexoes,
            P posts e D datas distintas.
        """
        self.ignorados = [0, 0, 0]
        self._ranking_cache = None
        self._carregar_usuarios(linhas_usuarios)
        self._carregar_seguidores(linhas_seguidores)
        self._carregar_posts(linhas_posts)

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    def _carregar_usuarios(self, linhas):
        """Preenche o vetor de usuarios, o vetor por id e a tabela hash. O(U)."""
        self.usuarios = []
        # Tamanho inicial ~2x o numero de usuarios: fator de carga ~0.5.
        self.tabela_usuarios = TabelaHash(2 * len(linhas) + 1)
        maior_id = 0
        validas = []
        for linha in linhas:
            if len(linha) < 4 or not linha[0].strip().isdigit():
                self.ignorados[0] += 1
                continue
            validas.append(linha)
            if int(linha[0]) > maior_id:
                maior_id = int(linha[0])

        self.indice_por_id = [-1] * (maior_id + 1)
        for linha in validas:
            id_usuario = int(linha[0])
            nome_usuario = linha[1].strip()
            if self.indice_por_id[id_usuario] != -1 or self.tabela_usuarios.contem(nome_usuario):
                self.ignorados[0] += 1  # id ou @usuario repetido
                continue
            usuario = Usuario(len(self.usuarios), id_usuario, nome_usuario,
                              linha[2].strip(), linha[3].strip())
            self.usuarios.append(usuario)
            self.indice_por_id[id_usuario] = usuario.indice
            self.tabela_usuarios.inserir(nome_usuario, usuario)

    def usuario_por_id(self, texto_id):
        """
        Converte um id (texto do CSV) no Usuario correspondente.
        Retorno: Usuario ou None. Complexidade: O(1).
        """
        texto_id = texto_id.strip()
        if not texto_id.isdigit():
            return None
        valor = int(texto_id)
        if valor >= len(self.indice_por_id) or self.indice_por_id[valor] == -1:
            return None
        return self.usuarios[self.indice_por_id[valor]]

    def _carregar_seguidores(self, linhas):
        """
        Monta o grafo. Usa uma TabelaHash com chave inteira
        origem * n + destino para descartar conexoes repetidas em O(1).
        Complexidade: O(S) em media.
        """
        n = len(self.usuarios)
        self.grafo = Grafo(n)
        ja_vistas = TabelaHash(2 * len(linhas) + 1)
        for linha in linhas:
            if len(linha) < 2:
                self.ignorados[1] += 1
                continue
            seguidor = self.usuario_por_id(linha[0])
            seguido = self.usuario_por_id(linha[1])
            if seguidor is None or seguido is None or seguidor is seguido:
                self.ignorados[1] += 1
                continue
            chave = seguidor.indice * n + seguido.indice
            if ja_vistas.contem(chave):
                self.ignorados[1] += 1
                continue
            ja_vistas.inserir(chave, True)
            self.grafo.adicionar_aresta(seguidor.indice, seguido.indice)

    def _carregar_posts(self, linhas):
        """
        Cria os posts, atualiza contadores dos autores e insere cada post
        na AVL pela data. Complexidade: O(P log D).
        """
        self.posts = []
        self.arvore_posts = ArvoreAVL()
        for linha in linhas:
            if len(linha) < 5:
                self.ignorados[2] += 1
                continue
            autor = self.usuario_por_id(linha[1])
            data = linha[2].strip()
            curtidas = linha[3].strip()
            if autor is None or not data_valida(data) or not curtidas.isdigit() \
                    or not linha[0].strip().isdigit():
                self.ignorados[2] += 1
                continue
            # Se o texto tiver ';', o split da aedlib quebrou em mais campos.
            texto = linha[4]
            for i in range(5, len(linha)):
                texto = texto + ";" + linha[i]
            post = Post(int(linha[0]), autor, data, int(curtidas), texto)
            self.posts.append(post)
            autor.quantidade_posts += 1
            autor.total_curtidas += post.curtidas
            self.arvore_posts.inserir(data, post)

    # ------------------------------------------------------------------
    # 3.1 BUSCAR (tabela hash)
    # ------------------------------------------------------------------
    def buscar_usuario(self, nome_usuario):
        """
        Procura um usuario pelo "@usuario" na tabela hash. Aceita o nome
        com ou sem "@".

        Retorno: Usuario ou None. Complexidade: O(L) em media
            (L = tamanho do nome, para calcular o hash).
        """
        nome_usuario = nome_usuario.strip()
        if not nome_usuario.startswith("@"):
            nome_usuario = "@" + nome_usuario
        return self.tabela_usuarios.buscar(nome_usuario)

    def quantidade_seguindo(self, usuario):
        """Quantas pessoas o usuario segue. O(1)."""
        return self.grafo.grau_saida(usuario.indice)

    def quantidade_seguidores(self, usuario):
        """Quantos seguidores o usuario tem. O(1)."""
        return self.grafo.grau_entrada(usuario.indice)

    # ------------------------------------------------------------------
    # 3.2 SUGERIR (grafo + heap)
    # ------------------------------------------------------------------
    def sugerir(self, usuario, k):
        """
        Sugere ate k pessoas para seguir (amigos de amigos).

        Ordem: mais conexoes em comum primeiro; empate pelo @usuario em
        ordem alfabetica (para o resultado ser deterministico).

        Retorno:
            list: [sugestoes, total_candidatos], onde sugestoes e uma lista
            de pares [Usuario, conexoes_em_comum].
        Complexidade: O(n + A + C log k), A = soma dos graus de saida dos
            amigos, C = numero de candidatos.
        """
        candidatos = self.grafo.amigos_de_amigos(usuario.indice)
        usuarios = self.usuarios

        def melhor(a, b):
            if a[1] != b[1]:
                return a[1] > b[1]
            return usuarios[a[0]].usuario < usuarios[b[0]].usuario

        escolhidos = top_k(candidatos, k, melhor)
        sugestoes = []
        for par in escolhidos:
            sugestoes.append([usuarios[par[0]], par[1]])
        return [sugestoes, len(candidatos)]

    # ------------------------------------------------------------------
    # 3.3 COMUNIDADES (grafo)
    # ------------------------------------------------------------------
    def comunidades(self):
        """
        Calcula os componentes conexos (grafo nao dirigido).

        Retorno:
            list: [tamanhos_comunidades, isolados]
              - tamanhos_comunidades: tamanhos dos componentes com 2 ou
                mais usuarios, do maior para o menor;
              - isolados: quantos usuarios nao seguem ninguem e nao sao
                seguidos por ninguem (componentes de tamanho 1).
        Complexidade: O(V + E) da BFS + O(c log c) para ordenar os c
            componentes.
        """
        tamanhos = self.grafo.componentes_conexos()[0]
        comunidades = []
        isolados = 0
        for tamanho in tamanhos:
            if tamanho == 1:
                isolados += 1
            else:
                comunidades.append(tamanho)
        comunidades = merge_sort(comunidades, lambda a, b: a > b)
        return [comunidades, isolados]

    # ------------------------------------------------------------------
    # 3.4 POSTS_ENTRE (AVL)
    # ------------------------------------------------------------------
    def posts_entre(self, data_inicio, data_fim):
        """
        Posts com data_inicio <= data <= data_fim, em ordem cronologica.
        As datas devem estar validadas e em ordem (feito pela interface).

        Complexidade: O(log D + m), m = posts encontrados.
        """
        return self.arvore_posts.buscar_intervalo(data_inicio, data_fim)

    # ------------------------------------------------------------------
    # 3.5 TOP_SEGUIDOS e TOP_CURTIDOS (heap)
    # ------------------------------------------------------------------
    def top_seguidos(self, k):
        """
        Os k usuarios com mais seguidores (empate: @usuario alfabetico).

        Retorno: lista de pares [Usuario, seguidores].
        Complexidade: O(U log k).
        """
        grafo = self.grafo

        def melhor(a, b):
            sa = grafo.grau_entrada(a.indice)
            sb = grafo.grau_entrada(b.indice)
            if sa != sb:
                return sa > sb
            return a.usuario < b.usuario

        resultado = []
        for usuario in top_k(self.usuarios, k, melhor):
            resultado.append([usuario, grafo.grau_entrada(usuario.indice)])
        return resultado

    def top_curtidos(self, k):
        """
        Os k posts com mais curtidas (empate: menor id do post primeiro).

        Retorno: lista de Post.
        Complexidade: O(P log k).
        """
        def melhor(a, b):
            if a.curtidas != b.curtidas:
                return a.curtidas > b.curtidas
            return a.id < b.id

        return top_k(self.posts, k, melhor)

    # ------------------------------------------------------------------
    # 3.6 RANKING (ordenacao)
    # ------------------------------------------------------------------
    def engajamento(self, usuario):
        """engajamento = seguidores * 2 + soma das curtidas dos posts. O(1)."""
        return self.grafo.grau_entrada(usuario.indice) * 2 + usuario.total_curtidas

    def ranking(self):
        """
        Ranking completo por engajamento (maior primeiro); empate pelo
        @usuario em ordem alfabetica. O resultado fica em cache, pois os
        dados nao mudam durante a execucao.

        Retorno: lista de pares [Usuario, engajamento], ja ordenada.
        Complexidade: O(U log U) com Merge Sort (O(1) depois do cache).
        """
        if self._ranking_cache is None:
            pares = []
            for usuario in self.usuarios:
                pares.append([usuario, self.engajamento(usuario)])

            def vem_antes(a, b):
                if a[1] != b[1]:
                    return a[1] > b[1]
                return a[0].usuario < b[0].usuario

            self._ranking_cache = merge_sort(pares, vem_antes)
        return self._ranking_cache

    def posicao_no_ranking(self, usuario):
        """
        Posicao (comecando em 1) do usuario no ranking.
        Complexidade: O(U) para localizar no vetor ordenado
            (alem do custo do ranking, se ainda nao estiver em cache).
        """
        lista = self.ranking()
        for i in range(len(lista)):
            if lista[i][0] is usuario:
                return i + 1
        return -1
