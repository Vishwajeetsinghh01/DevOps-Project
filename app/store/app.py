from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'devops-secret-key'

# This is where your chatbot.py is running
CHATBOT_SERVICE_HOST = os.getenv('CHATBOT_URL', 'http://127.0.0.1:5001')

# --- THE COMPLETE CSS (Login + Dashboard + Chat) ---
STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --bg-main: #f8fafc;
        --bg-sidebar: #0f172a;
        --text-dark: #1e293b;
        --card-bg: #ffffff;
    }

    body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; background: var(--bg-main); color: var(--text-dark); }

    /* --- LOGIN PAGE STYLES --- */
    .login-container { 
        display: flex; justify-content: center; align-items: center; height: 100vh; 
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
    }
    .login-box { 
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        padding: 40px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); 
        width: 350px; text-align: center; border: 1px solid rgba(255,255,255,0.1); color: white;
    }
    .login-box h2 { font-weight: 600; margin-bottom: 20px; letter-spacing: -1px; }
    .login-box input { 
        width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; box-sizing: border-box;
        border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white;
    }
    .login-box button { 
        width: 100%; padding: 12px; background: var(--primary); color: white; 
        border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.3s;
    }
    .login-box button:hover { background: var(--primary-dark); }

    /* --- DASHBOARD STYLES --- */
    .main-content { padding: 40px; max-width: 1200px; margin: 0 auto; height: 100vh; overflow-y: auto; }
    .navbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }
    .product-card { 
        background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: all 0.3s ease;
    }
    .product-card:hover { transform: translateY(-8px); border-color: var(--primary); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    .product-price { color: var(--primary); font-weight: 600; font-size: 1.4em; margin-top: 15px; }

    /* --- FLOATING DRAGGABLE CHATBOT --- */
    #chatWidget { position: fixed; bottom: 30px; right: 30px; z-index: 1000; display: flex; flex-direction: column; align-items: flex-end; }
    .chat-window {
        width: 340px; height: 480px; background: white; border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); display: none; flex-direction: column;
        overflow: hidden; border: 1px solid #e2e8f0; margin-bottom: 15px;
    }
    .chat-header { 
        padding: 15px; background: var(--bg-sidebar); color: white; 
        display: flex; justify-content: space-between; cursor: move; align-items: center;
    }
    .chat-history { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #f1f5f9; }
    .chat-input-area { padding: 15px; display: flex; gap: 10px; border-top: 1px solid #e2e8f0; background: white; }
    .chat-input-area input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
    .chat-fab {
        width: 60px; height: 60px; background: var(--primary); border-radius: 50%;
        display: flex; justify-content: center; align-items: center; color: white;
        font-size: 24px; cursor: pointer; box-shadow: 0 10px 15px rgba(99, 102, 241, 0.4); transition: transform 0.2s;
    }
    .chat-fab:hover { transform: scale(1.1); }

    /* Message Bubbles */
    .msg { padding: 10px 14px; border-radius: 12px; font-size: 13px; max-width: 80%; line-height: 1.4; }
    .msg.user { background: var(--primary); color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
    .msg.bot { background: white; color: #1e293b; align-self: flex-start; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }
</style>
"""

# --- PAGE TEMPLATES ---

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Login | DevOps Store</title>""" + STYLES + """</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <div style="font-size: 40px; margin-bottom: 10px;">☁️</div>
            <h2>DevOps Portal</h2>
            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Secure Management Access</p>
            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Cloud Store Dashboard</title>""" + STYLES + """</head>
<body>
    <div class="main-content">
        <div class="navbar">
            <h1>🛍️ Cloud Catalog</h1>
            <div>
                <span>Welcome, <strong>{{ username }}</strong></span>
                <a href="/logout" style="margin-left: 15px; color: #ef4444; text-decoration: none; font-weight: 600;">Logout</a>
            </div>
        </div>

        <div class="product-grid">
            {% set items = [
                ('Super K8s Hoodie', 'Premium deployment comfort.', '$80.00'),
                ('Linux Cap', 'Containerize your head.', '$50.00'),
                ('Terraform Mug', 'Infrastructure as Coffee.', '$15.99'),
                ('AWS Sticker Pack', 'Stick to the cloud.', '$25.00'),
                ('CI/CD T-Shirt', 'Automate your wardrobe.', '$45.00'),
                ('Docker Whale Plush', 'Cuddle your containers.', '$29.99')
            ] %}
            {% for name, desc, price in items %}
            <div class="product-card">
                <h3>{{ name }}</h3>
                <p>{{ desc }}</p>
                <div class="product-price">{{ price }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div id="chatWidget">
        <div id="chatWindow" class="chat-window">
            <div id="chatHeader" class="chat-header">
                <span>🤖 AI Support</span>
                <span onclick="toggleChat()" style="cursor:pointer">✖</span>
            </div>
            <div id="chat-history" class="chat-history">
                <div class="msg bot">Hello {{ username }}! How can I help with your order?</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="msgInput" placeholder="Ask a question..." onkeypress="handleEnter(event)">
                <button onclick="send()" style="border:none; background:none; cursor:pointer; font-size: 20px;">🚀</button>
            </div>
        </div>
        <div class="chat-fab" onclick="toggleChat()">💬</div>
    </div>

    <script>
        function toggleChat() {
            const win = document.getElementById('chatWindow');
            win.style.display = (win.style.display === 'none' || win.style.display === '') ? 'flex' : 'none';
        }

        function handleEnter(e) { if (e.key === 'Enter') send(); }

        async function send() {
            const input = document.getElementById('msgInput');
            const history = document.getElementById('chat-history');
            const text = input.value.trim();
            if (!text) return;

            history.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = '';
            history.scrollTop = history.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                history.innerHTML += `<div class="msg bot">${data.response}</div>`;
            } catch (e) {
                history.innerHTML += `<div class="msg bot" style="color:red">Bot Offline</div>`;
            }
            history.scrollTop = history.scrollHeight;
        }

        // Draggable Script
        dragElement(document.getElementById("chatWidget"));
        function dragElement(elmnt) {
            var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            const header = document.getElementById("chatHeader");
            header.onmousedown = dragMouseDown;

            function dragMouseDown(e) {
                e.preventDefault();
                pos3 = e.clientX; pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                document.onmousemove = elementDrag;
            }
            function elementDrag(e) {
                e.preventDefault();
                pos1 = pos3 - e.clientX; pos2 = pos4 - e.clientY;
                pos3 = e.clientX; pos4 = e.clientY;
                elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
                elmnt.style.bottom = "auto"; elmnt.style.right = "auto";
            }
            function closeDragElement() { document.onmouseup = null; document.onmousemove = null; }
        }
    </script>
</body>
</html>
"""

# --- BACKEND ROUTES ---

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
        # Calls the external chatbot microservice
        response = requests.post(f"{CHATBOT_SERVICE_HOST}/chat", json=user_data, timeout=3)
        return jsonify(response.json())
    except:
        return jsonify({"response": "⚠️ Service Offline. Check chatbot.py on port 5001."}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)