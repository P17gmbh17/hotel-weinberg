/* ==========================================================================
   Groesserer Vorlauf fuer das verzoegerte Bildladen
   --------------------------------------------------------------------------
   Ausgangslage: Alle Bilder unterhalb des sichtbaren Bereichs tragen
   loading="lazy". Der Browser entscheidet selbst, wie frueh er sie holt -
   Chrome faengt erst recht knapp vor dem Sichtbarwerden an. Beim zuegigen
   Scrollen kommt er damit nicht hinterher, und die Bilder erscheinen erst
   mit spuerbarer Verzoegerung.

   Dieses Skript zieht den Startpunkt nach vorne: Sobald ein Bild sich bis
   auf etwa zwei Bildschirmhoehen genaehert hat, wird es von "lazy" auf
   "eager" umgestellt und damit sofort geladen. Beim normalen Scrollen ist
   es dann laengst da.

   Warum nicht einfach alle Bilder sofort laden? Die Aktivitaetenseite hat
   64 Bilder. Ohne Verzoegerung waeren das rund 23 MB am Rechner und 4 MB
   am Handy - der Grossteil davon Karteikarten, die die meisten Gaeste nie
   zu Gesicht bekommen. Der Vorlauf holt nur, worauf man tatsaechlich
   zusteuert.

   Ruecksichtnahme:
     - bei aktiviertem Datensparmodus oder 2G/3G passiert nichts, dort
       bleibt die sparsame Voreinstellung des Browsers bestehen
     - laeuft erst nach dem vollstaendigen Laden der Seite, damit der
       Kopfbereich Vorrang behaelt
     - ohne JavaScript oder ohne IntersectionObserver bleibt das native
       loading="lazy" unveraendert wirksam
   ========================================================================== */
(function () {
  if (!('IntersectionObserver' in window)) return;

  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn) {
    if (conn.saveData) return;
    if (/(^|-)(2g|3g)$/.test(conn.effectiveType || '')) return;
  }

  function start() {
    // Zwei Bildschirmhoehen Vorlauf, nach unten wie nach oben.
    var margin = Math.round(window.innerHeight * 2) + 'px 0px';

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var img = entry.target;
        io.unobserve(img);
        if (img.complete) return;
        // Umstellen auf "eager" stoesst das Laden sofort an.
        img.loading = 'eager';
      });
    }, { rootMargin: margin });

    document.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
      if (img.complete) return;
      io.observe(img);
    });
  }

  if (document.readyState === 'complete') start();
  else window.addEventListener('load', start);
})();
