"""
Camada de interface: interpreta os comandos, valida os parametros,
chama a RedeSocial e formata o resultado como texto legivel ou JSON.

E usada tanto pelo menu interativo quanto pela API de linha de comando
(main.py). Nenhuma estrutura de dados e implementada aqui.
"""

from rede_social import data_valida
from saida_json import ObjetoJSON


class ErroComando(Exception):
    """Erro de uso: comando invalido, parametro faltando ou invalido."""


class ResultadoComando:
    """
    Resultado de um comando, nas duas formas de saida.

    Atributos:
        texto (str): saida legivel para humanos.
        json (ObjetoJSON): mesma informacao em formato estruturado.
    """

    def __init__(self, texto, objeto_json):
        self.texto = texto
        self.json = objeto_json


# ----------------------------------------------------------------------
# Leitura e validacao de parametros
# ----------------------------------------------------------------------
def separar_argumentos(argumentos):
    """
    Separa argumentos posicionais das opcoes "--nome valor" / "--json".

    Parametros:
        argumentos (list): palavras digitadas depois do comando.
    Retorno:
        list: [posicionais, opcoes, usar_json], onde opcoes e uma lista
        de pares [nome, valor].
    Lanca:
        ErroComando se uma opcao que exige valor vier sem valor.
    Complexidade: O(a), a = numero de argumentos.
    """
    posicionais = []
    opcoes = []
    usar_json = False
    i = 0
    while i < len(argumentos):
        arg = argumentos[i]
        if arg == "--json":
            usar_json = True
        elif arg.startswith("--"):
            if i + 1 >= len(argumentos):
                raise ErroComando("A opcao " + arg + " precisa de um valor.")
            opcoes.append([arg[2:], argumentos[i + 1]])
            i += 1
        else:
            posicionais.append(arg)
        i += 1
    return [posicionais, opcoes, usar_json]


def obter_opcao(opcoes, nome):
    """Valor da opcao --nome, ou None se nao foi informada. O(a)."""
    for par in opcoes:
        if par[0] == nome:
            return par[1]
    return None


def ler_inteiro_positivo(texto, nome_parametro):
    """
    Converte texto em inteiro > 0.

    Lanca:
        ErroComando com mensagem clara se nao for numero ou se for <= 0.
    """
    if texto is None:
        raise ErroComando("Parametro '" + nome_parametro + "' esta faltando.")
    if not texto.isdigit():
        raise ErroComando("O parametro '" + nome_parametro + "' deve ser um numero inteiro "
                          "positivo (recebido: '" + texto + "').")
    valor = int(texto)
    if valor <= 0:
        raise ErroComando("O parametro '" + nome_parametro + "' deve ser maior que zero.")
    return valor


def exigir_posicionais(posicionais, quantidade, uso):
    """Lanca ErroComando se faltarem parametros obrigatorios."""
    if len(posicionais) < quantidade:
        raise ErroComando("Parametros faltando. Uso: " + uso)


def obter_usuario(rede, nome):
    """
    Busca o usuario na tabela hash ou lanca ErroComando se nao existir.
    """
    usuario = rede.buscar_usuario(nome)
    if usuario is None:
        exibido = nome if nome.startswith("@") else "@" + nome
        raise ErroComando("Usuario " + exibido + " nao existe.")
    return usuario


def cortar(texto, tamanho):
    """Corta um texto longo para caber numa coluna da tabela."""
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho - 3] + "..."


# ----------------------------------------------------------------------
# 3.1 BUSCAR
# ----------------------------------------------------------------------
def comando_buscar(rede, posicionais, opcoes):
    """BUSCAR @usuario: dados do usuario via tabela hash."""
    exigir_posicionais(posicionais, 1, "buscar @usuario")
    usuario = obter_usuario(rede, posicionais[0])
    seguindo = rede.quantidade_seguindo(usuario)
    seguidores = rede.quantidade_seguidores(usuario)

    texto = ("Usuario:          " + usuario.usuario + "\n"
             "Nome:             " + usuario.nome + "\n"
             "Data de cadastro: " + usuario.data_cadastro + "\n"
             "Segue:            " + str(seguindo) + "\n"
             "Seguidores:       " + str(seguidores) + "\n"
             "Posts publicados: " + str(usuario.quantidade_posts))
    obj = (ObjetoJSON().adicionar("id", usuario.id)
           .adicionar("usuario", usuario.usuario)
           .adicionar("nome", usuario.nome)
           .adicionar("data_cadastro", usuario.data_cadastro)
           .adicionar("seguindo", seguindo)
           .adicionar("seguidores", seguidores)
           .adicionar("posts", usuario.quantidade_posts))
    return ResultadoComando(texto, obj)


# ----------------------------------------------------------------------
# 3.2 SUGERIR
# ----------------------------------------------------------------------
def comando_sugerir(rede, posicionais, opcoes):
    """SUGERIR @usuario k: amigos de amigos, top-k com heap."""
    exigir_posicionais(posicionais, 2, "sugerir @usuario k")
    usuario = obter_usuario(rede, posicionais[0])
    k = ler_inteiro_positivo(posicionais[1], "k")
    resultado = rede.sugerir(usuario, k)
    sugestoes = resultado[0]
    total = resultado[1]

    linhas = ["Sugestoes para " + usuario.usuario + " (k = " + str(k) + ", "
              + str(total) + " candidatos a distancia 2):"]
    if total == 0:
        if rede.quantidade_seguindo(usuario) == 0:
            linhas.append("  Nenhuma sugestao: " + usuario.usuario + " nao segue ninguem.")
        else:
            linhas.append("  Nenhuma sugestao: nao ha amigos de amigos que ele ainda nao siga.")
    else:
        linhas.append("  " + "Pos".ljust(5) + "Usuario".ljust(28) + "Nome".ljust(28) + "Em comum")
        for i in range(len(sugestoes)):
            u = sugestoes[i][0]
            linhas.append("  " + (str(i + 1) + ".").ljust(5) + cortar(u.usuario, 27).ljust(28)
                          + cortar(u.nome, 27).ljust(28) + str(sugestoes[i][1]))
        if k > total:
            linhas.append("  (k maior que o numero de candidatos: mostrando todos os "
                          + str(total) + ")")

    lista_json = []
    for par in sugestoes:
        lista_json.append(ObjetoJSON().adicionar("usuario", par[0].usuario)
                          .adicionar("nome", par[0].nome)
                          .adicionar("conexoes_em_comum", par[1]))
    obj = (ObjetoJSON().adicionar("usuario", usuario.usuario)
           .adicionar("k", k)
           .adicionar("total_candidatos", total)
           .adicionar("sugestoes", lista_json))
    return ResultadoComando("\n".join(linhas), obj)


# ----------------------------------------------------------------------
# 3.3 COMUNIDADES
# ----------------------------------------------------------------------
def comando_comunidades(rede, posicionais, opcoes):
    """COMUNIDADES: componentes conexos via BFS."""
    resultado = rede.comunidades()
    tamanhos = resultado[0]
    isolados = resultado[1]

    linhas = ["Comunidades (componentes conexos com 2 ou mais usuarios): " + str(len(tamanhos)),
              "Usuarios totalmente isolados: " + str(isolados),
              "Total de componentes (contando cada isolado como 1): "
              + str(len(tamanhos) + isolados),
              "Tamanho de cada comunidade, da maior para a menor:"]
    for i in range(len(tamanhos)):
        linhas.append("  Comunidade " + str(i + 1) + ": " + str(tamanhos[i]) + " usuarios")
    if len(tamanhos) == 0:
        linhas.append("  (nenhuma)")

    obj = (ObjetoJSON().adicionar("total_comunidades", len(tamanhos))
           .adicionar("tamanhos", tamanhos)
           .adicionar("isolados", isolados)
           .adicionar("total_componentes", len(tamanhos) + isolados))
    return ResultadoComando("\n".join(linhas), obj)


# ----------------------------------------------------------------------
# 3.4 POSTS_ENTRE
# ----------------------------------------------------------------------
def comando_posts_entre(rede, posicionais, opcoes):
    """POSTS_ENTRE data1 data2 [--limite N]: consulta por intervalo na AVL."""
    exigir_posicionais(posicionais, 2, "posts-entre AAAA-MM-DD AAAA-MM-DD [--limite N]")
    inicio = posicionais[0]
    fim = posicionais[1]
    for data in [inicio, fim]:
        if not data_valida(data):
            raise ErroComando("Data invalida: '" + data + "'. Use o formato AAAA-MM-DD "
                              "(ex.: 2025-03-01).")
    aviso = None
    if inicio > fim:
        aviso = "Datas invertidas: a consulta foi feita de " + fim + " ate " + inicio + "."
        inicio, fim = fim, inicio

    limite_texto = obter_opcao(opcoes, "limite")
    limite = None
    if limite_texto is not None:
        limite = ler_inteiro_positivo(limite_texto, "--limite")

    posts = rede.posts_entre(inicio, fim)
    exibidos = len(posts) if limite is None or limite > len(posts) else limite

    linhas = []
    if aviso is not None:
        linhas.append("Aviso: " + aviso)
    linhas.append("Posts entre " + inicio + " e " + fim + ": " + str(len(posts)) + " encontrados")
    if len(posts) == 0:
        linhas.append("  Nenhum post nesse intervalo.")
    else:
        linhas.append("  " + "Data".ljust(12) + "Id".ljust(7) + "Autor".ljust(26)
                      + "Curtidas".ljust(10) + "Texto")
        for i in range(exibidos):
            p = posts[i]
            linhas.append("  " + p.data.ljust(12) + str(p.id).ljust(7)
                          + cortar(p.autor.usuario, 25).ljust(26)
                          + str(p.curtidas).ljust(10) + p.texto)
        if exibidos < len(posts):
            linhas.append("  ... mostrando " + str(exibidos) + " de " + str(len(posts)) + " posts.")
    linhas.append("Total: " + str(len(posts)) + " posts.")

    lista_json = []
    for i in range(exibidos):
        p = posts[i]
        lista_json.append(ObjetoJSON().adicionar("id", p.id).adicionar("data", p.data)
                          .adicionar("autor", p.autor.usuario).adicionar("curtidas", p.curtidas)
                          .adicionar("texto", p.texto))
    obj = ObjetoJSON().adicionar("inicio", inicio).adicionar("fim", fim)
    if aviso is not None:
        obj.adicionar("aviso", aviso)
    obj.adicionar("total", len(posts)).adicionar("exibidos", exibidos).adicionar("posts", lista_json)
    return ResultadoComando("\n".join(linhas), obj)


# ----------------------------------------------------------------------
# 3.5 TOP_SEGUIDOS / TOP_CURTIDOS
# ----------------------------------------------------------------------
def comando_top_seguidos(rede, posicionais, opcoes):
    """TOP_SEGUIDOS k: usuarios com mais seguidores (heap)."""
    exigir_posicionais(posicionais, 1, "top-seguidos k")
    k = ler_inteiro_positivo(posicionais[0], "k")
    resultado = rede.top_seguidos(k)

    linhas = ["Top " + str(k) + " usuarios com mais seguidores:",
              "  " + "Pos".ljust(5) + "Usuario".ljust(28) + "Nome".ljust(28) + "Seguidores"]
    lista_json = []
    for i in range(len(resultado)):
        u = resultado[i][0]
        linhas.append("  " + (str(i + 1) + ".").ljust(5) + cortar(u.usuario, 27).ljust(28)
                      + cortar(u.nome, 27).ljust(28) + str(resultado[i][1]))
        lista_json.append(ObjetoJSON().adicionar("posicao", i + 1).adicionar("usuario", u.usuario)
                          .adicionar("nome", u.nome).adicionar("seguidores", resultado[i][1]))
    if k > len(resultado):
        linhas.append("  (k maior que o total de usuarios: mostrando todos os "
                      + str(len(resultado)) + ")")
    obj = ObjetoJSON().adicionar("k", k).adicionar("resultado", lista_json)
    return ResultadoComando("\n".join(linhas), obj)


def comando_top_curtidos(rede, posicionais, opcoes):
    """TOP_CURTIDOS k: posts com mais curtidas (heap)."""
    exigir_posicionais(posicionais, 1, "top-curtidos k")
    k = ler_inteiro_positivo(posicionais[0], "k")
    resultado = rede.top_curtidos(k)

    linhas = ["Top " + str(k) + " posts mais curtidos:",
              "  " + "Pos".ljust(5) + "Curtidas".ljust(10) + "Data".ljust(12)
              + "Autor".ljust(26) + "Texto"]
    lista_json = []
    for i in range(len(resultado)):
        p = resultado[i]
        linhas.append("  " + (str(i + 1) + ".").ljust(5) + str(p.curtidas).ljust(10)
                      + p.data.ljust(12) + cortar(p.autor.usuario, 25).ljust(26) + p.texto)
        lista_json.append(ObjetoJSON().adicionar("posicao", i + 1).adicionar("id", p.id)
                          .adicionar("autor", p.autor.usuario).adicionar("data", p.data)
                          .adicionar("curtidas", p.curtidas).adicionar("texto", p.texto))
    if k > len(resultado):
        linhas.append("  (k maior que o total de posts: mostrando todos os "
                      + str(len(resultado)) + ")")
    obj = ObjetoJSON().adicionar("k", k).adicionar("resultado", lista_json)
    return ResultadoComando("\n".join(linhas), obj)


# ----------------------------------------------------------------------
# 3.6 RANKING
# ----------------------------------------------------------------------
def comando_ranking(rede, posicionais, opcoes):
    """
    RANKING [--limite N] [--usuario @x]: ranking por engajamento (Merge Sort).
    Tambem aceita, sem "--", um numero (limite) e/ou um @usuario.
    """
    limite_texto = obter_opcao(opcoes, "limite")
    nome_usuario = obter_opcao(opcoes, "usuario")
    for arg in posicionais:
        if arg.startswith("@"):
            nome_usuario = arg
        else:
            limite_texto = arg
    limite = 20 if limite_texto is None else ler_inteiro_positivo(limite_texto, "limite")

    ranking = rede.ranking()
    exibidos = limite if limite < len(ranking) else len(ranking)

    linhas = ["Ranking de engajamento (seguidores x 2 + curtidas) - " + str(exibidos)
              + " primeiros de " + str(len(ranking)) + " usuarios:",
              "  " + "Pos".ljust(6) + "Usuario".ljust(28) + "Seguidores".ljust(12)
              + "Curtidas".ljust(10) + "Engajamento"]
    lista_json = []
    for i in range(exibidos):
        u = ranking[i][0]
        seguidores = rede.quantidade_seguidores(u)
        linhas.append("  " + (str(i + 1) + ".").ljust(6) + cortar(u.usuario, 27).ljust(28)
                      + str(seguidores).ljust(12) + str(u.total_curtidas).ljust(10)
                      + str(ranking[i][1]))
        lista_json.append(ObjetoJSON().adicionar("posicao", i + 1).adicionar("usuario", u.usuario)
                          .adicionar("nome", u.nome).adicionar("seguidores", seguidores)
                          .adicionar("curtidas", u.total_curtidas)
                          .adicionar("engajamento", ranking[i][1]))

    obj = (ObjetoJSON().adicionar("total_usuarios", len(ranking))
           .adicionar("limite", limite).adicionar("ranking", lista_json))
    if nome_usuario is not None:
        usuario = obter_usuario(rede, nome_usuario)
        posicao = rede.posicao_no_ranking(usuario)
        linhas.append("Posicao de " + usuario.usuario + ": " + str(posicao) + "o de "
                      + str(len(ranking)) + " (engajamento " + str(rede.engajamento(usuario)) + ")")
        obj.adicionar("consulta", ObjetoJSON().adicionar("usuario", usuario.usuario)
                      .adicionar("posicao", posicao)
                      .adicionar("engajamento", rede.engajamento(usuario)))
    return ResultadoComando("\n".join(linhas), obj)


# ----------------------------------------------------------------------
# Tabela de comandos e ajuda
# ----------------------------------------------------------------------
# Cada comando: [nome, funcao, parametros, descricao, exemplo]
COMANDOS = [
    ["buscar", comando_buscar, "@usuario",
     "Dados do usuario (tabela hash)", "buscar @ana_silva"],
    ["sugerir", comando_sugerir, "@usuario k",
     "Ate k sugestoes de quem seguir: amigos de amigos (grafo + heap)", "sugerir @ana_silva 5"],
    ["comunidades", comando_comunidades, "",
     "Comunidades (componentes conexos) e usuarios isolados (BFS)", "comunidades"],
    ["posts-entre", comando_posts_entre, "data1 data2 [--limite N]",
     "Posts entre duas datas AAAA-MM-DD, inclusive (arvore AVL)",
     "posts-entre 2025-03-01 2025-03-31"],
    ["top-seguidos", comando_top_seguidos, "k",
     "Os k usuarios com mais seguidores (heap)", "top-seguidos 10"],
    ["top-curtidos", comando_top_curtidos, "k",
     "Os k posts com mais curtidas (heap)", "top-curtidos 10"],
    ["ranking", comando_ranking, "[--limite N] [--usuario @x]",
     "Ranking de engajamento de todos os usuarios (Merge Sort); padrao: 20 primeiros",
     "ranking --limite 20 --usuario @ana_silva"],
    ["ajuda", None, "", "Mostra esta ajuda", "ajuda"],
]


def normalizar_nome_comando(nome):
    """
    Aceita o comando em qualquer caixa e com "_" ou "-":
    "POSTS_ENTRE", "posts_entre" e "posts-entre" viram "posts-entre".
    """
    return nome.strip().lower().replace("_", "-")


def encontrar_comando(nome):
    """Procura o comando na tabela (busca linear em 8 itens). Retorna a linha ou None."""
    nome = normalizar_nome_comando(nome)
    for comando in COMANDOS:
        if comando[0] == nome:
            return comando
    return None


def texto_ajuda(prefixo):
    """
    Monta o texto de ajuda com todos os comandos, parametros e exemplos.

    Parametros:
        prefixo (str): o que vem antes do comando no exemplo
            (ex.: "python3 py/main.py " na API, "" no modo interativo).
    """
    linhas = ["Comandos disponiveis:", ""]
    for comando in COMANDOS:
        assinatura = comando[0] + (" " + comando[2] if comando[2] else "")
        linhas.append("  " + assinatura)
        linhas.append("      " + comando[3])
        linhas.append("      Exemplo: " + prefixo + comando[4])
    linhas.append("")
    linhas.append("Opcao geral: --json troca a saida legivel por JSON valido.")
    linhas.append("  Exemplo: " + prefixo + "top-seguidos 3 --json")
    return "\n".join(linhas)


def executar(rede, nome_comando, argumentos):
    """
    Executa um comando e devolve [ResultadoComando, usar_json].

    Lanca:
        ErroComando se o comando nao existir ou os parametros forem invalidos.
    """
    separados = separar_argumentos(argumentos)
    comando = encontrar_comando(nome_comando)
    if comando is None or comando[1] is None:
        raise ErroComando("Comando invalido: '" + nome_comando + "'.")
    resultado = comando[1](rede, separados[0], separados[1])
    return [resultado, separados[2]]
