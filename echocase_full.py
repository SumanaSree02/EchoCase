import faiss
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# Load FAISS index
index = faiss.read_index("echo_case_faiss.index")

# Load stored complaint texts
with open("echo_case_texts.pkl", "rb") as f:
    texts = pickle.load(f)

# Load embedding model
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


def generate_full_analysis(user_complaint, retrieved_cases):
    context = ""

    for case in retrieved_cases:
        context += f"\nSimilar Case {case['rank']}:\n"
        context += case["case_text"]
        context += f"\nSimilarity Distance: {case['distance']}\n"

    prompt = f"""
You are EchoCase, a RAG-based Financial Complaint Intelligence Assistant.

User Complaint:
{user_complaint}

Retrieved Similar Historical Complaints:
{context}

Analyze the complaint using the user complaint and the retrieved historical cases.

Generate output in this exact format:

1. Complaint Category:
Identify the financial complaint category.

2. Main Issue Identified:
Explain the main problem in one or two lines.

3. Risk Level:
Choose only HIGH, MEDIUM, or LOW.
Explain the reason clearly.

Risk Rules:
HIGH = identity theft, fraud, unauthorized account, scam, serious credit damage.
MEDIUM = debt collection dispute, incorrect credit report, loan/mortgage issue, payment dispute.
LOW = general service issue or low financial impact.

4. Similar Case Pattern:
Explain what pattern is seen in the retrieved complaints.

5. Complaint Strength Score:
Give a score out of 100.
Mention what makes the complaint strong and what is missing.

6. Evidence Checklist:
List the documents or proof the user should collect.

7. Consumer Guidance:
Give practical guidance in simple language.

8. Suggested Next Steps:
Give step-by-step actions.

9. Draft Complaint Statement:
Write a professional complaint statement the user can submit.

Rules:
- Do not claim legal certainty.
- Do not say you are a lawyer.
- Keep the answer practical and professional.
- Use retrieved cases as supporting context.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are EchoCase, a professional financial complaint intelligence assistant."
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

answer = generate_full_analysis(
    user_complaint,
    similar_cases
)

print("\nEchoCase Full AI Analysis:\n")
print(answer)