📌 Eightfold Company Research Assistant

An AI-powered assistant that can research companies, generate structured account plans, extract company information, and interact through a clean frontend and API backend.

This project is designed to simulate real-world AI agent workflows, including:

Automated company research

AI-driven analysis

Clean, modular backend

Frontend UI to interact with the agent

FastAPI-based API server

Integration-ready architecture for APIs (OpenAI, Tavily, Clearbit, etc.)

🚀 Features

Company Name Extraction – Detects the company from user messages

Automated Research Mode – Switches into research mode when a company is detected

Account Plan Generation – Creates structured insights

Session-Based State – Uses in-memory session states

Extensible API Agent – Modular design for research tools

Frontend Interface – Basic UI for interacting with the assistant

🛠️ Tech Stack
Backend

Python

FastAPI

Pydantic

Uvicorn

Requests

OpenAI SDK (optional)

Frontend

HTML

CSS

JavaScript

Streamlit (optional)

📁 Project Structure
eightfold-company-assistant/
│
├── backend/
│   ├── agent.py
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .env  (ignored)
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│
└── README.md

⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/Sha-hub-2004/eightfold-company-assistant-.git
cd eightfold-company-assistant-

2. Create Virtual Environment
python -m venv venv

3. Activate Environment

Windows (PowerShell):

.\venv\Scripts\Activate.ps1

4. Install Dependencies
pip install -r backend/requirements.txt

▶️ Running the Project
Start Backend
python backend/app.py


API runs at:

http://127.0.0.1:8000

Start Frontend

If using Streamlit:

python -m streamlit run frontend/app.py


Or open directly:

frontend/index.html

🔧 Environment Variables

Create a .env inside backend/:

OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=optional
CLEARBIT_API_KEY=optional

🧩 Future Enhancements

Add real API integrations

Add web scraping capability

Expand research model

Add account summary export (PDF, Docx)

Add user authentication

Add vector database for long-term memory
