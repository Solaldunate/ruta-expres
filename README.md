# Ruta Exprés — Monitoreo con Evidently

Práctica autónoma 4. Comparamos pedidos de una tienda ficticia de Cochabamba con su lote piloto. GitHub Actions valida los archivos y publica en Pages el informe del commit aprobado.

## Datos

El CSV original de la práctica se conserva en `datos/pedidos_ruta_express.csv`. Con `python preparar.py` se seleccionaron las filas por el valor exacto de `lote`, conservando las siete columnas. El script comprueba 120 pedidos por lote y 360 identificadores únicos. Produce `referencia.csv` (base), `control.csv` y `expansion.csv`, y copia control a `actual.csv`. No vuelvas a ejecutar la preparación durante los cuatro escenarios: cambia solo `actual.csv` con `escenario.py`.

## Ejecución local

Python 3.12, Evidently 0.7.15 y pandas 2.2.3. En PowerShell, desde la raíz:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe validar.py
.\.venv\Scripts\python.exe monitorear.py
Start-Process public/index.html
```

En VS Code selecciona `.venv\Scripts\python.exe` con **Python: Select Interpreter**. Los comandos siguientes usan `python`; activa la venv con `.\.venv\Scripts\Activate.ps1` o sustituye `python` por `.\.venv\Scripts\python.exe`. Desde la portada, abre el informe y verifica que aparezcan las tres variables.

## Configuración del monitoreo

Se aplica la prueba Kolmogórov–Smirnov de dos muestras (`ks`) con umbral de p de 0,05 a `distancia_km`, `entrega_min` e `importe_bs` en todos los escenarios válidos. El umbral de proporción para el aviso global es 0,50. Consulta el resultado de cada variable: puede cambiar una sin que aparezca el aviso global. La zona se resume en la portada; los identificadores, fechas y lotes quedan en los CSV para rastrear los pedidos.

Un tiempo negativo incumple una regla y bloquea el despliegue. Una distancia o duración mayor que la observada en el piloto puede seguir siendo válida; si cambia la distribución, el informe permite investigar el motivo. No se mide precisión del modelo: faltan sus predicciones por pedido para compararlas con las duraciones reales.

## Publicación y evidencia

Crea el repositorio público `ruta-express-evidently` con rama `main`. Copia el contenido de la carpeta del proyecto en la raíz, incluida `.github`. En GitHub configura **Settings → Pages → Source → GitHub Actions**. Si el primer push ocurrió antes de activar Pages, vuelve a ejecutar ese flujo después de configurarlo.

Completa un commit y push a `main` por escenario. Espera a que termine Actions y verifica el commit que muestra Pages antes de avanzar. A partir del primer push conserva el mismo código y cambia solo `datos/actual.csv`.

| Escenario | Preparación | Qué comprobar |
|---|---|---|
| Control | Ya viene listo; para restaurarlo, `python escenario.py control` | CI y CD correctos. Registra el resultado por variable como punto de comparación. |
| Expansión | `python escenario.py expansion` | CI y CD correctos. Revisa el cambio de zonas y el drift por variable. |
| Error de captura | `python escenario.py error` | Guarda el valor original que imprime el comando. Las pruebas pasan, la validación falla en `entrega_min` y CD queda omitido. Pages conserva el commit de expansión. |
| Recuperación | `python escenario.py recuperacion` | Se restaura el lote de expansión. CI y CD pasan, Pages muestra el nuevo commit y el informe debe coincidir estadísticamente con expansión. |

Para la entrega copia los enlaces reales del repositorio y de la portada de Pages. Guarda también los enlaces a las cuatro ejecuciones, el commit publicado en cada caso y lo que mostró Evidently para cada variable. Como evidencia puedes guardar capturas de control, expansión, validación fallida con CD omitido y recuperación.

## Resultados esperados a partir de los CSV

| Lote | Centro | Periferia | Distancia | Entrega | Importe |
|---|---:|---:|---|---|---|
| Base (5 de octubre) | 115 | 5 | Referencia | Referencia | Referencia |
| Control (12 de octubre) | 118 | 2 | Sin drift | Sin drift | Sin drift |
| Expansion (19 de octubre) | 16 | 104 | Con drift | Con drift | Sin drift |

Una comprobacion independiente con KS sobre los CSV da p aproximados de
0,588 / 0,484 / 0,801 para control y de menos de 0,001 / menos de 0,001 /
0,237 para expansion, en el orden de la tabla. Confirma estos resultados
en el HTML de Evidently durante las ejecuciones en GitHub. El cambio de
distancia y tiempo coincide con la mayor presencia de pedidos en periferia;
eso orienta la investigacion, pero no demuestra causalidad.
