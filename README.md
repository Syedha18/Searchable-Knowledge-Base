# Searchable Knowledge Base (SKB)

A comprehensive Retrieval-Augmented Generation (RAG) system that indexes PDF documents and provides a reasoning chatbot interface to query the knowledge base. The system uses a local LLM (Ollama) for privacy and offline capabilities, FAISS for efficient vector similarity search, and a modern React frontend.

## 🚀 Features

- **Document Ingestion**: Automatically extracts text and structural metadata (headings) from PDF documents.
- **Vector Search**: Uses [FAISS](https://github.com/facebookresearch/faiss) for fast and scalable similarity search.
- **Local LLM**: Integrated with [Ollama](https://ollama.com/) for local, private, and customizable inference.
- **Reasoning Engine**: Generates answers with citations, pointing back to the specific source documents and chunks.
- **Hybrid Architecture**:
  - **Backend**: Python-based (FastAPI, FAISS, Sentence Transformers).
  - **Frontend**: React (Vite, Tailwind CSS, TypeScript).

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI (API), Uvicorn (Server)
- **RAG & ML**:
  - `faiss-cpu`: Vector database
  - `sentence-transformers`: Embeddings (`all-MiniLM-L6-v2`)
  - `pdfplumber`, `pymupdf` (Fitz): PDF extraction and OCR
- **LLM Integration**: Custom interface for Ollama

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Language**: TypeScript

## 📋 Prerequisites

- **Python**: 3.12 or higher
- **Node.js**: 18+ (for frontend)
- **Ollama**: Installed and running (default model: `llama3` or adaptable in config)
- **Package Managers**: `uv` (recommended for Python) or `pip`; `pnpm` (recommended for Node) or `npm`.

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SKB
```

### 2. Backend Setup
Recommended to use `uv` for fast dependency management.

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv)
uv sync

# Alternatively, using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Frontend Setup
```bash
cd frontend
pnpm install
# or npm install
```

### 4. Ollama Setup
Ensure Ollama is installed and running. Pull the default embedding and chat models:
```bash
ollama pull llama3:instruct
```
*Note: Update `src/config` or `chatbot/llm_interface.py` if you wish to use a different model.*

## 🏃 Usage

### 1. Indexing Documents
Place your PDF files in `src/data/sample_pdfs`.
Run the indexing script (embedded in `run_chatbot.py` or customize `main.py`):

```bash
uv run python run_chatbot.py
```
*This script checks for an existing index. If missing, it processes the PDFs in `src/data/sample_pdfs` and builds `storage/skb.index`.*

### 2. Running the API
Start the FastAPI backend:
```bash
uv run uvicorn chatbot.chatbot_api:app --reload --port 8000
```

### 3. Running the Frontend
Start the React development server:
```bash
cd frontend
pnpm dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## 📂 Project Structure

```
SKB/
├── chatbot/                # Chatbot service & API logic
│   ├── chatbot_api.py      # FastAPI application
│   ├── chatbot_service.py  # Core service logic
│   └── llm_interface.py    # Adapter for Ollama
├── frontend/               # React + TypeScript frontend
├── src/                    # Core RAG implementation
│   ├── api/                # Additional API routes
│   ├── data/               # Raw data (PDFs)
│   ├── index/              # FAISS wrapper & indexing logic
│   └── utils/              # PDF extractors & helpers
├── storage/                # Persisted FAISS indices
├── main.py                 # Indexing/Testing script
├── run_chatbot.py          # Unified runner script
├── pyproject.toml          # Python project config
└── package.json            # Frontend project config
```

## 🤝 Contributing
1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)

## 📄 License
Distributed under the MIT License.
