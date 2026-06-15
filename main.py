import os
import faiss
import pickle
import sqlite3
import hashlib
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return sqlite3.connect("echocase_users.db")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            complaint TEXT NOT NULL,
            analysis TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


init_auth_db()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

index = faiss.read_index("echo_case_faiss.index")

with open("echo_case_texts.pkl", "rb") as f:
    texts = pickle.load(f)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ComplaintRequest(BaseModel):
    complaint: str
    user_id: int | None = None


@app.get("/")
def home():
    return {
        "project": "EchoCase",
        "status": "Running"
    }


@app.post("/register")
def register(data: RegisterRequest):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (
                data.name,
                data.email,
                hash_password(data.password)
            )
        )

        conn.commit()

        return {
            "message": "Registration successful"
        }

    except sqlite3.IntegrityError:
        return {
            "error": "Email already registered"
        }

    finally:
        conn.close()


@app.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
        (
            data.email,
            hash_password(data.password)
        )
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "message": "Login successful",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        }

    return {
        "error": "Invalid email or password"
    }


@app.get("/history/{user_id}")
def get_history(user_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, complaint, analysis, created_at
        FROM complaint_history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "complaint": row[1],
            "analysis": row[2],
            "created_at": row[3]
        })

    return {
        "history": history
    }


def retrieve_similar_cases(query, top_k=5):
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for rank, idx in enumerate(indices[0], start=1):
        results.append({
            "rank": rank,
            "case_text": texts[idx][:1000],
            "distance": float(distances[0][rank - 1])
        })

    return results


def generate_full_analysis(user_complaint, retrieved_cases):
    context = ""

    for case in retrieved_cases:
        context += f"\nSimilar Case {case['rank']}:\n"
        context += case["case_text"]
        context += f"\nSimilarity Distance: {case['distance']}\n"

    prompt = f"""
You are EchoCase, a financial complaint intelligence assistant.

User Complaint:
{user_complaint}

Retrieved Similar Historical Complaints:
{context}

Generate output in this exact format:

1. Complaint Category:
2. Main Issue Identified:
3. Risk Level:
Choose HIGH, MEDIUM, or LOW and explain why.

4. Similar Case Pattern:
5. Complaint Strength Score:
Give score out of 100 and explain.
6. Evidence Checklist:
7. Consumer Guidance:
8. Suggested Next Steps:
9. Draft Complaint Statement:

Rules:
- Do not claim legal certainty.
- Keep the answer practical and professional.
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


@app.post("/analyze")
def analyze(data: ComplaintRequest):
    similar_cases = retrieve_similar_cases(data.complaint)

    analysis = generate_full_analysis(
        data.complaint,
        similar_cases
    )

    if data.user_id:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO complaint_history
            (user_id, complaint, analysis, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.user_id,
                data.complaint,
                analysis,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

    return {
        "complaint": data.complaint,
        "similar_cases": similar_cases,
        "analysis": analysis
    }