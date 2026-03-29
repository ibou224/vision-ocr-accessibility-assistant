# Rapport technique — Projet Capstone
## Vision-OCR Accessibility Assistant : un pipeline de reconnaissance de texte au service de l'accessibilité

---

**Cours :** IFM30542 — Communication en entreprise
**Professeure :** Souad Mimouni
**Programme :** Sciences des données
**Membres de l'équipe :** [Prénom NOM 1] · [Prénom NOM 2] · [Prénom NOM 3]
**Date de remise :** Mars 2026

---

## Table des matières

1. Introduction
2. Arguments principaux
   - 2.1 Un modèle de reconnaissance affiné qui atteint une précision opérationnelle
   - 2.2 Un pipeline modulaire qui respecte les contraintes d'accessibilité
   - 2.3 Un mécanisme de sécurité qui protège l'utilisateur contre les erreurs
3. Conclusion et recommandations
4. Références bibliographiques
5. Annexes

---

## Liste des tableaux

| Tableau | Titre |
|---------|-------|
| Tableau 1 | Comparaison des modèles de reconnaissance |
| Tableau 2 | Métriques du pipeline avant et après filtrage par confiance |
| Tableau 3 | Paramètres de configuration du pipeline |

## Liste des figures

| Figure | Titre |
|--------|-------|
| Figure 1 | Architecture du pipeline Vision-OCR |
| Figure 2 | Évolution du taux d'erreur au cours du fine-tuning |
| Figure 3 | Exemple de sortie annotée de l'interface Gradio |

## Liste des abréviations

| Abréviation | Définition |
|-------------|------------|
| OCR | Optical Character Recognition (Reconnaissance optique de caractères) |
| CER | Character Error Rate (Taux d'erreur au caractère) |
| TTS | Text-to-Speech (Synthèse vocale) |
| IoU | Intersection over Union |
| NMS | Non-Maximum Suppression |

---

## 1. Introduction

### Situation

Environ 285 millions de personnes dans le monde vivent avec une déficience visuelle (Organisation mondiale de la Santé, 2023). Ces personnes font face chaque jour à des textes visuels inaccessibles : panneaux, étiquettes, menus, documents imprimés. La majorité des solutions OCR commerciales ne sont pas conçues pour une utilisation en temps réel par des personnes malvoyantes.

### Complication

Les images du monde réel présentent des textes fragmentés, de petite taille (75 % des annotations COCO-Text font moins de 500 px²) ou de faible qualité. Les modèles génériques de reconnaissance de texte atteignent un taux d'erreur au caractère (CER) de 0,45 sur ce type de données, ce qui les rend inutilisables pour la vocalisation. Par ailleurs, aucune solution existante n'intègre de mécanisme de filtrage qui protège l'utilisateur contre les fausses lectures.

### Question

Comment concevoir un pipeline de reconnaissance de texte fiable, rapide et sécurisé, capable de vocaliser automatiquement le contenu textuel d'une image en conditions réelles ?

### Réponse — message principal

**Notre pipeline Vision-OCR, basé sur docTR et un modèle TrOCR affiné sur COCO-Text, atteint un CER de 0,20, respecte un budget de latence de 2 secondes, et intègre un filtrage de sécurité qui réduit de 62 % les fausses lectures vocalisées. Le système est prêt pour un déploiement en phase pilote auprès d'utilisateurs malvoyants.**

---

## 2. Arguments principaux

### 2.1 Un modèle de reconnaissance affiné qui atteint une précision opérationnelle

#### Argument

L'affinage (fine-tuning) du modèle TrOCR sur le jeu de données COCO-Text a divisé le taux d'erreur au caractère par deux, passant de 0,45 à 0,20 — un niveau suffisant pour que l'utilisateur comprenne le sens des textes vocalisés.

#### Preuves

Le tableau 1 compare les performances des trois modèles de reconnaissance évalués sur un échantillon de 500 recadrages de texte extraits de COCO-Text.

**Tableau 1 — Comparaison des modèles de reconnaissance**

| Modèle | CER | WER | Remarques |
|--------|-----|-----|-----------|
| EasyOCR | 0,38 | 0,52 | Peu précis sur les textes de petite taille |
| TrOCR (modèle de base) | 0,45 | 0,61 | Non adapté aux images de terrain |
| **TrOCR affiné (notre modèle)** | **0,20** | **0,31** | Affiné sur les textes lisibles de COCO-Text |

On observe dans le tableau 1 que notre modèle affiné surpasse EasyOCR de 47 % et le modèle TrOCR de base de 56 % en termes de CER. La figure 2 illustre la convergence du taux d'erreur au cours de l'entraînement.

**Figure 2 — Évolution du CER au cours du fine-tuning de TrOCR**
*(Courbe CER sur l'ensemble de validation en fonction du nombre d'epochs — convergence vers l'epoch 8, CER final = 0,20)*

Un CER de 0,20 signifie qu'en moyenne, 1 caractère sur 5 est mal transcrit. Pour des mots courants de 4 à 8 caractères, ce taux est suffisant pour que le sens du message reste intelligible. Le modèle affiné a été publié sur HuggingFace Hub afin de garantir la reproductibilité.

---

### 2.2 Un pipeline modulaire qui respecte les contraintes d'accessibilité

#### Argument

L'architecture en sept étapes séquentielles, pilotée par un fichier de configuration unique, traite une image de bout en bout en 1,8 seconde en moyenne — sous le budget de latence de 2 secondes fixé comme exigence d'accessibilité.

#### Preuves

La figure 1 présente l'architecture générale du pipeline.

**Figure 1 — Architecture du pipeline Vision-OCR**

```
Image d'entrée
      ↓
[1] Détection des zones de texte       (docTR db_resnet50)
      ↓
[2] Suppression des doublons           (NMS, IoU ≥ 0,5)
      ↓
[3] Tri en ordre de lecture            (haut→bas, gauche→droite)
      ↓
[4] Découpe des régions de texte       (+4 px de marge)
      ↓
[5] Reconnaissance du texte            (TrOCR affiné)
      ↓
[6] Filtrage par confiance             (seuil 0,75)
      ↓
[7] Synthèse vocale                    (gTTS ou pyttsx3)
      ↓
Sortie : image annotée + audio MP3
```

La latence moyenne mesurée sur 50 images représentatives est de **1,8 seconde** sur CPU. La décomposition est la suivante : détection 0,62 s, reconnaissance 0,89 s, post-traitement et synthèse vocale 0,29 s. Le budget de 2 secondes est respecté dans 91 % des cas. Les 9 % restants correspondent à des images contenant plus de 12 zones de texte simultanées, couvertes par le paramètre `max_crops = 12`.

Le tableau 3 récapitule les paramètres clés de configuration.

**Tableau 3 — Paramètres de configuration du pipeline**

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| Modèle de détection | `db_resnet50` | Meilleur F1 sur le benchmark de détection |
| Seuil IoU (NMS) | 0,50 | Élimine les boîtes redondantes sans perte |
| Marge de découpe | 4 px | Évite la troncature des caractères en bordure |
| Seuil de confiance | 0,75 | Calibré pour minimiser les fausses lectures |
| Nombre maximum de recadrages | 12 | Maintient la latence sous 2 secondes |
| Budget de latence | 2,0 s | Exigence définie en phase 0 du projet |

---

### 2.3 Un mécanisme de sécurité qui protège l'utilisateur contre les erreurs

#### Argument

Le filtrage par confiance est essentiel dans un contexte d'accessibilité : une fausse lecture peut induire l'utilisateur en erreur dans des situations à risque (lecture d'un médicament, d'un panneau de signalisation). Ce mécanisme réduit de 62 % les fausses lectures vocalisées, au prix de la mise en silence de 29 % des textes détectés.

#### Preuves

Le tableau 2 compare les métriques du pipeline avec et sans filtrage par confiance.

**Tableau 2 — Métriques du pipeline avant et après filtrage par confiance**

| Métrique | Sans filtrage | Avec filtrage (seuil 0,75) | Variation |
|----------|--------------|---------------------------|-----------|
| CER des textes vocalisés | 0,20 | **0,12** | −40 % |
| WER des textes vocalisés | 0,31 | **0,18** | −42 % |
| Proportion de textes vocalisés | 100 % | 71 % | −29 % |
| Taux de fausses lectures vocales | 22 % | **8 %** | −62 % |

On observe dans le tableau 2 que le filtrage améliore la qualité des transcriptions vocalisées (CER de 0,20 à 0,12), tout en mettant en silence 29 % des textes dont la confiance est insuffisante. Dans l'interface, les textes vocalisés apparaissent en vert et les textes silenciés en rouge, permettant à un accompagnateur de contrôler visuellement le résultat.

La figure 3 illustre une sortie typique de l'interface Gradio.

**Figure 3 — Exemple de sortie annotée de l'interface Gradio**
*(Image annotée : boîtes vertes = textes vocalisés avec confiance ≥ 0,75 ; boîtes rouges = textes silenciés ; panneau audio MP3 généré automatiquement)*

---

## 3. Conclusion et recommandations

**Le pipeline Vision-OCR Accessibility Assistant constitue une solution viable et déployable pour l'accessibilité des personnes malvoyantes.** Les trois arguments développés dans ce rapport le démontrent : le modèle affiné atteint une précision opérationnelle (CER 0,20), le pipeline respecte les contraintes de latence (1,8 s en moyenne), et le mécanisme de filtrage protège efficacement l'utilisateur (−62 % de fausses lectures vocalisées).

Nous formulons trois recommandations pour la suite du projet, par ordre de priorité :

1. **Déployer une phase pilote** auprès de 10 à 15 utilisateurs malvoyants pour évaluer l'utilisabilité et identifier les cas d'usage prioritaires.
2. **Étendre le fine-tuning** à des textes courbes et à d'autres langues (Total-Text, MLT-2019) pour élargir la portée du système.
3. **Ajouter une suite de tests automatisés** pour sécuriser les évolutions futures du code.

---

## 4. Références bibliographiques

[1] VEIT, A., MATERA, T., NEUMANN, L., MATAS, J., BELONGIE, S. (2016). *COCO-Text: Dataset and Benchmark for Text Detection and Recognition in Natural Images*. arXiv:1601.07140.

[2] LI, M., LV, T., CHEN, J., et coll. (2021). *TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models*. arXiv:2109.10282. Microsoft Research.

[3] MINDEE. (2021). *docTR: Document Text Recognition*. Bibliothèque Python open-source. Consulté le 15 janvier 2026. https://github.com/mindee/doctr

[4] MINTO, B. (2002). *The Pyramid Principle: Logic in Writing and Thinking*. 3e édition. Pearson Education.

[5] ORGANISATION MONDIALE DE LA SANTÉ. (2023). *Cécité et déficience visuelle*. Consulté le 10 mars 2026. https://www.who.int/fr/news-room/fact-sheets/detail/blindness-and-visual-impairment

[6] WOLF, T., et coll. (2020). *HuggingFace's Transformers: State-of-the-art Natural Language Processing*. EMNLP 2020. Association for Computational Linguistics.

---

## 5. Annexes

### Annexe A — Progression par phases du projet Capstone

| Phase | Contenu | Livrable |
|-------|---------|---------|
| Phase 1 — EDA | Analyse exploratoire de COCO-Text v2 | Rapport EDA + visualisations |
| Phase 2 — Benchmark | Comparaison des modèles de détection et de reconnaissance | Tableaux de métriques |
| Phase 3 — MVP | Pipeline de base bout-en-bout | Prototype fonctionnel |
| Phase 4 — Benchmark complet | Évaluation du pipeline complet + MLflow | Métriques CER/WER/latence |
| Phase 5 — Optimisation | Déduplication NMS, ordre de lecture, filtrage confiance | Pipeline optimisé |
| Phase 6 — Fine-tuning | Affinage TrOCR sur COCO-Text, évaluation, publication HuggingFace | Modèle affiné (CER 0,20) |
| Phase 7 — Déploiement | Interface Gradio (3 modes : upload, webcam, flux vidéo) | Application web |

### Annexe B — Extrait du fichier de configuration pipeline.yaml

Ce fichier constitue la source unique de vérité pour tous les hyperparamètres du système.

```yaml
detection:
  model: "db_resnet50"
  dedup_iou_threshold: 0.5
  assume_straight_pages: true

recognition:
  model: "microsoft/trocr-base-printed"
  max_new_tokens: 32
  confidence_threshold: 0.75
  crop_padding: 4
  max_crops: 12

latency:
  budget_s: 2.0

tts:
  backend: "local"   # local (pyttsx3) ou cloud (gTTS)
  rate: 150
  lang: "en"
```
