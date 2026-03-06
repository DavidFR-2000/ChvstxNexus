import os
import subprocess
import sys
import re

APP_NAME = "Chvstx Nexus"

def update_readme_version(version):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Actualizar badge de versión: badge/version-1.0.0-blue
    new_content = re.sub(r"badge/version-[\d\.]+-blue", f"badge/version-{version}-blue", content)
    
    if new_content != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ README.md actualizado a la versión {version}")

def get_current_version():
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'CURRENT_VERSION\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else "1.0.0"

def build():
    print(f"🚀 Iniciando proceso de empaquetado de {APP_NAME}...")
    
    version = get_current_version()
    update_readme_version(version)
    
    # 1. Verificar PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Definir comando
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--name=ChvstxNexus_v{version}",
        "main.py"
    ]
    
    print(f"📦 Ejecutando: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print(f"\n✅ ¡Éxito! El ejecutable ChvstxNexus_v{version}.exe se ha generado en la carpeta 'dist'.")
        print("\n⚠️  RECUERDA:")
        print(f"1. Sube tus cambios: git add . && git commit -m 'Release v{version}' && git push")
        print(f"2. Crea un Release en GitHub con el tag 'v{version}' y sube el .exe de la carpeta 'dist'.")
    except Exception as e:
        print(f"\n❌ Error durante el empaquetado: {e}")

if __name__ == "__main__":
    build()
