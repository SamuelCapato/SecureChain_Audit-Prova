"""
main.py — Ponto de entrada do SecureChain Audit
Integra autenticação, blockchain, monitoramento e auditoria (RF02, RF03, RF04, RF06, RF07)

Uso (a partir do diretório securechain/):
    python3 main.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Garante que os imports funcionam a partir de qualquer diretório
sys.path.insert(0, str(Path(__file__).parent))

from auth import login, cadastrar, listar_usuarios, remover_usuario
from blockchain.blockchain import Blockchain
from monitor import criar_baseline, verificar
from auditoria.auditor import coletar


def menu_principal(usuario, perfil, bc):
    """Exibe o menu de acordo com o perfil do usuário logado."""
    while True:
        print(f"\n{'='*50}")
        print(f"  SecureChain Audit  |  Usuário: {usuario}  |  Perfil: {perfil}")
        print(f"{'='*50}")
        print("  [1] Verificar integridade de arquivos")
        print("  [2] Validar blockchain")
        print("  [3] Exibir blockchain")
        print("  [4] Gerar relatório de auditoria do sistema")

        if perfil == "admin":
            print("  [5] Criar baseline de arquivos")
            print("  [6] Cadastrar novo usuário")
            print("  [7] Listar usuários")
            print("  [8] Remover usuário")

        print("  [0] Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            print("\n[MONITOR] Verificando integridade...")
            alteracoes = verificar(blockchain=bc)
            if not alteracoes:
                print("Todos os arquivos estão íntegros.")
            else:
                print(f"\n{len(alteracoes)} alteração(ões) detectada(s) e registrada(s) na blockchain.")

        elif opcao == "2":
            ok, bloco_corrompido = bc.validate()
            if ok:
                print("\n[BLOCKCHAIN] Cadeia íntegra — nenhuma adulteração detectada.")
            else:
                print(f"\n[ALERTA] Cadeia corrompida! Bloco inválido: #{bloco_corrompido}")
                bc.add_block(f"ALERTA: Corrupção detectada no bloco #{bloco_corrompido}")

        elif opcao == "3":
            bc.exibir()

        elif opcao == "4":
            caminho = coletar()
            print(f"Relatório gerado: {caminho}")
            bc.add_block(f"AUDITORIA DO SISTEMA EXECUTADA | arquivo={caminho}")

        elif opcao == "5" and perfil == "admin":
            criar_baseline()
            bc.add_block("BASELINE DE INTEGRIDADE CRIADO")

        elif opcao == "6" and perfil == "admin":
            novo_user  = input("Nome do usuário: ").strip()
            nova_senha = input("Senha: ").strip()
            novo_perfil = input("Perfil (admin/analista/visitante): ").strip()
            try:
                ok = cadastrar(novo_user, nova_senha, novo_perfil)
                if ok:
                    print(f"Usuário '{novo_user}' cadastrado.")
                    bc.add_block(f"USUÁRIO CADASTRADO: {novo_user} | perfil={novo_perfil}")
                else:
                    print(f"Usuário '{novo_user}' já existe.")
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "7" and perfil == "admin":
            usuarios = listar_usuarios()
            print(f"\n{'Nome':<20} {'Perfil':<12} {'Criado em'}")
            print("-" * 55)
            for nome, dados in usuarios.items():
                print(f"{nome:<20} {dados['perfil']:<12} {dados['criado']}")

        elif opcao == "8" and perfil == "admin":
            alvo = input("Nome do usuário a remover: ").strip()
            if alvo == usuario:
                print("Você não pode remover o próprio usuário.")
            else:
                ok = remover_usuario(alvo)
                if ok:
                    print(f"Usuário '{alvo}' removido.")
                    bc.add_block(f"USUÁRIO REMOVIDO: {alvo}")
                else:
                    print(f"Usuário '{alvo}' não encontrado.")

        elif opcao == "0":
            bc.add_block(f"LOGOUT: {usuario}")
            print("Sessão encerrada.")
            break

        else:
            print("Opção inválida ou sem permissão.")


def main():
    # Muda o diretório de trabalho para securechain/ independentemente de onde
    # o script for chamado — garante que os caminhos relativos funcionem
    os.chdir(Path(__file__).parent)

    bc = Blockchain()

    print("\n" + "="*50)
    print("   SecureChain Audit — Sistema de Auditoria")
    print("="*50)

    # Verificar se existe ao menos um usuário; se não, forçar criação do admin
    from auth import carregar
    if not carregar():
        print("\n[SETUP] Nenhum usuário encontrado.")
        print("[SETUP] Criando conta de administrador inicial...\n")
        usuario  = input("Nome do administrador: ").strip()
        senha    = input("Senha: ").strip()
        cadastrar(usuario, senha, "admin")
        bc.add_block(f"SETUP INICIAL: administrador '{usuario}' criado")
        print(f"\nAdministrador '{usuario}' criado. Faça login para continuar.\n")

    # Loop de autenticação
    tentativas = 0
    MAX_TENTATIVAS = 3

    while tentativas < MAX_TENTATIVAS:
        print(f"\n{'='*50}")
        usuario = input("Usuário: ").strip()
        senha   = input("Senha: ").strip()

        dados = login(usuario, senha)

        if dados:
            perfil = dados["perfil"]
            timestamp = datetime.now().isoformat()
            print(f"\nLogin bem-sucedido! Perfil: {perfil}")
            bc.add_block(
                f"LOGIN: {usuario} | perfil={perfil} | timestamp={timestamp}"
            )
            menu_principal(usuario, perfil, bc)
            break
        else:
            tentativas += 1
            restantes = MAX_TENTATIVAS - tentativas
            print(f"Acesso negado. Tentativas restantes: {restantes}")
            bc.add_block(
                f"FALHA DE LOGIN: usuário='{usuario}' | tentativa={tentativas}"
            )

    if tentativas == MAX_TENTATIVAS:
        print("\n[ALERTA] Número máximo de tentativas atingido. Acesso bloqueado.")
        bc.add_block(f"BLOQUEIO: usuário '{usuario}' excedeu tentativas de login")
        sys.exit(1)


if __name__ == "__main__":
    main()
