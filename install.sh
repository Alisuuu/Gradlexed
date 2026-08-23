#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/releases/download/0.5/backup_20260820_035641.zip"
TMP="/tmp/gradlexed_install"

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

rm -rf "$TMP"
mkdir -p "$TMP/extracted"

curl -fL "$URL" -o "$TMP/backup.zip"

echo "[*] Extraindo na raiz..."

unzip -q -o "$TMP/backup.zip" -d "$TMP/extracted"

echo "[*] Instalando arquivos em /..."

cp -af "$TMP/extracted"/. /

rm -rf "$TMP"

echo "[✓] Instalação concluída."
echo "[*] Iniciando /app.py..."
echo

exec python3 /app.py </dev/tty
