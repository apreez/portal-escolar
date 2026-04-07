import json
import bcrypt
from pathlib import Path
from datetime import datetime

USERS_FILE = Path("users.json")

def _load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def _save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def verify_login(username, password):
    users = _load_users()
    user = users.get(username)
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return user
    return None

def add_user(username, password, role="viewer", name=""):
    users = _load_users()
    if username in users:
        print(f"El usuario '{username}' ya existe")
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {
        "password": hashed,
        "role": role,
        "name": name or username,
        "created": datetime.now().isoformat()
    }
    _save_users(users)
    print(f"Usuario '{username}' creado!")
    return True

def delete_user(username):
    users = _load_users()
    if username not in users:
        print(f"Usuario '{username}' no encontrado")
        return False
    del users[username]
    _save_users(users)
    print(f"Usuario '{username}' eliminado")
    return True

def list_users():
    users = _load_users()
    for username, info in users.items():
        print(f"{username} | {info['role']} | {info['name']}")

def change_password(username, new_password):
    users = _load_users()
    if username not in users:
        print(f"Usuario '{username}' no encontrado")
        return False
    users[username]["password"] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    _save_users(users)
    print(f"Contraseña actualizada!")
    return True

# Crear admin por defecto al iniciar
def init_default_users():
    users = _load_users()
    if "admin" not in users:
        add_user("admin", "admin123", "admin", "Administrador")
    if "yanira" not in users:
        add_user("yanira", "pascualateamo", "editor", "Yanira")
    if "pascuala" not in users:
        add_user("pascuala", "papitoteamo", "editor", "Pascuala")

init_default_users()