#!/usr/bin/env python3
"""
fix_en_translations.py
Finds and fixes residual French text in the English TOOLS array of en/index.html.

Strategy:
  1. For PARTIALLY-French tools (~31 tools): targeted word/phrase replacements
  2. For FULLY-French tools (~178 tools): comprehensive multi-pass translation
     using sentence patterns, verb conjugations, and structural transformations

Only operates within the TOOLS array section.
Does NOT modify:
  - pricing:"gratuit" / pricing:"payant" (used as CSS class names / JS logic)
  - URLs, tool IDs
  - HTML tags or attributes

Usage:
  python fix_en_translations.py          # Dry run (report only)
  python fix_en_translations.py --apply  # Apply changes
"""

import re
import sys
import os
import io

# Fix console encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "en", "index.html")
APPLY_MODE = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════════════════
#  COMPREHENSIVE FRENCH-TO-ENGLISH TRANSLATION DICTIONARY
# ═══════════════════════════════════════════════════════════════════════
# Applied in order: longer phrases first, then shorter words.

TRANSLATIONS = [
    # ── Long phrases (must come first) ──
    (r"Recherche technique avec reponses verifiees par la communaute", "Technical search with community-verified answers"),
    (r"Creez des chatbots IA personnalises entraines sur vos donnees", "Create custom AI chatbots trained on your data"),
    (r"Studio d'enregistrement podcast et video avec transcription IA", "Podcast and video recording studio with AI transcription"),
    (r"Creation de flowcharts, wireframes et mind maps assistee par IA", "AI-assisted creation of flowcharts, wireframes and mind maps"),
    (r"Enregistrement d'ecran avec resumes et chapitres IA automatics", "Screen recording with AI summaries and automatic chapters"),
    (r"Suite complete de creation visualle avec IA integree", "Complete visual creation suite with integrated AI"),
    (r"Transformez du text en diagrammes et visuals explicatifs par IA", "Transform text into AI-powered diagrams and explanatory visuals"),
    (r"Analyse de feedback user et research UX par IA", "AI-powered user feedback analysis and UX research"),
    (r"Transformez n'importe quel content en mind map interactif par IA", "Transform any content into an interactive AI mind map"),
    (r"Assistant IA all-in-one dans votre browser : chat, redaction, traduction", "All-in-one AI assistant in your browser: chat, writing, translation"),
    (r"Panneau lateral IA pour ChatGPT, Claude et Gemini dans votre browser", "AI sidebar for ChatGPT, Claude and Gemini in your browser"),
    (r"Le generateur video revolutionnaire d'OpenAI", "OpenAI's revolutionary video generator"),
    (r"Le générateur video révolutionnaire d'OpenAI", "OpenAI's revolutionary video generator"),
    (r"Generation video IA chinoise avec mouvement naturel", "Chinese AI video generation with natural movement"),
    (r"Génération video IA chinoise avec mouvement naturel", "Chinese AI video generation with natural movement"),
    (r"Generation video IA creative et accessible pour tous", "Creative and accessible AI video generation for everyone"),
    (r"Génération video IA créative et accessible pour tous", "Creative and accessible AI video generation for everyone"),
    (r"Animez des personnages avec des mouvements controlables", "Animate characters with controllable movements"),
    (r"Animez des personnages avec des mouvements contrôlables", "Animate characters with controllable movements"),
    (r"Transformez un lien produit en video publicitaire UGC", "Transform a product link into a UGC advertising video"),
    (r"Creation de videos de formation avec avatars IA multilingues", "Training video creation with multilingual AI avatars"),
    (r"Création de videos de formation avec avatars IA multilingues", "Training video creation with multilingual AI avatars"),
    (r"Decoupez vos longs contents video en shorts viraux par IA", "Cut your long video content into viral shorts with AI"),
    (r"Découpez vos longs contents video en shorts viraux par IA", "Cut your long video content into viral shorts with AI"),

    # ── Multi-word French phrases ──
    (r"Idéal pour", "Ideal for"),
    (r"Ideal pour", "Ideal for"),
    (r"Parfait pour", "Perfect for"),
    (r"Perfect for", "Perfect for"),
    (r"Gratuit pour", "Free to"),
    (r"à partir de", "starting from"),
    (r"À partir de", "Starting from"),
    (r"a partir de", "starting from"),
    (r"en temps réel", "in real-time"),
    (r"en temps reel", "in real-time"),
    (r"En temps réel", "In real-time"),
    (r"Jusqu'à", "Up to"),
    (r"jusqu'à", "up to"),
    (r"Grâce à", "Thanks to"),
    (r"grâce à", "thanks to"),
    (r"Grace à", "Thanks to"),
    (r"grace à", "thanks to"),
    (r"n'importe quel", "any"),
    (r"N'importe quel", "Any"),
    (r"n'importe quelle", "any"),
    (r"N'importe quelle", "Any"),
    (r"Tout-en-un", "All-in-one"),
    (r"tout-en-un", "all-in-one"),
    (r"Tout en un", "All-in-one"),
    (r"tout en un", "all-in-one"),
    (r"Pas de\b", "No"),
    (r"pas de\b", "no"),
    (r"Pas d'", "No "),
    (r"pas d'", "no "),
    (r"Mise en page", "Layout"),
    (r"mise en page", "layout"),
    (r"Base de données", "Database"),
    (r"base de données", "database"),
    (r"Base de donnees", "Database"),
    (r"base de donnees", "database"),
    (r"Moteur de recherche", "Search engine"),
    (r"moteur de recherche", "search engine"),
    (r"Intelligence artificielle", "Artificial intelligence"),
    (r"intelligence artificielle", "artificial intelligence"),
    (r"Apprentissage automatique", "Machine learning"),
    (r"apprentissage automatique", "machine learning"),
    (r"Réseaux sociaux", "Social media"),
    (r"réseaux sociaux", "social media"),
    (r"Reseaux sociaux", "Social media"),
    (r"reseaux sociaux", "social media"),
    (r"Sous-titres dynamiques", "Dynamic subtitles"),
    (r"sous-titres dynamiques", "dynamic subtitles"),
    (r"Sous-titres", "Subtitles"),
    (r"sous-titres", "subtitles"),
    (r"Sous-titre", "Subtitle"),
    (r"sous-titre", "subtitle"),
    (r"Captions animées", "Animated captions"),
    (r"captions animées", "animated captions"),
    (r"Prix élevé", "High price"),
    (r"prix élevé", "high price"),
    (r"Prix eleve", "High price"),
    (r"prix eleve", "high price"),
    (r"Multi-langues", "Multi-language"),
    (r"multi-langues", "multi-language"),
    (r"Multi-pistes", "Multi-track"),
    (r"multi-pistes", "multi-track"),
    (r"Multi-platforms", "Multi-platform"),
    (r"multi-platforms", "multi-platform"),
    (r"Multi-modeles", "Multi-model"),
    (r"multi-modeles", "multi-model"),
    (r"Multi-modèles", "Multi-model"),
    (r"multi-modèles", "multi-model"),
    (r"Multi-format", "Multi-format"),
    (r"Court-métrages", "Short films"),
    (r"court-métrages", "short films"),
    (r"Jeux vidéo", "Video games"),
    (r"jeux vidéo", "video games"),
    (r"Jeux-video", "Video games"),
    (r"jeux-video", "video games"),
    (r"Prise en main", "Getting started"),
    (r"prise en main", "getting started"),
    (r"Par mois", "Per month"),
    (r"par mois", "per month"),
    (r"Par user", "Per user"),
    (r"par user", "per user"),
    (r"D'anciens", "Former"),
    (r"d'anciens", "former"),
    (r"d'OpenAI", "by OpenAI"),
    (r"d'IA", "AI"),
    (r"l'IA", "AI"),
    (r"L'IA", "AI"),
    (r"l'tool", "the tool"),
    (r"L'tool", "The tool"),
    (r"l'interface", "the interface"),
    (r"L'interface", "The interface"),
    (r"l'assistant", "the assistant"),
    (r"L'assistant", "The assistant"),
    (r"l'analyse", "the analysis"),
    (r"L'analyse", "The analysis"),
    (r"l'intelligence", "the intelligence"),
    (r"L'intelligence", "The intelligence"),
    (r"l'information", "information"),
    (r"L'information", "Information"),
    (r"d'company", "corporate"),
    (r"d'entreprise", "corporate"),
    (r"d'écran", "screen"),
    (r"d'ecran", "screen"),
    (r"de la\b", "of"),
    (r"De la\b", "Of"),

    # ── Verbs (conjugated forms) ──
    (r"\bse spécialise\b", "specializes"),
    (r"\bSe spécialise\b", "Specializes"),
    (r"\bse specialise\b", "specializes"),
    (r"\bSe specialise\b", "Specializes"),
    (r"\bTransformez\b", "Transform"),
    (r"\btransformez\b", "transform"),
    (r"\btransforme\b", "transforms"),
    (r"\bTransforme\b", "Transforms"),
    (r"\bgénère\b", "generates"),
    (r"\bGénère\b", "Generates"),
    (r"\bgenere\b", "generates"),
    (r"\bGenere\b", "Generates"),
    (r"\bgénérer\b", "generate"),
    (r"\bGénérer\b", "Generate"),
    (r"\bgenerer\b", "generate"),
    (r"\bGenerer\b", "Generate"),
    (r"\bCréez\b", "Create"),
    (r"\bcréez\b", "create"),
    (r"\bCreez\b", "Create"),
    (r"\bcreez\b", "create"),
    (r"\boffre\b", "offers"),
    (r"\bOffre\b", "Offers"),
    (r"\butilise\b", "uses"),
    (r"\bUtilise\b", "Uses"),
    (r"\bajoute\b", "adds"),
    (r"\bAjoute\b", "Adds"),
    (r"\bintègre\b", "integrates"),
    (r"\bIntègre\b", "Integrates"),
    (r"\bintegre\b", "integrates"),
    (r"\bIntegre\b", "Integrates"),
    (r"\bpermet\b", "allows"),
    (r"\bPermet\b", "Allows"),
    (r"\bpermettant\b", "allowing"),
    (r"\bPermettant\b", "Allowing"),
    (r"\brend\b", "makes"),
    (r"\bRend\b", "Makes"),
    (r"\bexcelle\b", "excels"),
    (r"\bExcelle\b", "Excels"),
    (r"\brivalisent\b", "rival"),
    (r"\bRivalisent\b", "Rival"),
    (r"\bcentralise\b", "centralizes"),
    (r"\bCentralise\b", "Centralizes"),
    (r"\bidentifie\b", "identifies"),
    (r"\bIdentifie\b", "Identifies"),
    (r"\benrichit\b", "enriches"),
    (r"\bEnrichit\b", "Enriches"),
    (r"\brévèle\b", "reveals"),
    (r"\bRévèle\b", "Reveals"),
    (r"\bcollez\b", "paste"),
    (r"\bCollez\b", "Paste"),
    (r"\bobtenez\b", "get"),
    (r"\bObtenez\b", "Get"),
    (r"\banalyser\b", "analyze"),
    (r"\bAnalyser\b", "Analyze"),
    (r"\bstructurer\b", "structure"),
    (r"\bStructurer\b", "Structure"),
    (r"\bspécialise\b", "specializes"),
    (r"\bSpécialise\b", "Specializes"),
    (r"\bhierarchise\b", "organizes"),
    (r"\bhiérarchise\b", "organizes"),
    (r"\bimpressionne\b", "impresses"),
    (r"\bImpressionne\b", "Impresses"),
    (r"\bdébuter\b", "get started"),
    (r"\bdébutent\b", "get started"),
    (r"\bdébute\b", "gets started"),
    (r"\bResumez\b", "Summarize"),
    (r"\bresumez\b", "summarize"),
    (r"\btraduit\b", "translates"),
    (r"\bTraduisez\b", "Translate"),
    (r"\btraduisez\b", "translate"),
    (r"\bredigez\b", "write"),
    (r"\bRedigez\b", "Write"),
    (r"\brédigez\b", "write"),
    (r"\bRédigez\b", "Write"),
    (r"\bquitter\b", "leaving"),
    (r"\bdisent\b", "say"),
    (r"\bextrait\b", "extracts"),
    (r"\bExtrait\b", "Extracts"),

    # ── Nouns & specific terms ──
    (r"\bFonctionnalités\b", "Features"),
    (r"\bfonctionnalités\b", "features"),
    (r"\bAvantages\b", "Advantages"),
    (r"\bavantages\b", "advantages"),
    (r"\bInconvénients\b", "Disadvantages"),
    (r"\binconvénients\b", "disadvantages"),
    (r"\bDisponible\b", "Available"),
    (r"\bdisponible\b", "available"),
    (r"\bRecommandé\b", "Recommended"),
    (r"\brecommandé\b", "recommended"),
    (r"\boutils\b", "tools"),
    (r"\bOutils\b", "Tools"),
    (r"\boutil\b", "tool"),
    (r"\bOutil\b", "Tool"),
    (r"\bcréation\b", "creation"),
    (r"\bCréation\b", "Creation"),
    (r"\bgénération\b", "generation"),
    (r"\bGénération\b", "Generation"),
    (r"\bgeneration\b", "generation"),
    (r"\bautomatisation\b", "automation"),
    (r"\bAutomatisation\b", "Automation"),
    (r"\brecherche\b", "research"),
    (r"\bRecherche\b", "Research"),
    (r"\bcontenu\b", "content"),
    (r"\bContenu\b", "Content"),
    (r"\bcontenus\b", "content"),
    (r"\bContenus\b", "Content"),
    (r"\bcontents\b", "content"),
    (r"\bContents\b", "Content"),
    (r"\btexte\b", "text"),
    (r"\bTexte\b", "Text"),
    (r"\bvidéos\b", "videos"),
    (r"\bVidéos\b", "Videos"),
    (r"\bvidéo\b", "video"),
    (r"\bVidéo\b", "Video"),
    (r"\bmeilleure?s?\b", "best"),
    (r"\bMeilleure?s?\b", "Best"),
    (r"\bpublicité\b", "advertising"),
    (r"\bPublicité\b", "Advertising"),
    (r"\bpublicités\b", "ads"),
    (r"\bPublicités\b", "Ads"),
    (r"\bpublicitaire\b", "advertising"),
    (r"\bpublicitaires\b", "advertising"),
    (r"\bsécurité\b", "security"),
    (r"\bSécurité\b", "Security"),
    (r"\butilisateurs?\b", "users"),
    (r"\bUtilisateurs?\b", "Users"),
    (r"\bentreprise\b", "enterprise"),
    (r"\bEntreprise\b", "Enterprise"),
    (r"\bentreprises\b", "enterprises"),
    (r"\bEntreprises\b", "Enterprises"),
    (r"\bformation\b", "training"),
    (r"\bFormation\b", "Training"),
    (r"\banalyse\b", "analysis"),
    (r"\bAnalyse\b", "Analysis"),
    (r"\bréponses?\b", "responses"),
    (r"\bRéponses?\b", "Responses"),
    (r"\breponses?\b", "responses"),
    (r"\bReponses?\b", "Responses"),
    (r"\bdonnées\b", "data"),
    (r"\bDonnées\b", "Data"),
    (r"\bdonnees\b", "data"),
    (r"\bDonnees\b", "Data"),
    (r"\bpersonnalisée?s?\b", "personalized"),
    (r"\bPersonnalisée?s?\b", "Personalized"),
    (r"\bPersonnalisation\b", "Customization"),
    (r"\bpersonnalisation\b", "customization"),
    (r"\bintégrations?\b", "integrations"),
    (r"\bIntégrations?\b", "Integrations"),
    (r"\bintégration\b", "integration"),
    (r"\bIntégration\b", "Integration"),
    (r"\btraduction\b", "translation"),
    (r"\bTraduction\b", "Translation"),
    (r"\brédaction\b", "writing"),
    (r"\bRédaction\b", "Writing"),
    (r"\bredaction\b", "writing"),
    (r"\bRedaction\b", "Writing"),
    (r"\brésumés?\b", "summaries"),
    (r"\bRésumés?\b", "Summaries"),
    (r"\bresumes?\b", "summaries"),
    (r"\bResumes?\b", "Summaries"),
    (r"\bprésentations?\b", "presentations"),
    (r"\bPrésentations?\b", "Presentations"),
    (r"\bmodèles?\b", "models"),
    (r"\bModèles?\b", "Models"),
    (r"\bcommunauté\b", "community"),
    (r"\bCommunauté\b", "Community"),
    (r"\bcommunaute\b", "community"),
    (r"\bCommunaute\b", "Community"),
    (r"\bcommunautaires?\b", "community"),
    (r"\bCommunautaires?\b", "Community"),
    (r"\bqualité\b", "quality"),
    (r"\bQualité\b", "Quality"),
    (r"\bqualite\b", "quality"),
    (r"\bQualite\b", "Quality"),
    (r"\bpuissante?\b", "powerful"),
    (r"\bPuissante?\b", "Powerful"),
    (r"\brapides?\b", "fast"),
    (r"\bRapides?\b", "Fast"),
    (r"\bprofessionnelle?s?\b", "professional"),
    (r"\bProfessionnelle?s?\b", "Professional"),
    (r"\bcomplète\b", "complete"),
    (r"\bComplète\b", "Complete"),
    (r"\bcomplet\b", "complete"),
    (r"\bcréatifs?\b", "creative"),
    (r"\bCréatifs?\b", "Creative"),
    (r"\bcréative\b", "creative"),
    (r"\bcréateurs?\b", "creators"),
    (r"\bCréateurs?\b", "Creators"),
    (r"\binteractifs?\b", "interactive"),
    (r"\bInteractifs?\b", "Interactive"),
    (r"\bautomatiques?\b", "automatic"),
    (r"\bAutomatiques?\b", "Automatic"),
    (r"\bautomatics\b", "automatic"),
    (r"\bautomatiquement\b", "automatically"),
    (r"\bautomaticment\b", "automatically"),
    (r"\bréalistes?\b", "realistic"),
    (r"\bRéalistes?\b", "Realistic"),
    (r"\bvisuell?e?s?\b", "visual"),
    (r"\bVisuell?e?s?\b", "Visual"),
    (r"\bdiagrammes?\b", "diagrams"),
    (r"\bDiagrammes?\b", "Diagrams"),
    (r"\bschémas?\b", "schemas"),
    (r"\bSchémas?\b", "Schemas"),
    (r"\bschemas?\b", "schemas"),
    (r"\bexplicatifs?\b", "explanatory"),
    (r"\bExplicatifs?\b", "Explanatory"),
    (r"\binfographies?\b", "infographics"),
    (r"\bInfographies?\b", "Infographics"),
    (r"\benregistrement\b", "recording"),
    (r"\bEnregistrement\b", "Recording"),
    (r"\blangues?\b", "languages"),
    (r"\bLangues?\b", "Languages"),
    (r"\bmouvements?\b", "movements"),
    (r"\bMouvements?\b", "Movements"),
    (r"\bpersonnages?\b", "characters"),
    (r"\bPersonnages?\b", "Characters"),
    (r"\bdécoupe\b", "cutting"),
    (r"\bDécoupe\b", "Cutting"),
    (r"\bdécoupage\b", "cutting"),
    (r"\bDécoupage\b", "Cutting"),
    (r"\bdécoupeur\b", "cutter"),
    (r"\bDécoupeur\b", "Cutter"),
    (r"\bviralité\b", "virality"),
    (r"\bViralité\b", "Virality"),
    (r"\brésultats?\b", "results"),
    (r"\bRésultats?\b", "Results"),
    (r"\bresultats?\b", "results"),
    (r"\bResultats?\b", "Results"),
    (r"\bsuppression\b", "removal"),
    (r"\bSuppression\b", "Removal"),
    (r"\bcaméra\b", "camera"),
    (r"\bCaméra\b", "Camera"),
    (r"\bstockage\b", "storage"),
    (r"\bStockage\b", "Storage"),
    (r"\bcohérence\b", "coherence"),
    (r"\bCohérence\b", "Coherence"),
    (r"\bcompréhension\b", "understanding"),
    (r"\bCompréhension\b", "Understanding"),
    (r"\bphysique\b", "physics"),
    (r"\bPhysique\b", "Physics"),
    (r"\bexceptionnelle?\b", "exceptional"),
    (r"\bExceptionnelle?\b", "Exceptional"),
    (r"\btemporelle\b", "temporal"),
    (r"\bséquences?\b", "sequences"),
    (r"\bSéquences?\b", "Sequences"),
    (r"\bfluidité\b", "fluidity"),
    (r"\bFluidity\b", "Fluidity"),
    (r"\bfluides?\b", "fluid"),
    (r"\bcensure\b", "censorship"),
    (r"\bCensure\b", "Censorship"),
    (r"\bculturelle\b", "cultural"),
    (r"\babordable\b", "affordable"),
    (r"\bAbordable\b", "Affordable"),
    (r"\bfondé\b", "founded"),
    (r"\bFondé\b", "Founded"),
    (r"\bchercheurs\b", "researchers"),
    (r"\bChercheurs\b", "Researchers"),
    (r"\bdéployé\b", "deployed"),
    (r"\bDéployé\b", "Deployed"),
    (r"\bwebinaires?\b", "webinars"),
    (r"\bWebinaires?\b", "Webinars"),
    (r"\bextraits?\b", "excerpts"),
    (r"\bExtraits?\b", "Excerpts"),
    (r"\bdurée\b", "duration"),
    (r"\bDurée\b", "Duration"),
    (r"\blimitée?s?\b", "limited"),
    (r"\bLimitée?s?\b", "Limited"),
    (r"\blimités\b", "limited"),
    (r"\blimite\b", "limited"),
    (r"\bLimite\b", "Limited"),
    (r"\blimites\b", "limits"),
    (r"\bLimites\b", "Limits"),
    (r"\bélégante?\b", "elegant"),
    (r"\belegante?\b", "elegant"),
    (r"\bimpressionnante?s?\b", "impressive"),
    (r"\bImpressionnante?s?\b", "Impressive"),
    (r"\bbluffant\b", "stunning"),
    (r"\bBluffant\b", "Stunning"),
    (r"\bgénéreux\b", "generous"),
    (r"\bGénéreux\b", "Generous"),
    (r"\bgenereux\b", "generous"),
    (r"\bincluse?\b", "included"),
    (r"\bIncluse?\b", "Included"),
    (r"\bpratique\b", "practical"),
    (r"\bPratique\b", "Practical"),
    (r"\butile\b", "useful"),
    (r"\bUtile\b", "Useful"),
    (r"\bréférence\b", "reference"),
    (r"\bRéférence\b", "Reference"),
    (r"\bcroissant\b", "increasing"),
    (r"\bCroissant\b", "Increasing"),
    (r"\bpanneau\b", "panel"),
    (r"\bPanneau\b", "Panel"),
    (r"\blatérale?\b", "side"),
    (r"\bLatérale?\b", "Side"),
    (r"\blaterale?\b", "side"),
    (r"\bLaterale?\b", "Side"),
    (r"\btoujours\b", "always"),
    (r"\bportée?\b", "scope"),
    (r"\bclic\b", "click"),
    (r"\bchaque\b", "each"),
    (r"\bChaque\b", "Each"),
    (r"\buniversel\b", "universal"),
    (r"\bUniversel\b", "Universal"),
    (r"\btransformateur\b", "transformer"),
    (r"\bmentale\b", "mental"),
    (r"\bcarte\b", "map"),
    (r"\bCarte\b", "Map"),
    (r"\bvisuallement\b", "visually"),
    (r"\bapprentissage\b", "learning"),
    (r"\bApprentissage\b", "Learning"),
    (r"\bthématisation\b", "thematization"),
    (r"\bcentralisation\b", "centralization"),
    (r"\bspécialisée?\b", "specialized"),
    (r"\bSpécialisée?\b", "Specialized"),
    (r"\bchapitres?\b", "chapters"),
    (r"\bChapitres?\b", "Chapters"),
    (r"\bsilences?\b", "silences"),
    (r"\basynchrone\b", "asynchronous"),
    (r"\bAsynchrone\b", "Asynchronous"),
    (r"\bconfiance\b", "trust"),
    (r"\bConfiance\b", "Trust"),
    (r"\bstandard\b", "standard"),
    (r"\bStandard\b", "Standard"),
    (r"\bdatée?\b", "dated"),
    (r"\bmassive?\b", "massive"),
    (r"\bMassive?\b", "Massive"),
    (r"\bvérifiée?s?\b", "verified"),
    (r"\bVérifiée?s?\b", "Verified"),
    (r"\bverifiee?s?\b", "verified"),
    (r"\bVerifiee?s?\b", "Verified"),
    (r"\btechniques?\b", "technical"),
    (r"\bTechniques?\b", "Technical"),
    (r"\bchinoise?\b", "Chinese"),
    (r"\bChinoise?\b", "Chinese"),
    (r"\bchinois\b", "Chinese"),
    (r"\bChinois\b", "Chinese"),
    (r"\bnaturel\b", "natural"),
    (r"\bNaturel\b", "Natural"),
    (r"\bnaturelle?s?\b", "natural"),
    (r"\bNaturelle?s?\b", "Natural"),
    (r"\bhumains?\b", "human"),
    (r"\bHumains?\b", "Human"),
    (r"\bcontrôle?\b", "control"),
    (r"\bContrôle?\b", "Control"),
    (r"\bcontrôlable?s?\b", "controllable"),
    (r"\bvariés?\b", "varied"),
    (r"\bVariés?\b", "Varied"),
    (r"\bvariées?\b", "varied"),
    (r"\bvariable\b", "variable"),
    (r"\bVariable\b", "Variable"),
    (r"\boptimisée?s?\b", "optimized"),
    (r"\bOptimisée?s?\b", "Optimized"),
    (r"\banimée?s?\b", "animated"),
    (r"\bAnimée?s?\b", "Animated"),
    (r"\bartificiels?\b", "artificial"),
    (r"\bArtificiels?\b", "Artificial"),
    (r"\bartificielle?s?\b", "artificial"),
    (r"\bArtificielle?s?\b", "Artificial"),
    (r"\bgénérique?s?\b", "generic"),
    (r"\bGénérique?s?\b", "Generic"),
    (r"\bsélection\b", "selection"),
    (r"\bSélection\b", "Selection"),
    (r"\baléatoire\b", "random"),
    (r"\bAléatoire\b", "Random"),
    (r"\bédition\b", "editing"),
    (r"\bÉdition\b", "Editing"),
    (r"\bedition\b", "editing"),
    (r"\bédition avancée\b", "advanced editing"),
    (r"\bédition limitée\b", "limited editing"),
    (r"\brésolution\b", "resolution"),
    (r"\bRésolution\b", "Resolution"),
    (r"\bseconde?s?\b", "seconds"),
    (r"\bSeconde?s?\b", "Seconds"),
    (r"\bminutes?\b", "minutes"),
    (r"\bMinutes?\b", "Minutes"),
    (r"\bnouveaux?\b", "new"),
    (r"\bNouveaux?\b", "New"),
    (r"\bnouvelle?s?\b", "new"),
    (r"\bNouvelle?s?\b", "New"),
    (r"\bproduit\b", "product"),
    (r"\bProduit\b", "Product"),
    (r"\bproduits\b", "products"),
    (r"\bProduits\b", "Products"),
    (r"\bmachine\b", "machine"),
    (r"\baccès\b", "access"),
    (r"\bAccès\b", "Access"),
    (r"\bacces\b", "access"),
    (r"\bAcces\b", "Access"),
    (r"\bprécédent\b", "precedent"),
    (r"\bencore\b", "still"),
    (r"\bEncore\b", "Still"),
    (r"\bmalin\b", "clever"),
    (r"\bMalin\b", "Clever"),
    (r"\bfun\b", "fun"),
    (r"\bviral\b", "viral"),
    (r"\bViral\b", "Viral"),
    (r"\bviraux\b", "viral"),
    (r"\bViraux\b", "Viral"),
    (r"\bvirale\b", "viral"),
    (r"\bgénérateur\b", "generator"),
    (r"\bGénérateur\b", "Generator"),
    (r"\bgenerateur\b", "generator"),
    (r"\bGenerateur\b", "Generator"),
    (r"\bsituation\b", "situation"),
    (r"\brévolutionnaire\b", "revolutionary"),
    (r"\bRévolutionnaire\b", "Revolutionary"),
    (r"\brevolutionnaire\b", "revolutionary"),
    (r"\bRevolutionnaire\b", "Revolutionary"),
    (r"\bprofonde?\b", "deep"),
    (r"\bProfonde?\b", "Deep"),
    (r"\btemps\b", "time"),
    (r"\bTemps\b", "Time"),
    (r"\blong\b", "long"),
    (r"\bLong\b", "Long"),
    (r"\bstrict\b", "strict"),
    (r"\bStrict\b", "Strict"),
    (r"\bpolicy\b", "policy"),
    (r"\bscripts?\b", "scripts"),
    (r"\bformats?\b", "formats"),
    (r"\bstyles?\b", "styles"),
    (r"\bscènes?\b", "scenes"),
    (r"\bGratuit\b", "Free"),
    (r"\bgratuit\b", "free"),
    (r"\bGratuite\b", "Free"),
    (r"\bgratuite\b", "free"),
    (r"\bmois\b", "month"),
    (r"\bMois\b", "Month"),
    (r"\breq\b", "req"),
    (r"\bmessages\b", "messages"),
    (r"\bvotre\b", "your"),
    (r"\bVotre\b", "Your"),
    (r"\bvos\b", "your"),
    (r"\bVos\b", "Your"),

    # ── Articles, prepositions, conjunctions (applied last) ──
    (r"\btrès\b", "very"),
    (r"\bTrès\b", "Very"),
    (r"\bmais\b", "but"),
    (r"\bMais\b", "But"),
    (r"\baussi\b", "also"),
    (r"\bAussi\b", "Also"),
    (r"\bsans\b", "without"),
    (r"\bSans\b", "Without"),
    (r"\bentre\b", "between"),
    (r"\bEntre\b", "Between"),
    (r"\bcomme\b", "like"),
    (r"\bComme\b", "Like"),
    (r"\bcette\b", "this"),
    (r"\bCette\b", "This"),
    (r"\bces\b", "these"),
    (r"\bCes\b", "These"),
    (r"\bpour\b", "for"),
    (r"\bPour\b", "For"),
    (r"\bavec\b", "with"),
    (r"\bAvec\b", "With"),
    (r"\bdans\b", "in"),
    (r"\bDans\b", "In"),
    (r"\bplus\b", "more"),
    (r"\bPlus\b", "More"),
    (r"\bsur\b", "on"),
    (r"\bSur\b", "On"),
    (r"\bpar\b", "by"),
    (r"\bPar\b", "By"),
    (r"\bdes\b", "the"),
    (r"\bDes\b", "The"),
    (r"\bles\b", "the"),
    (r"\bLes\b", "The"),
    (r"\bune\b", "a"),
    (r"\bUne\b", "A"),
    (r"\best\b", "is"),
    (r"\bEst\b", "Is"),
    (r"\bsont\b", "are"),
    (r"\bSont\b", "Are"),
    (r"\bqui\b", "that"),
    (r"\bQui\b", "That"),
    (r"\bsur\b", "on"),
    (r"\bpeut\b", "can"),
    (r"\bPeut\b", "Can"),
    (r"\bou\b", "or"),
    (r"\bOu\b", "Or"),
    (r" et ", " and "),
    (r"\bdu\b", "of the"),
    (r"\bDu\b", "Of the"),
    (r"\bau\b", "to the"),
    (r"\bAu\b", "To the"),
    (r"\baux\b", "to the"),
    (r"\bAux\b", "To the"),
    (r"\bun\b", "a"),
    (r"\bUn\b", "A"),
    (r"\bce\b", "this"),
    (r"\bCe\b", "This"),
    (r"\ben\b", "in"),
    (r"\bEn\b", "In"),
    (r"\bà\b", "to"),
    (r"\bÀ\b", "To"),
    (r"\bde\b", "of"),
    (r"\bDe\b", "Of"),
    (r"\bla\b", "the"),
    (r"\bLa\b", "The"),
    (r"\ble\b", "the"),
    (r"\bLe\b", "The"),
    (r"\bil\b", "it"),
    (r"\bIl\b", "It"),
]

# Tags that should be translated
TAG_TRANSLATIONS = {
    "communaute": "community",
    "verifie": "verified",
    "technique": "technical",
    "personnages": "characters",
    "créatif": "creative",
    "réaliste": "realistic",
    "chinois": "chinese",
    "enregistrement": "recording",
    "formation": "training",
    "publicité": "advertising",
    "viralité": "virality",
    "découpage": "cutting",
    "diagrammes": "diagrams",
    "explication": "explanation",
    "asynchrone": "async",
    "ecran": "screen",
    "resumes": "summaries",
    "sidebar": "sidebar",
    "donnees": "data",
    "image-à-3d": "image-to-3d",
    "objets": "objects",
    "jeux-video": "game",
    "hybride": "hybrid",
    "studio": "studio",
    "mémoire": "memory",
    "apprentissage": "learning",
    "visualisation": "visualization",
    "multi-modeles": "multi-model",
    "multi-modèles": "multi-model",
    "shorts": "shorts",
    "mouvement": "movement",
    "animation": "animation",
    "company": "enterprise",
    "Q&A": "Q&A",
}

# pricingNote patterns
PRICING_NOTE_REPLACEMENTS = [
    (r"Gratuit \(", "Free ("),
    (r"Gratuit$", "Free"),
    (r"Gratuit ", "Free "),
    (r"Complètement gratuit", "Completely free"),
    (r"Completement gratuit", "Completely free"),
]


def compute_french_ratio(text):
    """Compute ratio of French indicator words in text."""
    french_pats = [
        r'\b(le|la|les|des|du|un|une|ce|cette|ces|cet)\b',
        r'\b(est|sont|ont|fait|peut|être|avoir|etre)\b',
        r'\b(pour|avec|dans|sur|par|entre|sans|sous)\b',
        r'\b(qui|que|dont|où)\b',
        r'[àâäéèêëîïôùûüç]',
        r'\b(très|aussi|mais|plus|moins|bien|encore|toujours)\b',
    ]
    words = len(text.split())
    if words == 0:
        return 0
    score = 0
    for pat in french_pats:
        score += len(re.findall(pat, text, re.IGNORECASE))
    return score / words


def extract_tools_section(html):
    """Extract the TOOLS array section boundaries."""
    start_match = re.search(r'const TOOLS = \[', html)
    if not start_match:
        print("ERROR: Could not find 'const TOOLS = [' in the file.")
        sys.exit(1)

    start_pos = start_match.start()
    bracket_depth = 0
    in_string = False
    escape_next = False

    for i in range(start_match.end(), len(html)):
        ch = html[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '[':
            bracket_depth += 1
        elif ch == ']':
            if bracket_depth == 0:
                end_pos = i + 1
                break
            bracket_depth -= 1

    if end_pos < len(html) and html[end_pos] == ';':
        end_pos += 1

    return start_pos, end_pos, html[start_pos:end_pos]


def apply_translations(text, is_french_heavy):
    """Apply French-to-English translations to a text string.

    For French-heavy text: apply ALL translations including articles/prepositions.
    For partially-French text: only apply noun/verb/phrase translations (not risky small words).
    """
    changes = []
    risky_patterns = set()

    if not is_french_heavy:
        # Build set of patterns that are "risky" (small common words)
        risky_words = {
            "et", "ou", "un", "une", "est", "des", "les", "sur", "par",
            "ce", "la", "le", "du", "au", "aux", "en", "à", "de", "a",
            "plus", "qui", "peut", "il", "dans", "pour", "avec", "mais",
            "aussi", "sans", "entre", "comme", "cette", "ces", "ou",
            "sont", "vos", "votre", "on"
        }

    for pattern, replacement in TRANSLATIONS:
        # Check if this is a risky small-word replacement
        if not is_french_heavy:
            clean_pat = re.sub(r'\\b|[\(\)\?\[\]\+\*]', '', pattern).strip().lower()
            if clean_pat in risky_words:
                continue

        try:
            new_text = re.sub(pattern, replacement, text)
        except re.error:
            continue

        if new_text != text:
            changes.append(f"{pattern} -> {replacement}")
            text = new_text

    return text, changes


def process_tool_line(line):
    """Process a single tool line, translating French text fields."""
    if not line.strip().startswith('{id:"'):
        return line, 0, []

    # Extract tool metadata
    id_match = re.search(r'id:"([^"]*)"', line)
    name_match = re.search(r'name:"([^"]*)"', line)
    tool_id = id_match.group(1) if id_match else "unknown"
    tool_name = name_match.group(1) if name_match else "unknown"

    # Determine if this tool is heavily French
    text_fields = []
    for key in ['tagline', 'description', 'verdict', 'pricingNote']:
        m = re.search(rf'{key}:"([^"]*)"', line)
        if m:
            text_fields.append(m.group(1))
    combined_text = ' '.join(text_fields)
    french_ratio = compute_french_ratio(combined_text)
    is_french_heavy = french_ratio > 0.10

    original_line = line
    all_changes = []

    # Fields to translate (simple key:"value" pairs)
    translatable_keys = ['tagline', 'description', 'verdict', 'pricingNote']

    for key in translatable_keys:
        pattern = rf'({key}:")([^"]*)(")'
        match = re.search(pattern, line)
        if match:
            old_val = match.group(2)

            # For pricingNote, apply specific pricing translations first
            if key == 'pricingNote':
                new_val = old_val
                for ppat, prep in PRICING_NOTE_REPLACEMENTS:
                    new_val = re.sub(ppat, prep, new_val)
                if new_val != old_val:
                    all_changes.append(f"pricingNote: '{old_val[:50]}' -> '{new_val[:50]}'")
                    line = line[:match.start(2)] + new_val + line[match.end(2):]
                    old_val = new_val  # continue with updated value

            new_val, changes = apply_translations(old_val, is_french_heavy)
            if changes:
                all_changes.extend([f"{key}: {c}" for c in changes[:5]])  # limit log
                line = re.sub(pattern, rf'\g<1>{re.escape(new_val)}\3', line, count=1)
                # Simpler replacement to avoid regex escape issues:
                line = original_line  # reset and do it properly
                break  # need to restart

    # Better approach: process all fields in the line by finding and replacing each one
    new_line = original_line
    all_changes = []

    for key in translatable_keys:
        match = re.search(rf'{key}:"([^"]*)"', new_line)
        if match:
            old_val = match.group(1)
            new_val = old_val

            # For pricingNote, apply pricing-specific fixes first
            if key == 'pricingNote':
                for ppat, prep in PRICING_NOTE_REPLACEMENTS:
                    new_val = re.sub(ppat, prep, new_val)

            new_val, changes = apply_translations(new_val, is_french_heavy)

            if new_val != old_val:
                all_changes.extend([f"{key}: {c}" for c in changes[:3]])
                new_line = new_line[:match.start(1)] + new_val + new_line[match.end(1):]

    # Process array fields: features, useCases, pros, cons
    array_keys = ['features', 'useCases', 'pros', 'cons']
    for akey in array_keys:
        arr_match = re.search(rf'{akey}:\[([^\]]*)\]', new_line)
        if arr_match:
            arr_content = arr_match.group(1)
            new_arr_content = arr_content

            def translate_array_item(m):
                val = m.group(1)
                new_val, _ = apply_translations(val, is_french_heavy)
                return f'"{new_val}"'

            new_arr_content = re.sub(r'"([^"]*)"', translate_array_item, arr_content)
            if new_arr_content != arr_content:
                all_changes.append(f"{akey}: array items translated")
                new_line = new_line[:arr_match.start(1)] + new_arr_content + new_line[arr_match.end(1):]

    # Process tags array: replace known French tags
    tags_match = re.search(r'tags:\[([^\]]*)\]', new_line)
    if tags_match:
        tags_content = tags_match.group(1)
        new_tags_content = tags_content
        for fr_tag, en_tag in TAG_TRANSLATIONS.items():
            old_tag = f'"{fr_tag}"'
            new_tag = f'"{en_tag}"'
            if old_tag in new_tags_content:
                new_tags_content = new_tags_content.replace(old_tag, new_tag)
                all_changes.append(f"tag: {fr_tag} -> {en_tag}")
        if new_tags_content != tags_content:
            new_line = new_line[:tags_match.start(1)] + new_tags_content + new_line[tags_match.end(1):]

    change_count = len(all_changes)
    return new_line, change_count, all_changes


def main():
    print("=" * 72)
    print("  FIX ENGLISH TRANSLATIONS - French Residual Finder & Fixer")
    print("=" * 72)
    print(f"  Input:  {INPUT_FILE}")
    print(f"  Mode:   {'APPLY (writing changes)' if APPLY_MODE else 'DRY RUN (report only)'}")
    print("=" * 72)
    print()

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File not found: {INPUT_FILE}")
        sys.exit(1)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"File size: {len(html):,} characters")

    start_pos, end_pos, tools_text = extract_tools_section(html)
    print(f"TOOLS section: chars {start_pos:,} to {end_pos:,} ({end_pos - start_pos:,} chars)")

    tool_count = tools_text.count('{id:"')
    print(f"Tools found: {tool_count}")
    print()

    # Process line by line
    lines = tools_text.split('\n')
    new_lines = []
    total_replacements = 0
    tools_changed = 0
    change_details = []

    for line in lines:
        new_line, count, changes = process_tool_line(line)
        new_lines.append(new_line)
        if count > 0:
            tools_changed += 1
            total_replacements += count
            id_m = re.search(r'id:"([^"]*)"', line)
            name_m = re.search(r'name:"([^"]*)"', line)
            change_details.append({
                'id': id_m.group(1) if id_m else '?',
                'name': name_m.group(1) if name_m else '?',
                'count': count,
                'changes': changes,
                'original': line,
                'new': new_line,
            })

    new_tools_text = '\n'.join(new_lines)

    # Report
    print("=" * 72)
    print("  RESULTS")
    print("=" * 72)
    print(f"  Tools with French residuals found & fixed: {tools_changed} / {tool_count}")
    print(f"  Total replacements made:                   {total_replacements}")
    print()

    # Show top 5 most-changed tools with before/after
    if change_details:
        sorted_changes = sorted(change_details, key=lambda x: x['count'], reverse=True)
        sample_count = min(5, len(sorted_changes))

        print(f"  Sample before/after ({sample_count} most-changed tools):")
        print("-" * 72)

        for i, tc in enumerate(sorted_changes[:sample_count]):
            print(f"\n  [{i+1}] {tc['name']} (id: {tc['id']}) -- {tc['count']} replacements")

            for key in ['tagline', 'description', 'verdict']:
                orig_m = re.search(rf'{key}:"([^"]*)"', tc['original'])
                new_m = re.search(rf'{key}:"([^"]*)"', tc['new'])
                if orig_m and new_m and orig_m.group(1) != new_m.group(1):
                    print(f"      {key} BEFORE: {orig_m.group(1)[:120]}")
                    print(f"      {key} AFTER:  {new_m.group(1)[:120]}")

        print()
        print("-" * 72)
        print(f"\n  All {tools_changed} changed tools:")
        for tc in sorted_changes:
            print(f"    - {tc['name']:35s} ({tc['id']:25s}): {tc['count']:3d} replacements")

    # Verify no pricing field values were changed
    orig_gratuit_count = tools_text.count('pricing:"gratuit"')
    new_gratuit_count = new_tools_text.count('pricing:"gratuit"')
    orig_payant_count = tools_text.count('pricing:"payant"')
    new_payant_count = new_tools_text.count('pricing:"payant"')

    print(f"\n  Safety check - pricing field values preserved:")
    print(f"    pricing:\"gratuit\" : {orig_gratuit_count} -> {new_gratuit_count} {'OK' if orig_gratuit_count == new_gratuit_count else 'MISMATCH!'}")
    print(f"    pricing:\"payant\"  : {orig_payant_count} -> {new_payant_count} {'OK' if orig_payant_count == new_payant_count else 'MISMATCH!'}")

    if APPLY_MODE:
        print()
        print("=" * 72)
        print("  APPLYING CHANGES...")
        print("=" * 72)

        new_html = html[:start_pos] + new_tools_text + html[end_pos:]

        backup_path = INPUT_FILE + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Backup saved to: {backup_path}")

        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"  Changes written to: {INPUT_FILE}")
        print(f"  File size: {len(new_html):,} characters (was {len(html):,})")
        print()
        print("  DONE! Changes applied successfully.")
    else:
        print()
        print("  This was a DRY RUN. To apply changes, run:")
        print(f"    python fix_en_translations.py --apply")

    print()


if __name__ == '__main__':
    main()
