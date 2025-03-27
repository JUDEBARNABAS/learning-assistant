from flask import Flask, render_template, request, jsonify

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static') # Important:  Specify the static folder

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Google API Key not found. Check your .env file.")
    exit()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Google API configured successfully.")
except Exception as e:
    print(f"Error configuring Google API: {e}")
    exit()

# Select the Gemini model
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Print available models (and comment out the line that was causing the error)
print("Available Gemini models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")


# --- Prompts ---
BASE_PROMPT = "You are a helpful learning assistant.  You should answer student questions clearly and concisely.  If the student seems stuck, offer a hint rather than giving the answer directly."
HINT_PROMPT = "The student is having trouble. Provide a single, helpful hint to guide them to the answer without giving it away. Frame the hint as a question or suggestion, not a direct answer."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    response = get_response(question)
    return jsonify({"response": response})


def get_response(question, hint_requested=False):
    """Gets a response from Gemini for a given question."""

    prompt = BASE_PROMPT + "\nStudent Question: " + question
    if hint_requested:
        prompt = HINT_PROMPT + "\nStudent Question: " + question

    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        return answer
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an error. Please try again."


@app.route("/hint", methods=["POST"])
def hint():
    question = request.form["question"]
    hint_response = get_response(question, hint_requested=True)
    return jsonify({"hint": hint_response})


if __name__ == "__main__":
    app.run(debug=True)