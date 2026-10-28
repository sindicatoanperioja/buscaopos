# Buscaopos

Comparativa de las oposiciones docentes de todas las comunidades autónomas: cuántas plazas convoca cada una, de qué cuerpos y especialidades, y en qué punto está el proceso. Lo mantiene ANPE La Rioja.

## Carpetas

- `index.html`: la aplicación (una sola página, sin servidor).
- `datos/`: los datos en CSV, separados por `;` y en UTF-8.
  - `resumen_ccaa.csv`: plazas de 2025 y 2027 por comunidad y estado del proceso.
  - `plazas_especialidad_2027.csv`: una fila por comunidad, cuerpo, especialidad e idioma.
  - `estado_ccaa_2027.csv`: estado de cada comunidad en Secundaria y en Maestros.
  - `especialidades.csv`: catálogo de cuerpos y especialidades con su código.
  - `navarra_2027_turnos.csv`: Navarra 2027 por turno (libre, reserva y acceso).
- `documentacion/`: notas por comunidad y fuentes consultadas.
- `herramientas/`: scripts para generar la Excel comparativa a partir de los CSV.

## Estados

| Estado | Qué significa |
|---|---|
| Convocada | Convocatoria publicada en el boletín oficial |
| Acordada | Reparto acordado o aprobado en Mesa Sectorial |
| OEP publicada | Oferta de empleo en el boletín, sin convocatoria ni reparto por especialidad |
| Borrador | Propuesta presentada en mesa, sin acuerdo |
| Anuncio | Declaración del gobierno, sin documento |

Navarra va en dos filas, castellano y euskera, porque son listas separadas.

## Generar la Excel

```
python herramientas/generar_excel.py herramientas/plantilla_excel.xlsx datos/plazas_especialidad_2027.csv datos/estado_ccaa_2027.csv salida/plazas_especialidad_2027.xlsx herramientas/notas_excel.txt
```

Necesita Python 3 con `openpyxl`.
