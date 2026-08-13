# -*- coding: utf-8 -*-
"""
CMS-Rebuild-Skript fuer die Startseite, alle 3 Sprachen (de/it/en).

Liest content/index.json (i18n, ein File mit de/it/en-Keys - Decap CMS
"single_file"-Struktur) und setzt die Werte in {lang}/index.template.html
ein. Listenartige Bereiche werden pro Sprache als HTML/JS-Fragmente aus der
JSON-Struktur gebaut.

Aufruf:
    python3 build_index.py
"""
import json
import re
from urllib.parse import quote_plus

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/index.json", encoding="utf-8") as f:
    ALL = json.load(f)

PHONE_SVG = '<svg viewBox="0 0 24 24"><path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1.1-.3 1.2.4 2.5.6 3.8.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.9 21 3 13.1 3 3.9c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.6.6 3.8.1.4 0 .8-.3 1.1L6.6 10.8z"/></svg>'
MAIL_SVG = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M4 6.5l8 6 8-6"/></svg>'
MAPS_SVG = '<svg viewBox="0 0 24 24"><path d="M12 21s7-6.1 7-11.6C19 5.3 15.9 2 12 2S5 5.3 5 9.4C5 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.3"/></svg>'

STATIC = {
    "de": {
        "call_label": "Anrufen", "mail_label": "E-Mail schreiben", "maps_label": "Auf Google Maps ansehen",
        "mail_href_full": (
            "mailto:{email}?subject=Zimmeranfrage%20Hotel%20Weinberg&body=Liebe%20Familie%20Schrott%2C"
            "%0D%0A%0D%0Aich%20interessiere%20mich%20f%C3%BCr%20folgenden%20Aufenthalt%3A%0D%0A%0D%0A"
            "Anreise%3A%20%0D%0AAbreise%3A%20%0D%0AAnzahl%20Personen%3A%20%0D%0AZimmerkategorie%3A%20"
            "%0D%0A%0D%0AHerzliche%20Gr%C3%BC%C3%9Fe"
        ),
    },
    "it": {
        "call_label": "Chiama", "mail_label": "Scrivi un'email", "maps_label": "Vedi su Google Maps",
        "mail_href_full": (
            "mailto:{email}?subject=Richiesta%20camera%20Hotel%20Weinberg&body=Gentile%20Famiglia%20Schrott%2C"
            "%0D%0A%0D%0Asono%20interessato%2Fa%20al%20seguente%20soggiorno%3A%0D%0A%0D%0A"
            "Arrivo%3A%20%0D%0APartenza%3A%20%0D%0ANumero%20di%20persone%3A%20%0D%0ACategoria%20camera%3A%20"
            "%0D%0A%0D%0ACordiali%20saluti"
        ),
    },
    "en": {
        "call_label": "Call us", "mail_label": "Write an email", "maps_label": "View on Google Maps",
        "mail_href_full": (
            "mailto:{email}?subject=Room%20enquiry%20Hotel%20Weinberg&body=Dear%20Schrott%20family%2C"
            "%0D%0A%0D%0AI%20am%20interested%20in%20the%20following%20stay%3A%0D%0A%0D%0A"
            "Arrival%3A%20%0D%0ADeparture%3A%20%0D%0ANumber%20of%20guests%3A%20%0D%0ARoom%20category%3A%20"
            "%0D%0A%0D%0AKind%20regards"
        ),
    },
}


def js_str(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def build_lang(lang):
    c = ALL[lang]
    s = STATIC[lang]
    contact = c["contact"]
    phone_display = contact["phone_display"]
    phone_href = "tel:" + phone_display.replace(" ", "")
    email = contact["email"]
    street = contact["address_street"]
    zip_city = contact["address_zip_city"]
    city_only = re.sub(r"^\d+\s*", "", zip_city)
    maps_title = f"{street}, {city_only}"
    maps_query_text = f"Hotel Weinberg {street} {zip_city}".replace("/", " ")
    maps_href = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(maps_query_text)
    mail_href_full = s["mail_href_full"].format(email=email)

    def icons_block(indent):
        lines = [
            f'{indent}<a href="{phone_href}" aria-label="{s["call_label"]}" title="{phone_display}">{PHONE_SVG}</a>',
            f'{indent}<a href="{mail_href_full}" aria-label="{s["mail_label"]}" title="{email}">{MAIL_SVG}</a>',
            f'{indent}<a href="{maps_href}" target="_blank" rel="noopener" aria-label="{s["maps_label"]}" title="{maps_title}">{MAPS_SVG}</a>',
        ]
        return "\n".join(lines)

    nav_icons_fragment = '<span class="nav-icons">\n' + icons_block("        ") + '\n      </span>'
    mobile_icons_fragment = '<span class="mobile-action-bar__icons">\n' + icons_block("    ") + '\n  </span>'
    footer_contact_fragment = (
        '<ul>\n'
        f'          <li data-cms="contact.address_street">{street}</li>\n'
        f'          <li data-cms="contact.address_zip_city">{zip_city}</li>\n'
        f'          <li><a href="{phone_href}" data-cms="contact.phone_display">{phone_display}</a></li>\n'
        f'          <li><a href="mailto:{email}" data-cms="contact.email">{email}</a></li>\n'
        '        </ul>'
    )

    geniessen_imgs = c["geniessen"]["images"]
    frame_lines = [
        f'      <div class="img-frame" style="height:320px;"><img src="{img["image"]}" alt="{img["alt"]}" data-cms="geniessen.images.{i}.image"></div>'
        for i, img in enumerate(geniessen_imgs)
    ]
    geniessen_images_fragment = '<div class="grid-3 triptych" style="margin-top:40px;">\n' + "\n".join(frame_lines) + '\n    </div>'

    categories = c["aktivitaeten"]["categories"]
    filter_links = [
        f'      <a href="aktivitaeten.html?cat={cat["key"]}#filterBar" data-cms="aktivitaeten.categories.{i}.label">{cat["label"]}</a>'
        for i, cat in enumerate(categories)
    ]
    aktivitaeten_filter_fragment = '<div class="activities-teaser__filter">\n' + "\n".join(filter_links) + '\n    </div>'

    activity_data = {
        cat["key"]: {"label": cat["label"], "tips": [{"title": t["title"], "meta": t["meta"], "img": t["image"]} for t in cat["tips"]]}
        for cat in categories
    }
    activity_data_js = json.dumps(activity_data, ensure_ascii=False, indent=2)

    cards = c["kulinarik"]["cards"]
    card_blocks = [
        '      <a class="teaser-card" href="kulinarik.html">\n'
        f'        <img src="{card["image"]}" alt="{card["alt"]}" data-cms="kulinarik.cards.{i}.image">\n'
        f'        <span class="teaser-card__label" data-cms="kulinarik.cards.{i}.label">{card["label"]}</span>\n'
        '      </a>'
        for i, card in enumerate(cards)
    ]
    kulinarik_grid_fragment = '<div class="kulinarik-teaser-grid">\n' + "\n".join(card_blocks) + '\n    </div>'

    neuigkeiten_imgs = c["neuigkeiten"]["images"]
    neuigkeiten_slide_blocks = [
        f'    <div class="neuigkeiten-vslider__slide"><img src="{img["image"]}" alt="{img["alt"]}" data-cms="neuigkeiten.images.{i}.image"></div>'
        for i, img in enumerate(neuigkeiten_imgs)
    ]
    # Bilderliste verdoppeln, damit die CSS-Endlosschleife (translateY 0 -> -50%) nahtlos ist.
    neuigkeiten_images_fragment = (
        '<div class="neuigkeiten-vslider">\n'
        '  <div class="neuigkeiten-vslider__track">\n'
        + "\n".join(neuigkeiten_slide_blocks) + "\n"
        + "\n".join(neuigkeiten_slide_blocks) + "\n"
        '  </div>\n'
        '</div>'
    )

    with open(BASE + f"{lang}/index.template.html", encoding="utf-8") as f:
        html = f.read()

    fragments = {
        "{{FRAGMENT_NAV_ICONS}}": nav_icons_fragment,
        "{{FRAGMENT_MOBILE_ICONS}}": mobile_icons_fragment,
        "{{FRAGMENT_FOOTER_CONTACT}}": footer_contact_fragment,
        "{{FRAGMENT_GENIESSEN_IMAGES}}": geniessen_images_fragment,
        "{{FRAGMENT_AKTIVITAETEN_FILTER_NAV}}": aktivitaeten_filter_fragment,
        "{{FRAGMENT_ACTIVITY_DATA_JS}}": activity_data_js,
        "{{FRAGMENT_KULINARIK_GRID}}": kulinarik_grid_fragment,
        "{{FRAGMENT_NEUIGKEITEN_IMAGES}}": neuigkeiten_images_fragment,
    }
    for token, value in fragments.items():
        html = html.replace(token, value)

    scalars = {
        "{{meta_title}}": c["meta_title"],
        "{{meta_description}}": c["meta_description"],
        "{{cta_book_label}}": c["cta_book_label"],
        "{{cta_buchen_label}}": c["cta_buchen_label"],
        "{{hero_scroll_label}}": c["hero_scroll_label"],
        "{{hero_cta_secondary_label}}": c["hero_cta_secondary_label"],
        "{{willkommen.eyebrow}}": c["willkommen"]["eyebrow"],
        "{{willkommen.heading}}": c["willkommen"]["heading"],
        "{{willkommen.lede}}": c["willkommen"]["lede"],
        "{{willkommen.body}}": c["willkommen"]["body"],
        "{{willkommen.cta_label}}": c["willkommen"]["cta_label"],
        "{{willkommen.image}}": c["willkommen"]["image"],
        "{{zimmer.eyebrow}}": c["zimmer"]["eyebrow"],
        "{{zimmer.heading}}": c["zimmer"]["heading"],
        "{{zimmer.lede}}": c["zimmer"]["lede"],
        "{{zimmer.image}}": c["zimmer"]["image"],
        "{{zimmer.cta_label}}": c["zimmer"]["cta_label"],
        "{{geniessen.eyebrow}}": c["geniessen"]["eyebrow"],
        "{{geniessen.heading}}": c["geniessen"]["heading"],
        "{{geniessen.lede}}": c["geniessen"]["lede"],
        "{{geniessen.cta_label}}": c["geniessen"]["cta_label"],
        "{{aktivitaeten.background_image}}": c["aktivitaeten"]["background_image"],
        "{{aktivitaeten.eyebrow}}": c["aktivitaeten"]["eyebrow"],
        "{{aktivitaeten.heading}}": c["aktivitaeten"]["heading"],
        "{{aktivitaeten.lede}}": c["aktivitaeten"]["lede"],
        "{{aktivitaeten.cta_label}}": c["aktivitaeten"]["cta_label"],
        "{{kulinarik.eyebrow}}": c["kulinarik"]["eyebrow"],
        "{{kulinarik.heading}}": c["kulinarik"]["heading"],
        "{{kulinarik.lede}}": c["kulinarik"]["lede"],
        "{{kulinarik.cta_label}}": c["kulinarik"]["cta_label"],
        "{{neuigkeiten.eyebrow}}": c["neuigkeiten"]["eyebrow"],
        "{{neuigkeiten.heading}}": c["neuigkeiten"]["heading"],
        "{{neuigkeiten.lede}}": c["neuigkeiten"]["lede"],
        "{{neuigkeiten.body}}": c["neuigkeiten"]["body"],
        "{{cta_banner.heading}}": c["cta_banner"]["heading"],
        "{{cta_banner.text}}": c["cta_banner"]["text"],
        "{{footer.intro}}": c["footer"]["intro"],
        "{{footer.copyright}}": c["footer"]["copyright"],
    }
    for token, value in scalars.items():
        html = html.replace(token, value)

    with open(BASE + f"{lang}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] index.html neu gebaut.")


for lang in ["de", "it", "en"]:
    build_lang(lang)
