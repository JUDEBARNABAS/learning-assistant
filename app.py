from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')

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

# Print available models
print("Available Gemini models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")


# --- Prompts ---
SYSTEM_INSTRUCTIONS = """
You are Atim, a female AI educational assistant for students in Northern Uganda. 
Key characteristics:
- Speak primarily in English
- Offer support in Acholi when requested
- Provide patient, encouraging learning support
- Adapt to students with different learning needs
- Demonstrate cultural sensitivity to Acholi traditions

Your primary goals are to:
- Help students understand academic concepts
- Provide personalized learning guidance
- Promote inclusive education
- Maintain a friendly, supportive tone

When a student asks a question:
1. Understand the core learning objective
2. Break down complex concepts simply
3. Offer step-by-step explanations
4. Provide culturally relevant examples
5. Encourage student's learning journey
"""

BASE_PROMPT = SYSTEM_INSTRUCTIONS + "\nYou are ATIM, a helpful learning assistant from the Gender Tech Initiative. You should answer student questions clearly and concisely.  If the student seems stuck, offer a hint rather than giving the answer directly."
HINT_PROMPT = SYSTEM_INSTRUCTIONS + "\nThe student is having trouble. Provide a single, helpful hint to guide them to the answer without giving it away. Frame the hint as a question or suggestion, not a direct answer."

INITIAL_MESSAGE = "Hello! I'm Atim, your learning assistant from the Gender Tech Initiative. I'm here to help you with your studies. How can I help you today?"


@app.route("/")
def index():
    return render_template("index.html", initial_message=INITIAL_MESSAGE)


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    # Language selection (acholi)
    language = request.form.get("language", "english")  # Get the selected language, default is English
    response = get_response(question, language)
    return jsonify({"response": response})


def get_response(question, language="english", hint_requested=False):
    """Gets a response from Gemini for a given question."""

    prompt = BASE_PROMPT + f"\nThe student is asking in {language}. \nStudent Question: " + question
    if hint_requested:
        prompt = HINT_PROMPT + f"\nThe student is asking in {language}.\nStudent Question: " + question

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
    # Language selection (acholi)
    language = request.form.get("language", "english")  # Get the selected language, default is English
    hint_response = get_response(question, language, hint_requested=True)
    return jsonify({"hint": hint_response})


if __name__ == "__main__":
    app.run(debug=True)