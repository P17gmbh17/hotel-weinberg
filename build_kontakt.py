# -*- coding: utf-8 -*-
"""
Baut {lang}/kontakt.html aus content/kontakt.json + {lang}/kontakt.template.html
"""
import json

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

with open(BASE + "content/kontakt.json", encoding="utf-8") as f:
    ALL = json.load(f)


def build(lang):
    c = ALL[lang]
    with open(BASE + f"{lang}/kontakt.template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{meta_title}}", c["meta_title"])
    html = html.replace("{{meta_description}}", c["meta_description"])
    html = html.replace("{{hero_heading}}", c["hero_heading"])
    html = html.replace("{{hero_text}}", c["hero_text"])
    html = html.replace("{{hero_image}}", c["hero_image"])
    html = html.replace("{{hero_image_alt}}", c["hero_image_alt"])

    lg = c["lage"]
    html = html.replace("{{lage.eyebrow}}", lg["eyebrow"])
    html = html.replace("{{lage.heading}}", lg["heading"])
    html = html.replace("{{lage.lede}}", lg["lede"])
    html = html.replace("{{FRAGMENT_DL}}", lg["dl_html"], 1)

    an = c["anfrage"]
    html = html.replace("{{anfrage.eyebrow}}", an["eyebrow"])
    html = html.replace("{{anfrage.heading}}", an["heading"])
    html = html.replace("{{anfrage.lede}}", an["lede"])

    bp = c["booking_panel"]
    html = html.replace("{{booking_panel.heading}}", bp["heading"])
    html = html.replace("{{booking_panel.note}}", bp["note"])

    html = html.replace("{{FRAGMENT_FORM}}", c["booking_form_html"], 1)
    html = html.replace("{{FRAGMENT_CONTACT_STRIP}}", c["contact_strip_html"], 1)

    with open(BASE + f"{lang}/kontakt.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{lang}] kontakt.html geschrieben")


for lang in ["de", "it", "en"]:
    build(lang)
