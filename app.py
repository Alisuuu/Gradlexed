import os
import subprocess
import shutil
import shlex

BASE = os.path.dirname(os.path.abspath(__file__))
ALISU = os.path.join(BASE, ".alisu")
PROJETO = os.path.join(BASE, "projeto")
BUILD_APK = os.path.join(ALISU, "build-apk.sh")
EDITAR = os.path.join(ALISU, "editar-informacoes.py")
FIX_ADB = os.path.join(ALISU, "fix-adb.sh")
CONFIGURAR_PROJETO = os.path.join(ALISU, "configurar_projeto.py")
CONFIGURAR_DE = os.path.join(ALISU, "configurar_de.py")
ATUALIZAR = os.path.join(ALISU, "atualizar.py")
PACK = os.path.join(ALISU, "pack.py")
RESTAURAR = os.path.join(ALISU, "restaurar_backup.py")

OPENCODE_DIR = os.path.expanduser("~/.opencode/bin")
os.environ["PATH"] = OPENCODE_DIR + ":" + os.environ["PATH"]

SCRIPTS_ANTIGOS = [
    "configurar_projeto.py",
    "configurar_de.py",
    "editar-informacoes.py",
    "fix-adb.sh",
    "atualizar.py",
    "buildar.py",
    "build-apk.sh",
    "projeto/pack.py",
    "projeto/restaurar_backup.py",
]

def limpar_scripts_antigos():
    for nome in SCRIPTS_ANTIGOS:
        caminho = os.path.join(BASE, nome)
        if os.path.isfile(caminho):
            os.remove(caminho)

limpar_scripts_antigos()

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
        ".alisu/build-apk.sh",
        ".alisu/editar-informacoes.py",
        ".alisu/fix-adb.sh",
        ".alisu/configurar_de.py",
        ".alisu/configurar_projeto.py",
        ".alisu/buildar.py",
        ".alisu/atualizar.py",
        ".alisu/pack.py",
        ".alisu/restaurar_backup.py",
        ".alisu/_common.sh",
        ".alisu/fix_aapt2_arm64.sh",
        ".alisu/config_check.sh",
        "version.txt",
        "AGENTS.md",
        "opencode.json",
    ]

    projeto_arquivos = []

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
        ".alisu/build-apk.sh",
        ".alisu/editar-informacoes.py",
        ".alisu/fix-adb.sh",
        ".alisu/configurar_de.py",
        ".alisu/configurar_projeto.py",
        ".alisu/buildar.py",
        ".alisu/atualizar.py",
        ".alisu/pack.py",
        ".alisu/restaurar_backup.py",
        ".alisu/_common.sh",
        ".alisu/fix_aapt2_arm64.sh",
        ".alisu/config_check.sh",
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
    if not os.path.exists(PACK):
        print(f"  {R}!{N} pack.py nao encontrado em .alisu/\n")
        return
    run(f"python3 {shlex.quote(PACK)}", cwd=PROJETO)

def restaurar_projeto():
    h("RESTAURAR PROJETO")
    if not os.path.exists(RESTAURAR):
        print(f"  {R}!{N} restaurar_backup.py nao encontrado em .alisu/\n")
        return
    run(f"python3 {shlex.quote(RESTAURAR)}", cwd=PROJETO)

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
        print(f"  {R}3{N}  Backup do projeto")
        print(f"  {R}4{N}  Restaurar projeto")
        print(f"  {R}5{N}  Backup da ferramenta")
        print(f"  {R}6{N}  Restaurar ferramenta")
        print(f"  {R}7{N}  Editar informacoes")
        print(f"  {R}8{N}  Corrigir ADB")
        print(f"  {R}9{N}  Detectar projeto")
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
            backup_projeto()
        elif op == "4":
            restaurar_projeto()
        elif op == "5":
            backup()
        elif op == "6":
            restaurar()
        elif op == "7":
            editar_info()
        elif op == "8":
            corrigir_adb()
        elif op == "9":
            detectar_projeto()
        else:
            print(f"\n  {R}!{N} Opcao invalida\n")

if __name__ == "__main__":
    menu()
