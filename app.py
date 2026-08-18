import os
import subprocess
import shutil
import shlex

BASE = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(BASE, "projeto")
BUILD_APK = os.path.join(BASE, "build-apk.sh")
EDITAR = os.path.join(BASE, "editar-informacoes.py")
FIX_ADB = os.path.join(BASE, "fix-adb.sh")
CONFIGURAR_DE = os.path.join(BASE, "configurar_de.py")
ATUALIZAR = os.path.join(BASE, "atualizar.py")

OPENCODE_DIR = os.path.expanduser("~/.opencode/bin")
os.environ["PATH"] = OPENCODE_DIR + ":" + os.environ["PATH"]

R = "\033[1;31m"     # vermelho
B = "\033[1;34m"     # azul
A = "\033[36m"       # ciano pra detalhes
N = "\033[0m"

def h(text):
    print(f"\n  {B}{'─'*40}{N}")
    print(f"  {B}{text}{N}")
    print(f"  {B}{'─'*40}{N}")

def run(cmd, check=True, cwd=PROJETO):
    subprocess.run(cmd, shell=True, check=check, cwd=cwd, executable="/bin/bash")

def instalar_java():
    h("INSTALAR JAVA")
    if shutil.which("java"):
        print(f"  {R}✔{N} Java já está instalado!\n")
        return
    print(f"  {A}→{N} Instalando Java...")
    if shutil.which("pkg"):
        run("pkg install openjdk-17 -y", cwd=os.path.expanduser("~"))
    elif shutil.which("apt-get"):
        run("apt-get install -y openjdk-17-jdk-headless", cwd=os.path.expanduser("~"), check=False)
    else:
        print(f"\n  {R}✗{N} Gerenciador de pacotes não encontrado!")
        raise SystemExit(1)
    if not shutil.which("java"):
        print(f"\n  {R}✗{N} Falha ao instalar Java!")
        raise SystemExit(1)
    print(f"\n  {R}✔{N} Java instalado com sucesso!\n")

def instalar_opencode():
    h("INSTALAR OPENCODE")
    if shutil.which("opencode"):
        print(f"  {R}✔{N} opencode já está instalado!\n")
        return
    print(f"  {A}→{N} Baixando opencode...")
    run("curl -fsSL https://opencode.ai/install | bash", cwd=os.path.expanduser("~"))
    if not shutil.which("opencode"):
        print(f"\n  {R}✗{N} Falha ao instalar opencode!")
        raise SystemExit(1)
    print(f"  {A}→{N} Configurando PATH no .bashrc...")
    bashrc = os.path.expanduser("~/.bashrc")
    export_line = 'export PATH="$HOME/.opencode/bin:$PATH"'
    if os.path.exists(bashrc):
        with open(bashrc, "r") as f:
            if export_line not in f.read():
                with open(bashrc, "a") as f:
                    f.write(f"\n{export_line}\n")
                run("source ~/.bashrc", check=False)
    else:
        with open(bashrc, "w") as f:
            f.write(f"\n{export_line}\n")
    print(f"\n  {R}✔{N} opencode instalado com sucesso!\n")

def instalar_git():
    h("INSTALAR GIT")
    if shutil.which("git"):
        print(f"  {R}✔{N} git já está instalado!\n")
        return
    print(f"  {A}→{N} Instalando git...")
    if shutil.which("pkg"):
        run("pkg install git -y", cwd=os.path.expanduser("~"))
    elif shutil.which("apt-get"):
        run("apt-get install -y git", cwd=os.path.expanduser("~"), check=False)
    else:
        print(f"\n  {R}✗{N} Gerenciador de pacotes não encontrado!")
        raise SystemExit(1)
    if not shutil.which("git"):
        print(f"\n  {R}✗{N} Falha ao instalar git!")
        raise SystemExit(1)
    print(f"\n  {R}✔{N} git instalado com sucesso!\n")

ANDROID_HOME = "/opt/android-sdk"
SDK_TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"

def instalar_android_sdk():
    h("INSTALAR ANDROID SDK")
    sdkmanager = os.path.join(ANDROID_HOME, "cmdline-tools", "latest", "bin", "sdkmanager")
    if os.path.exists(sdkmanager):
        print(f"  {R}✔{N} Android SDK já está instalado!\n")
        return
    print(f"  {A}→{N} Baixando Android SDK cmdline-tools...")
    os.makedirs(ANDROID_HOME, exist_ok=True)
    tmp = "/tmp/cmdline-tools.zip"
    run(f"curl -fsSL -o {tmp} {SDK_TOOLS_URL}", cwd=os.path.expanduser("~"), check=False)
    if not os.path.exists(tmp):
        print(f"\n  {R}✗{N} Falha ao baixar cmdline-tools!")
        raise SystemExit(1)
    print(f"  {A}→{N} Extraindo...")
    run(f"unzip -qo {tmp} -d /tmp/sdk", cwd=os.path.expanduser("~"), check=False)
    os.makedirs(os.path.join(ANDROID_HOME, "cmdline-tools"), exist_ok=True)
    run(f"rm -rf {os.path.join(ANDROID_HOME, 'cmdline-tools', 'latest')}", cwd=os.path.expanduser("~"), check=False)
    run(f"mv /tmp/sdk/cmdline-tools {os.path.join(ANDROID_HOME, 'cmdline-tools', 'latest')}", cwd=os.path.expanduser("~"), check=False)
    run(f"rm -rf /tmp/sdk {tmp}", cwd=os.path.expanduser("~"), check=False)
    print(f"  {A}→{N} Aceitando licenças...")
    run(f"yes | {sdkmanager} --licenses > /dev/null 2>&1", cwd=os.path.expanduser("~"), check=False)
    print(f"  {A}→{N} Instalando platform-tools, build-tools;36.0.0, platforms;android-34...")
    run(f"{sdkmanager} 'platform-tools' 'build-tools;36.0.0' 'platforms;android-34'", cwd=os.path.expanduser("~"), check=False)
    aapt2_arm64 = "/usr/lib/android-sdk/build-tools/debian/aapt2"
    if not os.path.exists(aapt2_arm64):
        print(f"  {A}→{N} Instalando aapt2 ARM64 do sistema...")
        if shutil.which("apt-get"):
            run("apt-get install -y aapt", cwd=os.path.expanduser("~"), check=False)
    local_props = os.path.join(PROJETO, "local.properties")
    with open(local_props, "w") as f:
        f.write(f"sdk.dir={ANDROID_HOME}\n")
    if not os.path.exists(sdkmanager):
        print(f"\n  {R}✗{N} Falha ao instalar Android SDK!")
        raise SystemExit(1)
    print(f"\n  {R}✔{N} Android SDK instalado com sucesso!\n")

def configurar():
    h("CONFIGURAR AMBIENTE")
    instalar_java()
    instalar_git()
    instalar_opencode()
    instalar_android_sdk()
    os.environ["ANDROID_HOME"] = ANDROID_HOME
    os.environ["ANDROID_SDK_ROOT"] = ANDROID_HOME
    os.environ["PATH"] = os.path.join(ANDROID_HOME, "cmdline-tools", "latest", "bin") + ":" + os.path.join(ANDROID_HOME, "platform-tools") + ":" + os.environ["PATH"]
    print(f"\n  {R}✔{N} Ambiente configurado!\n")

def fix_kotlin_version():
    toml_path = os.path.join(PROJETO, "gradle", "libs.versions.toml")
    if not os.path.exists(toml_path):
        return
    with open(toml_path, "r") as f:
        content = f.read()
    import re
    match = re.search(r'^kotlin\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        return
    ver = match.group(1)
    parts = ver.split(".")
    if len(parts) >= 2:
        major, minor = int(parts[0]), int(parts[1])
        if major > 2 or (major == 2 and minor > 0):
            print(f"  {A}→{N} Corrigindo Kotlin {ver} -> 2.0.21 (compatibilidade R8)...")
            new_content = re.sub(r'^kotlin\s*=\s*"[^"]+"', 'kotlin = "2.0.21"', content, count=1, flags=re.MULTILINE)
            with open(toml_path, "w") as f:
                f.write(new_content)
            print(f"  {R}✔{N} Kotlin corrigido!\n")

def buildar():
    h("BUILDAR APK")
    print(f"  {R}1{N}  Debug")
    print(f"  {R}2{N}  Release")
    print(f"  {R}3{N}  App Bundle")
    tipo = input(f"\n  {R}❯{N} ").strip()
    if tipo in ("1", "2", "3"):
        tipo_map = {"1": "debug", "2": "release", "3": "appbundle"}
        fix_kotlin_version()
        run(f"bash {shlex.quote(BUILD_APK)} {tipo_map[tipo]}", check=False)
        print(f"\n  {R}✔{N} Build salvo em apks/\n")
    else:
        print(f"\n  {R}!{N} Opcao invalida\n")

def backup():
    h("BACKUP DA FERRAMENTA")
    import datetime
    import zipfile

    backup_base = os.path.join(BASE, "Backup", "ferramenta")
    os.makedirs(backup_base, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_zip = f"backup_{ts}.zip"
    caminho_zip = os.path.join(backup_base, nome_zip)

    arquivos = [
        "app.py",
        "build-apk.sh",
        "editar-informacoes.py",
        "fix-adb.sh",
        "configurar_de.py",
        "buildar.py",
        "configurar_gradle84.py",
        "atualizar.py",
        "version.txt",
        "AGENTS.md",
        "opencode.json",
    ]

    projeto_arquivos = [
        "pack.py",
        "restaurar_backup.py",
    ]

    print(f"  {A}→{N} Criando backup: {nome_zip}")

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for arq in arquivos:
            orig = os.path.join(BASE, arq)
            if os.path.exists(orig):
                zf.write(orig, arq)
                print(f"    {R}+{N} {arq}")
            else:
                print(f"    {A}~{N} {arq} (ignorado, nao existe)")

        for arq in projeto_arquivos:
            orig = os.path.join(PROJETO, arq)
            if os.path.exists(orig):
                zf.write(orig, f"projeto/{arq}")
                print(f"    {R}+{N} projeto/{arq}")
            else:
                print(f"    {A}~{N} projeto/{arq} (ignorado, nao existe)")

    tamanho = os.path.getsize(caminho_zip) / 1024
    print(f"\n  {R}✔{N} Backup salvo: Backup/ferramenta/{nome_zip} ({tamanho:.1f} KB)\n")

def restaurar():
    h("RESTAURAR BACKUP")
    import zipfile

    ferramenta_dir = os.path.join(BASE, "Backup", "ferramenta")
    backup_dir = os.path.join(BASE, "Backup")

    zips = []
    if os.path.isdir(ferramenta_dir):
        zips += [os.path.join(ferramenta_dir, f) for f in sorted(os.listdir(ferramenta_dir)) if f.endswith(".zip")]
    if os.path.isdir(backup_dir):
        zips += [os.path.join(backup_dir, f) for f in sorted(os.listdir(backup_dir)) if f.endswith(".zip")]

    if not zips:
        print(f"  {R}!{N} Nenhum backup encontrado\n")
        return

    print(f"  {A}Backups disponiveis:{N}\n")
    for i, z in enumerate(zips, 1):
        print(f"    {R}{i}{N}  {os.path.basename(z)}")

    escolha = input(f"\n  {R}❯{N} Escolha o backup (ou 0 pra cancelar): ").strip()
    if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(zips):
        print(f"  {R}!{N} Cancelado\n")
        return

    idx = int(escolha) - 1
    zip_sel = zips[idx]

    arquivos = [
        "app.py",
        "build-apk.sh",
        "editar-informacoes.py",
        "fix-adb.sh",
        "configurar_de.py",
        "buildar.py",
        "configurar_gradle84.py",
        "atualizar.py",
        "version.txt",
        "AGENTS.md",
        "opencode.json",
    ]

    print(f"\n  {A}→{N} Restaurando de: {os.path.basename(zip_sel)}")

    with zipfile.ZipFile(zip_sel, "r") as zf:
        for arq in arquivos:
            if arq in zf.namelist():
                zf.extract(arq, BASE)
                print(f"    {R}+{N} {arq}")

        projeto_files = [f for f in zf.namelist() if f.startswith("projeto/")]
        if projeto_files:
            projeto_dst = os.path.join(BASE, "projeto")
            os.makedirs(projeto_dst, exist_ok=True)
            for f in projeto_files:
                zf.extract(f, BASE)
            print(f"    {R}+{N} projeto/ (restaurado)")

    print(f"\n  {R}✔{N} Backup restaurado com sucesso!\n")

def reiniciar():
    h("REINICIAR PROJETO")
    restaurar()

def backup_projeto():
    h("BACKUP DO PROJETO")
    pack_path = os.path.join(PROJETO, "pack.py")
    if not os.path.exists(pack_path):
        print(f"  {R}!{N} pack.py nao encontrado em projeto/\n")
        return
    run(f"python3 {shlex.quote(pack_path)}", cwd=PROJETO)

def restaurar_projeto():
    h("RESTAURAR PROJETO")
    restore_path = os.path.join(PROJETO, "restaurar_backup.py")
    if not os.path.exists(restore_path):
        print(f"  {R}!{N} restaurar_backup.py nao encontrado em projeto/\n")
        return
    run(f"python3 {shlex.quote(restore_path)}", cwd=PROJETO)

def menu_config():
    while True:
        print(f"\n  {B}╔══════════════════════════╗{N}")
        print(f"  {B}║{N}      ⚙  CONFIGURACAO    {B}║{N}")
        print(f"  {B}╚══════════════════════════╝{N}")
        print(f"\n  {R}1{N}  Backup da ferramenta")
        print(f"  {R}2{N}  Restaurar backup")
        print(f"  {R}3{N}  Reiniciar projeto")
        print(f"  {R}4{N}  Voltar")
        op = input(f"\n  {R}❯{N} ").strip()

        if op == "1":
            backup()
        elif op == "2":
            restaurar()
        elif op == "3":
            reiniciar()
        elif op == "4":
            break
        else:
            print(f"\n  {R}!{N} Opcao invalida\n")

def editar_info():
    h("EDITAR INFORMACOES")
    run(f"bash {shlex.quote(EDITAR)} listar")
    print(f"\n  {A}Deixe em branco pra manter{N}\n")

    nome = input(f"  {R}❯{N} Nome do app: ").strip()
    pacote = input(f"  {R}❯{N} Pacote (ex: com.exemplo.app): ").strip()
    vc = input(f"  {R}❯{N} Version code: ").strip()
    vn = input(f"  {R}❯{N} Version name (ex: 1.0): ").strip()

    if nome:
        run(f"bash {shlex.quote(EDITAR)} nome {shlex.quote(nome)}")
    if pacote:
        run(f"bash {shlex.quote(EDITAR)} pacote {shlex.quote(pacote)}")
    if vc:
        run(f"bash {shlex.quote(EDITAR)} versao {shlex.quote(vc)}")
    if vn:
        run(f"bash {shlex.quote(EDITAR)} nomeversao {shlex.quote(vn)}")

    print(f"\n  {R}✔{N} Informacoes atualizadas!\n")

def corrigir_adb():
    h("CORRIGIR ADB")
    run(f"bash {shlex.quote(FIX_ADB)}", check=False)

def configurar_de():
    h("CONFIGURAR DE/ PRA GRADLE 8.4 + API 35")
    run(f"python3 {shlex.quote(CONFIGURAR_DE)}", check=False)

def verificar_atualizacoes():
    import importlib.util
    spec = importlib.util.spec_from_file_location("atualizar", ATUALIZAR)
    atualizar_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atualizar_mod)
    return atualizar_mod.tem_atualizacao()

def atualizar():
    import importlib.util
    spec = importlib.util.spec_from_file_location("atualizar", ATUALIZAR)
    atualizar_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atualizar_mod)
    atualizar_mod.atualizar()

def menu():
    tem_update = False
    try:
        import threading
        def check_update():
            nonlocal tem_update
            try:
                tem_update = verificar_atualizacoes()
            except Exception:
                pass
        t = threading.Thread(target=check_update, daemon=True)
        t.start()
    except Exception:
        pass

    while True:
        print(f"\n  {B}╔══════════════════════════╗{N}")
        print(f"  {B}║{N}     ⋆｡°✩ MENU ✩°｡⋆     {B}║{N}")
        print(f"  {B}╚══════════════════════════╝{N}")
        if tem_update:
            print(f"\n  {R}0{N}  ★ Atualizacao disponivel!")
        print(f"\n  {R}1{N}  Configurar ambiente")
        print(f"  {R}2{N}  Buildar APK")
        print(f"  {R}3{N}  Backup do projeto")
        print(f"  {R}4{N}  Restaurar projeto")
        print(f"  {R}5{N}  Backup da ferramenta")
        print(f"  {R}6{N}  Editar informacoes")
        print(f"  {R}7{N}  Corrigir ADB")
        print(f"  {R}8{N}  Configurar de/ (Gradle 8.4 + API 35)")
        print(f"  {R}9{N}  Sair")
        print(f"\n  {A}by alisu{N}")
        op = input(f"\n  {R}❯{N} ").strip()

        if op == "0" and tem_update:
            atualizar()
            tem_update = False
        elif op == "1":
            configurar()
        elif op == "2":
            buildar()
        elif op == "3":
            backup_projeto()
        elif op == "4":
            restaurar_projeto()
        elif op == "5":
            backup()
        elif op == "6":
            editar_info()
        elif op == "7":
            corrigir_adb()
        elif op == "8":
            configurar_de()
        elif op == "9":
            print(f"\n  {A}★ volte sempre ★{N}\n")
            break
        else:
            print(f"\n  {R}!{N} Opcao invalida\n")

if __name__ == "__main__":
    menu()
