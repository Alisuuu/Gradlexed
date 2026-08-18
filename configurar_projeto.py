#!/usr/bin/env python3
import os
import re
import stat
import subprocess
import sys

R = "\033[1;31m"
B = "\033[1;34m"
A = "\033[36m"
OK = "\033[1;32m"
N = "\033[0m"

ANDROID_HOME = os.environ.get("ANDROID_HOME", "/opt/android-sdk")
SDKMANAGER = os.path.join(ANDROID_HOME, "cmdline-tools", "latest", "bin", "sdkmanager")

BASE = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(BASE, "projeto")

_step = 0
_total = 0


def progress_start(total):
    global _step, _total
    _step = 0
    _total = total


def progress_next(label=""):
    global _step
    _step += 1
    print(f"\n  {B}[{_step}/{_total}]{N} {B}{label}{N}")


def h(text):
    print(f"\n  {B}{'─'*44}{N}")
    print(f"  {B}{text}{N}")
    print(f"  {B}{'─'*44}{N}")


def log(msg):
    print(f"  {A}→{N} {msg}")


def ok(msg):
    print(f"  {OK}✔{N} {msg}")


def err(msg):
    print(f"  {R}✗{N} {msg}")


def warn(msg):
    print(f"  {R}!{N} {msg}")


def fixed(msg):
    print(f"  {OK}+{N} {msg}")


def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def parse_value(pattern, content, default=None, flags=0):
    m = re.search(pattern, content, flags)
    return m.group(1) if m else default


def read_file(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def detect_project(projeto_dir):
    info = {}

    app_gradle = os.path.join(projeto_dir, "app", "build.gradle.kts")
    if not os.path.exists(app_gradle):
        app_gradle = os.path.join(projeto_dir, "app", "build.gradle")

    if os.path.exists(app_gradle):
        c = read_file(app_gradle)
        info["compileSdk"] = parse_value(r'compileSdk\s*=?\s*(\d+)', c)
        info["targetSdk"] = parse_value(r'targetSdk\s*=?\s*(\d+)', c)
        info["minSdk"] = parse_value(r'minSdk\s*=?\s*(\d+)', c)
        info["applicationId"] = parse_value(r'applicationId\s*=?\s*"([^"]+)"', c)
        info["namespace"] = parse_value(r'namespace\s*=?\s*"([^"]+)"', c)
        info["versionCode"] = parse_value(r'versionCode\s*=?\s*(\d+)', c)
        info["versionName"] = parse_value(r'versionName\s*=?\s*"([^"]+)"', c)
        info["gradle_file"] = app_gradle
    else:
        warn("app/build.gradle.kts nao encontrado")

    toml = os.path.join(projeto_dir, "gradle", "libs.versions.toml")
    if os.path.exists(toml):
        c = read_file(toml)
        info["agp"] = parse_value(r'^agp\s*=\s*"([^"]+)"', c, flags=re.MULTILINE)
        info["kotlin"] = parse_value(r'^kotlin\s*=\s*"([^"]+)"', c, flags=re.MULTILINE)
    else:
        root_gradle = os.path.join(projeto_dir, "build.gradle.kts")
        if not os.path.exists(root_gradle):
            root_gradle = os.path.join(projeto_dir, "build.gradle")
        if os.path.exists(root_gradle):
            c = read_file(root_gradle)
            info["agp"] = parse_value(r'com\.android\.tools\.build:gradle:([^\s"\']+)', c)

    wrapper = os.path.join(projeto_dir, "gradle", "wrapper", "gradle-wrapper.properties")
    if os.path.exists(wrapper):
        c = read_file(wrapper)
        info["gradle"] = parse_value(r'gradle-([0-9.]+)-bin\.zip', c)

    return info


AGP_GRADLE_COMPAT = {
    "8.13": {"min": "2.13", "max": "37"},
    "8.12": {"min": "2.12", "max": "36"},
    "8.11": {"min": "2.11", "max": "36"},
    "8.10": {"min": "2.10", "max": "36"},
    "8.9": {"min": "2.9", "max": "36"},
    "8.8": {"min": "2.8", "max": "35"},
    "8.7": {"min": "2.7", "max": "35"},
    "8.6": {"min": "2.6", "max": "35"},
    "8.5": {"min": "2.5", "max": "34"},
    "8.4": {"min": "2.4", "max": "34"},
    "8.3": {"min": "2.3", "max": "34"},
    "8.2": {"min": "2.2", "max": "34"},
    "8.1": {"min": "2.1", "max": "33"},
    "8.0": {"min": "2.0", "max": "33"},
    "7.4": {"min": "1.9", "max": "33"},
}

GRADLE_MIN = {
    "8.13": "8.13",
    "8.12": "8.13",
    "8.11": "8.11.1",
    "8.10": "8.11.1",
    "8.9": "8.11.1",
    "8.8": "8.10.2",
    "8.7": "8.9",
    "8.6": "8.7",
    "8.5": "8.7",
    "8.4": "8.6",
    "8.3": "8.4",
    "8.2": "8.2",
    "8.1": "8.0",
    "8.0": "8.0",
    "7.4": "7.5",
}


def get_agp_major(agp_ver):
    if not agp_ver:
        return None
    parts = agp_ver.split(".")
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else agp_ver


def check_compatibility(info):
    agp = info.get("agp", "")
    gradle = info.get("gradle", "")
    compile_sdk = info.get("compileSdk", "")

    if not agp or not compile_sdk:
        return

    agp_major = get_agp_major(agp)
    compat = AGP_GRADLE_COMPAT.get(agp_major, {})

    if compat:
        max_sdk = int(compat.get("max", 99))
        if compile_sdk and int(compile_sdk) > max_sdk:
            warn(f"AGP {agp} suporta no maximo compileSdk {max_sdk}")
            warn(f"O projeto usa compileSdk {compile_sdk}")
            log("O build pode funcionar mas com avisos")


def install_java():
    progress_next("Verificando Java")
    if subprocess.run(["which", "java"], capture_output=True).returncode == 0:
        ok("Java ja instalado")
        return True

    log("Instalando Java 17...")
    if subprocess.run(["which", "pkg"], capture_output=True).returncode == 0:
        subprocess.run(["pkg", "install", "openjdk-17", "-y"])
    elif subprocess.run(["which", "apt-get"], capture_output=True).returncode == 0:
        subprocess.run(["apt-get", "install", "-y", "openjdk-17-jdk-headless"])
    else:
        err("Gerenciador de pacotes nao encontrado")
        return False

    if subprocess.run(["which", "java"], capture_output=True).returncode != 0:
        err("Falha ao instalar Java")
        return False

    ok("Java instalado")
    return True


def install_git():
    progress_next("Verificando Git")
    if subprocess.run(["which", "git"], capture_output=True).returncode == 0:
        ok("Git ja instalado")
        return True

    log("Instalando Git...")
    if subprocess.run(["which", "pkg"], capture_output=True).returncode == 0:
        subprocess.run(["pkg", "install", "git", "-y"])
    elif subprocess.run(["which", "apt-get"], capture_output=True).returncode == 0:
        subprocess.run(["apt-get", "install", "-y", "git"])
    else:
        err("Gerenciador de pacotes nao encontrado")
        return False

    if subprocess.run(["which", "git"], capture_output=True).returncode != 0:
        err("Falha ao instalar Git")
        return False

    ok("Git instalado")
    return True


def install_sdk():
    progress_next("Verificando Android SDK")
    sdkmanager = SDKMANAGER
    if os.path.exists(sdkmanager):
        ok("Android SDK ja instalado")
        return True

    tmp = "/tmp/cmdline-tools.zip"

    MIN_SIZE = 100_000_000  # 100MB - zip real tem ~180MB

    if os.path.exists(tmp) and os.path.getsize(tmp) > MIN_SIZE:
        log(f"Zip ja existe ({os.path.getsize(tmp) // 1024}KB), usando...")
        downloaded = True
    else:
        if os.path.exists(tmp):
            log(f"Zip invalido ({os.path.getsize(tmp) // 1024}KB < {MIN_SIZE // 1024}KB), removendo...")
            subprocess.run(["rm", "-f", tmp], check=False)
        log("Baixando Android SDK cmdline-tools...")
        os.makedirs(ANDROID_HOME, exist_ok=True)

        urls = [
            "https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip",
            "https://dl.google.com/android/repository/commandlinetools-linux-11391160_latest.zip",
            "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip",
        ]

        downloaded = False
        has_aria2 = subprocess.run(["which", "aria2c"], capture_output=True).returncode == 0
        has_wget = subprocess.run(["which", "wget"], capture_output=True).returncode == 0

        for url in urls:
            fname = url.split("/")[-1]
            current_size = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            if current_size > 0:
                log(f"Retomando {fname} ({current_size // 1024}KB ja baixados)...")
            else:
                log(f"Baixando {fname}...")

            if has_aria2:
                log("usando aria2c (rapido, 8 conexoes)...")
                result = subprocess.run([
                    "aria2c", "-x", "8", "-s", "8", "-k", "1M",
                    "--connect-timeout=15", "--max-tries=3",
                    "--continue=true",
                    "-d", "/tmp", "-o", "cmdline-tools.zip",
                    url
                ])
            elif has_wget:
                log("usando wget (com resume)...")
                result = subprocess.run([
                    "wget", "-q", "--show-progress",
                    "--tries=3", "--timeout=15",
                    "-c", "-O", tmp, url
                ])
            else:
                log("usando curl (com resume)...")
                result = subprocess.run([
                    "curl", "-C", "-",
                    "--connect-timeout", "15", "--max-time", "1800",
                    "--retry", "2", "--retry-delay", "3",
                    "-fSL", "-o", tmp, url
                ])

            if result.returncode != 0:
                sz = os.path.getsize(tmp) // 1024 if os.path.exists(tmp) else 0
                log(f"Falha no download ({sz}KB baixados)")
                continue
            if os.path.exists(tmp) and os.path.getsize(tmp) > MIN_SIZE:
                downloaded = True
                log(f"Download OK ({os.path.getsize(tmp) // 1024}KB)")
                break
            else:
                sz = os.path.getsize(tmp) // 1024 if os.path.exists(tmp) else 0
                log(f"Arquivo invalido ({sz}KB < {MIN_SIZE // 1024}KB)")

    if not downloaded:
        err("Falha ao baixar cmdline-tools")
        log("Tentando install via apt...")
        result = subprocess.run(["apt-get", "install", "-y", "google-android-cmdline-tools"], capture_output=True)
        if result.returncode == 0 and os.path.exists(sdkmanager):
            ok("Android SDK instalado via apt")
            return True
        err("Nao foi possivel baixar o SDK")
        return False

    log("Extraindo...")
    subprocess.run(["rm", "-rf", "/tmp/sdk"], check=False)
    
    result = subprocess.run(["file", tmp], capture_output=True, text=True)
    if "Zip" not in result.stdout and "zip" not in result.stdout.lower():
        err(f"Arquivo nao e zip valido: {result.stdout.strip()[:60]}")
        subprocess.run(["rm", "-f", tmp], check=False)
        return False

    result = subprocess.run(["unzip", "-t", tmp], capture_output=True, text=True)
    if result.returncode != 0:
        err(f"Zip corrompido, removendo...")
        subprocess.run(["rm", "-f", tmp], check=False)
        return False

    result = subprocess.run(["unzip", "-qo", tmp, "-d", "/tmp/sdk"], capture_output=True, text=True)
    if result.returncode != 0:
        err(f"Falha ao extrair: {result.stderr.strip()[:80]}")
        subprocess.run(["rm", "-rf", "/tmp/sdk", tmp], check=False)
        return False

    cmdline_src = "/tmp/sdk/cmdline-tools"
    if not os.path.isdir(cmdline_src):
        log("Procurando cmdline-tools no zip...")
        contents = os.listdir("/tmp/sdk") if os.path.isdir("/tmp/sdk") else []
        for item in contents:
            if "cmdline-tools" in item.lower():
                cmdline_src = os.path.join("/tmp/sdk", item)
                break

    if not os.path.isdir(cmdline_src):
        err(f"Estrutura do zip invalida. Conteudo: {contents}")
        subprocess.run(["rm", "-rf", "/tmp/sdk", tmp], check=False)
        return False

    os.makedirs(os.path.join(ANDROID_HOME, "cmdline-tools"), exist_ok=True)
    dest = os.path.join(ANDROID_HOME, "cmdline-tools", "latest")
    if os.path.exists(dest):
        subprocess.run(["rm", "-rf", dest], check=False)

    result = subprocess.run(["mv", cmdline_src, dest], capture_output=True, text=True)
    if result.returncode != 0:
        err(f"Falha ao mover: {result.stderr.strip()[:80]}")
        subprocess.run(["rm", "-rf", "/tmp/sdk", tmp], check=False)
        return False

    subprocess.run(["rm", "-rf", "/tmp/sdk", tmp], check=False)

    if not os.path.exists(sdkmanager):
        err(f"sdkmanager nao encontrado em {sdkmanager}")
        return False

    log("Aceitando licencas...")
    subprocess.run(f"yes | {sdkmanager} --licenses > /dev/null 2>&1", shell=True)

    ok("Android SDK instalado")
    return True


def install_platform(compile_sdk):
    progress_next("Verificando platform Android")
    if not compile_sdk:
        return

    sdkmanager = SDKMANAGER
    if not os.path.exists(sdkmanager):
        err(f"sdkmanager nao encontrado: {sdkmanager}")
        return

    platform = f"platforms;android-{compile_sdk}"
    result = run(f"{sdkmanager} --list_installed | grep '{platform}'")
    if platform in result.stdout:
        ok(f"Platform {platform} ja instalada")
        return

    log(f"Instalando {platform}...")
    result = subprocess.run([sdkmanager, platform])
    if result.returncode != 0:
        err(f"Falha ao instalar {platform}")
        return
    ok(f"{platform} instalada")


def install_build_tools():
    progress_next("Verificando build-tools")
    sdkmanager = SDKMANAGER
    if not os.path.exists(sdkmanager):
        err(f"sdkmanager nao encontrado: {sdkmanager}")
        return

    result = run(f"{sdkmanager} --list_installed | grep 'build-tools;'")
    if "build-tools" in result.stdout:
        ok("Build-tools ja instalado")
        return

    log("Instalando build-tools;36.0.0...")
    result = subprocess.run([sdkmanager, "build-tools;36.0.0"])
    if result.returncode != 0:
        err("Falha ao instalar build-tools;36.0.0")
        return
    ok("build-tools;36.0.0 instalado")


def install_aapt2():
    progress_next("Verificando aapt2")
    aapt2 = "/usr/local/bin/aapt2"
    if os.path.exists(aapt2):
        ok("aapt2 ja instalado")
        return

    log("Instalando aapt2...")
    if subprocess.run(["which", "apt-get"], capture_output=True).returncode == 0:
        subprocess.run(["apt-get", "install", "-y", "aapt"])
    if os.path.exists(aapt2):
        ok("aapt2 instalado")
    else:
        warn("aapt2 nao encontrado - pode ser necessario manualmente")


def setup_local_properties(projeto_dir):
    progress_next("Configurando local.properties")
    props = os.path.join(projeto_dir, "local.properties")
    sdk_dir = ANDROID_HOME
    content = f"sdk.dir={sdk_dir}\n"

    if os.path.exists(props):
        existing = read_file(props)
        if f"sdk.dir={sdk_dir}" in existing:
            ok("local.properties ja configurado")
            return
        write_file(props, content)
    else:
        write_file(props, content)

    ok("local.properties configurado")


def setup_gradlew(projeto_dir):
    progress_next("Verificando gradlew")
    gradlew = os.path.join(projeto_dir, "gradlew")
    if not os.path.exists(gradlew):
        warn("gradlew nao encontrado")
        return

    st = os.stat(gradlew)
    if not (st.st_mode & stat.S_IXUSR):
        os.chmod(gradlew, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        fixed("gradlew agora e executavel")
    else:
        ok("gradlew ja e executavel")


def setup_gradle_props(projeto_dir):
    progress_next("Configurando gradle.properties")
    props = os.path.join(projeto_dir, "gradle.properties")
    content = read_file(props) if os.path.exists(props) else ""

    changes = []
    lines_to_add = []

    if "android.useAndroidX=true" not in content:
        lines_to_add.append("android.useAndroidX=true")
        changes.append("useAndroidX")

    if "android.enableJetifier=true" not in content:
        lines_to_add.append("android.enableJetifier=true")
        changes.append("enableJetifier")

    aapt2_line = "android.aapt2FromMavenOverride=/usr/local/bin/aapt2"
    if aapt2_line not in content and os.path.exists("/usr/local/bin/aapt2"):
        lines_to_add.append(aapt2_line)
        changes.append("aapt2 override")

    if lines_to_add:
        content = content.rstrip() + "\n" + "\n".join(lines_to_add) + "\n"
        write_file(props, content)
        fixed(f"gradle.properties: {', '.join(changes)}")
    else:
        ok("gradle.properties ja configurado")


def setup_suppress_sdk(projeto_dir, info):
    progress_next("Configurando suppressUnsupportedCompileSdk")
    compile_sdk = info.get("compileSdk")
    if not compile_sdk:
        return

    props = os.path.join(projeto_dir, "gradle.properties")
    content = read_file(props) if os.path.exists(props) else ""

    needed = f"android.suppressUnsupportedCompileSdk=35,{compile_sdk},{compile_sdk}.0"
    if needed in content:
        ok("suppressUnsupportedCompileSdk ja configurado")
        return

    old_suppress = re.search(r'android\.suppressUnsupportedCompileSdk\s*=\s*([^\n]+)', content)
    if old_suppress:
        old_val = old_suppress.group(1).strip()
        if str(compile_sdk) not in old_val:
            new_val = f"{old_val},{compile_sdk},{compile_sdk}.0"
            content = content.replace(
                f"android.suppressUnsupportedCompileSdk={old_val}",
                f"android.suppressUnsupportedCompileSdk={new_val}"
            )
            write_file(props, content)
            fixed(f"suppressUnsupportedCompileSdk atualizado: {new_val}")
        else:
            ok("suppressUnsupportedCompileSdk ja contem este SDK")
    else:
        content = content.rstrip() + f"\nandroid.suppressUnsupportedCompileSdk=35,{compile_sdk},{compile_sdk}.0\n"
        write_file(props, content)
        fixed(f"suppressUnsupportedCompileSdk adicionado: 35,{compile_sdk},{compile_sdk}.0")


def setup_gradle_wrapper(projeto_dir, info):
    progress_next("Verificando Gradle wrapper")
    gradle_ver = info.get("gradle")
    agp_ver = info.get("agp")
    if not gradle_ver or not agp_ver:
        return

    agp_major = get_agp_major(agp_ver)
    min_gradle = GRADLE_MIN.get(agp_major)
    if not min_gradle:
        return

    if gradle_ver >= min_gradle:
        ok(f"Gradle {gradle_ver} compativel com AGP {agp_ver}")
        return

    wrapper_path = os.path.join(projeto_dir, "gradle", "wrapper", "gradle-wrapper.properties")
    if not os.path.exists(wrapper_path):
        return

    content = read_file(wrapper_path)
    new_url = re.sub(
        r'gradle-[0-9.]+-bin\.zip',
        f'gradle-{min_gradle}-bin.zip',
        content
    )
    if new_url != content:
        write_file(wrapper_path, new_url)
        fixed(f"Gradle wrapper atualizado: {gradle_ver} -> {min_gradle}")
    else:
        ok(f"Gradle wrapper ja esta em {min_gradle}")


def setup_keystore(projeto_dir):
    progress_next("Verificando keystore")
    for gradle_name in ["build.gradle.kts", "build.gradle"]:
        gradle = os.path.join(projeto_dir, "app", gradle_name)
        if not os.path.exists(gradle):
            continue

        content = read_file(gradle)
        m = re.search(r'rootProject\.file\("\.\.\/keystore\/([^"]+)"\)', content)
        if not m:
            continue

        ks_name = m.group(1)
        ks_path = os.path.join(BASE, "keystore", ks_name)

        if os.path.exists(ks_path):
            ok(f"Keystore {ks_name} encontrado")
        else:
            warn(f"Keystore {ks_name} nao encontrado em {ks_path}")
        return


def run_checks(projeto_dir):
    info = detect_project(projeto_dir)

    log(f"compileSdk: {info.get('compileSdk', '?')}")
    log(f"targetSdk: {info.get('targetSdk', '?')}")
    log(f"minSdk: {info.get('minSdk', '?')}")
    log(f"AGP: {info.get('agp', '?')}")
    log(f"Gradle: {info.get('gradle', '?')}")
    log(f"Package: {info.get('applicationId', '?')}")

    return info


def configurar_ambiente():
    h("CONFIGURAR AMBIENTE")
    progress_start(5)

    ok_java = install_java()
    ok_git = install_git()
    ok_sdk = install_sdk()
    if ok_sdk:
        install_build_tools()
        install_aapt2()
        ok("Ambiente configurado!")
    else:
        err("Falha ao configurar ambiente - SDK nao instalado")
        return False
    return True


def configurar_projeto(projeto_dir=None):
    if projeto_dir is None:
        projeto_dir = PROJETO

    h("CONFIGURAR PROJETO")

    if not os.path.isdir(projeto_dir):
        err(f"Pasta do projeto nao encontrada: {projeto_dir}")
        return False

    progress_start(9)

    info = run_checks(projeto_dir)

    check_compatibility(info)

    install_platform(info.get("compileSdk"))
    install_build_tools()
    setup_local_properties(projeto_dir)
    setup_gradlew(projeto_dir)
    setup_gradle_props(projeto_dir)
    setup_suppress_sdk(projeto_dir, info)
    setup_gradle_wrapper(projeto_dir, info)
    setup_keystore(projeto_dir)

    ok("Projeto configurado!")
    return True


def configurar_tudo(projeto_dir=None):
    h("CONFIGURAR TUDO (AMBIENTE + PROJETO)")
    if not configurar_ambiente():
        return False
    configurar_projeto(projeto_dir)
    ok("Tudo configurado! Pronto pra buildar.")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        path = sys.argv[2] if len(sys.argv) > 2 else None
        if cmd == "ambiente":
            configurar_ambiente()
        elif cmd == "projeto":
            configurar_projeto(path)
        elif cmd == "tudo":
            configurar_tudo(path)
        elif cmd == "detectar":
            info = detect_project(path or PROJETO)
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print("Uso: configurar_projeto.py [ambiente|projeto|tudo|detectar] [caminho]")
    else:
        configurar_tudo()
