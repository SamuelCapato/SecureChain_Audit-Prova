from auth.auth import login
from blockchain.blockchain import Blockchain

bc = Blockchain()

usuario = input("Usuário: ")
senha = input("Senha: ")

if login(usuario, senha):

    print("Login bem-sucedido!")

    bc.add_block(
        f"LOGIN {usuario}"
    )

else:

    print("Acesso negado")

    bc.add_block(
        f"FALHA LOGIN {usuario}"
    )