/* Radar · consenso cookie e Google Analytics 4 (G-NVT8F1TZBX).
   Analytics si carica SOLO dopo "Accetta". Senza scelta o con "Rifiuta" nessun cookie di statistica. */
(function () {
  var ID = 'G-NVT8F1TZBX', KEY = 'radar_consenso_v1', loaded = false;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function loadGA() {
    if (loaded) return; loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'granted' });
    window.gtag('js', new Date());
    window.gtag('config', ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
    document.head.appendChild(s);
  }
  function clearGA() {
    var host = location.hostname, doms = ['', host, '.' + host, '.' + host.replace(/^www\./, '')];
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (/^_ga/.test(n)) doms.forEach(function (d) {
        document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }
  function css() {
    if (document.getElementById('rc-css')) return;
    var st = document.createElement('style'); st.id = 'rc-css';
    st.textContent = '#rc{position:fixed;left:0;right:0;bottom:0;z-index:1000;background:#fff;color:#1d1d1b;border-top:1px solid #e2e2df;box-shadow:0 -6px 24px rgba(0,0,0,.06)}' +
      '#rc .in{max-width:1120px;margin:0 auto;padding:16px;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}' +
      '#rc p{margin:0;font-size:14px;line-height:1.5;flex:1 1 320px}#rc a{color:inherit}' +
      '#rc .bt{display:flex;gap:8px;flex:0 0 auto}#rc button{font:inherit;font-size:14px;font-weight:600;padding:10px 18px;border-radius:999px;cursor:pointer;border:1px solid #1d1d1b}' +
      '#rc .ok{background:#1d1d1b;color:#fff}#rc .no{background:#fff;color:#1d1d1b}';
    document.head.appendChild(st);
  }
  function banner() {
    if (document.getElementById('rc')) return;
    css();
    var root = /\/numeri\//.test(location.pathname) ? '../' : '';
    var d = document.createElement('div'); d.id = 'rc'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Preferenze cookie');
    d.innerHTML = '<div class="in"><p>Con il tuo consenso usiamo Google Analytics per contare le visite in forma aggregata e capire quali contenuti interessano di più. Nessuna pubblicità, nessuna profilazione. Se rifiuti il sito funziona allo stesso modo. <a href="' + root + 'privacy.html">Informativa privacy</a></p>' +
      '<div class="bt"><button type="button" class="no">Rifiuta</button><button type="button" class="ok">Accetta</button></div></div>';
    document.body.appendChild(d);
    d.querySelector('.ok').onclick = function () { set('granted'); d.remove(); loadGA(); };
    d.querySelector('.no').onclick = function () {
      var was = loaded; set('denied'); d.remove(); clearGA(); if (was) location.reload();
    };
  }
  window.radarCookie = function () { banner(); return false; };
  function footerLink() {
    var a = document.querySelector('footer a[href$="privacy.html"]');
    if (!a || document.getElementById('rc-link')) return;
    var l = document.createElement('a'); l.id = 'rc-link'; l.href = '#'; l.textContent = 'Preferenze cookie';
    l.onclick = function (e) { e.preventDefault(); banner(); };
    a.parentNode.insertBefore(document.createElement('br'), a.nextSibling);
    a.parentNode.insertBefore(l, a.nextSibling.nextSibling);
  }
  function init() {
    footerLink();
    var v = get();
    if (v === 'granted') loadGA(); else if (v !== 'denied') banner();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
