"""Genera le pagine statiche del Radar a partire da data/issues.json.

Produce: index.html (ultimo numero), numeri/<id>.html (ogni numero),
sitemap.xml, robots.txt e inserisce i meta SEO in chi-sono, privacy e 404.
Uscita deterministica: se i dati non cambiano, i file non cambiano.
"""
import html
import json
import os
import re

SITE = "https://emilianodevenuti.it"
NAME = "Radar · Vino Cibo Olio"
AUTHOR = "Emiliano De Venuti"
ROOT = os.path.abspath(os.getcwd())
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
KEYWORDS = ("mercato del vino, consumi di vino in Italia, export vino italiano, "
            "prezzo olio extravergine, mercato olio d'oliva, consumi alimentari, "
            "agroalimentare italiano, turismo enogastronomico, enoturismo, "
            "turismo del gusto, Gen Z e vino, consumi per generazione, "
            "ristorazione e consumi fuori casa, tendenze di consumo, comportamento del consumatore")
DESC_SITE = ("Ogni lunedì i numeri del mercato del vino, dell'agroalimentare, dell'olio d'oliva "
             "e del turismo del gusto in Italia, con la lettura di come cambiano i consumatori, "
             "generazione per generazione. Ogni dato con fonte e link. A cura di Emiliano De Venuti.")
# Anni di nascita: definizione standard Pew Research Center.
GENS = {"gen z": (1997, 2012), "millennial": (1981, 1996), "gen x": (1965, 1980), "boomer": (1946, 1964)}
GEN_NOTE = ("Anni di nascita secondo la definizione standard (Pew Research Center); età calcolate sull'anno del numero, "
            "solo maggiorenni. Le fonti possono usare fasce d'età diverse: se succede è indicato nella nota.")


def gen_years(name, year):
    key = (name or "").lower().replace("millennials", "millennial").replace("baby boomer", "boomer").replace("boomers", "boomer")
    span = GENS.get(key.strip())
    if not span:
        return ""
    a, b = span
    lo, hi = max(18, year - b), year - a
    return f"nati {a}–{b} · {lo}–{hi} anni"


DRAFT = ""  # pubblicazione automatica firmata, senza etichetta bozza - 18/11/2026
ICON = ("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E"
        "%3Crect width=%2732%27 height=%2732%27 rx=%276%27 fill=%27%23fb3910%27/%3E%3Ctext x=%2716%27 "
        "y=%2723%27 font-family=%27Arial%27 font-weight=%27900%27 font-size=%2720%27 fill=%27white%27 "
        "text-anchor=%27middle%27%3ER%3C/text%3E%3C/svg%3E")


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def fmt(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MESI[int(m) - 1]} {y}"


def no(i):
    s = f"{i + 1:02d}"
    return f"{s[0]} {s[1]}"


def link(url, text):
    if url:
        return f'<a href="{e(url)}" target="_blank" rel="noopener">{e(text)} →</a>'
    return e(text)


def why(text):
    if not text:
        return ""
    return f'<details class="why"><summary>Cosa significa</summary><p>{e(text)}</p></details>'


def row(r):
    if isinstance(r, dict):
        return r.get("k"), r.get("v"), r.get("info")
    r = list(r) + ["", "", ""]
    return r[0], r[1], r[2] or None


def clip(text, n=158):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0].rstrip(",;:·-–")
    return cut + "…"


def issue_title(it):
    ct = (it.get("comportamento") or {}).get("title")
    if ct:
        return f"Il Comportamento · {ct} · Radar N. {it['number']}"
    names = [h.get("name") for h in it.get("highlights", []) if h.get("name")][:3]
    topic = ", ".join(names).lower() if names else "vino, cibo, olio e turismo del gusto"
    return f"Radar N. {it['number']} · {it['window']}: {topic}"


def issue_desc(it):
    c = it.get("comportamento") or {}
    if c.get("paragrafo"):
        return clip(plain(c["paragrafo"]))
    if it.get("summary"):
        return clip(" ".join(it["summary"]))
    if it.get("lettura", {}).get("text"):
        return clip(it["lettura"]["text"])
    return clip(DESC_SITE)


def head(title, desc, url, prefix, og_type="website", extra_ld=None, robots="index,follow"):
    ld = [{
        "@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/",
        "inLanguage": "it-IT", "description": DESC_SITE,
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/chi-sono.html"},
    }]
    if extra_ld:
        ld.append(extra_ld)
    ld_txt = json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False).replace("</", "<\\/")
    canon = (f'<link rel="canonical" href="{e(url)}">\n<link rel="alternate" hreflang="it" href="{e(url)}">') if url else ""
    ogurl = f'<meta property="og:url" content="{e(url)}">\n' if url else ""
    return f"""<!--seo-->
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(KEYWORDS)}">
<meta name="author" content="{AUTHOR}">
<meta name="robots" content="{robots}">
{canon}
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="it_IT">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{ogurl}<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og.png">
<link rel="sitemap" type="application/xml" href="{SITE}/sitemap.xml">
<script type="application/ld+json">{ld_txt}</script>
<script src="{SITE}/assets/consent.js" defer></script>
<!--/seo-->"""


def page(title, desc, url, prefix, body, nav_current, extra_ld=None, og_type="website", bar=""):
    p = prefix
    cur_key = nav_current if isinstance(nav_current, str) else ("home" if nav_current else "")
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<link rel="icon" href="{ICON}">
{head(title, desc, url, p, og_type, extra_ld)}
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body class="v-b">
<header class="top"><div class="wrap">
  <a class="brand" href="{p}index.html">Radar<span>.</span> Vino Cibo Olio</a>
  <nav class="nav">{nav_links(p, cur_key)}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
  <div><a class="brand" href="{p}index.html">Radar<span style="color:var(--accent)">.</span> Vino Cibo Olio</a>
  <p>Settimanale indipendente a cura di Emiliano De Venuti. Fonti pubbliche: istituti di statistica, associazioni, osservatori e stampa di settore. Dove la fonte è secondaria è indicato. I dati provvisori possono essere rivisti.</p></div>
  <div><div class="lab" style="color:#9a9a96">Esplora</div><p><a href="{p}index.html">Ultimo numero</a><br><a href="{p}il-comportamento.html">Il Comportamento</a><br><a href="{p}letture/index.html">Letture</a><br><a href="{p}index.html#archivio">Archivio</a><br><a href="{p}chi-sono.html">Chi sono</a></p></div>
  <div><div class="lab" style="color:#9a9a96">Legal</div><p><a href="{p}privacy.html">Privacy</a><br>emilianodevenuti.it © {datetime_year()}</p></div>
</div></footer>
<div class="bar"><div class="wrap"><span><b>Ogni lunedì</b> <span class="opt">· {e(bar)}</span></span><a href="{p}index.html#archivio">Archivio →</a></div></div>
<script src="{p}assets/app.js"></script>
</body>
</html>
"""


_YEAR = ["2026"]


def nav_links(p, cur_key=""):
    items = [("home", "index.html", "Ultimo numero", ""), ("comp", "il-comportamento.html", "Il Comportamento", ""),
             ("letture", "letture/index.html", "Letture", ""), ("arch", "index.html#archivio", "Archivio", "opt"),
             ("chi", "chi-sono.html", "Chi sono", "opt")]
    out = []
    for k, href, lbl, cls in items:
        a = ' aria-current="page"' if k == cur_key else ""
        c = f' class="{cls}"' if cls else ""
        out.append(f'<a href="{p}{href}"{c}{a}>{lbl}</a>')
    return "".join(out)


def datetime_year():
    return _YEAR[0]


LEVE = [("salute", "Salute e benessere"), ("tempo", "Tempo e stile di vita"), ("digitale", "Comunicazione e digitale"),
        ("valore", "Prezzi e valore"), ("socialita", "Socialità ed esperienze")]
LEVE_DESC = {
    "salute": "Si beve e si mangia pensando di più a come si sta.",
    "tempo": "Meno tempo, ritmi diversi, occasioni nuove.",
    "digitale": "Si scopre, si sceglie e si compra passando dallo schermo.",
    "valore": "Si spende con più attenzione e si cerca il senso di quello che si paga.",
    "socialita": "Conta il momento condiviso più del prodotto in sé.",
}


def rich(text):
    """Testo con **grassetto**: escape HTML e poi grassetto."""
    out = []
    for par in re.split(r"\n\s*\n", (text or "").strip()):
        par = e(par.strip())
        par = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", par)
        if par:
            out.append(f"<p>{par}</p>")
    return "".join(out)


def plain(text):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text or "")


def leve_html(active, prefix):
    active = set(active or [])
    chips = "".join(f'<li class="leva{" on" if k in active else ""}">{e(lbl)}</li>' for k, lbl in LEVE)
    return (f'<div class="leve"><div class="lab">Le leve del cambiamento</div><ul>{chips}</ul>'
            f'<a class="more" href="{prefix}il-comportamento.html">Cos\'è Il Comportamento →</a></div>')


def render_issue(it, issues, prefix):
    h = []
    c = it.get("comportamento") or {}
    title = c.get("title") or "I numeri della settimana su vino, cibo, olio e turismo del gusto."
    sub = c.get("sottotitolo") or "Ogni lunedì i numeri del mercato e la lettura di come cambia chi compra. Ogni dato con fonte e link."
    h.append('<section class="hero"><div class="wrap">')
    h.append(f'<div class="kick"><span class="pill">Il Comportamento · N. {e(it["number"])}</span><span class="lab">{e(fmt(it["date"]))} · settimana {e(it["window"])}</span></div>')
    h.append(f'<h1>{e(title)}</h1>')
    h.append(f'<p class="sub">{e(sub)}</p>')
    h.append(f'<div class="by">A cura di <b>{AUTHOR}</b></div>')
    h.append('</div></section>')

    if c:
        body = c.get("paragrafo") or c.get("intro") or ""
        h.append('<div class="wrap"><section class="comp" id="comportamento"><div class="lab">Il Comportamento della settimana</div>'
                 f'<div class="ctext">{rich(body)}<div class="sign">{AUTHOR}{DRAFT if c.get("draft") else ""}</div>'
                 '<p class="cnote">I numeri citati sono qui sotto, nelle prove, con fonte e link.</p></div>'
                 f'{leve_html(c.get("leve"), prefix)}</section></div>')
        if c.get("settori"):
            h.append('<div class="wrap"><section class="focus" id="focus"><div class="fhead"><div class="lab">Cosa cambia, settore per settore</div></div><div class="fgrid">')
            for x in c.get("settori", []):
                h.append(f'<article class="fcard" style="--sc:var(--c-{e(x.get("key"))})"><h3>{e(x.get("title"))}</h3><div class="lab">Cosa cambia</div><p>{e(x.get("cambia"))}</p>'
                         f'<div class="lab">L’opportunità</div><p class="op">{e(x.get("opportunita"))}</p></article>')
            h.append("</div></section></div>")

    gb = it.get("generazioni_box") or {}
    for k in ("vino", "ristorante"):
        g = gb.get(k)
        if not g:
            continue
        lab = "Consumo di vino" if k == "vino" else "Fuori casa"
        h.append(f'<div class="wrap"><section class="gens gens-{k}"><div class="ghead"><div class="lab">{lab} · per generazione</div><h2>{e(g.get("title"))}</h2>'
                 + (f'<p>{e(g["intro"])}</p>' if g.get("intro") else "") + '</div><div class="ggrid">')
        for cd in g.get("cards", []):
            yrs = gen_years(cd.get("gen"), int(it["date"][:4]))
            h.append(f'<article class="gcard"><h3>{e(cd.get("gen"))}</h3>' + (f'<div class="gyears">{e(yrs)}</div>' if yrs else ""))
            if cd.get("take"):
                h.append(f'<p class="take">{e(cd["take"])}</p>')
            h.append("<dl>")
            for r in cd.get("rows", []):
                k_, v_, info = row(r)
                cls = ("nd " if v_ == "n.d." else "") + ("nw" if len(str(v_ or "")) <= 12 else "")
                tip = f' title="{e(info)}"' if info else ""
                h.append(f'<div class="{cls.strip()}"{tip}><dt>{e(k_)}</dt><dd>{e(v_)}</dd></div>')
            h.append("</dl>")
            infos = [(row(r)[0], row(r)[2]) for r in cd.get("rows", []) if row(r)[2]]
            if infos:
                h.append('<details class="why"><summary>Cosa significano i dati</summary><ul>'
                         + "".join(f"<li><b>{e(k_)}</b>: {e(i_)}</li>" for k_, i_ in infos) + "</ul></details>")
            h.append("</article>")
        h.append("</div>")
        if g.get("note"):
            h.append(f'<p class="gnote">{e(g["note"])}</p>')
        h.append(f'<p class="gnote">{e(GEN_NOTE)}</p>')
        src = " · ".join(link(s.get("url"), s.get("source")) for s in g.get("sources", []))
        upd = f' · <span>ultimo controllo {e(fmt(g["updated"]))}</span>' if g.get("updated") else ""
        h.append(f'<div class="gsrc">Fonti: {src}{upd}</div></section></div>')

    h.append('<div class="wrap"><section class="proofs" id="prove"><div class="lab">Le prove</div><h2>I numeri della settimana</h2>'
             '<p class="psub">Ogni dato con fonte, periodo e link. Tocca un settore per aprirlo.</p></section></div>')

    if it.get("summary"):
        h.append('<div class="wrap"><section class="summary"><div class="lab">In sintesi</div><ul>')
        h += [f"<li>{e(s)}</li>" for s in it["summary"]]
        h.append("</ul></section></div>")

    if it.get("highlights"):
        h.append('<div class="wrap"><div class="nums">')
        for n in it["highlights"]:
            h.append(f'<div class="num"><div class="n">{e(n.get("name"))}</div><div class="v">{e(n.get("value"))}</div>'
                     + (f'<div class="l">{e(n["detail"])}</div>' if n.get("detail") else "")
                     + why(n.get("why"))
                     + f'<div class="s">{link(n.get("url"), n.get("source"))}</div></div>')
        h.append("</div></div>")

    if it.get("lettura"):
        L = it["lettura"]
        h.append(f'<div class="wrap"><section class="read"><div class="lab">La lettura dei mercati</div><div><h2>{e(L.get("title"))}</h2><p>{e(L.get("text"))}</p>'
                 f'<div class="sign">{AUTHOR}{DRAFT if L.get("draft") else ""}</div></div></section></div>')

    secs = it.get("sections", [])
    h.append('<div class="wrap"><nav class="toc" aria-label="Sezioni">')
    for i, s in enumerate(secs):
        h.append(f'<a href="#s-{e(s.get("key") or i)}">{e(s.get("title"))}</a>')
    h.append("</nav>")
    for i, s in enumerate(secs):
        key = s.get("key") or str(i)
        n_items = len(s.get("items") or [])
        cnt = f"{n_items} dat{'o' if n_items == 1 else 'i'}" if n_items else "nessuna novità"
        h.append(f'<details class="secd" id="s-{e(key)}" style="--sc:var(--c-{e(s.get("key") or "export")})">'
                 f'<summary><span class="no">{no(i)}</span><h3>{e(s.get("title"))}</h3><span class="cnt">{cnt}</span></summary><div class="secb">')
        if s.get("abstract"):
            h.append(f'<p class="abs">{e(s["abstract"])}</p>')
        if s.get("none"):
            h.append(f'<p class="none">{e(s["none"])}</p>')
        if s.get("items"):
            h.append('<ul class="items">')
            for x in s["items"]:
                num = f'<div class="inum">{e(x["num"])}</div>' if x.get("num") else ""
                h.append(f'<li>{num}<div class="t">{e(x.get("text"))}</div>{why(x.get("why"))}<div class="src">{link(x.get("url"), x.get("source"))}</div></li>')
            h.append("</ul>")
        if s.get("interpretation"):
            h.append(f'<p class="abs interp">{e(s["interpretation"])}</p>')
        h.append("</div></details>")
    h.append("</div>")

    h.append('<div class="wrap"><section class="arch" id="archivio"><h2>Archivio</h2><ol>')
    for x in issues:
        xt = (x.get("comportamento") or {}).get("title") or x["window"]
        h.append(f'<li><a href="{prefix}numeri/{e(x["id"])}.html"><span class="t">N. {e(x["number"])} · {e(fmt(x["date"]))}</span><span class="w">{e(xt)}</span></a></li>')
    h.append("</ol></section></div>")
    return "\n".join(h)


def article_ld(it, url, title, desc):
    return {
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": title[:110], "description": desc, "url": url,
        "mainEntityOfPage": url, "inLanguage": "it-IT",
        "datePublished": it["date"], "dateModified": (it.get("generazioni_box", {}).get("vino", {}) or {}).get("updated", it["date"]),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/chi-sono.html"},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "image": SITE + "/assets/og.png",
        "isPartOf": {"@type": "Periodical", "name": NAME, "url": SITE + "/"},
        "keywords": KEYWORDS,
    }


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    old = open(full, encoding="utf-8").read() if os.path.exists(full) else None
    if old != text:
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        print("scritto", path)


def inject_head(path, title, desc, url, robots="index,follow"):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return
    s = open(full, encoding="utf-8").read()
    s = re.sub(r"<!--seo-->.*?<!--/seo-->\n?", "", s, flags=re.S)
    s = re.sub(r'<meta (name="description"|property="og:[a-z]+")[^>]*>\n?', "", s)
    block = head(title, desc, url, "", robots=robots) + "\n"
    s = s.replace('<link rel="stylesheet"', block + '<link rel="stylesheet"', 1)
    write(path, s)


def render_blocks(blocks):
    out = []
    for b in blocks:
        if b.get("h"):
            out.append(f"<h2>{e(b['h'])}</h2>")
        if b.get("p"):
            out.append(rich(b["p"]))
        if b.get("ul"):
            out.append("<ul>" + "".join(f"<li>{rich(x)[3:-4]}</li>" for x in b["ul"]) + "</ul>")
    return "".join(out)


def build_static_pages(issues):
    letture = []
    lp = os.path.join(ROOT, "data", "letture.json")
    if os.path.exists(lp):
        letture = json.load(open(lp, encoding="utf-8"))
    letture.sort(key=lambda x: x.get("date", ""), reverse=True)
    bar = f"N. {issues[0]['number']} · {issues[0]['window']}" if issues else ""

    # Pagina manifesto
    prosecco = next((x for x in letture if x["slug"] == "perche-tutti-dicono-prosecco"), None)
    leve = "".join(f'<li><b>{e(lbl)}</b><span>{e(LEVE_DESC[k])}</span></li>' for k, lbl in LEVE)
    link_p = (f'<p><a class="more" href="letture/{prosecco["slug"]}.html">Leggi: {e(prosecco["title"])} →</a></p>' if prosecco else "")
    body = f"""<section class="hero"><div class="wrap"><div class="kick"><span class="pill">Il Comportamento</span></div>
<h1>Come cambia chi compra, quando cambia la società.</h1>
<p class="sub">Ogni lunedì leggo i numeri di vino, cibo, olio e turismo del gusto per capire una cosa sola: come cambia il comportamento delle persone, e perché.</p>
<div class="by">di <b>{AUTHOR}</b></div></div></section>
<div class="wrap"><article class="essay">
<h2>I numeri veri li fanno le persone normali</h2>
<p>Chi lavora nel vino parla di vitigni, territori e metodi. Chi lo beve sceglie per gusto, occasione e prezzo. I dati lo dicono chiaramente: per la maggior parte delle generazioni il vino preferito è il Prosecco. Per questo ogni mia lettura parte da come compra e da cosa immagina la persona comune, non da come ragiona il settore.</p>
{link_p}
<h2>Le 5 leve del cambiamento</h2>
<p>Ogni settimana segno quali sono in gioco. Sono il filo che lega i numeri alla vita di tutti i giorni.</p>
<ul class="levelist">{leve}</ul>
<h2>Come leggo i dati</h2>
<ul>
<li>Ogni cambiamento è un'evoluzione a cui chi produce può adattarsi, mai solo una crisi.</li>
<li>Ogni numero ha fonte, periodo e area. Se un dato non c'è, lo scrivo.</li>
<li>Parto da chi compra, non da chi produce.</li>
<li>Poche parole, chiare: si capisce al primo sguardo.</li>
</ul>
<p><a class="more" href="index.html#comportamento">Leggi Il Comportamento di questa settimana →</a></p>
</article></div>"""
    ttl = "Il Comportamento — come cambiano i consumi quando cambia la società · Emiliano De Venuti"
    dsc = ("Il Comportamento: la lettura settimanale di Emiliano De Venuti su come cambia il consumatore di vino, cibo e olio "
           "in funzione del cambiamento sociale. Le 5 leve, il metodo, i numeri con fonte.")
    write("il-comportamento.html", page(ttl, dsc, SITE + "/il-comportamento.html", "", body, "comp", None, "website", bar))

    # Letture: elenco
    items = "".join(f'<li><a href="{x["slug"]}.html"><span class="t">{e(x["title"])}</span>'
                    f'<span class="w">{e(x.get("subtitle", ""))} · {e(fmt(x["date"]))} · {x.get("minutes", 2)} min</span></a></li>' for x in letture)
    body = f"""<section class="hero"><div class="wrap"><div class="kick"><span class="pill">Letture</span></div>
<h1>Le letture che non scadono.</h1>
<p class="sub">Approfondimenti brevi per capire i comportamenti che stanno sotto ai numeri di ogni settimana.</p>
<div class="by">di <b>{AUTHOR}</b></div></div></section>
<div class="wrap"><section class="arch"><ol>{items}</ol></section></div>"""
    write("letture/index.html", page("Letture — Il Comportamento · Emiliano De Venuti",
                                     "Approfondimenti di Emiliano De Venuti sul comportamento del consumatore di vino, cibo e olio.",
                                     SITE + "/letture/index.html", "../", body, "letture", None, "website", bar))

    # Letture: singole pagine
    for x in letture:
        url = f"{SITE}/letture/{x['slug']}.html"
        src = " · ".join(link(s.get("url"), s.get("source")) for s in x.get("sources", []))
        body = f"""<section class="hero"><div class="wrap"><div class="kick"><span class="pill">Letture</span><span class="lab">{e(fmt(x["date"]))} · {x.get("minutes", 2)} minuti</span></div>
<h1>{e(x["title"])}</h1>
<p class="sub">{e(x.get("subtitle", ""))}</p>
<div class="by">Una lettura di <b>{AUTHOR}</b></div></div></section>
<div class="wrap"><article class="essay">{render_blocks(x.get("blocks", []))}
<div class="sign">{AUTHOR}</div>
<p class="gsrc">Fonti: {src}</p>
<p><a class="more" href="../il-comportamento.html">Cos'è Il Comportamento →</a></p></article></div>"""
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": x["title"], "description": x.get("description", ""),
              "url": url, "mainEntityOfPage": url, "inLanguage": "it-IT", "datePublished": x["date"],
              "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/chi-sono.html"},
              "publisher": {"@type": "Person", "name": AUTHOR}, "image": SITE + "/assets/og.png"}
        write(f"letture/{x['slug']}.html", page(f"{x['title']} — {x.get('subtitle', '')} · Emiliano De Venuti",
                                                 x.get("description", x.get("subtitle", "")), url, "../", body, "letture", ld, "article", bar))
    return letture


def fix_nav(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return
    s = open(full, encoding="utf-8").read()
    s2 = re.sub(r'<nav class="nav">.*?</nav>', '<nav class="nav">' + nav_links("", "chi" if path == "chi-sono.html" else "") + "</nav>", s, count=1, flags=re.S)
    if s2 != s:
        write(path, s2)


def main():
    issues = json.load(open(os.path.join(ROOT, "data", "issues.json"), encoding="utf-8"))
    issues.sort(key=lambda i: (i.get("date", ""), i.get("number", 0)), reverse=True)
    if issues:
        _YEAR[0] = issues[0]["date"][:4]

    for it in issues:
        url = f"{SITE}/numeri/{it['id']}.html"
        title = issue_title(it)
        desc = issue_desc(it)
        body = render_issue(it, issues, "../")
        write(f"numeri/{it['id']}.html",
              page(title + " — Radar", desc, url, "../", body, False, article_ld(it, url, title, desc), "article",
                   f"N. {it['number']} · {it['window']}"))

    if issues:
        it = issues[0]
        body = render_issue(it, issues, "")
        title = "Il Comportamento · Radar Vino Cibo Olio — come cambiano i consumi di vino, cibo e olio, ogni lunedì"
        write("index.html", page(title, DESC_SITE, SITE + "/", "", body, True,
                                 article_ld(it, f"{SITE}/numeri/{it['id']}.html", issue_title(it), issue_desc(it)),
                                 "website", f"N. {it['number']} · {it['window']}"))

    letture = build_static_pages(issues)
    for pth in ("chi-sono.html", "privacy.html", "404.html"):
        fix_nav(pth)
    inject_head("chi-sono.html", "Chi sono — Emiliano De Venuti · Radar Vino Cibo Olio",
                "Emiliano De Venuti cura il Radar: ogni lunedì numeri e lettura del mercato di vino, cibo, olio d'oliva e turismo del gusto in Italia.",
                SITE + "/chi-sono.html")
    inject_head("privacy.html", "Privacy — Radar · Vino Cibo Olio",
                "Informativa privacy del sito Radar · Vino Cibo Olio di Emiliano De Venuti.", SITE + "/privacy.html")
    inject_head("404.html", "Pagina non trovata — Radar", DESC_SITE, None, robots="noindex,follow")

    urls = [(SITE + "/", issues[0]["date"] if issues else None, "1.0")]
    urls += [(f"{SITE}/numeri/{x['id']}.html", x["date"], "0.8") for x in issues]
    urls += [(SITE + "/il-comportamento.html", None, "0.9"), (SITE + "/letture/index.html", letture[0]["date"] if letture else None, "0.7")]
    urls += [(f"{SITE}/letture/{x['slug']}.html", x["date"], "0.8") for x in letture]
    urls += [(SITE + "/chi-sono.html", None, "0.5"), (SITE + "/privacy.html", None, "0.2")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, d, p in urls:
        sm.append(f"  <url><loc>{e(u)}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + f"<priority>{p}</priority></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
