#!/usr/bin/env python3
"""
Fix sitemap.xml:
1. Add missing pages (Quiz, Radar, Packs, 14 blog articles)
2. Add xhtml:link hreflang to every bilingual URL pair
3. Rewrite the complete sitemap
"""
import re
import os
from datetime import date

BASE = "https://labibledelia.com"
TODAY = date.today().isoformat()

# ── Parse existing sitemap ──────────────────────────────
sitemap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap.xml")

with open(sitemap_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extract all existing <loc> URLs
existing_urls = set(re.findall(r"<loc>(.*?)</loc>", content))
print(f"URLs existantes dans le sitemap: {len(existing_urls)}")

# ── Define missing pages ────────────────────────────────
# Pages to add (not in sitemap)
missing_pages = []

# Quiz, Radar, Packs (FR + EN)
special_pages = [
    ("/fr/quiz/", "/en/quiz/", "weekly", "0.7"),
    ("/fr/radar/", "/en/radar/", "daily", "0.7"),
    ("/fr/packs/", "/en/packs/", "weekly", "0.7"),
]

for fr, en, freq, prio in special_pages:
    if BASE + fr not in existing_urls:
        missing_pages.append((fr, freq, prio))
    if BASE + en not in existing_urls:
        missing_pages.append((en, freq, prio))

# All blog articles that exist on disk
all_blog_slugs = [
    "chatgpt-guide-complet",
    "chatgpt-vs-claude-vs-gemini",
    "meilleurs-generateurs-images-ia",
    "cursor-vs-github-copilot",
    "meilleurs-outils-ia-gratuits",
    "automatiser-workflow-ia",
    "deepseek-revolution-ia-open-source",
    "generer-videos-ia-guide",
    "creer-musique-ia-suno-udio",
    "ia-marketing-digital-guide",
    "ia-productivite-personnelle",
    "midjourney-vs-dalle-vs-stable-diffusion",
    "claude-guide-complet",
    "elevenlabs-clonage-voix-ia",
    "ia-education-revolutionne-apprentissage",
    "construire-agent-ia-guide",
    "ia-design-web-2026",
    "meilleurs-outils-ia-redaction",
    "perplexity-ia-moteur-recherche-futur",
    "securite-confidentialite-outils-ia",
]

for slug in all_blog_slugs:
    fr_url = f"/fr/blog/{slug}/"
    en_url = f"/en/blog/{slug}/"
    if BASE + fr_url not in existing_urls:
        missing_pages.append((fr_url, "monthly", "0.8"))
    if BASE + en_url not in existing_urls:
        missing_pages.append((en_url, "monthly", "0.8"))

print(f"Pages manquantes a ajouter: {len(missing_pages)}")

# ── Build complete URL list ─────────────────────────────
# Collect all URLs with their metadata
all_urls = []

# Parse existing URLs with their metadata
url_blocks = re.findall(r"<url>\s*<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>\s*<changefreq>(.*?)</changefreq>\s*<priority>(.*?)</priority>\s*</url>", content)
for loc, lastmod, freq, prio in url_blocks:
    all_urls.append((loc, lastmod, freq, prio))

# Add missing pages
for path, freq, prio in missing_pages:
    all_urls.append((BASE + path, TODAY, freq, prio))

print(f"Total URLs dans le nouveau sitemap: {len(all_urls)}")

# ── Build hreflang mapping ──────────────────────────────
# Map FR URLs to their EN counterparts and vice versa
def get_hreflang_pair(url):
    """Return (fr_url, en_url) pair for a given URL"""
    path = url.replace(BASE, "")

    if path.startswith("/fr/"):
        fr_url = url
        en_url = url.replace("/fr/", "/en/", 1)
        # Check if EN version exists in our URL list
        return fr_url, en_url
    elif path.startswith("/en/"):
        en_url = url
        fr_url = url.replace("/en/", "/fr/", 1)
        return fr_url, en_url
    else:
        return None, None

# Build set of all URLs for quick lookup
all_url_set = set(u[0] for u in all_urls)

# ── Generate new sitemap ────────────────────────────────
lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

for loc, lastmod, freq, prio in all_urls:
    lines.append('  <url>')
    lines.append(f'    <loc>{loc}</loc>')
    lines.append(f'    <lastmod>{lastmod}</lastmod>')
    lines.append(f'    <changefreq>{freq}</changefreq>')
    lines.append(f'    <priority>{prio}</priority>')

    # Add hreflang links for bilingual pages
    fr_url, en_url = get_hreflang_pair(loc)
    if fr_url and en_url:
        # Only add hreflang if both versions exist
        if fr_url in all_url_set and en_url in all_url_set:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="fr" href="{fr_url}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>')

    lines.append('  </url>')

lines.append('</urlset>')

# ── Write new sitemap ───────────────────────────────────
new_content = '\n'.join(lines) + '\n'

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(new_content)

new_count = new_content.count("<url>")
hreflang_count = new_content.count("xhtml:link")
print(f"\nSitemap regenere avec succes!")
print(f"  URLs totales: {new_count}")
print(f"  Balises hreflang: {hreflang_count}")
print(f"  Taille: {len(new_content) / 1024:.0f} Ko")
