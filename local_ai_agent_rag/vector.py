#  vector search = db, it's hosted locally on our computer using ChromaDB
#  it help to quikly look up relevant info that we can then pass to our model

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("local_ai_agent/icecream/hd/reviews.csv")
embeddings = OllamaEmbeddings(model = "mxbai-embed-large")

db_location = "./chroma_langchain_db"
add_docs = not os.path.exists(db_location)

if add_docs: 
    docs = []
    ids = []
    for i,rows in df.iterrows():
        # Handle missing values in 'text' and 'title'
        text = rows["text"] if isinstance(rows["text"], str) else ""
        title = rows["title"] if isinstance(rows["title"], str) else ""
        
        doc = Document(
            page_content=text + " " + title,
            metadata = {"stars" : rows["stars"], "date": rows["date"], "taste" : rows["taste"]},
            id=str(i)
        )
        ids.append(str(i))
        docs.append(doc)

vector_store = Chroma(
    collection_name = "icecream_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_docs:
    vector_store.add_documents(documents==docs, ids=ids)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 10},
    search_type="similarity",
    search_score_type="cosine",
    search_distance_metric="cosine"
)