import json
import bcrypt
from datetime import datetime

USERS_FILE = "/home/samuel/Downloads/SecureChain_Audit-Prova/securechain/usuarios/users.json"

def carregar():
    try:
        with open(USERS_FILE,"r") as f:
            return json.load(f)
    except:
        return

def salvar(users):
    with open(USERS_FILE,"w") as f:
        json.dump(users,f,indent=4)

def cadastrar(usuario, senha, perfil):

    users = carregar()

    salt = bcrypt.gensalt()

    senha_hash = bcrypt.hashpw(
        senha.encode(),
        salt
    ).decode()

    users[usuario] = {
        "senha": senha_hash,
        "perfil": perfil,
        "criado": datetime.now().isoformat()
    }

    salvar(users)

def login(usuario, senha):

    users = carregar()

    if usuario not in users:
        return False
    
    senha_hash = users[usuario]["senha"]

    return bcrypt.checkpw(
        senha.encode(),
        senha_hash.encode()
    )