import os
import re
import unicodedata
import difflib
import subprocess
from core.config import APP_NAME

def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def clean_rom_name(filename):
    """Limpia un nombre de ROM eliminando tags de región, versión, etc."""
    name = os.path.splitext(filename)[0]
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = re.sub(r'\s*\[[^\]]*\]', '', name)
    name = re.sub(r'\s*(?:Disc|CD|Disk)\s*\d+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*v\d+[\.\d]*', '', name, flags=re.IGNORECASE)
    name = name.replace('_', ' ')
    name = re.sub(r'\s*-\s*$', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def name_similarity(a, b):
    def normalize(text):
        text = str(text).lower().strip()
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        return re.sub(r'[^a-z0-9\s]', '', text)
    
    a_norm = normalize(a)
    b_norm = normalize(b)
    
    if not a_norm or not b_norm: return 0.0
    
    if ":" in b and ":" not in a:
        b_base = normalize(b.split(":")[0])
        score = difflib.SequenceMatcher(None, a_norm, b_base).ratio()
    else:
        score = difflib.SequenceMatcher(None, a_norm, b_norm).ratio()
        
    if a_norm in b_norm or b_norm in a_norm:
        score += 0.1
        
    len_diff = abs(len(a_norm) - len(b_norm))
    penalty = min(0.3, (len_diff / max(len(a_norm), len(b_norm), 1)) * 0.5)
    
    return max(0.0, min(1.0, score - penalty))

def create_desktop_shortcut(target_exe):
    try:
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
        
        ps_script = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_exe}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
        $Shortcut.Save()
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"Error creando acceso directo: {e}")
        return False
