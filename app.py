from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://password_manager_database_8ubk_user:VR3JnfBYKvoFgR3MOvuaB9nvyfHo17Ww@dpg-d0j0bcmmcj7s7393u9n0-a.oregon-postgres.render.com/password_manager_database_8ubk')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

db = SQLAlchemy(app)

fernet = Fernet(open("key.key", "rb").read())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('passwords', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Log the user in after registration
    session['username'] = username

    return jsonify({"success": "User registered successfully."})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Both username and password are required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password."}), 401

    session['username'] = username
    return jsonify({"success": "Login successful."})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": "Logged out successfully."})

@app.route("/add", methods=["POST"])
def add():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data = request.get_json()
    service = data.get('service')
    username = data.get('username')
    password = data.get('password')

    if not service or not username or not password:
        return jsonify({"error": "All fields are required."}), 400

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    encrypted_password = fernet.encrypt(password.encode()).decode()
    new_password = Password(service=service, username=username, encrypted_password=encrypted_password, user=user)
    db.session.add(new_password)
    db.session.commit()

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

    user = User.query.filter_by(username=logged_in_user).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    passwords = Password.query.filter_by(user_id=user.id, service=service, username=requested_username).all()
    if not passwords:
        return jsonify({"error": "No credentials found for the specified username."}), 404

    credentials = [
        {
            "username": password.username,
            "password": fernet.decrypt(password.encrypted_password.encode()).decode()
        }
        for password in passwords
    ]

    return jsonify({"service": service, "credentials": credentials})

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
    user = User.query.filter_by(username=username).first()

    if user:
        services = list(set(password.service for password in user.passwords))
        return jsonify(services)
    return jsonify([])

@app.route("/get-all-passwords", methods=["GET"])
def get_all_passwords():
    if 'username' not in session:
        return jsonify([])

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify([])

    passwords = []
    for password_entry in user.passwords:
        decrypted_password = fernet.decrypt(password_entry.encrypted_password.encode()).decode()
        passwords.append({
            "service": password_entry.service,
            "username": password_entry.username,
            "password": decrypted_password
        })

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

    logged_in_user = session['username']
    user = User.query.filter_by(username=logged_in_user).first()

    if not user:
        return jsonify({"error": "User not found."}), 404

    password = Password.query.filter_by(user_id=user.id, service=service, username=username).first()
    if not password:
        return jsonify({"error": "Password not found."}), 404

    db.session.delete(password)
    db.session.commit()
    return jsonify({"success": "Password deleted successfully."})

@app.route("/edit-password", methods=["POST"])
def edit_password():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data = request.get_json()
    service = data.get('service')
    username = data.get('username')
    new_password = data.get('new_password')

    if not service or not username or not new_password:
        return jsonify({"error": "Service, username, and new password are required."}), 400

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    password_entry = Password.query.filter_by(service=service, username=username, user=user).first()
    if not password_entry:
        return jsonify({"error": "Password not found."}), 404

    password_entry.encrypted_password = fernet.encrypt(new_password.encode()).decode()
    db.session.commit()

    return jsonify({"success": "Password updated successfully."})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 500)))