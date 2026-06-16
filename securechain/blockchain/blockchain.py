import json
import hashlib
from datetime import datetime
from pathlib import Path

CHAIN_FILE = "blockchain/chain.json"

class Blockchain:

    def __init__(self):
        self.chain = self.load()

        if len(self.chain) == 0:
            self.genesis()

    def claculate_hash(self, block):

        data = (
            str(block["id"]) +
            block["timestamp"] +
            block["evento"] +
            block["hash_anterior"]
        )

        return hashlib.sha256(
            data.encode()
        ).hexdigest()
    
    def genesis(self):

        bloco = {
            "id":0,
            "timestamp":datetime.now().isoformat(),
            "evento":"GENESIS",
            "hash_anterior":"0"
        }

        bloco["hash_atual"] = \
            self.calculate_hash(bloco)
        
        self.chain.append(bloco)

        self.save()

    def add_block(self, evento):

        ultimo = self.chain[-1]

        bloco = {
            "id":len(self.chain),
            "timestamp":datetime.now().isoformat(),
            "evento":evento,
            "hash_anterior":ultimo["hash_atual"]
        }

        bloco["hash_atual"] = \
            self.calculate_hash(bloco)
        
        self.chain.append(bloco)

        self.save()

    def save(self):
        with open(CHAIN_FILE, "w") as f:
            json.dump(self.chain,f,indent=4)

    def load(self):
        if Path(CHAIN_FILE).exists():
            with open(CHAIN_FILE) as f:
                return json.load(f)
        return []
    
    def validate(self):

        for i in range(1,len(self.chain)):

            atual = self.chain[i]
            anterior = self.chain[i-1]

            recalculado = self.calculate_hash(atual)

            if recalculado != atual["hash_atual"]:
                return False
            
            if atual["hash_anterior"] != anterior["hash_atual"]:
                return False
        
        return True
