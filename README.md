# Buscaopos

Comparativa de las oposiciones docentes de todas las comunidades autónomas: cuántas plazas convoca cada una, de qué cuerpos y especialidades, y en qué punto está el proceso. Lo mantiene ANPE La Rioja.

## Carpetas

- `index.html`: el buscador de plazas (una sola página, sin servidor). Filtra por año, comunidad, cuerpo, especialidad y estado, y la dirección guarda los filtros para poder compartir la búsqueda.
- `datos/`: los datos en CSV, separados por `;` y en UTF-8.
  - `resumen_ccaa.csv`: plazas de 2025 y 2027 por comunidad y estado del proceso.
  - `plazas_especialidad_2027.csv`: una fila por comunidad, cuerpo, especialidad e idioma.
  - `estado_ccaa_2027.csv`: estado de cada comunidad en Secundaria y en Maestros.
  - `especialidades.csv`: catálogo de cuerpos y especialidades con su código.
  - `navarra_2027_turnos.csv`: Navarra 2027 por turno (libre, reserva y acceso).
  - `convocatorias.csv`: datos comunes de cada convocatoria (plazo de inscripción, fecha de las pruebas, normativa, requisito de idioma).
  - `plazas.json` y `plazas.js`: lo que lee el buscador. Se generan, no se editan a mano.
- `documentacion/`: notas por comunidad, fuentes consultadas y el formato de los datos del buscador (`esquema-datos.md`).
- `herramientas/`: scripts para generar los datos del buscador y la Excel comparativa a partir de los CSV.
- `img/`: logo.

## Estados

| Estado | Qué significa |
|---|---|
| Convocada | Convocatoria publicada en el boletín oficial |
| Acordada | Reparto acordado o aprobado en Mesa Sectorial |
| OEP publicada | Oferta de empleo en el boletín, sin convocatoria ni reparto por especialidad |
| Borrador | Propuesta presentada en mesa, sin acuerdo |
| Anuncio | Declaración del gobierno, sin documento |

Navarra va en dos filas, castellano y euskera, porque son listas separadas.

## Actualizar el buscador

Después de cambiar cualquier CSV:

```
python herramientas/generar_datos.py
```

## Generar la Excel

```
python herramientas/generar_excel.py herramientas/plantilla_excel.xlsx datos/plazas_especialidad_2027.csv datos/estado_ccaa_2027.csv salida/plazas_especialidad_2027.xlsx herramientas/notas_excel.txt
```

Necesita Python 3 con `openpyxl`.
