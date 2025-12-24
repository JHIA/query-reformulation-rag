# Indonesian Legal RAG System with Query Reformulation (Double-Hop)

This project implements an advanced **Retrieval-Augmented Generation (RAG)** system designed specifically for answering Indonesian legal questions. It utilizes a **"Double-Hop"** method and **Query Reformulation** to improve document retrieval accuracy and answer relevance.

Currently powered by **Qwen 3 32B (via Groq)** for high-speed intelligent reasoning, with **Google Gemini-2.5-Flash** as a robust alternative.

## 🚀 Key Features & Achievements

1.  **Double-Hop Retrieval Logic**: Performs two distinct searches (Context Gathering -> Reformulation -> Precision Search).
2.  **Query Reformulation (Layman -> Legal)**: Uses an LLM to rewrite user's layperson questions (e.g., *"Boss cut my salary unfairly"*) into standardized legal queries.
    *   **Evaluation Result**: Achieved **100% Hit Rate** on stratified layman datasets.
3.  **Cross-Encoder Reranking**: Re-orders search results to ensure the most relevant regulation appears at position #1 (MRR Score: 0.900).
4.  **Interactive UI**: Built with **Streamlit** for a responsive chat experience.
5.  **Cloud Deployment**: Ready for **Modal** serverless deployment.

## 🔄 End-to-End Flow

1.  **Hop 1: Initial Retrieval (Context Gathering)**
    *   Rough search in Vector DB using the raw user query.
2.  **Reasoning & Reformulation**
    *   **Qwen 3 32B** analyzes the context.
    *   Reformulates the layman question into a formal legal query.
3.  **Hop 2: Precision Search**
    *   System searches again using the *Reformulated Query*.
    *   Results are reranked using a local Cross-Encoder model.
4.  **Generation**
    *   **Qwen 3 32B** generates the final answer based on the selected legal documents, citing specific articles and laws.

## 🛠️ Tech Stack

*   **Language**: Python 3.10+
*   **Primary LLM**: **Qwen 3 32B** (via Groq API) - *Fast & Smart*
*   **Alternative LLM**: **Gemini 2.5 Flash** (Google)
*   **Embedding**: Google Text-Embedding-004
*   **Vector Database**: FAISS (CPU)
*   **Frontend**: Streamlit
*   **Deployment**: Modal (Serverless)

## 📂 Project Structure

```text
legal-rag-system/
├── data/
│   ├── hukumonline_sample.json      # Legal dataset
│   └── eval_datasets/               # Evaluation datasets (generated)
├── src/
│   ├── config.py                    # API Configuration
│   ├── ingestion.py                 # Indexing & Metadata Extraction
│   ├── rag_engine.py                # Core Logic (Reformulation + Rerank)
│   ├── generate_eval_data.py        # Evaluation Data Generator (Layman Style)
│   └── evaluation.py                # Evaluation Script (Retrieval Only)
├── app.py                           # Streamlit Frontend
├── main.py                          # CLI Version
├── modal_app.py                     # Modal Deployment Config
└── requirements.txt                 # Python Dependencies
```

## 💻 How to Run

### Prerequisites
*   Python 3.10+
*   API Keys: **Groq API Key** (for Qwen) and **Google API Key** (for Embedding).

### 1. Local Setup (Streamlit)
```powershell
# 1. Clone & Enter Directory
git clone https://github.com/JHIA/query-reformulation-rag.git
cd query-reformulation-rag

# 2. Setup Venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Setup .env
# Create .env file and add:
# GOOGLE_API_KEY=...
# GROQ_API_KEY=...
# LLM_PROVIDER=groq
# GROQ_MODEL=qwen/qwen-2.5-32b-instruct

# 5. Run App
streamlit run app.py
```

### 2. Deployment to Modal (Serverless)
```powershell
# 1. Setup Modal
pip install modal
modal setup

# 2. Upload Volume (Index FAISS)
modal volume create rag-storage
modal volume put -f rag-storage faiss_index data/faiss_index

# 3. Deploy
modal deploy modal_app.py
```

## 📊 Performance Evaluation
To test the system's accuracy against layman questions:
```powershell
# 1. Generate Layman Questions (using Gemini)
python src/generate_eval_data.py

# 2. Run Retrieval Evaluation
python src/evaluation.py
```
*Target Metric: Hit Rate > 90% (Current: 100%)*
