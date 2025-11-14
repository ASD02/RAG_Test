## RAG Conversational Tutor

A small Retrieval-Augmented Generation (RAG) playground that uses ChromaDB, LangChain’s `ChatOllama`, and conversational memory to act as an AI tutor over a local corpus of PDF documents.

---

## Table of Contents

- [About](#about)  
- [Features](#features)  
- [Quick Start](#quick-start)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Development](#development)  
- [Testing](#testing)  
- [Deployment](#deployment)  
- [Troubleshooting](#troubleshooting)  
- [Contributing](#contributing)  
- [License](#license)  
- [Authors & Maintainers](#authors--maintainers)  
- [Assumptions & Missing Info](#assumptions--missing-info)

---

## About

This project is a **RAG-based study tutor** that answers questions using a set of local PDF documents. It combines:

- A persistent **ChromaDB** collection for document storage and retrieval  
- An **in-memory ChromaDB collection** for conversational history  
- **LangChain + ChatOllama** to generate responses, optimized via a custom query optimizer and prompt templates

It is intended as a learning and experimentation tool for developers interested in practical RAG pipelines, conversational memory, and prompt engineering.

**Tech overview:**

- Language: **Python**  
- Vector store: **ChromaDB** (persistent + in-memory)  
- LLM runtime: **Ollama** `langchain-ollama`  
- Document types: primarily **PDFs** converted to markdown-like chunks  
- Entry point: `model.py`

---

## Features

- **RAG Tutor Loop**: Interactive CLI loop (`model.py`) that answers questions based on retrieved documents (UI to come).
- **Conversational Memory**: In-memory ChromaDB (`memory/conversation_memory.py`) stores Q&A pairs and retrieves relevant history.
- **LLM Query Optimization**: `core/query_optimizer.py` rewrites user questions (especially follow-ups) into optimized search queries.
- **Tokenization & Filtering**: `core/query_tokenizer.py` and `core/document_processor.py` extract key terms and filter documents by distance and keyword relevance.
- **Prompt Library**: Structured prompt templates in `prompts/` for both query optimization and tutor behavior.
- **Session Persistence**: `core/session_manager.py` serializes conversation history to `session.json` on exit.
- **Document Ingestion**: `utils/chroma_test.py` ingests PDFs from a folder into a ChromaDB collection, with chunking.

---

## Quick Start

Assuming you have Python and Ollama installed:

```bash
git clone <this-repo-url>
cd RAG

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Make sure Ollama is running and that gpt-oss:20b (or your chosen model) is pulled
# Example: ollama pull gpt-oss:20b

# Ingest example PDFs into ChromaDB
python -m utils.chroma_test

# Run the conversational tutor
python model.py
```

---

## Installation

### Prerequisites

- **Python**: 3.9+ 
- **Ollama**: Installed and running locally (You can change the model in model.py) 

### Dependencies

All Python dependencies are declared in `requirements.txt`:

- `chromadb`  
- `PyPDF2`  
- `langchain-ollama`  
- `scikit-learn`

Install them into a virtual environment:

```bash
python -m venv .venv
# Activate venv...
pip install -r requirements.txt
```

---

## Configuration

- **LLM model**: Set in `model.py`:

  ```python
  model = langchain_ollama.ChatOllama(
      model="gpt-oss:20b",
      num_ctx=32768
  )
  ```

  You can change `model` to any Ollama-hosted model you have available.

- **ChromaDB persistent path**: In `utils/chroma_test.py`, the persistent client points to `chroma_db`:

  ```python
  chroma_client = chromadb.PersistentClient(path="chroma_db")
  collection = chroma_client.get_or_create_collection(name="test_collection")
  ```

- **Document retrieval parameters**: In `core/document_processor.py`:

  ```python
  DocumentProcessor(n_results=20, distance_threshold=1.5)
  ```

  Adjust `n_results` and `distance_threshold` for recall vs precision trade-offs.

- **Session file**: `core/session_manager.py` writes to `session.json` by default.

No environment variables are required by default; you may add your own configuration layer if needed.

---

## Usage

### 1. Ingest Documents

Before running the tutor, ingest your PDFs into ChromaDB:

```bash
python -m utils.chroma_test
```

Choose option `1` (“Ingest documents”) and provide the folder path with PDFs (e.g., `test_documents/`). The utility:

- Converts PDFs to markdown-like text (`convert_to_markdown`)
- Chunks content into ~300-character segments (`ingest_markdown`)
- Stores them in `chroma_db/test_collection`

You can also choose option `2` to manually query the collection.

### 2. Run the Conversational Tutor

```bash
python model.py
```

Workflow:

1. You are prompted for the **first question**.  
2. The system:
   - Optimizes your query (`QueryOptimizer`)
   - Tokenizes and filters documents (`QueryTokenizer` + `DocumentProcessor`)
   - Builds the final LLM prompt (`PromptFormatter` + `prompts/tutor_prompt.py`)
   - Calls the LLM and prints:
     - Optimized query  
     - Final prompt sent to the model  
     - Model response  
3. The Q&A is stored in `ConversationMemory`.  
4. For subsequent questions, the system retrieves relevant conversation history and uses it to:
   - Improve query optimization  
   - Provide continuity in the tutor prompt (while still grounding in documents)

To exit, type `quit`, `exit`, or `q`. The session history is saved to `session.json`.

---

## Development

### Directory Structure

- `model.py` – Main entrypoint; orchestrates the full RAG + memory pipeline.
- `core/`
  - `query_optimizer.py` – LLM-based search query optimization using conversation history.
  - `query_tokenizer.py` – Extracts key and “important” terms from queries.
  - `document_processor.py` – ChromaDB retrieval, distance/keyword filtering, and formatting.
  - `prompt_formatter.py` – Assembles the final tutor prompt with history and documents.
  - `session_manager.py` – Session load/save and memory restoration.
- `memory/`
  - `conversation_memory.py` – In-memory ChromaDB collection for Q&A history.
- `prompts/`
  - `tutor_prompt.py` – Tutor behavior and history context templates.
  - `query_optimizer.py` – Query optimization prompt template.
- `utils/`
  - `chroma_test.py` – Document ingestion + query CLI for the vector store.
  - `model_test.py`, `tfidf_test.py` – Experimental / test scripts.
- `test_documents/` – Example PDFs for ingestion.
- `chroma_db/` – Persistent ChromaDB data directory (generated at runtime).
- `session.json` – Serialized conversation history (generated at runtime).

### Commands

- Run the main tutor:

  ```bash
  python model.py
  ```

- Run the ingestion/query utility:

  ```bash
  python -m utils.chroma_test
  ```

No explicit linters or formatters are configured in the repo; you can add tools like `black`, `ruff`, or `flake8` as needed.

---

## Troubleshooting

- **`ModuleNotFoundError: langchain_ollama` or `chromadb`**  
  Ensure you are inside the virtual environment and have run:

  ```bash
  pip install -r requirements.txt
  ```

- **Ollama / model not found**  
  - Make sure the Ollama service is running.  
  - Pull the configured model or change the model name in `model.py`.

- **No or poor retrieval results**  
  - Check that you ingested the correct folder via `utils/chroma_test.py`.  
  - Verify that `chroma_db/` contains data.  
  - Tune `n_results` and `distance_threshold` in `DocumentProcessor`.

- **Session restore issues**  
  - If `session.json` is corrupted, delete it and run again.  
  - `SessionManager` is defensive and will ignore invalid session files.

- **Interactive scripts failing under automated runs**  
  - `model.py` and `utils/chroma_test.py` are interactive (use `input()`).  
  - For non-interactive scenarios, you’ll need to refactor to inject questions programmatically.

---