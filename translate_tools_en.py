#!/usr/bin/env python3
"""Translate French tools in en/index.html to English using regex replacements."""
import re, os

FILE = os.path.join(os.path.dirname(__file__), 'en', 'index.html')

# === MASSIVE TRANSLATION DICTIONARY ===
# Ordered from longest to shortest to avoid partial matches

TRANSLATIONS = [
    # === FULL TAGLINES / DESCRIPTIONS (common patterns) ===
    ("Discutez avec vos documents et créez des chatbots de connaissances", "Chat with your documents and create knowledge chatbots"),
    ("Agent de recherche IA qui fouille la littérature scientifique en profondeur", "AI research agent that deeply explores scientific literature"),
    ("Plateforme de recherche IA avec paper espresso et mind maps", "AI research platform with paper espresso and mind maps"),
    ("API de recherche web optimisée pour les agents IA", "Web search API optimized for AI agents"),
    ("Création de sites web assistée par IA avec design professionnel", "AI-assisted website creation with professional design"),
    ("Créez des présentations, sites et documents visuels par IA", "Create presentations, websites and visual documents with AI"),
    ("Le builder de sites web avec IA et animations cinématiques", "The website builder with AI and cinematic animations"),
    ("Générez des interfaces web complètes à partir de descriptions textuelles", "Generate complete web interfaces from text descriptions"),
    ("Convertissez des maquettes Figma en code responsive propre", "Convert Figma mockups into clean responsive code"),

    # === COMMON SENTENCE PATTERNS ===
    ("permet de converser avec vos documents", "lets you chat with your documents"),
    ("permet de créer des", "lets you create"),
    ("permet de générer des", "lets you generate"),
    ("permet de", "lets you"),
    ("qui permet de", "that lets you"),
    ("qui permet", "that allows"),
    ("enrichit son builder de sites web avec l'IA", "enhances its website builder with AI"),
    ("génère des présentations", "generates presentations"),
    ("génère des interfaces web complètes", "generates complete web interfaces"),
    ("à partir de descriptions textuelles", "from text descriptions"),
    ("à partir de simples descriptions", "from simple descriptions"),
    ("à partir de", "from"),
    ("grâce à l'IA", "thanks to AI"),
    ("grâce à", "thanks to"),
    ("basé sur les preuves scientifiques", "based on scientific evidence"),
    ("basé sur", "based on"),
    ("basée sur", "based on"),
    ("conçu pour les LLM et agents IA", "designed for LLMs and AI agents"),
    ("conçu spécifiquement pour", "specifically designed for"),
    ("conçu pour", "designed for"),
    ("conçue pour", "designed for"),
    ("Idéal pour les équipes de recherche", "Ideal for research teams"),
    ("Idéal pour les équipes", "Ideal for teams"),
    ("Idéal pour", "Ideal for"),
    ("Parfait pour les équipes qui partagent des documents", "Perfect for teams sharing documents"),
    ("Parfait pour", "Perfect for"),
    ("en temps réel", "in real time"),
    ("sans code", "no-code"),
    ("tout-en-un", "all-in-one"),
    ("de qualité agence", "agency-quality"),
    ("de qualité", "quality"),
    ("Copy-paste le code directement dans votre projet", "Copy-paste the code directly into your project"),
    ("directement dans", "directly into"),
    ("L'IA crée le design, le contenu et la mise en page", "AI creates the design, content, and layout"),
    ("L'IA comprend la structure", "AI understands the structure"),

    # === VERDICT PATTERNS ===
    ("La recherche médicale evidence-based par IA. Un must pour les professionnels de santé.", "AI-powered evidence-based medical research. A must for healthcare professionals."),
    ("L'agent de recherche le plus approfondi. Comme avoir un assistant de recherche infatigable.", "The most thorough research agent. Like having a tireless research assistant."),
    ("La base de connaissances IA collaborative. Parfait pour les équipes qui partagent des documents.", "The collaborative AI knowledge base. Perfect for teams sharing documents."),
    ("L'approche visuelle de la recherche. Paper Espresso + mind maps = compréhension accélérée.", "The visual approach to research. Paper Espresso + mind maps = accelerated understanding."),
    ("L'API de recherche qui manquait aux agents IA. Résultats propres et structurés pour les LLM.", "The search API that AI agents were missing. Clean, structured results for LLMs."),
    ("Le builder de sites web le plus puissant, maintenant avec IA. Le choix des designers.", "The most powerful website builder, now with AI. The designers' choice."),
    ("De l'idée à la présentation en 30 secondes. Gamma redéfinit la création visuelle rapide.", "From idea to presentation in 30 seconds. Gamma redefines rapid visual creation."),
    ("Le builder des sites qui impressionnent. Animations cinématiques + IA = sites de qualité agence.", "The builder of impressive websites. Cinematic animations + AI = agency-quality sites."),
    ("Le générateur d'UI de référence. Code propre Tailwind/shadcn prêt à copier-coller.", "The reference UI generator. Clean Tailwind/shadcn code ready to copy-paste."),
    ("Le pont entre Figma et le code. Convertissez vos maquettes en sites responsive.", "The bridge between Figma and code. Convert your mockups into responsive sites."),
    ("Un must pour", "A must for"),
    ("Le choix des", "The choice of"),
    ("Le builder des", "The builder of"),
    ("Le builder de", "The builder of"),
    ("Le générateur de", "The generator of"),
    ("Le générateur d'", "The generator of"),
    ("La plateforme de", "The platform for"),
    ("Le pont entre", "The bridge between"),
    ("L'approche", "The approach"),
    ("De l'idée à", "From idea to"),
    ("redéfinit", "redefines"),
    ("maintenant avec", "now with"),

    # === PRICING NOTES ===
    ("Free (basique)", "Free (basic)"),
    ("Free (limité)", "Free (limited)"),
    ("basique", "basic"),

    # === FEATURES ===
    ("Recherche médicale IA", "AI medical research"),
    ("Essais cliniques", "Clinical trials"),
    ("Réponses sourcées", "Sourced answers"),
    ("Guidelines intégrées", "Integrated guidelines"),
    ("PubMed integration", "PubMed integration"),
    ("PICO framework", "PICO framework"),
    ("Recherche profonde IA", "AI deep search"),
    ("Explication du raisonnement", "Reasoning explanation"),
    ("Ranking de pertinence", "Relevance ranking"),
    ("Multi-queries", "Multi-queries"),
    ("Résumés contextuels", "Contextual summaries"),
    ("Full-text access", "Full-text access"),
    ("Chat multi-documents", "Multi-document chat"),
    ("Citations de sources", "Source citations"),
    ("Chatbots partageables", "Shareable chatbots"),
    ("Multi-formats", "Multi-format"),
    ("Collaboration d'équipe", "Team collaboration"),
    ("Paper Espresso (résumés)", "Paper Espresso (summaries)"),
    ("Mind maps automatiques", "Automatic mind maps"),
    ("Annotations IA", "AI annotations"),
    ("Library management", "Library management"),
    ("API de recherche pour IA", "Search API for AI"),
    ("Résultats structurés", "Structured results"),
    ("Content extraction", "Content extraction"),
    ("Multi-sources", "Multi-source"),
    ("Filtres avancés", "Advanced filters"),
    ("Compatible LangChain", "LangChain compatible"),
    ("Layout generation IA", "AI layout generation"),
    ("Content IA", "AI content"),
    ("CMS puissant", "Powerful CMS"),
    ("Animations natives", "Native animations"),
    ("E-commerce", "E-commerce"),
    ("Custom code", "Custom code"),
    ("IA de layout", "AI layout"),
    ("Animations cinématiques", "Cinematic animations"),
    ("CMS intégré", "Built-in CMS"),
    ("Responsive natif", "Native responsive"),
    ("Interactions avancées", "Advanced interactions"),
    ("Localisation", "Localization"),
    ("Texte vers UI", "Text to UI"),
    ("Code exportable", "Exportable code"),
    ("Itérations", "Iterations"),
    ("Preview live", "Live preview"),
    ("Figma vers code", "Figma to code"),
    ("Responsive automatique", "Automatic responsive"),
    ("CMS headless", "Headless CMS"),
    ("Hébergement inclus", "Hosting included"),

    # === USE CASES ===
    ("Recherche de preuves cliniques", "Clinical evidence research"),
    ("Décisions médicales informées", "Informed medical decisions"),
    ("Revue systématique", "Systematic review"),
    ("Formation médicale continue", "Continuing medical education"),
    ("Recherche de niche", "Niche research"),
    ("Papers difficiles à trouver", "Hard-to-find papers"),
    ("Revue de littérature exhaustive", "Comprehensive literature review"),
    ("Découverte de connections", "Connection discovery"),
    ("Base de connaissances IA", "AI knowledge base"),
    ("Analyse de documents", "Document analysis"),
    ("FAQ automatisées", "Automated FAQs"),
    ("Recherche collaborative", "Collaborative research"),
    ("Résumer des papers rapidement", "Summarize papers quickly"),
    ("Cartographier un domaine", "Map a domain"),
    ("Organiser sa recherche", "Organize your research"),
    ("Préparation de présentations", "Presentation preparation"),
    ("Recherche web pour agents IA", "Web search for AI agents"),
    ("RAG avec données web", "RAG with web data"),
    ("Applications de recherche", "Research applications"),
    ("Fact-checking automatisé", "Automated fact-checking"),
    ("Sites web professionnels", "Professional websites"),
    ("Landing pages", "Landing pages"),
    ("Portfolios", "Portfolios"),
    ("Présentations rapides", "Quick presentations"),
    ("Sites web simples", "Simple websites"),
    ("Propositions commerciales", "Business proposals"),
    ("Rapports visuels", "Visual reports"),
    ("Sites de startups", "Startup websites"),
    ("Portfolios créatifs", "Creative portfolios"),
    ("Sites d'agence", "Agency websites"),
    ("Prototypage UI", "UI prototyping"),
    ("Composants web", "Web components"),
    ("Dashboards", "Dashboards"),
    ("Convertir des maquettes en code", "Convert mockups to code"),
    ("Sites web depuis Figma", "Websites from Figma"),
    ("Prototypage rapide", "Rapid prototyping"),
    ("Handoff design-dev", "Design-dev handoff"),

    # === PROS ===
    ("Spécialisé médical", "Medical specialty"),
    ("Sources vérifiables", "Verifiable sources"),
    ("Framework PICO", "PICO framework"),
    ("Recherche profonde", "Deep search"),
    ("Transparent dans son raisonnement", "Transparent reasoning"),
    ("Résultats de qualité", "Quality results"),
    ("Multi-documents", "Multi-document"),
    ("Prix abordable", "Affordable pricing"),
    ("Paper Espresso original", "Original Paper Espresso"),
    ("Mind maps utiles", "Useful mind maps"),
    ("Gratuit généreux", "Generous free tier"),
    ("Conçu pour les LLM", "Designed for LLMs"),
    ("Résultats propres", "Clean results"),
    ("Design professionnel", "Professional design"),
    ("No-code avancé", "Advanced no-code"),
    ("Animations incroyables", "Amazing animations"),
    ("IA de layout", "AI layout"),
    ("Design premium", "Premium design"),
    ("Code propre", "Clean code"),
    ("Tailwind natif", "Native Tailwind"),
    ("Itérations rapides", "Fast iterations"),
    ("Rapide et beau", "Fast and beautiful"),
    ("Multi-formats", "Multi-format"),
    ("Figma to code", "Figma to code"),

    # === CONS ===
    ("5 docs en gratuit", "5 docs on free plan"),
    ("Interface basique", "Basic interface"),
    ("Qualité variable", "Variable quality"),
    ("Niche médical", "Medical niche"),
    ("Anglais uniquement", "English only"),
    ("Gratuit limité", "Limited free tier"),
    ("Lent (recherche en profondeur)", "Slow (deep search)"),
    ("Nouveau", "New"),
    ("Interface en anglais", "English interface"),
    ("Fonctionnalités en développement", "Features in development"),
    ("Communauté en croissance", "Growing community"),
    ("API uniquement", "API only"),
    ("Pas d'interface web", "No web interface"),
    ("Résultats parfois incomplets", "Sometimes incomplete results"),
    ("Courbe d'apprentissage", "Learning curve"),
    ("Prix premium", "Premium pricing"),
    ("Complexe pour débutants", "Complex for beginners"),
    ("Performance variable", "Variable performance"),
    ("CMS basique vs Webflow", "Basic CMS vs Webflow"),
    ("Design parfois générique", "Sometimes generic design"),
    ("Personnalisation limitée", "Limited customization"),
    ("Export limité en gratuit", "Limited export on free plan"),
    ("Composants moyens", "Average components"),
    ("React/Next.js seulement", "React/Next.js only"),
    ("Limité en gratuit", "Limited on free plan"),
    ("Qualité code variable", "Variable code quality"),
    ("Customization limitée", "Limited customization"),
    ("Moins connu", "Less known"),

    # === GENERIC FRENCH → ENGLISH WORD REPLACEMENTS ===
    ("recherche", "research"),
    ("littérature médicale", "medical literature"),
    ("littérature scientifique", "scientific literature"),
    ("essais cliniques", "clinical trials"),
    ("professionnels de santé", "healthcare professionals"),
    ("preuves scientifiques", "scientific evidence"),
    ("documents", "documents"),
    ("connaissances", "knowledge"),
    ("chatbots", "chatbots"),
    ("équipes", "teams"),
    ("équipe", "team"),
    ("entreprises", "companies"),
    ("entreprise", "company"),
    ("académique", "academic"),
    ("scientifique", "scientific"),
    ("médical", "medical"),
    ("santé", "health"),
    ("papers", "papers"),
    ("résumé", "summary"),
    ("résumés", "summaries"),
    ("mind-map", "mind-map"),
    ("agents", "agents"),
    ("structurés", "structured"),
    ("site-web", "website"),
    ("sites web", "websites"),
    ("site web", "website"),
    ("no-code", "no-code"),
    ("design", "design"),
    ("professionnel", "professional"),
    ("présentations", "presentations"),
    ("présentation", "presentation"),
    ("sites", "sites"),
    ("visuel", "visual"),
    ("visuels", "visuals"),
    ("animations", "animations"),
    ("agence", "agency"),
    ("composants", "components"),
    ("tailwind", "tailwind"),
    ("génération", "generation"),
    ("conversion", "conversion"),
    ("responsive", "responsive"),
    ("maquettes", "mockups"),
    ("maquette", "mockup"),
    ("automatique", "automatic"),
    ("collaboration", "collaboration"),
    ("intégration", "integration"),
    ("création", "creation"),
    ("rédaction", "writing"),
    ("automatisation", "automation"),
    ("développeur", "developer"),
    ("développeurs", "developers"),
    ("utilisateur", "user"),
    ("utilisateurs", "users"),
    ("navigateur", "browser"),
    ("assistant", "assistant"),
    ("données", "data"),
    ("contenu", "content"),
    ("texte", "text"),
    ("vidéo", "video"),
    ("audio", "audio"),
    ("image", "image"),
    ("images", "images"),
    ("musique", "music"),
    ("outil", "tool"),
    ("outils", "tools"),
    ("plateforme", "platform"),
    ("plateformes", "platforms"),
    ("fonctionnalités", "features"),
    ("fonctionnalité", "feature"),
    ("personnalisation", "customization"),
    ("optimisation", "optimization"),
    ("génère", "generates"),
    ("analysé", "analyzed"),
    ("analysés", "analyzed"),
    ("comparé", "compared"),
    ("comparés", "compared"),
    ("noté", "rated"),
    ("notés", "rated"),

    # === COMMON DESCRIPTION FRAGMENTS ===
    ("recherche dans la littérature", "searches the literature"),
    ("Réponses sourcées pour les", "Sourced answers for"),
    ("explore la littérature scientifique en profondeur", "deeply explores scientific literature"),
    ("pense, cherche et relit comme un chercheur humain", "thinks, searches and re-reads like a human researcher"),
    ("pour trouver les papers les plus pertinents", "to find the most relevant papers"),
    ("converser avec vos documents (PDF, Word, Web)", "chat with your documents (PDF, Word, Web)"),
    ("créer des chatbots de connaissances partagés", "create shared knowledge chatbots"),
    ("combine lecture de papers", "combines paper reading"),
    ("génération de résumés", "summary generation"),
    ("mind maps automatiques pour une recherche académique", "automatic mind maps for academic research"),
    ("plus efficace et visuelle", "more efficient and visual"),
    ("fournit une API de recherche web", "provides a web search API"),
    ("spécifiquement pour les LLM et agents IA", "specifically for LLMs and AI agents"),
    ("Résultats propres, structurés et optimisés pour l'injection dans des prompts", "Clean, structured results optimized for prompt injection"),
    ("enrichit son builder de sites web avec l'IA : génération de layouts, rédaction de contenu et optimisation automatique", "enhances its website builder with AI: layout generation, content writing, and automatic optimization"),
    ("pour un design professionnel sans code", "for professional no-code design"),
    ("des sites web one-page et des documents visuels", "one-page websites and visual documents"),
    ("L'IA crée le design, le contenu et la mise en page", "AI creates the design, content, and layout"),
    ("créer des sites web de qualité agence avec des animations cinématiques et l'IA", "create agency-quality websites with cinematic animations and AI"),
    ("Génération de contenu, layouts adaptatifs et interactions avancées", "Content generation, adaptive layouts and advanced interactions"),
    ("avec Tailwind CSS et shadcn/ui à partir de simples descriptions", "with Tailwind CSS and shadcn/ui from simple descriptions"),
    ("convertit vos designs Figma en code HTML/CSS/React propre et responsive", "converts your Figma designs into clean responsive HTML/CSS/React code"),
    ("comprend la structure, génère du code maintenable et gère le responsive", "understands the structure, generates maintainable code and handles responsive"),
]

def translate_line(line):
    """Apply all translations to a line."""
    result = line
    for fr, en in TRANSLATIONS:
        result = result.replace(fr, en)
    return result

def is_french_tool_line(line):
    """Check if a tool line contains French text."""
    stripped = line.strip()
    if not stripped.startswith('{id:"'):
        return False
    french_indicators = [
        'tagline:"D', 'tagline:"C', 'tagline:"G', 'tagline:"L', 'tagline:"P',
        'tagline:"R', 'tagline:"A', 'tagline:"U', 'tagline:"E',
        'permet de', 'Idéal pour', 'Parfait pour', 'Créez', 'Générez',
        'Discutez', 'à partir de', 'grâce à', 'en temps réel',
        'outil IA', 'plateforme', 'création', 'génération',
        'rédaction', 'automatisation', 'Recherche', 'Analyse',
        'conçu pour', 'qui permet', 'basé sur',
        'verdict:"L', 'verdict:"U', 'verdict:"D',
        '"médical"', '"santé"', '"résumé"', '"académique"',
        '"scientifique"', '"équipe"', '"connaissances"',
        '"présentations"', '"site-web"', '"visuel"',
        '"rédaction"', '"automatisation"', '"création"',
        'Courbe d', 'Prix premium', 'Gratuit limité',
        'Gratuit généreux', 'Interface basique',
    ]
    return any(ind in stripped for ind in french_indicators)

def main():
    print("=== Traduction des outils FR -> EN ===")

    with open(FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_tools = False
    translated_count = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect TOOLS array start
        if 'const TOOLS' in stripped and '[' in stripped:
            in_tools = True
            continue

        # Detect TOOLS array end
        if in_tools and stripped.startswith('];'):
            in_tools = False
            continue

        # Translate French tool lines
        if in_tools and is_french_tool_line(stripped):
            original = lines[i]
            lines[i] = translate_line(lines[i])
            if lines[i] != original:
                translated_count += 1

    with open(FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"  {translated_count} outils traduits")
    print("  Fichier mis a jour: en/index.html")

if __name__ == '__main__':
    main()
