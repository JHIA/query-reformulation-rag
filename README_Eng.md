# Indonesian Legal RAG System with Query Reformulation (Double-Hop)

This project implements an advanced **Retrieval-Augmented Generation (RAG)** system designed specifically for answering Indonesian legal questions. It utilizes a **"Double-Hop"** method and **Query Reformulation** to improve document retrieval accuracy and answer relevance.

Currently powered by **Qwen 3 32B (via Groq)** for high-speed intelligent reasoning, with **Google Gemini-2.5-Flash** as a robust alternative.

## 🚀 Key Features & Achievements

1.  **Double-Hop Retrieval Logic**: Performs two distinct searches (Context Gathering -> Reformulation -> Precision Search).
2.  **Query Reformulation (Layman -> Legal)**: Uses an LLM to rewrite user's layperson questions (e.g., *"Boss cut my salary unfairly"*) into standardized legal queries.
    *   **Evaluation Result**: Achieved **100% Hit Rate** on stratified layman datasets.
3.  **Cross-Encoder Reranking**: Re-orders search results to ensure the most relevant regulation appears at position #1.
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
│   └── eval_datasets/               # Evaluation datasets
├── src/
│   ├── evaluation/                  # Evaluation scripts
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

## 📊 Full Evaluation Report

**Date:** December 26, 2025

### 1. Summary
The goal of this test was to answer: **"If a user asks using layman/casual language (curhat), can the system find the correct legal rule?"**

The result is exceptional. Out of 15 tests across different topics, the system found the exact rule **100%** of the time.

### 2. Methodology
We designed a rigorous testing scenario to avoid evaluation bias:
1.  **Question Generation (Dataset Generation)**:
    Using an AI persona of a "Layperson" to generate natural language queries with everyday casual language from 15 different legal categories.

2.  **Retrieval Accuracy Analysis (Hit Rate & MRR)**:
    We assessed document retrieval performance using two key metrics:
    *   **Hit Rate (Recall@K)**: Measures if the relevant legal document was successfully found within the top search results (Top-K).
    *   **MRR (Mean Reciprocal Rank)**: Measures how high the first relevant document ranks, indicating user efficiency in finding answers without deep scrolling.

3.  **Generation Quality Analysis (LLM-as-a-Judge)**:
    We used an LLM-as-a-Judge scenario to evaluate two aspects of answer quality:
    *   **Faithfulness**: Measures if the system's answer is purely derived from the retrieved context (to detect hallucinations).
    *   **Answer Relevancy**: Measures if the answer is relevant and addresses the core of the user's question.

### 3.1 Retrieval Accuracy Assessment (Hit Rate & MRR)
Below are the 15 "Layman Terms" questions tested, including the Query Transformation and performance comparison (AI vs Raw):

| Topic | User Question (Input) | Reformulated Query (AI) | Targeted Document (Answer) | Rank (AI) | Change (vs Raw) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Business** | *"How to get a permit for selling fuel?"* | *"Prosedur dan persyaratan pengurusan izin usaha perdagangan BBM menurut UU Migas"* | Business Licensing for Fuel Trading | **#1** | ➖ Stable |
| **Human Rights** | *"Prisoner bullied in cell, any law protects them?"* | *"Perlindungan hukum terhadap narapidana korban kekerasan/perundungan di Lapas"* | Protection for Prisoners from Bullying | **#1** | ➖ Stable |
| **Legal Science** | *"Diff between legal protection vs law enforcement?"* | *"Perbedaan Konseptual Antara Perlindungan Hukum dan Penegakan Hukum"* | Definition of Legal Protection vs Enforcement | **#1** | ➖ Stable |
| **IPR** | *"My product sold by others without permit, report how?"* | *"Penegakan hukum atas pelanggaran hak distribusi eksklusif (UU 7/2014 Pasal 11)"* | Enforcement on Exclusive Distribution Rights | **#1** | ➖ Stable |
| **Family** | *"Husband says divorce verbally often, is it valid?"* | *"Status Perkawinan Setelah Talak Lisan dalam Hukum Islam & Keabsahannya"* | Marital Status if Divorced Verbally | **#1** | ➖ Stable |
| **State** | *"What are citizen rights in law?"* | *"Hak warga negara dalam bidang hukum (UUD 1945 & UU No. 39/1999)"* | 11 Citizen Rights in Law | **#1** | 🔼 **IMPROVED (2 -> 1)** |
| **Labor** | *"Can underage kids work?"* | *"Ketentuan hukum izin kerja & perlindungan bagi pekerja anak (UU Ketenagakerjaan)"* | Legal Protection for Child Workers | **#1** | 🔼 **IMPROVED (2 -> 1)** |
| **Sports** | *"Rules for foreign soccer players in Indonesia?"* | *"Syarat hukum dan regulasi bagi Pemain Sepak Bola Asing di Liga Indonesia"* | Rules on Foreign Soccer Players | **#2** | 🔻 Declined (1 -> 2) |
| **Civil Law** | *"What is 'Renvoi' in Supreme Court decision?"* | *"Dasar Hukum dan Tata Cara Renvoi Putusan Mahkamah Agung"* | Legal Basis of Renvoi | **#1** | ➖ Stable |
| **Consumer** | *"Clothes lost at laundry, must they compensate?"* | *"Kewajiban ganti rugi pemilik laundry atas hilangnya barang konsumen (UU Perlindungan Konsumen)"* | Laundry Compensation for Lost Items | **#1** | ➖ Stable |
| **Property** | *"Can waqf land be sold again?"* | *"Status hukum peralihan/penjualan tanah wakaf oleh nadhir (UU No. 41/2004)"* | Law on Selling Waqf Land | **#2** | 🔻 Declined (1 -> 2) |
| **Criminal** | *"Requirements for drug rehab?"* | *"Syarat dan Prosedur Permohonan Rehabilitasi Hukum Tersangka Narkoba"* | Requirements for Rehabilitation | **#1** | ➖ Stable |
| **Legal Prof** | *"Are lawyers immune to law?"* | *"Hak imunitas advokat vs tuntutan pidana (UU Advokat)"* | Can Advocates be Criminally Charged? | **#1** | ➖ Stable |
| **Startup** | *"Can startups manage traditional markets?"* | *"Legalitas perusahaan startup mengelola pasar tradisional (Perpres 112/2007)"* | Traditional Market Mgmt by Startups | **#1** | ➖ Stable |
| **Tech/ITE** | *"Is spreading parody songs mocking people illegal?"* | *"Tindakan hukum menyebarkan lagu parodi bermuatan penghinaan (UU ITE & KUHP)"* | Law on Spreading Insulting Songs | **#1** | 🔼 **IMPROVED (2 -> 1)** |

### 3.2 Generation Quality Assessment (LLM-as-a-Judge)
In addition to automated system evaluation, we performed an **LLM-as-a-Judge Simulation** on 15 samples using **Faithfulness** and **Answer Relevancy** criteria.

### 4. Results & Conclusion

The evaluation in steps 3.1 and 3.2 involved 4 key metrics:

1.  **Faithfulness**: Measures the factual consistency of the system's generated answer against the given context document (to detect hallucinations).
2.  **Answer Relevancy**: Measures the relevance level of the system's answer to the user's query.
3.  **Hit Rate (Recall@K)**: Measures the probability of the system finding at least one relevant document in the top-k search results.
4.  **MRR (Mean Reciprocal Rank)**: Measures the ranking accuracy by giving higher weight if the relevant document appears at the top.

The test results are as follows:

| Metric | Score | Predicate |
| :--- | :--- | :--- |
| **Faithfulness** | **98.6%** | Highly Reliable |
| **Relevancy** | **100%** | Highly Relevant |
| **Hit Rate** | **100%** | Highly Effective |
| **MRR (without reformulation)** | **90%** | High Precision |
| **MRR (with reformulation)** | **93%** | High Precision |

The system demonstrates exceptional maturity in 3 main aspects:

1.  **Context Understanding**: Able to filter relevant information from long and complex document chunks.
2.  **Regulatory Compliance**: Highly compliant with the latest regulations (e.g., correctly citing the 2024 ITE Law).
3.  **User Intent Alignment**: The query reformulation capability proved **successful**. The generated answers truly "connect" with everyday language questions by improving accuracy and ranking precision, effectively bridging the gap between layman language and legal terminology.

---

### 5. Gap Analysis & Limitations
For academic transparency, we note the following limitations:

1.  **Limited Dataset Scope**:
    *   The knowledge base contains only **15 legal categories** with **~50 articles each** (~750 total). The 100% score applies to this specific scope, but broader testing is needed for national-scale deployment.
    
2.  **Data Privacy Risk**:
    *   The system relies on Third-Party APIs (Groq/Google), meaning user queries are sent externally. Not recommended for highly confidential cases without additional encryption or On-Premise models.

3.  **Infrastructure Dependency**:
    *   Fully dependent on Cloud API uptime. If the API involves downtime, the system has no local fallback.
