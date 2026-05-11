from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

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
def auth():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('message')

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "MarkOne AI Chat"
    }

    data = {
        "model": "google/gemini-flash-1.5",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are MarkOne AI, a friendly and intelligent assistant. Answer beautifully with:\n"
                    "- Headings using Markdown syntax (##, ###)\n"
                    "- Emojis for section titles (📌, 📘, ✨, 🪜, 🔍, ✅)\n"
                    "- Clear explanations and step-by-step guidance\n"
                    "- Highlight keywords like `import`, `def`, `class`\n"
                    "- Use bullet points starting with ⦿ instead of - or *"
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content'].strip()
        formatted_reply = format_ai_response(reply)
        return jsonify({'reply': formatted_reply})
    else:
        print(f"❌ OpenRouter Error: {response.status_code} {response.text}")
        return jsonify({'reply': '❌ Sorry, something went wrong with OpenRouter API.'})

if __name__ == '__main__':
    app.run(debug=True)
