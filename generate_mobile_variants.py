# -*- coding: utf-8 -*-
"""
Erzeugt fuer jedes Content-Foto (assets/fotos/, assets/aktivitaeten/,
assets/kulinarik/) eine zusaetzliche "-450w"-Version mit max. 450px Breite,
fuer den Einsatz per srcset auf mobilen Geraeten (siehe img_srcset.py).

Aufruf:
    python3 generate_mobile_variants.py

Ueberspringt Dateien, die bereits eine aktuelle -450w-Variante haben
(Mobile-Datei neuer als Original), und Bilder die ohnehin schon <=450px
breit sind.
"""
import os
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"
MOBILE_MAXW = 450
MOBILE_QUALITY = 80
CONTENT_DIRS = ["assets/fotos", "assets/aktivitaeten", "assets/kulinarik"]
SUFFIX = "-450w"


def find_source_images():
    for content_dir in CONTENT_DIRS:
        abs_dir = os.path.join(BASE, content_dir)
        for root, dirs, files in os.walk(abs_dir):
            for fn in files:
                if fn.startswith("._"):
                    continue
                if not fn.lower().endswith((".jpg", ".jpeg")):
                    continue
                if SUFFIX in fn:
                    continue
                yield os.path.join(root, fn)


def main():
    created, skipped_small, skipped_uptodate, errors = 0, 0, 0, 0
    total_new_size = 0

    for src in find_source_images():
        stem, ext = os.path.splitext(src)
        dst = f"{stem}{SUFFIX}{ext}"

        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skipped_uptodate += 1
            continue

        try:
            im = Image.open(src)
            w, h = im.size
            if w <= MOBILE_MAXW:
                skipped_small += 1
                continue
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            nh = round(h * MOBILE_MAXW / w)
            im = im.resize((MOBILE_MAXW, nh), Image.LANCZOS)
            im.save(dst, "JPEG", quality=MOBILE_QUALITY, optimize=True)
            total_new_size += os.path.getsize(dst)
            created += 1
        except Exception as e:
            print(f"FEHLER bei {src}: {e}")
            errors += 1

    print(
        f"\n{created} Mobile-Varianten erstellt "
        f"({total_new_size / 1024 / 1024:.1f} MB neu), "
        f"{skipped_small} bereits <=450px, "
        f"{skipped_uptodate} bereits aktuell, "
        f"{errors} Fehler."
    )


if __name__ == "__main__":
    main()
