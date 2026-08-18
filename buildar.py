import os
import sys
import subprocess
import shlex

BASE = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(BASE, "projeto")
BUILD_APK = os.path.join(BASE, "build-apk.sh")

def run(cmd, check=True, cwd=PROJETO):
    subprocess.run(cmd, shell=True, check=check, cwd=cwd, executable="/bin/bash")

def buildar():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        tipo = {"1": "debug", "2": "release", "3": "appbundle"}.get(arg, arg)
    else:
        print("=== Build ===")
        print("  1 - Debug APK")
        print("  2 - Release APK (assinado)")
        print("  3 - App Bundle (.aab)")
        print()
        choice = input("Escolha: ").strip()
        tipo = {"1": "debug", "2": "release", "3": "appbundle"}.get(choice, "debug")
    run(f"bash {shlex.quote(BUILD_APK)} {shlex.quote(tipo)}", check=False)

if __name__ == "__main__":
    buildar()
