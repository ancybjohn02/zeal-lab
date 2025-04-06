from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# LLM model
model = OllamaLLM(model="llama3")

# Prompt
template = """
You are an expert in answering questions about ice creams from four different companies.
Use the provided reviews to give informative and honest answers.

Here are some relevant reviews:
{reviews}

Here's the question to answer:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model
