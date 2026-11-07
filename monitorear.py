import os
from collections import Counter
from html import escape
from validar import DATOS, NUMERICAS, validar


def tabla_fila(nombre, filas):
    zonas = Counter(fila["zona"] for fila in filas)
    valores = [nombre, filas[0]["lote"], filas[0]["fecha_lote"],
               len(filas), zonas["centro"], zonas["periferia"]]
    return "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in valores) + "</tr>"


def main():
    try:
        referencia, actual = validar()
    except ValueError as exc:
        raise SystemExit(str(exc))

    os.environ.setdefault("EVIDENTLY_DO_NOT_TRACK", "1")
    import pandas as pd
    from evidently import DataDefinition, Dataset, Report
    from evidently.presets import DataDriftPreset

    def dataset(filas):
        tabla = pd.DataFrame(filas)[NUMERICAS].astype(float)
        return Dataset.from_pandas(tabla, data_definition=DataDefinition(numerical_columns=NUMERICAS))

    reporte = Report([DataDriftPreset(method="ks", threshold=0.05, drift_share=0.5)])
    resultado = reporte.run(dataset(actual), dataset(referencia))
    salida = DATOS.parent / "public"
    salida.mkdir(exist_ok=True)
    resultado.save_html(str(salida / "comparacion.html"))
    commit = escape(os.getenv("GITHUB_SHA", "Ejecución local"))
    portada = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ruta Exprés | Monitoreo</title>
<style>
body {{ font: 1rem system-ui; background: #f2f6f8; color: #162b38; margin: 0; }}
main {{ max-width: 54rem; margin: 4rem auto; padding: 2rem; background: white; border-radius: 1rem; }}
table {{ width: 100%; border-collapse: collapse; text-align: left; }}
th, td {{ padding: .75rem; border-bottom: 1px solid #dae4e9; }}
code {{ overflow-wrap: anywhere; }}
a {{ color: #005c63; font-weight: bold; }}
</style></head><body><main>
<h1>Ruta Exprés · Monitoreo de entregas</h1>
<p>Comparación de distancia, tiempo de entrega e importe con el lote piloto.</p>
<div style="overflow-x:auto"><table>
<thead><tr><th>Grupo</th><th>Lote</th><th>Fecha</th><th>Pedidos</th><th>Centro</th><th>Periferia</th></tr></thead>
<tbody>{tabla_fila("Referencia", referencia)}{tabla_fila("Actual", actual)}</tbody>
</table></div>
<p>Commit: <code>{commit}</code></p>
<p><a href="comparacion.html">Abrir informe de Evidently</a></p>
</main></body></html>"""
    (salida / "index.html").write_text(portada, encoding="utf-8")
    print("Informe listo: public/index.html")


if __name__ == "__main__":
    main()
