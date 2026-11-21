"""
Gerador de JSON proprio para a opcao --json da API.

Como "dict" e proibido no trabalho, os objetos JSON sao representados
pela classe ObjetoJSON, que guarda uma lista ordenada de pares
[chave, valor]. A funcao para_json converte recursivamente para texto.
"""


class ObjetoJSON:
    """
    Objeto JSON ({...}) representado como lista de pares [chave, valor],
    mantendo a ordem em que os campos foram adicionados.
    """

    def __init__(self):
        self.campos = []

    def adicionar(self, chave, valor):
        """
        Adiciona um campo e devolve o proprio objeto (permite encadear:
        ObjetoJSON().adicionar("a", 1).adicionar("b", 2)).
        """
        self.campos.append([chave, valor])
        return self


def _escapar_texto(texto):
    """
    Converte uma string Python em string JSON entre aspas, escapando
    aspas, barra invertida e caracteres de controle (ex.: quebra de linha).
    Acentos sao mantidos (JSON aceita UTF-8).
    """
    partes = ['"']
    for c in texto:
        if c == '"':
            partes.append('\\"')
        elif c == "\\":
            partes.append("\\\\")
        elif c == "\n":
            partes.append("\\n")
        elif c == "\r":
            partes.append("\\r")
        elif c == "\t":
            partes.append("\\t")
        elif ord(c) < 32:
            partes.append("\\u%04x" % ord(c))
        else:
            partes.append(c)
    partes.append('"')
    return "".join(partes)


def para_json(valor, nivel=0):
    """
    Serializa um valor como texto JSON indentado (2 espacos).

    Tipos aceitos: None, bool, int, float, str, list e ObjetoJSON.

    Parametros:
        valor: valor a serializar.
        nivel (int): profundidade atual (usada na indentacao).
    Retorno:
        str: texto JSON valido.
    Complexidade: O(tamanho da saida).
    """
    recuo = "  " * (nivel + 1)
    recuo_fim = "  " * nivel
    if valor is None:
        return "null"
    if valor is True:
        return "true"
    if valor is False:
        return "false"
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, float):
        return repr(round(valor, 6))
    if isinstance(valor, str):
        return _escapar_texto(valor)
    if isinstance(valor, list):
        if len(valor) == 0:
            return "[]"
        itens = []
        for item in valor:
            itens.append(recuo + para_json(item, nivel + 1))
        return "[\n" + ",\n".join(itens) + "\n" + recuo_fim + "]"
    if isinstance(valor, ObjetoJSON):
        if len(valor.campos) == 0:
            return "{}"
        itens = []
        for par in valor.campos:
            itens.append(recuo + _escapar_texto(par[0]) + ": " + para_json(par[1], nivel + 1))
        return "{\n" + ",\n".join(itens) + "\n" + recuo_fim + "}"
    raise TypeError("Tipo nao suportado em JSON: " + type(valor).__name__)
