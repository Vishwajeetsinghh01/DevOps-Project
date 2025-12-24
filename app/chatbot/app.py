from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Initialize NVIDIA OpenAI Client
# Note: In a real job, use os.getenv('NVIDIA_API_KEY') instead of hardcoding!
client = OpenAI(
    api_key="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",
    base_url="https://integrate.api.nvidia.com/v1"
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    try:
        # Using meta/llama-3.1-8b-instruct for chat completion
        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        
        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "I am having trouble connecting to my brain right now."}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)