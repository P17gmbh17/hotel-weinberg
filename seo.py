# -*- coding: utf-8 -*-
"""
Zentrale SEO-Konfiguration fuer die Hotel-Weinberg-Seite.

Hier stehen alle Werte, die fuer hreflang, canonical, Schema.org (JSON-LD),
sitemap.xml und robots.txt gebraucht werden - an EINER Stelle, damit sie
nicht ueber 42 HTML-Dateien verstreut gepflegt werden muessen.

Angewendet wird das alles von build_seo.py, das nach den sieben
build_*.py-Skripten laeuft (siehe netlify.toml).

ZU PRUEFEN (siehe Kommentare unten): GEO-Koordinaten und Sternekategorie.
"""

# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------
# Ohne abschliessenden Slash. Wird die Domain jemals gewechselt, ist DAS hier
# die einzige Zeile, die geaendert werden muss - danach einmal neu bauen.
SITE_URL = "https://www.hotelweinberg.eu"

LANGS = ("de", "it", "en")
DEFAULT_LANG = "de"

# hreflang-Codes je Sprachordner. Bewusst ohne Laenderkennung (also "de" statt
# "de-DE"), weil sich die Seite an Gaeste aus DE/AT/CH gleichermassen richtet.
HREFLANG = {"de": "de", "it": "it", "en": "en"}


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------
# slug -> (Prioritaet in der Sitemap, Aenderungshaeufigkeit)
# Die Dateinamen sind in allen drei Sprachordnern identisch, deshalb genuegt
# eine Liste. Rechtstexte werden bewusst niedrig priorisiert.
PAGES = {
    "index.html":                 (1.0, "monthly"),
    "zimmer.html":                (0.9, "monthly"),
    "zimmer-balkon.html":         (0.8, "monthly"),
    "zimmer-garten.html":         (0.8, "monthly"),
    "zimmer-ohne-balkon.html":    (0.8, "monthly"),
    "zimmer-einzelzimmer.html":   (0.8, "monthly"),
    "geniessen.html":             (0.8, "monthly"),
    "aktivitaeten.html":          (0.7, "monthly"),
    "kulinarik.html":             (0.7, "monthly"),
    "philosophie.html":           (0.6, "yearly"),
    "kontakt.html":               (0.7, "yearly"),
    "impressum.html":             (0.1, "yearly"),
    "datenschutz.html":           (0.1, "yearly"),
    "cookie-einstellungen.html":  (0.1, "yearly"),
}

# Seiten, die zwar existieren, aber nicht in den Suchindex sollen.
NOINDEX = ("cookie-einstellungen.html",)

# Seiten aus der Hauptnavigation. Nur deren Inhalte werden im Hintergrund
# vorausgeladen (siehe assets/prefetch.js) - Rechtstexte und
# Zimmer-Detailseiten bewusst nicht, sonst laedt der Browser im Hintergrund
# mehr, als der Gast je aufruft.
NAV_PAGES = (
    "index.html",
    "zimmer.html",
    "geniessen.html",
    "aktivitaeten.html",
    "kulinarik.html",
    "philosophie.html",
    "kontakt.html",
)


# ---------------------------------------------------------------------------
# Stammdaten des Hotels (fuer Schema.org)
# ---------------------------------------------------------------------------
# Quelle: content/kontakt.json bzw. Impressum. Bei Aenderung dort bitte hier
# nachziehen - Schema.org-Daten muessen mit dem sichtbaren Text uebereinstimmen,
# sonst wertet Google sie ab.
HOTEL = {
    "name": "Hotel Weinberg",
    "street": "Luziafeldweg 3",
    "postal_code": "39057",
    "city": "St. Pauls/Eppan",
    "region": "Südtirol",
    "country": "IT",
    "phone": "+39 0471 662326",
    "email": "info@hotelweinberg.eu",
    "price_range": "€€",
    # Guenstigster Zimmerpreis laut content/zimmer.json (alle Kategorien ab 63 EUR).
    "price_from": 63,
    "currency": "EUR",
    # ZU BESTAETIGEN: mehrere Suedtiroler Buchungsportale fuehren das Haus als
    # 3-Sterne-Hotel. Stimmt das nicht, Zeile einfach auf None setzen - dann
    # faellt die Angabe aus dem JSON-LD raus.
    "star_rating": 3,
    # ZU ERGAENZEN: exakte Koordinaten des Hauses. In Google Maps mit
    # Rechtsklick auf das Gebaeude -> die beiden Zahlen erscheinen ganz oben
    # und koennen direkt kopiert werden. Solange None, laesst build_seo.py
    # die Geo-Angabe weg (lieber keine als eine falsche - eine falsche
    # Koordinate schickt Gaeste an den falschen Ort).
    "latitude": None,
    "longitude": None,
    # Repraesentatives Bild fuer die Suchergebnisse.
    "image": "assets/fotos/kontakt-header-sonnenuntergang-2026.jpg",
    "languages": ["Deutsch", "Italiano", "English"],
}

# Ausstattung, die sich aus den bestehenden Seiteninhalten belegen laesst.
AMENITIES = [
    ("Pool", True),
    ("Garten", True),
    ("Bar", True),
    ("Frühstücksbuffet", True),
    ("WLAN", True),
    ("Parkplatz", True),
]

# Beschreibung je Sprache (identisch mit der Meta-Description der Startseite).
DESCRIPTION = {
    "de": "Hotel Weinberg in St. Pauls/Eppan, persönlich geführtes Haus mitten "
          "in den Weinbergen der Südtiroler Weinstraße, mit Blick auf die Dolomiten.",
    "it": "Hotel Weinberg a St. Paolo/Appiano, struttura a conduzione familiare "
          "tra i vigneti della Strada del Vino altoatesina, con vista sulle Dolomiti.",
    "en": "Hotel Weinberg in St. Pauls/Appiano, a family-run house among the "
          "vineyards of the South Tyrolean Wine Route, with views of the Dolomites.",
}

# Verstecktes <h1> fuer die Startseite. Der Hero zeigt dort nur die
# Logo-Grafik, dadurch fehlt der wichtigsten Seite die Hauptueberschrift.
# Wird visuell ausgeblendet (.visually-hidden) - optisch aendert sich nichts,
# Screenreader und Suchmaschinen bekommen sie trotzdem.
HOME_H1 = {
    "de": "Hotel Weinberg — kleines Hotel in den Weinbergen von St. Pauls, Eppan, Südtirol",
    "it": "Hotel Weinberg — piccolo hotel tra i vigneti di St. Paolo, Appiano, Alto Adige",
    "en": "Hotel Weinberg — a small hotel in the vineyards of St. Pauls, Appiano, South Tyrol",
}

# Brotkrumen-Beschriftung der Startseite je Sprache.
HOME_LABEL = {"de": "Startseite", "it": "Home", "en": "Home"}

# Sprachkennungen fuer die Link-Vorschau (Open Graph verlangt ein anderes
# Format als hreflang: "de_DE" statt "de").
OG_LOCALE = {"de": "de_DE", "it": "it_IT", "en": "en_US"}

# Format der Vorschaubilder beim Teilen per WhatsApp/Facebook/iMessage.
# 1200x630 ist das von allen Plattformen erwartete Mass (Seitenverhaeltnis
# 1.91:1); kleinere Bilder werden teils gar nicht angezeigt.
OG_IMAGE_SIZE = (1200, 630)
OG_IMAGE_DIR = "assets/og"

# Rueckfallmotiv, falls fuer eine Seite kein eigenes Kopfbild ermittelbar ist.
OG_FALLBACK_IMAGE = "assets/fotos/kontakt-header-sonnenuntergang-2026.jpg"

# Sichtbare Seitennamen fuer die BreadcrumbList. Fehlt ein Slug hier, nimmt
# build_seo.py automatisch den <title> der Seite.
BREADCRUMB_LABELS = {
    "de": {
        "zimmer.html": "Zimmer",
        "geniessen.html": "Genießen",
        "aktivitaeten.html": "Aktivitäten",
        "kulinarik.html": "Kulinarik-Guide",
        "philosophie.html": "Über uns",
        "kontakt.html": "Kontakt",
    },
    "it": {
        "zimmer.html": "Camere",
        "geniessen.html": "Relax",
        "aktivitaeten.html": "Attività",
        "kulinarik.html": "Guida gastronomica",
        "philosophie.html": "Chi siamo",
        "kontakt.html": "Contatti",
    },
    "en": {
        "zimmer.html": "Rooms",
        "geniessen.html": "Relax",
        "aktivitaeten.html": "Activities",
        "kulinarik.html": "Food Guide",
        "philosophie.html": "About us",
        "kontakt.html": "Contact",
    },
}


def page_url(lang, filename):
    """Vollstaendige kanonische URL einer Seite."""
    return f"{SITE_URL}/{lang}/{filename}"


def asset_url(rel_path):
    """Macht aus einem relativen Bildpfad ('../assets/x.jpg' oder
    'assets/x.jpg') eine absolute URL."""
    clean = rel_path.replace("../", "", 1).lstrip("/")
    return f"{SITE_URL}/{clean}"
