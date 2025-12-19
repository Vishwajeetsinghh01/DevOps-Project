from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Health check for Kubernetes (Liveness Probe)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Logic Engine
    response_text = "I am not sure how to help with that."
    if "hello" in message or "hi" in message:
        response_text = "Hello! Welocme to the DevOps strore. How can I help you with your order?"
    elif "price" in message:
        response_text = "Our prices are competitive! The Docker shirt is $25."
    elif "shipping" in message:
        response_text = "We ship worldwide via AWS Logistics (3-5 days)."
    elif "return" in message:
        response_text = "You can return items within 30 days."
    elif "human" in message:
        response_text = "Connecting you to a human agent... (Just kidding, I'm a bot)."
        
    return jsonify({
        "response": response_text,
        "service": "chatbot-v1"
    })

if __name__ == '__main__':
    # Run with Gunicorn in production, but simple run here
    app.run(host='0.0.0.0', port=5001)