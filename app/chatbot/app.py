from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# The AI's "Personality" and Product Knowledge
SYSTEM_PROMPT = """
You are the helpful AI Sales Assistant for the 'DevOps Infrastructure Store'. 
Your goal is to help engineers buy cool DevOps merchandise.
Keep your answers short, friendly, and tech-savvy.

Here is our current Product Inventory:
1. Super K8s Hoodie ($80.00) - Premium deployment comfort.
2. Linux Cap ($40.00) - Containerize your head.
3. Terraform Mug ($15.99) - Infrastructure as Coffee.
4. AWS Sticker Pack ($25.00) - Stick to the cloud.
5. CI/CD T-Shirt ($45.00) - Automate your wardrobe.
6. Jenkins Build Shoe ($60.00) - Walk the pipeline.
7. Git Conflict Tee ($25.00) - Warning: High Anxiety.
8. Prometheus Pin ($8.00) - Monitor your lapel.
9. Docker Whale Plush ($29.99) - Cuddle containers.
10. Root User Hoodie ($45.00) - With great sudo power.
11. Cloud Native Bottle ($20.50) - Hydrate your clusters.
12. Code Extinguisher ($150.00) - For prod hotfixes.

If a user asks about something we don't sell, jokingly suggest they "open a feature request" or check StackOverflow.
"""

# Initialize NVIDIA OpenAI Client
client = OpenAI(
    api_key="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",
    base_url="https://integrate.api.nvidia.com/v1"
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"response": "I didn't hear anything! Try `echo 'Hello'`"}), 400

    try:
        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, # <--- Added Context Here
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        
        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "⚠️ Error: I cannot reach the AI brain (NVIDIA API). Check logs."}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    # Note: In production, use a WSGI server like Gunicorn to run the app.