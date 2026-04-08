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
    target_file = os.path.join("core", "config.py")
    if not os.path.exists(target_file):
        return "2.0.0"
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'CURRENT_VERSION\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else "2.0.0"

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

    # 2. Definir comando PyInstaller (MODO DIRECTORIO en lugar de ONEFILE)
    app_exe_name = "ChvstxNexus"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onedir",
        "--clean",
        "--hidden-import=py7zr",
        "--hidden-import=rarfile",
        "--hidden-import=cloudscraper",
        "--hidden-import=bs4",
        "--hidden-import=requests",
        f"--name={app_exe_name}",
        "main.py"
    ]
    
    print(f"📦 Ejecutando PyInstaller: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print(f"\n✅ PyInstaller: ¡Directorio construido en 'dist/{app_exe_name}'!")
    except Exception as e:
        print(f"\n❌ Error durante PyInstaller: {e}")
        return

    # 3. Generar assets para Inno Setup (Imágenes y Texto Limpio)
    try:
        from PIL import Image, ImageDraw, ImageFont
        # Banner (164x314)
        img_banner = Image.new('RGB', (164, 314), color='#121212')
        draw_b = ImageDraw.Draw(img_banner)
        draw_b.rectangle([(10, 10), (154, 304)], outline='#00e5ff', width=3)
        img_banner.save("dist/wizard_banner.bmp")
        
        # Small Logo (55x55)
        img_small = Image.new('RGB', (55, 55), color='#121212')
        draw_s = ImageDraw.Draw(img_small)
        draw_s.ellipse([(5, 5), (50, 50)], outline='#00e5ff', width=3)
        img_small.save("dist/wizard_small.bmp")
    except Exception as e:
        print("Aviso: No se pudieron generar imágenes personalizadas:", e)

    # Limpiar README.md para Inno Setup
    tutorial_path = "dist/tutorial.txt"
    with open("README.md", "r", encoding="utf-8") as f:
        rmd = f.read()
    # Quitar imágenes markdown
    rmd = re.sub(r'!\[.*?\]\(.*?\)', '', rmd)
    # Quitar hipervínculos markdown
    rmd = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', rmd)
    with open(tutorial_path, "w", encoding="utf-8") as f:
        f.write(rmd)

    # 4. Generar archivo .iss para Inno Setup
    iss_content = f"""[Setup]
AppName={APP_NAME}
AppVersion={version}
AppPublisher=DavidFR-2000
AppPublisherURL=https://github.com/DavidFR-2000/ChvstxNexux
DefaultDirName={{localappdata}}\\Programs\\ChvstxNexus
DefaultGroupName={APP_NAME}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=ChvstxNexus_v{version}_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
InfoBeforeFile=dist\\tutorial.txt
WizardImageFile=dist\\wizard_banner.bmp
WizardSmallImageFile=dist\\wizard_small.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\{app_exe_name}\\{app_exe_name}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\{app_exe_name}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\{APP_NAME}"; Filename: "{{app}}\\{app_exe_name}.exe"
Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{app_exe_name}.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{app_exe_name}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent
"""
    
    iss_path = "build_installer.iss"
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    print(f"✅ Script de instalación generado: {iss_path}")
    
    # 4. Intentar ejecutar Inno Setup Compiler (ISCC)
    # Buscamos rutas comunes de Inno Setup
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    ]
    
    iscc_exe = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_exe = path
            break
            
    if iscc_exe:
        print(f"📦 Compilando Instalador con Inno Setup ({iscc_exe})...")
        try:
            subprocess.check_call([iscc_exe, iss_path])
            print(f"\n🎉 ¡ÉXITO! El instalador final (ChvstxNexus_v{version}_Setup.exe) está en la carpeta 'dist'.")
            print("\n⚠️  RECUERDA:")
            print(f"1. Sube tus cambios: git add . && git commit -m 'Release v{version}' && git push")
            print(f"2. Crea un Release en GitHub con el tag 'v{version}' y sube el instalador de la carpeta 'dist'.")
        except Exception as e:
            print(f"\n❌ Error empaquetando con Inno Setup: {e}")
    else:
        print("\n⚠️  ATENCIÓN: Inno Setup no se encontró en las rutas estándar.")
        print("Para que se genere el instalador profesional ChvstxNexus_v{version}_Setup.exe:")
        print("1. Descarga e instala Inno Setup de https://jrsoftware.org/isdl.php")
        print(f"2. Haz clic derecho en '{iss_path}' y selecciona 'Compile' o abre Inno Setup y compila el script.")

if __name__ == "__main__":
    build()

