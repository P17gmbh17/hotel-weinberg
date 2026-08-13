# -*- coding: utf-8 -*-
"""
Baut {lang}/philosophie.html aus content/philosophie.json + {lang}/philosophie.template.html
"""
import json

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/philosophie.json", encoding="utf-8") as f:
    ALL = json.load(f)

# Statische, nicht-editierbare UI-Strings (Pfeil-Buttons des Slider) - je Sprache fix.
ARROW_LABELS = {
    "de": {"prev": "Zurück", "next": "Weiter"},
    "it": {"prev": "Indietro", "next": "Avanti"},
    "en": {"prev": "Previous", "next": "Next"},
}

# Original-Inline-Style des Slider-Wrappers ist je Sprache unterschiedlich
# (DE/IT: margin-bottom, EN: margin-top - bestehende Eigenheit der Live-Seite,
# 1:1 beibehalten statt "korrigiert").
SLIDER_MARGIN_STYLE = {
    "de": "margin-bottom:56px;",
    "it": "margin-bottom:56px;",
    "en": "margin-top:56px;",
}

# Amenity-Icons sind rein dekorativ und identisch in allen Sprachen (per Diff bestätigt).
AMENITY_ICONS = [
    '<svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M2 8c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0"/><path d="M2 14c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0"/><path d="M2 20c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M3 19 9 8l3.5 6L15 10l6 9H3z"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11"/><rect x="2" y="11" width="20" height="6" rx="2"/><circle cx="7" cy="17" r="1.6"/><circle cx="17" cy="17" r="1.6"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M12 2a6 6 0 0 1 6 6c0 3.5-2.6 6.4-4.6 8.2L14 22h-4l.6-5.8C8.6 14.4 6 11.5 6 8a6 6 0 0 1 6-6z"/><path d="M10 22h4"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M2 8.8a15.3 15.3 0 0 1 20 0"/><path d="M5 12.5a11 11 0 0 1 14 0"/><path d="M8.5 16a6 6 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/></svg>',
    '<svg viewBox="0 0 24 24"><circle cx="6" cy="8" r="1.6"/><circle cx="10.5" cy="5.3" r="1.6"/><circle cx="15" cy="5.6" r="1.6"/><circle cx="18.5" cy="9" r="1.6"/><path d="M12 12c-3.5 0-6 2-6 4.5S8 21 12 21s6-1.9 6-4.5S15.5 12 12 12z"/></svg>',
]


def build_team_fragment(team):
    parts = []
    for i, m in enumerate(team):
        parts.append(
            f'      <div class="team-portrait" data-portrait>\n'
            f'        <img src="{m["image"]}" alt="{m["alt"]}" data-cms="gastgeber.team.{i}.image">\n'
            f'        <span class="overlay"></span>\n'
            f'        <span class="name-script" data-cms="gastgeber.team.{i}.name">{m["name"]}</span>\n'
            f'      </div>'
        )
    return '<div class="team-portraits">\n' + "\n".join(parts) + "\n    </div>"


def build_slider_fragment(slider, lang):
    lbl = ARROW_LABELS[lang]
    parts = []
    for i, s in enumerate(slider):
        active = " is-active" if i == 0 else ""
        parts.append(
            f'      <div class="ausstattung-slider__slide{active}"><img src="{s["image"]}" alt="{s["alt"]}" data-cms="ausstattung.slider.{i}.image"></div>'
        )
    slides_html = "\n".join(parts)
    return (
        f'<div class="ausstattung-slider" id="ausstattungSlider" style="{SLIDER_MARGIN_STYLE[lang]}">\n'
        f'{slides_html}\n'
        f'      <button class="ausstattung-slider__arrow ausstattung-slider__arrow--prev" aria-label="{lbl["prev"]}"><svg viewBox="0 0 24 40"><polyline points="18,2 4,20 18,38"/></svg></button>\n'
        f'      <button class="ausstattung-slider__arrow ausstattung-slider__arrow--next" aria-label="{lbl["next"]}"><svg viewBox="0 0 24 40"><polyline points="6,2 20,20 6,38"/></svg></button>\n'
        '    </div>'
    )


def build_amenities_fragment(amenities):
    parts = []
    for i, (icon, text) in enumerate(zip(AMENITY_ICONS, amenities)):
        parts.append(
            f'      <li class="amenity-item">\n'
            f'        <span class="amenity-icon">{icon}</span>\n'
            f'        <span data-cms="ausstattung.amenities.{i}">{text}</span>\n'
            f'      </li>'
        )
    return '<ul class="amenity-list" style="max-width:820px;">\n' + "\n".join(parts) + "\n    </ul>"


def esc_attr(s):
    return s


def build(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/philosophie.template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{meta_title}}", c["meta_title"])
    html = html.replace("{{meta_description}}", c["meta_description"])
    html = html.replace("{{hero_heading}}", c["hero_heading"])
    html = html.replace("{{hero_text}}", c["hero_text"])

    g = c["geschichte"]
    html = html.replace("{{geschichte.eyebrow}}", g["eyebrow"])
    html = html.replace("{{geschichte.heading}}", g["heading"])
    html = html.replace("{{geschichte.lede}}", g["lede"])
    html = html.replace("{{geschichte.body}}", g["body"])
    html = html.replace("{{geschichte.image}}", g["image"])
    html = html.replace("{{geschichte.alt}}", g["alt"])

    gg = c["gastgeber"]
    html = html.replace("{{gastgeber.eyebrow}}", gg["eyebrow"])
    html = html.replace("{{gastgeber.heading}}", gg["heading"])
    html = html.replace("{{gastgeber.lede}}", gg["lede"])
    html = html.replace("{{FRAGMENT_TEAM}}", build_team_fragment(gg["team"]), 1)

    ph = c["philosophie"]
    html = html.replace("{{philosophie.badge}}", ph["badge"])
    html = html.replace("{{philosophie.heading}}", ph["heading"])
    html = html.replace("{{philosophie.lede}}", ph["lede"])

    au = c["ausstattung"]
    html = html.replace("{{ausstattung.eyebrow}}", au["eyebrow"])
    html = html.replace("{{ausstattung.heading}}", au["heading"])
    html = html.replace("{{FRAGMENT_SLIDER}}", build_slider_fragment(au["slider"], lang), 1)
    html = html.replace("{{FRAGMENT_AMENITIES}}", build_amenities_fragment(au["amenities"]), 1)

    pz = c["persoenlichkeit"]
    html = html.replace("{{persoenlichkeit.eyebrow}}", pz["eyebrow"])
    html = html.replace("{{persoenlichkeit.heading}}", pz["heading"])
    html = html.replace("{{persoenlichkeit.lede}}", pz["lede"])
    html = html.replace("{{persoenlichkeit.body}}", pz["body"])
    html = html.replace("{{persoenlichkeit.image}}", pz["image"])
    html = html.replace("{{persoenlichkeit.alt}}", pz["alt"])

    gl = c["geniessen_link"]
    html = html.replace("{{geniessen_link.image}}", gl["image"])
    html = html.replace("{{geniessen_link.alt}}", gl["alt"])
    html = html.replace("{{geniessen_link.eyebrow}}", gl["eyebrow"])
    html = html.replace("{{geniessen_link.heading}}", gl["heading"])
    html = html.replace("{{geniessen_link.lede}}", gl["lede"])
    html = html.replace("{{geniessen_link.cta_label}}", gl["cta_label"])

    cb = c["cta_banner"]
    html = html.replace("{{cta_banner.heading}}", cb["heading"])
    html = html.replace("{{cta_banner.text}}", cb["text"])
    html = html.replace("{{cta_banner.cta_label_book}}", cb["cta_label_book"])
    html = html.replace("{{cta_banner.cta_label_contact}}", cb["cta_label_contact"])

    with open(BASE + f"{lang}/philosophie.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] philosophie.html geschrieben")


for lang in ["de", "it", "en"]:
    build(lang)
