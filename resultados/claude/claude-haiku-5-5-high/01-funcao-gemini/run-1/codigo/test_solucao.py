import unittest

from solucao import resumir_intervalos


class TestResumirIntervalos(unittest.TestCase):
    def test_exemplos(self):
        self.assertEqual(resumir_intervalos([1, 2, 3, 5, 7, 8, 9]), "1-3, 5, 7-9")
        self.assertEqual(resumir_intervalos([9, 1, 8, 2, 7, 3, 5]), "1-3, 5, 7-9")
        self.assertEqual(resumir_intervalos([1, 1, 2, 2, 3]), "1-3")
        self.assertEqual(resumir_intervalos([42]), "42")
        self.assertEqual(resumir_intervalos([]), "")
        self.assertEqual(resumir_intervalos([-3, -2, -1, 1, 2]), "-3--1, 1-2")

    def test_dois_consecutivos_formam_intervalo(self):
        self.assertEqual(resumir_intervalos([7, 8]), "7-8")

    def test_nao_modifica_lista_original(self):
        entrada = [3, 1, 2, 2]
        resumir_intervalos(entrada)
        self.assertEqual(entrada, [3, 1, 2, 2])

    def test_grandes_magnitudes(self):
        n = 10**30
        self.assertEqual(resumir_intervalos([n + 1, n, -n, -n - 1]), f"{-n - 1}-{-n}, {n}-{n + 1}")

    def test_grande_volume(self):
        dados = list(range(200_000, 0, -1)) + [300_000]
        self.assertEqual(resumir_intervalos(dados), "1-200000, 300000")

    def test_tipo_nao_lista(self):
        for valor in [(1, 2), "1,2", None, {1: 2}]:
            with self.subTest(valor=valor):
                with self.assertRaises(TypeError):
                    resumir_intervalos(valor)

    def test_elementos_nao_int_primitivos(self):
        for lista in [[True], [1, False], [1.0], ["1"], [None]]:
            with self.subTest(lista=lista):
                with self.assertRaises(TypeError):
                    resumir_intervalos(lista)


if __name__ == "__main__":
    unittest.main()
