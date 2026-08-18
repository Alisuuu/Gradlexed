import os

BASE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(BASE, "de")

R = "\033[1;31m"
A = "\033[36m"
N = "\033[0m"

def h(text):
    print(f"\n  \033[1;34m{'─'*40}{N}")
    print(f"  \033[1;34m{text}{N}")
    print(f"  \033[1;34m{'─'*40}{N}")

def configurar_de():
    h("CONFIGURAR DE/ PRA GRADLE 8.4 + API 35")

    # 1. gradle-wrapper.properties
    wrapper = os.path.join(DE, "gradle", "wrapper", "gradle-wrapper.properties")
    print(f"  {A}→{N} Atualizando gradle-wrapper.properties...")
    with open(wrapper, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace("gradle-9.0.0-bin.zip", "gradle-8.4-bin.zip")
    with open(wrapper, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} Gradle 9.0.0 → 8.4")

    # 2. libs.versions.toml
    toml = os.path.join(DE, "gradle", "libs.versions.toml")
    print(f"  {A}→{N} Atualizando libs.versions.toml...")
    with open(toml, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace('agp = "8.13.0"', 'agp = "8.3.2"')
    conteudo = conteudo.replace('coreKtx = "1.17.0"', 'coreKtx = "1.13.1"')
    conteudo = conteudo.replace('lifecycleRuntimeKtx = "2.9.2"', 'lifecycleRuntimeKtx = "2.8.4"')
    conteudo = conteudo.replace('activityCompose = "1.11.0"', 'activityCompose = "1.9.1"')
    conteudo = conteudo.replace('composeBom = "2025.10.01"', 'composeBom = "2024.09.00"')
    with open(toml, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} AGP 8.13.0 → 8.3.2, deps compatíveis com API 35")

    # 3. app/build.gradle.kts
    app_gradle = os.path.join(DE, "app", "build.gradle.kts")
    print(f"  {A}→{N} Atualizando app/build.gradle.kts...")
    with open(app_gradle, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace("compileSdk = 36", "compileSdk = 35")
    conteudo = conteudo.replace("targetSdk = 36", "targetSdk = 35")
    conteudo = conteudo.replace('constraintlayout:constraintlayout:2.2.1', 'constraintlayout:constraintlayout:2.1.4')
    conteudo = conteudo.replace('recyclerview:recyclerview:1.4.0', 'recyclerview:recyclerview:1.3.2')
    conteudo = conteudo.replace('activity:activity-ktx:1.10.1', 'activity:activity-ktx:1.9.1')
    conteudo = conteudo.replace('kotlinx-coroutines-android:1.9.0', 'kotlinx-coroutines-android:1.8.1')
    conteudo = conteudo.replace('io.coil-kt:coil:2.7.0', 'io.coil-kt:coil:2.6.0')
    with open(app_gradle, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} compileSdk/targetSdk 36 → 35, deps downgrade")

    # 4. baseline-profile/build.gradle.kts
    bp_gradle = os.path.join(DE, "baseline-profile", "build.gradle.kts")
    if os.path.exists(bp_gradle):
        print(f"  {A}→{N} Atualizando baseline-profile/build.gradle.kts...")
        with open(bp_gradle, "r") as f:
            conteudo = f.read()
        conteudo = conteudo.replace("compileSdk = 36", "compileSdk = 35")
        conteudo = conteudo.replace("targetSdk = 36", "targetSdk = 35")
        with open(bp_gradle, "w") as f:
            f.write(conteudo)
        print(f"  {R}✔{N} baseline-profile atualizado")

    # 5. gradle.properties
    props = os.path.join(DE, "gradle.properties")
    print(f"  {A}→{N} Atualizando gradle.properties...")
    with open(props, "r") as f:
        conteudo = f.read()
    if "android.suppressUnsupportedCompileSdk=35" not in conteudo:
        conteudo = conteudo.replace(
            "android.useAndroidX=true",
            "android.useAndroidX=true\nandroid.suppressUnsupportedCompileSdk=35\nandroid.enableJetifier=true\nandroid.aapt2FromMavenOverride=/usr/local/bin/aapt2"
        )
    with open(props, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} Propriedades ARM64 adicionadas")

    print(f"\n  {R}✔{N} Projeto de/ configurado pra Gradle 8.4 + API 35!\n")

if __name__ == "__main__":
    configurar_de()
