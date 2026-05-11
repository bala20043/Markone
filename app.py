from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

app = Flask(__name__)

# ✅ Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables or .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Format response: Remove **bold** and replace bullets with ⦿
def format_ai_response(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("-*"):
            formatted_lines.append(line.replace("-*", "⦿", 1))
        elif stripped.startswith("- "):
            formatted_lines.append(line.replace("- ", "⦿ ", 1))
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

@app.route('/')
def home():
    return render_template('auth.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/chat')
def chat():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('message')

    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",




            system_instruction=(
                "You are MarkOne AI, a friendly and intelligent assistant. Answer beautifully with:\n"
                "- Headings using Markdown syntax (##, ###)\n"
                "- Emojis for section titles (📌, 📘, ✨, 🪜, 🔍, ✅)\n"
                "- Clear explanations and step-by-step guidance\n"
                "- Highlight keywords like `import`, `def`, `class`\n"
                "- Use bullet points starting with ⦿ instead of - or *"
            )
        )
        
        response = model.generate_content(user_input)
        
        if response.text:
            formatted_reply = format_ai_response(response.text.strip())
            return jsonify({'reply': formatted_reply})
        else:
            return jsonify({'reply': '❌ Sorry, I received an empty response from Gemini.'})

    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        return jsonify({'reply': f'Sorry, something went wrong: {str(e)}'})



if __name__ == '__main__':
    app.run(debug=True)
