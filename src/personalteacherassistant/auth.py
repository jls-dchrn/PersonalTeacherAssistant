import bcrypt
import json
import os

class AuthManager:
    USERS_FILE = "users.json"

    def __init__(self):
        self.users = self._load_users()
        self.session = {
            "authenticated": False,
            "username": None
        }

    def _load_users(self):
        if not os.path.exists(self.USERS_FILE):
            return {}
        with open(self.USERS_FILE, "r") as f:
            return json.load(f)

    def save_users(self):
        with open(self.USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=2)

    def login(self, username, password):
        if username not in self.users:
            return False, "❌ Unknown user."
        
        hashed = self.users[username]['password_hash'].encode()
        if bcrypt.checkpw(password.encode(), hashed):
            self.session["authenticated"] = True
            self.session["username"] = username
            return True, ""
        return False, "❌ Incorrect password."


    def logout(self):
        self.session["authenticated"] = False
        self.session["username"] = None

    def add_user(self, username, password):
        if username in self.users:
            raise ValueError("User already exists.")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.users[username] = {"password_hash": hashed}
        self.save_users()

    def get_session(self):
        return self.session
