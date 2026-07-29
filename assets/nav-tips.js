/* ==========================================================================
   Hotel Weinberg — Navi-Tipps (mobiles Fullscreen-Menü)
   Zeigt am Ende des mobilen Menüs zwei feste Bild-Kacheln aus dem
   Genießen-Bereich (Pool & Frühstück) mit Text im Bild — Klick führt
   direkt zur jeweiligen Station auf der Genießen-Seite.
   ========================================================================== */
(function () {
  var TAG = { de: 'Genießen', it: 'Relax', en: 'Enjoy' };

  var TIPS = {
    de: [
      { img: '../assets/fotos/pool.jpg', title: 'Pool', link: 'geniessen.html#pool' },
      { img: '../assets/fotos/fruehstuecksraum.jpg', title: 'Frühstück', link: 'geniessen.html#fruehstueck' }
    ],
    it: [
      { img: '../assets/fotos/pool.jpg', title: 'Piscina', link: 'geniessen.html#pool' },
      { img: '../assets/fotos/fruehstuecksraum.jpg', title: 'Colazione', link: 'geniessen.html#fruehstueck' }
    ],
    en: [
      { img: '../assets/fotos/pool.jpg', title: 'Pool', link: 'geniessen.html#pool' },
      { img: '../assets/fotos/fruehstuecksraum.jpg', title: 'Breakfast', link: 'geniessen.html#fruehstueck' }
    ]
  };

  function render() {
    var el = document.getElementById('navTips');
    if (!el) return;
    var lang = (document.documentElement.lang || 'de').slice(0, 2);
    var tips = TIPS[lang] || TIPS.de;
    var tag = TAG[lang] || TAG.de;
    el.innerHTML = tips.map(function (t) {
      return '<a class="nav-tip" href="' + t.link + '">' +
        '<img src="' + t.img + '" alt="" loading="lazy">' +
        '<span class="nav-tip__tag">' + tag + '</span>' +
        '<span class="nav-tip__title">' + t.title + '</span>' +
        '</a>';
    }).join('');
  }

  render();
})();
