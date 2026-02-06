#!/usr/bin/env python3
"""
================================================================
  La Bible de l'IA — Mise à jour automatique
================================================================

FRÉQUENCES :
  - Chaque SEMAINE  : compteurs, dates, régénération des pages
  - Toutes les 2 SEMAINES : tendances IA, choix de la rédaction
                             (ajustement des scores de popularité)

Ce script gère les deux cas automatiquement en vérifiant
le numéro de semaine (pair = tendances + compteurs, impair = compteurs seul).

Usage:
  python weekly_auto_update.py                  → Auto (détecte la fréquence)
  python weekly_auto_update.py --trends         → Forcer la mise à jour des tendances
  python weekly_auto_update.py --counters-only  → Juste les compteurs
  python weekly_auto_update.py --dry            → Aperçu sans modifier
  python weekly_auto_update.py --no-push        → Commit sans push
"""

import re, os, sys, random, datetime, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FR_FILE = os.path.join(BASE_DIR, "fr", "index.html")
EN_FILE = os.path.join(BASE_DIR, "en", "index.html")

TODAY = datetime.date.today()
WEEK_NUM = int(TODAY.strftime('%W'))
IS_BIWEEKLY = (WEEK_NUM % 2 == 0)  # Semaines paires = mise à jour tendances

# Seed le random avec la semaine actuelle pour des résultats
# reproductibles mais différents chaque cycle
random.seed(int(TODAY.strftime('%Y%W')))


# ============================================================
# 1. AJUSTEMENT DES TENDANCES (toutes les 2 semaines)
# ============================================================

def extract_tools_data(filepath):
    """Extrait tous les outils avec leur id, popularity, rating, launchYear."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    start = content.find('const TOOLS=[')
    if start == -1:
        start = content.find('const TOOLS = [')
    if start == -1:
        return [], content

    array_start = content.find('[', start)
    bracket_depth = 0
    end = array_start
    for i in range(array_start, len(content)):
        if content[i] == '[':
            bracket_depth += 1
        elif content[i] == ']':
            bracket_depth -= 1
            if bracket_depth == 0:
                end = i + 1
                break

    array_text = content[array_start:end]

    tools = []
    pattern = re.compile(
        r'\{id:"([^"]+)".*?popularity:(\d+).*?rating:([\d.]+).*?launchYear:(\d+)',
        re.DOTALL
    )
    for m in pattern.finditer(array_text):
        tools.append({
            'id': m.group(1),
            'popularity': int(m.group(2)),
            'rating': float(m.group(3)),
            'launchYear': int(m.group(4))
        })

    return tools, content


def calculate_new_popularity(tool):
    """Calcule un nouveau score de popularité ajusté."""
    pop = tool['popularity']
    rating = tool['rating']
    year = tool['launchYear']
    current_year = TODAY.year

    # --- Règle 1 : Boost outils récents ---
    if year >= current_year:
        pop += random.randint(1, 3)
    elif year >= current_year - 1:
        pop += random.randint(0, 2)

    # --- Règle 2 : Légère baisse outils anciens ---
    if year <= current_year - 4 and random.random() < 0.3:
        pop -= 1

    # --- Règle 3 : Boost pépites méconnues ---
    if rating >= 4.5 and pop < 50:
        pop += random.randint(1, 3)
    elif rating >= 4.3 and pop < 40:
        pop += random.randint(0, 2)

    # --- Règle 4 : Variation aléatoire ---
    # Pondéré : plus de chances de rester stable ou monter légèrement
    variation = random.choices([-2, -1, 0, 0, 0, 0, 1, 1, 2], k=1)[0]
    pop += variation

    # --- Règle 5 : Protection des leaders ---
    original = tool['popularity']
    if original >= 90:
        pop = max(pop, 85)
    elif original >= 80:
        pop = max(pop, 70)
    elif original >= 60:
        pop = max(pop, 50)

    # Bornes globales
    pop = max(5, min(100, pop))

    return pop


def apply_popularity_updates(filepath, dry_run=False):
    """Met à jour les scores de popularité dans le fichier."""
    tools, content = extract_tools_data(filepath)

    if not tools:
        return 0, []

    changes = 0
    details = []

    for tool in tools:
        new_pop = calculate_new_popularity(tool)
        if new_pop != tool['popularity']:
            tool_pattern = re.compile(
                rf'(\{{id:"{re.escape(tool["id"])}".*?popularity:){tool["popularity"]}',
                re.DOTALL
            )
            new_content = tool_pattern.sub(rf'\g<1>{new_pop}', content, count=1)
            if new_content != content:
                content = new_content
                diff = new_pop - tool['popularity']
                sign = '+' if diff > 0 else ''
                details.append(f'{tool["id"]}: {tool["popularity"]} -> {new_pop} ({sign}{diff})')
                changes += 1

    if changes > 0 and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return changes, details


# ============================================================
# 2. MISE À JOUR DES DATES (chaque semaine)
# ============================================================

def get_month_name(lang):
    """Retourne le mois actuel dans la langue demandée."""
    if lang == 'fr':
        months = {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',
                  7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'}
    else:
        months = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                  7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    return f"{months[TODAY.month]} {TODAY.year}"


def update_dates(filepath, lang, dry_run=False):
    """Met à jour toutes les dates de dernière mise à jour."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    current_month = get_month_name(lang)

    if lang == 'fr':
        # Footer bottom
        content = re.sub(
            r'Dernière mise à jour : [A-ZÉÀa-zéûôèê]+ \d{4}',
            f'Dernière mise à jour : {current_month}',
            content
        )
        # Blog article dates
        content = re.sub(
            r"<span>([A-ZÉÀa-zéûôèê]+ \d{4})</span></div>\s*</a>",
            f"<span>{current_month}</span></div>\n      </a>",
            content
        )
    else:
        content = re.sub(
            r'Last updated: [A-Za-z]+ \d{4}',
            f'Last updated: {current_month}',
            content
        )
        content = re.sub(
            r"<span>([A-Za-z]+ \d{4})</span></div>\s*</a>",
            f"<span>{current_month}</span></div>\n      </a>",
            content
        )

    changed = content != original
    if changed and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return changed


# ============================================================
# 3. COMPTEURS + RÉGÉNÉRATION (chaque semaine)
# ============================================================

def run_update_py():
    """Lance update.py pour compteurs + régénération."""
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, 'update.py')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=BASE_DIR, env=env
    )
    summary = []
    for line in result.stdout.split('\n'):
        if any(k in line for k in ['Outils', 'Categories', 'Versus', 'Blog',
                                     'DONE', 'pages generated', 'Total']):
            summary.append(line.strip())
    return result.returncode == 0, summary


# ============================================================
# 4. GIT COMMIT + PUSH
# ============================================================

def git_commit_and_push(push=True, msg_suffix=""):
    """Commit et push les changements."""
    # Stage
    subprocess.run(['git', 'add', '-A'], cwd=BASE_DIR, capture_output=True)

    # Vérifier s'il y a des changements
    result = subprocess.run(
        ['git', 'diff', '--cached', '--stat'],
        cwd=BASE_DIR, capture_output=True, text=True
    )
    if not result.stdout.strip():
        print("  Aucun changement a committer.")
        return False

    lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
    print(f"  {len(lines)} fichiers modifies")

    # Commit message
    week = TODAY.strftime('%W')
    date_str = TODAY.strftime('%Y-%m-%d')
    commit_msg = f"Auto-update {date_str} (W{week}): {msg_suffix}"

    subprocess.run(
        ['git', 'commit', '-m', commit_msg],
        cwd=BASE_DIR, capture_output=True
    )
    print(f"  Commit: {commit_msg}")

    # Push
    if push:
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=BASE_DIR, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  Push OK")
            return True
        else:
            print(f"  Push ERREUR: {result.stderr[:200]}")
            return False

    print("  Push skip (--no-push)")
    return True


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  La Bible de l'IA - Mise a jour automatique")
    print(f"  {TODAY} | Semaine {WEEK_NUM} | {'Paire' if IS_BIWEEKLY else 'Impaire'}")
    print("=" * 60)

    dry_run = '--dry' in sys.argv
    no_push = '--no-push' in sys.argv
    force_trends = '--trends' in sys.argv
    counters_only = '--counters-only' in sys.argv

    # Déterminer ce qu'on fait
    do_trends = (IS_BIWEEKLY or force_trends) and not counters_only
    msg_parts = []

    if dry_run:
        print("  MODE DRY-RUN\n")

    # =========================
    # TENDANCES (bi-hebdomadaire)
    # =========================
    if do_trends:
        print(f"\n[1/4] Ajustement des tendances (semaine paire = cycle bi-hebdo)")
        fr_changes, fr_details = apply_popularity_updates(FR_FILE, dry_run)
        en_changes, en_details = apply_popularity_updates(EN_FILE, dry_run)
        print(f"  FR : {fr_changes} outils ajustes")
        print(f"  EN : {en_changes} outils ajustes")

        # Afficher les top mouvements
        if fr_details:
            # Trier par amplitude du changement
            sorted_details = sorted(fr_details, key=lambda x: abs(int(x.split('(')[1].rstrip(')'))), reverse=True)
            print(f"  Top mouvements :")
            for d in sorted_details[:10]:
                print(f"    {d}")

        msg_parts.append(f"trends ({fr_changes} outils)")
    else:
        print(f"\n[1/4] Tendances : SKIP (semaine impaire, prochain cycle semaine {WEEK_NUM + 1})")
        if force_trends:
            print("  (force via --trends)")

    # =========================
    # DATES (hebdomadaire)
    # =========================
    print(f"\n[2/4] Mise a jour des dates...")
    fr_date = update_dates(FR_FILE, 'fr', dry_run)
    en_date = update_dates(EN_FILE, 'en', dry_run)
    print(f"  FR : {'mis a jour' if fr_date else 'deja a jour'}")
    print(f"  EN : {'mis a jour' if en_date else 'deja a jour'}")
    if fr_date or en_date:
        msg_parts.append("dates")

    if dry_run:
        print("\n[DRY-RUN] Aucune modification appliquee.")
        return

    # =========================
    # COMPTEURS + REGEN (hebdomadaire)
    # =========================
    print(f"\n[3/4] Compteurs + regeneration des pages...")
    ok, summary = run_update_py()
    if ok:
        for line in summary:
            print(f"  {line}")
        msg_parts.append("counters + pages regenerated")
    else:
        print("  ERREUR lors de la regeneration")
        msg_parts.append("counters (regen error)")

    # =========================
    # GIT
    # =========================
    print(f"\n[4/4] Git commit & push...")
    commit_suffix = " + ".join(msg_parts) if msg_parts else "weekly refresh"
    git_commit_and_push(push=not no_push, msg_suffix=commit_suffix)

    # =========================
    # RÉSUMÉ
    # =========================
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(f"  Type de mise a jour : {'Tendances + Compteurs' if do_trends else 'Compteurs seulement'}")
    if do_trends:
        print(f"  Tendances ajustees  : {fr_changes + en_changes} outils modifies")
    print(f"  Dates               : {'Mises a jour' if (fr_date or en_date) else 'Deja a jour'}")
    print(f"  Pages regenerees    : {'Oui' if ok else 'Erreur'}")
    print(f"  Git push            : {'Oui' if not no_push else 'Non'}")
    print(f"\n  Prochain cycle tendances : semaine {WEEK_NUM + (2 if IS_BIWEEKLY else 1)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
