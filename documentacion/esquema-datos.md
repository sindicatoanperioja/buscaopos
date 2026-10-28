# Formato de los datos del buscador

El buscador (`index.html`) lee una lista de registros. Hoy la genera `herramientas/generar_datos.py` a partir de los CSV de `datos/` y la deja en `datos/plazas.json` y `datos/plazas.js`. El `.js` es el mismo contenido y sirve para abrir la página con doble clic, sin servidor. Cuando exista el backend, tendrá que devolver este mismo formato y bastará con cambiar la función `cargarDatos()` de `index.html`.

```json
{
  "generado": "2026-10-28",
  "plazas": [ { ...registro... } ]
}
```

## Un registro

Cada registro es un año, una comunidad, un cuerpo y una especialidad con su número de plazas. Si la comunidad aún no ha repartido por especialidad, el registro lleva `especialidad` vacía y es el total de la comunidad o del cuerpo. En la página esos registros salen aparte, en "Sin reparto por especialidad todavía".

| Campo | Obligatorio | Ejemplo | Notas |
|---|---|---|---|
| `id` | sí | `2027-la-rioja-0590-006` | Único. |
| `anio` | sí | `2027` | Año de celebración de las pruebas, no el de publicación. Navarra convoca en otoño o diciembre y examina en junio del año siguiente: va en el año siguiente. En los concursos de méritos sin pruebas, el año en que termina el plazo de solicitudes. |
| `comunidad` | sí | `Navarra` | |
| `lista` | sí | `Navarra (euskera)` | Lo que se muestra. Navarra va en dos listas; en el resto coincide con la comunidad. |
| `lista_id` | sí | `navarra-euskera` | Es lo que va en el enlace (`?ccaa=navarra-euskera`). |
| `cuerpo` | no | `0590` | Cuatro cifras. Vacío si el total abarca varios cuerpos. |
| `cuerpo_nombre`, `cuerpo_corto` | no | `Secundaria` | |
| `codigo` | no | `006` | Solo si está confirmado (ver `especialidades.csv`). |
| `especialidad` | no | `Matemáticas` | Vacío en los totales sin reparto. |
| `idioma` | no | `Euskera` | |
| `plazas` | no | `25` | Vacío si solo hay anuncio sin cifra. |
| `turnos` | no | `{"libre":24,"reserva":6,"acceso":30}` | Cuando la convocatoria los separa: `libre`, `reserva` (discapacidad), `acceso` (promoción interna desde otro cuerpo o subgrupo) y `otras` (otras reservas, como víctimas del terrorismo; sale de restar al total los otros tres). |
| `desglose` | no | `{"ordinarias":17,"extraordinarias":8}` | De momento solo La Rioja. |
| `estado` | sí | `convocada` | `previsto`, `convocada` o `cerrada` (convocada con el plazo de inscripción cerrado). |
| `fase` | no | `Acordada en mesa sectorial` | Solo en las previstas: de dónde sale la cifra (anuncio, propuesta en mesa, acuerdo u OEP). |
| `tipo` | sí | `ordinaria` | `ordinaria` (RD 276/2007), `estabilizacion_prueba` (concurso-oposición de estabilización, RD 270/2022) o `estabilizacion_sin_prueba` (concurso de méritos excepcional, sin examen). |
| `normativa` | no | `RD 276/2007` | |
| `inicio_plazo`, `fin_plazo` | no | `2026-10-28` | Plazo de inscripción, en formato AAAA-MM-DD. |
| `fecha_examen` | no | `2027-04-17` | Día en que empiezan las pruebas. |
| `requisito_linguistico` | no | `Catalán C1` | En Cataluña, C. Valenciana, Baleares, Galicia y País Vasco sale de `requisitos_linguisticos.csv` y vale para todas sus plazas. En Navarra (euskera), de la convocatoria. |
| `requisito_detalle` | no | `Hay que acreditar el nivel C1 de catalán.` | Explicación corta del requisito. |
| `procedimiento` | sí | `concurso_oposicion` | `concurso_oposicion` (con examen) o `concurso_meritos` (sin examen). Hay concursos de méritos que no son de estabilización, como el acceso a Catedráticos. |
| `observaciones` | no | | Texto libre. |
| `fuentes` | sí | `["https://bon.navarra.es/..."]` | Enlaces o descripciones de la fuente. |

## Estado que ve el usuario

Hay tres estados:

- Previstas: todo lo que aún no está convocado. Da igual que la cifra venga de un anuncio, de una noticia de un sindicato o de la Consejería, de una propuesta en mesa o de una OEP aprobada: la OEP se puede convocar en cualquiera de los tres años siguientes, así que lo que cuenta es el año en que se prevé convocar. El campo `fase` dice de dónde sale el dato.
- Convocadas: publicadas en el boletín. Si hoy cae dentro del plazo de inscripción, la ficha dice cuántos días quedan.
- Convocadas, plazo cerrado: la página la marca así sola cuando ya pasó `fin_plazo` o el año es anterior al actual. También se puede poner a mano en el CSV con el estado "Convocada - plazo cerrado".

## De dónde sale cada campo hoy

- `plazas_convocadas.csv` (2023 a 2026) y `plazas_especialidad_2027.csv`: una fila por especialidad.
- `convocatorias.csv`: los datos comunes a toda una convocatoria (plazo, fecha de las pruebas, normativa, requisito de idioma, enlace). Con el cuerpo vacío se aplican a todos los cuerpos de esa comunidad y año. Así, si cambia el plazo, se toca una fila y no cincuenta. Si un mismo año y cuerpo tiene dos convocatorias (por ejemplo, ordinaria y de estabilización), cada fila de plazas se asocia a la convocatoria cuyo enlace aparece en su columna fuente.
- `resumen_ccaa.csv`: los totales de 2025 de las comunidades sin reparto.
- `requisitos_linguisticos.csv`: el requisito de lengua cooficial de cada comunidad que lo exige.

En `convocatorias.csv`, la columna `tipo` vale "Ordinaria" o "Estabilización", `normativa` dice la norma, y `procedimiento` vale "Concurso de méritos" cuando no hay examen (vacía es concurso-oposición). Con `tipo` y `procedimiento` el generador saca los tres tipos: ordinaria, estabilización con prueba y estabilización sin prueba.

Después de tocar un CSV hay que volver a generar los datos:

```
python herramientas/generar_datos.py
```

## Enlaces con filtros

La dirección de la página guarda la búsqueda, así que se puede copiar y compartir:

- `?ccaa=la-rioja`: La Rioja (es el enlace para poner en la web de ANPE La Rioja).
- `?anio=2027&esp=0590-006`: Matemáticas de Secundaria en 2027, en todas las comunidades.
- `?estado=convocada`: todo lo convocado que aún admite inscripciones.
- `?vista=lista`: resultados en lista en vez de fichas.
- `?idioma=ninguno`: solo plazas sin requisito de lengua cooficial.
- `?tipo=ordinaria`: solo oposiciones ordinarias, sin estabilización.
- `?turno=reserva`: solo plazas de reserva para personas con discapacidad; las cifras pasan a ser las de ese turno.
- `?q=ingles&cuerpo=0590,0592`: búsqueda de texto con dos cuerpos.

Los valores múltiples van separados por comas. Si el enlace no lleva año, la página muestra la primera convocatoria con datos a partir del año en curso.
