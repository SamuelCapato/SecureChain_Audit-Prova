#!/bin/bash
# backup.sh — Backup seguro com compactação e criptografia AES-256
# Parte do projeto SecureChain Audit (RF05)
#
# Uso: execute a partir do diretório securechain/
#   bash backup/backup.sh

set -euo pipefail   # encerra imediatamente em caso de erro

# Configurações
DATA=$(date +"%Y-%m-%d-%H-%M-%S")
ARQUIVO="backup-${DATA}.tar.gz"
TEMP="/tmp/${ARQUIVO}"
DESTINO_DIR="$(dirname "$0")/../logs"      # securechain/logs/
DESTINO_ENC="${DESTINO_DIR}/backup-${DATA}.tar.gz.enc"
LOG="${DESTINO_DIR}/backup.log"
DOCS_DIR="$(dirname "$0")/../documentos"   # securechain/documentos/

# Chave de criptografia via variável de ambiente (nunca exposta no histórico)
if [ -z "${BACKUP_PASS:-}" ]; then
    echo "[ERRO] Variável BACKUP_PASS não definida."
    echo "       Execute: export BACKUP_PASS=\"sua_senha_forte\""
    exit 1
fi

mkdir -p "$DESTINO_DIR"

echo "[BACKUP] Iniciando backup em ${DATA}..."

# Passo 1: Compactação
tar -czf "$TEMP" -C "$(dirname "$DOCS_DIR")" documentos/
echo "[BACKUP] Compactação concluída: ${TEMP}"

# Passo 2: Criptografia AES-256-CBC com OpenSSL
# -pbkdf2 usa PBKDF2 para derivar a chave — mais seguro que -md md5 padrão
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in  "$TEMP" \
    -out "$DESTINO_ENC" \
    -pass env:BACKUP_PASS

echo "[BACKUP] Criptografia concluída: ${DESTINO_ENC}"

# Passo 3: Calcular tamanho do arquivo criptografado
SIZE=$(du -h "$DESTINO_ENC" | cut -f1)

# Passo 4: Remover arquivo temporário não criptografado
rm -f "$TEMP"

# Passo 5: Log local
echo "$(date --iso-8601=seconds) | STATUS=OK | ARQUIVO=${DESTINO_ENC} | TAMANHO=${SIZE}" >> "$LOG"
echo "[BACKUP] Backup concluído. Tamanho: ${SIZE}"

# Passo 6: Registrar evento na blockchain via Python
python3 - << PYEOF
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname("$0"), ".."))
from blockchain.blockchain import Blockchain
bc = Blockchain()
bc.add_block("BACKUP EXECUTADO | arquivo=${DESTINO_ENC} | tamanho=${SIZE}")
print("[BACKUP] Evento registrado na blockchain.")
PYEOF
