#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/releases/download/0.5/backup_20260818_230405.zip"
TMP="/tmp/backup_20260818_230405"
DIR="$(pwd)"

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
mkdir -p "$TMP"

curl -fL "$URL" -o "$TMP/backup.zip"

echo "[*] Extraindo..."

unzip -q -o "$TMP/backup.zip" -d "$TMP/extracted"

echo "[*] Instalando em $DIR..."

cp -af "$TMP/extracted"/. "$DIR"/

rm -rf "$TMP"

echo "[✓] Instalação concluída."
echo "[*] Iniciando app..."
echo

exec python3 "$DIR/app.py"
