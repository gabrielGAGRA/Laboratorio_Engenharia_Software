class Sessao:
    def __init__(self, sala=None, filme=None, data=None, hora_inicio=None, codigo=None):
        self.codigo = codigo
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio
        self.assentos = {}
