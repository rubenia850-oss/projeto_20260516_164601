import hashlib
import time
from typing import Optional, Dict
import bcrypt
import jwt

SECRET_KEY = "llm-calculadora-2026-jwt-secret"

class AuthService:
    def __init__(self, db_path: str = "data/users.db"):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def register_user(self, user_id: str, password: str) -> bool:
        c = self.conn.cursor()
        if c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,)).fetchone():
            return False
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (user_id, password_hash) VALUES (?, ?)", (user_id, hashed))
        self.conn.commit()
        return True

    def authenticate(self, user_id: str, password: str) -> Optional[str]:
        c = self.conn.cursor()
        row = c.execute("SELECT password_hash FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return None
        if bcrypt.checkpw(password.encode(), row[0].encode()):
            payload = {"user_id": user_id, "exp": time.time() + 3600}
            return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return None

    def validate_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["user_id"]
        except:
            return None
