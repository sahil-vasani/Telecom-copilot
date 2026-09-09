# 📡 TelecomRAG — Retrieval-Augmented Generation for Telecom Customer Support

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?logo=huggingface&logoColor=black" />
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-00A86B" />
  <img src="https://img.shields.io/badge/PEFT-DoRA%20%7C%20LoRA-8A2BE2" />
  <img src="https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> A production-grade, end-to-end **Tool-Augmented RAG System** designed for Indian telecom customer support. Combines fine-tuned dense retrieval, cross-encoder reranking, BERT-based tool policy routing, and DoRA / LLM generation — grounded on a massive 26,000+ passage corpus built from **Jio, Airtel, Vi, BSNL, TRAI guidelines**, and grounded dialogue datasets (**MultiDoc2Dial**).

---

## 🗂 Table of Contents

- [Overview](#-overview)
- [Live Demo Screenshots](#-live-demo-screenshots)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Core Components](#-core-components)
- [Dataset & Knowledge Base](#-dataset--knowledge-base)
- [Training & Ingestion Pipeline](#-training--ingestion-pipeline)
- [Inference Pipeline (ReAct Control Loop)](#-inference-pipeline-react-control-loop)
- [Evaluation Harness & Metrics](#-evaluation-harness--metrics)
- [Installation & Setup Guide](#-installation--setup-guide)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [Design Decisions](#-design-decisions)
- [Roadmap & Acknowledgements](#-roadmap--acknowledgements)

---

## 🔍 Overview

**TelecomRAG (Telecom Copilot)** addresses a critical challenge in conversational AI: general-purpose LLMs lack reliable, up-to-date knowledge on carrier-specific policies, recharge tariffs, network APN configurations, regulatory guidelines, and real-time network status.

This project delivers a multi-stage NLP & Agentic pipeline that standardizes telecom knowledge into structured vector spaces, routes user intents via specialized classifiers, executes external tools (including live outage inspection and ticket generation), and generates cited, grounded answers.

### Key Highlights

- **26,104 Knowledge Passages**: Hybrid corpus comprising 24,933 grounded passages from MultiDoc2Dial and 1,171 telecom overlay passages spanning Jio, Airtel, Vi, BSNL, and TRAI regulatory frameworks.
- **Fine-Tuned Retrieval & Reranking**: BGE-large retriever trained with Multiple Negatives Ranking Loss (MNRL) coupled with a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) reranker.
- **BERT Tool Policy Classifier**: Fine-tuned BERT routing model that classifies incoming intent into specific tool executions (`SearchKB`, `GetPolicy`, `CreateTicket`, `CheckNetworkStatus`).
- **Flexible Dual Generator Support**:
  - **Local DoRA Flan-T5**: Parameter-Efficient Fine-Tuning using Weight-Decomposed Low-Rank Adaptation (DoRA rank 16, alpha 32).
  - **Cloud OpenRouter LLM**: Production fallback integration supporting models like NVIDIA Nemotron 3 Super 120B with automated rate-limit retry handling.
- **Novel Telecom Evaluation Metrics**: Custom evaluation harness computing **Citation Recall@1**, **Answer Coverage (ROUGE-1 proxy)**, **Grounded Escalation Accuracy (GEA)**, and **Outage-Aware Response Rate (OARR)**.
- **Interactive React 19 Operations Dashboard**: SaaS control panel built with Vite, Tailwind CSS, Framer Motion, and Recharts to view live metrics, copilot chats, ticket queues, and network status feeds.

---

## 📸 Live Demo Screenshots

Below are screenshots of the operational web interface for Telecom Copilot:

### 📊 Dashboard Overview
*Monitors system health, ticket distribution (Open vs. Escalated), active network anomalies, and knowledge base indexing stats.*
![Dashboard Page](docs/images/dashboard_demo.png)

### 💬 Copilot Chat Interface
*Handles live query routing, tool execution traces (dense vector search, reranking, outage checks), citation rendering, and automated ticket generation.*
![Copilot Chat](docs/images/copilot_chat_demo.png)

### 🎫 Support Tickets View
*Tracks complaints confidence-escalated into structured customer support tickets with SLA tracking and queue management.*
![Support Tickets](docs/images/tickets_demo.png)

### 🚨 Live Network Status Feed
*Simulates real-time network anomaly feeds across Indian telecom circles, calculating compensation eligibility and outage durations.*
![Network Status](docs/images/network_status_demo.png)

---

## 🏗 System Architecture

```
                                 User Query
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    Tool Policy Classifier    │
                      │  (fine-tuned BERT / Rules)   │
                      └──────────────┬───────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
         ▼                                                       ▼
┌──────────────────┐                                   ┌──────────────────┐
│ CheckNetworkStatus│ (Network outage queries)         │     SearchKB     │ (General domain queries)
│  (Live Feed)     │                                   │  FAISS IndexFlat │
└────────┬─────────┘                                   └────────┬─────────┘
         │                                                       │ Top-20 Passages
         │                                                       ▼
         │                                             ┌──────────────────┐
         │                                             │   Cross-Encoder  │
         │                                             │     Reranker     │
         │                                             └────────┬─────────┘
         │                                                       │ Top-3 Passages
         └───────────────────────────┬───────────────────────────┘
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    Confidence Escalation     │
                      │  (Low score -> CreateTicket) │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    Generator (DoRA T5 /      │
                      │    Nemotron 120B via API)    │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
                      Structured Response + Citations
                      [SOURCE: doc_id, section_id]
```

---

## 📁 Project Structure

```
Telecom-copilot/
├── data/
│   ├── raw/
│   │   ├── telecom_kb/                   # Raw operator documents & policy text
│   │   └── network_status.json           # Mock live network feed across regions
│   └── processed/
│       ├── dataset_stats.json            # Corpus passage, document & word counts
│       ├── kb_passages.jsonl             # 26,104 structured passages for FAISS
│       ├── span_index.json               # Fast span-level lookup table
│       ├── doc_index.json                # Document metadata lookup table
│       ├── retriever_train.jsonl         # Merged retrieval training triples
│       ├── retriever_train_md2d.jsonl    # MultiDoc2Dial retrieval triples
│       ├── retriever_train_telecom.jsonl # Telecom BM25-mined training triples
│       ├── generator_sft_train.jsonl     # Supervised fine-tuning pair data
│       ├── dpo_pairs.jsonl               # Preference pairs (MD2D + SHP-2)
│       ├── test_cases.jsonl              # Test dataset for evaluation harness
│       ├── tickets.jsonl                 # Logged customer escalation tickets
│       ├── full_system_results.jsonl     # Inference outputs on test dataset
│       └── full_system_results.eval.json # Evaluator metrics report
│
├── src/
│   ├── ingestion/                        # Knowledge Base & Dataset Construction
│   │   ├── kb_builder.py                 # MultiDoc2Dial + Telecom KB merger
│   │   ├── telecom_corpus_builder.py     # Base telecom passage generator
│   │   ├── telecom_corpus_builder_expanded.py # 1,100+ expanded telecom passages
│   │   ├── training_data_builder.py      # Merged SFT, DPO & retriever dataset generator
│   │   └── data_source/                  # Carrier-specific data scrapers/parsers
│   │       ├── airtel_data_ingestion.py  # Airtel FAQs & policy passages
│   │       ├── bsnl_data_ingestion.py    # BSNL citizen charter passages
│   │       ├── jio_data_ingestion.py     # Jio FAQ data
│   │       ├── vi_data_ingestion.py      # Vi (Vodafone Idea) data
│   │       ├── TRAI_data_ingestion.py    # TRAI regulatory guidelines
│   │       └── general_ingestion.py      # Generic telecom & APN setup guides
│   │
│   ├── retrieval/                        # Vector Search & Reranking
│   │   ├── train_retriever.py            # BGE dense retriever fine-tuning (MNRL)
│   │   ├── faiss_indexer.py              # FAISS IndexFlatIP vector index build
│   │   └── reranker.py                   # Cross-Encoder fine-tuning & inference
│   │
│   ├── generation/                       # Response Generation
│   │   ├── train_generator.py            # DoRA fine-tuning for Flan-T5
│   │   └── openrouter_generator.py       # OpenRouter cloud generator (Nemotron 120B)
│   │
│   ├── policy/                           # Intent Routing
│   │   └── tool_policy_classifier.py     # Fine-tuned BERT tool routing classifier
│   │
│   ├── tools/                            # System Tools
│   │   └── tool_executor.py              # SearchKB, GetPolicy, CreateTicket, CheckNetworkStatus
│   │
│   ├── pipeline/                         # Execution Orchestration
│   │   └── inference_pipeline.py         # Full ReAct-style end-to-end pipeline
│   │
│   └── evaluation/                       # Evaluation Suite
│       └── evaluator.py                  # Multi-metric automated evaluation harness
│
├── frontend/                             # React 19 Operations Dashboard
│   ├── public/                           # Static assets & favicon
│   ├── src/                              # React components, pages, & state
│   ├── package.json                      # Node dependencies (Vite, Tailwind, Recharts)
│   ├── tailwind.config.js                # Custom styling system
│   └── vite.config.ts                    # Vite dev server configuration
│
├── checkpoints/                          # Saved Model Weights (gitignored)
│   ├── retriever/                        # Fine-tuned BGE retriever weights
│   ├── reranker/                         # Fine-tuned Cross-Encoder weights
│   └── generator/                        # DoRA Flan-T5 adapter checkpoints
│
├── docs/                                 # Documentation & media assets
│   └── images/                           # Dashboard & feature screenshots
│
├── telecom_explanation.txt               # In-depth architectural & data-flow whitepaper
├── requirements.txt                      # Python dependencies
├── .env                                  # API keys & environment variables
└── README.md                             # Main documentation
```

---

## 🧩 Core Components

### 1. Data Ingestion & Knowledge Base (`src/ingestion/`)
- **MultiDoc2Dial Layer**: 24,933 passages across 488 documents grounding customer service interactions.
- **Telecom Overlay Layer**: 1,171 passages across 10 documents representing Indian carriers (Jio, Airtel, Vi, BSNL) and TRAI regulations across 6 domain categories (`billing`, `plans`, `network`, `device`, `account`, `roaming`).
- Output files: `kb_passages.jsonl` (26,104 vector index records), `span_index.json` (span-level lookup), and `doc_index.json` (document metadata).

### 2. Dense Retriever & Vector Indexing (`src/retrieval/`)
- **Model**: `BAAI/bge-large-en-v1.5` fine-tuned with Multiple Negatives Ranking Loss (MNRL).
- **Indexing**: FAISS `IndexFlatIP` over normalized 1024-d embeddings ensuring exact inner product cosine search across 26,000+ passages.

### 3. Cross-Encoder Reranker (`src/retrieval/reranker.py`)
- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Pipeline Role**: Reranks top-20 dense retrieval candidates down to the top-3 most contextual passages before handing them to the generator.

### 4. Tool Policy Classifier (`src/policy/tool_policy_classifier.py`)
- Fine-tuned BERT model (`bert-base-uncased`) that classifies user queries into tool routing actions:
  - Label 0: `SearchKB`
  - Label 1: `GetPolicy`
  - Label 2: `CreateTicket`
  - Label 3: `CheckNetworkStatus`

### 5. Executable Tool Engine (`src/tools/tool_executor.py`)
- `SearchKB`: Performs dense retrieval and cross-encoder reranking over the corpus.
- `GetPolicy`: Rapid span-based document lookup for precise legal/regulatory clauses.
- `CreateTicket`: Confidence-based customer complaint escalation logging to `tickets.jsonl`.
- `CheckNetworkStatus`: Simulated live telecom network feed returning active outages and compensation eligibility.

### 6. Dual Generator Engine (`src/generation/`)
- **Local DoRA Flan-T5**: Parameter-efficient fine-tuning on `google/flan-t5-base` using Weight-Decomposed Low-Rank Adaptation (rank 16, alpha 32) to generate structured citations (`[SOURCE: doc_id, section_id]`).
- **Cloud LLM (OpenRouter)**: High-capability inference engine utilizing NVIDIA Nemotron 3 Super 120B (`nvidia/nemotron-3-super-120b-a12b:free`) with automated exponential backoff retry.

---

## 📊 Dataset & Knowledge Base

### Corpus Statistics (`data/processed/dataset_stats.json`)

| Metric | Count |
|--------|-------|
| **Total Passages** | **26,104** |
| MultiDoc2Dial Passages | 24,933 |
| Telecom Overlay Passages | 1,171 |
| **Total Documents** | **498** |
| MultiDoc2Dial Documents | 488 |
| Telecom Overlay Documents | 10 |
| **Total Words in Corpus** | **407,938** |

### Datasets Created During Pipeline Run

| File | Purpose | Source / Method |
|------|---------|-----------------|
| `retriever_train.jsonl` | Dense retriever training triples `(query, pos, neg)` | Merged MD2D + BM25-mined Telecom overlay |
| `generator_sft_train.jsonl` | Generator SFT training pairs `(context+query, answer)` | Grounded MultiDoc2Dial agent dialogues |
| `dpo_pairs.jsonl` | Direct Preference Optimization pairs | MultiDoc2Dial + Stanford Human Preferences (SHP-2) |
| `test_cases.jsonl` | Comprehensive evaluation set | Validation split + Telecom evaluation queries |

---

## 🔁 Training & Ingestion Pipeline

To run the complete data processing and training pipeline from scratch:

```bash
# 1. Build Telecom Corpus & Expand Passages
python -m src.ingestion.telecom_corpus_builder_expanded

# 2. Build Unified Knowledge Base
python -m src.ingestion.kb_builder

# 3. Construct Training Datasets (Retriever, Generator SFT, DPO)
python -m src.ingestion.training_data_builder

# 4. Fine-Tune Dense Retriever (BGE-Large)
python -m src.retrieval.train_retriever

# 5. Build FAISS Vector Index
python -m src.retrieval.faiss_indexer --model checkpoints/retriever

# 6. Fine-Tune Cross-Encoder Reranker
python -m src.retrieval.reranker --train

# 7. Fine-Tune DoRA Generator (Flan-T5)
python -m src.generation.train_generator

# 8. Train Tool Policy Classifier
python -m src.policy.tool_policy_classifier --train
```

---

## 🤖 Inference Pipeline (ReAct Control Loop)

The inference pipeline (`src/pipeline/inference_pipeline.py`) executes a multi-step control loop:

1. **Intent Classification**: Query is sent to the Tool Policy Classifier to decide required tool calls.
2. **Tool Execution Loop**: Runs `SearchKB`, `CheckNetworkStatus`, or `GetPolicy` to gather evidence.
3. **Escalation Assessment**: If retrieval confidence falls below threshold, automatically triggers `CreateTicket`.
4. **Context Prompting & Generation**: Assembles context and query into structured prompt template and invokes the generator.
5. **Citation Post-Processing**: Extracts source tags `[SOURCE: doc_id, section_id]` and formats final answer payload.

---

## 📐 Evaluation Harness & Metrics

Evaluation is performed using `src/evaluation/evaluator.py`, comparing outputs on `test_cases.jsonl`.

### Metric Definitions

1. **Citation Recall@1**: Validates whether the gold target document ID is present in the output citation list.
2. **Answer Coverage Score**: Measures token-level ROUGE-1 recall of key content words against reference gold answers.
3. **Grounded Escalation Accuracy (GEA)**: Custom metric measuring correct ticket escalation decisions on ambiguous or ungrounded queries.
4. **Outage-Aware Response Rate (OARR)**: Custom metric verifying that active network outages trigger proactive status notices and compensation info.

### System Benchmark Summary (`full_system_results.eval.json`)

| Evaluation Metric | Full System Score |
|-------------------|-------------------|
| **Grounded Escalation Accuracy (GEA)** | **91.71%** |
| **Outage-Aware Response Rate (OARR)** | **100.0%** |
| **BERTScore F1** | **0.8107** |
| **Evaluated Test Queries** | 205 cases |

To re-run evaluation:
```bash
python -m src.evaluation.evaluator --results data/processed/full_system_results.jsonl
```

---

## ⚙️ Installation & Setup Guide

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+ & npm 9+
- CUDA GPU (Optional; CPU execution supported)
- [OpenRouter API key](https://openrouter.ai) (for cloud generator fallback)

### Step 1: Clone Repository & Python Virtual Environment

```bash
git clone https://github.com/sahil-vasani/Telecom-copilot.git
cd Telecom-copilot

# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.venv\Scripts\activate

# Activate environment (Linux/macOS)
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API=https://openrouter.ai/api/v1/chat/completions
HF_HOME=./huggingface_cache
```

### Step 3: Frontend Dashboard Setup

```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Usage Guide

### 1. Interactive Python CLI Demo
Run an interactive session in your terminal:
```bash
python -m src.pipeline.inference_pipeline --demo
```

### 2. Python API Usage
```python
from src.pipeline.inference_pipeline import run_inference

response = run_inference(
    query="How do I dispute an incorrect charge on my Airtel bill?",
    history=[]
)

print("Answer:", response["answer"])
print("Citations:", response["citations"])
print("Tools Called:", response["tools_called"])
```

### 3. Launching the React Operations Dashboard
Start the Vite development server for the web interface:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 🔧 Configuration

Key system parameters can be configured in their respective module files:

| Parameter | Default Value | Location |
|-----------|---------------|----------|
| Retriever Base Model | `BAAI/bge-large-en-v1.5` | `train_retriever.py` |
| Vector Index Type | `IndexFlatIP` (Cosine) | `faiss_indexer.py` |
| Reranker Model | `cross-encoder/ms-marco-MiniLM-L-6-v2` | `reranker.py` |
| Generator Model (Local) | `google/flan-t5-base` | `train_generator.py` |
| Generator Rank / Alpha (DoRA) | Rank 16, Alpha 32 | `train_generator.py` |
| Cloud Generator Model | `nvidia/nemotron-3-super-120b-a12b:free` | `openrouter_generator.py` |
| FAISS Top-K Retrieve | 20 candidates | `inference_pipeline.py` |
| Reranker Top-K Output | 3 candidates | `inference_pipeline.py` |

---

## 🧠 Design Decisions

- **Why DoRA over standard LoRA?**: Weight-Decomposed Low-Rank Adaptation (DoRA) decouples magnitude and direction of weight updates, outperforming LoRA by +0.5–2.0% at identical ranks on structured text output tasks.
- **Why FAISS `IndexFlatIP`?**: Vector normalization combined with Inner Product (`IP`) yields exact cosine similarity search. Given the 26,000+ passage corpus size, exact search executes in milliseconds without requiring lossy quantization (`IVFFlat` or `HNSW`).
- **Why MultiDoc2Dial as Grounding Base?**: MultiDoc2Dial provides thousands of turn-by-turn dialogue interactions paired with explicit document span groundings, giving the dense retriever and cross-encoder a high-quality supervision signal.
- **Why Novel Metrics (GEA & OARR)?**: Standard NLP metrics (BLEU/ROUGE) fail to capture domain-specific telecom requirements such as knowing when to escalate unanswerable queries to human agents or detecting active regional outages.

---

## 🗺 Roadmap & Acknowledgements

### Roadmap
- [ ] Implement DPO fine-tuning using `dpo_pairs.jsonl` for preference optimization.
- [ ] Add FastAPI server endpoints to connect React frontend directly to Python backend pipeline.
- [ ] Support multilingual queries across major Indian languages (Hindi, Tamil, Telugu, Marathi).
- [ ] Expand FAISS index to `IndexIVFFlat` for large-scale enterprise deployments (>1M passages).

### Acknowledgements
- [MultiDoc2Dial](https://github.com/IBM/multidoc2dial) for document-grounded dialogue data.
- [BAAI BGE Models](https://huggingface.co/BAAI/bge-large-en-v1.5) for text embeddings.
- [DoRA Paper (Liu et al., ICML 2024)](https://arxiv.org/abs/2402.09353) for PEFT methodology.
- [HuggingFace Transformers](https://huggingface.co/) & [FAISS](https://github.com/facebookresearch/faiss).

---

<p align="center">
  Built with ❤️ for Indian Telecom Customers · Powered by Open-Source NLP & Agentic AI
</p>