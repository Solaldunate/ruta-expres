import csv
import math
import re
from datetime import date
from pathlib import Path

DATOS = Path(__file__).resolve().parent / "datos"
CAMPOS = "pedido_id fecha_lote lote zona distancia_km entrega_min importe_bs".split()
NUMERICAS = CAMPOS[4:]


def leer(ruta, permitidos):
    filas, ids = [], set()
    try:
        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.reader(archivo, strict=True)
            if next(lector, None) != CAMPOS:
                raise ValueError(f"{ruta}: se esperaban los siete encabezados en orden")
            for valores in lector:
                numero = lector.line_num

                def error(columna, causa):
                    raise ValueError(f"{ruta}: fila {numero}, {columna}: {causa}")

                if len(valores) != len(CAMPOS):
                    error("columnas", "se esperaban siete valores")
                fila = dict(zip(CAMPOS, valores))
                pedido = fila["pedido_id"].strip()
                if not pedido or pedido in ids:
                    error("pedido_id", "identificador vacío o repetido")
                ids.add(pedido)
                fecha = fila["fecha_lote"]
                try:
                    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", fecha):
                        raise ValueError
                    date.fromisoformat(fecha)
                except ValueError:
                    error("fecha_lote", "fecha inválida; usa AAAA-MM-DD")
                if fila["zona"] not in {"centro", "periferia"}:
                    error("zona", "debe ser centro o periferia")
                if fila["lote"] not in permitidos:
                    error("lote", f"se esperaba uno de: {', '.join(sorted(permitidos))}")
                for columna in ("lote", "fecha_lote"):
                    if filas and fila[columna] != filas[0][columna]:
                        error(columna, "el archivo debe tener un solo valor")
                for columna in NUMERICAS:
                    try:
                        valor = float(fila[columna])
                    except ValueError:
                        error(columna, "se esperaba un número")
                    if not math.isfinite(valor) or valor <= 0:
                        error(columna, "debe ser un número finito mayor que cero")
                filas.append(fila)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError(f"{ruta}: no se pudo leer el CSV: {exc}") from exc
    if not filas:
        raise ValueError(f"{ruta}: no contiene pedidos")
    return filas


def validar():
    return leer(DATOS / "referencia.csv", {"base"}), leer(DATOS / "actual.csv", {"control", "expansion"})


if __name__ == "__main__":
    try:
        referencia, actual = validar()
    except ValueError as exc:
        raise SystemExit(str(exc))
    print(f"Validación correcta: {len(referencia)} de referencia y {len(actual)} actuales.")
