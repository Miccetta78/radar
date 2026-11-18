/* Radar — le pagine sono statiche (generate da .github/scripts/build.py).
   Qui solo: vecchi link #<id-numero> -> pagina del numero; indice che apre e scorre al settore. */
(function () {
  var h = (location.hash || '').slice(1);
  if (/^n-\d{4}-\d{2}-\d{2}$/.test(h)) {
    var base = /\/numeri\//.test(location.pathname) ? '' : 'numeri/';
    location.replace(base + h + '.html');
    return;
  }
  function openTarget(sel) {
    var t = document.querySelector(sel);
    if (t && t.tagName === 'DETAILS') t.open = true;
    return t;
  }
  if (/^s-/.test(h)) openTarget('#' + h);
  document.querySelectorAll('.toc a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var t = openTarget(a.getAttribute('href'));
      if (t) { e.preventDefault(); t.scrollIntoView({behavior: 'smooth'}); history.replaceState(null, '', a.getAttribute('href')); }
    });
  });
})();
