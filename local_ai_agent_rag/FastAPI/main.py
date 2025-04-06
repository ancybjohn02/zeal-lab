from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_chain import chain, retriever  # Your custom logic

app = FastAPI()

# Mount static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates
templates = Jinja2Templates(directory="templates")

# Pydantic model to parse incoming JSON request
class QuestionRequest(BaseModel):
    question: str

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat endpoint that processes the question and returns JSON
@app.post("/chat")
async def chat(data: QuestionRequest):
    question = data.question
    reviews = retriever.invoke(question)
    review_texts = [doc.page_content for doc in reviews]
    result = chain.invoke({"reviews": "\n".join(review_texts), "question": question})
    return JSONResponse(content={"response": result})
