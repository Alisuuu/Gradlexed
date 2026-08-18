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

curl -fL "$URL" -o "$TMP/backup_20260818_230405.zip"

echo "[*] Extraindo..."

unzip -q -o "$TMP/backup_20260818_230405.zip" -d "$TMP"

ROOT="$TMP/backup_20260818_230405"

if [ ! -d "$ROOT" ]; then
    echo "[!] Estrutura do ZIP inválida."
    exit 1
fi

echo "[*] Instalando em $DIR..."

cp -af "$ROOT"/. "$DIR"/

rm -rf "$TMP"

echo "[✓] Instalação concluída."
echo "[*] Iniciando app..."
echo

# Executa usando o terminal real
if [ -c /dev/tty ]; then
    python3 "$DIR/app.py" < /dev/tty > /dev/tty 2>&1
else
    echo "[!] Terminal interativo não encontrado."
    echo "[!] Execute diretamente:"
    echo "    python3 $DIR/app.py"
    exit 1
fi
