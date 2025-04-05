# app.py
from flask import Flask, render_template, request, jsonify
from chatbot import chain  # importing the chain object
import chatbot  # to access and maintain context

app = Flask(__name__)
context = ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global context
    user_input = request.json["message"]
    result = chain.invoke({"context": context, "question": user_input})
    context += f"\nUser : {user_input}\nZeal: {result}"
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
