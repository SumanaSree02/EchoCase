import faiss
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
load_dotenv()
# Add your Groq API key here

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

index = faiss.read_index("echo_case_faiss.index")

with open("echo_case_texts.pkl", "rb") as f:
    texts = pickle.load(f)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_similar_cases(query, top_k=5):
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    retrieved_cases = []

    for rank, idx in enumerate(indices[0], start=1):
        retrieved_cases.append({
            "rank": rank,
            "case_text": texts[idx][:1200],
            "distance": float(distances[0][rank - 1])
        })

    return retrieved_cases


def generate_answer(user_complaint, retrieved_cases):
    context = ""

    for case in retrieved_cases:
        context += f"\nSimilar Case {case['rank']}:\n"
        context += case["case_text"]
        context += f"\nSimilarity Distance: {case['distance']}\n"

    prompt = f"""
You are EchoCase, a RAG-based financial complaint intelligence assistant.

User Complaint:
{user_complaint}

Similar Historical Complaints Retrieved:
{context}

Based only on the user's complaint and the retrieved similar complaints, generate a helpful response.

Give output in this format:

1. Complaint Category
2. Main Issue Identified
3. Similar Case Pattern
4. Consumer Guidance
5. Evidence Checklist
6. Suggested Next Steps
7. Draft Complaint Statement

Rules:
- Keep the answer simple and professional.
- Do not claim legal certainty.
- Do not say "I am a lawyer".
- Use the retrieved complaints as supporting context.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are EchoCase, a helpful financial complaint intelligence assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


user_complaint = input("Enter your complaint: ")

similar_cases = retrieve_similar_cases(user_complaint)

answer = generate_answer(user_complaint, similar_cases)

print("\nEchoCase AI Response:\n")
print(answer)