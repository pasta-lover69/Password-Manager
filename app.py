from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
import base64

app = Flask(__name__)

# Configuration for Vercel deployment
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Database configuration - Use environment variable for database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Handle different database URL formats
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
    app.config["SESSION_COOKIE_SECURE"] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key_change_in_production")

db = SQLAlchemy(app)

# Encryption key management for Vercel
def get_encryption_key():
    """Get encryption key from environment variable"""
    encryption_key = os.getenv('ENCRYPTION_KEY')
    if encryption_key:
        try:
            # Try to decode as base64
            return base64.b64decode(encryption_key.encode())
        except:
            # If that fails, use the key directly
            return encryption_key.encode()
    else:
        # Generate a default key for development (not recommended for production)
        return Fernet.generate_key()

fernet = Fernet(get_encryption_key())

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    passwords = db.relationship('Password', backref='user', lazy=True)

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password_encrypted = db.Column(db.String(256), nullable=False)

# Initialize database - Updated for newer Flask versions
def create_tables():
    with app.app_context():
        db.create_all()

# Routes
@app.route('/')
def index():
    # Ensure tables exist on first request
    try:
        db.create_all()
    except:
        pass
    return render_template('index.html')

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    try:
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in after successful registration
        session['username'] = username
        
        return jsonify({
            "success": "User registered successfully.",
            "redirect": "/profile"
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed. Please try again."}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f"Login attempt for username: {username}")  # Debug

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        user = User.query.filter_by(username=username).first()
        print(f"User found in database: {user is not None}")  # Debug

        if not user:
            return jsonify({"error": "Invalid username or password."}), 401

        password_valid = check_password_hash(user.password_hash, password)
        print(f"Password valid: {password_valid}")  # Debug

        if not password_valid:
            return jsonify({"error": "Invalid username or password."}), 401

        # Set session
        session['username'] = username
        print(f"Session set for user: {username}")  # Debug
        print(f"Session contents: {dict(session)}")  # Debug

        return jsonify({
            "success": "Login successful.",
            "username": username,
            "redirect": "/profile"
        })

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug
        return jsonify({"error": "Login failed. Please try again."}), 500

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    if request.method == "GET":
        return redirect(url_for('index'))
    return jsonify({"success": "Logged out successfully."})

@app.route("/add", methods=["POST"])
def add():
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401

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
    new_password = Password(service=service, username=username, password_encrypted=encrypted_password, user_id=user.id)
    db.session.add(new_password)
    db.session.commit()

    return jsonify({"success": "Password added successfully."})

@app.route("/get/<service>", methods=["POST"])
def get(service):
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401

    logged_in_user = session['username']
    data = request.get_json()
    requested_username = data.get('username')

    if not requested_username:
        return jsonify({"error": "Username is required."}), 400

    try:
        user = User.query.filter_by(username=logged_in_user).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        password_entry = Password.query.filter_by(
            user_id=user.id, 
            service=service, 
            username=requested_username
        ).first()
        
        if not password_entry:
            return jsonify({"error": f"No password found for {requested_username} on {service}."}), 404

        decrypted_password = fernet.decrypt(password_entry.password_encrypted.encode()).decode()
        return jsonify({
            "username": requested_username, 
            "password": decrypted_password,
            "service": service
        })
    
    except Exception as e:
        return jsonify({"error": "Failed to retrieve password."}), 500

@app.route("/check-session", methods=["GET"])
def check_session():
    if 'username' in session:
        return jsonify({"logged_in": True, "username": session['username']})
    return jsonify({"logged_in": False})

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # Double-check the user exists in database
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.clear()  # Clear invalid session
        return redirect(url_for('index'))
    
    return render_template('profile.html')

@app.route("/get-services", methods=["GET"])
def get_services():
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    services = db.session.query(Password.service).filter_by(user_id=user.id).distinct().all()
    return jsonify([service[0] for service in services])

@app.route("/get-all-passwords", methods=["GET"])
def get_all_passwords():
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    passwords = Password.query.filter_by(user_id=user.id).all()
    result = []
    for pwd in passwords:
        decrypted_password = fernet.decrypt(pwd.password_encrypted.encode()).decode()
        result.append({
            "id": pwd.id,
            "service": pwd.service,
            "username": pwd.username,
            "password": decrypted_password
        })
    return jsonify(result)

@app.route("/view-passwords")
def view_passwords():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('view_passwords.html')

@app.route("/delete-password", methods=["POST"])
def delete_password():
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401
    
    data = request.get_json()
    password_id = data.get('id')
    
    if not password_id:
        return jsonify({"error": "Password ID is required."}), 400
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    password_entry = Password.query.filter_by(id=password_id, user_id=user.id).first()
    if not password_entry:
        return jsonify({"error": "Password not found."}), 404
    
    db.session.delete(password_entry)
    db.session.commit()
    
    return jsonify({"success": "Password deleted successfully."})

@app.route("/edit-password", methods=["POST"])
def edit_password():
    if 'username' not in session:
        return jsonify({"error": "Not logged in."}), 401
    
    data = request.get_json()
    password_id = data.get('id')
    new_password = data.get('password')
    
    if not password_id or not new_password:
        return jsonify({"error": "Password ID and new password are required."}), 400
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    password_entry = Password.query.filter_by(id=password_id, user_id=user.id).first()
    if not password_entry:
        return jsonify({"error": "Password not found."}), 404
    
    encrypted_password = fernet.encrypt(new_password.encode()).decode()
    password_entry.password_encrypted = encrypted_password
    db.session.commit()
    
    return jsonify({"success": "Password updated successfully."})

# Vercel entry point
def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(debug=True)