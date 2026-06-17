import subprocess
from datetime import datetime

arquivo = f"audit_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

with open(arquivo, 'w') as f:

    comandos = [
        "who",
        "last -n 20",
        "ss -tuln",
        "ip a"
    ]

    for cmd in comandos:

        f.write(f"\n===== {cmd} =====\n")

        resultado = subprocess.getoutput(cmd)

        f.write(resultado + "\n")