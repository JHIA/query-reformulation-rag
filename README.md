# Sistem RAG Hukum Indonesia dengan Query Reformulation (Double-Hop)

Proyek ini adalah implementasi sistem **Retrieval-Augmented Generation (RAG)** tingkat lanjut yang dirancang khusus untuk menjawab pertanyaan hukum Indonesia. Sistem ini menggunakan metode **"Double-Hop"** dan **Query Reformulation** untuk meningkatkan akurasi pencarian dokumen dan relevansi jawaban.

Saat ini didukung oleh **Qwen 3 32B (via Groq)** untuk kecepatan dan kecerdasan analisis, serta **Google Gemini-2.5-Flash** sebagai alternatif.

## 🚀 Fitur Utama & Pencapaian

1.  **Double-Hop Retrieval Logic**: Melakukan pencarian dua kali (Konteks Awal -> Reformulasi -> Pencarian Presisi).
2.  **Query Reformulation (Bahasa Awam -> Hukum)**: Menggunakan LLM untuk menerjemahkan pertanyaan pengguna seperti *"Bos potong gaji seenaknya"* menjadi kueri hukum standar.
    *   **Hasil Evaluasi**: Mencapai **100% Hit Rate** pada dataset pengujian bahasa sehari-hari.
3.  **Cross-Encoder Reranking**: Mengurutkan ulang dokumen untuk memastikan regulasi yang paling relevan muncul diposisi #1 (MRR Score: 0.900).
4.  **UI Interaktif**: Menggunakan **Streamlit** untuk antarmuka chat yang responsif.
5.  **Cloud Deployment**: Siap dideploy ke **Modal** untuk skalabilitas serverless.

## 🔄 Alur Kerja (End-to-End Flow)

1.  **Hop 1: Pencarian Awal (Context Gathering)**
    *   Sistem mencari dokumen kasar di Vector DB menggunakan pertanyaan asli.
2.  **Reasoning & Reformulation**
    *   **Qwen 3 32B** menganalisis hasil pencarian.
    *   Mereformulasi pertanyaan awam menjadi pertanyaan hukum baku.
3.  **Hop 2: Pencarian Presisi (Precision Search)**
    *   Sistem mencari ulang menggunakan *Query Reformulasi*.
    *   Dokumen di-rerank menggunakan model Cross-Encoder lokal.
4.  **Generation (Pembuatan Jawaban)**
    *   **Qwen 3 32B** menyusun jawaban berdasarkan dokumen hukum terpilih, menyertakan dasar hukum dan interpretasi.

## 🛠️ Teknologi yang Digunakan

*   **Language**: Python 3.10+
*   **LLM Utama**: **Qwen 3 32B** (via Groq API) - *Fast & Smart*
*   **LLM Alternatif**: **Gemini 2.5 Flash** (Google)
*   **Embedding**: Google Text-Embedding-004
*   **Vector Database**: FAISS (CPU)
*   **Frontend**: Streamlit
*   **Deployment**: Modal (Serverless)

## 📂 Struktur Proyek

```text
legal-rag-system/
├── data/
│   ├── hukumonline_sample.json      # Dataset artikel hukum
│   └── eval_datasets/               # Dataset evaluasi (generated)
├── src/
│   ├── config.py                    # Konfigurasi API
│   ├── ingestion.py                 # Indexing & Metadata
│   ├── rag_engine.py                # Core Logic (Reformulation + Rerank)
│   ├── generate_eval_data.py        # Generator Data Evaluasi (Layman Style)
│   └── evaluation.py                # Script Pengujian (Retrieval Only)
├── app.py                           # Frontend Streamlit
├── main.py                          # CLI Version
├── modal_app.py                     # Modal Deployment Config
└── requirements.txt                 # Dependensi Python
```

## 💻 Cara Menjalankan

### Prasyarat
*   Python 3.10+
*   API Key: **Groq API Key** (untuk Qwen) dan **Google API Key** (untuk Embedding).

### 1. Setup Lokal (Streamlit)
```powershell
# 1. Clone & Masuk Folder
git clone https://github.com/JHIA/query-reformulation-rag.git
cd query-reformulation-rag

# 2. Setup Venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install
pip install -r requirements.txt

# 4. Setup .env
# Buat file .env dan isi:
# GOOGLE_API_KEY=...
# GROQ_API_KEY=...
# LLM_PROVIDER=groq
# GROQ_MODEL=qwen/qwen-2.5-32b-instruct

# 5. Jalankan
streamlit run app.py
```

### 2. Deployment ke Modal (Serverless)
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

## 📊 Evaluasi Kinerja
Untuk menguji akurasi sistem terhadap pertanyaan bahasa sehari-hari:
```powershell
# 1. Generate Pertanyaan Awam (menggunakan Gemini)
python src/generate_eval_data.py

# 2. Jalankan Evaluasi Retrieval
python src/evaluation.py
```
*Target Metric: Hit Rate > 90% (Saat ini: 100%)*
