#!/usr/bin/env python3
"""Generate blog article pages for La Bible de l'IA."""

import os, sys, html, datetime

# Import blog articles data
from blog_articles import get_blog_articles

DOMAIN = "https://labibledelia.com"
BASE_DIR = r"C:\Users\Loïc\Desktop\labibledelai"
TODAY = datetime.date.today().isoformat()


def get_shared_css():
    """Blog article page CSS."""
    return """
:root{
  --bg-page:#0e0e1a;--bg-card:#181830;--bg-card-hover:#1e1e3a;
  --text-main:#e8e8f0;--text-muted:#9898b0;--text-heading:#f8f8ff;
  --gold:#c9a84c;--gold-hover:#e0c068;
  --accent:#6366f1;--accent-hover:#818cf8;
  --radius-md:12px;--radius-lg:18px;
  --shadow-md:0 4px 20px rgba(0,0,0,.3);--shadow-lg:0 8px 40px rgba(0,0,0,.4);
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg-page);color:var(--text-main);line-height:1.7;min-height:100vh}
a{color:var(--gold);text-decoration:none;transition:color .2s}
a:hover{color:var(--gold-hover)}

/* NAV */
.top-nav{position:sticky;top:0;z-index:1000;background:rgba(14,14,26,.92);backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(201,168,76,.12);padding:.7rem 2rem;display:flex;align-items:center;gap:.8rem}
.nav-logo svg{width:26px;height:26px}
.nav-title{font-family:Georgia,serif;font-size:1rem;color:var(--gold);font-weight:600;letter-spacing:.5px}
.nav-links{margin-left:auto;display:flex;gap:1.2rem;align-items:center}
.nav-links a{color:var(--text-muted);font-size:.85rem;font-weight:500}
.nav-links a:hover{color:var(--gold)}
.lang-btn{display:inline-flex;align-items:center;padding:2px 6px;border-radius:4px;opacity:.7;transition:opacity .2s}
.lang-btn:hover,.lang-btn.active{opacity:1;background:rgba(255,255,255,.08)}
.lang-btn img{width:22px;height:16px;border-radius:2px;display:block}

/* BREADCRUMB */
.breadcrumb{padding:1rem 0;font-size:.85rem;color:var(--text-muted)}
.breadcrumb a{color:var(--text-muted)}
.breadcrumb a:hover{color:var(--gold)}
.breadcrumb .sep{margin:0 .5rem;opacity:.5}

/* ARTICLE */
.article-container{max-width:780px;margin:0 auto;padding:2rem 1.5rem}
.article-header{text-align:center;padding:2rem 0 2.5rem;border-bottom:1px solid rgba(201,168,76,.15);margin-bottom:2.5rem}
.article-emoji{font-size:3rem;margin-bottom:1rem}
.article-tag{display:inline-block;font-family:'Courier New',monospace;font-size:.7rem;color:var(--gold);
  text-transform:uppercase;letter-spacing:.15em;padding:.3rem .8rem;border:1px solid rgba(201,168,76,.3);
  border-radius:20px;margin-bottom:1rem}
.article-title{font-family:Georgia,serif;font-size:2.2rem;color:var(--text-heading);line-height:1.3;margin-bottom:.8rem}
.article-meta{display:flex;justify-content:center;gap:1.5rem;font-size:.8rem;color:var(--text-muted);font-family:'Courier New',monospace}
.article-desc{font-size:1.1rem;color:var(--text-muted);font-style:italic;margin-top:1rem;line-height:1.6}

/* ARTICLE CONTENT */
.article-content{font-size:1.05rem;line-height:1.85;color:var(--text-main)}
.article-content h2{font-family:Georgia,serif;font-size:1.5rem;color:var(--gold);margin:2.5rem 0 1rem;
  padding-bottom:.5rem;border-bottom:1px solid rgba(201,168,76,.15)}
.article-content h3{font-family:Georgia,serif;font-size:1.15rem;color:var(--text-heading);margin:1.8rem 0 .8rem}
.article-content p{margin-bottom:1.2rem}
.article-content ul,.article-content ol{margin:1rem 0 1.5rem 1.5rem}
.article-content li{margin-bottom:.5rem;line-height:1.7}
.article-content strong{color:var(--text-heading)}
.article-content blockquote{border-left:3px solid var(--gold);padding:.8rem 1.2rem;margin:1.5rem 0;
  background:rgba(201,168,76,.05);border-radius:0 var(--radius-md) var(--radius-md) 0;font-style:italic}
.article-content table{width:100%;border-collapse:collapse;margin:1.5rem 0}
.article-content th,.article-content td{padding:.6rem .8rem;text-align:left;border-bottom:1px solid rgba(255,255,255,.06)}
.article-content th{color:var(--text-muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}

/* CTA */
.article-cta{background:linear-gradient(135deg,rgba(201,168,76,.1),rgba(99,102,241,.1));
  border:1px solid rgba(201,168,76,.25);border-radius:var(--radius-lg);padding:2rem;margin:3rem 0;text-align:center}
.article-cta h3{font-family:Georgia,serif;color:var(--text-heading);font-size:1.2rem;margin-bottom:.5rem}
.article-cta p{color:var(--text-muted);font-size:.9rem;margin-bottom:1rem}
.btn-primary{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 1.5rem;background:var(--gold);
  color:#0e0e1a;font-weight:700;border-radius:8px;font-size:.95rem;transition:all .2s}
.btn-primary:hover{background:var(--gold-hover);color:#0e0e1a;transform:translateY(-1px)}

/* RELATED ARTICLES */
.related-section{margin-top:3rem;padding-top:2rem;border-top:1px solid rgba(201,168,76,.15)}
.related-title{font-family:Georgia,serif;font-size:1.3rem;color:var(--gold);margin-bottom:1.5rem}
.related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem}
.related-card{background:var(--bg-card);border:1px solid rgba(255,255,255,.06);border-radius:var(--radius-md);
  padding:1rem;transition:all .3s;display:block;color:var(--text-main);text-decoration:none}
.related-card:hover{background:var(--bg-card-hover);border-color:rgba(201,168,76,.3);transform:translateY(-2px)}
.related-card .rc-emoji{font-size:1.5rem;margin-bottom:.4rem}
.related-card .rc-tag{font-family:'Courier New',monospace;font-size:.6rem;color:var(--gold);text-transform:uppercase;letter-spacing:.1em}
.related-card .rc-title{font-weight:700;font-size:.9rem;color:var(--text-heading);margin-top:.3rem;line-height:1.3}

/* FOOTER */
.site-footer{background:rgba(0,0,0,.3);border-top:1px solid rgba(201,168,76,.1);padding:2rem;text-align:center;margin-top:4rem}
.footer-logo{font-family:Georgia,serif;font-size:1rem;color:var(--gold);margin-bottom:.5rem}
.footer-links{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;margin:.8rem 0}
.footer-links a{color:var(--text-muted);font-size:.8rem}
.footer-links a:hover{color:var(--gold)}
.footer-copy{color:var(--text-muted);font-size:.75rem;margin-top:.8rem}

@media(max-width:768px){
  .top-nav{padding:.5rem 1rem;gap:.5rem}
  .article-container{padding:1.5rem 1rem}
  .article-title{font-size:1.6rem}
  .article-content{font-size:.95rem}
  .related-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:480px){
  .related-grid{grid-template-columns:1fr}
}
"""


def get_nav_html(lang):
    home = f"/{lang}/"
    other_lang = "en" if lang == "fr" else "fr"
    title = "La Bible de l'IA" if lang == "fr" else "The AI Bible"
    cat_label = "Catalogue" if lang == "fr" else "Catalog"
    blog_label = "Blog" if lang == "fr" else "Blog"

    return f'''<nav class="top-nav">
  <a href="{home}" class="nav-logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:var(--gold)"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg></a>
  <a href="{home}" class="nav-title">{title}</a>
  <div class="nav-links">
    <a href="{home}#catalogue">{cat_label}</a>
    <a href="{home}#blog">{blog_label}</a>
    <a href="/{other_lang}/" class="lang-btn"><img src="https://flagcdn.com/w40/{'gb' if lang=='fr' else 'fr'}.png" alt="{other_lang.upper()}"></a>
  </div>
</nav>'''


def get_footer_html(lang):
    if lang == "fr":
        return '''<footer class="site-footer">
  <div class="footer-logo">La Bible de l'IA</div>
  <div class="footer-links">
    <a href="/fr/">Accueil</a>
    <a href="/fr/#catalogue">Catalogue</a>
    <a href="/fr/#blog">Blog</a>
    <a href="/fr/#newsletter">Newsletter</a>
  </div>
  <div class="footer-copy">&copy; 2026 La Bible de l'IA. Tous droits r&eacute;serv&eacute;s.</div>
</footer>'''
    else:
        return '''<footer class="site-footer">
  <div class="footer-logo">The AI Bible</div>
  <div class="footer-links">
    <a href="/en/">Home</a>
    <a href="/en/#catalogue">Catalog</a>
    <a href="/en/#blog">Blog</a>
    <a href="/en/#newsletter">Newsletter</a>
  </div>
  <div class="footer-copy">&copy; 2026 The AI Bible. All rights reserved.</div>
</footer>'''


def generate_blog_page(article, all_articles, lang):
    """Generate a full blog article page."""
    slug = article['slug']
    tag = article['tag_fr'] if lang == 'fr' else article['tag_en']
    title = article['title_fr'] if lang == 'fr' else article['title_en']
    desc = article['desc_fr'] if lang == 'fr' else article['desc_en']
    content = article['content_fr'] if lang == 'fr' else article['content_en']
    time_read = article['time']
    emoji = article['emoji']

    page_url = f"{DOMAIN}/{lang}/blog/{slug}/"
    alt_lang = 'en' if lang == 'fr' else 'fr'
    alt_url = f"{DOMAIN}/{alt_lang}/blog/{slug}/"
    home_url = f"/{lang}/"

    if lang == "fr":
        seo_title = f"{title} | La Bible de l'IA"
        breadcrumb_home = "Accueil"
        breadcrumb_blog = "Blog"
        read_time_label = f"{time_read} de lecture"
        date_label = "F&eacute;vrier 2026"
        cta_title = "Explorez notre catalogue de 200 outils IA"
        cta_desc = "D&eacute;couvrez, comparez et choisissez les meilleurs outils d'intelligence artificielle."
        cta_btn = "Voir le catalogue"
        related_title = "Articles recommand&eacute;s"
    else:
        seo_title = f"{title} | The AI Bible"
        breadcrumb_home = "Home"
        breadcrumb_blog = "Blog"
        read_time_label = f"{time_read} read"
        date_label = "February 2026"
        cta_title = "Explore our catalog of 200 AI tools"
        cta_desc = "Discover, compare and choose the best artificial intelligence tools."
        cta_btn = "View catalog"
        related_title = "Recommended articles"

    # Build related articles (exclude current)
    related_html = ""
    for a in all_articles:
        if a['slug'] == slug:
            continue
        a_tag = a['tag_fr'] if lang == 'fr' else a['tag_en']
        a_title = a['title_fr'] if lang == 'fr' else a['title_en']
        related_html += f'''<a href="/{lang}/blog/{a['slug']}/" class="related-card">
      <div class="rc-emoji">{a['emoji']}</div>
      <div class="rc-tag">{a_tag}</div>
      <div class="rc-title">{a_title}</div>
    </a>\n'''

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(seo_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="{lang}" href="{page_url}">
<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">
<meta property="og:title" content="{html.escape(seo_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="article:published_time" content="2026-02-01">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(seo_title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{html.escape(title)}",
  "description": "{html.escape(desc)}",
  "datePublished": "2026-02-01",
  "dateModified": "2026-02-06",
  "author": {{"@type": "Organization", "name": "La Bible de l'IA", "url": "https://labibledelia.com"}},
  "publisher": {{"@type": "Organization", "name": "La Bible de l'IA", "url": "https://labibledelia.com"}},
  "mainEntityOfPage": "{page_url}",
  "inLanguage": "{lang}"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "{breadcrumb_home}", "item": "https://labibledelia.com/{lang}/"}},
    {{"@type": "ListItem", "position": 2, "name": "{breadcrumb_blog}", "item": "https://labibledelia.com/{lang}/#blog"}},
    {{"@type": "ListItem", "position": 3, "name": "{html.escape(title)}", "item": "{page_url}"}}
  ]
}}
</script>
<style>{get_shared_css()}</style>
</head>
<body>
{get_nav_html(lang)}

<div class="article-container">

<div class="breadcrumb">
  <a href="{home_url}">{breadcrumb_home}</a>
  <span class="sep">&rsaquo;</span>
  <a href="{home_url}#blog">{breadcrumb_blog}</a>
  <span class="sep">&rsaquo;</span>
  <span>{tag}</span>
</div>

<header class="article-header">
  <div class="article-emoji">{emoji}</div>
  <span class="article-tag">{tag}</span>
  <h1 class="article-title">{title}</h1>
  <div class="article-meta">
    <span>&#128214; {read_time_label}</span>
    <span>&bull;</span>
    <span>{date_label}</span>
  </div>
  <p class="article-desc">{desc}</p>
</header>

<article class="article-content">
{content}
</article>

<div class="article-cta">
  <h3>{cta_title}</h3>
  <p>{cta_desc}</p>
  <a href="{home_url}#catalogue" class="btn-primary">&#128218; {cta_btn}</a>
</div>

<div class="related-section">
  <h2 class="related-title">{related_title}</h2>
  <div class="related-grid">
    {related_html}
  </div>
</div>

</div>

{get_footer_html(lang)}
</body>
</html>'''

    return page_html


def main():
    articles = get_blog_articles()

    print("=" * 50)
    print("  Blog Article Generator")
    print("=" * 50)

    generated = 0

    for lang in ['fr', 'en']:
        print(f"\nGenerating {lang.upper()} blog articles...")
        for article in articles:
            slug = article['slug']
            dir_path = os.path.join(BASE_DIR, lang, "blog", slug)
            os.makedirs(dir_path, exist_ok=True)

            page = generate_blog_page(article, articles, lang)
            # Fix surrogate pairs from source: encode to utf-16 then back to utf-8
            page = page.encode('utf-16', errors='surrogatepass').decode('utf-16')
            filepath = os.path.join(dir_path, "index.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page)
            generated += 1

            title = article[f'title_{lang}']
            print(f"  -> {slug}/ ({title[:50]}...)")

    print(f"\nDone! {generated} blog pages generated.")
    print(f"  {BASE_DIR}/fr/blog/  ({len(articles)} articles)")
    print(f"  {BASE_DIR}/en/blog/  ({len(articles)} articles)")


if __name__ == "__main__":
    main()
