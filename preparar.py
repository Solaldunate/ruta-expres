import csv
import shutil
from collections import Counter
from validar import CAMPOS, DATOS, leer


def main():
    with (DATOS / "pedidos_ruta_express.csv").open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != CAMPOS:
            raise SystemExit("Encabezados incorrectos en el original.")
        filas = list(lector)
    lotes = {"base": "referencia", "control": "control", "expansion": "expansion"}
    if Counter(f["lote"] for f in filas) != {lote: 120 for lote in lotes}:
        raise SystemExit("Se esperaban 120 pedidos por lote.")
    if len({f["pedido_id"].strip() for f in filas}) != len(filas):
        raise SystemExit("Hay identificadores repetidos.")
    for lote, nombre in lotes.items():
        ruta = DATOS / f"{nombre}.csv"
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(f for f in filas if f["lote"] == lote)
        leer(ruta, {lote})
    shutil.copyfile(DATOS / "control.csv", DATOS / "actual.csv")


if __name__ == "__main__":
    main()
