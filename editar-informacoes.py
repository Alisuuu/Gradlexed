#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJETO_DIR="$SCRIPT_DIR/projeto"
APP_GRADLE="$PROJETO_DIR/app/build.gradle.kts"
SETTINGS_GRADLE="$PROJETO_DIR/settings.gradle.kts"
MANIFEST="$PROJETO_DIR/app/src/main/AndroidManifest.xml"

if [ ! -f "$APP_GRADLE" ]; then
    echo "ERRO: app/build.gradle.kts nao encontrado em $PROJETO_DIR"
    exit 1
fi

show_help() {
    echo "=== Editar Informacoes do App ==="
    echo ""
    echo "Uso: $0 <comando> [valor]"
    echo ""
    echo "Comandos:"
    echo "  listar                   - Mostra todas as informacoes atuais"
    echo "  nome <nome>              - Altera o nome do app (string no manifest)"
    echo "  pacote <id>              - Altera applicationId e namespace"
    echo "  versao <codigo>          - Altera versionCode"
    echo "  nomeversao <nome>        - Altera versionName"
    echo "  minsdk <api>             - Altera minSdk"
    echo "  targetsdk <api>          - Altera targetSdk"
    echo "  compilesdk <api>         - Altera compileSdk"
    echo "  projeto <nome>           - Altera rootProject.name no settings.gradle.kts"
    echo ""
    echo "Exemplos:"
    echo "  $0 nome \"Meu App\""
    echo "  $0 pacote com.exemplo.meuapp"
    echo "  $0 versao 2"
    echo "  $0 nomeversao \"2.0\""
}

listar() {
    echo "=== Informacoes do App ==="
    echo ""

    # Nome do projeto
    PROJ_NAME=$(grep 'rootProject.name' "$SETTINGS_GRADLE" | sed 's/.*= *"\(.*\)".*/\1/')
    echo "Nome do projeto: $PROJ_NAME"

    # applicationId / namespace
    APP_ID=$(grep 'applicationId' "$APP_GRADLE" | sed 's/.*= *"\(.*\)".*/\1/')
    NAMESPACE=$(grep 'namespace' "$APP_GRADLE" | sed 's/.*= *"\(.*\)".*/\1/')
    echo "Application ID: $APP_ID"
    echo "Namespace: $NAMESPACE"

    # Versao
    VC=$(grep 'versionCode' "$APP_GRADLE" | grep -o '[0-9]\+')
    VN=$(grep 'versionName' "$APP_GRADLE" | sed 's/.*= *"\(.*\)".*/\1/')
    echo "Version Code: $VC"
    echo "Version Name: $VN"

    # SDKs
    COMPILE=$(grep 'compileSdk' "$APP_GRADLE" | grep -o '[0-9]\+')
    MIN=$(grep 'minSdk' "$APP_GRADLE" | grep -o '[0-9]\+')
    TARGET=$(grep 'targetSdk' "$APP_GRADLE" | grep -o '[0-9]\+')
    echo "Compile SDK: $COMPILE"
    echo "Min SDK: $MIN"
    echo "Target SDK: $TARGET"

    # Nome do app (do strings.xml)
    STRINGS="$PROJETO_DIR/app/src/main/res/values/strings.xml"
    if [ -f "$STRINGS" ]; then
        APP_NAME=$(grep 'app_name' "$STRINGS" | sed 's/.*>\(.*\)<.*/\1/')
        echo "Nome do app (strings): $APP_NAME"
    fi

    echo ""
}

alterar() {
    local ARQUIVO="$1"
    local PADRAO="$2"
    local SUBST="$3"
    sed -i "s|$PADRAO|$SUBST|g" "$ARQUIVO"
}

case "${1:-}" in
    listar|list)
        listar
        ;;
    nome)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o nome do app"
            echo "Uso: $0 nome \"Meu App\""
            exit 1
        fi
        STRINGS="$PROJETO_DIR/app/src/main/res/values/strings.xml"
        if [ -f "$STRINGS" ]; then
            sed -i "s|<string name=\"app_name\">.*</string>|<string name=\"app_name\">$2</string>|" "$STRINGS"
            echo "Nome do app alterado para: $2"
        else
            echo "ERRO: strings.xml nao encontrado"
            exit 1
        fi
        ;;
    pacote)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o applicationId"
            echo "Uso: $0 pacote com.exemplo.meuapp"
            exit 1
        fi
        alterar "$APP_GRADLE" 'applicationId = ".*"' "applicationId = \"$2\""
        alterar "$APP_GRADLE" 'namespace = ".*"' "namespace = \"$2\""
        echo "Application ID e Namespace alterados para: $2"
        ;;
    versao)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o versionCode"
            echo "Uso: $0 versao 2"
            exit 1
        fi
        alterar "$APP_GRADLE" 'versionCode = [0-9]*' "versionCode = $2"
        echo "Version Code alterado para: $2"
        ;;
    nomeversao)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o versionName"
            echo "Uso: $0 nomeversao \"2.0\""
            exit 1
        fi
        alterar "$APP_GRADLE" 'versionName = ".*"' "versionName = \"$2\""
        echo "Version Name alterado para: $2"
        ;;
    minsdk)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o minSdk"
            echo "Uso: $0 minsdk 21"
            exit 1
        fi
        alterar "$APP_GRADLE" 'minSdk = [0-9]*' "minSdk = $2"
        echo "Min SDK alterado para: $2"
        ;;
    targetsdk)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o targetSdk"
            echo "Uso: $0 targetsdk 34"
            exit 1
        fi
        alterar "$APP_GRADLE" 'targetSdk = [0-9]*' "targetSdk = $2"
        echo "Target SDK alterado para: $2"
        ;;
    compilesdk)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o compileSdk"
            echo "Uso: $0 compilesdk 36"
            exit 1
        fi
        alterar "$APP_GRADLE" 'compileSdk = [0-9]*' "compileSdk = $2"
        echo "Compile SDK alterado para: $2"
        ;;
    projeto)
        if [ -z "${2:-}" ]; then
            echo "ERRO: Informe o nome do projeto"
            echo "Uso: $0 projeto MeuProjeto"
            exit 1
        fi
        alterar "$SETTINGS_GRADLE" 'rootProject.name = ".*"' "rootProject.name = \"$2\""
        echo "Nome do projeto alterado para: $2"
        ;;
    *)
        show_help
        ;;
esac
