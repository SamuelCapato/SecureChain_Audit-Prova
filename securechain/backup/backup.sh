#!/bin/bash

DATA=$(date +"%Y-%m-%d-%H-%M-%S")

ARQUIVO="backup-$DATA.tar.gz"

DESTINO="/tmp/$ARQUIVO"

tar -czvf "$DESTINO" documentos/

openssl enc -aes-256-cbc -salt -in "$DESTINO" -out "$DESTINO.enc -pass pass:SecureChain

SIZE=$(du -h "$DESTINO.enc" | cut -f1)

echo "$(date) BACKUP OK $SIZE" >> logs/backup.log

rm "$DESTINO"