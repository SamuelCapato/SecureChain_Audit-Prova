import json
import hashlib
from datetime import datetime
from pathlib import Path

# Caminho relativo ao diretório onde o script está sendo executado (securechain/)
CHAIN_FILE = Path(__file__).parent / "chain.json"


class Blockchain:

    def __init__(self):
        self.chain = self.load()

        if len(self.chain) == 0:
            self.genesis()

    def calculate_hash(self, block):
        """Recalcula o SHA-256 de um bloco com base em seus campos fixos."""
        data = (
            str(block["id"]) +
            block["timestamp"] +
            block["evento"] +
            block["hash_anterior"]
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def genesis(self):
        """Cria o bloco inicial (genesis) da cadeia."""
        bloco = {
            "id": 0,
            "timestamp": datetime.now().isoformat(),
            "evento": "GENESIS - Blockchain inicializada",
            "hash_anterior": "0" * 64   # padrão: 64 zeros, não apenas "0"
        }
        bloco["hash_atual"] = self.calculate_hash(bloco)

        self.chain.append(bloco)
        self.save()

    def add_block(self, evento):
        """Adiciona um novo bloco ao final da cadeia e persiste."""
        ultimo = self.chain[-1]

        bloco = {
            "id": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "hash_anterior": ultimo["hash_atual"]
        }
        bloco["hash_atual"] = self.calculate_hash(bloco)

        self.chain.append(bloco)
        self.save()

    def save(self):
        """Persiste a cadeia no arquivo chain.json."""
        with open(CHAIN_FILE, "w") as f:
            json.dump(self.chain, f, indent=4, ensure_ascii=False)

    def load(self):
        """Carrega a cadeia do arquivo chain.json, se existir."""
        if CHAIN_FILE.exists():
            with open(CHAIN_FILE) as f:
                return json.load(f)
        return []

    def validate(self):
        """
        Percorre toda a cadeia verificando:
          1. O hash armazenado bate com o recalculado (adulteração direta)
          2. O hash_anterior bate com o hash_atual do bloco anterior (encadeamento)

        Retorna (True, None) se a cadeia está íntegra.
        Retorna (False, id_do_bloco) identificando o primeiro bloco corrompido.
        """
        # Valida o bloco genesis separadamente
        recalculado = self.calculate_hash(self.chain[0])
        if recalculado != self.chain[0]["hash_atual"]:
            return False, 0

        for i in range(1, len(self.chain)):
            atual = self.chain[i]
            anterior = self.chain[i - 1]

            # Verificação 1: hash armazenado vs recalculado
            recalculado = self.calculate_hash(atual)
            if recalculado != atual["hash_atual"]:
                return False, atual["id"]

            # Verificação 2: encadeamento com o bloco anterior
            if atual["hash_anterior"] != anterior["hash_atual"]:
                return False, atual["id"]

        return True, None

    def exibir(self):
        """Exibe a cadeia completa no terminal (útil para debug/demo)."""
        for bloco in self.chain:
            print(f"\n[Bloco {bloco['id']}]")
            print(f"  Timestamp  : {bloco['timestamp']}")
            print(f"  Evento     : {bloco['evento']}")
            print(f"  Hash ant.  : {bloco['hash_anterior'][:16]}...")
            print(f"  Hash atual : {bloco['hash_atual'][:16]}...")
