import unittest

import cinema
from cinema import (
    cadastrar_filme,
    cadastrar_sala,
    cadastrar_sessao,
    cadastrar_valor_ingresso,
    comprarIngressos,
    listar_filmes_por_data,
)


def reiniciar_estado():
    cinema.filmes.clear()
    cinema.salas.clear()
    cinema.sessoes.clear()
    cinema.tipo_sala.clear()


class TestUS01CadastrarFilme(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()

    def test_cadastrar_filme_sucesso(self):
        filme = cadastrar_filme("Matrix", "21/05/1999", "21/08/1999", 136)
        self.assertIsNotNone(filme)
        self.assertEqual(filme.codigo, 1)
        self.assertEqual(filme.nome, "Matrix")
        self.assertEqual(filme.data_estreia, "21/05/1999")
        self.assertEqual(filme.data_saida, "21/08/1999")
        self.assertEqual(filme.duracao, 136)
        self.assertIn(filme, cinema.filmes)

    def test_cadastrar_multiplos_filmes_codigos_sequenciais(self):
        f1 = cadastrar_filme("Filme 1", "01/01/2026", "10/01/2026", 100)
        f2 = cadastrar_filme("Filme 2", "05/01/2026", "15/01/2026", 120)
        self.assertIsNotNone(f1)
        self.assertIsNotNone(f2)
        self.assertEqual(f1.codigo, 1)
        self.assertEqual(f2.codigo, 2)

    def test_cadastrar_filme_data_invalida(self):
        filme = cadastrar_filme("Matrix", "32/01/2026", "10/02/2026", 120)
        self.assertIsNone(filme)
        filme2 = cadastrar_filme("Matrix", "data_errada", "10/02/2026", 120)
        self.assertIsNone(filme2)

    def test_cadastrar_filme_saida_anterior_a_estreia(self):
        filme = cadastrar_filme("Matrix", "20/05/2026", "10/05/2026", 120)
        self.assertIsNone(filme)

    def test_cadastrar_filme_duracao_invalida(self):
        filme_zero = cadastrar_filme("Matrix", "01/01/2026", "10/01/2026", 0)
        self.assertIsNone(filme_zero)
        filme_neg = cadastrar_filme("Matrix", "01/01/2026", "10/01/2026", -90)
        self.assertIsNone(filme_neg)

    def test_cadastrar_filme_nome_invalido(self):
        filme = cadastrar_filme("", "01/01/2026", "10/01/2026", 100)
        self.assertIsNone(filme)
        filme_spaces = cadastrar_filme("   ", "01/01/2026", "10/01/2026", 100)
        self.assertIsNone(filme_spaces)

    def test_cadastrar_filme_nome_repetido(self):
        f1 = cadastrar_filme("Carros", "01/01/2010", "01/03/2010", 115)
        self.assertIsNotNone(f1)
        f2 = cadastrar_filme("Carros", "01/01/2010", "01/03/2010", 115)
        self.assertIsNone(f2)


class TestUS02CadastrarValorIngresso(unittest.TestCase):

    def setUp(self):
        reiniciar_estado()

    def test_cadastrar_valor_ingresso_2d_sucesso(self):
        resultado = cadastrar_valor_ingresso("2D", 30)
        self.assertTrue(resultado)
        self.assertEqual(cinema.tipo_sala["2D"], 30)

    def test_cadastrar_valor_ingresso_3d_sucesso(self):
        resultado = cadastrar_valor_ingresso("3D", 45)
        self.assertTrue(resultado)
        self.assertEqual(cinema.tipo_sala["3D"], 45)

    def test_cadastrar_valor_ingresso_tipo_invalido(self):
        self.assertFalse(cadastrar_valor_ingresso("4D", 50))
        self.assertFalse(cadastrar_valor_ingresso("IMAX", 60))
        self.assertFalse(cadastrar_valor_ingresso("", 30))
        self.assertFalse(cadastrar_valor_ingresso(None, 30))

    def test_cadastrar_valor_ingresso_valor_menor_ou_igual_a_zero(self):
        self.assertFalse(cadastrar_valor_ingresso("2D", 0))
        self.assertFalse(cadastrar_valor_ingresso("2D", -20))

    def test_cadastrar_valor_ingresso_valor_nao_inteiro(self):
        self.assertFalse(cadastrar_valor_ingresso("2D", 35.5))
        self.assertFalse(cadastrar_valor_ingresso("2D", "30"))


class TestUS03CadastrarSala(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()

    def test_cadastrar_sala_sucesso(self):
        sala = cadastrar_sala(1, 50, "2D")
        self.assertIsNotNone(sala)
        self.assertEqual(sala.numero, 1)
        self.assertEqual(sala.capacidade, 50)
        self.assertEqual(sala.tipo, "2D")
        self.assertIn(sala, cinema.salas)

    def test_cadastrar_sala_numero_repetido(self):
        s1 = cadastrar_sala(1, 50, "2D")
        self.assertIsNotNone(s1)
        s2 = cadastrar_sala(1, 60, "3D")
        self.assertIsNone(s2)
        self.assertEqual(len(cinema.salas), 1)

    def test_cadastrar_sala_numero_invalido(self):
        self.assertIsNone(cadastrar_sala(0, 50, "2D"))
        self.assertIsNone(cadastrar_sala(-1, 50, "2D"))

    def test_cadastrar_sala_capacidade_invalida(self):
        self.assertIsNone(cadastrar_sala(2, 0, "2D"))
        self.assertIsNone(cadastrar_sala(2, -10, "2D"))

    def test_cadastrar_sala_tipo_invalido(self):
        self.assertIsNone(cadastrar_sala(3, 50, "4D"))
        self.assertIsNone(cadastrar_sala(3, 50, ""))
        self.assertIsNone(cadastrar_sala(3, 50, None))


class TestUS04CadastrarSessao(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()
        self.sala = cadastrar_sala(1, 10, "2D")
        self.filme = cadastrar_filme("Inception", "01/06/2026", "30/06/2026", 148)

    def test_cadastrar_sessao_sucesso(self):
        sessao = cadastrar_sessao(1, 1, "15/06/2026", 20)
        self.assertIsNotNone(sessao)
        self.assertEqual(sessao.codigo, 1)
        self.assertEqual(sessao.sala, self.sala)
        self.assertEqual(sessao.filme, self.filme)
        self.assertEqual(sessao.data, "15/06/2026")
        self.assertEqual(sessao.hora_inicio, 20)
        self.assertEqual(len(sessao.assentos), 10)
        for num_assento in range(1, 11):
            self.assertEqual(sessao.assentos[num_assento], 0)
        self.assertIn(sessao, cinema.sessoes)

    def test_cadastrar_multiplas_sessoes_codigos_sequenciais(self):
        s1 = cadastrar_sessao(1, 1, "15/06/2026", 14)
        s2 = cadastrar_sessao(1, 1, "15/06/2026", 18)
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)
        self.assertEqual(s1.codigo, 1)
        self.assertEqual(s2.codigo, 2)

    def test_cadastrar_sessao_sala_inexistente(self):
        sessao = cadastrar_sessao(99, 1, "15/06/2026", 20)
        self.assertIsNone(sessao)

    def test_cadastrar_sessao_filme_inexistente(self):
        sessao = cadastrar_sessao(1, 99, "15/06/2026", 20)
        self.assertIsNone(sessao)

    def test_cadastrar_sessao_conflito_horario_mesma_sala(self):
        s1 = cadastrar_sessao(1, 1, "15/06/2026", 20)
        self.assertIsNotNone(s1)
        s2 = cadastrar_sessao(1, 1, "15/06/2026", 20)
        self.assertIsNone(s2)

    def test_cadastrar_sessao_mesmo_horario_salas_diferentes(self):
        cadastrar_sala(2, 20, "3D")
        s1 = cadastrar_sessao(1, 1, "15/06/2026", 20)
        s2 = cadastrar_sessao(2, 1, "15/06/2026", 20)
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)

    def test_cadastrar_sessao_hora_invalida(self):
        self.assertIsNone(cadastrar_sessao(1, 1, "15/06/2026", -1))
        self.assertIsNone(cadastrar_sessao(1, 1, "15/06/2026", 24))
        self.assertIsNone(cadastrar_sessao(1, 1, "15/06/2026", "20"))

    def test_cadastrar_sessao_assentos_quantidade(self):
        sessao = cadastrar_sessao(1, 1, "15/06/2026", 20)
        self.assertIsNotNone(sessao)
        self.assertEqual(cinema.pegar_sala(1).capacidade, len(sessao.assentos))

    def test_cadastrar_sessao_data_invalida(self):
        self.assertIsNone(cadastrar_sessao(1, 1, "32/06/2026", 20))
        self.assertIsNone(cadastrar_sessao(1, 1, "data_invalida", 20))


class TestUS05ListarFilmesPorData(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()
        cadastrar_valor_ingresso("2D", 40)
        cadastrar_valor_ingresso("3D", 50)
        self.sala1 = cadastrar_sala(1, 2, "3D")
        self.sala2 = cadastrar_sala(2, 5, "2D")
        self.filme1 = cadastrar_filme("King Kong", "01/06/2026", "30/06/2026", 120)
        self.filme2 = cadastrar_filme("Star Wars", "01/06/2026", "30/06/2026", 140)

    def test_listar_filmes_por_data_sucesso_uma_sessao(self):
        cadastrar_sessao(1, 1, "15/06/2026", 12)
        esperado = "1: King Kong, sala 1 (3D), 12h, 50 reais."
        self.assertEqual(listar_filmes_por_data("15/06/2026"), esperado)

    def test_listar_filmes_por_data_multiplas_sessoes(self):
        cadastrar_sessao(1, 1, "15/06/2026", 12)
        cadastrar_sessao(2, 2, "15/06/2026", 13)
        resultado = listar_filmes_por_data("15/06/2026")
        esperado = (
            "1: King Kong, sala 1 (3D), 12h, 50 reais.\n"
            "2: Star Wars, sala 2 (2D), 13h, 40 reais."
        )
        self.assertEqual(resultado, esperado)

    def test_listar_filmes_por_data_sessao_sem_assentos_disponiveis(self):
        sessao = cadastrar_sessao(1, 1, "15/06/2026", 12)
        # Ocupa todos os assentos (capacidade = 2)
        sessao.assentos[1] = 1
        sessao.assentos[2] = 1
        resultado = listar_filmes_por_data("15/06/2026")
        self.assertEqual(resultado, "Nenhum filme no dia escolhido.")

    def test_listar_filmes_por_data_dia_sem_sessoes(self):
        cadastrar_sessao(1, 1, "15/06/2026", 12)
        resultado = listar_filmes_por_data("20/06/2026")
        self.assertEqual(resultado, "Nenhum filme no dia escolhido.")

    def test_listar_filmes_por_data_data_invalida(self):
        self.assertEqual(listar_filmes_por_data("32/06/2026"), "Data invalida.")
        self.assertEqual(listar_filmes_por_data("data_errada"), "Data invalida.")
        self.assertEqual(listar_filmes_por_data(None), "Data invalida.")


class TestUS06ComprarIngressos(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()
        cadastrar_valor_ingresso("2D", 40)
        self.sala = cadastrar_sala(1, 5, "2D")
        self.filme = cadastrar_filme("Interestelar", "01/06/2026", "30/06/2026", 169)
        self.sessao = cadastrar_sessao(1, 1, "15/06/2026", 19)

    def test_comprar_ingressos_sucesso_inteira(self):
        total = comprarIngressos(1, [1], [0])
        self.assertEqual(total, 40)
        self.assertEqual(self.sessao.assentos[1], 1)

    def test_comprar_ingressos_sucesso_meia(self):
        total = comprarIngressos(1, [2], [1])
        self.assertEqual(total, 20)
        self.assertEqual(self.sessao.assentos[2], 1)

    def test_comprar_ingressos_sucesso_multiplos_misto(self):
        total = comprarIngressos(1, [1, 2], [0, 1])
        self.assertEqual(total, 60)
        self.assertEqual(self.sessao.assentos[1], 1)
        self.assertEqual(self.sessao.assentos[2], 1)

    def test_comprar_ingressos_sessao_inexistente(self):
        total = comprarIngressos(99, [1], [0])
        self.assertEqual(total, 0)
        self.assertEqual(self.sessao.assentos[1], 0)

    def test_comprar_ingressos_assento_ja_ocupado_atomicidade(self):
        self.sessao.assentos[1] = 1

        total = comprarIngressos(1, [1, 2], [0, 0])
        self.assertEqual(total, 0)
        self.assertEqual(self.sessao.assentos[1], 1)
        self.assertEqual(self.sessao.assentos[2], 0)

    def test_comprar_ingressos_assento_inexistente(self):
        total = comprarIngressos(1, [99], [0])
        self.assertEqual(total, 0)

        total_zero = comprarIngressos(1, [0], [0])
        self.assertEqual(total_zero, 0)

    def test_comprar_ingressos_assentos_duplicados(self):
        total = comprarIngressos(1, [1, 1], [0, 0])
        self.assertEqual(total, 0)
        self.assertEqual(self.sessao.assentos[1], 0)

    def test_comprar_ingressos_tamanhos_diferentes(self):
        total = comprarIngressos(1, [1, 2], [0])
        self.assertEqual(total, 0)
        self.assertEqual(self.sessao.assentos[1], 0)
        self.assertEqual(self.sessao.assentos[2], 0)

    def test_comprar_ingressos_lista_vazia(self):
        total = comprarIngressos(1, [], [])
        self.assertEqual(total, 0)

    def test_comprar_ingressos_tipo_invalido(self):
        total = comprarIngressos(1, [1], [2])
        self.assertEqual(total, 0)
        self.assertEqual(self.sessao.assentos[1], 0)