import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer

df = pd.read_csv("rag_ready_data.csv")

texts = df["combined_text"].astype(str).tolist()[:10000]

print("Total documents:", len(texts))

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Creating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, "echo_case_faiss.index")

with open("echo_case_texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("FAISS vector database created successfully")
print("Embedding shape:", embeddings.shape)