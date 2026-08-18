/* ==========================================================================
   Hintergrund-Vorausladen der uebrigen Seiten
   --------------------------------------------------------------------------
   Waehrend der Gast auf der aktuellen Seite liest, laedt der Browser im
   Hintergrund schon die Inhalte der anderen Seiten. Wechselt der Gast dann
   auf "Zimmer" oder "Geniessen", ist der Kopfbereich sofort da statt erst
   nach dem Klick zu laden.

   Reihenfolge (bewusst zweistufig):
     1. die Header-/Hero-Bilder aller uebrigen Navigationsseiten
     2. erst danach die HTML-Seiten selbst

   Drei Schutzmechanismen, damit das nie zulasten der aktuellen Seite geht:
     - startet erst nach dem "load"-Event, also wenn die aktuelle Seite
       vollstaendig geladen ist
     - laeuft dann nur in einer Leerlaufphase des Browsers
       (requestIdleCallback)
     - rel="prefetch" ist die niedrigste Prioritaetsstufe des Browsers und
       wird bei Bedarf zugunsten echter Anfragen zurueckgestellt

   Ausserdem passiert gar nichts bei aktiviertem Datensparmodus oder auf
   langsamen Mobilverbindungen - dort waere Vorausladen reine
   Datenverschwendung.

   Die Liste der Adressen wird beim Build von build_seo.py als JSON in die
   Seite geschrieben (<script id="prefetch-manifest">), getrennt nach
   Desktop- und Mobilmotiven.
   ========================================================================== */
(function () {
  var el = document.getElementById('prefetch-manifest');
  if (!el) return;

  var data;
  try { data = JSON.parse(el.textContent); } catch (e) { return; }
  if (!data) return;

  // Datensparmodus oder langsame Verbindung: nichts vorausladen.
  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn) {
    if (conn.saveData) return;
    if (/(^|-)2g$/.test(conn.effectiveType || '')) return;
  }

  // Auf Mobilgeraeten die kleineren Hochformat-Motive vorausladen, sonst
  // wuerde das Handy grosse Desktop-Dateien holen, die es nie anzeigt.
  var isMobile = window.matchMedia('(max-width: 780px)').matches;
  var images = (isMobile ? data.mobile : data.desktop) || [];
  var docs = data.docs || [];

  var done = {};
  function prefetch(href, as) {
    if (!href || done[href]) return;
    done[href] = true;
    var link = document.createElement('link');
    link.rel = 'prefetch';
    if (as) link.as = as;
    link.href = href;
    document.head.appendChild(link);
  }

  function run() {
    // Stufe 1: Kopfbereiche
    images.forEach(function (url) { prefetch(url, 'image'); });

    // Stufe 2: die Seiten selbst, mit Abstand, damit Stufe 1 Vorrang hat
    setTimeout(function () {
      docs.forEach(function (url) { prefetch(url, 'document'); });
    }, 2000);
  }

  function start() {
    if (window.requestIdleCallback) {
      requestIdleCallback(run, { timeout: 4000 });
    } else {
      setTimeout(run, 1500);
    }
  }

  if (document.readyState === 'complete') start();
  else window.addEventListener('load', start);
})();
