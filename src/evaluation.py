import json
import os
import sys

# Setup path to run from root or src
current_dir = os.path.dirname(os.path.abspath(__file__))
# If running from inside src, parent is root
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.rag_engine import RAGEngine

def calculate_mrr(rank):
    """Calculate Mean Reciprocal Rank score (1/rank)."""
    if rank == 0:
        return 0
    return 1.0 / rank

def run_evaluation(data_path):
    print(f"Loading evaluation set from: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    engine = RAGEngine()
    
    total_questions = len(eval_data)
    hits = 0
    mrr_sum = 0
    
    print(f"\n--- Starting Evaluation on {total_questions} Questions ---\n")
    
    for item in eval_data:
        q = item['question']
        target_doc = item['expected_document_title'].lower()
        
        print(f"Query: {q}")
        
        # Run Pipeline (Only need retrieval part, but we run full to be safe or optimize later)
        # We can cheat and just call final_retrieval_and_rerank if we want speed,
        # but better to run process_query to test the REAL pipeline including reformulation.
        try:
            # STRATEGY: RETRIEVAL ONLY (Zero Groq Tokens)
            # We bypass process_query (Reformulation + Generation) to avoid 429 Errors.
            # This only tests: "If we search for X, do we find it?" (Hit Rate)
            
            # result = engine.process_query(q)
            # retrieved_docs = result['final_docs']
            
            # USE THIS FOR EVALUATION (Safe):
            retrieved_docs = engine.final_retrieval_and_rerank(q, top_k_initial=15, top_k_final=8)
            
            # Check for Hit
            found_rank = 0 # 0 means not found
            
            for rank, doc in enumerate(retrieved_docs, start=1):
                # Loose matching: check if target title keyword is in metadata title
                doc_title = doc.metadata.get('title', '').lower()
                doc_source = doc.metadata.get('source', '').lower()
                
                # Check match
                if target_doc in doc_title or target_doc in doc_source:
                    found_rank = rank
                    break
            
            if found_rank > 0:
                print(f"  [HIT] Found at Rank {found_rank}")
                hits += 1
                mrr_sum += calculate_mrr(found_rank)
            else:
                print(f"  [MISS] Correct Doc '{target_doc}' not in top {len(retrieved_docs)}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")

    # Final Stats
    hit_rate = (hits / total_questions) * 100
    mrr_score = mrr_sum / total_questions
    
    print("\n=== EVALUATION RESULTS ===")
    print(f"Total Questions: {total_questions}")
    print(f"Hit Rate: {hit_rate:.1f}%")
    print(f"MRR Score: {mrr_score:.3f}")
    print("===========================")

if __name__ == "__main__":
    generated_path = os.path.join(root_dir, 'data', 'eval_datasets', 'evaluation_dataset.json')
    
    if os.path.exists(generated_path):
        run_evaluation(generated_path)
    else:
        print(f"Dataset not found at: {generated_path}")
        print("Please run: python src/generate_eval_data.py")
