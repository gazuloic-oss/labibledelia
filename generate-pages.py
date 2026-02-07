#!/usr/bin/env python3
"""
La Bible de l'IA — Multi-page generator
Generates individual tool pages, category pages, comparison pages,
sitemap.xml and robots.txt from the existing single-file HTML data.
"""

import json, re, os, html, datetime, unicodedata

DOMAIN = "https://labibledelia.com"
BASE_DIR = r"C:\Users\Loïc\Desktop\labibledelai"
TODAY = datetime.date.today().isoformat()

# ============================================================
# 1. EXTRACT DATA FROM HTML FILES
# ============================================================

def extract_js_array(filepath, var_name):
    """Extract a JS array variable from an HTML file using robust tokenization."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the variable declaration
    pattern = rf'const {var_name}\s*=\s*\['
    match = re.search(pattern, content)
    if not match:
        raise ValueError(f"Could not find {var_name} in {filepath}")

    arr_start = match.end()  # position right after the [

    # The source uses double-quoted strings only.
    # Extract objects by tracking { } depth, respecting strings.
    region = content[arr_start:]

    objects = []
    depth = 0
    obj_start = None
    in_string = False

    i = 0
    while i < len(region):
        ch = region[i]
        if in_string:
            if ch == '\\':
                i += 2  # skip escaped character
                continue
            if ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '{':
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and obj_start is not None:
                    obj_str = region[obj_start:i+1]
                    parsed = js_object_to_python(obj_str)
                    if parsed:
                        objects.append(parsed)
                    obj_start = None
            elif ch == ']' and depth == 0:
                break
        i += 1

    return objects


def js_object_to_python(js_obj):
    """Convert a single JS object literal {key:"val",...} to a Python dict."""
    try:
        # Quote unquoted property keys: id:"..." -> "id":"..."
        result = re.sub(r'(?<=[{,])\s*([a-zA-Z_]\w*)\s*:', r'"\1":', js_obj)
        # Remove trailing commas before } or ]
        result = re.sub(r',\s*([}\]])', r'\1', result)
        return json.loads(result)
    except (json.JSONDecodeError, Exception):
        return None


def extract_css(filepath):
    """Extract the full <style> block from the HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    return match.group(1) if match else ""


def extract_nav_and_footer(filepath):
    """Extract key HTML snippets from the original file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract nav
    nav_match = re.search(r'(<nav.*?</nav>)', content, re.DOTALL)
    nav = nav_match.group(1) if nav_match else ""

    # Extract footer
    footer_match = re.search(r'(<footer.*?</footer>)', content, re.DOTALL)
    footer = footer_match.group(1) if footer_match else ""

    return nav, footer


# ============================================================
# 2. SLUG GENERATION
# ============================================================

def slugify(text):
    """Convert text to URL-safe slug."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


# ============================================================
# 3. HTML TEMPLATES
# ============================================================

def get_shared_css():
    """Return the shared CSS for all generated pages."""
    return """
:root{
  --bg-page:#0e0e1a;--bg-card:#181830;--bg-card-hover:#1e1e3a;
  --text-main:#e8e8f0;--text-muted:#9898b0;--text-heading:#f8f8ff;
  --gold:#c9a84c;--gold-hover:#e0c068;
  --accent:#6366f1;--accent-hover:#818cf8;
  --radius-md:12px;--radius-lg:18px;
  --shadow-md:0 4px 20px rgba(0,0,0,.3);--shadow-lg:0 8px 40px rgba(0,0,0,.4);
  --cat-chatbots:#6366f1;--cat-texte:#f59e0b;--cat-image:#ec4899;
  --cat-video:#ef4444;--cat-audio:#8b5cf6;--cat-code:#10b981;
  --cat-marketing:#f97316;--cat-productivite:#06b6d4;--cat-education:#14b8a6;
  --cat-automation:#3b82f6;--cat-recherche:#6d28d9;--cat-design-web:#d946ef;
  --cat-reunions-email:#0ea5e9;--cat-carriere:#84cc16;--cat-finance:#f43f5e;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg-page);color:var(--text-main);line-height:1.7;min-height:100vh}
a{color:var(--gold);text-decoration:none;transition:color .2s}
a:hover{color:var(--gold-hover)}
.container{max-width:900px;margin:0 auto;padding:2rem 1.5rem}

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

/* TOOL PAGE */
.tool-header{display:flex;gap:1.5rem;align-items:flex-start;margin-bottom:2rem;flex-wrap:wrap}
.tool-icon{font-size:3rem;line-height:1}
.tool-title-group{flex:1;min-width:200px}
.tool-name{font-family:Georgia,serif;font-size:2rem;color:var(--text-heading);margin-bottom:.3rem}
.tool-tagline{font-size:1.1rem;color:var(--text-muted);font-style:italic}
.tool-meta{display:flex;flex-wrap:wrap;gap:.8rem;margin:1.5rem 0}
.meta-badge{display:inline-flex;align-items:center;gap:.3rem;padding:.3rem .7rem;border-radius:20px;font-size:.78rem;font-weight:600;background:rgba(99,102,241,.15);color:var(--accent)}
.meta-badge.pricing-gratuit{background:rgba(16,185,129,.15);color:#10b981}
.meta-badge.pricing-freemium{background:rgba(245,158,11,.15);color:#f59e0b}
.meta-badge.pricing-payant{background:rgba(239,68,68,.15);color:#ef4444}
.meta-badge.cat{background:rgba(99,102,241,.12)}
.stars{color:var(--gold);font-size:.9rem;letter-spacing:1px}

.section-title{font-family:Georgia,serif;font-size:1.3rem;color:var(--gold);margin:2rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid rgba(201,168,76,.15)}
.tool-description{font-size:1.05rem;line-height:1.8;color:var(--text-main);margin-bottom:1.5rem}
.pricing-note{background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:var(--radius-md);padding:1rem 1.2rem;margin:1rem 0;font-size:.95rem}
.pricing-note strong{color:var(--gold)}

.feature-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:.8rem;margin:1rem 0}
.feature-item{display:flex;align-items:flex-start;gap:.5rem;padding:.5rem;background:rgba(255,255,255,.03);border-radius:8px;font-size:.9rem}
.feature-item::before{content:"✓";color:var(--gold);font-weight:bold;flex-shrink:0}

.use-case-list,.pros-list,.cons-list{list-style:none;padding:0;margin:1rem 0}
.use-case-list li,.pros-list li,.cons-list li{padding:.4rem 0 .4rem 1.5rem;position:relative;font-size:.95rem}
.use-case-list li::before{content:"→";position:absolute;left:0;color:var(--accent)}
.pros-list li::before{content:"[OK]";position:absolute;left:0}
.cons-list li::before{content:"⚠️";position:absolute;left:0}

.verdict-box{background:linear-gradient(135deg,rgba(201,168,76,.1),rgba(99,102,241,.1));border:1px solid rgba(201,168,76,.25);border-radius:var(--radius-lg);padding:1.5rem;margin:2rem 0;font-size:1.05rem;font-style:italic;color:var(--text-heading)}
.verdict-box::before{content:"💡 ";font-style:normal}

.cta-row{display:flex;gap:1rem;flex-wrap:wrap;margin:2rem 0}
.btn-primary{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 1.5rem;background:var(--gold);color:#0e0e1a;font-weight:700;border-radius:8px;font-size:.95rem;transition:all .2s}
.btn-primary:hover{background:var(--gold-hover);color:#0e0e1a;transform:translateY(-1px)}
.btn-secondary{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 1.5rem;border:1px solid var(--gold);color:var(--gold);font-weight:600;border-radius:8px;font-size:.95rem;transition:all .2s}
.btn-secondary:hover{background:rgba(201,168,76,.1)}

/* ALTERNATIVES */
.alternatives-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin:1rem 0}
.alt-card{background:var(--bg-card);border:1px solid rgba(255,255,255,.06);border-radius:var(--radius-md);padding:1rem;text-align:center;transition:all .3s}
.alt-card:hover{background:var(--bg-card-hover);border-color:rgba(201,168,76,.3);transform:translateY(-2px)}
.alt-card .alt-icon{font-size:1.8rem;margin-bottom:.3rem}
.alt-card .alt-name{font-weight:600;color:var(--text-heading);font-size:.9rem}
.alt-card .alt-tagline{font-size:.75rem;color:var(--text-muted);margin-top:.2rem}

/* INFO TABLE */
.info-table{width:100%;border-collapse:collapse;margin:1rem 0}
.info-table th,.info-table td{padding:.6rem 1rem;text-align:left;border-bottom:1px solid rgba(255,255,255,.06)}
.info-table th{color:var(--text-muted);font-size:.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;width:35%}
.info-table td{color:var(--text-main);font-size:.9rem}

/* TAGS */
.tags{display:flex;flex-wrap:wrap;gap:.4rem;margin:.5rem 0}
.tag{padding:.2rem .6rem;background:rgba(99,102,241,.1);border-radius:12px;font-size:.75rem;color:var(--accent)}

/* CATEGORY PAGE */
.cat-header{text-align:center;padding:3rem 0 2rem}
.cat-icon{font-size:3rem;margin-bottom:1rem}
.cat-title{font-family:Georgia,serif;font-size:2.2rem;color:var(--text-heading)}
.cat-desc{color:var(--text-muted);font-size:1.1rem;margin-top:.5rem}
.cat-count{color:var(--gold);font-size:.9rem;margin-top:.5rem}
.tools-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.2rem;margin:2rem 0}
.tool-card{background:var(--bg-card);border:1px solid rgba(255,255,255,.06);border-radius:var(--radius-md);padding:1.2rem;transition:all .3s;display:flex;flex-direction:column}
.tool-card:hover{background:var(--bg-card-hover);border-color:rgba(201,168,76,.3);transform:translateY(-3px);box-shadow:var(--shadow-md)}
.tool-card .card-top{display:flex;gap:.8rem;align-items:flex-start;margin-bottom:.8rem}
.tool-card .card-icon{font-size:1.8rem}
.tool-card .card-info{flex:1}
.tool-card .card-name{font-weight:700;color:var(--text-heading);font-size:1rem}
.tool-card .card-tagline{font-size:.8rem;color:var(--text-muted);margin-top:.2rem}
.tool-card .card-bottom{margin-top:auto;padding-top:.8rem;display:flex;justify-content:space-between;align-items:center}
.tool-card .card-rating{color:var(--gold);font-size:.8rem}
.tool-card .card-pricing{font-size:.72rem;padding:.2rem .5rem;border-radius:10px}

/* COMPARISON PAGE */
.vs-header{text-align:center;padding:3rem 0 2rem}
.vs-title{font-family:Georgia,serif;font-size:2rem;color:var(--text-heading)}
.vs-subtitle{color:var(--text-muted);font-size:1rem;margin-top:.5rem}
.compare-table{width:100%;border-collapse:collapse;margin:2rem 0}
.compare-table th{padding:.8rem;text-align:center;background:rgba(99,102,241,.08);color:var(--text-heading);font-size:.85rem}
.compare-table td{padding:.7rem;text-align:center;border-bottom:1px solid rgba(255,255,255,.06);font-size:.9rem}
.compare-table td:first-child{text-align:left;color:var(--text-muted);font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}

/* SCHEMA FAQ */
.faq-section{margin:2rem 0}
.faq-item{margin-bottom:1rem;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:var(--radius-md);overflow:hidden}
.faq-question{padding:1rem 1.2rem;cursor:pointer;font-weight:600;color:var(--text-heading);display:flex;justify-content:space-between;align-items:center;font-size:.95rem}
.faq-question::after{content:"+";color:var(--gold);font-size:1.2rem;font-weight:300;transition:transform .3s}
.faq-item.open .faq-question::after{transform:rotate(45deg)}
.faq-answer{padding:0 1.2rem;max-height:0;overflow:hidden;transition:all .3s;color:var(--text-muted);font-size:.9rem;line-height:1.7}
.faq-item.open .faq-answer{padding:0 1.2rem 1rem;max-height:500px}

/* FOOTER */
.site-footer{background:rgba(0,0,0,.3);border-top:1px solid rgba(201,168,76,.1);padding:2rem;text-align:center;margin-top:4rem}
.footer-logo{font-family:Georgia,serif;font-size:1rem;color:var(--gold);margin-bottom:.5rem}
.footer-links{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;margin:.8rem 0}
.footer-links a{color:var(--text-muted);font-size:.8rem}
.footer-links a:hover{color:var(--gold)}
.footer-copy{color:var(--text-muted);font-size:.75rem;margin-top:.8rem}

@media(max-width:768px){
  .top-nav{padding:.5rem 1rem;gap:.5rem}
  .nav-links{gap:.8rem}
  .container{padding:1.5rem 1rem}
  .tool-header{flex-direction:column}
  .tool-name{font-size:1.5rem}
  .feature-grid{grid-template-columns:1fr}
  .alternatives-grid{grid-template-columns:repeat(2,1fr)}
  .cta-row{flex-direction:column}
  .compare-table{font-size:.8rem}
}
"""


def get_nav_html(lang, active_cat=None):
    """Generate navigation bar HTML."""
    home = f"/{lang}/"
    other_lang = "en" if lang == "fr" else "fr"

    title = "La Bible de l'IA" if lang == "fr" else "The AI Bible"
    catalog = "Catalogue" if lang == "fr" else "Catalog"
    categories = "Catégories" if lang == "fr" else "Categories"

    fr_flag = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 600'%3E%3Crect width='300' height='600' fill='%23002395'/%3E%3Crect x='300' width='300' height='600' fill='%23fff'/%3E%3Crect x='600' width='300' height='600' fill='%23ED2939'/%3E%3C/svg%3E"
    en_flag = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 30'%3E%3CclipPath id='s'%3E%3Cpath d='M0 0v30h60V0z'/%3E%3C/clipPath%3E%3CclipPath id='t'%3E%3Cpath d='M30 15h30v15zv15H0zH0V0zV0h30z'/%3E%3C/clipPath%3E%3Cg clip-path='url(%23s)'%3E%3Cpath d='M0 0v30h60V0z' fill='%23012169'/%3E%3Cpath d='M0 0l60 30m0-30L0 30' stroke='%23fff' stroke-width='6'/%3E%3Cpath d='M0 0l60 30m0-30L0 30' clip-path='url(%23t)' stroke='%23C8102E' stroke-width='4'/%3E%3Cpath d='M30 0v30M0 15h60' stroke='%23fff' stroke-width='10'/%3E%3Cpath d='M30 0v30M0 15h60' stroke='%23C8102E' stroke-width='6'/%3E%3C/g%3E%3C/svg%3E"

    fr_active = ' active' if lang == 'fr' else ''
    en_active = ' active' if lang == 'en' else ''

    logo_svg = '<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><polygon points="50,4 96,50 50,96 4,50" stroke="#c9a84c" stroke-width="3" fill="none"/><polygon points="50,14 86,50 50,86 14,50" stroke="#c9a84c" stroke-width="1.5" fill="none"/><text x="50" y="58" text-anchor="middle" font-family="Georgia,serif" font-size="30" font-weight="400" fill="#c9a84c" letter-spacing="2">BI</text></svg>'

    return f'''<nav class="top-nav">
  <a class="lang-btn{fr_active}" href="/fr/" title="Français"><img src="{fr_flag}" alt="FR"></a>
  <a class="lang-btn{en_active}" href="/en/" title="English"><img src="{en_flag}" alt="EN"></a>
  <a href="{home}" class="nav-logo">{logo_svg}</a>
  <a href="{home}" class="nav-title">{title}</a>
  <div class="nav-links">
    <a href="{home}">{catalog}</a>
    <a href="{home}#categories">{categories}</a>
  </div>
</nav>'''


def get_footer_html(lang):
    """Generate footer HTML."""
    if lang == "fr":
        return '''<footer class="site-footer">
  <div class="footer-logo">La Bible de l'IA</div>
  <div class="footer-links">
    <a href="/fr/">Accueil</a>
    <a href="/fr/#categories">Catégories</a>
    <a href="/en/">English</a>
  </div>
  <div class="footer-copy">© 2025-2026 La Bible de l'IA — labibledelia.com</div>
</footer>'''
    else:
        return '''<footer class="site-footer">
  <div class="footer-logo">The AI Bible</div>
  <div class="footer-links">
    <a href="/en/">Home</a>
    <a href="/en/#categories">Categories</a>
    <a href="/fr/">Français</a>
  </div>
  <div class="footer-copy">© 2025-2026 The AI Bible — labibledelia.com</div>
</footer>'''


def get_faq_js():
    """Simple FAQ toggle JavaScript."""
    return """
<script>
document.querySelectorAll('.faq-question').forEach(q=>{
  q.addEventListener('click',()=>{
    q.parentElement.classList.toggle('open');
  });
});
</script>"""


# ============================================================
# 4. TOOL PAGE GENERATOR
# ============================================================

def generate_tool_page(tool, all_tools, categories, lang):
    """Generate a full HTML page for a single tool."""

    tool_id = tool['id']
    name = tool['name']
    tagline = tool.get('tagline', '')
    description = tool.get('description', '')
    icon = tool.get('icon', '🔧')
    url = tool.get('url', '#')
    category = tool.get('category', '')
    tags = tool.get('tags', [])
    pricing = tool.get('pricing', 'freemium')
    pricing_note = tool.get('pricingNote', '')
    rating = tool.get('rating', 0)
    platforms = tool.get('platforms', [])
    features = tool.get('features', [])
    use_cases = tool.get('useCases', [])
    pros = tool.get('pros', [])
    cons = tool.get('cons', [])
    alternatives = tool.get('alternatives', [])
    company = tool.get('company', '')
    launch_year = tool.get('launchYear', '')
    verdict = tool.get('verdict', '')

    # Find category info
    cat_info = next((c for c in categories if c['id'] == category), None)
    cat_name = cat_info['name'] if cat_info else category

    # Rating stars
    stars_html = ''.join('★' if i < round(rating) else '☆' for i in range(5))

    # Page URL
    page_url = f"{DOMAIN}/{lang}/{tool_id}/"
    alt_lang = 'en' if lang == 'fr' else 'fr'
    alt_url = f"{DOMAIN}/{alt_lang}/{tool_id}/"
    home_url = f"/{lang}/"
    cat_url = f"/{lang}/categorie/{category}/"

    # Translated labels
    if lang == "fr":
        L = {
            'title_suffix': f"— Avis, Prix & Alternatives | La Bible de l'IA",
            'breadcrumb_home': 'Accueil',
            'features': '[*] Fonctionnalités',
            'use_cases': '🎯 Cas d\'usage',
            'pricing_title': '💰 Tarification',
            'pros_cons': '⚖️ Avantages & Inconvénients',
            'pros': 'Avantages',
            'cons': 'Inconvénients',
            'verdict': '🏆 Verdict',
            'alternatives_title': '[SYNC] Alternatives',
            'info': 'ℹ️ Informations',
            'company_label': 'Entreprise',
            'launch_label': 'Lancement',
            'platforms_label': 'Plateformes',
            'category_label': 'Catégorie',
            'visit': f'Visiter {name}',
            'compare': 'Comparer',
            'back_cat': f'Voir tous les outils {cat_name}',
            'faq_title': '❓ Questions fréquentes',
            'faq_what': f"Qu'est-ce que {name} ?",
            'faq_what_a': f"{name} est {tagline.lower()}. {description[:200]}",
            'faq_price': f"{name} est-il gratuit ?",
            'faq_price_a': f"Le modèle de tarification de {name} est : {pricing}. {pricing_note}",
            'faq_alt': f"Quelles sont les alternatives à {name} ?",
            'meta_desc': f"{name} — {tagline}. Avis complet, prix, fonctionnalités et alternatives. Découvrez si {name} est fait pour vous.",
        }
    else:
        L = {
            'title_suffix': f"— Review, Pricing & Alternatives | The AI Bible",
            'breadcrumb_home': 'Home',
            'features': '[*] Features',
            'use_cases': '🎯 Use Cases',
            'pricing_title': '💰 Pricing',
            'pros_cons': '⚖️ Pros & Cons',
            'pros': 'Pros',
            'cons': 'Cons',
            'verdict': '🏆 Verdict',
            'alternatives_title': '[SYNC] Alternatives',
            'info': 'ℹ️ Information',
            'company_label': 'Company',
            'launch_label': 'Launched',
            'platforms_label': 'Platforms',
            'category_label': 'Category',
            'visit': f'Visit {name}',
            'compare': 'Compare',
            'back_cat': f'See all {cat_name} tools',
            'faq_title': '❓ Frequently Asked Questions',
            'faq_what': f"What is {name}?",
            'faq_what_a': f"{name} is {tagline[0].lower() + tagline[1:] if tagline else ''}. {description[:200]}",
            'faq_price': f"Is {name} free?",
            'faq_price_a': f"The pricing model for {name} is: {pricing}. {pricing_note}",
            'faq_alt': f"What are the alternatives to {name}?",
            'meta_desc': f"{name} — {tagline}. Complete review, pricing, features and alternatives. Find out if {name} is right for you.",
        }

    # Build alternatives HTML
    alt_tools = [t for t in all_tools if t['id'] in alternatives]
    alt_html_parts = []
    for at in alt_tools:
        at_url = f"/{lang}/{at['id']}/"
        alt_html_parts.append(f'''<a href="{at_url}" class="alt-card">
  <div class="alt-icon">{at.get('icon','🔧')}</div>
  <div class="alt-name">{at['name']}</div>
  <div class="alt-tagline">{at.get('tagline','')[:60]}</div>
</a>''')

    # Alternatives names for FAQ
    alt_names = ", ".join(at['name'] for at in alt_tools)
    faq_alt_answer = f"{L['faq_alt'].replace('?','')} : {alt_names}." if alt_names else "No known alternatives."

    # Features HTML
    features_html = '\n'.join(f'<div class="feature-item">{html.escape(f)}</div>' for f in features)

    # Use cases HTML
    use_cases_html = '\n'.join(f'<li>{html.escape(u)}</li>' for u in use_cases)

    # Pros HTML
    pros_html = '\n'.join(f'<li>{html.escape(p)}</li>' for p in pros)

    # Cons HTML
    cons_html = '\n'.join(f'<li>{html.escape(c)}</li>' for c in cons)

    # Tags HTML
    tags_html = '\n'.join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)

    # Platforms
    platform_str = ', '.join(p.upper() if p in ['web','api','ios'] else p.capitalize() for p in platforms)

    # Schema.org JSON-LD
    schema_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "description": tagline,
        "url": url,
        "applicationCategory": cat_name,
        "operatingSystem": platform_str,
        "offers": {
            "@type": "Offer",
            "price": "0" if pricing in ["gratuit", "free", "freemium"] else "",
            "priceCurrency": "USD",
            "description": pricing_note
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": str(max(50, int(rating * 100)))
        },
        "review": {
            "@type": "Review",
            "reviewBody": verdict,
            "author": {
                "@type": "Organization",
                "name": "La Bible de l'IA"
            }
        }
    }, ensure_ascii=False, indent=2)

    # FAQ Schema
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": L['faq_what'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": L['faq_what_a']
                }
            },
            {
                "@type": "Question",
                "name": L['faq_price'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": L['faq_price_a']
                }
            },
            {
                "@type": "Question",
                "name": L['faq_alt'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq_alt_answer
                }
            }
        ]
    }, ensure_ascii=False, indent=2)

    # BreadcrumbList Schema
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": L['breadcrumb_home'], "item": f"{DOMAIN}/{lang}/"},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{DOMAIN}/{lang}/categorie/{category}/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": page_url}
        ]
    }, ensure_ascii=False, indent=2)

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} {L['title_suffix']}</title>
<meta name="description" content="{html.escape(L['meta_desc'])}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="{lang}" href="{page_url}">
<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">
<meta property="og:title" content="{name} {L['title_suffix']}">
<meta property="og:description" content="{html.escape(L['meta_desc'])}">
<meta property="og:type" content="article">
<meta property="og:url" content="{page_url}">
<meta property="og:site_name" content="La Bible de l'IA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{name} {L['title_suffix']}">
<script type="application/ld+json">
{schema_json}
</script>
<script type="application/ld+json">
{faq_schema}
</script>
<script type="application/ld+json">
{breadcrumb_schema}
</script>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="manifest" href="/manifest.json">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<style>{get_shared_css()}</style>
</head>
<body>
{get_nav_html(lang)}
<div class="container">

<!-- Breadcrumb -->
<div class="breadcrumb">
  <a href="{home_url}">{L['breadcrumb_home']}</a>
  <span class="sep">›</span>
  <a href="{cat_url}">{cat_name}</a>
  <span class="sep">›</span>
  <span>{name}</span>
</div>

<!-- Header -->
<div class="tool-header">
  <div class="tool-icon">{icon}</div>
  <div class="tool-title-group">
    <h1 class="tool-name">{name}</h1>
    <p class="tool-tagline">{tagline}</p>
  </div>
</div>

<!-- Meta badges -->
<div class="tool-meta">
  <span class="meta-badge cat" style="background:rgba({_cat_rgb(category)},.15);color:var(--cat-{category})">{cat_name}</span>
  <span class="meta-badge pricing-{pricing}">{pricing.capitalize()}</span>
  <span class="meta-badge"><span class="stars">{stars_html}</span> {rating}/5</span>
  <span class="meta-badge">{platform_str}</span>
</div>

<!-- Tags -->
<div class="tags">{tags_html}</div>

<!-- Description -->
<p class="tool-description">{description}</p>

<!-- CTA -->
<div class="cta-row">
  <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn-primary">🔗 {L['visit']}</a>
  <a href="{cat_url}" class="btn-secondary">📂 {L['back_cat']}</a>
</div>

<!-- Pricing -->
<h2 class="section-title">{L['pricing_title']}</h2>
<div class="pricing-note"><strong>{pricing.capitalize()}</strong> — {pricing_note}</div>

<!-- Features -->
<h2 class="section-title">{L['features']}</h2>
<div class="feature-grid">
{features_html}
</div>

<!-- Use Cases -->
<h2 class="section-title">{L['use_cases']}</h2>
<ul class="use-case-list">
{use_cases_html}
</ul>

<!-- Pros & Cons -->
<h2 class="section-title">{L['pros_cons']}</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">
<div>
<h3 style="color:#10b981;font-size:.9rem;margin-bottom:.5rem">👍 {L['pros']}</h3>
<ul class="pros-list">{pros_html}</ul>
</div>
<div>
<h3 style="color:#ef4444;font-size:.9rem;margin-bottom:.5rem">👎 {L['cons']}</h3>
<ul class="cons-list">{cons_html}</ul>
</div>
</div>

<!-- Verdict -->
<h2 class="section-title">{L['verdict']}</h2>
<div class="verdict-box">{verdict}</div>

<!-- Info Table -->
<h2 class="section-title">{L['info']}</h2>
<table class="info-table">
<tr><th>{L['company_label']}</th><td>{company}</td></tr>
<tr><th>{L['launch_label']}</th><td>{launch_year}</td></tr>
<tr><th>{L['platforms_label']}</th><td>{platform_str}</td></tr>
<tr><th>{L['category_label']}</th><td><a href="{cat_url}">{cat_name}</a></td></tr>
<tr><th>Site</th><td><a href="{url}" target="_blank" rel="noopener">{url}</a></td></tr>
</table>

<!-- Alternatives -->
<h2 class="section-title">{L['alternatives_title']}</h2>
<div class="alternatives-grid">
{chr(10).join(alt_html_parts)}
</div>

<!-- FAQ -->
<h2 class="section-title">{L['faq_title']}</h2>
<div class="faq-section">
  <div class="faq-item">
    <div class="faq-question">{L['faq_what']}</div>
    <div class="faq-answer">{L['faq_what_a']}</div>
  </div>
  <div class="faq-item">
    <div class="faq-question">{L['faq_price']}</div>
    <div class="faq-answer">{L['faq_price_a']}</div>
  </div>
  <div class="faq-item">
    <div class="faq-question">{L['faq_alt']}</div>
    <div class="faq-answer">{faq_alt_answer}</div>
  </div>
</div>

</div><!-- .container -->

{get_footer_html(lang)}
{get_faq_js()}
</body>
</html>'''

    return page_html


def _cat_rgb(cat_id):
    """Return approximate RGB for category color (for rgba backgrounds)."""
    colors = {
        'chatbots': '99,102,241', 'texte': '245,158,11', 'image': '236,72,153',
        'video': '239,68,68', 'audio': '139,92,246', 'code': '16,185,129',
        'marketing': '249,115,22', 'productivite': '6,182,212', 'education': '20,184,166',
        'automation': '59,130,246', 'recherche': '109,40,217', 'design-web': '217,70,239',
        'reunions-email': '14,165,233', 'carriere': '132,204,22', 'finance': '244,63,94'
    }
    return colors.get(cat_id, '136,136,136')


# ============================================================
# 5. CATEGORY PAGE GENERATOR
# ============================================================

def generate_category_page(cat, tools, categories, lang):
    """Generate a category page listing all tools in that category."""

    cat_id = cat['id']
    cat_name = cat['name']
    cat_icon = cat['icon']
    cat_desc = cat.get('description', '')
    cat_roman = cat.get('roman', '')

    cat_tools = sorted([t for t in tools if t.get('category') == cat_id], key=lambda t: -t.get('popularity', 0))
    count = len(cat_tools)

    page_url = f"{DOMAIN}/{lang}/categorie/{cat_id}/"
    alt_lang = 'en' if lang == 'fr' else 'fr'
    alt_url = f"{DOMAIN}/{alt_lang}/categorie/{cat_id}/"
    home_url = f"/{lang}/"

    if lang == "fr":
        title = f"{cat_name} — {count} meilleurs outils IA | La Bible de l'IA"
        meta_desc = f"Découvrez les {count} meilleurs outils IA pour {cat_desc.lower()}. Comparatif complet avec avis, prix et alternatives."
        breadcrumb_home = "Accueil"
        tools_label = "outils"
    else:
        title = f"{cat_name} — {count} Best AI Tools | The AI Bible"
        meta_desc = f"Discover the {count} best AI tools for {cat_desc.lower()}. Complete comparison with reviews, pricing and alternatives."
        breadcrumb_home = "Home"
        tools_label = "tools"

    # Tool cards
    cards_html = []
    for t in cat_tools:
        t_url = f"/{lang}/{t['id']}/"
        pricing_class = f"pricing-{t.get('pricing','freemium')}"
        stars = ''.join('★' if i < round(t.get('rating',0)) else '☆' for i in range(5))
        cards_html.append(f'''<a href="{t_url}" class="tool-card">
  <div class="card-top">
    <div class="card-icon">{t.get('icon','🔧')}</div>
    <div class="card-info">
      <div class="card-name">{t['name']}</div>
      <div class="card-tagline">{t.get('tagline','')[:80]}</div>
    </div>
  </div>
  <div class="card-bottom">
    <span class="card-rating">{stars} {t.get('rating',0)}</span>
    <span class="card-pricing meta-badge {pricing_class}">{t.get('pricing','').capitalize()}</span>
  </div>
</a>''')

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="{lang}" href="{page_url}">
<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<style>{get_shared_css()}</style>
</head>
<body>
{get_nav_html(lang)}
<div class="container">

<div class="breadcrumb">
  <a href="{home_url}">{breadcrumb_home}</a>
  <span class="sep">›</span>
  <span>{cat_name}</span>
</div>

<div class="cat-header">
  <div class="cat-icon">{cat_icon}</div>
  <h1 class="cat-title">{cat_roman}. {cat_name}</h1>
  <p class="cat-desc">{cat_desc}</p>
  <p class="cat-count">{count} {tools_label}</p>
</div>

<div class="tools-grid">
{chr(10).join(cards_html)}
</div>

</div>

{get_footer_html(lang)}
</body>
</html>'''

    return page_html


# ============================================================
# 6. COMPARISON PAGE GENERATOR
# ============================================================

def generate_comparison_page(tool1, tool2, all_tools, categories, lang):
    """Generate a comparison page for two tools."""

    name1 = tool1['name']
    name2 = tool2['name']
    id1 = tool1['id']
    id2 = tool2['id']

    slug = f"{id1}-vs-{id2}"
    page_url = f"{DOMAIN}/{lang}/comparer/{slug}/"
    alt_lang = 'en' if lang == 'fr' else 'fr'
    alt_url = f"{DOMAIN}/{alt_lang}/comparer/{slug}/"
    home_url = f"/{lang}/"

    if lang == "fr":
        title = f"{name1} vs {name2} — Comparatif IA | La Bible de l'IA"
        meta_desc = f"Comparatif détaillé {name1} vs {name2}. Prix, fonctionnalités, avantages et inconvénients. Quel outil IA choisir ?"
        breadcrumb_home = "Accueil"
        compare_label = "Comparaison"
        criteria_labels = {
            'pricing': 'Tarification', 'rating': 'Note', 'company': 'Entreprise',
            'launch': 'Lancement', 'platforms': 'Plateformes', 'pricing_detail': 'Détail prix'
        }
        verdict_label = "Verdict"
    else:
        title = f"{name1} vs {name2} — AI Comparison | The AI Bible"
        meta_desc = f"Detailed comparison {name1} vs {name2}. Pricing, features, pros and cons. Which AI tool should you choose?"
        breadcrumb_home = "Home"
        compare_label = "Comparison"
        criteria_labels = {
            'pricing': 'Pricing', 'rating': 'Rating', 'company': 'Company',
            'launch': 'Launched', 'platforms': 'Platforms', 'pricing_detail': 'Price detail'
        }
        verdict_label = "Verdict"

    stars1 = ''.join('★' if i < round(tool1.get('rating',0)) else '☆' for i in range(5))
    stars2 = ''.join('★' if i < round(tool2.get('rating',0)) else '☆' for i in range(5))

    # Features comparison
    features1 = tool1.get('features', [])
    features2 = tool2.get('features', [])

    features_rows = ""
    max_features = max(len(features1), len(features2))
    for i in range(max_features):
        f1 = features1[i] if i < len(features1) else "—"
        f2 = features2[i] if i < len(features2) else "—"
        features_rows += f"<tr><td>{f1}</td><td>{f2}</td></tr>\n"

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="{lang}" href="{page_url}">
<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<style>{get_shared_css()}</style>
</head>
<body>
{get_nav_html(lang)}
<div class="container">

<div class="breadcrumb">
  <a href="{home_url}">{breadcrumb_home}</a>
  <span class="sep">›</span>
  <span>{name1} vs {name2}</span>
</div>

<div class="vs-header">
  <div style="font-size:2.5rem;margin-bottom:1rem">{tool1.get('icon','')} ⚔️ {tool2.get('icon','')}</div>
  <h1 class="vs-title">{name1} vs {name2}</h1>
  <p class="vs-subtitle">{compare_label}</p>
</div>

<table class="compare-table">
<thead><tr><th></th><th>{tool1.get('icon','')} {name1}</th><th>{tool2.get('icon','')} {name2}</th></tr></thead>
<tbody>
<tr><td>{criteria_labels['rating']}</td><td><span class="stars">{stars1}</span> {tool1.get('rating','')}</td><td><span class="stars">{stars2}</span> {tool2.get('rating','')}</td></tr>
<tr><td>{criteria_labels['pricing']}</td><td>{tool1.get('pricing','').capitalize()}</td><td>{tool2.get('pricing','').capitalize()}</td></tr>
<tr><td>{criteria_labels['pricing_detail']}</td><td style="font-size:.8rem">{tool1.get('pricingNote','')}</td><td style="font-size:.8rem">{tool2.get('pricingNote','')}</td></tr>
<tr><td>{criteria_labels['company']}</td><td>{tool1.get('company','')}</td><td>{tool2.get('company','')}</td></tr>
<tr><td>{criteria_labels['launch']}</td><td>{tool1.get('launchYear','')}</td><td>{tool2.get('launchYear','')}</td></tr>
<tr><td>{criteria_labels['platforms']}</td><td>{', '.join(tool1.get('platforms',[]))}</td><td>{', '.join(tool2.get('platforms',[]))}</td></tr>
</tbody>
</table>

<h2 class="section-title">[*] Features</h2>
<table class="compare-table">
<thead><tr><th>{name1}</th><th>{name2}</th></tr></thead>
<tbody>
{features_rows}
</tbody>
</table>

<h2 class="section-title">👍 {criteria_labels.get('pricing','Pros')}</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem">
<div>
<h3 style="color:var(--gold);font-size:.95rem;margin-bottom:.5rem">{name1}</h3>
<ul class="pros-list">{''.join(f"<li>{p}</li>" for p in tool1.get('pros',[]))}</ul>
<ul class="cons-list">{''.join(f"<li>{c}</li>" for c in tool1.get('cons',[]))}</ul>
</div>
<div>
<h3 style="color:var(--gold);font-size:.95rem;margin-bottom:.5rem">{name2}</h3>
<ul class="pros-list">{''.join(f"<li>{p}</li>" for p in tool2.get('pros',[]))}</ul>
<ul class="cons-list">{''.join(f"<li>{c}</li>" for c in tool2.get('cons',[]))}</ul>
</div>
</div>

<h2 class="section-title">🏆 {verdict_label}</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">
<div class="verdict-box">{tool1.get('verdict','')}</div>
<div class="verdict-box">{tool2.get('verdict','')}</div>
</div>

<div class="cta-row" style="justify-content:center;margin-top:2rem">
  <a href="/{lang}/{id1}/" class="btn-primary">{tool1.get('icon','')} {name1}</a>
  <a href="/{lang}/{id2}/" class="btn-primary">{tool2.get('icon','')} {name2}</a>
</div>

</div>

{get_footer_html(lang)}
</body>
</html>'''

    return page_html


# ============================================================
# 7. SITEMAP & ROBOTS
# ============================================================

def generate_sitemap(tools, categories, comparisons):
    """Generate sitemap.xml."""
    urls = []

    # Home pages
    urls.append(('/', '1.0', 'daily'))
    urls.append(('/fr/', '1.0', 'daily'))
    urls.append(('/en/', '1.0', 'daily'))

    # Tool pages
    for t in tools:
        urls.append((f"/fr/{t['id']}/", '0.8', 'weekly'))
        urls.append((f"/en/{t['id']}/", '0.8', 'weekly'))

    # Category pages
    for c in categories:
        urls.append((f"/fr/categorie/{c['id']}/", '0.9', 'weekly'))
        urls.append((f"/en/categorie/{c['id']}/", '0.9', 'weekly'))

    # Comparison pages
    for (id1, id2) in comparisons:
        urls.append((f"/fr/comparer/{id1}-vs-{id2}/", '0.7', 'monthly'))
        urls.append((f"/en/comparer/{id1}-vs-{id2}/", '0.7', 'monthly'))

    # Blog articles
    blog_slugs = [
        "chatgpt-guide-complet",
        "chatgpt-vs-claude-vs-gemini",
        "meilleurs-generateurs-images-ia",
        "cursor-vs-github-copilot",
        "meilleurs-outils-ia-gratuits",
        "automatiser-workflow-ia",
    ]
    for slug in blog_slugs:
        urls.append((f"/fr/blog/{slug}/", '0.8', 'monthly'))
        urls.append((f"/en/blog/{slug}/", '0.8', 'monthly'))

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    xml_parts.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    for path, priority, freq in urls:
        xml_parts.append(f'''  <url>
    <loc>{DOMAIN}{path}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>''')

    xml_parts.append('</urlset>')
    return '\n'.join(xml_parts)


def generate_robots():
    """Generate robots.txt."""
    return f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""


# ============================================================
# 8. DETERMINE TOP COMPARISONS
# ============================================================

def get_top_comparisons(tools):
    """Generate the most searched comparison pairs."""
    # Top tools that people compare
    compare_pairs = [
        ("chatgpt", "claude"),
        ("chatgpt", "gemini"),
        ("chatgpt", "perplexity"),
        ("claude", "gemini"),
        ("claude", "perplexity"),
        ("chatgpt", "deepseek"),
        ("chatgpt", "lechat"),
        ("chatgpt", "grok"),
        ("claude", "deepseek"),
        ("midjourney", "dalle3"),
        ("midjourney", "stablediffusion"),
        ("midjourney", "flux"),
        ("dalle3", "stablediffusion"),
        ("dalle3", "flux"),
        ("runway", "pika"),
        ("runway", "kling"),
        ("pika", "kling"),
        ("synthesia", "heygen"),
        ("elevenlabs", "murf"),
        ("suno", "udio"),
        ("copilot-gh", "cursor"),
        ("cursor", "windsurf"),
        ("cursor", "bolt"),
        ("copilot-gh", "windsurf"),
        ("v0", "bolt"),
        ("bolt", "lovable"),
        ("bolt", "replit"),
        ("zapier", "make"),
        ("zapier", "n8n"),
        ("make", "n8n"),
        ("grammarly", "languagetool"),
        ("grammarly", "deepl"),
        ("jasper", "copyai"),
        ("jasper", "writesonic"),
        ("otter", "fireflies"),
        ("otter", "fathom"),
        ("fathom", "tldv"),
        ("framer", "durable"),
        ("canvaai", "firefly"),
        ("removebg", "clipdrop"),
        ("notebooklm", "elicit"),
        ("gamma", "tome"),
        ("superhuman", "shortwave"),
        ("teal", "kickresume"),
        ("notionai", "notionai-prod"),
        # New pairs (2026 update)
        ("capcut", "filmora"),
        ("capcut", "descript"),
        ("capcut", "veed"),
        ("cursor", "zed"),
        ("lovable", "replit"),
        ("claude-code", "aider"),
        ("coderabbit", "copilot-gh"),
        ("chatgpt", "meta-ai"),
        ("deepseek", "kimi"),
        ("claude", "cohere"),
        ("leonardo", "midjourney"),
        ("topaz", "magnific"),
        ("pixlr", "canvaai"),
        ("meshy", "tripo"),
        ("meshy", "kaedim"),
        ("motion", "reclaim"),
        ("clickupai", "notionai-prod"),
        ("beautifulai", "gamma"),
        ("manychat", "hubspotai"),
        ("phantombuster", "instantly"),
        ("manus", "genspark"),
        ("botpress", "lindy"),
        ("photomath", "socratic"),
        ("quizizz", "khanmigo"),
        ("wixai", "framer"),
        ("hostinger", "durable"),
        # Batch 2 (new tools)
        ("sora", "runway-gen3"),
        ("sora", "kling"),
        ("runway-gen3", "kling"),
        ("ollama", "jan"),
        ("groq", "together"),
        ("llama", "qwen"),
        ("phind", "perplexity"),
        ("chatpdf", "notebooklm"),
        ("codeium", "supermaven"),
        ("dify", "flowise"),
        ("crew-ai", "langchain"),
        ("jasper-campaigns", "typeface"),
        ("surfer", "frase"),
    ]

    tool_ids = {t['id'] for t in tools}
    valid_pairs = [(a, b) for a, b in compare_pairs if a in tool_ids and b in tool_ids and a != b]
    return valid_pairs


# ============================================================
# 9. MAIN — GENERATE EVERYTHING
# ============================================================

def main():
    print("=" * 60)
    print("  La Bible de l'IA — Multi-page Generator")
    print("=" * 60)

    # After refactoring, data is in separate JS files
    fr_tools_file = os.path.join(BASE_DIR, "tools-fr.js")
    en_tools_file = os.path.join(BASE_DIR, "tools-en.js")
    fr_app_file = os.path.join(BASE_DIR, "app-fr.js")
    en_app_file = os.path.join(BASE_DIR, "app-en.js")

    # Extract data from separate files
    print("\n[*] Extracting data from FR files...")
    fr_categories = extract_js_array(fr_app_file, "CATEGORIES")
    fr_tools = extract_js_array(fr_tools_file, "TOOLS")
    print(f"   Found {len(fr_categories)} categories, {len(fr_tools)} tools")

    print("\n[*] Extracting data from EN files...")
    en_categories = extract_js_array(en_app_file, "CATEGORIES")
    en_tools = extract_js_array(en_tools_file, "TOOLS")
    print(f"   Found {len(en_categories)} categories, {len(en_tools)} tools")

    # Get comparison pairs
    comparisons = get_top_comparisons(fr_tools)
    print(f"\n[SYNC] {len(comparisons)} comparison pairs to generate")

    total_pages = (len(fr_tools) + len(en_tools)) + (len(fr_categories) + len(en_categories)) + (len(comparisons) * 2) + 2
    print(f"\n[*] Total pages to generate: {total_pages}")

    generated = 0

    # --- Generate FR tool pages ---
    print("\n[FR] Generating FR tool pages...")
    for tool in fr_tools:
        dir_path = os.path.join(BASE_DIR, "fr", tool['id'])
        os.makedirs(dir_path, exist_ok=True)
        page = generate_tool_page(tool, fr_tools, fr_categories, "fr")
        with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
            f.write(page)
        generated += 1
    print(f"   [OK] {len(fr_tools)} FR tool pages generated")

    # --- Generate EN tool pages ---
    print("\n[EN] Generating EN tool pages...")
    for tool in en_tools:
        dir_path = os.path.join(BASE_DIR, "en", tool['id'])
        os.makedirs(dir_path, exist_ok=True)
        page = generate_tool_page(tool, en_tools, en_categories, "en")
        with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
            f.write(page)
        generated += 1
    print(f"   [OK] {len(en_tools)} EN tool pages generated")

    # --- Generate FR category pages ---
    print("\n[FR] Generating FR category pages...")
    for cat in fr_categories:
        dir_path = os.path.join(BASE_DIR, "fr", "categorie", cat['id'])
        os.makedirs(dir_path, exist_ok=True)
        page = generate_category_page(cat, fr_tools, fr_categories, "fr")
        with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
            f.write(page)
        generated += 1
    print(f"   [OK] {len(fr_categories)} FR category pages generated")

    # --- Generate EN category pages ---
    print("\n[EN] Generating EN category pages...")
    for cat in en_categories:
        dir_path = os.path.join(BASE_DIR, "en", "categorie", cat['id'])
        os.makedirs(dir_path, exist_ok=True)
        page = generate_category_page(cat, en_tools, en_categories, "en")
        with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
            f.write(page)
        generated += 1
    print(f"   [OK] {len(en_categories)} EN category pages generated")

    # --- Generate comparison pages ---
    print("\n[VS] Generating comparison pages...")
    fr_tool_map = {t['id']: t for t in fr_tools}
    en_tool_map = {t['id']: t for t in en_tools}

    for id1, id2 in comparisons:
        # FR
        if id1 in fr_tool_map and id2 in fr_tool_map:
            dir_path = os.path.join(BASE_DIR, "fr", "comparer", f"{id1}-vs-{id2}")
            os.makedirs(dir_path, exist_ok=True)
            page = generate_comparison_page(fr_tool_map[id1], fr_tool_map[id2], fr_tools, fr_categories, "fr")
            with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
                f.write(page)
            generated += 1

        # EN
        if id1 in en_tool_map and id2 in en_tool_map:
            dir_path = os.path.join(BASE_DIR, "en", "comparer", f"{id1}-vs-{id2}")
            os.makedirs(dir_path, exist_ok=True)
            page = generate_comparison_page(en_tool_map[id1], en_tool_map[id2], en_tools, en_categories, "en")
            with open(os.path.join(dir_path, "index.html"), 'w', encoding='utf-8') as f:
                f.write(page)
            generated += 1
    print(f"   [OK] {len(comparisons) * 2} comparison pages generated")

    # --- Generate sitemap.xml ---
    print("\n[MAP] Generating sitemap.xml...")
    sitemap = generate_sitemap(fr_tools, fr_categories, comparisons)
    with open(os.path.join(BASE_DIR, "sitemap.xml"), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("   [OK]sitemap.xml generated")

    # --- Generate robots.txt ---
    print("\n[BOT] Generating robots.txt...")
    robots = generate_robots()
    with open(os.path.join(BASE_DIR, "robots.txt"), 'w', encoding='utf-8') as f:
        f.write(robots)
    print("   [OK]robots.txt generated")

    print(f"\n{'=' * 60}")
    print(f"  [DONE] DONE! {generated} pages generated")
    print(f"{'=' * 60}")
    print(f"\nFile structure:")
    print(f"  {BASE_DIR}/")
    print(f"  +-- fr/")
    print(f"  |   +-- index.html (existing homepage)")
    print(f"  |   +-- chatgpt/index.html")
    print(f"  |   +-- claude/index.html")
    print(f"  |   +-- ... ({len(fr_tools)} tool pages)")
    print(f"  |   +-- categorie/chatbots/index.html")
    print(f"  |   +-- ... ({len(fr_categories)} category pages)")
    print(f"  |   +-- comparer/chatgpt-vs-claude/index.html")
    print(f"  |       ... ({len(comparisons)} comparison pages)")
    print(f"  +-- en/")
    print(f"  |   +-- (same structure)")
    print(f"  +-- sitemap.xml")
    print(f"  +-- robots.txt")
    print(f"  +-- netlify.toml")


if __name__ == "__main__":
    main()
