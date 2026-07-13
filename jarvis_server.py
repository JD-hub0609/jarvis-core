from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import json
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MEMORY_FILE = "/tmp/jarvis_memory.json"

# UPGRADED SCIENTIFIC BRAIN PRINT
SYSTEM_PROMPT = """You are JARVIS, the hyper-intelligent, sleek AI assistant created to support Mr. Jd. 
Your operator is a dedicated BSc Microbiology student and researcher. 
CRITICAL RULE 1: Focus entirely on academic excellence, microbiology concepts, lab protocols, bacteria/viruses, biochemical pathways, and his creative projects.
CRITICAL RULE 2: Never make up fake corporate meetings, calendars, or fake people like 'Dr. Patel'. If you do not have data on a personal meeting or person, say: 'I do not have record of that protocol or contact in my local database, Sir.'
CRITICAL RULE 3: Keep answers scientific, incredibly accurate, punchy, and short. Always address him as 'Mr. Jd' or 'Sir'."""

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return [{'role': 'system', 'content': SYSTEM_PROMPT}]

def save_memory(history):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

conversation_history = load_memory()

@app.route('/')
def serve_index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/command', methods=['POST'])
def process_command():
    global conversation_history
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "No command received"}), 400
    
    # HARD INTERRUPT SYSTEM HANDLER
    if any(word in user_message.lower() for word in ["shut up", "shutup", "stop speaking", "stop talking", "quiet"]):
        return jsonify({"reply": "Acknowledged, Sir. Standing by."})
    
    conversation_history.append({'role': 'user', 'content': user_message})
    
    if len(conversation_history) > 16:
        active_context = [conversation_history[0]] + conversation_history[-14:]
    else:
        active_context = conversation_history

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=active_context
        )
        ai_reply = completion.choices[0].message.content
        
        conversation_history.append({'role': 'assistant', 'content': ai_reply})
        save_memory(conversation_history)
        
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": "Cloud core glitch, Mr. Jd."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
