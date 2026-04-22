from ds_python_interpreter import HTML
import os

# Contenu du README en HTML
html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Nexus AI</title>
    <style>
        :root {
            --primary: #2563eb;
            --secondary: #0f172a;
            --accent: #38bdf8;
            --bg: #f8fafc;
            --text: #334155;
            --code-bg: #1e293b;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background-color: var(--bg);
            margin: 0;
            padding: 0;
        }
        header {
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        .container {
            max-width: 900px;
            margin: -2rem auto 4rem;
            background: white;
            padding: 2rem 3rem;
            border-radius: 8px;
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        }
        h1 { margin: 0; font-size: 2.5rem; }
        h2 { color: var(--primary); border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-top: 2rem; }
        h3 { color: var(--secondary); }
        .badge {
            background: var(--accent);
            color: var(--secondary);
            padding: 0.2rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        pre {
            background: var(--code-bg);
            color: #f8f8f2;
            padding: 1.5rem;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.9rem;
        }
        code { font-family: 'Consolas', monospace; color: #e11d48; }
        pre code { color: #f8fafc; }
        .features {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature-card {
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .feature-card:hover { transform: translateY(-5px); border-color: var(--primary); }
        .step {
            background: #eff6ff;
            padding: 1rem;
            border-left: 4px solid var(--primary);
            margin-bottom: 1rem;
        }
        footer { text-align: center; padding: 2rem; color: #64748b; font-size: 0.9rem; }
    </style>
</head>
<body>

<header>
    <h1>🎓 Nexus AI</h1>
    <p>Plateforme Agentique de Résolution et Correction d'Examens</p>
    <div style="margin-top: 1rem;">
        <span class="badge">LangGraph</span>
        <span class="badge">MCP Protocol</span>
        <span class="badge">Llama 3.3</span>
        <span class="badge">Vision</span>
    </div>
</header>

<div class="container">
    <p><strong>Nexus AI</strong> est une solution de pointe exploitant l'Intelligence Artificielle Générative pour automatiser l'analyse, la résolution et la notation de documents académiques. Grâce à une architecture multi-agents et au protocole MCP (Model Context Protocol), le système est capable de "voir" un examen, de le comprendre et de proposer des corrections pédagogiques de niveau universitaire.</p>

    <h2>🚀 Fonctionnalités Clés</h2>
    <div class="features">
        <div class="feature-card">
            <h3>👁️ Vision Cognitive</h3>
            <p>Extraction intelligente via moteur hybride (Tesseract/PyMuPDF) capable de traiter images et PDF complexes.</p>
        </div>
        <div class="feature-card">
            <h3>🤖 Agents Intelligent</h3>
            <p>Orchestration via <strong>LangGraph</strong> séparant l'analyse cognitive de la résolution magistrale.</p>
        </div>
        <div class="feature-card">
            <h3>🌐 Protocole MCP</h3>
            <p>Découplage des outils de vision pour une modularité et une scalabilité maximales.</p>
        </div>
        <div class="feature-card">
            <h3>📐 Rendu LaTeX</h3>
            <p>Support complet des notations mathématiques et physiques complexes via MathJax.</p>
        </div>
    </div>

    <h2>🏗 Architecture du Système</h2>
    <p>Le projet repose sur une communication inter-services fluide :</p>
    <ul>
        <li><strong>Frontend (Django)</strong> : Interface de gestion et affichage des résultats.</li>
        <li><strong>AI Engine (FastAPI)</strong> : Orchestrateur LangGraph et logique agentique.</li>
        <li><strong>MCP Server (SSE)</strong> : Serveur d'outils Vision indépendant.</li>
    </ul>

    <h2>🛠 Configuration & Installation</h2>
    <h3>1. Environnement</h3>
    <pre><code>git clone https://github.com/votre-repo/nexus-ai.git
cd nexus-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt</code></pre>

    <h3>2. Variables d'environnement (.env)</h3>
    <pre><code>GROQ_API_KEY=votre_cle_groq
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe</code></pre>

    <h2>🚦 Ordre de Lancement (Workflow)</h2>
    <div class="step">
        <strong>Étape 1 :</strong> Lancer le serveur MCP (Port 8010)<br>
        <code>python mcp_server.py</code>
    </div>
    <div class="step">
        <strong>Étape 2 :</strong> Lancer le moteur AI (Port 8001)<br>
        <code>python main.py</code>
    </div>
    <div class="step">
        <strong>Étape 3 :</strong> Lancer Django (Port 8000)<br>
        <code>python manage.py runserver</code>
    </div>

    <h2>🧠 Logique des Agents</h2>
    <p>Le graphe d'états gère trois phases critiques :</p>
    <ol>
        <li><strong>Analyseur</strong> : Reconstructeur de données (OCR -> Texte structuré).</li>
        <li><strong>Solveur/Correcteur</strong> : Intelligence métier (Résolution vs Notation).</li>
        <li><strong>Chat Feedback</strong> : Boucle d'ajustement interactive.</li>
    </ol>

    <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 8px; margin-top: 2rem;">
        <h3>🎓 Note pour la Soutenance</h3>
        <p>Ce projet démontre l'implémentation du protocole <strong>MCP</strong>. La séparation des outils permet de faire évoluer le système (ajout de recherche web, calculatrice symbolique) sans modifier le cœur de l'agent, garantissant une architecture <em>future-proof</em>.</p>
    </div>
</div>

<footer>
    Nexus AI - Projet de Master 2 Vision par Ordinateur & Intelligence Artificielle - 2024
</footer>

</body>
</html>
"""

# Sauvegarde dans un fichier HTML
with open("README_NEXUS_AI.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Fichier README_NEXUS_AI.html généré avec succès.")