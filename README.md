# Searchable Knowledge Base (SKB)

Searchable Knowledge Base (SKB) is a **semantic and multimodal Retrieval-Augmented Generation (RAG) system** designed to index PDF documents and enable natural-language querying through a reasoning chatbot.

The system focuses on **clean architecture, modular design, and local-first execution**, using a local LLM for privacy, FAISS for efficient vector search, and a modern React frontend for interaction.

---

## 🚀 Key Features

* **PDF Ingestion Pipeline**

  * Extracts text, headings, tables, and images from PDF documents
  * Supports scanned PDFs via OCR
  * Robust to partial extraction failures

* **Semantic Vector Search**

  * Uses FAISS for fast similarity search over embedded document chunks
  * Sentence-Transformer embeddings for semantic retrieval

* **Local LLM Reasoning**

  * Integrated with Ollama for local, private inference
  * Answers grounded in retrieved document context
  * Returns cited sources for transparency

* **Clean, Modular Architecture**

  * Separation of concerns between indexing, retrieval, prompt construction, and API
  * Strong typing with Pydantic models across the internal pipeline
  * Centralized configuration (single source of truth)

* **Modern Frontend**

  * React + TypeScript UI
  * Displays answers alongside source documents and tables

---

## 🛠️ Tech Stack

### Backend

* **Language**: Python 3.12+
* **Framework**: FastAPI
* **Vector Search**: FAISS (CPU)
* **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
* **PDF Processing**: `pdfplumber`, `PyMuPDF (fitz)`, OCR support
* **LLM Interface**: Ollama (local inference)
* **Optional Persistence**: MongoDB (via `motor`)

### Frontend

* **Framework**: React 18
* **Language**: TypeScript
* **Build Tool**: Vite
* **Styling**: Tailwind CSS

---

## 📋 Prerequisites

* **Python**: 3.12 or higher
* **Node.js**: 18+
* **Ollama**: Installed and running locally
* **MongoDB (Optional)**:
  Used only for persistence (chat history / metadata).
  **Not required** for core indexing, retrieval, or chatbot functionality.

---

## ⚙️ Configuration

The application is configured via environment variables.

### MongoDB (Optional Persistence)

MongoDB is used **only for optional persistence**, such as storing chat history and metadata.

The **core SKB pipeline** — PDF ingestion, vector indexing, retrieval, and LLM-based answering — works **without MongoDB**.

If MongoDB is disabled or unavailable, the system runs in a **stateless mode**.

---

### Environment Setup

1. Copy the example environment file:

```bash
cp src/.env.example src/.env
```

2. Edit `src/.env` as needed.

#### Enable MongoDB (Optional)

```ini
USE_MONGODB=true
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=skb
```

MongoDB Atlas can also be used by providing a cloud connection string.

#### LLM & Embeddings

```ini
LLM_MODEL=llama3
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Searchable-Knowledge-Base
```

---

### 2. Backend Setup

Recommended: use `uv` for fast dependency management.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

Alternative using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### 3. Frontend Setup

```bash
cd frontend
pnpm install
# or npm install
```

---

### 4. Ollama Setup

Ensure Ollama is running and pull a model:

```bash
ollama pull llama3:instruct
```

---

## 🏃 Usage

### 1. Index Documents

Place PDF files in:

```
src/data/sample_pdfs/
```

Run:

```bash
uv run python run_chatbot.py
```

* Automatically builds the FAISS index if missing
* Stores the index under `storage/`

---

### 2. Run Backend API

```bash
uv run uvicorn chatbot.chatbot_api:app --reload --port 8000
```

---

### 3. Run Frontend

```bash
cd frontend
pnpm dev
```

Open:

```
http://localhost:5173
```

---

## 📂 Project Structure

```
SKB/
├── chatbot/                # Chatbot services & prompt logic
├── frontend/               # React + TypeScript frontend
├── src/
│   ├── api/                # API routes
│   ├── index/              # FAISS indexing & search
│   ├── schemas/            # Pydantic domain models
│   ├── utils/              # PDF extraction & helpers
│   └── data/               # Sample PDFs
├── storage/                # Persisted FAISS indices
├── Project_report/         # Final project report
├── Submission_ppt/         # Submission presentation
├── run_chatbot.py          # Unified runner
└── README.md
```

---

## ⚠️ Limitations & Future Work

**Current Limitations**

* Visual search uses linear scans for image/table metadata
* OCR and image captioning are sequential
* Single-node FAISS index

**Planned Improvements**

* Vectorized indexing for images and tables
* Parallel OCR and GPU-batched captioning
* Distributed and production-grade indexing
* Advanced query rewriting for improved retrieval

---

## 📄 Submission Materials

This repository includes:

* 📘 Full project report (`Project_report/`)
* 📊 Submission presentation (`Submission_ppt/`)

No external links are required.

---

## 🧠 Design Philosophy

> Prioritize correctness, clarity, and maintainability over feature bloat.
> Build systems that are explainable, extensible, and honest about their limits.
