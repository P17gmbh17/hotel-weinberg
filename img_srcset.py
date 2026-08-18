# -*- coding: utf-8 -*-
"""
Gemeinsamer Helfer fuer responsive Bilder (srcset/sizes) in allen
build_*.py-Skripten.

Fuer jedes Content-Foto (assets/fotos/, assets/aktivitaeten/,
assets/kulinarik/) existiert optional eine "-450w"-Mobile-Variante
(erzeugt durch generate_mobile_variants.py, max. 450px breit). Ist eine
solche Variante vorhanden, wird hier automatisch ein srcset/sizes-Attribut
gebaut, damit mobile Geraete die kleinere Datei laden.

Nutzung in einem build_*.py:
    from img_srcset import srcset_attr
    ...
    f'<img src="{path}"{srcset_attr(path)} alt="...">'

Faellt bewusst auf einen leeren String zurueck (kein Fehler), wenn keine
Mobile-Variante existiert oder der Pfad nicht zu einem Content-Foto gehoert
(z.B. Logos/Icons) - damit ist die Funktion an jeder <img>-Stelle gefahrlos
einsetzbar.
"""
import os
from functools import lru_cache

MOBILE_SUFFIX = "-450w"
CONTENT_DIRS = ("assets/fotos/", "assets/aktivitaeten/", "assets/kulinarik/")

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"


@lru_cache(maxsize=None)
def _dims(abs_path):
    try:
        from PIL import Image
        with Image.open(abs_path) as im:
            return im.size
    except Exception:
        return None


def _is_content_photo(rel_path):
    if not rel_path or not rel_path.lower().endswith((".jpg", ".jpeg")):
        return False
    norm = rel_path.replace("../", "", 1)
    return any(norm.startswith(d) for d in CONTENT_DIRS)


def srcset_attr(rel_path):
    """rel_path: Bildpfad wie er im HTML steht, z.B. '../assets/fotos/x.jpg'.
    Gibt ' srcset="..." sizes="..."' zurueck oder '' wenn nicht anwendbar."""
    if not _is_content_photo(rel_path):
        return ""

    norm = rel_path.replace("../", "", 1)
    abs_full = os.path.normpath(os.path.join(BASE, norm))
    stem, ext = os.path.splitext(norm)
    mobile_norm = f"{stem}{MOBILE_SUFFIX}{ext}"
    abs_mobile = os.path.normpath(os.path.join(BASE, mobile_norm))

    dims_full = _dims(abs_full)
    dims_mobile = _dims(abs_mobile)
    if not dims_full or not dims_mobile:
        return ""
    if dims_full[0] <= dims_mobile[0]:
        return ""

    mobile_rel = rel_path.replace(norm, mobile_norm)
    return (
        f' srcset="{mobile_rel} {dims_mobile[0]}w, {rel_path} {dims_full[0]}w"'
        f' sizes="(max-width: 480px) {dims_mobile[0]}px, {dims_full[0]}px"'
    )


def mobile_src(rel_path):
    """Fuer Komponenten, die AUSSCHLIESSLICH auf Mobile gerendert werden
    (z.B. per JS src-Rotation, wo srcset wegen dynamischer img.src-Wechsel
    nicht zuverlaessig funktioniert): gibt direkt den Pfad der -450w-Variante
    zurueck, falls vorhanden, sonst den Originalpfad unveraendert."""
    if not _is_content_photo(rel_path):
        return rel_path
    norm = rel_path.replace("../", "", 1)
    stem, ext = os.path.splitext(norm)
    mobile_norm = f"{stem}{MOBILE_SUFFIX}{ext}"
    abs_mobile = os.path.normpath(os.path.join(BASE, mobile_norm))
    if not _dims(abs_mobile):
        return rel_path
    return rel_path.replace(norm, mobile_norm)
