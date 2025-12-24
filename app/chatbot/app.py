from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Product data matching your New UI
PRODUCTS = {
    "hoodie": 80.00,
    "cap": 50.00,
    "mug": 15.99,
    "sticker": 25.00,
    "t-shirt": 45.00,
    "shoe": 60.00,
    "pin": 8.00,
    "plush": 29.99,
    "bottle": 20.50,
    "extinguisher": 150.00
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Logic Engine
    response_text = "I'm not quite sure about that. Try asking about a product price or shipping!"

    # 1. Greetings
    if any(word in message for word in ["hello", "hi", "hey"]):
        response_text = "Hello! Welcome to the DevOps store. How can I help you today?"
    
    # 2. Dynamic Price Lookup
    elif "price" in message or "cost" in message:
        found = False
        for item, price in PRODUCTS.items():
            if item in message:
                response_text = f"The {item.capitalize()} costs ${price}. It's one of our best sellers!"
                found = True
                break
        if not found:
            response_text = "Our prices are competitive! Which specific item are you asking about?"

    # 3. Shipping & Returns
      elif "shipping" in message:
        response_text = "We ship worldwide via AWS Logistics. You can expect your order in 3-5 business days."
    elif "return" in message:
        response_text = "We offer a 30-day return policy on all DevOps gear if you aren't satisfied."
    
    # 4. Human Agent Joke
    elif "human" in message:
        response_text = "I'm currently your dedicated AI agent. But don't worry, I have root access to all your answers!"

    return jsonify({
        "response": response_text,
        "service": "chatbot-v1"
    })

if __name__ == '__main__':
    # Running on 5001 so it doesn't conflict with app.py on 5000
    app.run(host='0.0.0.0', port=5001)