"""
Atividade Final - AED II - Rede Social

Ponto de entrada do programa. Dois modos de uso:

  1. API de linha de comando (bonus 3.7): uma consulta por chamada.
       python3 py/main.py buscar @ana_silva
       python3 py/main.py top-seguidos 3 --json
       python3 py/main.py ajuda

  2. Modo interativo: sem argumentos, abre um prompt onde os comandos
     sao digitados um por vez (BUSCAR @usuario, SUGERIR @usuario k, ...).
       python3 py/main.py

Organizacao do codigo (pasta py/):
  tabela_hash.py  - TabelaHash (encadeamento)         -> BUSCAR
  heap.py         - HeapBinaria e top_k               -> SUGERIR, TOP_*
  arvore_avl.py   - ArvoreAVL com rotacoes            -> POSTS_ENTRE
  grafo.py        - Grafo (listas de adjacencia), BFS -> SUGERIR, COMUNIDADES
  ordenacao.py    - merge_sort                        -> RANKING
  rede_social.py  - monta as estruturas e faz as consultas (sem print)
  comandos.py     - valida parametros e formata texto/JSON
  saida_json.py   - gerador de JSON proprio
  main.py         - este arquivo: escolhe o modo e trata codigos de saida
"""

import sys

import aedlib  # biblioteca base do projeto (obrigatória - não remova)
from rede_social import RedeSocial
from comandos import ErroComando, executar, texto_ajuda
from saida_json import ObjetoJSON, para_json


PREFIXO_API = "python3 py/main.py "


def carregar_rede():
    """
    Le os tres arquivos com a aedlib e monta todas as estruturas.

    Retorno:
        list: [rede, quantidade_usuarios, quantidade_conexoes, quantidade_posts]
            (as quantidades sao as linhas lidas dos arquivos).
    """
    usuarios, seguidores, posts = aedlib.social_carregar_dados()
    # usuarios: [id, usuario, nome, data_cadastro]
    # seguidores: [seguidor, seguido]
    # posts: [id, autor, data, curtidas, texto]
    rede = RedeSocial(usuarios, seguidores, posts)
    return [rede, len(usuarios), len(seguidores), len(posts)]


def modo_api(argumentos):
    """
    Executa UMA consulta a partir de sys.argv e devolve o codigo de saida:
    0 em caso de sucesso, 1 em caso de erro (parametro invalido, usuario
    inexistente, comando desconhecido...).

    - "ajuda" mostra a ajuda e devolve 0.
    - Comando invalido mostra a mensagem de erro + ajuda e devolve 1.
    - Com --json, sucesso e erro sao impressos como JSON valido
      (o erro vira {"erro": "mensagem"}).
    """
    usar_json = "--json" in argumentos
    nome = argumentos[0]

    if nome.lower() in ["ajuda", "--ajuda", "-h", "--help", "help"]:
        print(texto_ajuda(PREFIXO_API))
        return 0

    rede = carregar_rede()[0]
    try:
        resultado = executar(rede, nome, argumentos[1:])[0]
    except ErroComando as erro:
        mensagem = str(erro)
        if usar_json:
            print(para_json(ObjetoJSON().adicionar("erro", mensagem)))
        else:
            print("Erro: " + mensagem, file=sys.stderr)
            if mensagem.startswith("Comando invalido"):
                print("", file=sys.stderr)
                print(texto_ajuda(PREFIXO_API), file=sys.stderr)
        return 1

    if usar_json:
        print(para_json(resultado.json))
    else:
        print(resultado.texto)
    return 0


def modo_interativo():
    """
    Laco de comandos: le uma linha, executa e mostra o resultado.
    Erros apenas mostram a mensagem; "sair" (ou Ctrl+D) encerra.
    """
    dados = carregar_rede()
    rede = dados[0]
    print(f"Usuários carregados: {dados[1]}")
    print(f"Conexões carregadas: {dados[2]}")
    print(f"Posts carregados: {dados[3]}")
    print()
    print(texto_ajuda(""))
    print("  sair")
    print("      Encerra o programa")

    while True:
        try:
            linha = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if linha == "":
            continue
        partes = linha.split()
        nome = partes[0].lower()
        if nome in ["sair", "exit", "quit"]:
            break
        if nome == "ajuda":
            print(texto_ajuda(""))
            continue
        try:
            resultado_e_json = executar(rede, partes[0], partes[1:])
        except ErroComando as erro:
            print("Erro: " + str(erro))
            if str(erro).startswith("Comando invalido"):
                print("Digite 'ajuda' para ver os comandos.")
            continue
        resultado = resultado_e_json[0]
        if resultado_e_json[1]:
            print(para_json(resultado.json))
        else:
            print(resultado.texto)


def main():
    """Escolhe o modo: com argumentos -> API; sem argumentos -> interativo."""
    if len(sys.argv) > 1:
        sys.exit(modo_api(sys.argv[1:]))
    modo_interativo()


if __name__ == "__main__":
    main()
