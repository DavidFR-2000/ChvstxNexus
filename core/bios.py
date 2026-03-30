import os
import requests
from PySide6.QtCore import QThread, Signal

# Map of console names to their required RetroArch BIOS filenames and Github path
BIOS_MAP = {
    "PS1": [
        ("scph5500.bin", "bios/Sony/PlayStation/scph5500.bin"),
        ("scph5501.bin", "bios/Sony/PlayStation/scph5501.bin"),
        ("scph5502.bin", "bios/Sony/PlayStation/scph5502.bin")
    ],
    "Saturn": [
        ("mpr-17933.bin", "bios/Sega/Saturn/mpr-17933.bin"),
        ("sega_101.bin", "bios/Sega/Saturn/sega_101.bin")
    ],
    "Sega CD": [
        ("bios_CD_E.bin", "bios/Sega/Mega-CD/bios_CD_E.bin"),
        ("bios_CD_J.bin", "bios/Sega/Mega-CD/bios_CD_J.bin"),
        ("bios_CD_U.bin", "bios/Sega/Mega-CD/bios_CD_U.bin")
    ],
    "GBA": [
        ("gba_bios.bin", "bios/Nintendo/Game Boy Advance/gba_bios.bin")
    ],
    "PS2": [
        ("pcsx2/bios/scph39001.bin", "bios/Sony/PlayStation 2/ps2_scph39001.bin"),
        ("pcsx2/bios/rom1.bin", "bios/Sony/PlayStation 2/rom1.bin")
    ]
}

def needs_bios(console_name, system_dir):
    needed = BIOS_MAP.get(console_name)
    if not needed:
        return False
    for local_name, _ in needed:
        if not os.path.exists(os.path.join(system_dir, local_name)):
            return True
    return False

class BiosDownloadWorker(QThread):
    progress = Signal(str, int)  # file, percentage 0-100
    finished = Signal(bool, str) # success, message

    def __init__(self, console_name, system_dir):
        super().__init__()
        self.console_name = console_name
        self.system_dir = system_dir
        self.base_url = "https://raw.githubusercontent.com/Abdess/retrobios/main/"

    def run(self):
        needed = BIOS_MAP.get(self.console_name)
        if not needed:
            self.finished.emit(True, "No se requieren BIOS")
            return
            
        os.makedirs(self.system_dir, exist_ok=True)
        missing = [(l, r) for l, r in needed if not os.path.exists(os.path.join(self.system_dir, l))]
                
        if not missing:
            self.finished.emit(True, "OK")
            return
            
        for idx, (local_name, repo_path) in enumerate(missing):
            url = self.base_url + repo_path
            self.progress.emit(f"Descargando BIOS: {local_name}", int((idx/len(missing))*100))
            
            try:
                r = requests.get(url, stream=True, timeout=10)
                if r.status_code == 200:
                    local_path = os.path.join(self.system_dir, local_name)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    pct = int((downloaded / total_size) * 100)
                                    sub_pct = int((idx/len(missing))*100) + int((pct/100) * (100/len(missing)))
                                    self.progress.emit(f"Descargando BIOS: {local_name}", sub_pct)
                else:
                    self.finished.emit(False, f"Error 404: BIOS {local_name} no encontrada en github.")
                    return
            except Exception as e:
                self.finished.emit(False, f"Error de red:\n{e}")
                return
                
        self.finished.emit(True, "BIOS instaladas con éxito")
