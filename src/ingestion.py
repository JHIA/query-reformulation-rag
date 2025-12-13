import json
import os
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from . import config

def load_data():
    """Loads data from JSON file and converts to Documents."""
    if not os.path.exists(config.DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {config.DATA_PATH}")
        
    with open(config.DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    docs = []
    for entry in data:
        # Extract metadata
        metadata = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "publish_date": entry.get("publish_date", ""),
            "tags": entry.get("tags", []),
            "theme": entry.get("theme", "")
        }
        content = entry.get("content", "")
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)
    return docs

def build_index():
    """Loads data, splits it, and builds a FAISS index."""
    print("Loading data...")
    raw_docs = load_data()
    
    print(f"Splitting {len(raw_docs)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(raw_docs)
    
    print("Initializing Embeddings...")
    if not config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY
    )
    
    print("Creating FAISS index...")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    print(f"Saving index to {config.INDEX_PATH}...")
    vectorstore.save_local(config.INDEX_PATH)
    print("Index built and saved successfully.")

if __name__ == "__main__":
    build_index()
