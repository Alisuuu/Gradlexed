#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/archive/refs/heads/main.zip"
TMP="/tmp/gradlexed"
DIR="$(pwd)"

echo "[*] Verificando dependências..."

command -v curl >/dev/null 2>&1 || {
    apt update && apt install -y curl
}

command -v unzip >/dev/null 2>&1 || {
    apt update && apt install -y unzip
}

command -v python3 >/dev/null 2>&1 || {
    apt update && apt install -y python3
}

echo "[*] Baixando Gradlexed..."

rm -rf "$TMP"
mkdir -p "$TMP"

curl -fL "$URL" -o "$TMP/main.zip"

echo "[*] Extraindo..."

unzip -q -o "$TMP/main.zip" -d "$TMP"

ROOT="$TMP/Gradlexed-main"

if [ ! -d "$ROOT" ]; then
    echo "[!] Estrutura do ZIP inválida."
    exit 1
fi

echo "[*] Copiando arquivos para: $DIR"

cp -af "$ROOT"/. "$DIR"/

rm -rf "$TMP"

echo "[✓] Concluído."

exec python3 "$DIR/app.py"
