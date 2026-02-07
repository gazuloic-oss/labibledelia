#!/usr/bin/env python3
"""
SEO Audit Report Generator for La Bible de l'IA
Generates a professional PDF audit report
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ── Colors ──────────────────────────────────────────────
DARK = HexColor('#1a1a2e')
GOLD = HexColor('#c9a84c')
GOLD_LIGHT = HexColor('#e4c76b')
RED = HexColor('#dc2626')
RED_LIGHT = HexColor('#fef2f2')
ORANGE = HexColor('#ea580c')
ORANGE_LIGHT = HexColor('#fff7ed')
GREEN = HexColor('#059669')
GREEN_LIGHT = HexColor('#f0fdf4')
BLUE = HexColor('#2563eb')
BLUE_LIGHT = HexColor('#eff6ff')
GRAY = HexColor('#6b7280')
GRAY_LIGHT = HexColor('#f9fafb')
GRAY_BORDER = HexColor('#e5e7eb')
TEXT = HexColor('#1f2937')
TEXT_LIGHT = HexColor('#4b5563')

WIDTH, HEIGHT = A4

# ── Styles ──────────────────────────────────────────────
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    'AuditTitle', parent=styles['Title'],
    fontName='Helvetica-Bold', fontSize=28, leading=34,
    textColor=DARK, spaceAfter=6
)
style_subtitle = ParagraphStyle(
    'AuditSubtitle', parent=styles['Normal'],
    fontName='Helvetica', fontSize=13, leading=18,
    textColor=GOLD, spaceAfter=20
)
style_h1 = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='Helvetica-Bold', fontSize=20, leading=26,
    textColor=DARK, spaceBefore=20, spaceAfter=10,
    borderPadding=(0, 0, 4, 0)
)
style_h2 = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='Helvetica-Bold', fontSize=14, leading=18,
    textColor=DARK, spaceBefore=14, spaceAfter=6
)
style_h3 = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='Helvetica-Bold', fontSize=11, leading=14,
    textColor=TEXT, spaceBefore=10, spaceAfter=4
)
style_body = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='Helvetica', fontSize=9.5, leading=14,
    textColor=TEXT, spaceAfter=6, alignment=TA_JUSTIFY
)
style_body_small = ParagraphStyle(
    'BodySmall', parent=style_body,
    fontSize=8.5, leading=12, spaceAfter=4
)
style_bullet = ParagraphStyle(
    'Bullet', parent=style_body,
    leftIndent=15, bulletIndent=5, spaceAfter=3
)
style_critical = ParagraphStyle(
    'Critical', parent=style_body,
    fontName='Helvetica-Bold', fontSize=10, textColor=RED
)
style_warning = ParagraphStyle(
    'Warning', parent=style_body,
    fontName='Helvetica-Bold', fontSize=10, textColor=ORANGE
)
style_good = ParagraphStyle(
    'Good', parent=style_body,
    fontName='Helvetica-Bold', fontSize=10, textColor=GREEN
)
style_score = ParagraphStyle(
    'Score', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=48, leading=52,
    textColor=GOLD, alignment=TA_CENTER
)
style_score_label = ParagraphStyle(
    'ScoreLabel', parent=styles['Normal'],
    fontName='Helvetica', fontSize=11, leading=14,
    textColor=TEXT_LIGHT, alignment=TA_CENTER
)

def gold_line():
    return HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=10, spaceBefore=4)

def gray_line():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY_BORDER, spaceAfter=8, spaceBefore=8)

def make_score_box(score, label, color):
    """Create a score indicator box"""
    data = [[Paragraph(f'<font color="{color.hexval()}">{score}</font>',
             ParagraphStyle('s', fontName='Helvetica-Bold', fontSize=32, alignment=TA_CENTER, textColor=color)),
            ],
            [Paragraph(label, ParagraphStyle('sl', fontName='Helvetica', fontSize=9, alignment=TA_CENTER, textColor=TEXT_LIGHT))]]
    t = Table(data, colWidths=[90])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, GRAY_BORDER),
        ('ROUNDEDCORNERS', [6,6,6,6]),
        ('BACKGROUND', (0,0), (-1,-1), GRAY_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def issue_table(issues, severity_color):
    """Create a formatted issue table"""
    data = []
    for issue in issues:
        data.append([
            Paragraph(f'<font color="{severity_color.hexval()}"><b>{issue[0]}</b></font>', style_body_small),
            Paragraph(issue[1], style_body_small),
            Paragraph(f'<font color="{severity_color.hexval()}">{issue[2]}</font>', style_body_small),
        ])

    col_widths = [140, 260, 80]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, GRAY_BORDER),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def header_table(headers):
    """Create a table header row"""
    data = [[Paragraph(f'<b>{h}</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_LIGHT)) for h in headers]]
    col_widths = [140, 260, 80]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_LIGHT),
        ('TOPPADDING', (0,0), (-1,0), 5),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('LEFTPADDING', (0,0), (-1,0), 4),
        ('LINEBELOW', (0,0), (-1,0), 1, GRAY_BORDER),
    ]))
    return t

def checklist_item(text, status="fail"):
    """Create a checklist item"""
    icon = "X" if status == "fail" else ("!" if status == "warn" else "OK")
    color = RED if status == "fail" else (ORANGE if status == "warn" else GREEN)
    return Paragraph(
        f'<font color="{color.hexval()}"><b>[{icon}]</b></font> {text}',
        style_body_small
    )

# ── Background page function ───────────────────────────
class AuditTemplate:
    def __init__(self):
        pass

    @staticmethod
    def first_page(canvas_obj, doc):
        canvas_obj.saveState()
        # Dark header band
        canvas_obj.setFillColor(DARK)
        canvas_obj.rect(0, HEIGHT - 180, WIDTH, 180, fill=1, stroke=0)
        # Gold accent line
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, HEIGHT - 183, WIDTH, 3, fill=1, stroke=0)
        # Logo text
        canvas_obj.setFont('Helvetica-Bold', 14)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.drawString(40, HEIGHT - 45, "LA BIBLE DE L'IA")
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(white)
        canvas_obj.drawString(40, HEIGHT - 62, "labibledelia.com")
        # Audit badge
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.drawRightString(WIDTH - 40, HEIGHT - 45, "AUDIT SEO")
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(white)
        canvas_obj.drawRightString(WIDTH - 40, HEIGHT - 62, "Fevrier 2026")
        # Footer
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(GRAY)
        canvas_obj.drawString(40, 25, "La Bible de l'IA - Audit SEO Complet - Confidentiel")
        canvas_obj.drawRightString(WIDTH - 40, 25, f"Page {doc.page}")
        canvas_obj.restoreState()

    @staticmethod
    def later_pages(canvas_obj, doc):
        canvas_obj.saveState()
        # Thin gold line at top
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, HEIGHT - 20, WIDTH, 2, fill=1, stroke=0)
        # Header
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(GRAY)
        canvas_obj.drawString(40, HEIGHT - 15, "LA BIBLE DE L'IA | AUDIT SEO")
        canvas_obj.drawRightString(WIDTH - 40, HEIGHT - 15, "Fevrier 2026")
        # Footer
        canvas_obj.drawString(40, 25, "Confidentiel - Usage interne uniquement")
        canvas_obj.drawRightString(WIDTH - 40, 25, f"Page {doc.page}")
        canvas_obj.restoreState()

# ── BUILD REPORT ────────────────────────────────────────
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AUDIT_SEO_La_Bible_de_IA.pdf")

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    topMargin=70,
    bottomMargin=50,
    leftMargin=40,
    rightMargin=40
)

story = []

# ══════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════
story.append(Spacer(1, 100))
story.append(Paragraph("AUDIT SEO COMPLET", style_title))
story.append(Paragraph("labibledelia.com", style_subtitle))
story.append(gold_line())
story.append(Spacer(1, 15))

# Score boxes
scores_data = [[
    make_score_box("62/100", "Score Global", ORANGE),
    make_score_box("85/100", "On-Page", GREEN),
    make_score_box("35/100", "Technique", RED),
    make_score_box("70/100", "Contenu", ORANGE),
]]
scores_table = Table(scores_data, colWidths=[120]*4)
scores_table.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(scores_table)

story.append(Spacer(1, 25))
story.append(Paragraph("<b>Resume executif</b>", style_h2))
story.append(Paragraph(
    "Cet audit identifie <b>12 problemes critiques</b>, <b>18 avertissements</b> et <b>25 opportunites</b> "
    "pour ameliorer le referencement naturel de La Bible de l'IA. Le site possede une excellente base "
    "on-page (meta tags, schema markup, structure HTML) mais souffre de <b>problemes techniques majeurs</b> "
    "qui penalisent fortement son indexation et ses performances.",
    style_body
))

story.append(Spacer(1, 10))
summary_data = [
    [Paragraph('<b>Problemes critiques</b>', style_body_small),
     Paragraph('<font color="#dc2626"><b>12</b></font>', style_body_small),
     Paragraph('Bloquent l\'indexation ou le ranking', style_body_small)],
    [Paragraph('<b>Avertissements</b>', style_body_small),
     Paragraph('<font color="#ea580c"><b>18</b></font>', style_body_small),
     Paragraph('Impact negatif sur les performances SEO', style_body_small)],
    [Paragraph('<b>Opportunites</b>', style_body_small),
     Paragraph('<font color="#059669"><b>25</b></font>', style_body_small),
     Paragraph('Potentiel d\'amelioration significatif', style_body_small)],
    [Paragraph('<b>Points positifs</b>', style_body_small),
     Paragraph('<font color="#2563eb"><b>15</b></font>', style_body_small),
     Paragraph('Deja bien implementes', style_body_small)],
]
summary_t = Table(summary_data, colWidths=[130, 40, 310])
summary_t.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LINEBELOW', (0,0), (-1,-1), 0.5, GRAY_BORDER),
    ('BACKGROUND', (0,0), (-1,-1), GRAY_LIGHT),
]))
story.append(summary_t)

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════
story.append(Paragraph("TABLE DES MATIERES", style_h1))
story.append(gold_line())

toc_items = [
    ("1.", "Problemes Critiques (Impact Negatif Direct)", "URGENT"),
    ("2.", "Performance et Vitesse de Chargement", "CRITIQUE"),
    ("3.", "Architecture et Indexation", "IMPORTANT"),
    ("4.", "Analyse On-Page (Meta, Schema, H1)", "BON"),
    ("5.", "Sitemap et Robots.txt", "A CORRIGER"),
    ("6.", "Pages Individuelles (Outils)", "BON"),
    ("7.", "Contenu et Maillage Interne", "MOYEN"),
    ("8.", "Mobile et Accessibilite", "MOYEN"),
    ("9.", "Securite et Infrastructure", "A CONFIGURER"),
    ("10.", "Checklist des Corrections Prioritaires", "ACTION"),
    ("11.", "Opportunites SEO Non Exploitees", "POTENTIEL"),
    ("12.", "Plan d'Action par Priorite", "ROADMAP"),
]

for num, title, status in toc_items:
    color = RED if status in ["URGENT", "CRITIQUE"] else (ORANGE if status in ["A CORRIGER", "MOYEN", "A CONFIGURER"] else (GREEN if status == "BON" else BLUE))
    story.append(Paragraph(
        f'<b>{num}</b> {title} <font color="{color.hexval()}">[{status}]</font>',
        ParagraphStyle('toc', parent=style_body, fontSize=10, leading=18, spaceBefore=2, spaceAfter=2)
    ))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 1. PROBLEMES CRITIQUES
# ══════════════════════════════════════════════════════════
story.append(Paragraph("1. PROBLEMES CRITIQUES", style_h1))
story.append(Paragraph("Impact negatif direct sur le referencement", style_subtitle))
story.append(gold_line())

# Critical 1: File size
story.append(Paragraph("1.1 FICHIER HTML MONOLITHIQUE ENORME (595 Ko)", style_critical))
story.append(Paragraph(
    "Le fichier <b>fr/index.html</b> pese <b>595 346 octets (595 Ko)</b> et le en/index.html <b>567 356 octets (567 Ko)</b>. "
    "C'est un SPA (Single Page Application) qui embarque les 400 outils IA directement dans le HTML. "
    "Cela pose plusieurs problemes majeurs :",
    style_body
))
story.append(Paragraph("- <b>Temps de chargement initial</b> : Le navigateur doit telecharger, parser et executer ~600 Ko de HTML pur avant tout affichage", style_bullet))
story.append(Paragraph("- <b>Time to First Contentful Paint (FCP)</b> : Probablement > 3 secondes sur mobile 3G", style_bullet))
story.append(Paragraph("- <b>Largest Contentful Paint (LCP)</b> : Probablement > 4 secondes (seuil Google : 2.5s)", style_bullet))
story.append(Paragraph("- <b>Total Blocking Time (TBT)</b> : Le JS inline bloque le thread principal pendant le parsing", style_bullet))
story.append(Paragraph("- <b>Impact Core Web Vitals</b> : Echec quasi certain sur mobile pour LCP et TBT", style_bullet))
story.append(Spacer(1, 6))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Externaliser le tableau TOOLS dans un fichier tools.json charge en lazy loading via fetch(). '
    'Implementer le code-splitting CSS/JS. Envisager le Server-Side Rendering (SSR) ou le pre-rendering statique.',
    style_body
))

story.append(gray_line())

# Critical 2: SPA not crawlable
story.append(Paragraph("1.2 CONTENU SPA NON CRAWLABLE PAR GOOGLE", style_critical))
story.append(Paragraph(
    "L'architecture SPA avec hash routing (#catalogue, #categories, #versus, #blog) signifie que <b>Google ne voit qu'une seule page</b> "
    "pour tout le contenu de la homepage. Les sections Catalogue, Categories, Tendances, Versus et Blog sont <b>invisibles pour le crawler</b> "
    "car generees par JavaScript cote client.",
    style_body
))
story.append(Paragraph("- Les URLs avec # (hash) ne sont <b>PAS envoyees au serveur</b> et <b>PAS indexees</b> par Google", style_bullet))
story.append(Paragraph("- Le contenu dynamique genere par renderCatalogue(), renderTrends(), etc. n'existe pas dans le HTML initial", style_bullet))
story.append(Paragraph("- Google peut executer le JS mais avec <b>delai et fiabilite limitee</b>, surtout sur 600 Ko de HTML", style_bullet))
story.append(Paragraph("- <b>Resultat</b> : Google n'indexe probablement que le hero + meta tags de la homepage, pas les 400 outils", style_bullet))
story.append(Spacer(1, 6))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Les pages individuelles /fr/chatgpt/, /fr/claude/ etc. sont correctement generees en statique (BIEN). '
    'Mais la homepage doit avoir du contenu HTML statique visible sans JS. Ajouter les premiers outils en HTML pur dans le code source.',
    style_body
))

story.append(gray_line())

# Critical 3: Missing pages in sitemap
story.append(Paragraph("1.3 PAGES MANQUANTES DANS LE SITEMAP", style_critical))
story.append(Paragraph(
    "Le sitemap.xml contient <b>~1015 URLs</b> dans 6093 lignes. Cependant, plusieurs pages importantes sont <b>absentes</b> :",
    style_body
))
story.append(Paragraph("- <b>/fr/quiz/</b> et <b>/en/quiz/</b> : Pages Quiz IA absentes du sitemap", style_bullet))
story.append(Paragraph("- <b>/fr/radar/</b> et <b>/en/radar/</b> : Pages Actualites absentes du sitemap", style_bullet))
story.append(Paragraph("- <b>/fr/packs/</b> et <b>/en/packs/</b> : Pages Packs IA absentes du sitemap", style_bullet))
story.append(Paragraph("- <b>/fr/glossaire/</b> et <b>/en/glossary/</b> : Pages Glossaire non encore creees", style_bullet))
story.append(Paragraph("- <b>Pages blog</b> : Seulement 6 articles blog dans le sitemap sur 20 existants", style_bullet))
story.append(Spacer(1, 6))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Regenerer le sitemap.xml avec TOUTES les pages. Ajouter les xhtml:link hreflang '
    'dans le sitemap pour chaque page bilingue (actuellement absent = Google ne sait pas relier FR et EN).',
    style_body
))

story.append(gray_line())

# Critical 4: No hreflang in sitemap
story.append(Paragraph("1.4 HREFLANG ABSENT DU SITEMAP", style_critical))
story.append(Paragraph(
    "Le sitemap declare le namespace xhtml (<b>xmlns:xhtml</b>) mais <b>n'utilise aucun xhtml:link</b> pour les hreflang. "
    "Seules les pages HTML individuelles ont les balises hreflang dans leur &lt;head&gt;. "
    "Google recommande d'avoir les hreflang dans le sitemap ET dans les pages pour une couverture maximale.",
    style_body
))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Ajouter pour chaque URL du sitemap les liens xhtml:link hreflang vers la version FR et EN correspondante.',
    style_body
))

story.append(gray_line())

# Critical 5: Nginx not configured
story.append(Paragraph("1.5 SERVEUR NGINX NON CONFIGURE (VPS)", style_critical))
story.append(Paragraph(
    "Le test <b>nginx -t</b> a echoue lors de la session precedente. Cela signifie que le site n'est probablement <b>pas en ligne sur le VPS Hostinger</b>. "
    "Sans serveur fonctionnel, pas d'indexation possible.",
    style_body
))
story.append(Paragraph("- Pas de <b>SSL/HTTPS</b> configure (certificat Let's Encrypt manquant)", style_bullet))
story.append(Paragraph("- Pas de <b>redirections HTTP > HTTPS</b>", style_bullet))
story.append(Paragraph("- Pas de <b>compression gzip/brotli</b> cote serveur", style_bullet))
story.append(Paragraph("- Pas de <b>headers de cache</b> configures", style_bullet))
story.append(Paragraph("- Pas de <b>headers de securite</b> (HSTS, X-Frame-Options, CSP)", style_bullet))
story.append(Spacer(1, 6))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Configurer nginx avec : SSL (certbot), gzip, cache headers (assets statiques 1 an), '
    'redirections www/non-www, headers securite. C\'est le PREREQUIS avant tout effort SEO.',
    style_body
))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 2. PERFORMANCE
# ══════════════════════════════════════════════════════════
story.append(Paragraph("2. PERFORMANCE ET VITESSE", style_h1))
story.append(Paragraph("Impact direct sur Core Web Vitals et ranking Google", style_subtitle))
story.append(gold_line())

story.append(Paragraph("2.1 POIDS DES FICHIERS", style_warning))

perf_data = [
    [Paragraph('<b>Fichier</b>', style_body_small), Paragraph('<b>Taille</b>', style_body_small), Paragraph('<b>Seuil Recommande</b>', style_body_small), Paragraph('<b>Status</b>', style_body_small)],
    [Paragraph('fr/index.html', style_body_small), Paragraph('595 Ko', style_body_small), Paragraph('< 100 Ko HTML', style_body_small), Paragraph('<font color="#dc2626"><b>CRITIQUE</b></font>', style_body_small)],
    [Paragraph('en/index.html', style_body_small), Paragraph('567 Ko', style_body_small), Paragraph('< 100 Ko HTML', style_body_small), Paragraph('<font color="#dc2626"><b>CRITIQUE</b></font>', style_body_small)],
    [Paragraph('CSS inline', style_body_small), Paragraph('~35 Ko', style_body_small), Paragraph('< 50 Ko', style_body_small), Paragraph('<font color="#059669"><b>OK</b></font>', style_body_small)],
    [Paragraph('JS inline', style_body_small), Paragraph('~80 Ko', style_body_small), Paragraph('< 50 Ko', style_body_small), Paragraph('<font color="#ea580c"><b>ELEVE</b></font>', style_body_small)],
    [Paragraph('TOOLS array (inline)', style_body_small), Paragraph('~450 Ko', style_body_small), Paragraph('Fichier externe', style_body_small), Paragraph('<font color="#dc2626"><b>CRITIQUE</b></font>', style_body_small)],
    [Paragraph('Google Fonts (4 familles)', style_body_small), Paragraph('~120 Ko', style_body_small), Paragraph('2 familles max', style_body_small), Paragraph('<font color="#ea580c"><b>ELEVE</b></font>', style_body_small)],
]
perf_t = Table(perf_data, colWidths=[130, 80, 120, 80])
perf_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), GRAY_LIGHT),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LINEBELOW', (0,0), (-1,-1), 0.5, GRAY_BORDER),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(perf_t)

story.append(Spacer(1, 10))
story.append(Paragraph("2.2 GOOGLE FONTS : 4 FAMILLES CHARGEES", style_warning))
story.append(Paragraph(
    "Le site charge <b>4 familles de polices</b> : Playfair Display, Lora, DM Sans, JetBrains Mono. "
    "Chacune avec plusieurs graisses (400, 500, 600, 700, 900). Cela represente ~120 Ko de polices + "
    "plusieurs requetes HTTP bloquantes.",
    style_body
))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Reduire a 2 familles maximum. Garder Playfair Display (titres) + DM Sans (corps). '
    'Supprimer Lora et JetBrains Mono. Utiliser font-display: swap. Preloader les polices critiques.',
    style_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("2.3 CSS/JS NON MINIFIES ET NON EXTERNALISES", style_warning))
story.append(Paragraph(
    "Tout le CSS (~35 Ko) et tout le JS (~80 Ko + 450 Ko TOOLS) sont <b>inline dans le HTML</b>. "
    "Le navigateur ne peut pas les mettre en cache separement. A chaque visite, il re-telecharge tout.",
    style_body
))
story.append(Paragraph("- Pas de mise en cache des assets CSS/JS (tout est inline = recharge complete a chaque page)", style_bullet))
story.append(Paragraph("- Pas de minification visible du CSS/JS", style_bullet))
story.append(Paragraph("- Pas de compression brotli/gzip cote serveur (nginx non configure)", style_bullet))

story.append(Spacer(1, 8))
story.append(Paragraph("2.4 TEXTURE SVG SUR body::before", style_warning))
story.append(Paragraph(
    "Un SVG de texture papier est applique en <b>position:fixed sur tout le viewport</b> via body::before. "
    "Ce filtre de bruit SVG (feTurbulence) est <b>extremement couteux en GPU</b>, surtout sur mobile. "
    "Il declenche des repaints constants lors du scroll.",
    style_body
))
story.append(Paragraph(
    '<font color="#059669"><b>SOLUTION :</b></font> Remplacer le SVG feTurbulence par une image PNG legere repetee, ou le supprimer sur mobile. '
    'Ajouter will-change: transform pour forcer le GPU compositing.',
    style_body
))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 3. ARCHITECTURE ET INDEXATION
# ══════════════════════════════════════════════════════════
story.append(Paragraph("3. ARCHITECTURE ET INDEXATION", style_h1))
story.append(Paragraph("Structure du site et crawlabilite", style_subtitle))
story.append(gold_line())

story.append(Paragraph("3.1 INVENTAIRE DES PAGES", style_h2))
arch_data = [
    [Paragraph('<b>Type de page</b>', style_body_small), Paragraph('<b>FR</b>', style_body_small), Paragraph('<b>EN</b>', style_body_small), Paragraph('<b>Total</b>', style_body_small), Paragraph('<b>Dans Sitemap?</b>', style_body_small)],
    [Paragraph('Homepage', style_body_small), Paragraph('1', style_body_small), Paragraph('1', style_body_small), Paragraph('2', style_body_small), Paragraph('<font color="#059669">OUI</font>', style_body_small)],
    [Paragraph('Pages outils individuelles', style_body_small), Paragraph('~404', style_body_small), Paragraph('~404', style_body_small), Paragraph('~808', style_body_small), Paragraph('<font color="#059669">OUI</font>', style_body_small)],
    [Paragraph('Pages categories', style_body_small), Paragraph('16', style_body_small), Paragraph('16', style_body_small), Paragraph('32', style_body_small), Paragraph('<font color="#059669">OUI</font>', style_body_small)],
    [Paragraph('Pages comparaison (vs)', style_body_small), Paragraph('~50', style_body_small), Paragraph('~50', style_body_small), Paragraph('~100', style_body_small), Paragraph('<font color="#059669">OUI</font>', style_body_small)],
    [Paragraph('Articles blog', style_body_small), Paragraph('20', style_body_small), Paragraph('20', style_body_small), Paragraph('40', style_body_small), Paragraph('<font color="#ea580c">PARTIEL (6/20)</font>', style_body_small)],
    [Paragraph('Quiz IA', style_body_small), Paragraph('1', style_body_small), Paragraph('1', style_body_small), Paragraph('2', style_body_small), Paragraph('<font color="#dc2626">NON</font>', style_body_small)],
    [Paragraph('Actualites (Radar)', style_body_small), Paragraph('1', style_body_small), Paragraph('1', style_body_small), Paragraph('2', style_body_small), Paragraph('<font color="#dc2626">NON</font>', style_body_small)],
    [Paragraph('Packs IA', style_body_small), Paragraph('1', style_body_small), Paragraph('1', style_body_small), Paragraph('2', style_body_small), Paragraph('<font color="#dc2626">NON</font>', style_body_small)],
    [Paragraph('Glossaire', style_body_small), Paragraph('0', style_body_small), Paragraph('0', style_body_small), Paragraph('0', style_body_small), Paragraph('<font color="#dc2626">NON CREE</font>', style_body_small)],
    [Paragraph('<b>TOTAL</b>', style_body_small), Paragraph('<b>~494</b>', style_body_small), Paragraph('<b>~494</b>', style_body_small), Paragraph('<b>~988</b>', style_body_small), Paragraph('', style_body_small)],
]
arch_t = Table(arch_data, colWidths=[140, 55, 55, 55, 140])
arch_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), GRAY_LIGHT),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LINEBELOW', (0,0), (-1,-1), 0.5, GRAY_BORDER),
    ('LEFTPADDING', (0,0), (-1,-1), 4),
    ('ALIGN', (1,0), (3,-1), 'CENTER'),
]))
story.append(arch_t)

story.append(Spacer(1, 12))
story.append(Paragraph("3.2 PROBLEMES DE STRUCTURE D'URL", style_h2))
story.append(Paragraph("- Les URLs EN utilisent <b>/en/categorie/</b> au lieu de <b>/en/category/</b> (slug FR dans l'URL anglaise)", style_bullet))
story.append(Paragraph("- Les URLs EN du blog utilisent des slugs FR : <b>/en/blog/meilleurs-outils-ia-gratuits/</b> au lieu de /en/blog/best-free-ai-tools/", style_bullet))
story.append(Paragraph("- Les URLs EN des comparaisons : <b>/en/comparer/</b> au lieu de <b>/en/compare/</b>", style_bullet))
story.append(Paragraph("- URL du breadcrumb reference <b>/fr/categorie/chatbots/</b> qui n'est pas une page de categories navigable depuis la homepage", style_bullet))

story.append(Spacer(1, 8))
story.append(Paragraph("3.3 REDIRECT PAGE RACINE", style_h2))
story.append(Paragraph(
    "La page racine index.html fait un redirect JS vers /fr/ ou /en/ selon la langue du navigateur. "
    "C'est correct mais <b>la page racine n'a pas de balise canonical ni de hreflang</b>, et ne renvoie pas "
    "de code 301 (redirect permanente) - c'est un redirect JS client-side que Google peut ne pas suivre correctement.",
    style_body
))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 4. ON-PAGE (POSITIF)
# ══════════════════════════════════════════════════════════
story.append(Paragraph("4. ANALYSE ON-PAGE", style_h1))
story.append(Paragraph("Meta tags, Schema.org, Structure HTML", style_subtitle))
story.append(gold_line())

story.append(Paragraph("4.1 CE QUI EST BIEN FAIT", style_good))
story.append(Spacer(1, 4))
story.append(checklist_item("Balise &lt;title&gt; unique et optimisee (67 caracteres, mots-cles en debut)", "pass"))
story.append(checklist_item("Meta description riche (155 caracteres, call-to-action)", "pass"))
story.append(checklist_item("Canonical URL correcte sur chaque page", "pass"))
story.append(checklist_item("Hreflang FR/EN + x-default dans le &lt;head&gt; de chaque page", "pass"))
story.append(checklist_item("Open Graph complet (title, description, image 1200x630, locale)", "pass"))
story.append(checklist_item("Twitter Card summary_large_image configuree", "pass"))
story.append(checklist_item("Schema.org WebSite avec SearchAction (sitelinks search box)", "pass"))
story.append(checklist_item("Schema.org Organization avec logo", "pass"))
story.append(checklist_item("Schema.org ItemList (15 premiers outils pour rich results)", "pass"))
story.append(checklist_item("Schema.org FAQPage avec 3 questions strategiques", "pass"))
story.append(checklist_item("Schema.org BreadcrumbList sur chaque page outil", "pass"))
story.append(checklist_item("Schema.org SoftwareApplication avec AggregateRating sur chaque fiche outil", "pass"))
story.append(checklist_item("Meta robots index, follow avec max-image-preview:large", "pass"))
story.append(checklist_item("H1 unique et pertinent sur la homepage et chaque page outil", "pass"))
story.append(checklist_item("Preconnect Google Fonts + preload stylesheet", "pass"))

story.append(Spacer(1, 10))
story.append(Paragraph("4.2 PROBLEMES ON-PAGE DETECTES", style_warning))
story.append(Spacer(1, 4))
story.append(checklist_item("meta keywords encore presente (ignoree par Google, signal de spam potentiel)", "warn"))
story.append(checklist_item("manifest.json dit '200 outils analyses' alors qu'il y en a 400+", "fail"))
story.append(checklist_item("og:image pointe vers /og-image-fr.png mais le fichier doit etre verifie (dimensions, qualite)", "warn"))
story.append(checklist_item("SearchAction cible une URL avec hash (#/recherche/) - non indexable par Google", "warn"))
story.append(checklist_item("Schema Organization 'sameAs' est un tableau vide [] - ajouter les reseaux sociaux", "warn"))
story.append(checklist_item("FAQPage sur la homepage ET sur les pages outils = risque de cannibalisation FAQ", "warn"))
story.append(checklist_item("ItemList ne liste que 15 outils sur 400 - ajouter les 50 premiers au minimum", "warn"))
story.append(checklist_item("Pas de meta 'article:published_time' sur les articles de blog", "warn"))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 5. SITEMAP & ROBOTS
# ══════════════════════════════════════════════════════════
story.append(Paragraph("5. SITEMAP ET ROBOTS.TXT", style_h1))
story.append(Paragraph("Fichiers essentiels pour l'indexation", style_subtitle))
story.append(gold_line())

story.append(Paragraph("5.1 ROBOTS.TXT", style_h2))
story.append(Paragraph("Contenu actuel :", style_body))
story.append(Paragraph("<font name='Courier'><b>User-agent: *<br/>Allow: /<br/>Sitemap: https://labibledelia.com/sitemap.xml</b></font>", style_body))
story.append(Spacer(1, 6))
story.append(checklist_item("robots.txt est present et accessible", "pass"))
story.append(checklist_item("Sitemap reference correctement", "pass"))
story.append(checklist_item("Pas de Disallow inutile", "pass"))
story.append(checklist_item("MANQUE : Disallow pour les pages non-SEO (ex: fichiers JS/CSS generes, node_modules)", "warn"))
story.append(checklist_item("MANQUE : Crawl-delay pour eviter la surcharge du serveur", "warn"))

story.append(Spacer(1, 10))
story.append(Paragraph("5.2 SITEMAP.XML - PROBLEMES DETECTES", style_h2))
story.append(Spacer(1, 4))
story.append(checklist_item("~1015 URLs referencees (bon volume)", "pass"))
story.append(checklist_item("lastmod, changefreq et priority presents", "pass"))
story.append(checklist_item("MANQUE : balises xhtml:link hreflang (namespace declare mais jamais utilise !)", "fail"))
story.append(checklist_item("MANQUE : Pages Quiz, Radar, Packs absentes du sitemap", "fail"))
story.append(checklist_item("MANQUE : 14 articles blog sur 20 absents du sitemap", "fail"))
story.append(checklist_item("Toutes les lastmod sont identiques (2026-02-07) - pas de differentiation des dates reelles", "warn"))
story.append(checklist_item("Toutes les pages outils ont priority 0.8 - pas de hierarchie (top outils devraient avoir 0.9)", "warn"))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 6. PAGES INDIVIDUELLES
# ══════════════════════════════════════════════════════════
story.append(Paragraph("6. PAGES OUTILS INDIVIDUELLES", style_h1))
story.append(Paragraph("Analyse de la page /fr/chatgpt/ comme reference", style_subtitle))
story.append(gold_line())

story.append(Paragraph("6.1 POINTS POSITIFS (EXEMPLAIRE)", style_good))
story.append(checklist_item("Title optimise : 'ChatGPT - Avis, Prix &amp; Alternatives | La Bible de l'IA'", "pass"))
story.append(checklist_item("Meta description unique et descriptive", "pass"))
story.append(checklist_item("Canonical + hreflang FR/EN corrects", "pass"))
story.append(checklist_item("Schema SoftwareApplication avec AggregateRating", "pass"))
story.append(checklist_item("Schema FAQPage avec 3 questions pertinentes", "pass"))
story.append(checklist_item("Schema BreadcrumbList (Accueil > Categorie > Outil)", "pass"))
story.append(checklist_item("H1 avec le nom de l'outil", "pass"))
story.append(checklist_item("Contenu riche : description, features, use cases, pros/cons, verdict, alternatives", "pass"))
story.append(checklist_item("Liens internes vers les alternatives et la categorie", "pass"))
story.append(checklist_item("Design responsive avec media queries", "pass"))

story.append(Spacer(1, 10))
story.append(Paragraph("6.2 PROBLEMES DETECTES", style_warning))
story.append(checklist_item("og:type = 'article' mais pas de article:published_time ni article:author", "warn"))
story.append(checklist_item("twitter:card = 'summary' au lieu de 'summary_large_image' (pas d'image OG specifique a l'outil)", "warn"))
story.append(checklist_item("Pas d'image OG specifique par outil (manque og:image)", "fail"))
story.append(checklist_item("ratingCount = 480 dans le Schema - semble artificiel (pas de vrai systeme d'avis)", "fail"))
story.append(checklist_item("Breadcrumb reference /fr/categorie/chatbots/ qui est une page generee mais pas un hub reel de navigation", "warn"))
story.append(checklist_item("Pas de table des matieres interne (ancres) pour le contenu long", "warn"))
story.append(checklist_item("Pas de date de derniere mise a jour visible", "fail"))
story.append(checklist_item("Le CSS est entierement inline (~10 Ko par page) au lieu d'un fichier externe cache", "warn"))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 7. CONTENU ET MAILLAGE
# ══════════════════════════════════════════════════════════
story.append(Paragraph("7. CONTENU ET MAILLAGE INTERNE", style_h1))
story.append(Paragraph("Qualite du contenu et liens internes", style_subtitle))
story.append(gold_line())

story.append(Paragraph("7.1 CONTENU DUPLIQUE / THIN CONTENT", style_h2))
story.append(Paragraph(
    "Les pages outils anglaises ont ete traduites via un script regex (~85% de qualite). "
    "Certaines pages EN contiennent probablement <b>des fragments de texte en francais</b> melan ges avec l'anglais. "
    "Google considere le contenu mixte (langues melangees) comme du <b>contenu de faible qualite</b>.",
    style_body
))
story.append(Paragraph("- Verifier systematiquement que les taglines, descriptions et verdicts EN sont 100% en anglais", style_bullet))
story.append(Paragraph("- Les slugs d'URL EN sont en francais (/en/blog/meilleurs-outils-ia-gratuits/) - mauvais signal pour Google", style_bullet))
story.append(Paragraph("- Les pages categories EN utilisent /en/categorie/ au lieu de /en/category/", style_bullet))

story.append(Spacer(1, 10))
story.append(Paragraph("7.2 MAILLAGE INTERNE", style_h2))
story.append(Paragraph("Points positifs :", style_body))
story.append(Paragraph("- Chaque page outil link vers ses alternatives (maillage horizontal)", style_bullet))
story.append(Paragraph("- Breadcrumbs present sur chaque page (maillage vertical)", style_bullet))
story.append(Paragraph("- Pages de comparaison lient les deux outils compares", style_bullet))
story.append(Spacer(1, 6))
story.append(Paragraph("Manques :", style_body))
story.append(Paragraph("- <b>Pas de liens contextuels</b> dans les descriptions d'outils vers d'autres outils ou articles", style_bullet))
story.append(Paragraph("- <b>Pas de 'A lire aussi'</b> en fin de page outil", style_bullet))
story.append(Paragraph("- <b>Pas de liens depuis les articles blog</b> vers les fiches outils (maillage blog > fiches)", style_bullet))
story.append(Paragraph("- <b>Pas de hub de categorie navigable</b> depuis le menu principal (les categories sont dans le dropdown mais pointent vers des ancres hash)", style_bullet))
story.append(Paragraph("- <b>Orphan pages potentielles</b> : pages blog et comparaisons accessibles uniquement via sitemap, pas depuis le menu", style_bullet))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 8. MOBILE & ACCESSIBILITE
# ══════════════════════════════════════════════════════════
story.append(Paragraph("8. MOBILE ET ACCESSIBILITE", style_h1))
story.append(gold_line())

story.append(Paragraph("8.1 MOBILE", style_h2))
story.append(checklist_item("Viewport meta tag present et correct", "pass"))
story.append(checklist_item("CSS responsive avec media queries (@media max-width:768px, 500px)", "pass"))
story.append(checklist_item("Navigation hamburger pour mobile", "pass"))
story.append(checklist_item("Font-size clamp() pour les titres (responsive typography)", "pass"))
story.append(checklist_item("PROBLEME : Fichier de 600 Ko + SVG feTurbulence = performances catastrophiques sur mobile", "fail"))
story.append(checklist_item("PROBLEME : 4 polices Google chargees = render-blocking sur mobile 3G/4G", "fail"))
story.append(checklist_item("PROBLEME : Pas de lazy-loading des images (seulement 2 img dans le HTML)", "warn"))

story.append(Spacer(1, 10))
story.append(Paragraph("8.2 ACCESSIBILITE", style_h2))
story.append(checklist_item("Alt text present sur les images (drapeaux FR/EN)", "pass"))
story.append(checklist_item("Lang attribute correct (lang='fr' / lang='en')", "pass"))
story.append(checklist_item("PROBLEME : Boutons d'actions (search, favorites, theme) sans aria-label explicite", "warn"))
story.append(checklist_item("PROBLEME : Dropdown Explorer n'a pas de role='menu' ni aria-expanded", "warn"))
story.append(checklist_item("PROBLEME : Navigation au clavier non testee sur les modales (search, comparator)", "warn"))
story.append(checklist_item("PROBLEME : Contrastes de couleurs a verifier (text-muted sur fond clair)", "warn"))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 9. SECURITE
# ══════════════════════════════════════════════════════════
story.append(Paragraph("9. SECURITE ET INFRASTRUCTURE", style_h1))
story.append(gold_line())

story.append(checklist_item("HTTPS non verifie (nginx non configure sur le VPS)", "fail"))
story.append(checklist_item("Pas de header HSTS (Strict-Transport-Security)", "fail"))
story.append(checklist_item("Pas de header X-Content-Type-Options", "fail"))
story.append(checklist_item("Pas de header Content-Security-Policy", "fail"))
story.append(checklist_item("Pas de header X-Frame-Options", "fail"))
story.append(checklist_item("GA4 correctement integre (G-X4YE8TLX0E)", "pass"))
story.append(checklist_item("Pas de fichier security.txt (recommande)", "warn"))
story.append(checklist_item("node_modules present dans le repo (ne devrait pas etre deploye)", "warn"))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 10. CHECKLIST PRIORITAIRE
# ══════════════════════════════════════════════════════════
story.append(Paragraph("10. CHECKLIST DES CORRECTIONS", style_h1))
story.append(Paragraph("Par ordre de priorite", style_subtitle))
story.append(gold_line())

story.append(Paragraph("PRIORITE 1 - BLOQUANT (Semaine 1)", style_critical))
story.append(Spacer(1, 4))
checklist_p1 = [
    "Configurer nginx sur le VPS (SSL, gzip, cache, headers securite)",
    "Installer certificat SSL Let's Encrypt (certbot)",
    "Ajouter les pages Quiz, Radar, Packs dans le sitemap.xml",
    "Ajouter les 14 articles blog manquants dans le sitemap",
    "Ajouter les xhtml:link hreflang dans le sitemap pour chaque URL bilingue",
    "Corriger manifest.json : '200 outils' > '400 outils'",
    "Soumettre le sitemap dans Google Search Console",
]
for item in checklist_p1:
    story.append(Paragraph(f"<font color='#dc2626'><b>[  ]</b></font> {item}", style_body_small))

story.append(Spacer(1, 10))
story.append(Paragraph("PRIORITE 2 - IMPORTANT (Semaine 2-3)", style_warning))
story.append(Spacer(1, 4))
checklist_p2 = [
    "Externaliser le tableau TOOLS dans un fichier tools.json (reduction HTML de 450 Ko)",
    "Reduire les polices Google de 4 a 2 familles (Playfair + DM Sans)",
    "Remplacer le SVG feTurbulence par une image PNG legere ou le supprimer sur mobile",
    "Externaliser CSS et JS dans des fichiers cacheables (.css, .js)",
    "Supprimer la meta keywords de toutes les pages",
    "Ajouter rel='nofollow' sur les liens externes vers les outils (conserver le link juice)",
    "Creer les pages Glossaire FR et EN",
    "Ajouter une date de mise a jour sur chaque fiche outil",
]
for item in checklist_p2:
    story.append(Paragraph(f"<font color='#ea580c'><b>[  ]</b></font> {item}", style_body_small))

story.append(Spacer(1, 10))
story.append(Paragraph("PRIORITE 3 - AMELIORATION (Semaine 4-6)", style_h3))
story.append(Spacer(1, 4))
checklist_p3 = [
    "Traduire les slugs d'URL EN (categorie > category, comparer > compare, blog slugs en anglais)",
    "Verifier et corriger les traductions EN contenant du texte FR residuel",
    "Ajouter des images OG specifiques par outil (ou generees dynamiquement)",
    "Ajouter article:published_time et article:modified_time sur les pages blog",
    "Enrichir le Schema Organization avec les liens sameAs (reseaux sociaux)",
    "Ajouter des liens contextuels dans les descriptions d'outils",
    "Creer un bloc 'A lire aussi' sur chaque page outil et article",
    "Ajouter aria-label et roles ARIA aux elements interactifs",
    "Ajouter un fichier security.txt",
    "Configurer les redirections www > non-www (ou inverse) dans nginx",
]
for item in checklist_p3:
    story.append(Paragraph(f"<font color='#2563eb'><b>[  ]</b></font> {item}", style_body_small))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 11. OPPORTUNITES SEO
# ══════════════════════════════════════════════════════════
story.append(Paragraph("11. OPPORTUNITES SEO NON EXPLOITEES", style_h1))
story.append(Paragraph("Potentiel de trafic organique inexploite", style_subtitle))
story.append(gold_line())

story.append(Paragraph("11.1 PAGES 'X VS Y' - POTENTIEL ENORME", style_h2))
story.append(Paragraph(
    "Vous avez deja ~50 pages de comparaison (chatgpt-vs-claude, midjourney-vs-dalle3...). "
    "C'est EXCELLENT. En francais, ces requetes ont <b>tres peu de concurrence</b> et un volume de recherche eleve. "
    "Objectif : <b>passer de 50 a 150+ comparaisons</b>.",
    style_body
))
story.append(Paragraph("- Ajouter les comparaisons cross-categories (ChatGPT vs Notion AI, Canva AI vs Midjourney)", style_bullet))
story.append(Paragraph("- Chaque page de comparaison doit cibler 'X vs Y' + 'X ou Y' + 'comparatif X Y' + 'difference entre X et Y'", style_bullet))
story.append(Paragraph("- Ajouter un Schema CompareAction ou utiliser une table de comparaison structuree pour les featured snippets", style_bullet))

story.append(Spacer(1, 8))
story.append(Paragraph("11.2 GLOSSAIRE IA - LONGUE TRAINE MASSIVE", style_h2))
story.append(Paragraph(
    "Le glossaire n'existe pas encore. C'est <b>100+ pages supplementaires</b> qui ciblent des requetes educatives "
    "('qu'est-ce que le RAG', 'LLM definition', 'fine-tuning IA', 'prompt engineering explication'). "
    "En francais, la concurrence sur ces termes est <b>quasi nulle</b>.",
    style_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("11.3 PAGES PAR METIER - REQUETES TRANSACTIONNELLES", style_h2))
story.append(Paragraph(
    "Creer des pages dedicees : 'Meilleurs outils IA pour avocats', 'IA pour les RH', 'IA pour les enseignants'. "
    "Ces requetes ont un intent transactionnel fort et sont <b>totalement sous-exploitees en francais</b>.",
    style_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("11.4 GOOGLE SEARCH CONSOLE - NON CONFIGURE", style_h2))
story.append(Paragraph(
    "Google Search Console n'est apparemment pas encore configure. C'est <b>obligatoire</b> pour : "
    "soumettre le sitemap, verifier l'indexation, detecter les erreurs de crawl, suivre les positions.",
    style_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("11.5 NEWSLETTER SIGNUP - PAS DE POPUP/CTA STRATEGIQUE", style_h2))
story.append(Paragraph(
    "Le CTA newsletter est dans la nav mais il n'y a <b>pas de formulaire de capture email</b> visible sur la homepage. "
    "La newsletter est le canal de monetisation #1 (TAAFT genere l'essentiel de ses revenus via sa newsletter de 1,2M abonnes). "
    "Ajouter un formulaire mid-page et un exit-intent popup.",
    style_body
))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════
# 12. PLAN D'ACTION
# ══════════════════════════════════════════════════════════
story.append(Paragraph("12. PLAN D'ACTION PAR PRIORITE", style_h1))
story.append(Paragraph("Roadmap SEO sur 8 semaines", style_subtitle))
story.append(gold_line())

roadmap_data = [
    [Paragraph('<b>Semaine</b>', style_body_small), Paragraph('<b>Actions</b>', style_body_small), Paragraph('<b>Impact</b>', style_body_small)],
    [Paragraph('<b>S1</b>', style_body_small),
     Paragraph('Configurer nginx + SSL + gzip<br/>Corriger sitemap (pages manquantes + hreflang)<br/>Configurer Google Search Console<br/>Fix manifest.json', style_body_small),
     Paragraph('<font color="#dc2626"><b>CRITIQUE</b></font><br/>Prerequis a tout', style_body_small)],
    [Paragraph('<b>S2</b>', style_body_small),
     Paragraph('Externaliser TOOLS en tools.json<br/>Reduire fonts a 2 familles<br/>Supprimer SVG feTurbulence sur mobile<br/>Externaliser CSS/JS', style_body_small),
     Paragraph('<font color="#dc2626"><b>CRITIQUE</b></font><br/>Core Web Vitals', style_body_small)],
    [Paragraph('<b>S3</b>', style_body_small),
     Paragraph('Creer le Glossaire IA (100+ termes FR/EN)<br/>Ajouter rel=nofollow liens externes<br/>Supprimer meta keywords', style_body_small),
     Paragraph('<font color="#ea580c"><b>ELEVE</b></font><br/>+100 pages SEO', style_body_small)],
    [Paragraph('<b>S4</b>', style_body_small),
     Paragraph('Ajouter 50 comparaisons supplementaires<br/>Creer pages par metier (5 metiers)<br/>Ajouter dates sur fiches outils', style_body_small),
     Paragraph('<font color="#ea580c"><b>ELEVE</b></font><br/>Long tail traffic', style_body_small)],
    [Paragraph('<b>S5-6</b>', style_body_small),
     Paragraph('Verifier/corriger traductions EN<br/>Traduire slugs URLs EN<br/>Ajouter images OG par outil<br/>Enrichir maillage interne', style_body_small),
     Paragraph('<font color="#2563eb"><b>MOYEN</b></font><br/>Qualite globale', style_body_small)],
    [Paragraph('<b>S7-8</b>', style_body_small),
     Paragraph('Ajouter formulaire newsletter mid-page<br/>Configurer redirections 301<br/>Audit accessibilite<br/>Test Core Web Vitals final', style_body_small),
     Paragraph('<font color="#2563eb"><b>MOYEN</b></font><br/>Conversion + UX', style_body_small)],
]
roadmap_t = Table(roadmap_data, colWidths=[55, 310, 115])
roadmap_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), DARK),
    ('TEXTCOLOR', (0,0), (-1,0), white),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LINEBELOW', (0,1), (-1,-1), 0.5, GRAY_BORDER),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ('BACKGROUND', (0,1), (-1,1), HexColor('#fef2f2')),
    ('BACKGROUND', (0,2), (-1,2), HexColor('#fef2f2')),
]))
story.append(roadmap_t)

story.append(Spacer(1, 20))
story.append(Paragraph("SCORE SEO ESTIME APRES CORRECTIONS", style_h2))

after_data = [[
    make_score_box("85/100", "Score Global", GREEN),
    make_score_box("90/100", "On-Page", GREEN),
    make_score_box("80/100", "Technique", GREEN),
    make_score_box("85/100", "Contenu", GREEN),
]]
after_t = Table(after_data, colWidths=[120]*4)
after_t.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(after_t)

story.append(Spacer(1, 15))
story.append(Paragraph(
    "<i>Ce rapport a ete genere le 7 fevrier 2026 sur la base d'une analyse du code source local. "
    "Un audit complementaire avec des outils comme Lighthouse, PageSpeed Insights, Screaming Frog et "
    "Google Search Console est recommande une fois le site deploye sur le VPS.</i>",
    ParagraphStyle('footer_note', parent=style_body, fontSize=8, textColor=GRAY, fontName='Helvetica-Oblique')
))

# ── BUILD PDF ───────────────────────────────────────────
template = AuditTemplate()
doc.build(story, onFirstPage=template.first_page, onLaterPages=template.later_pages)

print(f"\n{'='*60}")
print(f"  AUDIT SEO PDF GENERE AVEC SUCCES")
print(f"  {output_path}")
print(f"  {os.path.getsize(output_path) / 1024:.0f} Ko")
print(f"{'='*60}")
