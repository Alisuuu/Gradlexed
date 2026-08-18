#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Cores
R='\033[1;31m'
B='\033[1;34m'
A='\033[36m'
N='\033[0m'

h() {
    echo ""
    echo -e "  ${B}────────────────────────────────${N}"
    echo -e "  ${B}$1${N}"
    echo -e "  ${B}────────────────────────────────${N}"
}

h "CORRIGIR ADB"

# Verificar se adb ja funciona
if adb version > /dev/null 2>&1; then
    VERSION=$(adb version | head -1)
    ARCH=$(adb version | grep -o "arm64\|x86_64\|aarch64" || echo "unknown")
    echo -e "  ${R}✔${N} ADB ja funciona: $VERSION ($ARCH)"
    echo ""
    adb devices 2>&1 | sed 's/^/  /'
    echo ""
    exit 0
fi

echo -e "  ${A}→${N} ADB do SDK e x86-64 e nao roda em ARM64"
echo -e "  ${A}→${N} Instalando ADB nativo ARM64..."

# Detectar gerenciador de pacotes
if command -v apt-get > /dev/null 2>&1; then
    apt-get install -y adb 2>&1 | sed 's/^/  /'
elif command -v pkg > /dev/null 2>&1; then
    pkg install adb -y 2>&1 | sed 's/^/  /'
else
    echo -e "  ${R}✗${N} Gerenciador de pacotes nao encontrado!"
    echo -e "  ${A}→${N} Instale manualmente: apt-get install -y adb"
    exit 1
fi

# Verificar se instalou
if ! adb version > /dev/null 2>&1; then
    echo -e "  ${R}✗${N} Falha ao instalar ADB!"
    exit 1
fi

VERSION=$(adb version | head -1)
echo ""
echo -e "  ${R}✔${N} ADB instalado com sucesso!"
echo -e "  ${A}→${N} $VERSION"
echo ""
echo -e "  ${A}→${N} Dispositivos conectados:"
adb devices 2>&1 | sed 's/^/  /'
echo ""
