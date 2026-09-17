# Nomes dos integrantes do grupo:
# 1. Carolina Britto Haddad
# 2. Gabriel Agra de Castro Motta
# 3. Mateus Silva Araújo

from datetime import datetime

###listas
filmes = []
salas = []
sessoes = []

###dictionary
tipo_sala = {}


class Filme:
    def __init__(self, nome=None, data_estreia=None, data_saida=None, duracao=None, codigo=None):
        self.codigo = codigo
        self.nome = nome
        self.data_estreia = data_estreia
        self.data_saida = data_saida
        self.duracao = duracao


class Sala:
    def __init__(self, numero=None, capacidade=None, tipo=None):
        self.numero = numero
        self.capacidade = capacidade
        self.tipo = tipo


class Sessao:
    def __init__(self, sala=None, filme=None, data=None, hora_inicio=None, codigo=None):
        self.codigo = codigo
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio
        self.assentos = {}


#metodos
def _validar_data(data_str):
    if not isinstance(data_str, str):
        return None
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def pegar_sala(numero):
    for s in salas:
        if s.numero == numero or str(s.numero) == str(numero):
            return s
    return None


def pegar_filme(codigo):
    for f in filmes:
        if f.codigo == codigo or str(f.codigo) == str(codigo):
            return f
    return None


def pegar_sessao(codigo):
    for s in sessoes:
        if s.codigo == codigo or str(s.codigo) == str(codigo):
            return s
    return None


def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    if not isinstance(nome, str) or not nome.strip():
        return None
    if not isinstance(duracao, int) or duracao <= 0:
        return None

    dt_estreia = _validar_data(data_estreia)
    dt_saida = _validar_data(data_saida)
    if dt_estreia is None or dt_saida is None:
        return None
    if dt_saida < dt_estreia:
        return None

    for f in filmes:
        if f.nome == nome:
            return None

    codigo = len(filmes) + 1
    filme = Filme(
        nome=nome,
        data_estreia=data_estreia,
        data_saida=data_saida,
        duracao=duracao,
        codigo=codigo,
    )
    filmes.append(filme)
    return filme


def cadastrar_valor_ingresso(tipo_sala, valor_ingresso):
    if not isinstance(tipo_sala, str) or tipo_sala not in ("2D", "3D"):
        return False
    if type(valor_ingresso) is not int or valor_ingresso <= 0:
        return False
    globals()["tipo_sala"][tipo_sala] = valor_ingresso
    return True


def cadastrar_sala(numero, capacidade, tipo_sala):
    if type(numero) is not int or numero <= 0:
        return None
    if type(capacidade) is not int or capacidade <= 0:
        return None
    if not isinstance(tipo_sala, str) or tipo_sala not in ("2D", "3D"):
        return None

    for s in salas:
        if s.numero == numero:
            return None

    sala = Sala(numero=numero, capacidade=capacidade, tipo=tipo_sala)
    salas.append(sala)
    return sala


def cadastrar_sessao(numero_sala, codigo_filme, data_sessao, hora_inicio):
    hora_minima = 0
    hora_maxima = 23
    dt_sessao = _validar_data(data_sessao)
    if (
        type(numero_sala) is not int
        or type(codigo_filme) is not int
        or type(hora_inicio) is not int
        or not (hora_minima <= hora_inicio <= hora_maxima)
        or dt_sessao is None
    ):
        return None

    sala = pegar_sala(numero_sala)
    filme = pegar_filme(codigo_filme)
    if sala is None or filme is None:
        return None

    conflito = any(
        s.sala.numero == numero_sala and s.data == data_sessao and s.hora_inicio == hora_inicio
        for s in sessoes
    )
    if conflito:
        return None

    codigo = len(sessoes) + 1
    sessao = Sessao(
        sala=sala,
        filme=filme,
        data=data_sessao,
        hora_inicio=hora_inicio,
        codigo=codigo,
    )
    sessao.assentos = dict.fromkeys(range(1, sala.capacidade + 1), 0)
    sessoes.append(sessao)
    return sessao


def listar_filmes_por_data(data):
    if _validar_data(data) is None:
        return "Data invalida."

    linhas = []
    for sessao in sessoes:
        if sessao.data == data:
            tem_assentos_disponiveis = any(status == 0 for status in sessao.assentos.values())
            if tem_assentos_disponiveis:
                valor = tipo_sala.get(sessao.sala.tipo, 0)
                linha = (
                    f"{sessao.codigo}: {sessao.filme.nome}, "
                    f"sala {sessao.sala.numero} ({sessao.sala.tipo}), "
                    f"{sessao.hora_inicio}h, {valor} reais."
                )
                linhas.append(linha)

    if not linhas:
        return "Nenhum filme no dia escolhido."

    return "\n".join(linhas)


def comprarIngressos(codigo_sessao, assentos, tipos_ingresso):  # noqa: N802
    if (
        not isinstance(assentos, list)
        or not isinstance(tipos_ingresso, list)
        or not assentos
        or len(assentos) != len(tipos_ingresso)
        or len(assentos) != len(set(assentos))
    ):
        return 0

    sessao = pegar_sessao(codigo_sessao)
    if sessao is None:
        return 0

    for assento, tipo_ing in zip(assentos, tipos_ingresso, strict=True):
        if assento not in sessao.assentos or sessao.assentos[assento] != 0 or tipo_ing not in (0, 1):
            return 0

    preco_sala = tipo_sala.get(sessao.sala.tipo, 0)
    for assento in assentos:
        sessao.assentos[assento] = 1

    total = sum(preco_sala if tipo == 0 else preco_sala / 2 for tipo in tipos_ingresso)
    return int(total) if total == int(total) else total