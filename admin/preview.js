/*
 * Vorschau fuer Decap CMS: zeigt jeden Inhalts-Block als eigenen, klar
 * abgetrennten "Sektor" (Karte mit Rahmen, Beschriftung, viel Abstand),
 * mit der echten Schrift/Farben der Seite (styles.css wird geladen), aber
 * bewusst KLEINEN Bild-Thumbnails statt Bildern in echter Website-Groesse -
 * damit man in der schmalen Vorschau-Spalte auf einen Blick sieht, was man
 * gerade bearbeitet, ohne dass ein einzelnes riesiges Bild den ganzen
 * Platz einnimmt.
 */

function esc(s) {
  if (s === undefined || s === null) return '';
  return String(s);
}

function normalizeSectorTitle(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9äöüß]+/g, '');
}

function sector(number, title, innerHtml) {
  // data-sector-title traegt den normalisierten Titel (z.B. "genieenteaser"),
  // damit ein Klick auf die passende aufklappbare Sektion im linken
  // Formular (z.B. "3 · Genießen-Teaser") diesen Block hier rechts
  // markieren und dahin scrollen kann - siehe Klick-Listener in
  // admin/index.html. WICHTIG: es wird NICHT nach Nummer gematcht, weil die
  // Nummerierung im Formular (jedes einzelne Feld zaehlt mit) und hier in
  // der Vorschau (mehrere Felder zu einem Block zusammengefasst) oft
  // auseinanderlaufen - der TITEL-Text ist der stabile gemeinsame Anker.
  //
  // Die "aktiv"-Klasse wird HIER beim Rendern direkt eingebacken (statt
  // hinterher von aussen per DOM-Mutation gesetzt zu werden) - Decap
  // rendert die Vorschau periodisch neu (auch ohne Klick, per Live-Test
  // am 2026-07-29 bestaetigt) und wuerde eine nachtraeglich von aussen
  // gesetzte Klasse sonst innerhalb von ca. 2 Sekunden wieder ueberschreiben.
  // window.__weinbergActiveSectionTitle wird vom Klick-Listener in
  // admin/index.html gesetzt; da Vorschau-Komponenten im selben (aeusseren)
  // Fenster-Kontext laufen wie dieses Skript, ist der Zugriff synchron und
  // ohne iframe-Grenze moeglich.
  var norm = normalizeSectorTitle(title);
  var activeCls = (typeof window !== 'undefined' && window.__weinbergActiveSectionTitle === norm) ? ' cms-sector--active' : '';
  return (
    '<section class="cms-sector' + activeCls + '" data-sector="' + esc(number) + '" data-sector-title="' + norm + '">' +
      '<div class="cms-sector__label">' + number + ' · ' + esc(title) + '</div>' +
      '<div class="cms-sector__body">' + innerHtml + '</div>' +
    '</section>'
  );
}

function thumb(src, label, size) {
  size = size || 84;
  var img = src ? '<img src="' + src + '" style="width:' + size + 'px;height:' + size + 'px;object-fit:cover;border-radius:8px;display:block;">' : '';
  return (
    '<div class="cms-thumb">' + img +
      (label ? '<span class="cms-thumb__label">' + esc(label) + '</span>' : '') +
    '</div>'
  );
}

var WeinbergIndexPreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var w = data.willkommen || {};
    var z = data.zimmer || {};
    var g = data.geniessen || {};
    var ak = data.aktivitaeten || {};
    var k = data.kulinarik || {};
    var cta = data.cta_banner || {};
    var footer = data.footer || {};
    var contact = data.contact || {};

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/index.html';
    var html = '';

    // 0 Referenz: echte, aktuell veröffentlichte Live-Seite (Netlify).
    // Aus einer anderen Domain eingebettet -> zeigt den letzten
    // veröffentlichten Stand, reagiert nicht live auf ungespeicherte
    // Entwuerfe (Browser-Sicherheitsgrenze zwischen Domains).
    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    // 1 Willkommen
    html += sector('1', 'Willkommen',
      '<div class="cms-eyebrow">' + esc(w.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(w.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(w.lede) + '</p>' +
      '<p class="cms-body">' + esc(w.body) + '</p>' +
      '<div class="cms-row">' + thumb(w.image, 'Bild', 100) +
        '<span class="cms-cta">' + esc(w.cta_label) + '</span>' +
      '</div>'
    );

    // 2 Zimmer
    html += sector('2', 'Zimmer-Teaser',
      '<div class="cms-eyebrow">' + esc(z.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(z.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(z.lede) + '</p>' +
      '<div class="cms-row">' + thumb(z.image, 'Bild', 100) +
        '<span class="cms-cta">' + esc(z.cta_label) + '</span>' +
      '</div>'
    );

    // 3 Genießen
    var gImgs = (g.images || []).map(function (im) { return thumb(im.image, im.alt, 64); }).join('');
    html += sector('3', 'Genießen-Teaser',
      '<div class="cms-eyebrow">' + esc(g.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(g.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(g.lede) + '</p>' +
      '<div class="cms-row cms-row--wrap">' + gImgs + '</div>' +
      '<div class="cms-row"><span class="cms-cta">' + esc(g.cta_label) + '</span></div>'
    );

    // 4 Aktivitaeten
    var cats = ak.categories || [];
    var catsHtml = cats.map(function (cat) {
      var tipsHtml = (cat.tips || []).map(function (t) {
        return thumb(t.image, t.title + (t.meta ? ' · ' + t.meta : ''), 56);
      }).join('');
      return (
        '<div class="cms-category">' +
          '<div class="cms-category__label">' + esc(cat.label) + '</div>' +
          '<div class="cms-row cms-row--wrap">' + tipsHtml + '</div>' +
        '</div>'
      );
    }).join('');
    html += sector('4', 'Aktivitäten-Teaser',
      '<div class="cms-row">' + thumb(ak.background_image, 'Hintergrund', 100) + '</div>' +
      '<div class="cms-eyebrow">' + esc(ak.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(ak.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(ak.lede) + '</p>' +
      catsHtml +
      '<div class="cms-row"><span class="cms-cta">' + esc(ak.cta_label) + '</span></div>'
    );

    // 5 Kulinarik
    var cards = (k.cards || []).map(function (card) { return thumb(card.image, card.label, 64); }).join('');
    html += sector('5', 'Kulinarik-Teaser',
      '<div class="cms-eyebrow">' + esc(k.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(k.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(k.lede) + '</p>' +
      '<div class="cms-row cms-row--wrap">' + cards + '</div>' +
      '<div class="cms-row"><span class="cms-cta">' + esc(k.cta_label) + '</span></div>'
    );

    // 6 CTA-Banner
    html += sector('6', 'CTA-Banner',
      '<h3 class="cms-heading">' + esc(cta.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(cta.text) + '</p>'
    );

    // 7 Footer
    html += sector('7', 'Footer',
      '<p class="cms-body">' + esc(footer.intro) + '</p>' +
      '<p class="cms-meta">' + esc(footer.copyright) + '</p>'
    );

    // 8 Kontakt
    html += sector('8', 'Kontaktdaten',
      '<p class="cms-meta">' + esc(contact.phone_display) + ' · ' + esc(contact.email) + '</p>' +
      '<p class="cms-meta">' + esc(contact.address_street) + ', ' + esc(contact.address_zip_city) + '</p>'
    );

    // 9-12 Buttons / Meta
    html += sector('9–15', 'Buttons & Seitentitel',
      '<p class="cms-meta"><b>Jetzt anfragen:</b> ' + esc(data.cta_book_label) + ' &nbsp; ' +
      '<b>Jetzt buchen:</b> ' + esc(data.cta_buchen_label) + ' &nbsp; ' +
      '<b>Scroll-Hinweis:</b> ' + esc(data.hero_scroll_label) + ' &nbsp; ' +
      '<b>2. Hero-Button:</b> ' + esc(data.hero_cta_secondary_label) + '</p>' +
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

var WeinbergZimmerPreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var rooms = data.rooms || [];

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/zimmer.html';
    var html = '';

    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    // 1 Header
    html += sector('1', 'Übersichtsseite: Header',
      '<h3 class="cms-heading">' + esc(data.hero_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.hero_text) + '</p>' +
      '<p class="cms-meta"><b>Überschrift über den Karten:</b> ' + esc(data.overview_heading) + '</p>'
    );

    // 2 Zimmerkategorien
    var roomsHtml = rooms.map(function (room, i) {
      return (
        '<div class="cms-category">' +
          '<div class="cms-category__label">' + (i + 1) + ' · ' + esc(room.title) +
            (room.card_title && room.card_title !== room.title ? ' (Karte: ' + esc(room.card_title) + ')' : '') +
          '</div>' +
          '<div class="cms-row">' + thumb(room.image, 'Bild', 80) +
            '<span class="cms-cta">ab ' + esc(room.price) + ' €</span>' +
          '</div>' +
          '<p class="cms-body">' + esc(room.teaser) + '</p>' +
          '<p class="cms-lede">' + esc(room.lede) + '</p>' +
          '<div class="cms-row cms-row--wrap">' +
            (room.gallery || []).map(function (img) { return thumb(img, '', 56); }).join('') +
          '</div>' +
        '</div>'
      );
    }).join('');
    html += sector('2', 'Zimmerkategorien', roomsHtml);

    // 3 Wiederkehrende Texte
    html += sector('3', 'Wiederkehrende Texte (alle Detailseiten)',
      '<p class="cms-meta"><b>Eyebrow Zimmerkategorie:</b> ' + esc(data.room_category_eyebrow) + '</p>' +
      '<p class="cms-meta"><b>Eyebrow Impressionen:</b> ' + esc(data.gallery_eyebrow) + '</p>' +
      '<p class="cms-meta"><b>Weitere Zimmerkategorien:</b> ' + esc(data.related_heading) + '</p>'
    );

    // 4 Slideshow
    html += sector('4', 'Übersichtsseite: Slideshow',
      '<div class="cms-eyebrow">' + esc(data.slideshow_eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(data.slideshow_heading) + '</h3>'
    );

    // 5 CTA-Banner
    html += sector('5', 'Übersichtsseite: CTA-Banner',
      '<h3 class="cms-heading">' + esc(data.cta_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.cta_text) + '</p>'
    );

    // 6 Meta
    html += sector('6', 'Seitentitel & SEO (Übersichtsseite)',
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

var WeinbergGeniessenPreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var pool = data.pool || {};
    var garten = data.garten || {};
    var fs = data.fruehstueck || {};
    var zl = data.zimmer_link || {};
    var kt = data.kulinarik_teaser || {};
    var cta = data.cta_banner || {};

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/geniessen.html';
    var html = '';

    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    html += sector('1', 'Header & Einleitung',
      '<h3 class="cms-heading">' + esc(data.hero_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.hero_text) + '</p>' +
      '<div class="cms-eyebrow">' + esc(data.story_eyebrow) + '</div>' +
      '<p class="cms-body">' + esc(data.story_lede) + '</p>'
    );

    function chapterHtml(chap) {
      var tips = (chap.tick_list || []).map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
      var imps = (chap.impressions || []).map(function (im) { return thumb(im.image, im.caption, 64); }).join('');
      return (
        '<div class="cms-row">' + thumb(chap.background_image, 'Hintergrund', 90) + '</div>' +
        '<div class="cms-eyebrow">' + esc(chap.eyebrow) + '</div>' +
        '<h3 class="cms-heading">' + esc(chap.heading) + '</h3>' +
        '<p class="cms-lede">' + esc(chap.lede) + '</p>' +
        (chap.body ? '<p class="cms-body">' + esc(chap.body) + '</p>' : '') +
        (chap.body_desktop ? '<p class="cms-body"><b>Desktop:</b> ' + esc(chap.body_desktop) + '</p>' : '') +
        (chap.body_mobile ? '<p class="cms-body"><b>Mobile:</b> ' + esc(chap.body_mobile) + '</p>' : '') +
        (tips ? '<ul>' + tips + '</ul>' : '') +
        '<div class="cms-row cms-row--wrap">' + imps + '</div>'
      );
    }

    html += sector('2', 'Station 1 · Pool', chapterHtml(pool));
    html += sector('3', 'Station 2 · Garten', chapterHtml(garten));
    html += sector('4', 'Station 3 · Frühstück', chapterHtml(fs));

    html += sector('5', 'Zimmer-Verlinkung',
      '<div class="cms-eyebrow">' + esc(zl.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(zl.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(zl.lede) + '</p>' +
      '<div class="cms-row">' + thumb(zl.image, 'Bild', 90) + '</div>'
    );

    var cards = (kt.cards || []).map(function (c) { return thumb(c.image, c.label, 64); }).join('');
    html += sector('6', 'Kulinarik-Teaser',
      '<div class="cms-eyebrow">' + esc(kt.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(kt.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(kt.lede) + '</p>' +
      '<div class="cms-row cms-row--wrap">' + cards + '</div>'
    );

    html += sector('7', 'CTA-Banner',
      '<h3 class="cms-heading">' + esc(cta.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(cta.text) + '</p>'
    );

    html += sector('8', 'Seitentitel & SEO',
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

var WeinbergKulinarikPreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var polaroids = data.polaroids || [];
    var cards = data.cards || [];

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/kulinarik.html';
    var html = '';

    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    var polThumbs = polaroids.map(function (p) { return thumb(p.image, p.caption, 64); }).join('');
    html += sector('1', 'Header',
      '<h3 class="cms-heading">' + esc(data.hero_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.hero_text) + '</p>' +
      '<div class="cms-row cms-row--wrap">' + polThumbs + '</div>'
    );

    var cardsHtml = cards.map(function (c, i) {
      var tags = (c.tags || []).join(' · ');
      return (
        '<div class="cms-category">' +
          '<div class="cms-category__label">' + (i + 1) + ' · ' + esc(c.name) + '</div>' +
          '<div class="cms-row">' + thumb(c.image, '', 70) +
            '<span class="cms-meta">' + esc(c.place) + '<br>' + esc(tags) + '</span>' +
          '</div>' +
          '<p class="cms-body">' + esc(c.desc) + '</p>' +
          '<p class="cms-meta">' + esc(c.walk_time) + ' · ' + esc(c.drive_time) + '</p>' +
          '<p class="cms-meta">' + esc(c.hours) + '</p>' +
        '</div>'
      );
    }).join('');
    html += sector('2', 'Restaurants / Lokale', cardsHtml);

    html += sector('3', 'Seitentitel & SEO',
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

var WeinbergPhilosophiePreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var g = data.geschichte || {};
    var gg = data.gastgeber || {};
    var ph = data.philosophie || {};
    var au = data.ausstattung || {};
    var gl = data.geniessen_link || {};
    var cta = data.cta_banner || {};

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/philosophie.html';
    var html = '';

    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    html += sector('1', 'Header',
      '<h3 class="cms-heading">' + esc(data.hero_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.hero_text) + '</p>'
    );

    html += sector('2', 'Konzept & Geschichte',
      '<div class="cms-eyebrow">' + esc(g.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(g.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(g.lede) + '</p>' +
      '<p class="cms-body">' + esc(g.body) + '</p>' +
      '<div class="cms-row">' + thumb(g.image, g.alt, 90) + '</div>'
    );

    var team = (gg.team || []).map(function (m) { return thumb(m.image, m.name, 72); }).join('');
    html += sector('3', 'Eure Gastgeber',
      '<div class="cms-eyebrow">' + esc(gg.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(gg.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(gg.lede) + '</p>' +
      '<div class="cms-row cms-row--wrap">' + team + '</div>'
    );

    html += sector('4', 'Unsere Philosophie',
      '<div class="cms-eyebrow">' + esc(ph.badge) + '</div>' +
      '<h3 class="cms-heading">' + esc(ph.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(ph.lede) + '</p>'
    );

    var slides = (au.slider || []).map(function (s) { return thumb(s.image, s.alt, 72); }).join('');
    var amenities = (au.amenities || []).map(function (a) { return '<li>' + esc(a) + '</li>'; }).join('');
    html += sector('5', 'Das Haus auf einen Blick',
      '<div class="cms-eyebrow">' + esc(au.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(au.heading) + '</h3>' +
      '<div class="cms-row cms-row--wrap">' + slides + '</div>' +
      (amenities ? '<ul>' + amenities + '</ul>' : '')
    );

    html += sector('6', 'Genießen-Verlinkung',
      '<div class="cms-eyebrow">' + esc(gl.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(gl.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(gl.lede) + '</p>' +
      '<div class="cms-row">' + thumb(gl.image, gl.alt, 90) + '</div>'
    );

    html += sector('7', 'CTA-Banner',
      '<h3 class="cms-heading">' + esc(cta.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(cta.text) + '</p>'
    );

    html += sector('8', 'Seitentitel & SEO',
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

var WeinbergKontaktPreview = createClass({
  render: function () {
    var data = this.props.entry.get('data').toJS() || {};
    var lg = data.lage || {};
    var an = data.anfrage || {};
    var bp = data.booking_panel || {};

    var LIVE_URL = 'https://hotel-weinberg.netlify.app/de/kontakt.html';
    var html = '';

    html +=
      '<section class="cms-sector cms-sector--live">' +
        '<div class="cms-sector__label">Referenz · aktuelle Live-Seite' +
          '<a href="' + LIVE_URL + '" target="_blank" rel="noopener" class="cms-live-link">In neuem Tab öffnen ↗</a>' +
        '</div>' +
        '<iframe src="' + LIVE_URL + '" class="cms-live-frame" title="Live-Seite"></iframe>' +
      '</section>';

    html += sector('1', 'Header',
      '<h3 class="cms-heading">' + esc(data.hero_heading) + '</h3>' +
      '<p class="cms-lede">' + esc(data.hero_text) + '</p>' +
      '<div class="cms-row">' + thumb(data.hero_image, data.hero_image_alt, 90) + '</div>'
    );

    html += sector('2', 'Lage',
      '<div class="cms-eyebrow">' + esc(lg.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(lg.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(lg.lede) + '</p>'
    );

    html += sector('3', 'Verfügbarkeit & Anfrage',
      '<div class="cms-eyebrow">' + esc(an.eyebrow) + '</div>' +
      '<h3 class="cms-heading">' + esc(an.heading) + '</h3>' +
      '<p class="cms-lede">' + esc(an.lede) + '</p>'
    );

    html += sector('4', 'Anfrageformular-Panel',
      '<h3 class="cms-heading">' + esc(bp.heading) + '</h3>' +
      '<p class="cms-body">' + esc(bp.note) + '</p>'
    );

    html += sector('5', 'Seitentitel & SEO',
      '<p class="cms-meta"><b>Seitentitel:</b> ' + esc(data.meta_title) + '</p>' +
      '<p class="cms-meta"><b>Meta-Beschreibung:</b> ' + esc(data.meta_description) + '</p>'
    );

    return h('div', {
      className: 'cms-preview-root',
      dangerouslySetInnerHTML: { __html: html },
    });
  },
});

CMS.registerPreviewStyle('/assets/styles.css');
CMS.registerPreviewStyle(
  '@import url("https://fonts.googleapis.com/css2?family=Tenor+Sans&display=swap");' +
  'body { margin:0; background:#f7f5f0; }' +
  '.cms-preview-root { padding: 28px 32px; max-width: 720px; }' +
  '.cms-sector { background:#fff; border:1px solid rgba(35,55,33,0.12); border-radius:10px; padding:20px 24px; margin-bottom:28px; box-shadow:0 1px 4px rgba(29,47,30,0.05); }' +
  '.cms-sector__label { font-family:var(--sans, sans-serif); font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color:#9a8f78; font-weight:600; margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(35,55,33,0.1); }' +
  '.cms-eyebrow { font-family:var(--sans, sans-serif); font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color: var(--olive, #7a8452); margin-bottom:6px; }' +
  '.cms-heading { font-family:var(--serif, serif); font-size:1.3rem; color: var(--green-dark, #23371f); margin:0 0 10px; line-height:1.25; }' +
  '.cms-lede { font-weight:600; color:#2b2b2b; margin:0 0 8px; line-height:1.5; }' +
  '.cms-body { color:#4a4a4a; margin:0 0 12px; line-height:1.55; }' +
  '.cms-meta { color:#6b6b6b; font-size:0.85rem; margin:4px 0; }' +
  '.cms-row { display:flex; align-items:center; gap:14px; margin-top:10px; }' +
  '.cms-row--wrap { flex-wrap:wrap; }' +
  '.cms-thumb { display:flex; flex-direction:column; align-items:center; gap:4px; max-width:100px; }' +
  '.cms-thumb img { border:1px solid rgba(35,55,33,0.12); }' +
  '.cms-thumb__label { font-size:0.68rem; color:#8a8a8a; text-align:center; line-height:1.2; }' +
  '.cms-cta { display:inline-block; padding:7px 16px; background: var(--green-dark, #23371f); color:#fff; border-radius:999px; font-size:0.75rem; letter-spacing:0.03em; }' +
  '.cms-category { margin-top:16px; padding-top:14px; border-top:1px dashed rgba(35,55,33,0.15); }' +
  '.cms-category__label { font-family:var(--sans, sans-serif); font-size:0.8rem; font-weight:600; color: var(--green-dark, #23371f); margin-bottom:8px; }' +
  '.cms-sector--live { padding:0; overflow:hidden; }' +
  '.cms-sector--live .cms-sector__label { padding:14px 20px; margin:0; border-bottom:1px solid rgba(35,55,33,0.1); display:flex; justify-content:space-between; align-items:center; }' +
  '.cms-live-link { text-transform:none; letter-spacing:normal; font-size:12px; color: var(--olive, #7a8452); text-decoration:none; }' +
  '.cms-live-frame { display:block; width:100%; height:480px; border:0; }' +
  /* Aktive Sektion: wird per JS (admin/index.html) markiert, wenn links im
     Formular die passende aufklappbare Sektion angeklickt/geoeffnet wird. */
  '.cms-sector--active { border-color: #898453; box-shadow: 0 0 0 3px rgba(137,132,83,0.35), 0 2px 10px rgba(29,47,30,0.12); }' +
  '.cms-sector--active .cms-sector__label { color: #6e6a41; }',
  { raw: true }
);

CMS.registerPreviewTemplate('startseite', WeinbergIndexPreview);
// Bei allen anderen Sammlungen ist der interne Datei-Name (files: -> name)
// identisch zum Sammlungs-Namen (z.B. "kontakt"/"kontakt"), nur bei der
// Startseite weicht er ab (Sammlung "startseite", Datei "index" - historisch
// gewachsen). Decap scheint hier den DATEI-Namen fuer die Vorschau-Zuordnung
// zu verwenden, nicht den Sammlungs-Namen - deshalb zusaetzlich unter
// "index" registrieren, sonst faellt die Startseite auf die generische
// Standard-Vorschau zurueck.
CMS.registerPreviewTemplate('index', WeinbergIndexPreview);
CMS.registerPreviewTemplate('zimmer', WeinbergZimmerPreview);
CMS.registerPreviewTemplate('geniessen', WeinbergGeniessenPreview);
CMS.registerPreviewTemplate('kulinarik', WeinbergKulinarikPreview);
CMS.registerPreviewTemplate('philosophie', WeinbergPhilosophiePreview);
CMS.registerPreviewTemplate('kontakt', WeinbergKontaktPreview);
