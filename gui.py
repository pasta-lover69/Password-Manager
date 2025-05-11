import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import os, json

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

def load_passwords():
    if not os.path.exists(PASS_FILE):
        with open(PASS_FILE, 'w') as f:
            json.dump({}, f)
    with open(PASS_FILE, 'r') as f:
        return json.load(f)

def save_passwords(passwords):
    with open(PASS_FILE , 'w') as f:
      json.dump(passwords, f)

def add_password():
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    if service and username and password:
      ecrypted = fernet.encrypt(password.encode()).decode()
      passwords = load_passwords()
      passwords[service] = {
        'username': username,
        'password': ecrypted
      }
      save_passwords(passwords)
      messagebox.showinfo("Success", "Password added successfully!")
    else:
      messagebox.showerror("Error", "Please fill in all fields.")
    
def get_password():
    service = service_entry.get()
    passwords = load_passwords()
    if service in passwords:
      username = passwords[service]['username']
      decrypted = fernet.decrypt(passwords[service]['password'].encode()).decode()
      messagebox.showinfo("Retrieved", f"Username: {username}\nPassword: {decrypted}")
    else:
      messagebox.showerror("Error", "Service not found.")
    
root = tk.Tk()
root.title("Password Manager")

tk.Label(root, text="Service").grid(row=0, column=0)
tk.Label(root, text="Username").grid(row=1, column=0)
tk.Label(root, text="Password").grid(row=2, column=0)

service_entry = tk.Entry(root)
username_entry = tk.Entry(root)
password_entry = tk.Entry(root, show='*')

service_entry.grid(row=0, column=1)
username_entry.grid(row=1, column=1)
password_entry.grid(row=2, column=1)

tk.Button(root, text="Add Password", command=add_password).grid(row=3, column=0)
tk.Button(root, text="Get Password", command=get_password).grid(row=3, column=1)

root.mainloop()