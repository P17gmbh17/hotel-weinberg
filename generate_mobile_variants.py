# -*- coding: utf-8 -*-
"""
Erzeugt fuer jedes Content-Foto (assets/fotos/, assets/aktivitaeten/,
assets/kulinarik/) zusaetzliche verkleinerte Versionen fuer den Einsatz per
srcset (siehe img_srcset.py):

    -450w   kleine Vorschau / kleine Bildflaechen auf Mobile
    -900w   grosse Bildflaechen auf Mobile (z.B. die quadratischen
            Impressionen-Rotator-Slots auf der Geniessen-Seite, die fast
            die volle Viewport-Breite einnehmen). Mit 450px allein wurden
            diese auf Retina-Displays um mehr als das Dreifache
            hochskaliert und waren sichtbar unscharf.

Aufruf:
    python3 generate_mobile_variants.py

Ueberspringt Dateien, die bereits eine aktuelle Variante haben (Variante
neuer als Original), und Bilder die ohnehin schon schmaler sind als die
Zielbreite.
"""
import os
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"
CONTENT_DIRS = ["assets/fotos", "assets/aktivitaeten", "assets/kulinarik"]

# (Suffix, max. Breite, JPEG-Qualitaet)
VARIANTS = [
    ("-450w", 450, 80),
    ("-900w", 900, 82),
]
SUFFIXES = [suffix for suffix, _, _ in VARIANTS]


def find_source_images():
    for content_dir in CONTENT_DIRS:
        abs_dir = os.path.join(BASE, content_dir)
        for root, dirs, files in os.walk(abs_dir):
            for fn in files:
                if fn.startswith("._"):
                    continue
                if not fn.lower().endswith((".jpg", ".jpeg")):
                    continue
                stem = os.path.splitext(fn)[0]
                if any(stem.endswith(s) for s in SUFFIXES):
                    continue
                yield os.path.join(root, fn)


def main():
    created, skipped_small, skipped_uptodate, errors = 0, 0, 0, 0
    total_new_size = 0

    for src in find_source_images():
        stem, ext = os.path.splitext(src)

        for suffix, maxw, quality in VARIANTS:
            dst = f"{stem}{suffix}{ext}"

            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                skipped_uptodate += 1
                continue

            try:
                im = Image.open(src)
                im = ImageOps.exif_transpose(im)
                w, h = im.size
                if w <= maxw:
                    skipped_small += 1
                    continue
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                nh = round(h * maxw / w)
                im = im.resize((maxw, nh), Image.LANCZOS)
                im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
                total_new_size += os.path.getsize(dst)
                created += 1
            except Exception as e:
                print(f"FEHLER bei {src} ({suffix}): {e}")
                errors += 1

    print(
        f"\n{created} Varianten erstellt "
        f"({total_new_size / 1024 / 1024:.1f} MB neu), "
        f"{skipped_small} Original bereits kleiner als Zielbreite, "
        f"{skipped_uptodate} bereits aktuell, "
        f"{errors} Fehler."
    )


if __name__ == "__main__":
    main()
