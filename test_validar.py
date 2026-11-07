import csv
import tempfile
import unittest
from pathlib import Path
from validar import CAMPOS, leer


class PruebasValidador(unittest.TestCase):
    def comprobar(self, filas):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "prueba.csv"
            with ruta.open("w", encoding="utf-8", newline="") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(CAMPOS)
                escritor.writerows(filas)
            return leer(ruta, {"control"})

    def setUp(self):
        self.fila = ["P1", "2026-10-01", "control", "centro", "2", "25", "80"]

    def test_valido(self):
        self.assertEqual(self.comprobar([self.fila])[0]["pedido_id"], "P1")

    def test_id_duplicado(self):
        with self.assertRaisesRegex(ValueError, r"fila 3, pedido_id"):
            self.comprobar([self.fila, self.fila])

    def test_fecha_imposible(self):
        self.fila[1] = "2026-02-30"
        with self.assertRaisesRegex(ValueError, r"fila 2, fecha_lote"):
            self.comprobar([self.fila])

    def test_entrega_negativa(self):
        self.fila[5] = "-1"
        with self.assertRaisesRegex(ValueError, r"fila 2, entrega_min"):
            self.comprobar([self.fila])
