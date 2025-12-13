from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'devops-secret-key' # Required for session (login)

# Configurable Chatbot URL
CHATBOT_SERVICE_HOST = os.getenv('CHATBOT_URL', 'http://chatbot:5001')

# --- CSS STYLES (The Look & Feel) ---
STYLES = """
<style>
    body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f4f7f6; height: 100vh; display: flex; flex-direction: column; }
    
    /* LOGIN PAGE STYLES */
    .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 300px; text-align: center; }
    .login-box input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box;}
    .login-box button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
    .login-box button:hover { background: #5a6fd6; }

    /* DASHBOARD LAYOUT (Left Sidebar + Right Content) */
    .dashboard { display: flex; height: 100vh; overflow: hidden; }
    
    /* LEFT SIDEBAR (Chatbot) */
    .sidebar { width: 350px; background: #2c3e50; color: white; display: flex; flex-direction: column; border-right: 1px solid #ddd; }
    .sidebar-header { padding: 20px; background: #1a252f; text-align: center; font-weight: bold; border-bottom: 1px solid #34495e; }
    .chat-history { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
    .chat-input-area { padding: 20px; background: #34495e; display: flex; gap: 10px; }
    .chat-input-area input { flex: 1; padding: 10px; border-radius: 4px; border: none; }
    .chat-input-area button { padding: 10px 15px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }

    /* RIGHT CONTENT (Store) */
    .main-content { flex: 1; padding: 40px; overflow-y: auto; background: #ecf0f1; }
    .navbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
    .product-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s; }
    .product-card:hover { transform: translateY(-5px); }
    .product-price { color: #e74c3c; font-weight: bold; font-size: 1.2em; }
    
    /* Chat Messages */
    .msg { padding: 10px; border-radius: 8px; max-width: 80%; font-size: 0.9em; }
    .msg.user { background: #3498db; color: white; align-self: flex-end; }
    .msg.bot { background: #ecf0f1; color: #2c3e50; align-self: flex-start; }
</style>
"""

# --- PAGE TEMPLATES ---

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Login - DevOps Store</title>""" + STYLES + """</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2>Welcome Back</h2>
            <p style="color: #666; font-size: 0.9em;">DevOps E-Commerce Portal</p>
            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
            <p style="margin-top: 15px; font-size: 0.8em; color: #888;">(Hint: Use any password)</p>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Shop Dashboard</title>""" + STYLES + """</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="sidebar-header">🤖 AI Support Agent</div>
            <div id="chat-history" class="chat-history">
                <div class="msg bot">Hello {{ username }}! How can I help you today?</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="msgInput" placeholder="Ask about shipping..." onkeypress="handleEnter(event)">
                <button onclick="send()">Send</button>
            </div>
        </div>

        <div class="main-content">
            <div class="navbar">
                <h1>🛍️ DevOps Microstore</h1>
                <div>
                    <span>Welcome, <strong>{{ username }}</strong></span>
                    <a href="/logout" style="margin-left: 15px; color: #e74c3c; text-decoration: none;">Logout</a>
                </div>
            </div>

            <div class="product-grid">
                <div class="product-card">
                    <h3>"SUPER K8S HOODIE"</h3>
                    <p>Deploy in comfort.</p>
                    <div class="product-price">$20.00</div>
                </div>
                <div class="product-card">
                    <h3>Docker Cap</h3>
                    <p>Containerize your head.</p>
                    <div class="product-price">$25.00</div>
                </div>
                <div class="product-card">
                    <h3>Terraform Mug</h3>
                    <p>Infrastructure as Coffee.</p>
                    <div class="product-price">$99.99</div>
                </div>
                <div class="product-card">
                    <h3>AWS Sticker Pack</h3>
                    <p>Stick to the cloud.</p>
                    <div class="product-price">$5.00</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function handleEnter(e) {
            if (e.key === 'Enter') send();
        }

        async function send() {
            const input = document.getElementById('msgInput');
            const history = document.getElementById('chat-history');
            const text = input.value;
            if (!text) return;

            // 1. Add User Message
            history.innerHTML += `<div class="msg user">You: ${text}</div>`;
            input.value = '';
            history.scrollTop = history.scrollHeight;

            // 2. Call API
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                
                // 3. Add Bot Response
                history.innerHTML += `<div class="msg bot">Bot: ${data.response}</div>`;
                history.scrollTop = history.scrollHeight;
            } catch (e) {
                history.innerHTML += `<div class="msg bot" style="color:red">Error connecting to AI service</div>`;
            }
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template_string(LOGIN_PAGE)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_PAGE, username=session['username'])

@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    user_data = request.get_json()
    try:
        response = requests.post(f"{CHATBOT_SERVICE_HOST}/chat", json=user_data, timeout=3)
        return jsonify(response.json())
    except:
        return jsonify({"response": "⚠️ AI Service Unavailable"}), 503

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)