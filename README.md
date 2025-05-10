# 🔐 Password Manager

A secure and user-friendly password manager built with Flask for the backend, a modern HTML/CSS/JavaScript frontend, and an optional Tkinter-based GUI for desktop use. This application allows users to securely store, retrieve, and manage passwords for various services.

---

## ✨ Features

- 🔒 **Secure Password Storage**: Passwords are encrypted using the `cryptography` library.
- 📋 **Service Selection**: Predefined services like Facebook, Spotify, Netflix, Instagram, Twitter, and TikTok.
- 🌐 **Modern Web Interface**: A responsive and visually appealing frontend built with HTML, CSS, and JavaScript.
- 🖥️ **Desktop GUI**: A Tkinter-based GUI for local use.
- 🔍 **Password Retrieval**: Retrieve stored passwords securely.
- 🚪 **Exit Feature**: Option to exit the application after retrieving a password.

---

## 🛠️ Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Encryption**: `cryptography` library
- **Desktop GUI**: Tkinter
- **Data Storage**: JSON file (`passwords.json`)

---

## 🚀 Installation

### Prerequisites
- 🐍 Python 3.x installed on your system
- 📦 `pip` (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/password-manager.git
   cd password-manager
   ```

2. Install dependencies:
   ```bash
   pip install flask cryptography
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 📂 File Structure

```
Password Manager/
├── 📄 app.py               # Flask backend
├── 📄 gui.py               # Tkinter-based GUI
├── 📁 templates/           # Frontend HTML templates
│   └── 📄 index.html       # Main HTML file
├── 📁 static/              # Frontend static files
│   ├── 🎨 style.css        # CSS for styling
│   └── ✨ main.js          # JavaScript for interactivity
├── 📄 passwords.json       # Encrypted password storage
├── 🔑 key.key              # Encryption key
└── 📄 README.md            # Project documentation
```

---

## 📞 Contact

For questions or support, please contact:

- **Name**: Jayvien Mocallay  
- **Email**: [jayvienmocallay7@example.com](mailto:jayvienmocallay7@example.com)

---

Let me know if you'd like further adjustments or enhancements!
