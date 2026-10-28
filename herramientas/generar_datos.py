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
ESTADOS = {
    "convocada": "convocada",
    "acordada": "acordada",
    "acordada en mesa": "acordada",
    "oep publicada": "oep",
    "borrador": "borrador",
    "anuncio": "anuncio",
    "sin datos": "sin_datos",
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
for r in leer("especialidades.csv"):
    CUERPOS.setdefault(r["cuerpo"], r["nombre_cuerpo"])
    if r["codigo_confirmado"].strip().lower() == "si":
        catalogo[(r["cuerpo"], r["codigo"].zfill(3))] = r["especialidad"]

convocatorias = {}
for r in leer("convocatorias.csv"):
    convocatorias[(r["fila"], r["anio"], cuerpo(r["cuerpo"]))] = r


def datos_convocatoria(fila, anio, cu):
    """Los datos comunes de la convocatoria: primero los del cuerpo, si no los de toda la comunidad."""
    return convocatorias.get((fila, anio, cu)) or convocatorias.get((fila, anio, None)) or {}


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


def registro(fila, anio, est, cu, codigo, especialidad, idioma, plazas_n, nota, fuente,
             turnos=None, desglose=None):
    conv = datos_convocatoria(fila, str(anio), cu)
    codigo = codigo.zfill(3) if codigo else ""
    nombre = catalogo.get((cu, codigo)) or especialidad or ""
    requisito = conv.get("requisito_linguistico", "").strip()
    if not requisito and idioma and idioma.lower() != "castellano":
        requisito = idioma
    obs = [x for x in (nota, conv.get("observaciones", "").strip()) if x]
    fuentes = [x.strip() for x in (fuente or "").split("|") if x.strip()]
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
        "tipo_oposicion": conv.get("tipo_oposicion", "").strip() or None,
        "inicio_plazo": conv.get("inicio_plazo", "").strip() or None,
        "fin_plazo": conv.get("fin_plazo", "").strip() or None,
        "fecha_examen": conv.get("fecha_examen", "").strip() or None,
        "requisito_linguistico": requisito or None,
        "observaciones": " ".join(o if o.endswith(".") else o + "." for o in obs) or None,
        "fuentes": fuentes,
    }


# 2027: una fila por comunidad, cuerpo y especialidad
for r in leer("plazas_especialidad_2027.csv"):
    if "superada" in r["fila"]:
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

# 2025: solo el total por comunidad
for r in leer("resumen_ccaa.csv"):
    n = entero(r["plazas_2025"])
    if not n:
        continue
    nota = f"Total de la convocatoria de 2025 ({r['cuerpos_2025']})" if r["cuerpos_2025"] else "Total de la convocatoria de 2025"
    anadir(registro(r["comunidad"], 2025, "convocada", None, "", "", "", n, nota, ""))

salida = {
    "generado": date.today().isoformat(),
    "plazas": plazas,
}
texto = json.dumps(salida, ensure_ascii=False, indent=1)
(DATOS / "plazas.json").write_text(texto + "\n", encoding="utf-8")
(DATOS / "plazas.js").write_text(
    "// Generado con herramientas/generar_datos.py. No editar a mano.\n"
    f"window.BUSCAOPOS_DATOS = {texto};\n", encoding="utf-8")
print(f"{len(plazas)} registros, {sum(p['plazas'] or 0 for p in plazas if p['anio'] == 2027)} plazas en 2027")
