<div class="container">

<h1>🎓 Agentic AI Exam Solver</h1>

<p>
A production-oriented, multi-agent AI system designed to solve academic exam questions directly from images.
It combines a modern web interface with advanced agent orchestration to deliver structured, reliable, and explainable results.
</p>

<div class="card">
<h2>🏗️ Architecture Overview</h2>
<p>
The system follows a modular, three-layer architecture separating:
</p>
<ul>
    <li><span class="highlight">Reasoning (LLMs)</span> → the brain (Ollama / Llama 3)</li>
    <li><span class="highlight">Tools & execution</span> → the body (Tesseract / OpenCV)</li>
    <li><span class="highlight">User interface</span> → interaction layer (Django)</li>
</ul>
</div>

<div class="card">
<h2>🚀 Quick Start & Deployment</h2>
<p>Follow these steps to deploy the project locally:</p>
<ol>
    <li><strong>Clone & Env:</strong> 
        <code>git clone [repository-url]</code><br>
        <code>python -m venv venv</code> (Activate with <code>venv\Scripts\activate</code>)
    </li>
    <li><strong>Install Dependencies:</strong> 
        <code>pip install -r requirements.txt</code>
    </li>
    <li><strong>External Tools:</strong>
        <ul>
            <li>Install <strong>Tesseract OCR</strong> (add to System PATH).</li>
            <li>Install <strong>Ollama</strong> and run <code>ollama pull llama3</code>.</li>
        </ul>
    </li>
    <li><strong>Database Setup:</strong>
        <code>python manage.py makemigrations</code>
        <code>python manage.py migrate</code>
    </li>
    <li><strong>Run:</strong>
        <code>python manage.py runserver</code>
    </li>
</ol>
</div>

<div class="card">
<h2>1. Web Application Layer (Django)</h2>
<ul>
    <li><strong>User Interface:</strong> Dashboard for uploading images and viewing results</li>
    <li><strong>Backend:</strong> Handles storage, pipeline execution, and database</li>
    <li><strong>Flow:</strong> Upload → Process → Display results</li>
</ul>
</div>

<div class="card">
<h2>2. Orchestration Layer (LangGraph)</h2>
<p>The system uses a stateful graph of agents instead of a linear pipeline:</p>
<ul>
    <li><strong>Planner Agent:</strong> Defines solving strategy</li>
    <li><strong>OCR Agent:</strong> Extracts text from images</li>
    <li><strong>Question Agent:</strong> Structures extracted content</li>
    <li><strong>Answer Agent:</strong> Generates solutions using LLMs</li>
    <li><strong>Reviewer Agent:</strong> Validates and corrects outputs</li>
</ul>
</div>

<div class="card">
<h2>3. Tool Layer (MCP Server)</h2>
<p>Implements the Model Context Protocol (MCP) to separate reasoning from execution.</p>
<ul>
    <li><strong>OCR Tool:</strong> OpenCV + Tesseract</li>
    <li><strong>Math Solver:</strong> Symbolic computation engine</li>
    <li><strong>Python Executor:</strong> Secure sandbox execution</li>
</ul>
</div>

<div class="card">
<h2>🛠️ Tech Stack</h2>
<p>
<span class="badge">Django</span>
<span class="badge">LangGraph</span>
<span class="badge">LangChain</span>
<span class="badge">MCP</span>
<span class="badge">Ollama</span>
<span class="badge">OpenCV</span>
<span class="badge">Tesseract</span>
<span class="badge">Pydantic</span>
</p>
</div>

<div class="card">
<h2>✨ Key Features</h2>
<ul>
    <li>Multi-agent reasoning system</li>
    <li>End-to-end pipeline (image → solution)</li>
    <li>Self-correction to reduce hallucinations</li>
    <li>Modular and extensible architecture</li>
    <li>Local model support (privacy-friendly)</li>
</ul>
</div>

<p style="text-align:center; font-size:12px; color:#8e8ea0; margin-top:20px;">
    Master 2 Project - Computer Vision & Generative AI Integration
</p>

</div>
