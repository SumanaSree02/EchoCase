import pandas as pd

df = pd.read_csv(
    "complaints.csv",
    low_memory=False
)

required_columns = [
    "Product",
    "Sub-product",
    "Issue",
    "Sub-issue",
    "Consumer complaint narrative",
    "Company public response",
    "Company",
    "Company response to consumer"
]

df = df[required_columns]

df = df.dropna(subset=["Consumer complaint narrative"])
df = df.sample(n=50000, random_state=42)

df["combined_text"] = (
    "Product: " + df["Product"].astype(str) +
    "\nSub Product: " + df["Sub-product"].astype(str) +
    "\nIssue: " + df["Issue"].astype(str) +
    "\nSub Issue: " + df["Sub-issue"].astype(str) +
    "\nCompany: " + df["Company"].astype(str) +
    "\nComplaint: " + df["Consumer complaint narrative"].astype(str) +
    "\nCompany Response: " + df["Company public response"].astype(str) +
    "\nFinal Response: " + df["Company response to consumer"].astype(str)
)

df.to_csv("rag_ready_data.csv", index=False)

print("RAG-ready dataset created successfully")
print("Final Shape:", df.shape)
print("\nSample Document:\n")
print(df["combined_text"].iloc[0])