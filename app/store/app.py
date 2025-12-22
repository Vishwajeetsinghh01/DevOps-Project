from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'devops-secret-key'

# Configurable Chatbot URL
CHATBOT_SERVICE_HOST = os.getenv('CHATBOT_URL', 'http://chatbot:5000')

# --- TECH-CENTRIC INDIGO STYLES ---
STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    :root {
        --primary: #4f46e5;    /* Indigo */
        --primary-light: #6366f1;
        --accent: #0ea5e9;     /* Sky Blue for Cart/Actions */
        --success: #10b981;    /* Emerald for Buy buttons */
        --bg-main: #f8fafc;
        --bg-dark: #0f172a;    /* Slate 900 */
    }

    body { font-family: 'Inter', sans-serif; margin: 0; background: var(--bg-main); color: #1e293b; }

    /* --- LOGIN PAGE --- */
    .login-container { 
        display: flex; justify-content: center; align-items: center; height: 100vh; 
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
    }
    .login-box { 
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px);
        padding: 45px; border-radius: 24px; box-shadow: 0 25px 50px rgba(0,0,0,0.5); 
        width: 360px; text-align: center; border: 1px solid rgba(255,255,255,0.1); color: white;
    }
    .login-box input { 
        width: 100%; padding: 14px; margin: 12px 0; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.05); color: white; outline: none; box-sizing: border-box;
    }
    .login-box button { 
        width: 100%; padding: 14px; background: var(--primary); color: white; 
        border: none; border-radius: 12px; cursor: pointer; font-weight: 700; transition: 0.3s; margin-top: 10px;
    }
    .login-box button:hover { background: var(--primary-light); transform: translateY(-2px); }

    /* --- DASHBOARD & NAVBAR --- */
    .main-content { padding: 40px; max-width: 1300px; margin: 0 auto; }
    .navbar { 
        display: flex; justify-content: space-between; align-items: center; 
        background: white; padding: 20px 40px; border-radius: 20px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 40px; border: 1px solid #e2e8f0;
    }
    .cart-btn {
        background: var(--bg-dark); color: white; padding: 12px 24px; 
        border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 14px; transition: 0.3s;
    }
    .cart-btn:hover { background: var(--primary); }

    /* --- PRODUCT GRID --- */
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 30px; }
    .product-card { 
        background: white; border-radius: 20px; overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        border: 1px solid #e2e8f0; position: relative;
    }
    .product-card:hover { transform: translateY(-12px); box-shadow: 0 20px 30px rgba(0,0,0,0.08); border-color: var(--primary-light); }
    .product-info { padding: 25px; }
    .product-price { color: var(--primary); font-weight: 800; font-size: 1.6em; margin: 15px 0; }
    .order-btn { 
        width: 100%; padding: 12px; background: var(--success); color: white; 
        border: none; border-radius: 12px; cursor: pointer; font-weight: 700; transition: 0.3s;
    }
    .order-btn:hover { background: #059669; filter: brightness(1.1); }

    /* --- DRAGGABLE CHAT --- */
    #chatWidget { position: fixed; bottom: 30px; right: 30px; z-index: 9999; }
    .chat-window {
        width: 360px; height: 520px; background: white; border-radius: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15); display: none; flex-direction: column;
        overflow: hidden; border: 1px solid #e2e8f0;
    }
    .chat-header { padding: 18px 24px; background: var(--bg-dark); color: white; cursor: move; display: flex; justify-content: space-between; align-items: center; }
    .chat-history { flex: 1; padding: 20px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; gap: 12px; }
    .chat-input-area { padding: 18px; display: flex; gap: 12px; background: white; border-top: 1px solid #f1f5f9; }
    .chat-input-area input { flex: 1; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; outline: none; background: #f8fafc; }
    .chat-fab {
        width: 65px; height: 65px; background: var(--primary); border-radius: 22px; /* Squircle shape */
        display: flex; justify-content: center; align-items: center; color: white;
        font-size: 28px; cursor: pointer; box-shadow: 0 12px 24px rgba(79, 70, 229, 0.3); margin-left: auto; transition: 0.3s;
    }
    .chat-fab:hover { transform: rotate(-10deg) scale(1.1); background: var(--accent); }

    .msg { padding: 12px 16px; border-radius: 16px; font-size: 13.5px; max-width: 80%; line-height: 1.5; }
    .msg.user { background: var(--primary); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
    .msg.bot { background: white; color: #334155; align-self: flex-start; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
</style>
"""

# --- LOGIN PAGE ---
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - DevOps Store</title>
    """ + STYLES + """
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2 style="margin-bottom:10px">🔐 Access Control</h2>
            <p style="opacity:0.7; margin-bottom:20px">Please sign in to access the provisioning dashboard.</p>
            <form method="post">
                <input type="text" name="username" placeholder="Enter Operator ID" required>
                <button type="submit">Authenticate</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- DASHBOARD PAGE ---
DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head><title>DevOps Infrastructure Store</title>""" + STYLES + """</head>
<body>
    <div class="main-content">
        <div class="navbar">
            <h2 style="margin:0; display:flex; align-items:center; gap:10px; color:var(--bg-dark)">
                <span style="color:var(--primary)">⚡</span> DevOps Gear
            </h2>
            <div style="display:flex; align-items:center; gap:25px;">
                <span style="font-size:14px; color:#64748b">Operator: <strong style="color:var(--bg-dark)">{{ username }}</strong></span>
                <a href="#" class="cart-btn" onclick="alert('Cart system initialized!')">🛒 Cart (0)</a>
                <a href="/logout" style="color:#ef4444; text-decoration:none; font-size:14px; font-weight:700;">Sign Out</a>
            </div>
        </div>

        <div class="product-grid">
            {% set items = [
                ('Super K8s Hoodie', 'Premium deployment comfort.', '$80.00'),
                ('Linux Cap', 'Containerize your head.', '$40.00'),
                ('Terraform Mug', 'Infrastructure as Coffee.', '$15.99'),
                ('AWS Sticker Pack', 'Stick to the cloud.', '$25.00'),
                ('CI/CD T-Shirt', 'Automate your wardrobe.', '$45.00'),
                ('Jenkins Build Shoe', 'Walk the pipeline.', '$60.00'),
                ('Git Conflict Tee', 'Warning: High Anxiety.', '$25.00'),
                ('Prometheus Pin', 'Monitor your lapel.', '$8.00'),
                ('Docker Whale Plush', 'Cuddle containers.', '$29.99'),
                ('Root User Hoodie', 'With great sudo power.', '$45.00'),
                ('Cloud Native Bottle', 'Hydrate your clusters.', '$20.50'),
                ('Code Extinguisher', 'For prod hotfixes.', '$150.00')
            ] %}
            {% for name, desc, price in items %}
            <div class="product-card">
                <div class="product-info">
                    <h3 style="margin:0 0 8px 0; font-size:18px;">{{ name }}</h3>
                    <p style="color:#64748b; font-size:13px; line-height:1.4;">{{ desc }}</p>
                    <div class="product-price">{{ price }}</div>
                    <button class="order-btn" onclick="alert('{{ name }} added to deployment queue!')">Order Now</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div id="chatWidget">
        <div id="chatWindow" class="chat-window">
            <div id="chatHeader" class="chat-header">
                <span style="font-weight:700;">🤖 System Support</span>
                <span onclick="toggleChat()" style="cursor:pointer; opacity:0.7">✖</span>
            </div>
            <div id="chat-history" class="chat-history">
                <div class="msg bot">System ready. Hello {{ username }}, how can I assist with your provisioning today?</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="msgInput" placeholder="Ask a question..." onkeypress="handleEnter(event)">
                <button onclick="send()" style="border:none; background:none; cursor:pointer; font-size:22px; color:var(--primary)">🚀</button>
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
                history.innerHTML += `<div class="msg bot" style="color:#ef4444">Connection Error: Bot Offline</div>`;
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
#jjj