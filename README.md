
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
    <li><span class="highlight">Reasoning (LLMs)</span> → the brain</li>
    <li><span class="highlight">Tools & execution</span> → the body</li>
    <li><span class="highlight">User interface</span> → interaction layer</li>
</ul>
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
    <li><strong>OCR Tool:</strong> OpenCV + Tesseract/PaddleOCR</li>
    <li><strong>Math Solver:</strong> Symbolic computation engine</li>
    <li><strong>Python Executor:</strong> Secure sandbox execution</li>
</ul>
</div>

<!-- <div class="card">
<h2>📂 Project Structure</h2>
<pre>
ai_exam_solver/
├── manage.py
├── config/
├── exam_app/
│   ├── services/
│   ├── models.py
│   └── templates/
├── agents/
├── langgraph_workflow/
├── mcp_server/
│   ├── server.py
│   └── tools/
└── media/
</pre>
</div> -->

<div class="card">
<h2>🚀 Execution Pipeline</h2>
<ul>
    <li><strong>Upload:</strong> User submits an exam image</li>
    <li><strong>Pre-processing:</strong> Image enhancement using OpenCV</li>
    <li><strong>Analysis:</strong> Identify question types</li>
    <li><strong>Solving:</strong> Generate answers using reasoning</li>
    <li><strong>Verification:</strong> Validate results</li>
    <li><strong>Delivery:</strong> Display structured report</li>
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

</div>
