"""Genera los datos del buscador (datos/plazas.json y datos/plazas.js) a partir de los CSV.

Uso: python herramientas/generar_datos.py

Cada registro es una "plaza" en el sentido del buscador: un año, una comunidad (o lista,
en Navarra), un cuerpo y una especialidad con su número de plazas. Las filas sin
especialidad son totales de comunidad o de cuerpo que aún no tienen reparto.
El formato es el que tendrá que devolver el backend; está descrito en
documentacion/esquema-datos.md.
"""
import csv
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"

CUERPOS = {
    "0510": "Inspectores de Educación",
    "0511": "Catedráticos de Enseñanza Secundaria",
    "0512": "Catedráticos de Escuelas Oficiales de Idiomas",
    "0513": "Catedráticos de Música y Artes Escénicas",
    "0593": "Catedráticos de Música y Artes Escénicas",
}
CUERPOS_CORTO = {
    "0510": "Inspección",
    "0511": "Catedráticos de Secundaria",
    "0512": "Catedráticos de EOI",
    "0513": "Catedráticos de Música",
    "0590": "Secundaria",
    "0592": "Escuelas Oficiales de Idiomas",
    "0593": "Catedráticos de Música",
    "0594": "Música y Artes Escénicas",
    "0595": "Artes Plásticas y Diseño",
    "0596": "Maestros de Taller",
    "0597": "Maestros",
    "0598": "FP (sectores singulares)",
}
# El buscador solo distingue tres estados. Anuncio, borrador, acuerdo en mesa y OEP son
# todos previsión de una convocatoria futura ("borrador"); lo que fue se guarda en "fase".
ESTADOS = {
    "convocada": ("convocada", None),
    "convocada - plazo cerrado": ("cerrada", None),
    "acordada": ("borrador", "Acordada"),
    "acordada en mesa": ("borrador", "Acordada en mesa sectorial"),
    "oep publicada": ("borrador", "Oferta de empleo publicada, sin convocar"),
    "borrador": ("borrador", "Borrador presentado en mesa"),
    "anuncio": ("borrador", "Anuncio, sin documento"),
    "sin datos": (None, None),
}


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def entero(valor):
    valor = (valor or "").strip().replace(".", "")
    return int(valor) if valor.isdigit() else None


def estado(valor):
    clave = ESTADOS.get((valor or "").strip().lower())
    if not clave:
        raise ValueError(f"Estado desconocido: {valor!r}")
    return clave


def cuerpo(codigo):
    codigo = (codigo or "").strip()
    if not codigo:
        return None
    return codigo.zfill(4)


catalogo = {}
por_nombre = {}  # (cuerpo, nombre normalizado) -> código, para convocatorias que no dan código
for r in leer("especialidades.csv"):
    CUERPOS.setdefault(r["cuerpo"], r["nombre_cuerpo"])
    if r["codigo_confirmado"].strip().lower() == "si":
        catalogo[(r["cuerpo"], r["codigo"].zfill(3))] = r["especialidad"]
        por_nombre[(r["cuerpo"], slug(r["especialidad"]))] = r["codigo"].zfill(3)

# La columna cuerpo puede llevar varios separados por comas, o ir vacía para todos.
# Un mismo año y cuerpo puede tener varias convocatorias (ordinaria y estabilización).
convocatorias = {}
for r in leer("convocatorias.csv"):
    for cu in (r["cuerpo"] or "").split(","):
        convocatorias.setdefault((r["fila"], r["anio"], cuerpo(cu)), []).append(r)


def datos_convocatoria(fila, anio, cu, fuentes):
    """Los datos comunes de la convocatoria: primero los del cuerpo, si no los de toda la comunidad.
    Si hay varias, la que tiene como enlace la primera fuente de la fila que coincida."""
    candidatas = convocatorias.get((fila, anio, cu)) or convocatorias.get((fila, anio, None)) or [{}]
    for f in fuentes:
        for c in candidatas:
            if c.get("enlace", "").strip() == f:
                return c
    return candidatas[0]


# Requisito de lengua cooficial por comunidad: se aplica a todas sus plazas, de cualquier año.
requisitos = {r["comunidad"]: r for r in leer("requisitos_linguisticos.csv")}


def comunidad(fila):
    return fila.split(" (")[0]


plazas = []
ids = set()


def anadir(reg):
    base = "-".join(str(x) for x in (reg["anio"], reg["lista_id"], reg["cuerpo"] or "todos",
                                     reg["codigo"] or slug(reg["especialidad"] or "sin-reparto")) )
    if reg["idioma"]:
        base += "-" + slug(reg["idioma"])
    rid, n = base, 2
    while rid in ids:
        rid, n = f"{base}-{n}", n + 1
    ids.add(rid)
    plazas.append({"id": rid, **reg})


def registro(fila, anio, est_fase, cu, codigo, especialidad, idioma, plazas_n, nota, fuente,
             turnos=None, desglose=None):
    est, fase = est_fase
    fuentes = [x.strip() for x in (fuente or "").split("|") if x.strip()]
    conv = datos_convocatoria(fila, str(anio), cu, fuentes)
    codigo = codigo.zfill(3) if codigo else por_nombre.get((cu, slug(especialidad or "")), "")
    nombre = catalogo.get((cu, codigo)) or especialidad or ""
    req_ccaa = requisitos.get(comunidad(fila), {})
    requisito = req_ccaa.get("requisito") or conv.get("requisito_linguistico", "").strip()
    if not requisito and idioma and idioma.lower() != "castellano":
        requisito = idioma
    obs = [x for x in (nota, conv.get("observaciones", "").strip()) if x]
    if conv.get("enlace") and conv["enlace"] not in fuentes:
        fuentes.insert(0, conv["enlace"].strip())
    return {
        "anio": int(anio),
        "comunidad": comunidad(fila),
        "lista": fila,
        "lista_id": slug(fila),
        "cuerpo": cu,
        "cuerpo_nombre": CUERPOS.get(cu) if cu else None,
        "cuerpo_corto": CUERPOS_CORTO.get(cu) if cu else None,
        "codigo": codigo or None,
        "especialidad": nombre or None,
        "idioma": idioma or None,
        "plazas": plazas_n,
        "turnos": turnos,
        "desglose": desglose,
        "estado": est,
        "fase": fase,
        "tipo_oposicion": conv.get("tipo_oposicion", "").strip() or None,
        "inicio_plazo": conv.get("inicio_plazo", "").strip() or None,
        "fin_plazo": conv.get("fin_plazo", "").strip() or None,
        "fecha_examen": conv.get("fecha_examen", "").strip() or None,
        "requisito_linguistico": requisito or None,
        "requisito_detalle": req_ccaa.get("detalle") or None,
        "procedimiento": "concurso_meritos" if conv.get("procedimiento", "").strip().lower() == "concurso de méritos" else "concurso_oposicion",
        "observaciones": " ".join(o if o.endswith(".") else o + "." for o in obs) or None,
        "fuentes": fuentes,
    }


# Una fila por comunidad, cuerpo y especialidad: convocatorias ya celebradas y previsión de 2027
FICHEROS_PLAZAS = ["plazas_convocadas.csv", "plazas_especialidad_2027.csv"]
filas_plazas = [r for f in FICHEROS_PLAZAS if (DATOS / f).exists() for r in leer(f)]
for r in filas_plazas:
    if "superada" in r["fila"] or estado(r["estado"])[0] is None:
        continue
    turnos = None
    if any(r[k].strip() for k in ("libre", "reserva", "acceso")):
        turnos = {k: entero(r[k]) or 0 for k in ("libre", "reserva", "acceso")}
    desglose = None
    if r["aprobadas"].strip() or r["extra"].strip():
        desglose = {"ordinarias": entero(r["aprobadas"]) or 0, "extraordinarias": entero(r["extra"]) or 0}
    n = entero(r["plazas"])
    anadir(registro(r["fila"], r["anio"], estado(r["estado"]), cuerpo(r["cuerpo"]), r["codigo"].strip(),
                    r["especialidad"].strip(), r["idioma"].strip(), n if n else None,
                    r["nota"].strip(), r["fuente"], turnos, desglose))

# 2025: el total por comunidad, solo donde no hay reparto por especialidad
con_detalle = {(r["fila"], r["anio"]) for r in filas_plazas} | {(comunidad(r["fila"]), r["anio"]) for r in filas_plazas}
for r in leer("resumen_ccaa.csv"):
    n = entero(r["plazas_2025"])
    if not n or (r["comunidad"], "2025") in con_detalle:
        continue
    nota = f"Total de la convocatoria de 2025 ({r['cuerpos_2025']})" if r["cuerpos_2025"] else "Total de la convocatoria de 2025"
    anadir(registro(r["comunidad"], 2025, ("convocada", None), None, "", "", "", n, nota, ""))

# Si una especialidad sin código se llama igual que otra que sí lo trae en otra convocatoria
# (y ese nombre solo tiene un código), se le pone ese código para que se agrupen al buscar.
codigos_vistos = {}
for p in plazas:
    if p["codigo"] and p["especialidad"]:
        codigos_vistos.setdefault((p["cuerpo"], slug(p["especialidad"])), set()).add(p["codigo"])
for p in plazas:
    if not p["codigo"] and p["especialidad"]:
        cods = codigos_vistos.get((p["cuerpo"], slug(p["especialidad"])), set())
        if len(cods) == 1:
            p["codigo"] = next(iter(cods))

salida = {
    "generado": date.today().isoformat(),
    "plazas": plazas,
}
texto = json.dumps(salida, ensure_ascii=False, indent=1)
(DATOS / "plazas.json").write_text(texto + "\n", encoding="utf-8")
(DATOS / "plazas.js").write_text(
    "// Generado con herramientas/generar_datos.py. No editar a mano.\n"
    f"window.BUSCAOPOS_DATOS = {texto};\n", encoding="utf-8")
for anio in sorted({p["anio"] for p in plazas}):
    print(anio, sum(1 for p in plazas if p["anio"] == anio), "registros,",
          sum(p["plazas"] or 0 for p in plazas if p["anio"] == anio), "plazas")
