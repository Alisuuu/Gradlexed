#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJETO_DIR="$SCRIPT_DIR/projeto"
OUTPUT_DIR="$SCRIPT_DIR/apks"
CONFIGURAR="$SCRIPT_DIR/configurar_projeto.py"

if [ -f "$SCRIPT_DIR/.ambiente" ]; then
    source "$SCRIPT_DIR/.ambiente"
fi

export ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

TIPO="${1:-debug}"
TOTAL=8
STEP=0

R='\033[1;31m'
B='\033[1;34m'
A='\033[36m'
OK='\033[1;32m'
N='\033[0m'

progress() {
    STEP=$((STEP + 1))
    echo ""
    echo -e "  ${B}[${STEP}/${TOTAL}]${N} ${B}$1${N}"
}

echo "=== Buildando APK ==="
echo "Tipo: $TIPO"
echo "Projeto: $PROJETO_DIR"

mkdir -p "$OUTPUT_DIR"

if [ ! -d "$PROJETO_DIR" ]; then
    echo "ERRO: Pasta projeto/ nao encontrada"
    exit 1
fi

# ── [1/8] Configuracao do projeto ──
progress "Verificando e corrigindo configuracao"
python3 "$CONFIGURAR" projeto "$PROJETO_DIR"
echo ""

# ── [2/8] Verificar SDK ──
progress "Verificando Android SDK"
if [ ! -f "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo -e "  ${R}!${N} Android SDK cmdline-tools nao encontrado em $ANDROID_HOME"
    echo -e "  ${A}→${N} Tentando instalar ambiente completo..."
    python3 "$CONFIGURAR" ambiente
    if [ ! -f "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
        echo -e "  ${R}✗${N} Falha ao instalar Android SDK"
        exit 1
    fi
fi
echo -e "  ${OK}✔${N} Android SDK pronto"

# ── [3/8] Auto-fix gradle.properties ──
progress "Verificando gradle.properties"
PROPS="$PROJETO_DIR/gradle.properties"
if [ -f "$PROPS" ]; then
    FIXED=0

    JVMARGS_COUNT=$(grep -c "^org.gradle.jvmargs=" "$PROPS" || true)
    if [ "$JVMARGS_COUNT" -gt 1 ]; then
        TMPFILE=$(mktemp)
        awk '!seen[$0]++ { if ($0 ~ /^org\.gradle\.jvmargs=/) { if (prev_jvmargs) print prev_jvmargs; prev_jvmargs=$0; next } else { if (prev_jvmargs) { print prev_jvmargs; prev_jvmargs="" } print } } END { if (prev_jvmargs) print prev_jvmargs }' "$PROPS" > "$TMPFILE"
        mv "$TMPFILE" "$PROPS"
        echo -e "  ${OK}+${N} Removidas linhas duplicadas de jvmargs"
        FIXED=1
    fi

    JVMARGS=$(grep "^org.gradle.jvmargs=" "$PROPS" | tail -1)
    if echo "$JVMARGS" | grep -q "Xmx[0-9]*[gG]"; then
        GB=$(echo "$JVMARGS" | sed 's/.*Xmx\([0-9]*\)[gG].*/\1/')
        if [ "$GB" -gt 2 ] 2>/dev/null; then
            NEW_JVMARGS=$(echo "$JVMARGS" | sed 's/Xmx[0-9]*[gG]/Xmx2048m/')
            sed -i "s|^org.gradle.jvmargs=.*|${NEW_JVMARGS}|" "$PROPS"
            echo -e "  ${OK}+${N} JVM args limitado a 2048m"
            FIXED=1
        fi
    fi

    for PROP in "org.gradle.caching=true" "org.gradle.parallel=true" "org.gradle.daemon=true" "kotlin.incremental=true"; do
        KEY=$(echo "$PROP" | cut -d= -f1)
        if ! grep -q "^${KEY}=" "$PROPS"; then
            echo "$PROP" >> "$PROPS"
            echo -e "  ${OK}+${N} Adicionado: $PROP"
            FIXED=1
        fi
    done

    COMPILE_SDK=$(grep -oP 'compileSdk\s*=?\s*\K\d+' "$PROJETO_DIR/app/build.gradle.kts" 2>/dev/null || grep -oP 'compileSdk\s*=?\s*\K\d+' "$PROJETO_DIR/app/build.gradle" 2>/dev/null || echo "")
    if [ -n "$COMPILE_SDK" ]; then
        if ! grep -q "android.suppressUnsupportedCompileSdk=.*${COMPILE_SDK}" "$PROPS"; then
            OLD=$(grep "android.suppressUnsupportedCompileSdk=" "$PROPS" | head -1 | cut -d= -f2)
            if [ -n "$OLD" ]; then
                if ! echo "$OLD" | grep -q "$COMPILE_SDK"; then
                    sed -i "s|^android.suppressUnsupportedCompileSdk=.*|android.suppressUnsupportedCompileSdk=${OLD},${COMPILE_SDK},${COMPILE_SDK}.0|" "$PROPS"
                    echo -e "  ${OK}+${N} suppressUnsupportedCompileSdk atualizado com SDK $COMPILE_SDK"
                    FIXED=1
                fi
            else
                echo "android.suppressUnsupportedCompileSdk=35,${COMPILE_SDK},${COMPILE_SDK}.0" >> "$PROPS"
                echo -e "  ${OK}+${N} suppressUnsupportedCompileSdk adicionado"
                FIXED=1
            fi
        fi
    fi

    if [ -f "/usr/local/bin/aapt2" ]; then
        if ! grep -q "android.aapt2FromMavenOverride" "$PROPS"; then
            echo "android.aapt2FromMavenOverride=/usr/local/bin/aapt2" >> "$PROPS"
            echo -e "  ${OK}+${N} aapt2 override adicionado"
            FIXED=1
        fi
    fi

    if [ "$FIXED" -eq 0 ]; then
        echo -e "  ${OK}✔${N} gradle.properties ok"
    fi
fi

# ── [4/8] Verificar gradlew ──
progress "Verificando gradlew"
GRADLEW="$PROJETO_DIR/gradlew"
if [ -f "$GRADLEW" ]; then
    if [ ! -x "$GRADLEW" ]; then
        chmod +x "$GRADLEW"
        echo -e "  ${OK}+${N} gradlew agora e executavel"
    else
        echo -e "  ${OK}✔${N} gradlew ja e executavel"
    fi
fi

# ── [5/8] Verificar compatibilidade AGP/Gradle ──
progress "Verificando compatibilidade AGP/Gradle"
WRAPPER_PROPS="$PROJETO_DIR/gradle/wrapper/gradle-wrapper.properties"
if [ -f "$WRAPPER_PROPS" ]; then
    GRADLE_VER=$(grep -oP 'gradle-\K[0-9.]+' "$WRAPPER_PROPS" | head -1)
    TOML="$PROJETO_DIR/gradle/libs.versions.toml"
    if [ -f "$TOML" ]; then
        AGP_VER=$(grep -oP '^agp\s*=\s*"\K[^"]+' "$TOML" | head -1)
    else
        ROOT_GRADLE="$PROJETO_DIR/build.gradle.kts"
        [ ! -f "$ROOT_GRADLE" ] && ROOT_GRADLE="$PROJETO_DIR/build.gradle"
        AGP_VER=$(grep -oP 'com\.android\.tools\.build:gradle:\K[^\s"'"'"']+' "$ROOT_GRADLE" 2>/dev/null | head -1)
    fi

    if [ -n "$GRADLE_VER" ] && [ -n "$AGP_VER" ]; then
        AGP_MAJOR=$(echo "$AGP_VER" | cut -d. -f1,2)
        case "$AGP_MAJOR" in
            8.13) MIN_GRADLE="8.13" ;;
            8.12) MIN_GRADLE="8.13" ;;
            8.11) MIN_GRADLE="8.11.1" ;;
            8.10) MIN_GRADLE="8.11.1" ;;
            8.9)  MIN_GRADLE="8.11.1" ;;
            8.8)  MIN_GRADLE="8.10.2" ;;
            8.7)  MIN_GRADLE="8.9" ;;
            8.6)  MIN_GRADLE="8.7" ;;
            8.5)  MIN_GRADLE="8.7" ;;
            8.4)  MIN_GRADLE="8.6" ;;
            8.3)  MIN_GRADLE="8.4" ;;
            8.2)  MIN_GRADLE="8.2" ;;
            8.1)  MIN_GRADLE="8.0" ;;
            8.0)  MIN_GRADLE="8.0" ;;
            7.4)  MIN_GRADLE="7.5" ;;
            *)    MIN_GRADLE="" ;;
        esac

        if [ -n "$MIN_GRADLE" ]; then
            GRADLE_NUM=$(echo "$GRADLE_VER" | tr -d '.')
            MIN_NUM=$(echo "$MIN_GRADLE" | tr -d '.')
            if [ "$GRADLE_NUM" -lt "$MIN_NUM" ] 2>/dev/null; then
                echo -e "  ${R}!${N} AGP $AGP_VER requer Gradle >= $MIN_GRADLE (atual: $GRADLE_VER)"
                sed -i "s|gradle-${GRADLE_VER}-bin.zip|gradle-${MIN_GRADLE}-bin.zip|" "$WRAPPER_PROPS"
                echo -e "  ${OK}+${N} Gradle wrapper atualizado: $GRADLE_VER -> $MIN_GRADLE"
            else
                echo -e "  ${OK}✔${N} Gradle $GRADLE_VER compativel com AGP $AGP_VER"
            fi
        fi
    fi
fi

cd "$PROJETO_DIR"

case "$TIPO" in
    debug)
        # ── [6/8] Build ──
        progress "Buildando debug APK..."
        bash gradlew assembleDebug -x stripDebugDebugSymbols -x extractDebugNativeSymbolTables 2>&1
        APK=$(find app/build/outputs/apk/debug -name "*.apk" 2>/dev/null | head -1)
        if [ -n "$APK" ]; then
            mv "$APK" "$OUTPUT_DIR/app-debug.apk"
            # ── [7/8] Copiar APK ──
            progress "Copiando APK para saida"
            echo -e "  ${OK}✔${N} Debug APK pronto"
            echo ""
            # ── [8/8] Concluido ──
            progress "Concluido"
            echo -e "  ${OK}✔${N} Salvo em: $OUTPUT_DIR/app-debug.apk"
        else
            echo -e "  ${R}✗${N} APK nao gerado"
            exit 1
        fi
        ;;
    release)
        # ── [6/8] Build ──
        progress "Buildando release APK..."
        bash gradlew assembleRelease -x stripReleaseDebugSymbols -x extractReleaseNativeSymbolTables 2>&1
        APK=$(find app/build/outputs/apk/release -name "*.apk" ! -name "*.idsig" 2>/dev/null | head -1)
        if [ -n "$APK" ]; then
            cp "$APK" "$OUTPUT_DIR/app-release.apk"
        else
            echo -e "  ${R}✗${N} APK release nao gerado"
            exit 1
        fi

        # ── [7/8] Verificar assinatura ──
        progress "Verificando assinatura"
        for VER in 36.0.0 35.0.0 34.0.0; do
            BUILD_TOOLS="$ANDROID_HOME/build-tools/$VER"
            [ -d "$BUILD_TOOLS" ] && break
        done

        "$BUILD_TOOLS/apksigner" verify "$OUTPUT_DIR/app-release.apk" && echo -e "  ${OK}✔${N} Assinatura OK!"

        # ── [8/8] Concluido ──
        progress "Concluido"
        echo -e "  ${OK}✔${N} Salvo em: $OUTPUT_DIR/app-release.apk"
        ;;
    appbundle|bundle|aab)
        # ── [6/8] Build ──
        progress "Buildando App Bundle..."
        bash gradlew bundleRelease -x stripReleaseDebugSymbols -x extractReleaseNativeSymbolTables 2>&1
        AAB=$(find app/build/outputs/bundle/release -name "*.aab" 2>/dev/null | head -1)
        if [ -n "$AAB" ]; then
            mv "$AAB" "$OUTPUT_DIR/app-release.aab"
            # ── [7/8] Copiar AAB ──
            progress "Copiando AAB para saida"
            echo -e "  ${OK}✔${N} App Bundle pronto"
            echo ""
            # ── [8/8] Concluido ──
            progress "Concluido"
            echo -e "  ${OK}✔${N} Salvo em: $OUTPUT_DIR/app-release.aab"
        else
            echo -e "  ${R}✗${N} AAB nao gerado"
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
