import os
import subprocess
import shutil
import shlex

BASE = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(BASE, "projeto")
BUILD_APK = os.path.join(BASE, "build-apk.sh")
EDITAR = os.path.join(BASE, "editar-informacoes.py")
FIX_ADB = os.path.join(BASE, "fix-adb.sh")
CONFIGURAR_PROJETO = os.path.join(BASE, "configurar_projeto.py")
CONFIGURAR_DE = os.path.join(BASE, "configurar_de.py")
ATUALIZAR = os.path.join(BASE, "atualizar.py")

OPENCODE_DIR = os.path.expanduser("~/.opencode/bin")
os.environ["PATH"] = OPENCODE_DIR + ":" + os.environ["PATH"]

R = "\033[1;31m"
B = "\033[1;34m"
A = "\033[36m"
OK = "\033[1;32m"
N = "\033[0m"

def h(text):
    print(f"\n  {B}{'─'*44}{N}")
    print(f"  {B}{text}{N}")
    print(f"  {B}{'─'*44}{N}")

def run(cmd, check=True, cwd=PROJETO):
    subprocess.run(cmd, shell=True, check=check, cwd=cwd, executable="/bin/bash")

def configurar():
    h("CONFIGURAR AMBIENTE + PROJETO")
    run(f"python3 {shlex.quote(CONFIGURAR_PROJETO)} tudo", check=False)

def configurar_ambiente():
    h("CONFIGURAR AMBIENTE")
    run(f"python3 {shlex.quote(CONFIGURAR_PROJETO)} ambiente", check=False)

def configurar_projeto():
    h("CONFIGURAR PROJETO")
    run(f"python3 {shlex.quote(CONFIGURAR_PROJETO)} projeto", check=False)

def detectar_projeto():
    h("DETECTAR PROJETO")
    run(f"python3 {shlex.quote(CONFIGURAR_PROJETO)} detectar", check=False)

def buildar():
    h("BUILDAR APK")
    print(f"  {R}1{N}  Debug")
    print(f"  {R}2{N}  Release")
    print(f"  {R}3{N}  App Bundle")
    tipo = input(f"\n  {R}❯{N} ").strip()
    if tipo in ("1", "2", "3"):
        tipo_map = {"1": "debug", "2": "release", "3": "appbundle"}
        run(f"bash {shlex.quote(BUILD_APK)} {tipo_map[tipo]}", check=False)
        print(f"\n  {OK}✔{N} Build salvo em apks/\n")
    else:
        print(f"\n  {R}!{N} Opcao invalida\n")

def instalar_apk():
    h("INSTALAR APK VIA ADB")

    apks_dir = os.path.join(BASE, "apks")
    if not os.path.isdir(apks_dir):
        print(f"  {R}!{N} Pasta apks/ nao encontrada\n")
        return

    apks = sorted([f for f in os.listdir(apks_dir) if f.endswith(".apk")])
    if not apks:
        print(f"  {R}!{N} Nenhum APK encontrado em apks/\n")
        return

    print(f"\n  {A}APKs disponiveis:{N}\n")
    for i, apk in enumerate(apks, 1):
        tam = os.path.getsize(os.path.join(apks_dir, apk)) / (1024 * 1024)
        print(f"    {R}{i}{N}  {apk} ({tam:.1f} MB)")

    escolha = input(f"\n  {R}❯{N} Escolha o APK (ou 0 pra cancelar): ").strip()
    if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(apks):
        print(f"  {R}!{N} Cancelado\n")
        return

    apk_sel = apks[int(escolha) - 1]
    apk_path = os.path.join(apks_dir, apk_sel)

    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    lines = [l for l in result.stdout.strip().split("\n")[1:] if l.strip() and "offline" not in l]

    if not lines:
        print(f"\n  {R}!{N} Nenhum aparelho conectado\n")
        return

    devices = []
    for line in lines:
        parts = line.split()
        devices.append(parts[0])

    if len(devices) == 1:
        device = devices[0]
    else:
        print(f"\n  {A}Aparelhos conectados:{N}\n")
        for i, d in enumerate(devices, 1):
            print(f"    {R}{i}{N}  {d}")
        d_escolha = input(f"\n  {R}❯{N} Escolha o aparelho: ").strip()
        if not d_escolha.isdigit() or int(d_escolha) < 1 or int(d_escolha) > len(devices):
            print(f"  {R}!{N} Cancelado\n")
            return
        device = devices[int(d_escolha) - 1]

    print(f"\n  {A}→{N} Instalando {apk_sel} em {device}...")

    tmp = f"/data/local/tmp/{apk_sel}"
    push = subprocess.run(
        ["adb", "-s", device, "push", apk_path, tmp],
        capture_output=True, text=True
    )
    if push.returncode != 0:
        print(f"  {R}!{N} Falha ao enviar APK: {push.stderr.strip()}\n")
        return

    install = subprocess.run(
        ["adb", "-s", device, "shell", "pm", "install", "-r", "-t", tmp],
        capture_output=True, text=True
    )
    subprocess.run(["adb", "-s", device, "shell", "rm", "-f", tmp], capture_output=True)

    if "Success" in install.stdout:
        print(f"\n  {OK}✔{N} APK instalado com sucesso!\n")
    else:
        print(f"\n  {R}!{N} Falha na instalacao: {install.stdout.strip()}{install.stderr.strip()}\n")

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
        "configurar_projeto.py",
        "buildar.py",
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
                print(f"    {OK}+{N} {arq}")
            else:
                print(f"    {A}~{N} {arq} (ignorado)")

        for arq in projeto_arquivos:
            orig = os.path.join(PROJETO, arq)
            if os.path.exists(orig):
                zf.write(orig, f"projeto/{arq}")
                print(f"    {OK}+{N} projeto/{arq}")
            else:
                print(f"    {A}~{N} projeto/{arq} (ignorado)")

    tamanho = os.path.getsize(caminho_zip) / 1024
    print(f"\n  {OK}✔{N} Backup salvo: Backup/ferramenta/{nome_zip} ({tamanho:.1f} KB)\n")

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
        "configurar_projeto.py",
        "buildar.py",
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
                print(f"    {OK}+{N} {arq}")

        projeto_files = [f for f in zf.namelist() if f.startswith("projeto/")]
        if projeto_files:
            projeto_dst = os.path.join(BASE, "projeto")
            os.makedirs(projeto_dst, exist_ok=True)
            for f in projeto_files:
                zf.extract(f, BASE)
            print(f"    {OK}+{N} projeto/ (restaurado)")

    print(f"\n  {OK}✔{N} Backup restaurado com sucesso!\n")

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

    print(f"\n  {OK}✔{N} Informacoes atualizadas!\n")

def corrigir_adb():
    h("CORRIGIR ADB")
    run(f"bash {shlex.quote(FIX_ADB)}", check=False)

def configurar_de():
    h("CONFIGURAR DE/ PRA GRADLE 8.13 + API 37")
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
        print(f"\n  {R}1{N}  Configurar ambiente + projeto")
        print(f"  {R}2{N}  Buildar APK")
        print(f"  {R}3{N}  Instalar APK")
        print(f"  {R}4{N}  Backup do projeto")
        print(f"  {R}5{N}  Restaurar projeto")
        print(f"  {R}6{N}  Backup da ferramenta")
        print(f"  {R}7{N}  Restaurar ferramenta")
        print(f"  {R}8{N}  Editar informacoes")
        print(f"  {R}9{N}  Corrigir ADB")
        print(f"  {R}a{N}  Detectar projeto")
        print(f"  {R}x{N}  Sair")
        print(f"\n  {A}by alisu{N}")
        op = input(f"\n  {R}❯{N} ").strip()

        if op == "0" and tem_update:
            atualizar()
            tem_update = False
        elif op == "x" or op == "X":
            print(f"\n  {A}★ volte sempre ★{N}\n")
            break
        elif op == "1":
            configurar()
        elif op == "2":
            buildar()
        elif op == "3":
            instalar_apk()
        elif op == "4":
            backup_projeto()
        elif op == "5":
            restaurar_projeto()
        elif op == "6":
            backup()
        elif op == "7":
            restaurar()
        elif op == "8":
            editar_info()
        elif op == "9":
            corrigir_adb()
        elif op == "a" or op == "A":
            detectar_projeto()
        else:
            print(f"\n  {R}!{N} Opcao invalida\n")

if __name__ == "__main__":
    menu()
