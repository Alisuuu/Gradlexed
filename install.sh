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

echo "[*] Preparando..."

rm -rf "$TMP"
mkdir -p "$TMP/extracted"

echo "[*] Baixando..."

curl -fL "$URL" -o "$TMP/backup.zip"

echo "[*] Extraindo..."

unzip -q -o "$TMP/backup.zip" -d "$TMP/extracted"

echo "[*] Localizando app.py..."

APP=$(find "$TMP/extracted" -type f -name "app.py" -print -quit)

if [ -z "$APP" ]; then
    echo "[!] app.py não encontrado no backup."
    echo
    echo "[*] Conteúdo encontrado:"
    find "$TMP/extracted" -maxdepth 3 -type f
    exit 1
fi

BASE=$(dirname "$APP")

echo "[*] Instalando conteúdo de:"
echo "    $BASE"
echo
echo "[*] Destino: /"

cp -af "$BASE"/. /

rm -rf "$TMP"

if [ ! -f /app.py ]; then
    echo "[!] Erro: /app.py não foi instalado."
    exit 1
fi

echo
echo "[✓] Instalação concluída."
echo "[✓] /app.py encontrado."
echo "[*] Iniciando..."
echo

exec python3 /app.py
