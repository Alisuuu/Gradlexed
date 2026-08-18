import os
import json
import subprocess
import zipfile
import tempfile
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(BASE, "version.txt")
REPO = "Alisuuu/Gradlexed"
API_URL = f"https://api.github.com/repos/{REPO}/releases"

R = "\033[1;31m"
B = "\033[1;34m"
A = "\033[36m"
N = "\033[0m"


def h(text):
    print(f"\n  {B}{'─'*40}{N}")
    print(f"  {B}{text}{N}")
    print(f"  {B}{'─'*40}{N}")


def get_version_local():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0"


def set_version_local(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)


def checar_atualizacoes():
    try:
        result = subprocess.run(
            ["curl", "-fsSL", API_URL],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None, None

        releases = json.loads(result.stdout)
        if not releases:
            return None, None

        latest = releases[0]
        tag = latest.get("tag_name", "")
        nome = latest.get("name", tag)
        assets = latest.get("assets", [])

        zip_asset = None
        for asset in assets:
            if asset.get("name", "").endswith(".zip"):
                zip_asset = asset
                break

        return tag, zip_asset, nome
    except Exception:
        return None, None, None


def tem_atualizacao():
    tag, _, _ = checar_atualizacoes()
    if not tag:
        return False
    local = get_version_local()
    return tag != local


def atualizar():
    h("ATUALIZAR FERRAMENTA")

    print(f"  {A}→{N} Verificando atualizacoes...")
    tag, zip_asset, nome = checar_atualizacoes()

    if not tag:
        print(f"  {R}!{N} Nenhuma atualizacao encontrada\n")
        return False

    local = get_version_local()
    print(f"  {A}Versao local:{N} {local}")
    print(f"  {A}Versao remota:{N} {tag} ({nome})")

    if tag == local:
        print(f"\n  {R}✔{N} Ja esta na ultima versao!\n")
        return False

    if not zip_asset:
        print(f"  {R}!{N} Nenhum arquivo ZIP encontrado na release\n")
        return False

    escolha = input(f"\n  {R}❯{N} Atualizar? (s/n): ").strip().lower()
    if escolha != "s":
        print(f"  {A}Atualizacao cancelada{N}\n")
        return False

    print(f"\n  {A}→{N} Baixando {zip_asset['name']}...")
    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, zip_asset["name"])

    result = subprocess.run(
        ["curl", "-fsSL", "-o", zip_path, zip_asset["browser_download_url"]],
        capture_output=True, timeout=120
    )
    if result.returncode != 0 or not os.path.exists(zip_path):
        print(f"  {R}✗{N} Falha ao baixar atualizacao!")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return False

    print(f"  {A}→{N} Extraindo...")
    extract_dir = os.path.join(tmp_dir, "extract")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
    except zipfile.BadZipFile:
        print(f"  {R}✗{N} Arquivo ZIP corrompido!")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return False

    arquivos_ferramenta = [
        "app.py", "build-apk.sh", "editar-informacoes.py", "fix-adb.sh",
        "configurar_de.py", "buildar.py", "configurar_gradle84.py",
        "AGENTS.md", "opencode.json", "atualizar.py",
    ]

    print(f"  {A}→{N} Substituindo arquivos...")
    for arq in arquivos_ferramenta:
        src = os.path.join(extract_dir, arq)
        dst = os.path.join(BASE, arq)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"    {R}+{N} {arq}")

    projeto_dir_src = os.path.join(extract_dir, "projeto")
    if os.path.isdir(projeto_dir_src):
        for root, _, files in os.walk(projeto_dir_src):
            for f in files:
                src = os.path.join(root, f)
                rel = os.path.relpath(src, extract_dir)
                dst = os.path.join(BASE, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                print(f"    {R}+{N} {rel}")

    set_version_local(tag)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n  {R}✔{N} Atualizacao baixada com sucesso!")
    print(f"  {A}As mudancas serao aplicadas na proxima reinicializacao{N}\n")
    return True


if __name__ == "__main__":
    atualizar()
