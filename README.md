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