import os

BASE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(BASE, "de")

R = "\033[1;31m"
A = "\033[36m"
N = "\033[0m"

def h(text):
    print(f"  \033[1;34m{'─'*40}{N}")
    print(f"  \033[1;34m{text}{N}")
    print(f"  \033[1;34m{'─'*40}{N}")

def configurar_de():
    h("CONFIGURAR DE/ PRA GRADLE 8.13 + API 37")

    # 1. gradle-wrapper.properties
    wrapper = os.path.join(DE, "gradle", "wrapper", "gradle-wrapper.properties")
    print(f"  {A}→{N} Atualizando gradle-wrapper.properties...")
    with open(wrapper, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace("gradle-8.4-bin.zip", "gradle-8.13-bin.zip")
    conteudo = conteudo.replace("gradle-9.0.0-bin.zip", "gradle-8.13-bin.zip")
    with open(wrapper, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} Gradle -> 8.13")

    # 2. libs.versions.toml
    toml = os.path.join(DE, "gradle", "libs.versions.toml")
    print(f"  {A}→{N} Atualizando libs.versions.toml...")
    with open(toml, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace('agp = "8.3.2"', 'agp = "8.13.0"')
    conteudo = conteudo.replace('agp = "9.1.1"', 'agp = "8.13.0"')
    with open(toml, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} AGP -> 8.13.0")

    # 3. app/build.gradle.kts
    app_gradle = os.path.join(DE, "app", "build.gradle.kts")
    print(f"  {A}→{N} Atualizando app/build.gradle.kts...")
    with open(app_gradle, "r") as f:
        conteudo = f.read()
    conteudo = conteudo.replace("compileSdk = 35", "compileSdk = 37")
    conteudo = conteudo.replace("compileSdk = 36", "compileSdk = 37")
    conteudo = conteudo.replace("targetSdk = 35", "targetSdk = 37")
    conteudo = conteudo.replace("targetSdk = 36", "targetSdk = 37")
    with open(app_gradle, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} compileSdk/targetSdk -> 37")

    # 4. gradle.properties
    props = os.path.join(DE, "gradle.properties")
    print(f"  {A}→{N} Atualizando gradle.properties...")
    with open(props, "r") as f:
        conteudo = f.read()
    if "android.suppressUnsupportedCompileSdk=35,37" not in conteudo:
        conteudo = conteudo.replace(
            "android.useAndroidX=True",
            "android.useAndroidX=true\nandroid.suppressUnsupportedCompileSdk=35,37\nandroid.enableJetifier=true\nandroid.aapt2FromMavenOverride=/usr/local/bin/aapt2"
        )
        conteudo = conteudo.replace(
            "android.useAndroidX=true",
            "android.useAndroidX=true\nandroid.suppressUnsupportedCompileSdk=35,37\nandroid.enableJetifier=true\nandroid.aapt2FromMavenOverride=/usr/local/bin/aapt2"
        )
    with open(props, "w") as f:
        f.write(conteudo)
    print(f"  {R}✔{N} Propriedades configuradas")

    print(f"\n  {R}✔{N} Projeto de/ configurado pra Gradle 8.13 + API 37!\n")

if __name__ == "__main__":
    configurar_de()
