#!/usr/bin/env python3
"""
========================================================
  La Bible de l'IA — Script de mise à jour automatique
========================================================

Ce script met à jour TOUT automatiquement quand tu modifies
le TOOLS array ou les articles blog :

  1. Compte les outils, catégories, comparaisons
  2. Met à jour TOUS les compteurs (hero, meta, OG, Schema, footer)
  3. Met à jour la date de dernière mise à jour
  4. Régénère toutes les pages outils/catégories/comparaisons
  5. Régénère toutes les pages blog

Usage:
  python update.py          → Tout mettre à jour
  python update.py --dry    → Voir ce qui changerait sans modifier
  python update.py --count  → Juste afficher les compteurs actuels
"""

import re, os, sys, datetime, subprocess, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FR_FILE = os.path.join(BASE_DIR, "fr", "index.html")
EN_FILE = os.path.join(BASE_DIR, "en", "index.html")

# ============================================================
# UTILITAIRES
# ============================================================

def extract_js_array_count(filepath, array_name):
    """Compte les éléments d'un array JS dans le fichier HTML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver le début du array
    pattern = f'const {array_name}=['
    start = content.find(pattern)
    if start == -1:
        pattern = f'const {array_name} = ['
        start = content.find(pattern)
    if start == -1:
        return 0

    # Compter les objets {id:"..."} dans le array
    array_start = content.find('[', start)
    bracket_depth = 0
    count = 0
    i = array_start
    while i < len(content):
        char = content[i]
        if char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
            if bracket_depth == 0:
                break
        elif char == '{' and bracket_depth == 1:
            count += 1
        i += 1
    return count


def count_comparison_pairs(filepath):
    """Compte les paires de comparaison dans renderVersus()."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver renderVersus et extraire les paires
    match = re.search(r'renderVersus\(\)\{[^}]*const pairs=\[(.*?)\];', content, re.DOTALL)
    if not match:
        return 0
    pairs_text = match.group(1)
    # Compter les paires ['a','b']
    return len(re.findall(r"\['[^']+','[^']+'\]", pairs_text))


def count_blog_articles(filepath):
    """Compte les articles blog dans renderBlog()."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'renderBlog\(\)\{[^{]*const articles=\[(.*?)\];', content, re.DOTALL)
    if not match:
        return 0
    articles_text = match.group(1)
    return len(re.findall(r"\{slug:", articles_text))


def get_current_month_fr():
    """Retourne le mois actuel en français."""
    months = {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',
              7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'}
    now = datetime.date.today()
    return f"{months[now.month]} {now.year}"


def get_current_month_en():
    """Retourne le mois actuel en anglais."""
    months = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
              7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    now = datetime.date.today()
    return f"{months[now.month]} {now.year}"


# ============================================================
# MISE À JOUR DES COMPTEURS
# ============================================================

def update_counters(filepath, lang, tool_count, cat_count, versus_count, blog_count, dry_run=False):
    """Met à jour tous les compteurs dans un fichier index.html."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    current_month = get_current_month_fr() if lang == 'fr' else get_current_month_en()

    # --- REGEX REPLACEMENTS ---

    # 1. data-count pour outils
    old_match = re.search(r'data-count="(\d+)"(>0</div><div class="lbl">Outils analysés|>0</div><div class="lbl">Tools analyzed)', content)
    if old_match:
        old_count = old_match.group(1)
        if old_count != str(tool_count):
            content = content.replace(
                f'data-count="{old_count}"{old_match.group(2)}',
                f'data-count="{tool_count}"{old_match.group(2)}'
            )
            changes.append(f'  Hero outils: {old_count} -> {tool_count}')

    # 2. data-count pour comparatifs
    old_match = re.search(r'data-count="(\d+)"(>0</div><div class="lbl">Comparatifs|>0</div><div class="lbl">Comparisons)', content)
    if old_match:
        old_count = old_match.group(1)
        if old_count != str(versus_count):
            content = content.replace(
                f'data-count="{old_count}"{old_match.group(2)}',
                f'data-count="{versus_count}"{old_match.group(2)}'
            )
            changes.append(f'  Hero comparatifs: {old_count} -> {versus_count}')

    # 3. data-count pour catégories
    old_match = re.search(r'data-count="(\d+)"(>0</div><div class="lbl">Cat[eé]gories)', content)
    if old_match:
        old_count = old_match.group(1)
        if old_count != str(cat_count):
            content = content.replace(
                f'data-count="{old_count}"{old_match.group(2)}',
                f'data-count="{cat_count}"{old_match.group(2)}'
            )
            changes.append(f'  Hero catégories: {old_count} -> {cat_count}')

    # 4. numberOfItems dans Schema.org
    old_match = re.search(r'"numberOfItems":\s*(\d+)', content)
    if old_match:
        old_count = old_match.group(1)
        if old_count != str(tool_count):
            content = content.replace(f'"numberOfItems": {old_count}', f'"numberOfItems": {tool_count}')
            content = content.replace(f'"numberOfItems":{old_count}', f'"numberOfItems":{tool_count}')
            changes.append(f'  Schema numberOfItems: {old_count} -> {tool_count}')

    # 5. Meta descriptions, OG, Twitter — remplacer l'ancien nombre d'outils par le nouveau
    # On cherche le pattern "N outils" ou "N tools" dans les meta/og/twitter/schema
    if lang == 'fr':
        # Trouver l'ancien nombre dans les meta (premier match)
        old_num_match = re.search(r'<meta name="description" content="[^"]*?(\d+) outils', content)
        if old_num_match:
            old_num = old_num_match.group(1)
            if old_num != str(tool_count):
                # Remplacer N outils -> nouveau N outils dans les 150 premières lignes (meta/schema)
                lines = content.split('\n')
                for i in range(min(150, len(lines))):
                    lines[i] = re.sub(rf'\b{old_num} outils\b', f'{tool_count} outils', lines[i])
                content = '\n'.join(lines)
                changes.append(f'  Meta/OG/Schema "{old_num} outils" -> "{tool_count} outils"')

        # resultsCount default
        content = re.sub(
            r'(<span[^>]*id="resultsCount">)\d+ outils(</span>)',
            rf'\g<1>{tool_count} outils\2',
            content
        )

        # Footer brand desc
        old_footer = re.search(r'(\d+) outils analysés, comparés et notés pour vous', content)
        if old_footer and old_footer.group(1) != str(tool_count):
            content = content.replace(
                f'{old_footer.group(1)} outils analysés, comparés et notés pour vous',
                f'{tool_count} outils analysés, comparés et notés pour vous'
            )
            changes.append(f'  Footer desc: {old_footer.group(1)} -> {tool_count}')

        # Footer bottom
        old_footer2 = re.search(r'(\d+) outils recensés', content)
        if old_footer2 and old_footer2.group(1) != str(tool_count):
            content = content.replace(
                f'{old_footer2.group(1)} outils recensés',
                f'{tool_count} outils recensés'
            )
            changes.append(f'  Footer bottom: {old_footer2.group(1)} -> {tool_count}')

        # Date de mise à jour footer
        old_date = re.search(r'Dernière mise à jour : ([A-ZÉa-zéû]+ \d{4})', content)
        if old_date and old_date.group(1) != current_month:
            content = content.replace(
                f'Dernière mise à jour : {old_date.group(1)}',
                f'Dernière mise à jour : {current_month}'
            )
            changes.append(f'  Date: {old_date.group(1)} -> {current_month}')

    else:  # EN
        old_num_match = re.search(r'<meta name="description" content="[^"]*?(\d+) tools', content)
        if old_num_match:
            old_num = old_num_match.group(1)
            if old_num != str(tool_count):
                lines = content.split('\n')
                for i in range(min(150, len(lines))):
                    lines[i] = re.sub(rf'\b{old_num} tools\b', f'{tool_count} tools', lines[i])
                    lines[i] = re.sub(rf'\b{old_num} AI tools\b', f'{tool_count} AI tools', lines[i])
                    lines[i] = re.sub(rf'\b{old_num} artificial intelligence tools\b', f'{tool_count} artificial intelligence tools', lines[i])
                content = '\n'.join(lines)
                changes.append(f'  Meta/OG/Schema "{old_num} tools" -> "{tool_count} tools"')

        content = re.sub(
            r'(<span[^>]*id="resultsCount">)\d+ tools(</span>)',
            rf'\g<1>{tool_count} tools\2',
            content
        )

        old_footer = re.search(r'(\d+) tools analyzed, compared, and rated to help', content)
        if old_footer and old_footer.group(1) != str(tool_count):
            content = content.replace(
                f'{old_footer.group(1)} tools analyzed, compared, and rated to help',
                f'{tool_count} tools analyzed, compared, and rated to help'
            )
            changes.append(f'  Footer desc: {old_footer.group(1)} -> {tool_count}')

        old_footer2 = re.search(r'(\d+) tools listed', content)
        if old_footer2 and old_footer2.group(1) != str(tool_count):
            content = content.replace(
                f'{old_footer2.group(1)} tools listed',
                f'{tool_count} tools listed'
            )
            changes.append(f'  Footer bottom: {old_footer2.group(1)} -> {tool_count}')

        old_date = re.search(r'Last updated: ([A-Za-z]+ \d{4})', content)
        if old_date and old_date.group(1) != current_month:
            content = content.replace(
                f'Last updated: {old_date.group(1)}',
                f'Last updated: {current_month}'
            )
            changes.append(f'  Date: {old_date.group(1)} -> {current_month}')

    # Écrire si des changements
    if content != original:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        return changes
    return []


# ============================================================
# RÉGÉNÉRATION DES PAGES
# ============================================================

def regenerate_pages():
    """Régénère toutes les pages outils/catégories/comparaisons."""
    print("\n[3/4] Regeneration des pages outils/categories/versus...")
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, 'generate-pages.py')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=BASE_DIR, env=env
    )
    if result.returncode != 0:
        print(f"  ERREUR: {result.stderr[:500]}")
        return False
    # Extraire le résumé
    for line in result.stdout.split('\n'):
        if 'DONE' in line or 'pages generated' in line or 'Total pages' in line:
            print(f"  {line.strip()}")
    return True


def regenerate_blog():
    """Régénère toutes les pages blog."""
    print("\n[4/4] Regeneration des pages blog...")
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, 'generate-blog.py')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=BASE_DIR, env=env
    )
    if result.returncode != 0:
        print(f"  ERREUR: {result.stderr[:500]}")
        return False
    for line in result.stdout.split('\n'):
        if 'Done' in line or 'articles' in line.lower():
            print(f"  {line.strip()}")
    return True


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  La Bible de l'IA - Script de mise a jour automatique")
    print("=" * 60)

    dry_run = '--dry' in sys.argv
    count_only = '--count' in sys.argv

    if dry_run:
        print("  MODE DRY-RUN : aucune modification ne sera effectuee\n")

    # --- ÉTAPE 1 : Compter ---
    print("[1/4] Analyse des donnees actuelles...")

    fr_tools = extract_js_array_count(FR_FILE, 'TOOLS')
    fr_cats = extract_js_array_count(FR_FILE, 'CATEGORIES')
    en_tools = extract_js_array_count(EN_FILE, 'TOOLS')
    en_cats = extract_js_array_count(EN_FILE, 'CATEGORIES')

    fr_versus = count_comparison_pairs(FR_FILE)
    en_versus = count_comparison_pairs(EN_FILE)

    fr_blog = count_blog_articles(FR_FILE)
    en_blog = count_blog_articles(EN_FILE)

    print(f"\n  FR : {fr_tools} outils | {fr_cats} categories | {fr_versus} versus | {fr_blog} articles blog")
    print(f"  EN : {en_tools} outils | {en_cats} categories | {en_versus} versus | {en_blog} articles blog")

    if fr_tools != en_tools:
        print(f"\n  ATTENTION : FR ({fr_tools}) et EN ({en_tools}) ont un nombre d'outils different !")

    if count_only:
        return

    # --- ÉTAPE 2 : Mettre à jour les compteurs ---
    print(f"\n[2/4] Mise a jour des compteurs...")

    fr_changes = update_counters(FR_FILE, 'fr', fr_tools, fr_cats, fr_versus, fr_blog, dry_run)
    en_changes = update_counters(EN_FILE, 'en', en_tools, en_cats, en_versus, en_blog, dry_run)

    if fr_changes:
        print(f"\n  FR - {len(fr_changes)} modification(s) :")
        for c in fr_changes:
            print(f"    {c}")
    else:
        print("  FR : compteurs deja a jour")

    if en_changes:
        print(f"\n  EN - {len(en_changes)} modification(s) :")
        for c in en_changes:
            print(f"    {c}")
    else:
        print("  EN : compteurs deja a jour")

    if dry_run:
        print("\n  [DRY-RUN] Aucun fichier modifie.")
        print("  Relancez sans --dry pour appliquer les changements.")
        return

    # --- ÉTAPE 3 : Régénérer les pages ---
    pages_ok = regenerate_pages()

    # --- ÉTAPE 4 : Régénérer le blog ---
    blog_ok = regenerate_blog()

    # --- RÉSUMÉ ---
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(f"  Outils  : {fr_tools} FR / {en_tools} EN")
    print(f"  Categories : {fr_cats}")
    print(f"  Versus  : {fr_versus} paires")
    print(f"  Blog    : {fr_blog} articles")
    print(f"  Pages   : {'OK' if pages_ok else 'ERREUR'}")
    print(f"  Blog    : {'OK' if blog_ok else 'ERREUR'}")
    print(f"  Compteurs : {len(fr_changes) + len(en_changes)} modifications")
    print(f"\n  Prochaine etape : git add . && git commit && git push")
    print("=" * 60)


if __name__ == '__main__':
    main()
