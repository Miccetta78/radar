/* Radar — rende il numero corrente e l'archivio da data/issues.json (il più recente in cima). */
(function () {
  var MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  function fmt(iso) { var p = iso.split('-'); return parseInt(p[2], 10) + ' ' + MESI[+p[1] - 1] + ' ' + p[0]; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function pad(n) { return (n < 10 ? '0 ' : '') + String(n).split('').join(' ').replace(/^0 /, '0 '); }
  function no(i) { var s = String(i + 1).padStart(2, '0'); return s[0] + ' ' + s[1]; }

  function render(issues) {
    var id = (location.hash || '').slice(1);
    var it = issues.find(function (x) { return x.id === id; }) || issues[0];
    var main = document.getElementById('main');
    if (!it) { main.innerHTML = '<div class="wrap hero"><h1>Il primo numero esce lunedì.</h1></div>'; return; }
    var h = '';
    h += '<section class="hero"><div class="wrap">';
    h += '<div class="kick"><span class="pill">N. ' + it.number + '</span><span class="lab">' + esc(fmt(it.date)) + ' · settimana ' + esc(it.window) + '</span></div>';
    h += '<h1>I numeri della settimana su <em>vino, cibo, olio</em> e turismo del gusto.</h1>';
    h += '<p class="sub">Ogni lunedì i numeri del mercato e la lettura di come cambia chi compra. Ogni dato con fonte e link.</p>';
    h += '<div class="by">A cura di <b>Emiliano De Venuti</b></div>';
    h += '</div></section>';

    if (it.highlights && it.highlights.length) {
      h += '<div class="wrap"><div class="nums">';
      it.highlights.forEach(function (n) {
        h += '<div class="num"><div class="n">' + esc(n.name) + '</div><div class="v">' + esc(n.value) + '</div>' +
             (n.detail ? '<div class="l">' + esc(n.detail) + '</div>' : '') +
             '<div class="s">' + (n.url ? '<a href="' + esc(n.url) + '" target="_blank" rel="noopener">' + esc(n.source) + ' →</a>' : esc(n.source)) + '</div></div>';
      });
      h += '</div></div>';
    }

    if (it.generazioni_box) {
      ['vino', 'ristorante'].forEach(function (k) {
        var g = it.generazioni_box[k]; if (!g) return;
        h += '<div class="wrap"><section class="gens gens-' + k + '"><div class="ghead"><div class="lab">' + (k === 'vino' ? 'Consumo di vino' : 'Fuori casa') + ' · per generazione</div><h2>' + esc(g.title) + '</h2>' + (g.intro ? '<p>' + esc(g.intro) + '</p>' : '') + '</div><div class="ggrid">';
        g.cards.forEach(function (c) {
          h += '<article class="gcard"><h3>' + esc(c.gen) + '</h3><dl>';
          c.rows.forEach(function (r) { h += '<div class="' + (r[1] === 'n.d.' ? 'nd ' : '') + (String(r[1]).length <= 12 ? 'nw' : '') + '"><dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd></div>'; });
          h += '</dl></article>';
        });
        h += '</div><div class="gsrc">Fonti: ' + g.sources.map(function (s) { return '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.source) + ' →</a>'; }).join(' · ') + (g.updated ? ' · <span>ultimo controllo ' + esc(fmt(g.updated)) + '</span>' : '') + '</div></section></div>';
      });
    }

    if (it.lettura) {
      h += '<div class="wrap"><section class="read"><div class="lab">La lettura della settimana</div><div><h2>' + esc(it.lettura.title) + '</h2><p>' + esc(it.lettura.text) + '</p>' +
           '<div class="sign">Emiliano De Venuti' + (it.lettura.draft ? ' · <span class="draft">bozza da approvare</span>' : '') + '</div></div></section></div>';
    }

    if (it.comportamento) {
      var c = it.comportamento;
      h += '<div class="wrap"><section class="focus" id="focus"><div class="fhead"><div class="lab">Il focus · Consumatori e società</div><h2>' + esc(c.title) + '</h2><p>' + esc(c.intro) + '</p>' +
           '<div class="sign">Emiliano De Venuti' + (c.draft ? ' · <span class="draft">bozza da approvare</span>' : '') + '</div></div><div class="fgrid">';
      (c.settori || []).forEach(function (x) {
        h += '<article class="fcard" style="--sc:var(--c-' + esc(x.key) + ')"><h3>' + esc(x.title) + '</h3><div class="lab">Cosa cambia</div><p>' + esc(x.cambia) + '</p><div class="lab">L’opportunità</div><p class="op">' + esc(x.opportunita) + '</p></article>';
      });
      h += '</div></section></div>';
    }

    h += '<div class="wrap"><nav class="toc" aria-label="Sezioni">';
    it.sections.forEach(function (s, i) { h += '<a href="#' + it.id + '/' + (s.key || i) + '" data-sec="' + (s.key || i) + '">' + esc(s.title) + '</a>'; });
    h += '</nav>';
    it.sections.forEach(function (s, i) {
      h += '<section class="sec" id="s-' + (s.key || i) + '" style="--sc:var(--c-' + esc(s.key || 'export') + ')"><div class="h"><div class="no">' + no(i) + '</div><h3>' + esc(s.title) + '</h3></div><div>';
      if (s.abstract) h += '<p class="abs">' + esc(s.abstract) + '</p>';
      if (s.none) h += '<p class="none">' + esc(s.none) + '</p>';
      if (s.items && s.items.length) {
        h += '<ul class="items">';
        s.items.forEach(function (x) {
          h += '<li><div class="t">' + esc(x.text) + '</div><div class="src">' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.source) + ' →</a>' : esc(x.source)) + '</div></li>';
        });
        h += '</ul>';
      }
      h += '</div></section>';
    });
    h += '</div>';

    h += '<div class="wrap"><section class="arch" id="archivio"><h2>Archivio</h2><ol>';
    issues.forEach(function (x) { h += '<li><a href="#' + x.id + '"><span class="t">N. ' + x.number + ' · ' + esc(fmt(x.date)) + '</span><span class="w">' + esc(x.window) + '</span></a></li>'; });
    h += '</ol></section></div>';
    main.innerHTML = h;
    var bar = document.getElementById('bar-no'); if (bar) bar.textContent = 'N. ' + it.number + ' · ' + it.window;

    document.querySelectorAll('.toc a').forEach(function (a) {
      a.addEventListener('click', function (e) { e.preventDefault(); var t = document.getElementById('s-' + a.dataset.sec); if (t) t.scrollIntoView({behavior: 'smooth'}); });
    });
  }

  function start(data) { render(data); window.addEventListener('hashchange', function () { if (!/\//.test(location.hash)) { render(data); window.scrollTo(0, 0); } }); }
  if (window.ISSUES) start(window.ISSUES);
  else fetch('data/issues.json', {cache: 'no-cache'}).then(function (r) { return r.json(); }).then(start)
    .catch(function () { document.getElementById('main').innerHTML = '<div class="wrap hero"><p class="sub">Contenuti non disponibili. Riprova tra poco.</p></div>'; });
})();
