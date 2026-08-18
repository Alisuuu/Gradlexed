#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJETO_DIR="$SCRIPT_DIR/projeto"
OUTPUT_DIR="$SCRIPT_DIR/apks"

# Carregar ambiente se existir
if [ -f "$SCRIPT_DIR/.ambiente" ]; then
    source "$SCRIPT_DIR/.ambiente"
fi

# Garantir ANDROID_HOME
export ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

TIPO="${1:-debug}"

echo "=== Buildando APK ==="
echo "Tipo: $TIPO"
echo "Projeto: $PROJETO_DIR"

mkdir -p "$OUTPUT_DIR"

cd "$PROJETO_DIR"

case "$TIPO" in
    debug)
        echo ""
        echo "[1/2] Buildando debug APK..."
        bash gradlew assembleDebug --no-daemon 2>&1
        APK=$(find app/build/outputs/apk/debug -name "*.apk" 2>/dev/null | head -1)
        if [ -n "$APK" ]; then
            mv "$APK" "$OUTPUT_DIR/app-debug.apk"
            echo ""
            echo "=== Debug APK pronto ==="
            echo "Salvo em: $OUTPUT_DIR/app-debug.apk"
        else
            echo "ERRO: APK nao gerado"
            exit 1
        fi
        ;;
    release)
        echo ""
        echo "[1/3] Buildando release APK..."
        bash gradlew assembleRelease --no-daemon 2>&1
        APK=$(find app/build/outputs/apk/release -name "*.apk" ! -name "*.idsig" 2>/dev/null | head -1)
        if [ -n "$APK" ]; then
            echo "  APK unsigned encontrado: $APK"
        else
            echo "ERRO: APK release nao gerado"
            exit 1
        fi

        echo ""
        echo "[2/3] Assinando com chave do projeto..."
        RELEASE_KEYSTORE="$SCRIPT_DIR/alauncher.keystore"
        if [ ! -f "$RELEASE_KEYSTORE" ]; then
            echo "  ERRO: Keystore nao encontrado em $RELEASE_KEYSTORE"
            exit 1
        fi

        SIGNED_APK="$OUTPUT_DIR/app-release-signed.apk"
        rm -f "$SIGNED_APK"

        for VER in 36.0.0 35.0.0 34.0.0; do
            BUILD_TOOLS="$ANDROID_HOME/build-tools/$VER"
            [ -d "$BUILD_TOOLS" ] && break
        done

        "$BUILD_TOOLS/apksigner" sign \
            --ks "$RELEASE_KEYSTORE" \
            --ks-key-alias alauncher \
            --ks-pass pass:alauncher123 \
            --key-pass pass:alauncher123 \
            --out "$SIGNED_APK" \
            "$APK"

        echo ""
        echo "[3/3] Verificando assinatura..."
        "$BUILD_TOOLS/apksigner" verify "$SIGNED_APK" && echo "  Assinatura OK!"

        echo ""
        echo "=== Release APK assinado ==="
        echo "Salvo em: $SIGNED_APK"
        ;;
    appbundle|bundle|aab)
        echo ""
        echo "[1/2] Buildando App Bundle..."
        bash gradlew bundleRelease --no-daemon 2>&1
        AAB=$(find app/build/outputs/bundle/release -name "*.aab" 2>/dev/null | head -1)
        if [ -n "$AAB" ]; then
            mv "$AAB" "$OUTPUT_DIR/app-release.aab"
            echo ""
            echo "=== App Bundle pronto ==="
            echo "Salvo em: $OUTPUT_DIR/app-release.aab"
        else
            echo "ERRO: AAB nao gerado"
            exit 1
        fi
        ;;
    *)
        echo "Uso: $0 [debug|release|appbundle]"
        echo ""
        echo "  debug     - Build debug APK (padrao)"
        echo "  release   - Build release APK assinado com chave do projeto"
        echo "  appbundle - Build App Bundle (.aab)"
        exit 1
        ;;
esac

echo ""
echo "=== Build concluido! ==="
