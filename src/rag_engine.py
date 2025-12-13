import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from . import config, utils

class RAGEngine:
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.7
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )
        
        # Load Vector Store
        try:
            self.vectorstore = FAISS.load_local(
                config.INDEX_PATH, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Index not found or error loading: {e}. Please run ingestion first.")
            self.vectorstore = None

        # Helper for reranking (Lazy load if needed, but initializing here)
        # Using a standard lightweight cross-encoder
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def initial_retrieval(self, query, top_k=3):
        """Hop 1: Rough retrieval."""
        if not self.vectorstore:
            return []
        
        docs = self.vectorstore.similarity_search(query, k=top_k)
        return docs

    def reformulate_query(self, original_query, context_docs):
        """Uses LLM to reformulate query based on retrieved docs."""
        if not context_docs:
            return original_query
            
        context_text = utils.format_docs_with_metadata(context_docs)
        
        template = """
Role: Ahli Hukum Senior.
Tugas: Reformulasi pertanyaan awam menjadi QUERY PENCARIAN HUKUM baku.

Konteks Awal (Perhatikan istilah hukum dalam Judul & Tags):
{context_text}

Pertanyaan User: {original_query}

Output: Query baku saja.
"""
        prompt = PromptTemplate(
            input_variables=["context_text", "original_query"],
            template=template
        )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context_text": context_text,
            "original_query": original_query
        })
        return response.content.strip()

    def final_retrieval_and_rerank(self, formulated_query, top_k_initial=10, top_k_final=5):
        """Hop 2: Retrieve with new query and Rerank."""
        if not self.vectorstore:
            return []

        # 1. Retrieve more clips
        docs = self.vectorstore.similarity_search(formulated_query, k=top_k_initial)
        
        if not docs:
            return []

        # 2. Rerank
        # Pairs for cross-encoder: [[query, doc_text], ...]
        doc_texts = [d.page_content for d in docs]
        pairs = [[formulated_query, text] for text in doc_texts]
        
        scores = self.reranker.predict(pairs)
        
        # Combine docs with scores
        doc_score_pairs = list(zip(docs, scores))
        
        # Sort by score descending
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k_final
        return [p[0] for p in doc_score_pairs[:top_k_final]]

    def generate_answer(self, query, final_docs):
        """Generates the final answer."""
        context_text = utils.format_docs_with_metadata(final_docs)
        
        template = """
Role: Asisten Hukum AI.
Instruksi: Jawab pertanyaan user berdasarkan referensi berikut.

ATURAN PENTING:
1. Perhatikan [TANGGAL TERBIT]. Jika ada dua aturan yang bertentangan, prioritaskan yang lebih baru.
2. Sebutkan Dasar Hukum (Pasal/UU) yang tercantum dalam konten.
3. Gunakan [TAGS] dan [KATEGORI] untuk memahami konteks spesifik (Pidana/Perdata/Acara).

Dokumen Referensi:
{context_text}

Pertanyaan: {query}
"""
        prompt = PromptTemplate(
            input_variables=["context_text", "query"],
            template=template
        )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context_text": context_text,
            "query": query
        })
        return response.content

    def process_query(self, user_query):
        """Pipeline execution."""
        # 1. Hop 1
        print("--- Hop 1: Initial Retrieval ---")
        initial_docs = self.initial_retrieval(user_query)
        
        # 2. Reformulate
        print("--- Reformulating Query ---")
        new_query = self.reformulate_query(user_query, initial_docs)
        print(f"Reformulated Query: {new_query}")
        
        # 3. Hop 2 & Rerank
        print("--- Hop 2: Final Retrieval & Rerank ---")
        final_docs = self.final_retrieval_and_rerank(new_query)
        
        # 4. Generate
        print("--- Generating Answer ---")
        answer = self.generate_answer(user_query, final_docs)
        
        return {
            "reformulated_query": new_query,
            "final_docs": final_docs,
            "answer": answer
        }
