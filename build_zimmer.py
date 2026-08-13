# -*- coding: utf-8 -*-
"""
CMS-Rebuild-Skript fuer Zimmer-Uebersicht + die 4 Zimmerkategorie-Seiten,
alle 3 Sprachen (de/it/en).

Liest content/zimmer.json und baut daraus:
  {lang}/zimmer.html                aus zimmer.template.html
  {lang}/zimmer-{slug}.html  (x4)   aus zimmer-room.template.html

Aufruf:
    python3 build_zimmer.py
"""
import json

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/zimmer.json", encoding="utf-8") as f:
    ALL = json.load(f)

# Anfrage-Ueberschrift auf der Detailseite: title-abhaengiges Muster, pro
# Sprache unterschiedlich aufgebaut (Suffix bei DE, Praefix bei IT/EN).
ANFRAGE_TPL = {
    "de": "{title} anfragen",
    "it": "Richiedi: {title}",
    "en": "Enquire: {title}",
}

# Preiszeile auf den Zimmer-Karten (Uebersicht) - sprachspezifischer Satzbau
# UND Symbolreihenfolge (DE/IT "63 €", EN "€63").
CARD_PRICE_TPL = {
    "de": "ab <strong>{price} €</strong> p. P. &amp; Nacht inkl. Frühstück",
    "it": "da <strong>{price} €</strong> a persona &amp; notte, colazione inclusa",
    "en": "from <strong>€{price}</strong> p.p. &amp; night incl. breakfast",
}

# aria-label-Wort fuer die Slideshow-Punkte auf der Uebersicht ("Bild 1" /
# "Immagine 1" / "Image 1") - im Original korrekt pro Sprache uebersetzt.
SLIDE_WORD = {"de": "Bild", "it": "Immagine", "en": "Image"}


def build_room_cards_fragment(c, lang):
    cards = []
    for room in c["rooms"]:
        idx = cards_index(c, room)
        price_line = CARD_PRICE_TPL[lang].format(price=room["price"])
        # "garten" hat auf der Karte einen bewusst gekuerzten Titel (Platzgrund) -
        # ueberall sonst (Bild-Alt, Detailseite, Slideshow, verwandte Zimmer)
        # steht der volle Titel.
        card_title = room.get("card_title", room["title"])
        cards.append(
            '      <div class="room-card">\n'
            f'        <a href="zimmer-{room["slug"]}.html" class="room-card__img" style="display:block;"><img src="{room["image"]}" alt="{room["title"]}" data-cms="rooms.{idx}.image"></a>\n'
            '        <div class="room-card__body">\n'
            f'          <h3><a href="zimmer-{room["slug"]}.html" style="color:inherit; text-decoration:none;" data-cms="rooms.{idx}.card_title">{card_title}</a></h3>\n'
            f'          <p data-cms="rooms.{idx}.teaser">{room["teaser"]}</p>\n'
            f'          <div class="room-card__amenities">{room["amenities_html"]}\n          </div>\n'
            f'          <div class="room-card__price">{price_line}</div>\n'
            f'          <a href="zimmer-{room["slug"]}.html" class="btn btn--dark" style="align-self:flex-start;">{c["card_cta_label"]}</a>\n'
            '        </div>\n'
            '      </div>'
        )
    return '<div class="grid-4">\n' + "\n".join(cards) + '\n    </div>'


def cards_index(c, room):
    return c["rooms"].index(room)


def build_slideshow_fragment(c, lang):
    slides = []
    dots = []
    word = SLIDE_WORD[lang]
    images = c.get("slideshow_images") or [room["image"] for room in c["rooms"]]
    for i, image in enumerate(images):
        active = " is-active" if i == 0 else ""
        slides.append(f'  <div class="room-slideshow__slide{active}"><img src="{image}" alt="{c["slideshow_heading"]}"></div>')
        dots.append(f'    <button class="room-slideshow__dot{active}" data-slide="{i}" aria-label="{word} {i+1}"></button>')
    body = (
        '<section class="room-slideshow" id="roomSlideshow">\n'
        + "\n".join(slides) + "\n"
        + '  <div class="room-slideshow__caption">\n'
        '    <div class="wrap">\n'
        f'      <span class="eyebrow" style="color:var(--sand);" data-cms="slideshow_eyebrow">{c["slideshow_eyebrow"]}</span>\n'
        f'      <h2 style="color:var(--white); margin-bottom:0;" data-cms="slideshow_heading">{c["slideshow_heading"]}</h2>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="room-slideshow__dots">\n'
        + "\n".join(dots) + "\n"
        '  </div>\n'
        '</section>'
    )
    return body


def build_gallery_fragment(room):
    slides = [f'    <div class="room-gallery__slide"><img src="{img}" alt="{room["title"]}" draggable="false"></div>' for img in room["gallery"]]
    dots = [f'    <button class="{"is-active" if i == 0 else ""}" data-slide="{i}" aria-label="Bild {i+1}"></button>' for i in range(len(room["gallery"]))]
    return (
        '<div class="room-gallery" id="roomGallery">\n' + "\n".join(slides) + "\n  </div>\n"
        '  <div class="room-gallery-dots" id="roomGalleryDots">\n' + "\n".join(dots) + "\n  </div>"
    )


def build_related_rooms_fragment(c, current_slug):
    others = [r for r in c["rooms"] if r["slug"] != current_slug]
    cards = []
    dots = []
    for i, room in enumerate(others):
        cards.append(
            f'<div class="related-room-card"><a href="zimmer-{room["slug"]}.html" class="related-room-card__link">'
            f'<div class="img-frame"><img src="{room["image"]}" alt="{room["title"]}"></div><h4>{room["title"]}</h4></a>'
            f'<a href="zimmer-{room["slug"]}.html" class="related-room-card__cta btn btn--dark">{c["card_cta_label"]}</a></div>'
        )
        active = " is-active" if i == 0 else ""
        dots.append(f'<button class="{active.strip()}" data-slide="{i}" aria-label="{room["title"]}"></button>')
    return (
        '<div class="related-rooms-grid" id="relatedRoomsSlider">\n      ' + "".join(cards) + '\n    </div>\n'
        '    <div class="room-gallery-dots related-rooms-dots" id="relatedRoomsDots">\n      ' + "".join(dots) + '\n    </div>'
    )


def build_overview(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/zimmer.template.html", encoding="utf-8") as f:
        html = f.read()

    fragments = {
        "{{FRAGMENT_ROOM_CARDS}}": build_room_cards_fragment(c, lang),
        "{{FRAGMENT_ROOM_SLIDESHOW}}": build_slideshow_fragment(c, lang),
    }
    for token, value in fragments.items():
        html = html.replace(token, value)

    scalars = {
        "{{meta_title}}": c["meta_title"],
        "{{meta_description}}": c["meta_description"],
        "{{hero_heading}}": c["hero_heading"],
        "{{hero_text}}": c["hero_text"],
        "{{overview_heading}}": c["overview_heading"],
        "{{cta_heading}}": c["cta_heading"],
        "{{cta_text}}": c["cta_text"],
        "{{cta_label}}": c["cta_label"],
    }
    for token, value in scalars.items():
        html = html.replace(token, value)

    with open(BASE + f"{lang}/zimmer.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] zimmer.html neu gebaut.")


def build_room_pages(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/zimmer-room.template.html", encoding="utf-8") as f:
        template = f.read()

    for room in c["rooms"]:
        html = template
        fragments = {
            "{{FRAGMENT_GALLERY}}": build_gallery_fragment(room),
            "{{FRAGMENT_RELATED_ROOMS}}": build_related_rooms_fragment(c, room["slug"]),
        }
        for token, value in fragments.items():
            html = html.replace(token, value)

        scalars = {
            "{{title}}": room["title"],
            "{{detail_meta_description}}": room["detail_meta_description"],
            "{{slug}}": room["slug"],
            "{{image}}": room["image"],
            "{{room_category_eyebrow}}": c["room_category_eyebrow"],
            "{{lede}}": room["lede"],
            "{{price}}": room["price"],
            "{{gallery_eyebrow}}": c["gallery_eyebrow"],
            "{{anfrage_heading}}": ANFRAGE_TPL[lang].format(title=room["title"]),
            "{{related_heading}}": c["related_heading"],
        }
        for token, value in scalars.items():
            html = html.replace(token, value)

        out_path = BASE + f"{lang}/zimmer-{room['slug']}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[{lang}] zimmer-{room['slug']}.html neu gebaut.")


for lang in ["de", "it", "en"]:
    build_overview(lang)
    build_room_pages(lang)
