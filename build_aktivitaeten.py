# -*- coding: utf-8 -*-
"""
CMS-Rebuild-Skript fuer die Aktivitaeten-Seite, alle 3 Sprachen (de/it/en).

Liest content/aktivitaeten.json und baut daraus {lang}/aktivitaeten.html
aus {lang}/aktivitaeten.template.html.

Aufruf:
    python3 build_aktivitaeten.py
"""
import json
import os

from img_srcset import srcset_attr

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/aktivitaeten.json", encoding="utf-8") as f:
    ALL = json.load(f)

# Rein dekorative Werte je Kapitel (Position/Groesse des Palmen-Wasserzeichens,
# links/rechts-Ausrichtung des Textblocks) - identisch in allen 3 Sprachen,
# nicht im CMS editierbar, deshalb hier fest hinterlegt statt in content/*.json.
CHAPTER_DECOR = [
    {"right": False, "palm": "width:320px; top:-50px; right:-70px;"},
    {"right": True, "palm": "width:280px; bottom:-50px; left:-60px;"},
    {"right": False, "palm": "width:300px; top:-40px; right:-60px;"},
    {"right": True, "palm": "width:280px; bottom:-40px; left:-70px;"},
    {"right": False, "palm": "width:320px; top:-50px; right:-70px;"},
    {"right": True, "palm": "width:280px; bottom:-50px; left:-60px;"},
]

# HTML-Kommentar-Beschriftungen je Station - rein intern/unsichtbar, im
# Original NICHT konsistent mit den sichtbaren Eyebrow-Texten (z.B. DE Station
# 05 heisst im Kommentar "Umgebung", sichtbar aber "Badespaß") und bei EN teils
# uebersetzt, teils nicht - deshalb 1:1 aus dem Original uebernommen statt aus
# den editierbaren Feldern abgeleitet.
STATION_COMMENT_LABEL = {
    "de": ["Wandern", "Bike", "Burgen", "Golf", "Kultur", "Umgebung"],
    "it": ["Wandern", "Bike", "Burgen", "Golf", "Kultur", "Umgebung"],
    "en": ["Hiking", "Biking", "Castles", "Golf", "Kultur", "Umgebung"],
}
DISCOVER_COMMENT_LABEL = ["Wandern", "Bike", "Burgen", "Golf", "Kultur", "Badespaß"]


def build_story_rail_fragment(chapters):
    items = []
    for ch in chapters:
        items.append(
            '\n  <div class="story-rail__item">\n'
            '    <span class="story-rail__dot"></span>\n'
            f'    <span class="story-rail__label">{ch["num"]} · {ch["eyebrow"]}</span>\n'
            '  </div>'
        )
    return ('\n  <span class="story-rail__line"></span>'.join(items)) + '\n'


def build_tip_fragment(tip, chapter_idx, tip_idx):
    prefix = f"chapters.{chapter_idx}.tips.{tip_idx}"
    pos = tip.get("position", "").strip()
    style_attr = f' style="object-position:{pos};"' if pos else ""
    return (
        f'<div class="discover-more__tip"><img class="discover-more__tip-img" src="{tip["image"]}"{srcset_attr(tip["image"])} alt="{tip["alt"]}"{style_attr} loading="lazy" data-cms="{prefix}.image">'
        f'<span class="discover-more__tip-caption"><span class="discover-more__tip-title" data-cms="{prefix}.title">{tip["title"]}</span>'
        f'<span class="discover-more__tip-meta" data-cms="{prefix}.meta">{tip["meta"]}</span></span></div>'
    )


def build_chapters_fragment(c, lang):
    parts = []
    for i, ch in enumerate(c["chapters"]):
        decor = CHAPTER_DECOR[i]
        right_mod = " story-chapter--right" if decor["right"] else ""
        prefix = f"chapters.{i}"
        tips_html = "\n        ".join(build_tip_fragment(t, i, ti) for ti, t in enumerate(ch["tips"]))
        parts.append(
            f'\n\n  <!-- Station {ch["num"]} — {STATION_COMMENT_LABEL[lang][i]} -->\n'
            '  <div class="story-chapter-wrap">\n'
            f'  <section class="story-chapter{right_mod}" data-chapter>\n'
            f'    <div class="story-chapter__bg"><img src="{ch["bg_image"]}"{srcset_attr(ch["bg_image"])} alt="{ch["bg_alt"]}" data-cms="{prefix}.bg_image"></div>\n'
            f'    <img class="palm-decor" src="../assets/logo/icon-white.png" alt="" style="{decor["palm"]}">\n'
            '    <div class="story-chapter__inner">\n'
            '      <div class="story-chapter__content reveal">\n'
            f'        <span class="story-chapter__num">{ch["num"]}</span>\n'
            f'        <span class="eyebrow" data-cms="{prefix}.eyebrow">{ch["eyebrow"]}</span>\n'
            f'        <h2 data-cms="{prefix}.heading">{ch["heading"]}</h2>\n'
            f'        <p class="lede" style="color:#e3e6d5;" data-cms="{prefix}.lede">{ch["lede"]}</p>\n'
            f'        <p data-cms="{prefix}.body">{ch["body"]}</p>\n'
            '      </div>\n'
            '    </div>\n'
            '  </section>\n'
            '  </div>\n\n'
            f'  <!-- Entdecke mehr · {DISCOVER_COMMENT_LABEL[i]} -->\n'
            '  <div class="impression-band impression-band--cta">\n'
            '    <div class="impression-band__sticky">\n'
            f'      <span class="impression-band__tag" data-cms="{prefix}.eyebrow">{ch["eyebrow"]}</span>\n'
            '      <div class="discover-more__tips">\n'
            f'        {tips_html}\n'
            '      </div>\n'
            f'      <a href="#filterBar" data-cat="{ch["key"]}" class="btn btn--primary" data-cms="discover_more_label">{c["discover_more_label"]}</a>\n'
            '    </div>\n'
            '  </div>'
        )
    return "".join(parts) + "\n\n"


def build_filter_cats_fragment(c):
    items = []
    for i, cat in enumerate(c["filter_cats"]):
        items.append(f'\n      <button class="filter-btn" data-filter="cat" data-value="{cat["value"]}" data-cms="filter_cats.{i}.label">{cat["label"]}</button>')
    # Das Template-Muster fuer FRAGMENT_FILTER_CATS reicht bis (exklusive) dem
    # Oeffnungstag von #zeitFilters - das schliesst das schliessende </div>
    # von #categoryFilters mit ein, das hier deshalb mit ausgegeben wird.
    return "".join(items) + "\n    </div>\n    "


def build_filter_zeiten_fragment(c):
    items = []
    for i, z in enumerate(c["filter_zeiten"]):
        items.append(f'\n      <button class="filter-btn" data-filter="zeit" data-value="{z["value"]}" data-cms="filter_zeiten.{i}.label">{z["label"]}</button>')
    # Analog zu build_filter_cats_fragment: das schliessende </div> von
    # #zeitFilters wurde vom Template-Muster mit eingeschlossen.
    return "".join(items) + "\n    </div>\n  "


def build_guide_cards_fragment(c):
    parts = []
    for i, card in enumerate(c["guide_cards"]):
        prefix = f"guide_cards.{i}"
        tags_html = "".join(f'<span class="tag" data-cms="{prefix}.tags.{ti}">{t}</span>' for ti, t in enumerate(card["tags"]))
        pos = card.get("position", "").strip()
        style_attr = f' style="object-position:{pos};"' if pos else ""
        parts.append(
            f'\n\n    <!-- {card["comment"]} -->\n'
            f'    <article class="guide-card" data-cat="{card["cat"]}" data-zeit="{card["zeit"]}">\n'
            f'      <div class="guide-card__img"><img src="{card["image"]}"{srcset_attr(card["image"])} alt="{card["alt"]}"{style_attr} data-cms="{prefix}.image"></div>\n'
            '      <div class="guide-card__body">\n'
            f'        <div class="guide-card__tags">{tags_html}</div>\n'
            f'        <span class="place" data-cms="{prefix}.place">{card["place"]}</span>\n'
            f'        <h3 data-cms="{prefix}.title">{card["title"]}</h3>\n'
            f'        <p class="desc" data-cms="{prefix}.desc">{card["desc"]}</p>\n'
            f'        <div class="meta-row" data-cms="{prefix}.meta_row_1_html">\n          {card["meta_row_1_html"]}\n        </div>\n'
            f'        <div class="meta-row" data-cms="{prefix}.meta_row_2_html">\n          {card["meta_row_2_html"]}\n        </div>\n'
            f'        <div class="hours" data-cms="{prefix}.hours">{card["hours"]}</div>\n'
            f'        <div class="actions" data-cms="{prefix}.actions_html">\n          {card["actions_html"]}\n        </div>\n'
            '      </div>\n'
            '    </article>'
        )
    return "".join(parts) + "\n\n  "


def build(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/aktivitaeten.template.html", encoding="utf-8") as f:
        html = f.read()

    fragments = {
        "{{FRAGMENT_STORY_RAIL}}": build_story_rail_fragment(c["chapters"]),
        "{{FRAGMENT_CHAPTERS}}": build_chapters_fragment(c, lang),
        "{{FRAGMENT_FILTER_CATS}}": build_filter_cats_fragment(c),
        "{{FRAGMENT_FILTER_ZEITEN}}": build_filter_zeiten_fragment(c),
        "{{FRAGMENT_GUIDE_CARDS}}": build_guide_cards_fragment(c),
    }
    for token, value in fragments.items():
        html = html.replace(token, value)

    scalars = {
        "{{meta_title}}": c["meta_title"],
        "{{meta_description}}": c["meta_description"],
        "{{hero_heading}}": c["hero_heading"],
        "{{hero_text}}": c["hero_text"],
        "{{story_eyebrow}}": c["story_eyebrow"],
        "{{story_lede}}": c["story_lede"],
        "{{filter_art_label}}": c["filter_art_label"],
        "{{filter_cat_alle_label}}": c["filter_cat_alle_label"],
        "{{filter_zeit_label}}": c["filter_zeit_label"],
        "{{filter_zeit_alle_label}}": c["filter_zeit_alle_label"],
        "{{cta_heading}}": c["cta_heading"],
        "{{cta_text}}": c["cta_text"],
        "{{cta_label}}": c["cta_label"],
    }
    for token, value in scalars.items():
        html = html.replace(token, value)

    with open(BASE + f"{lang}/aktivitaeten.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] aktivitaeten.html neu gebaut.")


for lang in ["de", "it", "en"]:
    build(lang)
