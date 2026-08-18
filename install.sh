#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/releases/latest/download/Gradlexed.zip"
DIR="$(pwd)"
TMP="/tmp/gradlexed"

echo "[*] Verificando ambiente..."

if [ ! -d "$DIR" ]; then
    echo "[!] Diretório inválido."
    exit 1
fi

command -v curl >/dev/null 2>&1 || {
    echo "[*] Instalando curl..."
    apt update && apt install -y curl
}

command -v unzip >/dev/null 2>&1 || {
    echo "[*] Instalando unzip..."
    apt update && apt install -y unzip
}

command -v python3 >/dev/null 2>&1 || {
    echo "[*] Instalando Python..."
    apt update && apt install -y python3
}

echo "[*] Baixando..."

rm -rf "$TMP"
mkdir -p "$TMP"

curl -fL "$URL" -o "$TMP/app.zip"

if ! file "$TMP/app.zip" | grep -qi zip; then
    echo "[!] O download não é um ZIP válido."
    exit 1
fi

echo "[*] Extraindo..."

unzip -q -o "$TMP/app.zip" -d "$TMP/extracted"

echo "[*] Instalando arquivos..."

# Se o ZIP tiver uma pasta única, entra nela
ROOT="$TMP/extracted"

COUNT=$(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | wc -l)

if [ "$COUNT" = "1" ] && [ "$(find "$ROOT" -mindepth 1 -maxdepth 1 -type f | wc -l)" = "0" ]; then
    ROOT="$(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | head -1)"
fi

cp -af "$ROOT"/. "$DIR"/

rm -rf "$TMP"

echo "[✓] Instalação concluída."

if [ -f "$DIR/app.py" ]; then
    echo "[*] Executando app.py..."
    exec python3 "$DIR/app.py"
else
    echo "[!] app.py não encontrado."
    exit 1
fi
