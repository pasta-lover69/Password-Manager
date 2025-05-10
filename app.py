from flask import Flask, request, jsonify, render_template
from cryptography.fernet import Fernet
import os,json

app = Flask(__name__)
KEY_FILE = 'key.key'
PASS_FILE = 'passwords.json'

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

def load_passwords():
    if not os.path.exists(PASS_FILE):
        with open(PASS_FILE, 'w') as f:
            json.dump({}, f)
    with open(PASS_FILE, 'r') as f:
        return json.load(f)
  
def save_passwords(passwords):
    with open(PASS_FILE, 'w') as f:
        json.dump(passwords, f)
        
@app.route('/')
def index():
    return render_template('index.html')
  
@app.route("/add", methods = ["POST"])
def add():
    data = request.get_json()
    service = data.get('service')
    username = data.get('username')
    password = data.get('password')
    if not all([service, username, password]):
        return jsonify({"error": "Please fill in all fields."}), 400
    passwords = load_passwords()
    passwords[service] = {
        'username': username,
        'password': fernet.encrypt(password.encode()).decode()
    }
    save_passwords(passwords)
    return jsonify({"success": True})
  
@app.route("/get/<service>", methods=["GET"])
def get(service):
    passwords = load_passwords()
    if service in passwords:
        decrypted = fernet.decrypt(passwords[service]['password'].encode()).decode()
        return jsonify({
            "username": passwords[service]['username'],
            "password": decrypted
        })
    return jsonify({"error": "Service not found."}), 404
  
@app.route("/")
def home():
    return "Password Manager is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))