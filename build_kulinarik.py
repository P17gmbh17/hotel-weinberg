# -*- coding: utf-8 -*-
"""
CMS-Rebuild-Skript fuer kulinarik.html, alle 3 Sprachen (de/it/en).
"""
import json

import os

from img_srcset import srcset_attr

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/kulinarik.json", encoding="utf-8") as f:
    ALL = json.load(f)


def build_polaroids_fragment(c):
    items = []
    for p in c["polaroids"]:
        items.append(
            '      <div class="polaroid">\n'
            f'        <img class="polaroid__img" src="{p["image"]}"{srcset_attr(p["image"])} alt="{p["alt"]}">\n'
            f'        <span>{p["caption"]}</span>\n'
            '      </div>'
        )
    return (
        '<div class="page-hero__polaroids">\n' + "\n".join(items) + "\n"
        '    </div>\n'
        '  </div>'
    )


def build_guide_grid_fragment(c):
    cards = []
    for card in c["cards"]:
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in card["tags"])
        pos = card.get("position", "").strip()
        style_attr = f' style="object-position:{pos};"' if pos else ""
        cards.append(
            f'    <article class="guide-card" data-cat="{card["cat"]}" data-dist="{card["dist"]}">\n'
            f'      <div class="guide-card__img"><img src="{card["image"]}"{srcset_attr(card["image"])} alt="{card["img_alt"]}"{style_attr}></div>\n'
            '      <div class="guide-card__body">\n'
            f'        <div class="guide-card__tags">{tags_html}</div>\n'
            f'        <span class="place">{card["place"]}</span>\n'
            f'        <h3>{card["name"]}</h3>\n'
            f'        <p class="desc">{card["desc"]}</p>\n'
            '        <div class="meta-row">\n'
            f'          <span><svg viewBox="0 0 24 24"><circle cx="13.2" cy="4.3" r="1.5" fill="currentColor" stroke="none"/><path d="M11 8.2l-1.3 4.5 2.3 1.6-.7 5.4"/><path d="M13.3 8.6l1.4 3.6-2 2.2 2.6 2"/><path d="M9.7 10.6l-2.9 1.8"/></svg> {card["walk_time"]}</span>\n'
            f'          <span><svg class="icon-fill" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M3 17.5v-3c0-.8.6-1.5 1.5-1.5H6l1.3-4.3C7.6 7.7 8.5 7 9.6 7h4.8c1.1 0 2 .7 2.3 1.7L18 13h1.5c.9 0 1.5.7 1.5 1.5v3H3Z M8.3 8.3h3.3v4h-3.3z M12.4 8.3h3.3v4h-3.3z"/><circle cx="7.2" cy="17.5" r="2.3"/><circle cx="16.8" cy="17.5" r="2.3"/></svg> {card["drive_time"]}</span>\n'
            '        </div>\n'
            f'        <div class="hours">{card["hours"]}</div>\n'
            '        <div class="actions">\n'
            f'          <a href="{card["phone_href"]}">{card["phone_label"]}</a>\n'
            f'          <a href="{card["website_href"]}" target="_blank" rel="noopener">{card["website_label"]}</a>\n'
            '        </div>\n'
            '      </div>\n'
            '    </article>'
        )
    return (
        '<div class="guide-grid" id="guideGrid">\n\n' + "\n\n".join(cards) + "\n\n"
        '  </div>\n'
        '</div>'
    )


def build(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/kulinarik.template.html", encoding="utf-8") as f:
        html = f.read()

    fragments = {
        "{{FRAGMENT_POLAROIDS}}": build_polaroids_fragment(c),
        "{{FRAGMENT_GUIDE_GRID}}": build_guide_grid_fragment(c),
    }
    for token, value in fragments.items():
        assert token in html, f"Token {token} fehlt im Template ({lang})"
        html = html.replace(token, value)

    scalars = {
        "meta_title": c["meta_title"],
        "meta_description": c["meta_description"],
        "hero_heading": c["hero_heading"],
        "hero_text": c["hero_text"],
    }
    for name, value in scalars.items():
        token = "{{" + name + "}}"
        assert token in html, f"Token {token} fehlt im Template ({lang})"
        html = html.replace(token, value)

    with open(BASE + f"{lang}/kulinarik.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] kulinarik.html neu gebaut.")


for lang in ["de", "it", "en"]:
    build(lang)
