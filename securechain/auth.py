import json
import bcrypt
from datetime import datetime
from pathlib import Path

USERS_FILE = Path(__file__).parent / "usuarios" / "users.json"


def carregar():
    """Carrega o dicionário de usuários do arquivo JSON."""
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def salvar(users):
    """Persiste o dicionário de usuários no arquivo JSON."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def cadastrar(usuario, senha, perfil):
    """
    Cadastra um novo usuário com senha em hash bcrypt.
    Perfis aceitos: admin, analista, visitante.
    Retorna True em caso de sucesso, False se o usuário já existe.
    """
    perfis_validos = {"admin", "analista", "visitante"}
    if perfil not in perfis_validos:
        raise ValueError(f"Perfil inválido. Use um de: {perfis_validos}")

    users = carregar()

    if usuario in users:
        return False   # usuário já existe

    # bcrypt gera o salt internamente e o embute no hash — não precisa guardá-lo
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    users[usuario] = {
        "senha": senha_hash,
        "perfil": perfil,
        "criado": datetime.now().isoformat()
    }

    salvar(users)
    return True


def login(usuario, senha):
    """
    Verifica credenciais.
    Retorna o dict do usuário (com perfil) em caso de sucesso, ou None se falhar.
    """
    users = carregar()

    if usuario not in users:
        return None

    dados = users[usuario]
    senha_correta = bcrypt.checkpw(senha.encode(), dados["senha"].encode())

    if senha_correta:
        return dados   # retorna perfil, data de criação, etc.
    return None


def listar_usuarios():
    """Lista todos os usuários cadastrados (sem expor as senhas)."""
    users = carregar()
    resultado = {}
    for nome, dados in users.items():
        resultado[nome] = {
            "perfil": dados["perfil"],
            "criado": dados["criado"]
        }
    return resultado


def remover_usuario(usuario):
    """Remove um usuário existente. Retorna True se removido, False se não existia."""
    users = carregar()
    if usuario not in users:
        return False
    del users[usuario]
    salvar(users)
    return True
