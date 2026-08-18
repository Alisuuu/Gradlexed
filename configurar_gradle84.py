import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(BASE, "projeto")

R = "\033[1;31m"
A = "\033[36m"
N = "\033[0m"

def h(text):
    print(f"\n  \033[1;34m{'─'*40}{N}")
    print(f"  \033[1;34m{text}{N}")
    print(f"  \033[1;34m{'─'*40}{N}")

def configurar_gradle84():
    h("CONFIGURAR GRADLE 8.4")

    wrapper_props = os.path.join(PROJETO, "gradle", "wrapper", "gradle-wrapper.properties")
    libs_toml = os.path.join(PROJETO, "gradle", "libs.versions.toml")
    app_gradle = os.path.join(PROJETO, "app", "build.gradle.kts")
    gradle_props = os.path.join(PROJETO, "gradle.properties")

    for f in [wrapper_props, libs_toml, app_gradle, gradle_props]:
        if not os.path.exists(f):
            print(f"  {R}✗{N} {os.path.basename(f)} não encontrado!")
            return False

    print(f"  {A}→{N} Fazendo backup...")
    backup_dir = os.path.join(PROJETO, "gradle", "backup_gradle9")
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(wrapper_props, os.path.join(backup_dir, "gradle-wrapper.properties"))
    shutil.copy2(libs_toml, os.path.join(backup_dir, "libs.versions.toml"))
    shutil.copy2(app_gradle, os.path.join(backup_dir, "build.gradle.kts"))
    shutil.copy2(gradle_props, os.path.join(backup_dir, "gradle.properties"))

    print(f"  {A}→{N} Configurando Gradle 8.4...")
    with open(wrapper_props, "r") as f:
        content = f.read()
    content = content.replace("gradle-9.0.0-bin.zip", "gradle-8.4-bin.zip")
    with open(wrapper_props, "w") as f:
        f.write(content)

    print(f"  {A}→{N} Configurando AGP 8.2.0 e dependências...")
    with open(libs_toml, "r") as f:
        content = f.read()
    content = content.replace('agp = "8.13.0"', 'agp = "8.2.0"')
    content = content.replace('kotlin = "2.1.0"', 'kotlin = "1.9.22"')
    content = content.replace('coreKtx = "1.17.0"', 'coreKtx = "1.12.0"')
    content = content.replace('lifecycleRuntimeKtx = "2.9.2"', 'lifecycleRuntimeKtx = "2.6.2"')
    content = content.replace('activityCompose = "1.11.0"', 'activityCompose = "1.8.2"')
    content = content.replace('composeBom = "2025.10.01"', 'composeBom = "2024.02.00"')
    content = content.replace('datastore = "1.1.1"', 'datastore = "1.0.0"')
    content = content.replace('kotlinxSerializationJson = "1.7.3"', 'kotlinxSerializationJson = "1.6.0"')
    content = content.replace('version = "1.4.1"', 'version = "1.3.1"')
    with open(libs_toml, "w") as f:
        f.write(content)

    print(f"  {A}→{N} Ajustando dependências do app...")
    with open(app_gradle, "r") as f:
        content = f.read()
    content = re.sub(r'compileSdk\s*=\s*\d+', 'compileSdk = 34', content)
    content = re.sub(r'targetSdk\s*=\s*\d+', 'targetSdk = 34', content)
    content = content.replace('appcompat:1.7.0', 'appcompat:1.6.1')
    content = content.replace('constraintlayout:2.2.1', 'constraintlayout:2.1.4')
    content = content.replace('recyclerview:1.4.0', 'recyclerview:1.3.2')
    content = content.replace('activity-ktx:1.10.1', 'activity-ktx:1.8.2')
    content = content.replace('kotlinx-coroutines-android:1.9.0', 'kotlinx-coroutines-android:1.7.3')
    content = content.replace('coil:2.7.0', 'coil:2.5.0')
    content = content.replace('leakcanary-android:2.14', 'leakcanary-android:2.12')
    with open(app_gradle, "w") as f:
        f.write(content)

    print(f"  {A}→{N} Configurando gradle.properties (aapt2 arm64)...")
    with open(gradle_props, "r") as f:
        content = f.read()
    aapt2_line = "android.aapt2FromMavenOverride=/usr/lib/android-sdk/build-tools/debian/aapt2"
    if aapt2_line not in content:
        content = content.rstrip() + "\n" + aapt2_line + "\n"
    with open(gradle_props, "w") as f:
        f.write(content)

    print(f"\n  {R}✔{N} Gradle 8.4 configurado!")
    print(f"  {A}→{N} AGP 8.2.0, Kotlin 1.9.22")
    print(f"  {A}→{N} Dependências ajustadas para compatibilidade")
    print(f"  {A}→{N} Backup em: gradle/backup_gradle9/\n")
    return True

def restaurar_gradle9():
    h("RESTAURAR GRADLE 9.0")

    wrapper_props = os.path.join(PROJETO, "gradle", "wrapper", "gradle-wrapper.properties")
    libs_toml = os.path.join(PROJETO, "gradle", "libs.versions.toml")
    app_gradle = os.path.join(PROJETO, "app", "build.gradle.kts")
    gradle_props = os.path.join(PROJETO, "gradle.properties")
    backup_dir = os.path.join(PROJETO, "gradle", "backup_gradle9")

    backup_wrapper = os.path.join(backup_dir, "gradle-wrapper.properties")
    backup_toml = os.path.join(backup_dir, "libs.versions.toml")
    backup_app = os.path.join(backup_dir, "build.gradle.kts")
    backup_gradle_props = os.path.join(backup_dir, "gradle.properties")

    if not os.path.exists(backup_wrapper) or not os.path.exists(backup_toml):
        print(f"  {R}✗{N} Backup não encontrado! Execute 'Configurar Gradle 8.4' primeiro.")
        return False

    print(f"  {A}→{N} Restaurando configurações do Gradle 9.0...")
    shutil.copy2(backup_wrapper, wrapper_props)
    shutil.copy2(backup_toml, libs_toml)
    if os.path.exists(backup_app):
        shutil.copy2(backup_app, app_gradle)
    if os.path.exists(backup_gradle_props):
        shutil.copy2(backup_gradle_props, gradle_props)

    print(f"\n  {R}✔{N} Gradle restaurado para versão 9.0!\n")
    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        op = sys.argv[1]
    else:
        print(f"\n  \033[1;34m╔══════════════════════════════╗{N}")
        print(f"  \033[1;34m║{N}  Configurar Versão Gradle  \033[1;34m║{N}")
        print(f"  \033[1;34m╚══════════════════════════════╝{N}")
        print(f"\n  {R}1{N}  Configurar Gradle 8.4")
        print(f"  {R}2{N}  Restaurar Gradle 9.0")
        print(f"  {R}3{N}  Sair")
        op = input(f"\n  {R}❯{N} ").strip()

    if op == "1":
        configurar_gradle84()
    elif op == "2":
        restaurar_gradle9()
    elif op == "3":
        print(f"\n  {A}★ volte sempre ★{N}\n")
    else:
        print(f"\n  {R}!{N} Opcao invalida\n")
