# <p align="center"><ins>🌌 Nexus AI : Next-Gen Agentic Intelligence</ins></p>

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Multi--Agents-6E56AF?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/Engine-LangGraph-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Protocol-MCP--Ready-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-v1.0.0--Stable-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <i>Plateforme Agentique de Haute Précision pour la Résolution et la Correction d'Examens Scientifiques.</i>
</p>

---

## 🎯 1. Vision & Objectifs
**Nexus AI** est un système expert conçu pour automatiser l'analyse de documents académiques complexes. En fusionnant la **Vision par Ordinateur** et les **LLM (Large Language Models)**, la plateforme offre une solution de bout en bout pour :

*   **Numérisation Intelligente :** Transcription d'examens (manuscrits ou numériques) avec une fidélité mathématique totale via LaTeX.
*   **Résolution Scientifique :** Production de corrigés types détaillés avec une approche pédagogique universitaire.
*   **Correction Automatisée :** Évaluation des copies d'élèves, notation sur 20 et feedback chirurgical par comparaison sémantique.

---

## 🛠️ 2. Écosystème Technique (Stack)

<table width="100%">
  <tr>
    <th width="30%">Domaine</th>
    <th width="70%">Technologies Utilisées</th>
  </tr>
  <tr>
    <td><b>Intelligence Artificielle</b></td>
    <td>LangGraph (Orchestration), LangChain, Groq API (Llama 3.3 70B)</td>
  </tr>
  <tr>
    <td><b>Vision & OCR</b></td>
    <td>OpenCV, Tesseract OCR, PyMuPDF (fitz), PDF2Image</td>
  </tr>
  <tr>
    <td><b>Architectures Web</b></td>
    <td>FastAPI (Moteur AI), Django (Interface Utilisateur)</td>
  </tr>
  <tr>
    <td><b>Protocoles</b></td>
    <td>Model Context Protocol (MCP), SSE (Server-Sent Events)</td>
  </tr>
  <tr>
    <td><b>Rendu Scientifique</b></td>
    <td>LaTeX, MathJax (Rendu équations 2D/3D), Markdown</td>
  </tr>
</table>

---

## 📂 3. Structure du Projet
Le projet est structuré en **services découplés** pour une maintenance modulaire et une scalabilité optimale :

```text
📦 Nexus-AI
 ┣ 📂 ai_engine              # Cœur de l'Intelligence Artificielle
 ┃ ┣ 📜 agent.py             # Graphe LangGraph (Logique des agents)
 ┃ ┣ 📜 main.py              # API FastAPI (Point d'entrée du moteur)
 ┃ ┣ 📜 mcp_server.py        # Serveur d'outils Vision (Standard MCP)
 ┃ ┗ 📜 ocr_engine.py        # Moteur hybride de Vision par Ordinateur
 ┣ 📂 nexus_web              # Interface Utilisateur (Django)
 ┃ ┣ 📂 templates            # Pages HTML/CSS (Glassmorphism UI)
 ┃ ┗ 📜 manage.py            # Script d'administration Django
 ┣ 📜 requirements.txt       # Dépendances globales
 ┗ 📜 .env                   # Variables de configuration (Secret)

 ---

## 🧠 4. Workflow de l'Agent (Chain-of-Thought)
Le flux de travail est orchestré par un graphe d'états cyclique garantissant la cohérence et la rigueur scientifique des données :

*   **Phase de Perception (Vision Tool)** : L'agent détecte un fichier et invoque le serveur MCP. L'outil `read_document` effectue un nettoyage OpenCV (Upscaling, Thresholding) avant l'extraction OCR.
*   **Phase d'Analyse (Cognitive Node)** : Le LLM reconstruit l'énoncé, identifie le domaine (Physique, Maths) et prépare le contexte de correction.
*   **Phase de Résolution/Notation (Expert Node)** :
    *   **Mode Solver** : Génération d'une solution idéale, pas-à-pas.
    *   **Mode Grader** : Comparaison point par point entre l'énoncé et la copie élève pour déduire une note équitable.
*   **Boucle de Feedback (Interaction Node)** : L'utilisateur peut affiner les résultats, déclenchant une ré-inférence ciblée de l'IA.

---

## 🚦 5. Protocole de Déploiement (Workflow de démarrage)
Pour garantir la connectivité entre l'agent et ses outils, respectez l'ordre suivant dans vos terminaux respectifs :

| Ordre | Service | Commande | Rôle |
| :--- | :--- | :--- | :--- |
| **1** | **MCP Vision** | `python ai_engine/mcp_server.py` | Expose les capacités OCR sur le port 8010 |
| **2** | **Nexus Core** | `python ai_engine/main.py` | Active le graphe d'IA sur le port 8001 |
| **3** | **Web Interface** | `python manage.py runserver` | Lance le portail utilisateur sur le port 8000 |

---

## ⚙️ 6. Configuration Système
Avant le lancement, configurez le fichier `.env` dans le dossier `ai_engine/` :

```env
# Clé API pour l'inférence du modèle Llama 3.3 via Groq
GROQ_API_KEY=gsk_your_key_here

# Chemin vers l'exécutable Tesseract sur Windows
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

---

## 👨‍💻 7. Acteurs & Exploitation

*   **Architectes** : Aimad & Mahdi (_Master 2 Vision par Ordinateur_)
*   **Exploitation** : Plateforme destinée aux institutions académiques pour l'assistance à la correction de masse et l'aide à la révision personnalisée.
*   **Versioning** : `v1.0.0-stable` (Basé sur le protocole MCP v0.1.0).

<br />

<p align="center">
  <b>©  Nexus AI - Engineering Intelligence for the Future of Education</b><br />
  <i>Made with ❤️ for Academic Excellence</i>
</p>