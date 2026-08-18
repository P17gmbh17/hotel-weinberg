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
MIDSIZE_SUFFIX = "-900w"
CONTENT_DIRS = ("assets/fotos/", "assets/aktivitaeten/", "assets/kulinarik/")

# Breite des Rotator-Slots auf Mobile: volle Viewport-Breite minus der
# seitlichen Raender (.impression-band__mobile { margin: 0 24px }).
ROTATOR_SIZES = "calc(100vw - 48px)"

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
    """Fuer Komponenten, die AUSSCHLIESSLICH auf Mobile gerendert werden:
    gibt direkt den Pfad der -450w-Variante zurueck, falls vorhanden, sonst
    den Originalpfad unveraendert.

    ACHTUNG: nur fuer Bilder verwenden, die auch wirklich klein DARGESTELLT
    werden. Fuer die grossen Rotator-Slots (nahezu volle Viewport-Breite,
    quadratisch, object-fit: cover) ist 450px viel zu wenig - dort
    rotator_variant() benutzen."""
    if not _is_content_photo(rel_path):
        return rel_path
    norm = rel_path.replace("../", "", 1)
    stem, ext = os.path.splitext(norm)
    mobile_norm = f"{stem}{MOBILE_SUFFIX}{ext}"
    abs_mobile = os.path.normpath(os.path.join(BASE, mobile_norm))
    if not _dims(abs_mobile):
        return rel_path
    return rel_path.replace(norm, mobile_norm)


def _variant(rel_path, suffix):
    """Pfad + Breite einer Groessenvariante, oder None wenn sie nicht existiert."""
    norm = rel_path.replace("../", "", 1)
    stem, ext = os.path.splitext(norm)
    var_norm = f"{stem}{suffix}{ext}"
    dims = _dims(os.path.normpath(os.path.join(BASE, var_norm)))
    if not dims:
        return None
    return rel_path.replace(norm, var_norm), dims[0]


def rotator_variant(rel_path):
    """Fuer die per JS rotierten Impressionen-Slots auf Mobile.

    Diese Slots sind quadratisch und fast so breit wie der Viewport; bei
    object-fit: cover auf einer 3:2-Quelle und DPR 2-3 werden dort ueber
    1000 echte Pixel gebraucht. Die -450w-Variante allein (450x300) wurde
    dadurch mehr als 3-fach hochskaliert - Ergebnis: komplett unscharfe
    Bilder. Deshalb hier ein vollstaendiges srcset ueber alle vorhandenen
    Groessen (450w / 900w / Original) und der Browser waehlt passend zur
    Geraeteaufloesung.

    srcset funktioniert dabei sehr wohl zuverlaessig mit JS-Wechseln - man
    muss beim Wechsel nur img.srcset MITSETZEN und nicht nur img.src (das
    macht das Rotator-Snippet in den Templates).

    Gibt ein dict zurueck: {"src", "srcset", "sizes"}. "srcset"/"sizes"
    koennen leer sein, wenn keine Varianten existieren.
    """
    if not _is_content_photo(rel_path):
        return {"src": rel_path, "srcset": "", "sizes": ""}

    full_dims = _dims(os.path.normpath(os.path.join(BASE, rel_path.replace("../", "", 1))))
    candidates = []
    for suffix in (MOBILE_SUFFIX, MIDSIZE_SUFFIX):
        var = _variant(rel_path, suffix)
        if var:
            candidates.append(var)
    if full_dims:
        candidates.append((rel_path, full_dims[0]))

    # nach Breite sortieren und Duplikate/zu grosse Zwischengroessen filtern
    seen = set()
    entries = []
    for path, width in sorted(candidates, key=lambda x: x[1]):
        if width in seen:
            continue
        seen.add(width)
        entries.append((path, width))

    if len(entries) < 2:
        return {"src": rel_path, "srcset": "", "sizes": ""}

    # Default-src: mittlere Groesse, damit Browser ohne srcset-Support
    # (und der No-JS-Fall) etwas Brauchbares bekommen.
    default = entries[len(entries) // 2][0]
    return {
        "src": default,
        "srcset": ", ".join(f"{p} {w}w" for p, w in entries),
        "sizes": ROTATOR_SIZES,
    }
