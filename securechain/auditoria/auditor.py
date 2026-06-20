import subprocess
from datetime import datetime
from pathlib import Path

# Caminho relativo ao próprio arquivo — funciona em qualquer máquina
RELATORIOS = Path(__file__).parent / "relatorios"


def coletar():
    """
    Coleta informações do sistema operacional (RF06):
      - who       : usuários conectados no momento
      - last -n20 : histórico dos últimos 20 logins
      - ss -tuln  : portas e serviços em escuta
      - ip a      : interfaces de rede e endereços IP

    Salva um relatório datado em auditoria/relatorios/
    e retorna o caminho do arquivo gerado.
    """
    RELATORIOS.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    arquivo = RELATORIOS / f"audit_{timestamp}.txt"

    comandos = [
        ("who",        "Usuários conectados no momento"),
        ("last -n 20", "Histórico dos últimos 20 logins"),
        ("ss -tuln",   "Portas e serviços em escuta"),
        ("ip a",       "Interfaces de rede e endereços IP"),
    ]

    with open(arquivo, "w") as f:
        f.write(f"SecureChain Audit — Relatório do Sistema\n")
        f.write(f"Gerado em: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n")

        for cmd, descricao in comandos:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"COMANDO : {cmd}\n")
            f.write(f"DESCRIÇÃO: {descricao}\n")
            f.write(f"{'=' * 60}\n")
            resultado = subprocess.getoutput(cmd)
            f.write(resultado + "\n")

    print(f"[AUDITORIA] Relatório salvo em: {arquivo}")
    return str(arquivo)


if __name__ == "__main__":
    coletar()
