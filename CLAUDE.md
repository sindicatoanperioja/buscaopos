# Buscaopos

Comparativa de oposiciones docentes por CCAA, de ANPE La Rioja. Repositorio pensado para GitHub (cuenta sindicatoanperioja), como Retribuciones.

- Los datos viven en `datos/*.csv` (separador `;`, UTF-8 con BOM). La app y la Excel se generan desde ahí; no meter cifras a mano en `index.html`.
- El buscador lee `datos/plazas.js`/`plazas.json`, que genera `herramientas/generar_datos.py`; regenerar tras tocar un CSV. El formato (el contrato del futuro backend) está en `documentacion/esquema-datos.md`.
- Cada cifra lleva estado (Convocada, Acordada, OEP publicada, Borrador, Anuncio, Sin datos) y fuente. Distinguir siempre OEP de convocatoria.
- En el buscador solo hay tres estados: Previstas (anuncio, noticia, propuesta, acuerdo u OEP: todo lo no convocado), Convocadas y Convocadas con plazo cerrado. Interesa el año previsto de convocatoria, no el de la OEP. El detalle original se guarda en `fase`.
- Navarra se trata como dos filas: castellano y euskera.
- El año es siempre el de celebración de las pruebas, no el de publicación de la convocatoria. En concursos de méritos sin pruebas, el del fin del plazo de solicitudes.
- Tipo de oposición: ordinaria (RD 276/2007), estabilización con prueba o estabilización sin prueba (concurso de méritos). Turnos: libre, discapacidad, promoción interna y otras reservas.
- En la tabla resumen, por cada CCAA se usa la cifra más alta entre 2025 y 2027.
- Códigos de especialidad: solo los confirmados; si no, se deja vacío (`codigo_confirmado = no` en `especialidades.csv`).
- Textos humanizados, sin patrones de IA (ver instrucciones globales). Diseño con la identidad de ANPE La Rioja.
- El repo es público y se publica con GitHub Pages (https://sindicatoanperioja.github.io/buscaopos/), como Retribuciones. El 28-10-2026 el usuario decidió publicar también el reparto de la OPE extraordinaria de La Rioja. No subir rutas de la unidad Z: ni enlaces privados.
