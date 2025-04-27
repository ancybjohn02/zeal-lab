# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import json
import uvicorn
import re
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


# Load your knowledge base
with open('enhanced_knowledge_base.json') as f:
    kb = json.load(f)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with a list of allowed domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

class QueryRequest(BaseModel):
    question: str

def simple_parser(question):
    # Lowercase question
    q = question.lower()
    
    # Try to find store id (like NYC-001)
    store_match = re.search(r'\b([A-Z]{2,3}-\d{3})\b', question)
    store = store_match.group(1) if store_match else None
    
    # Try to find region (NYC, LA, etc.)
    regions = ['NYC', 'LA', 'CHI', 'HOU', 'SF']
    region = next((r for r in regions if r.lower() in q), None)

    # Try to find category
    categories = ['grocery', 'furniture', 'electronics', 'clothing', 'beverages']
    category = next((c for c in categories if c in q), None)
    
    # Try to guess intent
    if 'stock' in q:
        intent = 'stock'
    elif 'rate' in q or 'pricing' in q:
        intent = 'rate'
    elif 'comment' in q or 'performance' in q:
        intent = 'comment'
    elif 'suggestion' in q or 'advise' in q:
        intent = 'suggestion'
    else:
        intent = 'general'
    
    return {
        'store': store,
        'region': region,
        'category': category,
        'intent': intent
    }

def find_answer(parsed_query):
    store = parsed_query['store']
    region = parsed_query['region']
    category = parsed_query['category']
    intent = parsed_query['intent']
    
    # Fallback if store not specified
    if not store:
        if region:
            stores = kb['regions'][region]['stores']
            store = stores[0]  # Pick first store in region if needed
        else:
            return "Could you please specify a store or region?"
    
    store_data = kb.get(store)
    if not store_data:
        return f"I couldn't find data for store {store}."
    
    if category:
        cat_data = store_data['categories'].get(category)
        if not cat_data:
            return f"I couldn't find the {category} category in {store}."

        if intent == 'stock':
            return f"The total stock for {category} in {store} is {cat_data['total_stock']} units."
        elif intent == 'rate':
            return f"The average product rate for {category} in {store} is {cat_data['avg_product_rate']}."
        elif intent == 'comment':
            return f"Performance comment for {category} in {store}: {cat_data['comment']}"
        elif intent == 'suggestion':
            return f"Suggestion for {category} in {store}: {cat_data['suggestion']}"
        else:
            return cat_data['content']
    else:
        # Overall store level info
        if intent == 'stock':
            return f"The total stock for store {store} is {store_data['total_stock']}."
        elif intent == 'rate':
            return f"The average product rate for store {store} is {store_data['avg_product_rate']}."
        elif intent == 'comment':
            return f"Overall store performance: {store_data['performance_metrics']['overall_comment']}"
        elif intent == 'suggestion':
            restocks = store_data['performance_metrics']['restock_suggestions']
            if restocks:
                return f"Restock suggested for: {', '.join(restocks)}."
            else:
                return "No restock suggestions currently."
        else:
            return store_data['content']

@app.post("/ask")
def ask_question(req: QueryRequest):
    parsed_query = simple_parser(req.question)
    answer = find_answer(parsed_query)
    return {"answer": answer}

# Local run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
