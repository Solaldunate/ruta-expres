import argparse
import csv
import shutil
from validar import CAMPOS, DATOS, leer

parser = argparse.ArgumentParser(description="Cambia únicamente datos/actual.csv")
parser.add_argument("escenario", choices=["control", "expansion", "error", "recuperacion"])
opcion = parser.parse_args().escenario
destino = DATOS / "actual.csv"
origen = DATOS / ("control.csv" if opcion == "control" else "expansion.csv")
if opcion != "error":
    shutil.copyfile(origen, destino)
else:
    filas = leer(origen, {"expansion"})
    primera = filas[0]
    print(f'{primera["pedido_id"]}: entrega_min original = {primera["entrega_min"]}; nuevo = -1')
    primera["entrega_min"] = "-1"
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)
print(f"Escenario preparado: {opcion}")
