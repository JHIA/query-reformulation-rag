import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    # Warning or error logging could go here, but strictly raising might crash if just testing parts
    pass 

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Models
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_MODEL = "gemini-2.5-flash"

# Paths
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "kekayaan_intelektual_sample.json")
INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index")
