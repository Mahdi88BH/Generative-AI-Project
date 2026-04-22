# 🌌 Nexus AI : Next-Gen Agentic Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Multi--Agents-6E56AF?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/Engine-LangGraph-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Protocol-MCP--Ready-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-v1.0.0--Stable-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <strong>Système expert de numérisation, résolution et correction automatisée d'examens scientifiques.</strong><br />
  <i>Une fusion entre Vision par Ordinateur avancée et Intelligence Artificielle Agentique.</i>
</p>

---

## 🚀 Vision du Projet

**Nexus AI** n'est pas qu'un simple outil d'OCR. C'est un écosystème intelligent conçu pour le milieu académique de haut niveau. En combinant la puissance de **Llama 3.3 (70B)** et une orchestration par graphes d'états (**LangGraph**), la plateforme transforme des documents manuscrits ou numériques complexes en données structurées, résout des problèmes mathématiques de niveau universitaire et fournit une notation pédagogique précise.

### ✨ Fonctionnalités Clés
- 🧠 **Analyse Cognitive :** Interprétation de l'énoncé avec une fidélité mathématique totale (LaTeX).
- ✍️ **Résolution Autonome :** Génération de corrigés types détaillés avec une approche *Chain-of-Thought*.
- ⚖️ **Correction Chirurgicale :** Comparaison entre la copie élève et le corrigé type, avec feedback constructif.
- 👁️ **Vision Hybride :** Extraction de texte via un serveur MCP dédié utilisant OpenCV et Tesseract.

---

## 🛠️ Stack Technique & Écosystème

| Domaine | Technologies |
| :--- | :--- |
| **Intelligence Artificielle** | LangGraph (Orchestration), LangChain, Groq API (Llama 3.3 70B) |
| **Vision & OCR** | OpenCV, Tesseract OCR, PyMuPDF, PDF2Image |
| **Back-end & API** | FastAPI (Moteur AI), Django (Serveur Web & Gestion Utilisateurs) |
| **Protocoles** | Model Context Protocol (MCP), Server-Sent Events (SSE) |
| **Interface & Rendu** | Glassmorphism UI, LaTeX, MathJax (Rendu 2D/3D) |

---

## 🏗️ Architecture du Système

Le projet repose sur une séparation stricte des préoccupations (**Separation of Concerns**) pour garantir scalabilité et performance.

```text
📦 Nexus-AI
 ┣ 📂 ai_engine              # Cœur de l'Intelligence Artificielle
 ┃ ┣ 📜 agent.py             # Logique du Graphe (Analyse -> Résolution -> Feedback)
 ┃ ┣ 📜 main.py              # Point d'entrée API (FastAPI)
 ┃ ┣ 📜 mcp_server.py        # Serveur d'outils de Vision (Standard MCP)
 ┃ ┗ 📜 ocr_engine.py        # Algorithmes de traitement d'image
 ┣ 📂 nexus_web              # Plateforme Utilisateur (Django)
 ┃ ┣ 📂 templates            # Interfaces modernes (CSS/JS)
 ┃ ┗ 📜 manage.py            # Administration Django
 ┗ 📜 requirements.txt       # Dépendances du projet