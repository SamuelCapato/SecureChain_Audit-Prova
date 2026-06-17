import hashlib
import json
import os

BASELINE = "/home/samuel/Downloads/SecureChain_Audit-Prova/securechain/baseline.json"
DOCS = "/home/samuel/Downloads/SecureChain_Audit-Prova/securechain/documentos/"

def gerar_hash(arquivo):
    
    h = hashlib.sha256()

    with open(arquivo,"rb") as f:

        while chunk := f.read(4096):
            h.update(chunk)

    return h.hexdigest()

def baseline():

    hashes = {}

    for arq in os.listdir(DOCS):

        caminho = os.path.join(DOCS, arq)

        if os.path.isfile(caminho):
            hashes[arq] = gerar_hash(caminho)
    
    with open(BASELINE,"w") as f:
        json.dump(hashes,f,indent=4)

def verificar():

    with open(BASELINE,"r") as f:
        antigo = json.load(f)

    atual = {}

    for arq in os.listdir(DOCS):

        caminho = os.path.join(DOCS, arq)

        if os.path.isfile(caminho):
            atual[arq] = gerar_hash(caminho)

    alterados = []

    for arquivo in antigo:

        if arquivo not in atual:
            alterados.append(f"REMOVIDO: {arquivo}")

        elif antigo[arquivo] != atual[arquivo]:
            alterados.append(f"ALTERADO: {arquivo}")
    
    for arquivo in atual:
        
        if arquivo not in antigo:
            alterados.append(f"NOVO: {arquivo}")

    return alterados