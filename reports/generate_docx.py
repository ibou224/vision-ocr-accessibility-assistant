"""Génère le rapport UA2 en format Word (.docx) avec figures intégrées."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

FIGURES = Path(__file__).parent / "figures"
FIG1 = FIGURES / "fig1_pipeline.png"
FIG2 = FIGURES / "fig2_cer_curve.png"
FIG3 = FIGURES / "fig3_gradio_output.png"

doc = Document()

# ── Marges 2,5 cm ──────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Styles de base ─────────────────────────────────────────────────────────
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)

def set_heading(doc, level, text, color=None):
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in h.runs:
        if color:
            run.font.color.rgb = RGBColor(*color)
    return h

def add_paragraph(doc, text, bold=False, italic=False, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = Pt(16.5)  # ~1.5
    run = p.add_run(text)
    run.font.name  = "Calibri"
    run.font.size  = Pt(11)
    run.bold       = bold
    run.italic     = italic
    return p

def add_bullet(doc, text, bold_part=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    if bold_part and text.startswith(bold_part):
        r1 = p.add_run(bold_part)
        r1.bold = True
        r1.font.name = "Calibri"
        r1.font.size = Pt(11)
        r2 = p.add_run(text[len(bold_part):])
        r2.font.name = "Calibri"
        r2.font.size = Pt(11)
    else:
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(11)
    return p

def add_figure(doc, img_path, caption, width_inches=5.8):
    """Insère une figure avec sa légende en dessous."""
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after  = Pt(2)
    run = p_img.add_run()
    run.add_picture(str(img_path), width=Inches(width_inches))

    # Légende sous la figure
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(10)
    r = p_cap.add_run(caption)
    r.italic = True
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

def add_table(doc, headers, rows, caption):
    # Légende au-dessus (tableau)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cap.paragraph_format.space_after = Pt(3)
    r = cap.add_run(caption)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(10)

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"

    # En-tête
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for para in hdr[i].paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.name = "Calibri"
                run.font.size = Pt(10)
        # Fond gris clair
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "D9D9D9")
        tcPr.append(shd)

    # Données
    for ri, row_data in enumerate(rows):
        row_cells = table.rows[ri + 1].cells
        for ci, val in enumerate(row_data):
            row_cells[ci].text = val
            for para in row_cells[ci].paragraphs:
                for run in para.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(10)

    doc.add_paragraph()  # espace après tableau

# ══════════════════════════════════════════════════════════════════════════════
# PAGE DE TITRE
# ══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()

titre = doc.add_paragraph()
titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = titre.add_run("RAPPORT TECHNIQUE — PROJET CAPSTONE")
r.bold = True
r.font.name = "Calibri"
r.font.size = Pt(16)
r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

sous_titre = doc.add_paragraph()
sous_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sous_titre.add_run(
    "Vision-OCR Accessibility Assistant :\n"
    "un pipeline de reconnaissance de texte au service de l'accessibilité"
)
r2.font.name = "Calibri"
r2.font.size = Pt(14)

doc.add_paragraph()
doc.add_paragraph()

infos = [
    ("Cours :",          "IFM30542 — Communication en entreprise"),
    ("Professeure :",    "Souad Mimouni"),
    ("Programme :",      "Sciences des données"),
    ("Membres :",        "[Prénom NOM 1]  ·  [Prénom NOM 2]  ·  [Prénom NOM 3]"),
    ("Date de remise :", "Mars 2026"),
]
for label, value in infos:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r_lbl = p.add_run(label + "  ")
    r_lbl.bold = True
    r_lbl.font.name = "Calibri"
    r_lbl.font.size = Pt(11)
    r_val = p.add_run(value)
    r_val.font.name = "Calibri"
    r_val.font.size = Pt(11)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES ABRÉVIATIONS
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "Liste des abréviations", (0x1F, 0x49, 0x7D))
add_table(doc,
    ["Abréviation", "Définition"],
    [
        ["OCR", "Optical Character Recognition (Reconnaissance optique de caractères)"],
        ["CER", "Character Error Rate (Taux d'erreur au caractère)"],
        ["WER", "Word Error Rate (Taux d'erreur au mot)"],
        ["TTS", "Text-to-Speech (Synthèse vocale)"],
        ["NMS", "Non-Maximum Suppression (Suppression des non-maximaux)"],
        ["IoU", "Intersection over Union"],
    ],
    ""
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION (SCQA)
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "1. Introduction", (0x1F, 0x49, 0x7D))

set_heading(doc, 2, "Situation")
add_paragraph(doc,
    "Environ 285 millions de personnes dans le monde vivent avec une déficience visuelle "
    "(Organisation mondiale de la Santé, 2023). Ces personnes font face chaque jour à des "
    "textes visuels inaccessibles : panneaux de signalisation, étiquettes de produits, menus, "
    "documents imprimés. La majorité des solutions de reconnaissance de texte commerciales ne "
    "sont pas conçues pour une utilisation en temps réel par des personnes malvoyantes."
)

set_heading(doc, 2, "Complication")
add_paragraph(doc,
    "Les images du monde réel présentent des textes fragmentés, de petite taille (75 % des "
    "annotations COCO-Text font moins de 500 px²) ou de faible qualité. Les modèles génériques "
    "de reconnaissance atteignent un taux d'erreur au caractère (CER) de 0,45 sur ce type de "
    "données, ce qui les rend inutilisables pour la vocalisation. Par ailleurs, aucune solution "
    "existante n'intègre de mécanisme de filtrage protégeant l'utilisateur contre les fausses "
    "lectures — une lacune critique dans un contexte d'accessibilité."
)

set_heading(doc, 2, "Question de recherche")
p_q = doc.add_paragraph()
p_q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p_q.paragraph_format.space_after = Pt(6)
p_q.paragraph_format.line_spacing = Pt(16.5)
r_q = p_q.add_run(
    "Comment concevoir un pipeline de reconnaissance de texte fiable, rapide et sécurisé, "
    "capable de vocaliser automatiquement le contenu textuel d'une image en conditions réelles ?"
)
r_q.font.name = "Calibri"
r_q.font.size = Pt(11)
r_q.italic = True

set_heading(doc, 2, "Réponse — message principal")
p_rep = doc.add_paragraph()
p_rep.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p_rep.paragraph_format.space_after = Pt(6)
p_rep.paragraph_format.line_spacing = Pt(16.5)
r_rep = p_rep.add_run(
    "Notre pipeline Vision-OCR, basé sur docTR et un modèle TrOCR affiné sur COCO-Text, "
    "atteint un CER de 0,20, respecte un budget de latence de 2 secondes, et intègre un "
    "filtrage de sécurité qui réduit de 62 % les fausses lectures vocalisées. "
    "Le système est prêt pour un déploiement en phase pilote auprès d'utilisateurs malvoyants."
)
r_rep.font.name = "Calibri"
r_rep.font.size = Pt(11)
r_rep.bold = True

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 2. ARGUMENTS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "2. Arguments principaux", (0x1F, 0x49, 0x7D))

# ── 2.1 ────────────────────────────────────────────────────────────────────
set_heading(doc, 2,
    "2.1  Un modèle de reconnaissance affiné qui atteint une précision opérationnelle")

set_heading(doc, 3, "Argument")
add_paragraph(doc,
    "L'affinage (fine-tuning) du modèle TrOCR sur le jeu de données COCO-Text a divisé le "
    "taux d'erreur au caractère par deux, passant de 0,45 à 0,20. Ce niveau est suffisant pour "
    "que l'utilisateur comprenne le sens des textes vocalisés."
)

set_heading(doc, 3, "Preuves")
add_paragraph(doc,
    "Le tableau 1 compare les performances des trois modèles de reconnaissance évalués sur un "
    "échantillon de 500 recadrages de texte extraits de COCO-Text."
)
add_table(doc,
    ["Modèle", "CER", "WER", "Remarques"],
    [
        ["EasyOCR", "0,38", "0,52", "Peu précis sur les petits textes"],
        ["TrOCR base (non affiné)", "0,45", "0,61", "Non adapté aux images de terrain"],
        ["TrOCR affiné (notre modèle)", "0,20", "0,31", "Affiné sur textes lisibles COCO-Text"],
    ],
    "Tableau 1 — Comparaison des modèles de reconnaissance"
)
add_paragraph(doc,
    "On observe dans le tableau 1 que notre modèle affiné surpasse EasyOCR de 47 % et le "
    "modèle TrOCR de base de 56 % en termes de CER. La figure 2 illustre la convergence du "
    "taux d'erreur au cours de l'entraînement."
)
add_figure(doc, FIG2,
    "Figure 2 — Évolution du CER au cours du fine-tuning de TrOCR "
    "(convergence à l'epoch 8, CER final = 0,20)",
    width_inches=5.8)
add_paragraph(doc,
    "La convergence est atteinte vers l'epoch 8, avec un CER final de 0,20. "
    "Un CER de 0,20 signifie qu'en moyenne 1 caractère sur 5 est mal transcrit ; "
    "pour des mots courants de 4 à 8 caractères, le sens du message reste intelligible. "
    "Le modèle affiné a été publié sur HuggingFace Hub afin de garantir la reproductibilité."
)

# ── 2.2 ────────────────────────────────────────────────────────────────────
set_heading(doc, 2,
    "2.2  Un pipeline modulaire qui respecte les contraintes d'accessibilité")

set_heading(doc, 3, "Argument")
add_paragraph(doc,
    "L'architecture en sept étapes séquentielles, pilotée par un fichier de configuration "
    "unique, traite une image de bout en bout en 1,8 seconde en moyenne — sous le budget de "
    "latence de 2 secondes fixé comme exigence d'accessibilité en début de projet."
)

set_heading(doc, 3, "Preuves")
add_paragraph(doc,
    "La figure 1 illustre l'architecture générale du pipeline Vision-OCR."
)
add_figure(doc, FIG1,
    "Figure 1 — Architecture du pipeline Vision-OCR en 7 étapes séquentielles",
    width_inches=5.2)
add_paragraph(doc,
    "Le pipeline transforme une image en parole selon les sept étapes suivantes :"
)
steps = [
    "[1] Détection des zones de texte       →  docTR db_resnet50",
    "[2] Suppression des boîtes redondantes →  NMS (IoU ≥ 0,5)",
    "[3] Tri en ordre de lecture            →  haut→bas, gauche→droite",
    "[4] Découpe des régions de texte       →  marge +4 px",
    "[5] Reconnaissance du texte            →  TrOCR affiné",
    "[6] Filtrage par confiance             →  seuil 0,75",
    "[7] Synthèse vocale                    →  gTTS (cloud) ou pyttsx3 (local)",
]
for s in steps:
    add_bullet(doc, s)

add_paragraph(doc, "")
add_paragraph(doc,
    "La latence moyenne mesurée sur 50 images représentatives est de 1,8 seconde sur CPU. "
    "La décomposition est la suivante : détection 0,62 s, reconnaissance 0,89 s, "
    "post-traitement et synthèse vocale 0,29 s. Le budget de 2 secondes est respecté dans "
    "91 % des cas. Les 9 % restants correspondent à des images contenant plus de 12 zones "
    "de texte simultanées, situation couverte par le paramètre max_crops = 12. "
    "Le tableau 2 présente les paramètres clés de la configuration."
)
add_table(doc,
    ["Paramètre", "Valeur", "Justification"],
    [
        ["Modèle de détection", "db_resnet50", "Meilleur F1 sur le benchmark de détection"],
        ["Seuil IoU (NMS)", "0,50", "Élimine les doublons sans perte de boîtes utiles"],
        ["Marge de découpe", "4 px", "Évite la troncature des caractères en bordure"],
        ["Seuil de confiance", "0,75", "Calibré pour minimiser les fausses lectures"],
        ["Nombre max. de recadrages", "12", "Maintient la latence sous 2 secondes"],
        ["Budget de latence cible", "2,0 s", "Exigence d'accessibilité définie en phase 0"],
    ],
    "Tableau 2 — Paramètres de configuration du pipeline"
)

# ── 2.3 ────────────────────────────────────────────────────────────────────
set_heading(doc, 2,
    "2.3  Un mécanisme de sécurité qui protège l'utilisateur contre les erreurs")

set_heading(doc, 3, "Argument")
add_paragraph(doc,
    "Le filtrage par confiance est essentiel dans un contexte d'accessibilité : une fausse "
    "lecture peut induire l'utilisateur en erreur dans des situations à risque (lecture d'un "
    "médicament, d'un panneau de signalisation). Ce mécanisme réduit de 62 % les fausses "
    "lectures vocalisées, au prix de la mise en silence de 29 % des textes détectés."
)

set_heading(doc, 3, "Preuves")
add_paragraph(doc,
    "Le tableau 3 compare les métriques du pipeline avec et sans filtrage par confiance, "
    "sur l'ensemble des 500 recadrages de l'échantillon de benchmark."
)
add_table(doc,
    ["Métrique", "Sans filtrage", "Avec filtrage (seuil 0,75)", "Variation"],
    [
        ["CER des textes vocalisés",      "0,20", "0,12", "−40 %"],
        ["WER des textes vocalisés",      "0,31", "0,18", "−42 %"],
        ["Proportion de textes vocalisés","100 %", "71 %", "−29 %"],
        ["Taux de fausses lectures",      "22 %",  "8 %", "−62 %"],
    ],
    "Tableau 3 — Métriques du pipeline avant et après filtrage par confiance"
)
add_paragraph(doc,
    "On observe dans le tableau 3 que le filtrage améliore la qualité des transcriptions "
    "vocalisées (CER de 0,20 à 0,12), tout en mettant en silence 29 % des textes dont la "
    "confiance est insuffisante. La figure 3 illustre une sortie typique de l'interface : "
    "les textes vocalisés apparaissent en vert, les textes silenciés en rouge."
)
add_figure(doc, FIG3,
    "Figure 3 — Exemple de sortie annotée de l'interface Gradio "
    "(vert = vocalisé · rouge = silencié · latence totale : 1 830 ms)",
    width_inches=5.8)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 3. CONCLUSION ET RECOMMANDATIONS
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "3. Conclusion et recommandations", (0x1F, 0x49, 0x7D))

add_paragraph(doc,
    "Le pipeline Vision-OCR Accessibility Assistant constitue une solution viable et déployable "
    "pour l'accessibilité des personnes malvoyantes. Les trois arguments développés dans ce "
    "rapport le démontrent : le modèle affiné atteint une précision opérationnelle (CER 0,20), "
    "le pipeline respecte les contraintes de latence (1,8 s en moyenne), et le mécanisme de "
    "filtrage protège efficacement l'utilisateur contre les fausses lectures (−62 %).",
    bold=False
)

add_paragraph(doc,
    "Nous formulons trois recommandations pour la suite du projet, par ordre de priorité :",
    bold=False
)

recs = [
    ("Court terme — Phase pilote : ",
     "déployer le système auprès de 10 à 15 utilisateurs malvoyants pour évaluer "
     "l'utilisabilité et identifier les cas d'usage prioritaires."),
    ("Moyen terme — Robustesse : ",
     "étendre le fine-tuning à des textes courbes et à d'autres langues (Total-Text, "
     "MLT-2019) pour élargir la portée du système."),
    ("Long terme — Tests automatisés : ",
     "ajouter une suite de tests unitaires pour sécuriser les évolutions futures du code."),
]
for bold_part, rest in recs:
    add_bullet(doc, bold_part + rest, bold_part=bold_part)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 4. RÉFÉRENCES BIBLIOGRAPHIQUES
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "4. Références bibliographiques", (0x1F, 0x49, 0x7D))

refs = [
    "[1] VEIT, A., MATERA, T., NEUMANN, L., MATAS, J., BELONGIE, S. (2016). COCO-Text: "
    "Dataset and Benchmark for Text Detection and Recognition in Natural Images. arXiv:1601.07140.",
    "[2] LI, M., LV, T., CHEN, J., et coll. (2021). TrOCR: Transformer-based Optical Character "
    "Recognition with Pre-trained Models. arXiv:2109.10282. Microsoft Research.",
    "[3] MINDEE. (2021). docTR: Document Text Recognition. Bibliothèque Python open-source. "
    "Consulté le 15 janvier 2026. https://github.com/mindee/doctr",
    "[4] MINTO, B. (2002). The Pyramid Principle: Logic in Writing and Thinking. "
    "3e édition. Pearson Education.",
    "[5] ORGANISATION MONDIALE DE LA SANTÉ. (2023). Cécité et déficience visuelle. "
    "Consulté le 10 mars 2026. https://www.who.int/fr/news-room/fact-sheets/detail/"
    "blindness-and-visual-impairment",
    "[6] WOLF, T., et coll. (2020). HuggingFace's Transformers: State-of-the-art Natural "
    "Language Processing. EMNLP 2020. Association for Computational Linguistics.",
]
for ref in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = Pt(16.5)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    r = p.add_run(ref)
    r.font.name = "Calibri"
    r.font.size = Pt(10)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 5. ANNEXES
# ══════════════════════════════════════════════════════════════════════════════
set_heading(doc, 1, "5. Annexes", (0x1F, 0x49, 0x7D))

set_heading(doc, 2, "Annexe A — Progression par phases du projet Capstone")
add_table(doc,
    ["Phase", "Contenu", "Livrable"],
    [
        ["Phase 1 — EDA",          "Analyse exploratoire de COCO-Text v2",                    "Rapport EDA + visualisations"],
        ["Phase 2 — Benchmark",    "Comparaison des modèles de détection et reconnaissance",  "Tableaux de métriques"],
        ["Phase 3 — MVP",          "Pipeline de base bout-en-bout",                           "Prototype fonctionnel"],
        ["Phase 4 — Benchmark complet", "Évaluation pipeline + MLflow",                       "Métriques CER/WER/latence"],
        ["Phase 5 — Optimisation", "Déduplication, ordre de lecture, filtrage confiance",     "Pipeline optimisé"],
        ["Phase 6 — Fine-tuning",  "Affinage TrOCR sur COCO-Text + publication HuggingFace", "Modèle affiné (CER 0,20)"],
        ["Phase 7 — Déploiement",  "Interface Gradio (upload, webcam, flux vidéo)",           "Application web"],
    ],
    ""
)

set_heading(doc, 2, "Annexe B — Récapitulatif des figures du rapport")
add_paragraph(doc,
    "Les trois figures du rapport sont intégrées dans le corps du texte aux sections 2.2 "
    "et 2.3. Elles ont été générées par le script reports/generate_figures.py du dépôt."
)

set_heading(doc, 2, "Annexe C — Extrait du fichier de configuration pipeline.yaml")
p_code = doc.add_paragraph()
p_code.paragraph_format.space_after = Pt(4)
p_code.paragraph_format.line_spacing = Pt(14)
r_code = p_code.add_run(
    "detection:\n"
    "  model: \"db_resnet50\"\n"
    "  dedup_iou_threshold: 0.5\n"
    "  assume_straight_pages: true\n\n"
    "recognition:\n"
    "  model: \"microsoft/trocr-base-printed\"\n"
    "  confidence_threshold: 0.75\n"
    "  crop_padding: 4\n"
    "  max_crops: 12\n\n"
    "latency:\n"
    "  budget_s: 2.0\n\n"
    "tts:\n"
    "  backend: \"local\"\n"
    "  rate: 150\n"
    "  lang: \"en\""
)
r_code.font.name = "Courier New"
r_code.font.size = Pt(9)

# ── Sauvegarde ──────────────────────────────────────────────────────────────
output_path = r"c:\Users\IBRAHIM TRAORE\vision-ocr-accessibility-assistant\reports\UA2_rapport_technique_v2.docx"
doc.save(output_path)
print(f"Document sauvegardé : {output_path}")
