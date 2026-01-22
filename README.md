Project Description

The AI-Powered Code Reviewer & Quality Assistant is a production-grade system that automatically analyzes Python source code, evaluates documentation quality, computes code complexity metrics, and assists developers in generating PEP-257 compliant docstrings using Large Language Models (LLMs).

The system combines static analysis, AI-assisted documentation, validation, reporting, and an interactive Streamlit dashboard, behaving like a mini IDE 🧠 + CI quality gate 🚦.

All changes are safe, reversible, and user-controlled, making it ideal for certification, academic evaluation, and real-world engineering.

✨ Key Features

🔍 AST-based Python source code parsing

🧠 AI-powered docstring generation (preview only)

📘 Supports Google, NumPy, and reST docstring styles

✅ PEP-257 docstring validation

📐 Cyclomatic complexity & maintainability metrics

📊 Accurate documentation coverage reporting

🔄 Before vs After diff preview

🖥️ Interactive Streamlit review dashboard

🔐 Safe Accept / Reject workflow

🧪 Pytest-based automated test suite

📁 JSON reports for CI/CD & certification use

🧠 Techniques Used
📖 Natural Language Processing (NLP)

Semantic understanding of function behavior

Argument and return value interpretation

Context-aware documentation generation

🎯 Prompt Engineering

Strict JSON-only LLM responses

Imperative-style summaries (PEP-257 compliant)

No hallucinated exceptions or metadata

✍️ LLM-Based Text Generation

Generates semantic content only

Formatting handled deterministically in code

Fully configurable LLM backend

🛠️ Tech Stack
💻 Programming Language

Python 3.9+

📚 Libraries & Frameworks

ast – Python Abstract Syntax Tree parsing

streamlit – Interactive dashboard

pytest – Automated testing

pytest-json-report – CI-ready test reports

pydocstyle – PEP-257 validation

radon – Complexity & maintainability metrics

python-dotenv – Environment variable management

🤖 AI / LLM Technologies

Transformer-based Large Language Models

LangChain orchestration

Groq-powered LLM backend (default)

🧬 LLM Details

Uses transformer-based LLMs

Default model: llama-3.1-8b-instant

🔁 LLM backend is fully configurable

Can be replaced with OpenAI, local LLMs, or other providers

🚫 LLM generates content only — never modifies code directly

📂 Project Structure
AI_POWERED_CHATBOT/
│
├── ai_powered/
│   ├── cli/
│   │   └── commands.py
│   │
│   ├── core/
│   │   ├── docstring_engine/
│   │   │   ├── generator.py
│   │   │   └── llm_integration.py
│   │   │
│   │   ├── parser/
│   │   │   └── python_parser.py
│   │   │
│   │   ├── reporter/
│   │   │   └── coverage_reporter.py
│   │   │
│   │   ├── review_engine/
│   │   │   └── ai_review.py
│   │   │
│   │   └── validator/
│   │       └── validator.py
│
├── examples/
│   ├── sample_a.py
│   └── sample_b.py
│
├── storage/
│   ├── reports/
│   └── review_logs.json
│
├── tests/
│   ├── test_parser.py
│   ├── test_generator.py
│   ├── test_validator.py
│   └── test_llm_integration.py
│
├── main_app.py
├── requirements.txt
├── pyproject.toml
├── README.md

⚙️ Installation Steps
1️⃣ Clone the Repository
git clone your_github_link
cd AI_POWERED_CHATBOT

2️⃣ Create Virtual Environment
python -m venv ai_powered

3️⃣ Activate Virtual Environment (Windows)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\ai_powered\Scripts\Activate.ps1

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Set Environment Variables

Create a .env file:

GROQ_API_KEY=your_api_key_here

▶️ How to Run the Project Locally
🖥️ Run Streamlit Dashboard
streamlit run main_app.py

🧪 Run Tests
pytest --json-report --json-report-file=storage/reports/pytest_results.json


📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software with attribution.