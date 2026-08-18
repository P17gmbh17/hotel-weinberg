# -*- coding: utf-8 -*-
"""
SEO-Nachbearbeitung fuer alle gebauten HTML-Seiten.

Laeuft NACH den sieben build_*.py-Skripten (siehe netlify.toml) und ergaenzt
in jeder Seite von de/, it/ und en/:

  1. <link rel="canonical">          - eine offizielle URL je Seite
  2. <link rel="alternate" hreflang> - Verknuepfung der drei Sprachversionen
  3. Schema.org JSON-LD              - Hotel / HotelRoom / BreadcrumbList
  4. verstecktes <h1>                - nur Startseite, die hat sonst keins
  5. loading/decoding/width/height   - an allen <img> (Ladezeit + Layoutruhe)

und schreibt anschliessend robots.txt und sitemap.xml ins Wurzelverzeichnis.

Warum als Nachbearbeitung und nicht in den einzelnen build_*.py-Skripten?
Weil es so ALLE Seiten erfasst - auch impressum.html, datenschutz.html und
cookie-einstellungen.html, die aus keinem Template gebaut werden - und weil
keine der 42 Template-Dateien angefasst werden muss.

Das Skript ist idempotent: der eingefuegte Block ist mit SEO:BEGIN/SEO:END
markiert und wird bei jedem Lauf ersetzt, nicht gedoppelt. Mehrfaches
Ausfuehren ist also gefahrlos.

Aufruf:
    python3 build_seo.py
"""
import hashlib
import json
import os
import re
import time
from datetime import date

from seo import (
    SITE_URL, LANGS, DEFAULT_LANG, HREFLANG, PAGES, NOINDEX, NAV_PAGES,
    HOTEL, AMENITIES, DESCRIPTION, HOME_H1, HOME_LABEL, BREADCRUMB_LABELS,
    OG_LOCALE, OG_IMAGE_SIZE, OG_IMAGE_DIR, OG_FALLBACK_IMAGE,
    page_url, asset_url,
)

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

BEGIN = "<!-- SEO:BEGIN (erzeugt von build_seo.py - nicht von Hand aendern) -->"
END = "<!-- SEO:END -->"

# <img>-Klassen, die oberhalb der Falz stehen und deshalb sofort laden muessen.
# Wuerden diese lazy geladen, verschlechtert sich der LCP-Wert (Zeit bis das
# groesste sichtbare Element da ist) - einer der drei Google Core Web Vitals.
EAGER_CLASSES = ("brand__lockup", "hero__icon", "hero__wordmark", "room-detail-hero__img")
# Das eigentliche Hauptbild der Zimmer-Detailseiten: hoechste Ladepriorität.
PRIORITY_CLASS = "room-detail-hero__img is-active"

_dim_cache = {}


def styles_version():
    """Cache-Buster fuer styles.css aus dem INHALT der Datei.

    Bisher stand in allen Templates eine fest eingetippte Zahl
    (styles.css?v=1787058302), die nie mitgewachsen ist - nach einer
    CSS-Aenderung lieferte Safari deshalb hartnaeckig die alte Datei aus.
    Jetzt wird der Wert bei jedem Build aus dem Dateiinhalt berechnet:
    aendert sich das CSS, aendert sich die Zahl automatisch; aendert es sich
    nicht, bleibt sie gleich und der Browser-Cache greift weiter.
    """
    try:
        with open(BASE + "assets/styles.css", "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:10]
    except OSError:
        return None


def img_dimensions(abs_path):
    """(Breite, Hoehe) eines Bildes, oder None.

    Mit zwei Wiederholversuchen: liegt das Projekt auf einer externen Platte,
    schlaegt ein Lesezugriff gelegentlich sporadisch fehl, obwohl die Datei
    einwandfrei da ist. Ohne Retry fehlten dadurch bei einzelnen, jedes Mal
    anderen Bildern die width/height-Angaben."""
    if abs_path in _dim_cache:
        return _dim_cache[abs_path]
    if not os.path.exists(abs_path):
        _dim_cache[abs_path] = None
        return None

    result = None
    for attempt in range(3):
        try:
            from PIL import Image
            with Image.open(abs_path) as im:
                result = im.size
            break
        except Exception:
            if attempt == 2:
                print(f"  Warnung: Masse von {abs_path} nicht lesbar")
            else:
                time.sleep(0.2)
    _dim_cache[abs_path] = result
    return result


# ---------------------------------------------------------------------------
# 1-3 · <head>-Block
# ---------------------------------------------------------------------------
def build_head_block(lang, filename, title, full_title, description, og_image_rel):
    """title = kurzer Seitenname (fuer Brotkrumen/Schema),
    full_title = vollstaendiger <title> (fuer die Link-Vorschau)."""
    lines = [BEGIN]

    # --- canonical ---------------------------------------------------------
    lines.append(f'<link rel="canonical" href="{page_url(lang, filename)}">')

    # --- hreflang ----------------------------------------------------------
    # Jede Seite verweist auf ALLE Sprachversionen inklusive sich selbst -
    # das verlangt Google ausdruecklich (die Verweise muessen gegenseitig sein).
    for other in LANGS:
        lines.append(
            f'<link rel="alternate" hreflang="{HREFLANG[other]}" '
            f'href="{page_url(other, filename)}">'
        )
    lines.append(
        f'<link rel="alternate" hreflang="x-default" '
        f'href="{page_url(DEFAULT_LANG, filename)}">'
    )

    if filename in NOINDEX:
        lines.append('<meta name="robots" content="noindex, follow">')

    # --- Link-Vorschau -----------------------------------------------------
    lines.extend(og_block(lang, filename, full_title or title, description, og_image_rel))

    # --- JSON-LD -----------------------------------------------------------
    for block in build_jsonld(lang, filename, title):
        lines.append(
            '<script type="application/ld+json">'
            + json.dumps(block, ensure_ascii=False, separators=(",", ":"))
            + "</script>"
        )

    lines.append(END)
    return "\n".join(lines)


def postal_address():
    return {
        "@type": "PostalAddress",
        "streetAddress": HOTEL["street"],
        "postalCode": HOTEL["postal_code"],
        "addressLocality": HOTEL["city"],
        "addressRegion": HOTEL["region"],
        "addressCountry": HOTEL["country"],
    }


def hotel_node(lang):
    node = {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "@id": f"{SITE_URL}/#hotel",
        "name": HOTEL["name"],
        "description": DESCRIPTION[lang],
        "url": page_url(lang, "index.html"),
        "telephone": HOTEL["phone"],
        "email": HOTEL["email"],
        "address": postal_address(),
        "image": asset_url(HOTEL["image"]),
        "priceRange": HOTEL["price_range"],
        "availableLanguage": HOTEL["languages"],
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": name, "value": value}
            for name, value in AMENITIES
        ],
    }
    if HOTEL.get("star_rating"):
        node["starRating"] = {
            "@type": "Rating",
            "ratingValue": HOTEL["star_rating"],
        }
    # Geo nur ausgeben, wenn echte Koordinaten hinterlegt sind - eine erfundene
    # Koordinate waere schlimmer als gar keine.
    if HOTEL.get("latitude") is not None and HOTEL.get("longitude") is not None:
        node["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": HOTEL["latitude"],
            "longitude": HOTEL["longitude"],
        }
    return node


def room_node(lang, filename, title):
    """HotelRoom fuer die vier Zimmer-Detailseiten."""
    return {
        "@context": "https://schema.org",
        "@type": "HotelRoom",
        "name": title,
        "url": page_url(lang, filename),
        "containedInPlace": {"@type": "Hotel", "@id": f"{SITE_URL}/#hotel"},
        "bed": {"@type": "BedDetails", "numberOfBeds": 1 if "einzel" in filename else 2},
        "occupancy": {
            "@type": "QuantitativeValue",
            "maxValue": 1 if "einzel" in filename else 2,
            "unitCode": "C62",
        },
        "offers": {
            "@type": "Offer",
            "price": HOTEL["price_from"],
            "priceCurrency": HOTEL["currency"],
            "availability": "https://schema.org/InStock",
            "url": page_url(lang, filename),
        },
    }


def breadcrumb_node(lang, filename, title):
    """Brotkrumen-Pfad. Zimmer-Detailseiten haengen unter zimmer.html."""
    items = [(HOME_LABEL[lang], page_url(lang, "index.html"))]

    if filename.startswith("zimmer-"):
        items.append((BREADCRUMB_LABELS[lang].get("zimmer.html", "Zimmer"),
                      page_url(lang, "zimmer.html")))

    label = BREADCRUMB_LABELS[lang].get(filename) or title
    items.append((label, page_url(lang, filename)))

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }


def build_jsonld(lang, filename, title):
    blocks = []
    if filename == "index.html":
        blocks.append(hotel_node(lang))
    else:
        if filename.startswith("zimmer-"):
            blocks.append(room_node(lang, filename, title))
        blocks.append(breadcrumb_node(lang, filename, title))
    return blocks


# ---------------------------------------------------------------------------
# 4 · Verstecktes <h1> auf der Startseite
# ---------------------------------------------------------------------------
def ensure_home_h1(html, lang):
    if re.search(r"<h1[\s>]", html):
        return html, False
    heading = f'<h1 class="visually-hidden">{HOME_H1[lang]}</h1>'
    # Direkt hinter das oeffnende <body>, damit es die erste Ueberschrift im
    # Dokument ist - das erwartet Google so.
    new = re.sub(r"(<body[^>]*>)", r"\1\n" + heading, html, count=1)
    return new, new != html


# ---------------------------------------------------------------------------
# 5 · Bild-Attribute
# ---------------------------------------------------------------------------
def enhance_images(html, page_dir):
    """Ergaenzt loading/decoding/width/height an <img>-Tags.

    Vorhandene Attribute werden nie ueberschrieben - handgesetzte Werte
    behalten also immer Vorrang."""
    stats = {"lazy": 0, "eager": 0, "dims": 0}

    def repl(m):
        tag = m.group(0)
        attrs = m.group(1)

        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1) if cls else ""
        is_eager = any(c in cls for c in EAGER_CLASSES)

        add = ""
        if "loading=" not in attrs:
            if is_eager:
                add += ' loading="eager"'
                stats["eager"] += 1
                if PRIORITY_CLASS in cls and "fetchpriority=" not in attrs:
                    add += ' fetchpriority="high"'
            else:
                add += ' loading="lazy"'
                stats["lazy"] += 1
        if "decoding=" not in attrs:
            add += ' decoding="async"'

        # width/height verhindern das Springen des Layouts beim Nachladen (CLS).
        if "width=" not in attrs and "height=" not in attrs:
            src = re.search(r'\ssrc="([^"]+)"', attrs)
            if src and not src.group(1).startswith(("http", "data:")):
                abs_path = os.path.normpath(os.path.join(page_dir, src.group(1)))
                dims = img_dimensions(abs_path)
                if dims:
                    add += f' width="{dims[0]}" height="{dims[1]}"'
                    stats["dims"] += 1

        if not add:
            return tag
        return "<img" + attrs + add + ">"

    html = re.sub(r"<img((?:[^>\"]|\"[^\"]*\")*?)>", repl, html)
    return html, stats


# ---------------------------------------------------------------------------
# 6 · Link-Vorschau (Open Graph / Twitter Cards)
# ---------------------------------------------------------------------------
def ensure_og_image(hero_rel, page_dir):
    """Erzeugt aus dem Kopfbild einer Seite ein 1200x630-Vorschaubild.

    Wird ein Link per WhatsApp, Facebook oder iMessage geteilt, zeigen diese
    Dienste dieses Bild an. Sie erwarten das Seitenverhaeltnis 1.91:1 - die
    Originalfotos sind 3:2 oder hochkant, wuerden also unschoen beschnitten
    dargestellt. Deshalb hier einmalig ein passender Mittenausschnitt.

    Rueckgabe: Pfad relativ zum Projektwurzelverzeichnis, oder None.
    """
    if not hero_rel:
        return None
    src_norm = os.path.normpath(os.path.join(page_dir, hero_rel))
    if not os.path.exists(src_norm):
        return None

    stem = os.path.splitext(os.path.basename(hero_rel))[0]
    # Hochformat-Varianten nicht als Quelle nehmen, das gaebe einen zu engen
    # Ausschnitt - stattdessen die Querformat-Fassung.
    stem = stem.replace("-9-16", "").replace("-450w", "").replace("-900w", "")
    out_rel = f"{OG_IMAGE_DIR}/{stem}-og.jpg"
    out_abs = BASE + out_rel

    if os.path.exists(out_abs) and os.path.getmtime(out_abs) >= os.path.getmtime(src_norm):
        return out_rel

    try:
        from PIL import Image, ImageOps
        with Image.open(src_norm) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode != "RGB":
                im = im.convert("RGB")
            # Mittenausschnitt im Zielverhaeltnis, dann auf Zielgroesse
            im = ImageOps.fit(im, OG_IMAGE_SIZE, Image.LANCZOS, centering=(0.5, 0.4))
            os.makedirs(os.path.dirname(out_abs), exist_ok=True)
            im.save(out_abs, "JPEG", quality=84, optimize=True, progressive=True)
    except Exception as e:
        print(f"  Warnung: Vorschaubild aus {hero_rel} fehlgeschlagen: {e}")
        return None
    return out_rel


def og_block(lang, filename, title, description, og_image_rel):
    """Meta-Angaben fuer die Link-Vorschau."""
    image = asset_url(og_image_rel or OG_FALLBACK_IMAGE)
    url = page_url(lang, filename)
    lines = [
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{HOTEL["name"]}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        f'<meta property="og:image:width" content="{OG_IMAGE_SIZE[0]}">',
        f'<meta property="og:image:height" content="{OG_IMAGE_SIZE[1]}">',
        f'<meta property="og:image:alt" content="{esc(title)}">',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">',
    ]
    for other in LANGS:
        if other != lang:
            lines.append(
                f'<meta property="og:locale:alternate" content="{OG_LOCALE[other]}">'
            )
    lines += [
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    return lines


def esc(text):
    """Fuer Attributwerte absichern."""
    return (text or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


# ---------------------------------------------------------------------------
# 7 · Hintergrund-Vorausladen der uebrigen Seiten
# ---------------------------------------------------------------------------
HERO_RE = re.compile(
    r'<(?:section|div)[^>]*class="(?:[^"]*\s)?'
    r'(?:hero|subpage-hero|page-hero|room-detail-hero)(?:\s[^"]*)?"'
)


def hero_assets(html, page_dir):
    """Findet das Kopfbild einer Seite, getrennt nach Desktop und Mobil.

    Die Kopfbereiche sind unterschiedlich aufgebaut: mal ein Hintergrundvideo
    mit Poster-Bild (je eines fuer Quer- und Hochformat), mal ein normales
    <img>. Zurueck kommt (desktop, mobil); ein Wert kann None sein.
    """
    m = HERO_RE.search(html)
    if not m:
        return None, None
    seg = html[m.start():m.start() + 4000]

    desktop = mobile = None

    # Fall 1: Hintergrundvideos mit Poster-Bildern. Die Poster sind das,
    # was der Gast als Erstes sieht (die Videos selbst haben preload="none").
    for tag in re.finditer(r"<video([^>]*)>", seg):
        attrs = tag.group(1)
        poster = re.search(r'poster="([^"]+)"', attrs)
        if not poster:
            continue
        if "--mobile" in attrs or "9-16" in poster.group(1):
            mobile = mobile or poster.group(1)
        else:
            desktop = desktop or poster.group(1)

    # Fall 2: normales Kopfbild. Logos ueberspringen.
    if not desktop:
        for tag in re.finditer(r"<img([^>]*)>", seg):
            src = re.search(r'\ssrc="([^"]+)"', tag.group(1))
            if not src or "/logo/" in src.group(1):
                continue
            desktop = src.group(1)
            break

    # Fuers Handy die kleine Variante nehmen, falls vorhanden - sonst lieber
    # gar nichts vorausladen, als ueber Mobilfunk eine 1600px-Datei zu ziehen,
    # die nie in dieser Groesse gebraucht wird.
    if not mobile and desktop:
        stem, ext = os.path.splitext(desktop)
        candidate = f"{stem}-450w{ext}"
        if os.path.exists(os.path.normpath(os.path.join(page_dir, candidate))):
            mobile = candidate

    return desktop, mobile


def collect_hero_map():
    """{(lang, seite): (desktop, mobil)} fuer alle Seiten.

    Wird zweifach gebraucht: fuer das Vorausladen (nur Navigationsseiten) und
    als Quelle der Vorschaubilder (alle Seiten)."""
    hero_map = {}
    for lang in LANGS:
        for fn in PAGES:
            path = BASE + f"{lang}/{fn}"
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                html = f.read()
            hero_map[(lang, fn)] = hero_assets(html, os.path.dirname(path))
    return hero_map


def prefetch_block(lang, filename, hero_map):
    """JSON-Manifest + Skript-Einbindung fuer die aktuelle Seite.

    Enthaelt immer nur die ANDEREN Navigationsseiten derselben Sprache -
    die aktuelle Seite ist ja schon geladen, und ein Gast auf /de/ wechselt
    nicht mitten im Besuch nach /it/.
    """
    desktop, mobile, docs = [], [], []
    for fn in NAV_PAGES:
        if fn == filename:
            continue
        assets = hero_map.get((lang, fn))
        if assets is None:
            continue
        docs.append(fn)
        if assets[0]:
            desktop.append(assets[0])
        if assets[1]:
            mobile.append(assets[1])

    if not docs:
        return ""

    manifest = {"desktop": desktop, "mobile": mobile, "docs": docs}
    return (
        '<script type="application/json" id="prefetch-manifest">'
        + json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
        + "</script>\n"
        + '<script src="../assets/prefetch.js" defer></script>'
    )


# ---------------------------------------------------------------------------
# robots.txt / sitemap.xml
# ---------------------------------------------------------------------------
def write_robots():
    content = (
        "# Hotel Weinberg\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# Reine Verwaltungsoberflaeche, gehoert nicht in den Suchindex\n"
        "Disallow: /admin/\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open(BASE + "robots.txt", "w", encoding="utf-8") as f:
        f.write(content)
    return "robots.txt"


def write_sitemap():
    today = date.today().isoformat()
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    count = 0
    for filename, (priority, changefreq) in PAGES.items():
        if filename in NOINDEX:
            continue
        for lang in LANGS:
            if not os.path.exists(BASE + f"{lang}/{filename}"):
                continue
            out.append("  <url>")
            out.append(f"    <loc>{page_url(lang, filename)}</loc>")
            # Die Sprachalternativen gehoeren laut Google auch in die Sitemap.
            for other in LANGS:
                out.append(
                    f'    <xhtml:link rel="alternate" hreflang="{HREFLANG[other]}" '
                    f'href="{page_url(other, filename)}"/>'
                )
            out.append(
                f'    <xhtml:link rel="alternate" hreflang="x-default" '
                f'href="{page_url(DEFAULT_LANG, filename)}"/>'
            )
            out.append(f"    <lastmod>{today}</lastmod>")
            out.append(f"    <changefreq>{changefreq}</changefreq>")
            out.append(f"    <priority>{priority}</priority>")
            out.append("  </url>")
            count += 1
    out.append("</urlset>")
    with open(BASE + "sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return count


# ---------------------------------------------------------------------------
PREFETCH_BEGIN = "<!-- PREFETCH:BEGIN (erzeugt von build_seo.py) -->"
PREFETCH_END = "<!-- PREFETCH:END -->"


def process_page(lang, filename, hero_map):
    path = BASE + f"{lang}/{filename}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    full_title = ""
    # Achtung: auf der Startseite steht <title data-cms="..."> - das Muster
    # muss Attribute zulassen, sonst bleibt der Titel der Link-Vorschau leer.
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    if m:
        full_title = m.group(1).strip()
    # Suffix " | Hotel Weinberg" fuer die Brotkrumen abschneiden
    title = re.split(r"\s*[|·]\s*", full_title)[0] if full_title else ""

    m = re.search(r'<meta name="description" content="([^"]*)"', html)
    description = m.group(1) if m else DESCRIPTION[lang]

    # Vorschaubild aus dem Kopfbild dieser Seite
    hero_desktop = (hero_map.get((lang, filename)) or (None, None))[0]
    og_image_rel = ensure_og_image(hero_desktop, os.path.dirname(path))

    # alten Block entfernen (Idempotenz)
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)

    block = build_head_block(lang, filename, title, full_title, description, og_image_rel)
    html = html.replace("</head>", block + "\n</head>", 1)

    added_h1 = False
    if filename == "index.html":
        html, added_h1 = ensure_home_h1(html, lang)

    html, stats = enhance_images(html, os.path.dirname(path))

    # Hintergrund-Vorausladen (alter Block raus, neuer rein)
    html = re.sub(
        re.escape(PREFETCH_BEGIN) + r".*?" + re.escape(PREFETCH_END) + r"\n?",
        "", html, flags=re.S,
    )
    pf = prefetch_block(lang, filename, hero_map)
    if pf and "</body>" in html:
        html = html.replace(
            "</body>",
            PREFETCH_BEGIN + "\n" + pf + "\n" + PREFETCH_END + "\n</body>", 1,
        )

    version = styles_version()
    if version:
        html = re.sub(r"(styles\.css)\?v=[^\"']*", r"\1?v=" + version, html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return stats, added_h1


def main():
    total = {"lazy": 0, "eager": 0, "dims": 0}
    pages = 0
    h1s = 0

    # Vorab einsammeln, welche Seite welches Kopfbild hat - das braucht jede
    # Seite, um die jeweils anderen vorausladen zu koennen.
    hero_map = collect_hero_map()
    missing_hero = [f"{l}/{f}" for (l, f), a in hero_map.items() if not a[0]]
    if missing_hero:
        print("  Hinweis: kein Kopfbild erkannt bei " + ", ".join(missing_hero))

    for lang in LANGS:
        for filename in PAGES:
            if not os.path.exists(BASE + f"{lang}/{filename}"):
                print(f"  Hinweis: {lang}/{filename} existiert nicht - uebersprungen")
                continue
            stats, added_h1 = process_page(lang, filename, hero_map)
            for k in total:
                total[k] += stats[k]
            pages += 1
            h1s += 1 if added_h1 else 0

    urls = write_sitemap()
    write_robots()

    print(
        f"\n{pages} Seiten mit canonical + hreflang + JSON-LD versehen.\n"
        f"{h1s} verstecktes <h1> ergaenzt (Startseiten).\n"
        f"Bilder: {total['lazy']} lazy, {total['eager']} eager (oberhalb der Falz), "
        f"{total['dims']} mit width/height.\n"
        f"styles.css-Cache-Buster: ?v={styles_version()}\n"
        f"Vorausladen aktiv fuer {len(NAV_PAGES)} Navigationsseiten je Sprache.\n"
        f"sitemap.xml mit {urls} URLs und robots.txt geschrieben."
    )


if __name__ == "__main__":
    main()
