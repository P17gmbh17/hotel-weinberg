/* ==========================================================================
   Hotel Weinberg — Seitenübergang (Filmstreifen-Effekt)
   NUR bei Klicks innerhalb der Hauptnavigation (.main-nav, inkl. "Jetzt
   buchen"): ein kurzer Filmstreifen aus Vorschaubildern aller dazwischen-
   liegenden Seiten wird gezeigt (leicht geblurt), bevor die echte
   Navigation ausgeführt wird. Alle anderen Buttons/CTAs (Startseite,
   Footer, Inline-Links etc.) navigieren ganz normal ohne Effekt.
   Ankerlinks auf derselben Seite, externe Links (mailto/tel/http) und
   der Sprachwechsel bleiben ebenfalls unberührt.
   Setzt vor der echten Navigation ein sessionStorage-Flag, damit die
   Ziel-Seite ihren eigenen Intro-Vorhang überspringt (kein doppelter
   "Sprung" — siehe skip-curtain in styles.css).
   ========================================================================== */
(function () {
  var PAGE_ORDER = [
    'index.html',
    'philosophie.html',
    'zimmer.html',
    'geniessen.html',
    'aktivitaeten.html',
    'kulinarik.html',
    'kontakt.html'
  ];
  var THUMB_DIR = '../assets/previews/';
  var THUMBS = {
    'index.html': 'index.jpg',
    'philosophie.html': 'philosophie.jpg',
    'zimmer.html': 'zimmer.jpg',
    'geniessen.html': 'geniessen.jpg',
    'aktivitaeten.html': 'aktivitaeten.jpg',
    'kulinarik.html': 'kulinarik.jpg',
    'kontakt.html': 'kontakt.jpg'
  };

  function fileOf(pathname) {
    var f = pathname.substring(pathname.lastIndexOf('/') + 1);
    return f || 'index.html';
  }
  function dirOf(pathname) {
    return pathname.substring(0, pathname.lastIndexOf('/'));
  }

  var currentFile = fileOf(location.pathname);
  var currentDir = dirOf(location.pathname);
  var currentIndex = PAGE_ORDER.indexOf(currentFile);
  if (currentIndex === -1) return; // z.B. Root-Alias — kein Filmstreifen

  var overlay, track;
  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement('div');
    overlay.className = 'page-transition-overlay';
    track = document.createElement('div');
    track.className = 'page-transition-overlay__track';
    overlay.appendChild(track);
    document.body.appendChild(overlay);
  }

  function runTransition(fromIdx, toIdx, done) {
    ensureOverlay();
    var minIdx = Math.min(fromIdx, toIdx);
    var maxIdx = Math.max(fromIdx, toIdx);
    var steps = maxIdx - minIdx;

    track.innerHTML = '';
    var frames = [];
    for (var i = minIdx; i <= maxIdx; i++) {
      var frame = document.createElement('div');
      frame.className = 'page-transition-overlay__frame';
      frame.style.backgroundImage = "url('" + THUMB_DIR + THUMBS[PAGE_ORDER[i]] + "')";
      track.appendChild(frame);
      frames.push(frame);
    }

    var startX = -(fromIdx - minIdx) * 100;
    var endX = -(toIdx - minIdx) * 100;
    var duration = Math.min(1300, 450 + steps * 140);

    track.style.transition = 'none';
    track.style.transform = 'translateX(' + startX + 'vw)';
    frames.forEach(function (f) { f.style.animation = 'none'; });
    overlay.classList.add('is-active');
    void track.offsetWidth; /* reflow erzwingen */

    track.style.transition = 'transform ' + duration + 'ms cubic-bezier(0.65,0,0.35,1)';
    requestAnimationFrame(function () {
      track.style.transform = 'translateX(' + endX + 'vw)';
    });

    setTimeout(done, duration + 20);
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank') return;
    if (!a.closest('.main-nav')) return; /* nur Hauptnavigation, keine sonstigen CTAs/Buttons */

    var url;
    try { url = new URL(a.getAttribute('href'), location.href); } catch (err) { return; }
    if (url.protocol !== 'http:' && url.protocol !== 'https:' && url.protocol !== 'file:') return;
    if (url.origin !== location.origin && url.protocol !== 'file:') return;
    if (dirOf(url.pathname) !== currentDir) return; /* z.B. Sprachwechsel -> normal navigieren */

    var file = fileOf(url.pathname);
    var targetIndex = PAGE_ORDER.indexOf(file);
    if (targetIndex === -1 || file === currentFile) return; /* unbekannte Seite oder Anker auf derselben Seite */

    e.preventDefault();
    runTransition(currentIndex, targetIndex, function () {
      window.location.href = a.href;
    });
  });
})();
