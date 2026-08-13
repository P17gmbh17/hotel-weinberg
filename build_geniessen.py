# -*- coding: utf-8 -*-
"""
CMS-Rebuild-Skript fuer geniessen.html, alle 3 Sprachen (de/it/en).

Liest content/geniessen.json und baut daraus {lang}/geniessen.html aus
{lang}/geniessen.template.html.

Aufruf:
    python3 build_geniessen.py
"""
import json

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/geniessen.json", encoding="utf-8") as f:
    ALL = json.load(f)


RAIL_KEYS = ["pool", "garten", "fruehstueck", "bar"]


def build_rail_fragment(c):
    items = []
    total = len(RAIL_KEYS)
    for i, key in enumerate(RAIL_KEYS, start=1):
        items.append(
            '  <div class="story-rail__item">\n'
            '    <span class="story-rail__dot"></span>\n'
            f'    <span class="story-rail__label">0{i} · {c[key]["eyebrow"]}</span>\n'
            '  </div>'
        )
        if i < total:
            items.append('  <span class="story-rail__line"></span>')
    return (
        '<nav class="story-rail" id="storyRail" aria-hidden="true">\n'
        + "\n".join(items) + "\n"
        '</nav>'
    )


def build_ticklist_fragment(c):
    items = "\n".join(f'      <li>{item}</li>' for item in c["pool"]["tick_list"])
    return '<ul class="tick-list">\n' + items + '\n    </ul>'


def build_band_fragment(chapter, tag, slug):
    n = len(chapter["impressions"])
    items = []
    for im in chapter["impressions"]:
        pos = im.get("position", "").strip()
        style_attr = f' style="object-position:{pos};"' if pos else ""
        items.append(
            '      <div class="impression-band__item">\n'
            f'          <img src="{im["image"]}" alt="{im["alt"]}"{style_attr}>\n'
            f'          <span class="impression-band__caption">{im["caption"]}</span>\n'
            '        </div>'
        )

    # Mobile: statt nur die ersten 2 Bilder statisch zu zeigen, rotiert die Ansicht
    # per reinem CSS durch ALLE Bilder des Themas (funktioniert auch, wenn das
    # Bilder-Array später auf mehr als 3 Fotos erweitert wird).
    slot_s = 4.5
    fade_s = 0.8
    total_s = round(n * slot_s, 2)
    keyframe_name = f"impressionFade{slug.capitalize()}"
    band_id = f"band{slug.capitalize()}"
    fade_in_end = round(fade_s / total_s * 100, 2) if total_s else 0
    slot_end = round(100 / n, 2) if n else 100
    fade_out_start = round(max(slot_end - fade_in_end, fade_in_end), 2)
    rules = []
    for i in range(n):
        delay = round(-(i * slot_s), 2)
        rules.append(
            f'  #{band_id} .impression-band__item:nth-child({i + 1}) {{ animation: {keyframe_name} {total_s}s ease-in-out infinite; animation-delay: {delay}s; }}'
        )
    style_block = (
        '<style>\n'
        '@media (max-width: 780px) {\n'
        f'  @keyframes {keyframe_name} {{ 0% {{ opacity: 0; }} {fade_in_end}% {{ opacity: 1; }} {fade_out_start}% {{ opacity: 1; }} {slot_end}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}\n'
        + "\n".join(rules) + "\n"
        '}\n'
        '</style>'
    )

    return (
        style_block + "\n"
        f'<div class="impression-band" id="{band_id}">\n'
        '    <div class="impression-band__sticky">\n'
        f'      <span class="impression-band__tag">{tag}</span>\n'
        '      <div class="impression-band__grid">\n'
        + "\n".join(items) + "\n"
        '      </div>\n'
        '    </div>\n'
        '  </div>'
    )


def build_kulinarik_grid_fragment(c):
    cards = []
    for card in c["kulinarik_teaser"]["cards"]:
        cards.append(
            '      <a class="teaser-card" href="kulinarik.html">\n'
            f'        <img src="{card["image"]}" alt="{card["label"]}">\n'
            f'        <span class="teaser-card__label">{card["label"]}</span>\n'
            '      </a>'
        )
    return '<div class="kulinarik-teaser-grid">\n' + "\n".join(cards) + '\n    </div>'


def build(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/geniessen.template.html", encoding="utf-8") as f:
        html = f.read()

    fragments = {
        "{{FRAGMENT_RAIL}}": build_rail_fragment(c),
        "{{FRAGMENT_POOL_TICKLIST}}": build_ticklist_fragment(c),
        "{{FRAGMENT_BAND_POOL}}": build_band_fragment(c["pool"], f'{c["impressions_prefix"]} · {c["pool"]["eyebrow"]}', "pool"),
        "{{FRAGMENT_BAND_GARTEN}}": build_band_fragment(c["garten"], f'{c["impressions_prefix"]} · {c["garten"]["eyebrow"]}', "garten"),
        "{{FRAGMENT_BAND_FRUEHSTUECK}}": build_band_fragment(c["fruehstueck"], f'{c["impressions_prefix"]} · {c["fruehstueck"]["eyebrow"]}', "fruehstueck"),
        "{{FRAGMENT_BAND_BAR}}": build_band_fragment(c["bar"], f'{c["impressions_prefix"]} · {c["bar"]["eyebrow"]}', "bar"),
        "{{FRAGMENT_KULINARIK_GRID}}": build_kulinarik_grid_fragment(c),
    }
    for token, value in fragments.items():
        assert token in html, f"Token {token} nicht im Template gefunden ({lang})"
        html = html.replace(token, value)

    scalars = {
        "meta_title": c["meta_title"],
        "meta_description": c["meta_description"],
        "hero_heading": c["hero_heading"],
        "hero_text": c["hero_text"],
        "story_eyebrow": c["story_eyebrow"],
        "story_lede": c["story_lede"],
        "story_scroll_label": c["story_scroll_label"],
        "pool.background_image": c["pool"]["background_image"],
        "pool.background_alt": c["pool"]["background_alt"],
        "pool.eyebrow": c["pool"]["eyebrow"],
        "pool.heading": c["pool"]["heading"],
        "pool.lede": c["pool"]["lede"],
        "garten.background_image": c["garten"]["background_image"],
        "garten.background_alt": c["garten"]["background_alt"],
        "garten.eyebrow": c["garten"]["eyebrow"],
        "garten.heading": c["garten"]["heading"],
        "garten.lede": c["garten"]["lede"],
        "garten.body": c["garten"]["body"],
        "fruehstueck.background_image": c["fruehstueck"]["background_image"],
        "fruehstueck.background_alt": c["fruehstueck"]["background_alt"],
        "fruehstueck.eyebrow": c["fruehstueck"]["eyebrow"],
        "fruehstueck.heading": c["fruehstueck"]["heading"],
        "fruehstueck.lede": c["fruehstueck"]["lede"],
        "fruehstueck.body_desktop": c["fruehstueck"]["body_desktop"],
        "fruehstueck.body_mobile": c["fruehstueck"]["body_mobile"],
        "fruehstueck.cta_label": c["fruehstueck"]["cta_label"],
        "bar.background_image": c["bar"]["background_image"],
        "bar.background_alt": c["bar"]["background_alt"],
        "bar.eyebrow": c["bar"]["eyebrow"],
        "bar.heading": c["bar"]["heading"],
        "bar.lede": c["bar"]["lede"],
        "bar.body": c["bar"]["body"],
        "zimmer_link.image": c["zimmer_link"]["image"],
        "zimmer_link.alt": c["zimmer_link"]["alt"],
        "zimmer_link.eyebrow": c["zimmer_link"]["eyebrow"],
        "zimmer_link.heading": c["zimmer_link"]["heading"],
        "zimmer_link.lede": c["zimmer_link"]["lede"],
        "zimmer_link.cta_label": c["zimmer_link"]["cta_label"],
        "kulinarik_teaser.eyebrow": c["kulinarik_teaser"]["eyebrow"],
        "kulinarik_teaser.heading": c["kulinarik_teaser"]["heading"],
        "kulinarik_teaser.lede": c["kulinarik_teaser"]["lede"],
        "kulinarik_teaser.cta_label": c["kulinarik_teaser"]["cta_label"],
        "cta_banner.heading": c["cta_banner"]["heading"],
        "cta_banner.text": c["cta_banner"]["text"],
        "cta_banner.cta_label": c["cta_banner"]["cta_label"],
    }
    for name, value in scalars.items():
        token = "{{" + name + "}}"
        assert token in html, f"Token {token} nicht im Template gefunden ({lang})"
        html = html.replace(token, value)

    with open(BASE + f"{lang}/geniessen.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] geniessen.html neu gebaut.")


for lang in ["de", "it", "en"]:
    build(lang)
