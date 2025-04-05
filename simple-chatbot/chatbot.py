from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Answer the ques. below
here's is the conversation history: {context}
Question : {question}
Answer : 
"""
model = OllamaLLM(model= "llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handle_conversation(): # only for terminal use
    context =""
    print("welcome, i'm zeal! type 'exit' to quit")
    while True: 
        user_input = input("You: ")
        if user_input.lower()=="exit":
            break
        result = chain.invoke({"context": context, "question":user_input})
        print("Zeal: ", result)
#  for conversation history
        context += f"\nUser : {user_input}\nZeal: {result}"

# result = model.invoke(input = "hello world")
if __name__ == "__main__":
    handle_conversation()