#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique le site : la racine (sélecteur JS, x-default) et sept pages statiques.

    python3 gen_site.py

Lit contenu.json et style.css. Écrit index.html et <lang>/index.html pour les sept
langues. Rien ne s'édite dans les fichiers produits : tout se corrige dans contenu.json.
"""
import json, os, html, sys

ICI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ICI, 'contenu.json'), encoding='utf-8'))
CSS = open(os.path.join(ICI, 'style.css'), encoding='utf-8').read().rstrip()

SITE, ORDRE, MAIL = D['site'], D['ordre'], D['mail']
L, EDITIONS = D['langues'], D['editions']
T = lambda s: html.escape(s, quote=False)   # texte : l'apostrophe reste une apostrophe
A = lambda s: html.escape(s, quote=True)    # valeur d'attribut : tout est échappé


def alternates(courant):
    """Le jeu hreflang complet, identique sur les huit pages."""
    out = ['<link rel="alternate" hreflang="x-default" href="%s/">' % SITE]
    for c in ORDRE:
        out.append('<link rel="alternate" hreflang="%s" href="%s/%s/">' % (c, SITE, c))
    return '\n'.join(out)


def tete(code, url):
    """<head> complet. code=None pour la racine, qui parle anglais."""
    x = L[code or 'en']
    lang_attr = code or 'en'
    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre_t}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{alt}
<link rel="icon" type="image/png" href="{site}/logo.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="La Direction du vent">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{locale}">
{oglang}<meta property="og:image" content="{site}/logo.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{titre}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}/logo.png">
<style>
{css}
</style>
</head>""".format(
        lang=lang_attr, titre=A(x['titre']), titre_t=T(x['titre']), desc=A(x['desc']), url=url,
        alt=alternates(code), site=SITE, locale=x['locale'],
        oglang=''.join('<meta property="og:locale:alternate" content="%s">\n' % L[c]['locale']
                       for c in ORDRE if L[c]['locale'] != x['locale']),
        css=CSS)


def picker_liens(courant):
    """Sélecteur des pages statiques : des liens, pas des boutons."""
    bouts = []
    for c in ORDRE:
        if c == courant:
            bouts.append('<span class="ici" lang="%s" aria-current="page">%s</span>' % (c, T(L[c]['nom'])))
        else:
            bouts.append('<a href="%s/%s/" lang="%s" hreflang="%s">%s</a>' % (SITE, c, c, c, T(L[c]['nom'])))
    return '<span class="sep">·</span>'.join(bouts)


def picker_boutons():
    """Sélecteur de la racine : les boutons d'origine, pilotés par le script."""
    bouts = ['<button type="button" data-go="%s" lang="%s">%s</button>' % (c, c, T(L[c]['nom']))
             for c in ORDRE]
    return '<span class="sep">·</span>'.join(bouts)


def liste_editions():
    li = []
    for x in EDITIONS:
        li.append(
            '    <li>\n'
            '      <span class="lang">%s</span>\n'
            '      <span class="ed-t" lang="%s">%s<span class="who">%s</span></span>\n'
            '      <span class="fmt" lang="%s"><a href="%s">%s</a><span class="dot">·</span>'
            '<a href="%s">%s</a></span>\n'
            '    </li>' % (x['code'], x['lang'], T(x['nom']), T(x['plume']), x['lang'],
                           x['u1'], T(x['f1']), x['u2'], T(x['f2'])))
    return '  <ul class="ed">\n' + '\n'.join(li) + '\n  </ul>'


def page_langue(code):
    x = L[code]
    url = '%s/%s/' % (SITE, code)
    return (tete(code, url) + """
<body>
<div class="sheet">

  <p class="rub">La Direction du vent</p>
  <h1>écrit de loin</h1>

  <nav class="picker" aria-label="{aria}">
    {picker}
  </nav>

  <hr class="keyline">

  <div lang="{code}">
    <p class="sub">{sub}</p>
    <p class="lede">{lede}</p>
  </div>

  <h2 class="hd">{hd_ed}</h2>

  <p class="nt" lang="{code}">{note}</p>

{editions}

  <h2 class="hd">{hd_ct}</h2>

  <div lang="{code}"><p>{contact}<br>
  <a class="mail" href="mailto:{mail}">{mail}</a></p></div>

  <footer>
    écrit de loin · La Direction du vent
    <span class="rights">© 2026 écrit de loin{droits}</span>
  </footer>

</div>
</body>
</html>
""".format(aria=A(x['aria_langue']), picker=picker_liens(code), code=code,
           sub=T(x['sub']), lede=T(x['lede']), hd_ed=T(x['hd_editions']),
           note=T(x['note']), editions=liste_editions(), hd_ct=T(x['hd_contact']),
           contact=T(x['contact']), mail=MAIL, droits=T(x['droits'])))


def page_racine():
    blocs_say = '\n'.join(
        '  <div class="say" data-lang="{c}" lang="{c}">\n'
        '    <p class="sub">{sub}</p>\n'
        '    <p class="lede">{lede}</p>\n'
        '  </div>\n'.format(c=c, sub=T(L[c]['sub']), lede=T(L[c]['lede'])) for c in ORDRE)
    blocs_nt = '\n'.join(
        '  <p class="nt" data-lang="{c}" lang="{c}">{t}</p>'.format(c=c, t=T(L[c]['note']))
        for c in ORDRE)
    blocs_ct = '\n'.join(
        '  <div class="ct" data-lang="{c}" lang="{c}"><p>{t}<br>\n'
        '  <a class="mail" href="mailto:{m}">{m}</a></p></div>'.format(
            c=c, t=T(L[c]['contact']), m=MAIL) for c in ORDRE)
    hd = lambda cle: json.dumps({c: L[c][cle] for c in ORDRE}, ensure_ascii=False)
    script = """<script>
(function(){{
  var LANGS = {langs};
  var HD = {{
    editions: {ed},
    contact:  {ct},
    rights:   {dr}
  }};
  var TITRE = {ti};
  var DESC  = {de};

  function pick(){{
    var q = new URLSearchParams(location.search).get("lang");
    if (q && LANGS.indexOf(q) > -1) return q;
    var stored = null;
    try {{ stored = localStorage.getItem("edl-lang"); }} catch(e){{}}
    if (stored && LANGS.indexOf(stored) > -1) return stored;
    var nav = (navigator.languages || [navigator.language || "fr"]);
    for (var i = 0; i < nav.length; i++){{
      var code = String(nav[i]).slice(0,2).toLowerCase();
      if (LANGS.indexOf(code) > -1) return code;
    }}
    return "en";
  }}

  function show(lang){{
    var blocks = document.querySelectorAll(".say, .ct, .nt");
    for (var i = 0; i < blocks.length; i++){{
      blocks[i].hidden = (blocks[i].getAttribute("data-lang") !== lang);
    }}
    var heads = document.querySelectorAll("[data-hd]");
    for (var j = 0; j < heads.length; j++){{
      var key = heads[j].getAttribute("data-hd");
      if (HD[key] && HD[key][lang]) heads[j].textContent = HD[key][lang];
    }}
    var btns = document.querySelectorAll("#picker button");
    for (var k = 0; k < btns.length; k++){{
      btns[k].setAttribute("aria-current", btns[k].getAttribute("data-go") === lang ? "true" : "false");
    }}
    document.documentElement.lang = lang;
    if (TITRE[lang]) document.title = TITRE[lang];
    var md = document.querySelector('meta[name="description"]');
    if (md && DESC[lang]) md.setAttribute("content", DESC[lang]);
    var pl = document.getElementById("plein");
    if (pl) pl.setAttribute("href", "{site}/" + lang + "/");
    try {{ localStorage.setItem("edl-lang", lang); }} catch(e){{}}
  }}

  document.getElementById("picker").addEventListener("click", function(ev){{
    var b = ev.target.closest("button[data-go]");
    if (b) show(b.getAttribute("data-go"));
  }});

  show(pick());
}})();
</script>""".format(langs=json.dumps(ORDRE), ed=hd('hd_editions'), ct=hd('hd_contact'),
                    dr=hd('droits'), ti=hd('titre'), de=hd('desc'), site=SITE)

    return (tete(None, SITE + '/') + """
<body>
<div class="sheet">

  <p class="rub">La Direction du vent</p>
  <h1>écrit de loin</h1>

  <nav class="picker" id="picker" aria-label="Language">
    {picker}
  </nav>

  <hr class="keyline">

{say}
  <h2 class="hd" data-hd="editions">Editions</h2>

{nt}

{editions}

  <h2 class="hd" data-hd="contact">Contact</h2>

{ct}

  <footer>
    écrit de loin · La Direction du vent
    <span class="rights">© 2026 écrit de loin<span class="hd-r" data-hd="rights"> · All rights reserved</span></span>
  </footer>

</div>
{script}
</body>
</html>
""".format(picker=picker_boutons(), say=blocs_say, nt=blocs_nt,
           editions=liste_editions(), ct=blocs_ct, script=script))


def ecrire(chemin, texte):
    d = os.path.dirname(chemin)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    open(chemin, 'w', encoding='utf-8').write(texte)
    return len(texte.encode('utf-8'))


def main():
    n = ecrire(os.path.join(ICI, 'index.html'), page_racine())
    print('  /                %6d octets   x-default, sélecteur' % n)
    for c in ORDRE:
        n = ecrire(os.path.join(ICI, c, 'index.html'), page_langue(c))
        print('  /%s/             %6d octets   %s' % (c, n, L[c]['titre']))
    # sitemap
    urls = ['%s/' % SITE] + ['%s/%s/' % (SITE, c) for c in ORDRE]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join('  <url><loc>%s</loc></url>\n' % u for u in urls)
          + '</urlset>\n')
    ecrire(os.path.join(ICI, 'sitemap.xml'), sm)
    ecrire(os.path.join(ICI, 'robots.txt'),
           'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)
    print('  sitemap.xml, robots.txt')


if __name__ == '__main__':
    main()
