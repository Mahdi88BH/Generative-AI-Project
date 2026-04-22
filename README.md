# <p align="center"><ins>🌌 Nexus AI : Next-Gen Agentic Intelligence</ins></p>

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Multi--Agents-6E56AF?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/Engine-LangGraph-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Protocol-MCP--Ready-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-v1.0.0--Stable-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <i>Système Expert d'Orchestration Agentique pour l'Analyse et la Correction Académique de Haute Précision.</i>
</p>

---

## 🎯 1. Vision & Objectifs Stratégiques
**Nexus AI** transcende les solutions d'OCR classiques en introduisant une couche de raisonnement probabiliste et déductif. En fusionnant la **Vision par Ordinateur** et les **LLM de pointe (Llama 3.3 70B)**, la plateforme automatise le cycle complet de l'évaluation scientifique :

* **Transcription Cognitive :** Reconstruction sémantique d'examens manuscrits ou numériques via LaTeX avec correction d'erreurs OCR en temps réel.
* **Résolution Magistrale :** Génération de corrigés structurés suivant une méthodologie universitaire stricte (Hypothèses → Lois → Résolution → Unités).
* **Auto-Grader Intelligent :** Analyse comparative sémantique entre une copie élève et un barème, incluant une notation sur 20 et un feedback pédagogique ciblé.

---

## 🛠️ 2. Écosystème Technique (Stack Élite)

<table width="100%">
  <tr>
    <th width="30%">Domaine</th>
    <th width="70%">Technologies & Frameworks</th>
  </tr>
  <tr>
    <td><b>Intelligence Artificielle</b></td>
    <td><b>LangGraph</b> (Cyclic Directed Graphs), LangChain Core, <b>Groq Llama 3.3 70B</b></td>
  </tr>
  <tr>
    <td><b>Vision Engine</b></td>
    <td><b>OpenCV</b> (Image Preprocessing), Tesseract OCR, PyMuPDF (fitz), PDF2Image</td>
  </tr>
  <tr>
    <td><b>Infrastructure API</b></td>
    <td><b>FastAPI</b> (Asynchrone), <b>Uvicorn</b>, Django (UX/UI Management)</td>
  </tr>
  <tr>
    <td><b>Protocoles</b></td>
    <td><b>MCP</b> (Model Context Protocol), SSE (Server-Sent Events), JSON-RPC</td>
  </tr>
  <tr>
    <td><b>Rendu Scientifique</b></td>
    <td>Markdown, <b>MathJax</b> (Rendu LaTeX dynamique pour équations 2D/3D)</td>
  </tr>
</table>

---

<table width="100%">
<tr>
<th width="15%">Phase</th>
<th width="25%">Nœud / Outil</th>
<th width="60%">Action Cognitive & Agentique</th>
</tr>
<tr>
<td align="center"><b>1. Perception</b></td>
<td align="center"><code>Vision Tool (MCP)</code></td>
<td>L'agent invoque le serveur distant. L'outil effectue un pré-traitement <b>OpenCV</b> (Denoising, Thresholding) avant l'extraction par OCR.</td>
</tr>
<tr>
<td align="center"><b>2. Analyse</b></td>
<td align="center"><code>Cognitive Node</code></td>
<td>Le LLM nettoie le texte brut, reconstruit l'énoncé en LaTeX, identifie le domaine (Physique, Maths) et structure le contexte.</td>
</tr>
<tr>
<td align="center"><b>3. Évaluation</b></td>
<td align="center"><code>Expert Node</code></td>
<td>
<ul>
<li><b>Mode Solver :</b> Génération d'une solution idéale détaillée étape par étape.</li>
<li><b>Mode Grader :</b> Comparaison sémantique (Énoncé vs Copie) pour déduire une note rigoureuse.</li>
</ul>
</td>
</tr>
<tr>
<td align="center"><b>4. Interaction</b></td>
<td align="center"><code>Feedback Node</code></td>
<td>Boucle d'ajustement : l'utilisateur affine les résultats via le chat, déclenchant une ré-inférence contextuelle immédiate de l'IA.</td>
</tr>
</table>

🚦 5. Protocole de Déploiement (Ordre Critique)
Pour garantir la connectivité réseau stricte entre l'agent intelligent et ses outils perceptuels, l'ordre de lancement des micro-services est impératif :

<table width="100%">
<tr>
<th width="10%">Ordre</th>
<th width="25%">Micro-Service</th>
<th width="45%">Commande d'exécution (CLI)</th>
<th width="20%">Port & Exposition</th>
</tr>
<tr>
<td align="center"><b>1</b></td>
<td><b>MCP Vision Server</b></td>
<td><code>python ai_engine/mcp_server.py</code></td>
<td align="center">Port <b>8010</b>


<i>(Outils OCR)</i></td>
</tr>
<tr>
<td align="center"><b>2</b></td>
<td><b>Nexus Core (API)</b></td>
<td><code>python ai_engine/main.py</code></td>
<td align="center">Port <b>8001</b>


<i>(Graphe IA)</i></td>
</tr>
<tr>
<td align="center"><b>3</b></td>
<td><b>Web UI Dashboard</b></td>
<td><code>python manage.py runserver</code></td>
<td align="center">Port <b>8000</b>


<i>(Interface)</i></td>
</tr>
</table>

⚙️ 6. Configuration Système
Avant le lancement de l'écosystème, la configuration des variables de sécurité est requise dans le fichier ai_engine/.env :

<table width="100%">
<tr>
<th width="25%">Variable d'Environnement</th>
<th width="15%">Requis</th>
<th width="60%">Description & Paramétrage</th>
</tr>
<tr>
<td><code>GROQ_API_KEY</code></td>
<td align="center">🟢 <b>Oui</b></td>
<td>Clé API pour l'inférence ultra-rapide du modèle Llama 3.3.


<i>Exemple : <code>gsk_abc123...</code></i></td>
</tr>
<tr>
<td><code>TESSERACT_PATH</code></td>
<td align="center">🟡 <b>Windows</b></td>
<td>Chemin absolu vers le binaire Tesseract pour le module Vision.


<i>Exemple : <code>C:\Program Files\Tesseract-OCR\tesseract.exe</code></i></td>
</tr>
</table>

👨‍💻 7. Acteurs & Exploitation
<table width="100%">
<tr>
<th width="25%">Catégorie</th>
<th width="75%">Informations & Détails</th>
</tr>
<tr>
<td><b>Architectes du Système</b></td>
<td><b>Aimad & Mahdi</b> <i>(Master 2 Vision par Ordinateur)</i></td>
</tr>
<tr>
<td><b>Secteurs d'Exploitation</b></td>
<td>Institutions académiques, centres de correction d'examens de masse, et plateformes intelligentes de révision personnalisée.</td>
</tr>
<tr>
<td><b>Versioning & Statut</b></td>
<td><code>v1.0.0-stable</code> — Implémentation basée sur le standard <b>MCP v0.1.0</b>.</td>
</tr>
<tr>
<td><b>Mentions Légales</b></td>
<td>© 2026 Nexus AI - Engineering Intelligence for the Future of Education.


<i>Développé avec rigueur pour l'excellence académique.</i></td>
</tr>
</table>
## 📂 3. Structure du Projet (Modular SoC)
Le projet suit le paradigme de **Separation of Concerns (SoC)** avec des services totalement découplés :

```text
📦 Nexus-AI
 ┣ 📂 ai_engine              # Cœur logique et Intelligence Artificielle
 ┃ ┣ 📜 agent.py             # Orchestration LangGraph & Définition des nœuds
 ┃ ┣ 📜 main.py              # Gateway FastAPI & Gestion de la concurrence
 ┃ ┣ 📜 mcp_server.py        # Micro-service d'outils Vision (Transport SSE)
 ┃ ┗ 📜 ocr_engine.py        # Pipeline de Computer Vision (OpenCV/OCR)
 ┣ 📂 nexus_web              # Couche d'interface utilisateur (UX Layer)
 ┃ ┣ 📂 templates            # Interfaces réactives (Glassmorphism UI)
 ┃ ┗ 📜 manage.py            # Orchestrateur du serveur Django
 ┣ 📜 requirements.txt       # Dépendances multi-services
 ┗ 📜 .env                   # Configuration des variables d'environnement
 
