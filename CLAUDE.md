# Buscaopos

Comparativa de oposiciones docentes por CCAA, de ANPE La Rioja. Repositorio pensado para GitHub (cuenta sindicatoanperioja), como Retribuciones.

- Los datos viven en `datos/*.csv` (separador `;`, UTF-8 con BOM). La app y la Excel se generan desde ahí; no meter cifras a mano en `index.html`.
- El buscador lee `datos/plazas.js`/`plazas.json`, que genera `herramientas/generar_datos.py`; regenerar tras tocar un CSV. El formato (el contrato del futuro backend) está en `documentacion/esquema-datos.md`.
- Cada cifra lleva estado (Convocada, Acordada, OEP publicada, Borrador, Anuncio, Sin datos) y fuente. Distinguir siempre OEP de convocatoria.
- En el buscador solo hay tres estados: Borrador (anuncio, noticia, propuesta, acuerdo u OEP: todo lo no convocado), Convocada y Convocada con plazo cerrado. Interesa el año previsto de convocatoria, no el de la OEP. El detalle original se guarda en `fase`.
- Navarra se trata como dos filas: castellano y euskera.
- En la tabla resumen, por cada CCAA se usa la cifra más alta entre 2025 y 2027.
- Códigos de especialidad: solo los confirmados; si no, se deja vacío (`codigo_confirmado = no` en `especialidades.csv`).
- Textos humanizados, sin patrones de IA (ver instrucciones globales). Diseño con la identidad de ANPE La Rioja.
- Antes de subir a GitHub, confirmar con el usuario qué datos son públicos: las plazas de La Rioja de la OPE extraordinaria vienen de una propuesta en negociación.
