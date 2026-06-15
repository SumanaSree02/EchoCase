import faiss
import pickle
from sentence_transformers import SentenceTransformer

index = faiss.read_index("echo_case_faiss.index")

with open("echo_case_texts.pkl", "rb") as f:
    texts = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_similar_cases(query, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)

    results = []

    for rank, idx in enumerate(indices[0], start=1):
        results.append({
            "rank": rank,
            "case_text": texts[idx],
            "distance": float(distances[0][rank - 1])
        })

    return results

query = input("Enter your complaint: ")

similar_cases = retrieve_similar_cases(query)

print("\nTop Similar Complaints:\n")

for case in similar_cases:
    print(f"\n--- Similar Case {case['rank']} ---")
    print(case["case_text"][:1000])
    print("Similarity Distance:", case["distance"])