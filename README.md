🎓 Agentic AI Exam Solver

A production-oriented, multi-agent AI system designed to solve academic exam questions directly from images.
This project combines a modern web interface with advanced agent orchestration to deliver structured, reliable, and explainable answers.

🏗️ Architecture Overview

The system follows a modular, three-layer architecture that cleanly separates:

Reasoning (LLMs) → the “brain”
Execution & tools → the “body”
User interaction → the interface
1. Web Application Layer (Django)
User Interface
A clean dashboard that allows users to upload exam images and view results in real time.
Backend
Handles file storage, triggers the AI pipeline, and manages application data.
Flow
Upload image → Launch AI pipeline → Display validated results
2. Orchestration Layer (LangGraph)

Instead of a linear pipeline, the system uses a stateful graph of agents to simulate structured reasoning:

Planner Agent
Determines the solving strategy based on the exam type.
OCR Agent
Coordinates vision tools to extract text from images.
Question Agent
Organizes raw text into structured question blocks.
Answer Agent
Generates solutions using local LLMs (via Ollama).
Reviewer Agent
Validates and corrects outputs to reduce hallucinations.
3. Tool Layer (MCP Server)

The system leverages the Model Context Protocol (MCP) to decouple reasoning from tool execution.

All tools are exposed via a standardized JSON-RPC interface, enabling modularity and scalability.

OCR Tool
Image preprocessing (OpenCV) + text extraction (Tesseract / PaddleOCR)
Math Solver
Symbolic computation for step-by-step verification
Python Executor
Secure sandbox for executing logic and validating results
📂 Project Structure
ai_exam_solver/
├── manage.py            # Django entry point
├── config/              # Settings & URL configuration
├── exam_app/            # Main web application
│   ├── services/        # AI pipeline integration
│   ├── models.py        # Database models
│   └── templates/       # UI صفحات
├── agents/              # Agent logic (Planner, Answer, Reviewer...)
├── langgraph_workflow/  # Graph definition & state machine
├── mcp_server/          # MCP server implementation
│   ├── server.py        # Entry point
│   └── tools/           # OCR, math solver, Python executor
└── media/               # Uploaded exam images
🚀 Execution Pipeline
Upload
The user uploads an exam image (math, physics, etc.)
Pre-processing
The OCR tool enhances the image using OpenCV filters.
Analysis
The system identifies question types (MCQ, open-ended, computational).
Solving
The Answer Agent generates solutions using structured reasoning.
Verification
The Reviewer Agent validates correctness and consistency.
Delivery
Results are displayed as a clear, step-by-step exam report.
🛠️ Tech Stack
Backend / Web: Django 5.x, Python 3.11+
Agent Framework: LangGraph, LangChain
Protocol: Model Context Protocol (MCP)
LLMs (Local): Ollama (Llama 3, Mistral)
Computer Vision: OpenCV, Tesseract OCR
Validation: Pydantic / PydanticAI
✨ Key Features
Multi-agent reasoning architecture
End-to-end pipeline from image to validated solution
Self-correction mechanism to improve reliability
Fully modular and extensible design
Local model support (privacy-friendly)
