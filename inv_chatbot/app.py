from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import numpy as np
import faiss
import json
import os
import httpx
import logging
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI()

# Add middleware for CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (like HTML, CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

# Load the knowledge base
json_path = os.path.join(os.path.dirname(__file__), "enhanced_knowledge_base.json")
with open(json_path, "r") as file:
    knowledge_base = json.load(file)

# Preprocess documents
documents = []
for store_id, store_data in knowledge_base.items():
    if store_id == "regions":
        continue
    documents.append({
        "store_id": store_id,
        "content": f"Summary for {store_id}: Total stock: {store_data['total_stock']}, "
                   f"Avg product rate: {store_data['avg_product_rate']}, Total rate: {store_data['total_rate']}"
    })
    for category, cat_data in store_data["categories"].items():
        documents.append({
            "store_id": store_id,
            "category": category,
            "content": f"Category {category} in {store_id}: Total stock: {cat_data['total_stock']}, "
                       f"Avg rate: {cat_data['avg_product_rate']}, Total rate: {cat_data['total_rate']}. "
                       f"Comment: {cat_data.get('comment', '')} Suggestion: {cat_data.get('suggestion', '')}"
        })

# Load or generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings_path = "doc_embeddings.npy"

if not os.path.exists(embeddings_path):
    print("Generating embeddings...")
    doc_texts = [doc["content"] for doc in documents]
    doc_embeddings = model.encode(doc_texts, convert_to_numpy=True)
    np.save(embeddings_path, doc_embeddings)
else:
    print("Loading embeddings from file...")
    doc_embeddings = np.load(embeddings_path)

# Set up FAISS
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

# Helper: Retrieve top-k relevant documents
def retrieve_documents(query, top_k=3):
    query_vec = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)
    return [documents[i] for i in indices[0]]

# Helper: Ask Ollama
async def ask_ollama_async(query: str, context: str, model_name="llama3") -> str:
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": context + "\n\nQuestion: " + query,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]

@app.get("/")
async def root():
    # Render the HTML directly as a response
    with open("static/index.html", "r") as file:
        return HTMLResponse(file.read())

@app.post("/chat")
async def chat(request: QueryRequest):
    user_query = request.query
    logging.info(f"Received query: {user_query}")  # This will log the query
    retrieved_docs = retrieve_documents(user_query)
    context = " ".join([doc["content"] for doc in retrieved_docs])
    response = await ask_ollama_async(user_query, context)
    logging.info(f"Response: {response}")  # This will log the response
    return {
        "query": user_query,
        "response": response,
        "documents_used": [doc["content"] for doc in retrieved_docs]
    }
