from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'devops-secret-key'

CHATBOT_SERVICE_HOST = os.getenv('CHATBOT_URL', 'http://127.0.0.1:5001')

# --- PROFESSIONAL CSS STYLES ---
STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --bg-main: #f8fafc;
        --bg-sidebar: #0f172a;
        --text-dark: #1e293b;
        --text-light: #f8fafc;
        --card-bg: #ffffff;
        --accent: #10b981;
    }

    body { font-family: 'Inter', sans-serif; margin: 0; background: var(--bg-main); color: var(--text-dark); height: 100vh; display: flex; flex-direction: column; }

    /* --- LOGIN PAGE --- */
    .login-container { 
        display: flex; justify-content: center; align-items: center; height: 100vh; 
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
    }
    .login-box { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        padding: 40px; border-radius: 16px; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); 
        width: 350px; text-align: center; border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    .login-box h2 { font-weight: 600; margin-bottom: 10px; letter-spacing: -1px; }
    .login-box input { 
        width: 100%; padding: 12px; margin: 12px 0; border-radius: 8px; 
        border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); 
        color: white; font-size: 14px;
    }
    .login-box button { 
        width: 100%; padding: 12px; background: var(--primary); color: white; 
        border: none; border-radius: 8px; cursor: pointer; font-weight: 600;
        transition: all 0.3s; margin-top: 10px;
    }
    .login-box button:hover { background: var(--primary-dark); transform: translateY(-2px); }

    /* --- DASHBOARD LAYOUT --- */
    .dashboard { display: flex; height: 100vh; }
    
    /* SIDEBAR (Chatbot) */
    .sidebar { width: 380px; background: var(--bg-sidebar); color: var(--text-light); display: flex; flex-direction: column; }
    .sidebar-header { 
        padding: 25px; background: rgba(255,255,255,0.03); 
        font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex; align-items: center; gap: 10px;
    }
    .chat-history { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; scrollbar-width: thin; }
    .chat-input-area { padding: 20px; background: #1e293b; display: flex; gap: 10px; border-top: 1px solid rgba(255,255,255,0.1); }
    .chat-input-area input { 
        flex: 1; padding: 12px; border-radius: 8px; border: none; 
        background: #334155; color: white; outline: none;
    }
    .chat-input-area button { padding: 0 20px; background: var(--accent); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }

    /* MAIN CONTENT */
    .main-content { flex: 1; padding: 40px; overflow-y: auto; }
    .navbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
    .navbar h1 { font-size: 24px; font-weight: 600; letter-spacing: -1px; }

    /* PRODUCT GRID */
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }
    .product-card { 
        background: var(--card-bg); padding: 25px; border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e2e8f0;
    }
    .product-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border-color: var(--primary); }
    .product-card h3 { margin: 0 0 10px 0; font-size: 18px; color: var(--bg-sidebar); }
    .product-card p { color: #64748b; font-size: 14px; margin-bottom: 20px; }
    .product-footer { display: flex; justify-content: space-between; align-items: center; }
    .product-price { color: var(--primary); font-weight: 600; font-size: 1.4em; }
    .buy-btn { padding: 8px 16px; background: #f1f5f9; border-radius: 6px; font-size: 12px; font-weight: 600; color: #475569; border: none; cursor: pointer; transition: 0.2s; }
    .product-card:hover .buy-btn { background: var(--primary); color: white; }

    /* CHAT BUBBLES */
    .msg { padding: 12px 16px; border-radius: 12px; max-width: 85%; font-size: 14px; line-height: 1.5; }
    .msg.user { background: var(--primary); color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
    .msg.bot { background: #334155; color: white; align-self: flex-start; border-bottom-left-radius: 2px; }
</style>
"""

# --- PAGE TEMPLATES ---

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Sign In | DevOps Store</title>""" + STYLES + """</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <div style="font-size: 40px; margin-bottom: 10px;">☁️</div>
            <h2>DevOps Portal</h2>
            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Enter your credentials to manage deployments</p>
            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Access Dashboard</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Dashboard | DevOps Microstore</title>""" + STYLES + """</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="sidebar-header">
                <div style="width: 10px; height: 10px; background: #10b981; border-radius: 50%;"></div>
                Support Bot v1.2
            </div>
            <div id="chat-history" class="chat-history">
                <div class="msg bot">Welcome back, {{ username }}! Need help with your infrastructure orders?</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="msgInput" placeholder="Message support..." onkeypress="handleEnter(event)">
                <button onclick="send()">Send</button>
            </div>
        </div>

        <div class="main-content">
            <div class="navbar">
                <h1>🛍️ Cloud Catalog</h1>
                <div>
                    <span style="color: #64748b;">Operator: <strong style="color: #1e293b">{{ username }}</strong></span>
                    <a href="/logout" style="margin-left: 20px; color: #ef4444; text-decoration: none; font-weight: 600; font-size: 14px;">Logout</a>
                </div>
            </div>

            <div class="product-grid">
                {% set products = [
                    ('Super K8s Hoodie', 'Premium deployment comfort.', '$80.00'),
                    ('Linux Cap', 'Containerize your head.', '$50.00'),
                    ('Terraform Mug', 'Infrastructure as Coffee.', '$15.99'),
                    ('AWS Sticker Pack', 'Stick to the cloud.', '$25.00'),
                    ('CI/CD T-Shirt', 'Automate your style.', '$45.00'),
                    ('Jenkins Build Shoe', 'Walk through the pipeline.', '$60.00'),
                    ('Git Conflict Tee', 'Warning: High Anxiety.', '$25.00'),
                    ('Prometheus Pin', 'Monitor your lapel.', '$8.00'),
                    ('Docker Whale Plush', 'Cuddle your containers.', '$29.99'),
                    ('Root User Hoodie', 'With great sudo power.', '$45.00'),
                    ('Cloud Native Bottle', 'Hydrate your clusters.', '$20.50'),
                    ('Code Extinguisher', 'For prod hotfixes.', '$150.00')
                ] %}
                
                {% for name, desc, price in products %}
                <div class="product-card">
                    <h3>{{ name }}</h3>
                    <p>{{ desc }}</p>
                    <div class="product-footer">
                        <div class="product-price">{{ price }}</div>
                        <button class="buy-btn">Order Now</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function handleEnter(e) { if (e.key === 'Enter') send(); }

        async function send() {
            const input = document.getElementById('msgInput');
            const history = document.getElementById('chat-history');
            const text = input.value;
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
                history.scrollTop = history.scrollHeight;
            } catch (e) {
                history.innerHTML += `<div class="msg bot" style="color:#ef4444">Service Offline</div>`;
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
        return jsonify({"response": "⚠️ Bot connection failed. Ensure chatbot.py is running on port 5001."}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)