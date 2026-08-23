#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/releases/download/0.5/backup_20260820_035641.zip"
ZIP="/tmp/gradlexed_backup.zip"

echo "[*] Verificando ambiente..."

command -v curl >/dev/null 2>&1 || {
    apt update
    apt install -y curl
}

command -v unzip >/dev/null 2>&1 || {
    apt update
    apt install -y unzip
}

command -v python3 >/dev/null 2>&1 || {
    apt update
    apt install -y python3
}

echo "[*] Baixando..."

rm -f "$ZIP"
curl -fL "$URL" -o "$ZIP"

echo "[*] Extraindo na raiz..."

unzip -o "$ZIP" -d /

rm -f "$ZIP"

echo "[✓] Arquivos instalados."
echo "[*] Executando /app.py..."
echo

python3 /app.py
