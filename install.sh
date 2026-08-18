#!/bin/sh

set -e

URL="https://github.com/Alisuuu/Gradlexed/archive/refs/heads/main.zip"
TMP="/tmp/gradlexed"
DIR="$(pwd)"

echo "[*] Verificando ambiente..."

# Verifica se está em uma pasta válida
if [ ! -d "$DIR" ]; then
    echo "[!] Diretório inválido."
    exit 1
fi

# Instala curl
if ! command -v curl >/dev/null 2>&1; then
    echo "[*] Instalando curl..."
    apt update
    apt install -y curl
fi

# Instala unzip
if ! command -v unzip >/dev/null 2>&1; then
    echo "[*] Instalando unzip..."
    apt update
    apt install -y unzip
fi

# Instala Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "[*] Instalando Python3..."
    apt update
    apt install -y python3
fi

echo "[*] Baixando..."

rm -rf "$TMP"
mkdir -p "$TMP"

curl -fL "$URL" -o "$TMP/main.zip"

# Verifica se o arquivo realmente é um ZIP
if ! unzip -t "$TMP/main.zip" >/dev/null 2>&1; then
    echo "[!] O download não é um ZIP válido."
    rm -rf "$TMP"
    exit 1
fi

echo "[*] Extraindo..."

unzip -q -o "$TMP/main.zip" -d "$TMP"

ROOT="$TMP/Gradlexed-main"

# Verifica estrutura
if [ ! -d "$ROOT" ]; then
    echo "[!] Pasta Gradlexed-main não encontrada no ZIP."
    rm -rf "$TMP"
    exit 1
fi

echo "[*] Instalando em:"
echo "    $DIR"

# Copia TUDO, incluindo arquivos ocultos
cp -af "$ROOT"/. "$DIR"/

# Limpa temporários
rm -rf "$TMP"

echo "[✓] Arquivos instalados."
echo "[*] Executando app.py..."
echo

# Garante que o app receba stdin do terminal
if [ -e /dev/tty ]; then
    exec python3 "$DIR/app.py" </dev/tty
else
    exec python3 "$DIR/app.py"
fi
