import hashlib
import json
import os
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------ #
# CORREÇÃO: caminhos absolutos hardcoded removidos — usa Path relativo
# ------------------------------------------------------------------ #
BASE_DIR  = Path(__file__).parent
BASELINE  = BASE_DIR / "baseline.json"
DOCS      = BASE_DIR / "documentos"


def gerar_hash(arquivo):
    """Calcula SHA-256 de um arquivo lendo em blocos de 4 KB (eficiente)."""
    h = hashlib.sha256()
    with open(arquivo, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()


def criar_baseline():
    """
    Percorre /documentos, calcula o SHA-256 de cada arquivo e
    salva o baseline em baseline.json com timestamp.
    Deve ser chamado na inicialização do sistema (RF03).
    """
    DOCS.mkdir(parents=True, exist_ok=True)
    hashes = {}

    for arq in os.listdir(DOCS):
        caminho = DOCS / arq
        if caminho.is_file() and arq != ".gitkeep":
            hashes[arq] = gerar_hash(caminho)

    baseline_data = {
        "gerado_em": datetime.now().isoformat(),
        "hashes": hashes
    }

    with open(BASELINE, "w") as f:
        json.dump(baseline_data, f, indent=4, ensure_ascii=False)

    print(f"[MONITOR] Baseline criado com {len(hashes)} arquivo(s).")
    return hashes


def verificar(blockchain=None):
    """
    Compara o estado atual de /documentos com o baseline salvo.
    Detecta: arquivos ALTERADOS, REMOVIDOS e NOVOS.

    Se um objeto Blockchain for passado, cada evento é registrado
    como bloco imutável (RF03 + RF04).

    Retorna lista de strings descrevendo cada alteração encontrada.
    """
    if not BASELINE.exists():
        print("[MONITOR] Baseline não encontrado. Criando agora...")
        criar_baseline()
        return []

    with open(BASELINE, "r") as f:
        baseline_data = json.load(f)

    # Compatibilidade: baseline antigo pode não ter a chave "hashes"
    antigo = baseline_data.get("hashes", baseline_data)

    atual = {}
    for arq in os.listdir(DOCS):
        caminho = DOCS / arq
        if caminho.is_file() and arq != ".gitkeep":
            atual[arq] = gerar_hash(caminho)

    alteracoes = []

    for arquivo in antigo:
        if arquivo not in atual:
            msg = f"ARQUIVO REMOVIDO: {arquivo}"
            alteracoes.append(msg)
            print(f"[ALERTA] {msg}")
            if blockchain:
                blockchain.add_block(msg)

        elif antigo[arquivo] != atual[arquivo]:
            msg = f"ARQUIVO ALTERADO: {arquivo}"
            alteracoes.append(msg)
            print(f"[ALERTA] {msg}")
            if blockchain:
                blockchain.add_block(msg)

    for arquivo in atual:
        if arquivo not in antigo:
            msg = f"ARQUIVO NOVO: {arquivo}"
            alteracoes.append(msg)
            print(f"[ALERTA] {msg}")
            if blockchain:
                blockchain.add_block(msg)

    if not alteracoes:
        print("[MONITOR] Integridade OK — nenhuma alteração detectada.")

    return alteracoes
