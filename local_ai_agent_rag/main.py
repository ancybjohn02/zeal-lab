from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3")

template = """
You are an expert in answering questions about ice creams of four differnt companies. Provide detailed and accurate responses to any queries related to ice creams.

here are some relevant reviews: {reviews}

here's the ques. to answer : {question}

"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n\n---------------------------------------------------")
    question = input("ask you question to the expert here, Zeal!! or q to quit : ")
    print("\n\n")
    if question == "q":
        break    
    reviews  = retriever.invoke(question)
    result = chain.invoke({"reviews": [], "question": "which is the best icecream?"})
    print(result)