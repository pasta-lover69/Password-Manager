from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from cryptography.fernet import Fernet
import os, json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
KEY_FILE = 'key.key'
PASS_FILE = 'passwords.json'
USERS_FILE = 'users.json'

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

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f"Register attempt: username={username}, password={password}")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    users = load_users()
    if username in users:
        print("Username already exists")
        return jsonify({"error": "Username already exists."}), 400

    users[username] = {
        "password": generate_password_hash(password),
        "passwords": {}
    }
    save_users(users)
    print("User registered successfully")
    return jsonify({"success": "User registered successfully."})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Both username and password are required."}), 400

    try:
        users = load_users()
    except FileNotFoundError:
        return jsonify({"error": "No users found. Please register first."}), 404

    if username not in users:
        return jsonify({"error": "Invalid username or password."}), 401

    if not check_password_hash(users[username]["password"], password):
        return jsonify({"error": "Invalid username or password."}), 401

    session['username'] = username
    return jsonify({"success": "Login successful."})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return jsonify({"success": "Logged out successfully."})


@app.route("/add", methods=["POST"])
def add():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data = request.get_json()
    logged_in_user = session['username']
    service = data.get('service')
    username = data.get('username')
    password = data.get('password')

    if not all([service, username, password]):
        return jsonify({"error": "All fields are required."}), 400

    users = load_users()
    if logged_in_user not in users:
        return jsonify({"error": "User not found."}), 404

    encrypted_password = fernet.encrypt(password.encode()).decode()

    if service not in users[logged_in_user]["passwords"]:
        users[logged_in_user]["passwords"][service] = []

    users[logged_in_user]["passwords"][service].append({
        "username": username,
        "password": encrypted_password
    })

    save_users(users)
    return jsonify({"success": "Password added successfully."})


@app.route("/get/<service>", methods=["POST"])
def get(service):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    logged_in_user = session['username']
    data = request.get_json()
    requested_username = data.get('username')

    if not requested_username:
        return jsonify({"error": "Username is required."}), 400

    users = load_users()

    if logged_in_user not in users:
        return jsonify({"error": "User not found."}), 404

    if service not in users[logged_in_user]["passwords"]:
        return jsonify({"error": "Service not found."}), 404

    try:
        credentials = [
            {
                "username": entry["username"],
                "password": fernet.decrypt(entry["password"].encode()).decode()
            }
            for entry in users[logged_in_user]["passwords"][service]
            if entry["username"] == requested_username
        ]

        if not credentials:
            return jsonify({"error": "No credentials found for the specified username."}), 404

        return jsonify({"service": service, "credentials": credentials})
    except Exception as e:
        print(f"Decryption error: {e}")
        return jsonify({"error": "Failed to decrypt passwords."}), 500

@app.route("/check-session", methods=["GET"])
def check_session():
    if 'username' in session:
        return jsonify({"logged_in": True, "username": session['username']})
    return jsonify({"logged_in": False})

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    return render_template("profile.html", username=username)

@app.route("/get-services", methods=["GET"])
def get_services():
    if 'username' not in session:
        return jsonify([])

    username = session['username']
    users = load_users()

    if username in users and "passwords" in users[username]:
        services = list(users[username]["passwords"].keys())
        return jsonify(services)
    return jsonify([])

@app.route("/get-all-passwords", methods=["GET"])
def get_all_passwords():
    if 'username' not in session:
        return jsonify([])

    logged_in_user = session['username']
    users = load_users()

    if logged_in_user not in users:
        return jsonify([])

    passwords = []
    for service, credentials in users[logged_in_user]["passwords"].items():
        for entry in credentials:
            try:
                decrypted_password = fernet.decrypt(entry["password"].encode()).decode()
                passwords.append({
                    "service": service,
                    "username": entry["username"],
                    "password": decrypted_password
                })
            except Exception as e:
                print(f"Decryption error for {service}: {e}")

    return jsonify(passwords)

@app.route("/view-passwords")
def view_passwords():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template("view_passwords.html")

@app.route("/delete-password", methods=["POST"])
def delete_password():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data = request.get_json()
    service = data.get('service')
    username = data.get('username')

    if not service or not username:
        return jsonify({"error": "Service and username are required."}), 400

    users = load_users()
    logged_in_user = session['username']

    if logged_in_user not in users:
        return jsonify({"error": "User not found."}), 404

    if service not in users[logged_in_user]["passwords"]:
        return jsonify({"error": "Service not found."}), 404

    passwords = users[logged_in_user]["passwords"][service]
    updated_passwords = [entry for entry in passwords if entry["username"] != username]

    if len(passwords) == len(updated_passwords):
        return jsonify({"error": "Password not found."}), 404
    
    if updated_passwords:
        users[logged_in_user]["passwords"][service] = updated_passwords
    else:
        del users[logged_in_user]["passwords"][service]

    save_users(users)
    return jsonify({"success": "Password deleted successfully."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))