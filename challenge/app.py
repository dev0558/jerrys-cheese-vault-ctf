from flask import Flask, request, render_template_string, session, redirect, url_for
import os, psycopg2, time, psycopg2.extras

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://jerry:cheese@db:5432/cheesevault")

# ============= SHARED CSS =============
SHARED_CSS = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}
.container {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
}
header {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 40px;
    text-align: center;
    position: relative;
}
header h1 {
    font-size: 3em;
    margin-bottom: 10px;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    animation: bounce 2s infinite;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
.subtitle {
    font-size: 1.2em;
    opacity: 0.95;
    font-weight: 300;
}
main {
    padding: 40px;
}
.story-box {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
    border-left: 6px solid #ff6b6b;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.story-box p {
    line-height: 1.8;
    font-size: 1.1em;
    color: #333;
}
.mission-box {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    border-left: 6px solid #667eea;
}
.mission-box h3 {
    color: #667eea;
    margin-bottom: 15px;
    font-size: 1.5em;
}
.mission-box ul {
    list-style: none;
    padding-left: 0;
}
.mission-box li {
    padding: 10px 0;
    padding-left: 30px;
    position: relative;
    font-size: 1.05em;
}
.mission-box li:before {
    content: "🎯";
    position: absolute;
    left: 0;
}
.hint-box {
    background: #fff9c4;
    border: 3px dashed #fbc02d;
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    text-align: center;
}
.hint-box p {
    font-size: 1.1em;
    color: #f57f17;
    font-weight: 500;
}
.login-box {
    max-width: 450px;
    margin: 0 auto;
    background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.login-box h2 {
    color: #4a148c;
    margin-bottom: 25px;
    text-align: center;
    font-size: 2em;
}
.form-group {
    margin-bottom: 20px;
}
.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #4a148c;
    font-size: 1.05em;
}
.form-group input {
    width: 100%;
    padding: 14px;
    border: 2px solid #b39ddb;
    border-radius: 10px;
    font-size: 1em;
    transition: all 0.3s;
    background: white;
}
.form-group input:focus {
    outline: none;
    border-color: #7c4dff;
    box-shadow: 0 0 0 3px rgba(124, 77, 255, 0.1);
    transform: scale(1.02);
}
.btn {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: 10px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}
.btn-primary:active {
    transform: translateY(-1px);
}
.action-button {
    text-align: center;
    margin-top: 30px;
}
.action-button a {
    display: inline-block;
    padding: 16px 40px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: bold;
    font-size: 1.1em;
    box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.action-button a:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(245, 87, 108, 0.6);
}
.error-message {
    background: #ffebee;
    color: #c62828;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    border-left: 4px solid #c62828;
    font-weight: 500;
}
.credentials-hint {
    margin-top: 25px;
    padding: 20px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.credentials-hint p {
    font-weight: 600;
    color: #4a148c;
    margin-bottom: 10px;
}
.credentials-hint ul {
    list-style: none;
    padding: 0;
}
.credentials-hint li {
    padding: 8px 0;
    font-size: 0.95em;
}
.credentials-hint code {
    background: #e1f5fe;
    padding: 4px 8px;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    color: #01579b;
    font-weight: bold;
}
.small-text {
    font-size: 0.9em;
    color: #666;
    font-style: italic;
    margin-top: 10px;
}
.user-info {
    margin-top: 15px;
    background: rgba(255,255,255,0.3);
    padding: 12px;
    border-radius: 10px;
    font-size: 1em;
}
.badge-admin {
    background: #ff1744;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(255, 23, 68, 0); }
}
.inventory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin: 30px 0;
}
.cheese-card {
    background: linear-gradient(135deg, #fff9e6 0%, #ffe0b2 100%);
    padding: 25px;
    border-radius: 15px;
    border: 3px solid #ffb74d;
    transition: all 0.3s;
    cursor: pointer;
}
.cheese-card:hover {
    transform: translateY(-8px) rotate(2deg);
    box-shadow: 0 12px 30px rgba(255, 183, 77, 0.4);
}
.cheese-card h3 {
    color: #e65100;
    margin-bottom: 15px;
    font-size: 1.5em;
}
.cheese-card p {
    margin: 8px 0;
    color: #5d4037;
    font-size: 1em;
}
.admin-section {
    background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
    padding: 35px;
    border-radius: 20px;
    margin-top: 40px;
    border: 4px solid #66bb6a;
    box-shadow: 0 10px 40px rgba(102, 187, 106, 0.3);
}
.admin-section h2 {
    color: #1b5e20;
    margin-bottom: 20px;
    font-size: 2em;
}
.admin-notice {
    background: #ff6b6b;
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    margin-bottom: 25px;
    font-size: 1.1em;
    text-transform: uppercase;
    letter-spacing: 2px;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}
.note-card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 20px;
    border-left: 6px solid #66bb6a;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s;
}
.note-card:hover {
    transform: translateX(5px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.note-card h3 {
    color: #2e7d32;
    margin-bottom: 15px;
    font-size: 1.4em;
}
.note-card p {
    line-height: 1.8;
    color: #333;
    font-size: 1.05em;
}
.note-meta {
    color: #777;
    font-size: 0.9em;
    margin-top: 15px;
    font-style: italic;
}
.notice-box {
    background: #e3f2fd;
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
    border-left: 6px solid #2196f3;
    color: #0d47a1;
}
footer {
    background: linear-gradient(135deg, #434343 0%, #000000 100%);
    color: white;
    padding: 25px;
    text-align: center;
    font-size: 0.95em;
}
.back-link {
    margin-top: 25px;
    text-align: center;
}
.back-link a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    font-size: 1.05em;
    transition: all 0.3s;
}
.back-link a:hover {
    color: #764ba2;
    text-decoration: underline;
}
</style>
"""

# ============= HOME PAGE =============
HOME_HTML = """
<!doctype html>
<html><head><meta charset="utf-8"><title>Jerry's Cheese Vault</title>
""" + SHARED_CSS + """
</head>
<body>
  <div class="container">
    <header>
      <h1>🧀 Jerry's Cheese Vault 🐭</h1>
      <p class="subtitle">Ultimate Cheese Management System</p>
    </header>
    <main>
      <div class="story-box">
        <p><strong>🎬 The Story:</strong> Oh no! Tom has caught Jerry and locked all his precious cheese collection in this digital vault. As <strong>Nibbles</strong> (Jerry's nephew), you need to break into the vault management system to free the cheese and find where Tom hid the master key to Jerry's cage!</p>
      </div>
      
      <div class="mission-box">
        <h3>🎯 Your Mission</h3>
        <ul>
          <li>Break into the vault management system</li>
          <li>Find Tom's secret admin notes</li>
          <li>Discover the location of the master key</li>
          <li>Free Jerry and save the cheese!</li>
        </ul>
      </div>
      
      <div class="hint-box">
        <p>💡 <strong>Hint:</strong> Tom's human owner built this system quickly... The login form might have some security holes!</p>
      </div>
      
      <div class="action-button">
        <a href="/login">🔐 Access Vault System</a>
      </div>
    </main>
    <footer>
      <p>🏆 Exploit3rs CTF Challenge | Created by Bhargav | Learn Secure Coding!</p>
    </footer>
  </div>
</body></html>
"""

# ============= LOGIN PAGE =============
LOGIN_HTML = """
<!doctype html>
<html><head><meta charset="utf-8"><title>Login - Jerry's Cheese Vault</title>
""" + SHARED_CSS + """
</head>
<body>
  <div class="container">
    <header>
      <h1>🧀 Jerry's Cheese Vault 🐭</h1>
      <p class="subtitle">Login to Access Secure Vault</p>
    </header>
    <main>
      <div class="login-box">
        <h2>🔐 Vault Access</h2>
        {% if error %}
        <div class="error-message">
          ⚠️ {{ error }}
        </div>
        {% endif %}
        <form method="POST" action="/login">
          <div class="form-group">
            <label>👤 Username</label>
            <input name="username" placeholder="Enter your username" required autofocus>
          </div>
          <div class="form-group">
            <label>🔒 Password</label>
            <input name="password" type="password" placeholder="Enter your password" required>
          </div>
          <button type="submit" class="btn btn-primary">🚀 Login</button>
        </form>
        
        <div class="credentials-hint">
          <p>📝 Test Credentials:</p>
          <ul>
            <li>🐭 Username: <code>jerry</code> / Password: <code>cheeselover</code></li>
            <li>🐱 Username: <code>tom</code> / Password: <code>meowmeow123</code></li>
          </ul>
          <p class="small-text">💭 These are regular users. Admin access reveals secret notes...</p>
        </div>
      </div>
      
      <div class="back-link">
        <a href="/">← Back to Home</a>
      </div>
    </main>
    <footer>
      <p>🏆 Exploit3rs CTF Challenge | Find the vulnerability and capture the flag!</p>
    </footer>
  </div>
</body></html>
"""

# ============= VAULT PAGE =============
VAULT_HTML = """
<!doctype html>
<html><head><meta charset="utf-8"><title>Vault - Jerry's Cheese Vault</title>
""" + SHARED_CSS + """
</head>
<body>
  <div class="container">
    <header>
      <h1>🧀 Jerry's Cheese Vault 🐭</h1>
      <p class="subtitle">Secure Cheese Inventory System</p>
      <div class="user-info">
        👤 Logged in as: <strong>{{ username }}</strong>
        {% if role == 'admin' %}
        <span class="badge-admin">⭐ ADMIN</span>
        {% else %}
        <span style="color:#fff; opacity:0.8;">({{ role }})</span>
        {% endif %}
        | <a href="/logout" style="color:#fff; text-decoration:underline;">Logout</a>
      </div>
    </header>
    <main>
      <h2 style="color:#333; border-bottom:3px solid #667eea; padding-bottom:10px;">📦 Cheese Inventory</h2>
      
      <div class="inventory-grid">
        {% for c in cheeses %}
        <div class="cheese-card">
          <h3>🧀 {{ c.cheese_type }}</h3>
          <p><strong>Quantity:</strong> {{ c.quantity }} wheels</p>
          <p><strong>Location:</strong> {{ c.location }}</p>
          <p><strong>Quality:</strong> {{ c.quality }}</p>
        </div>
        {% endfor %}
      </div>
      
      {% if role == 'admin' and admin_notes %}
      <div class="admin-section">
        <h2>🔒 Admin Notes</h2>
        <p class="admin-notice">⚠️ Confidential - Admin Eyes Only ⚠️</p>
        {% for n in admin_notes %}
        <div class="note-card">
          <h3>📌 {{ n.title }}</h3>
          <p>{{ n.content }}</p>
          <p class="note-meta">✍️ By {{ n.author }} on {{ n.created_at.strftime('%Y-%m-%d %H:%M') if n.created_at else 'N/A' }}</p>
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="notice-box">
        <p>ℹ️ <strong>Note:</strong> You are viewing the vault as a regular user. Admin notes are hidden from your view. Need admin access to see confidential information!</p>
      </div>
      {% endif %}
    </main>
    <footer>
      <p>🏆 Exploit3rs CTF Challenge | You've accessed the vault! Now find the flag!</p>
    </footer>
  </div>
</body></html>
"""

def get_conn_with_retry(dsn, tries=10, delay=0.8):
    for i in range(tries):
        try:
            return psycopg2.connect(dsn)
        except Exception as e:
            time.sleep(delay)
    return psycopg2.connect(dsn)

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)

    u = request.form.get("username","")
    p = request.form.get("password","")
    conn = get_conn_with_retry(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # INTENTIONAL SQLi for CTF
    query = f"SELECT username, role FROM users WHERE username = '{u}' AND password = '{p}'"
    cur.execute(query)
    row = cur.fetchone()
    cur.close(); conn.close()

    if not row:
        return render_template_string(LOGIN_HTML, error="Invalid credentials! Tom is watching... 👀")

    session["username"] = row["username"]
    session["role"] = row["role"]
    return redirect(url_for("vault"))

@app.route("/vault")
def vault():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_conn_with_retry(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT cheese_type, quantity, location, quality FROM cheese_inventory ORDER BY id")
    cheeses = cur.fetchall()

    admin_notes = []
    if session.get("role") == "admin":
        cur.execute("SELECT title, content, author, created_at FROM admin_notes ORDER BY created_at DESC")
        admin_notes = cur.fetchall()

    cur.close(); conn.close()
    return render_template_string(VAULT_HTML,
        username=session["username"], role=session["role"],
        cheeses=cheeses, admin_notes=admin_notes)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/_health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
