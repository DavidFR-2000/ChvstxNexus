import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json, os, subprocess, threading, requests, re, time, datetime, zipfile, shutil, tempfile, webbrowser
try:
    import py7zr
except ImportError:
    py7zr = None
try:
    import rarfile
except ImportError:
    rarfile = None
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import webbrowser
from io import BytesIO
import sys

# ─── Configuración Global ────────────────────────────────────────────────────
CURRENT_VERSION = "1.3.0"
APP_NAME = "Chvstx Nexus"
REPO_URL = "https://github.com/DavidFR-2000/ChvstxNexux"
UPDATE_URL = "https://api.github.com/repos/DavidFR-2000/ChvstxNexux/releases/latest"

# Detectar modo portable
BASE_PATH = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
PORTABLE_FILE = os.path.join(BASE_PATH, "portable_mode.txt")
IS_PORTABLE = os.path.exists(PORTABLE_FILE)

if IS_PORTABLE:
    CONFIG_DIR = BASE_PATH
else:
    CONFIG_DIR = os.path.expanduser("~")

CONFIG_FILE   = os.path.join(CONFIG_DIR, ".chvstxnexus_config.json")
PLAYTIME_FILE = os.path.join(CONFIG_DIR, ".chvstxnexus_playtime.json")

# ─── Apariencia ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_dark":     "#000814",  # Azul noche profundo
    "bg_mid":      "#001d3d",  # Azul noche KH
    "bg_card":     "#003566",  # Azul KH
    "bg_hover":    "#1d3557",  # Azul suave hover
    "accent":      "#ffc300",  # Dorado Kingdom Hearts
    "accent2":     "#ffd60a",  # Dorado brillante
    "secondary":   "#e5e5e5",  # Plata KH
    "text_bright": "#ffffff",
    "text_dim":    "#adb5bd",
    "border":      "#001d3d",
    "green":       "#06d6a0",
    "yellow":      "#ffd166",
    "red":         "#ef476f",
    "glass":       "rgba(255, 255, 255, 0.1)",
}

CONSOLES = {
    "SNES":       {"emoji":"🎮","color":"#9b5de5","extensions":[".sfc",".smc",".zip"],         "emulator_key":"snes",     "rawg_platform":10},
    "GBA":        {"emoji":"🕹️","color":"#00b4d8","extensions":[".gba",".zip"],                "emulator_key":"gba",      "rawg_platform":24},
    "NDS":        {"emoji":"📟","color":"#4cc9f0","extensions":[".nds",".zip"],                 "emulator_key":"nds",      "rawg_platform":77},
    "N64":        {"emoji":"🟡","color":"#f9c74f","extensions":[".z64",".n64",".v64",".zip"],   "emulator_key":"n64",      "rawg_platform":83},
    "GameCube":   {"emoji":"🟣","color":"#c77dff","extensions":[".iso",".gcm",".rvz"],          "emulator_key":"gamecube", "rawg_platform":105},
    "Game Boy":   {"emoji":"🟩","color":"#80b918","extensions":[".gb",".zip"],                  "emulator_key":"gb",       "rawg_platform":26},
    "PS1":        {"emoji":"🎯","color":"#0066cc","extensions":[".bin",".cue",".iso",".img"],   "emulator_key":"ps1",      "rawg_platform":27},
    "PS2":        {"emoji":"⚡","color":"#4361ee","extensions":[".iso",".bin",".img"],           "emulator_key":"ps2",      "rawg_platform":15},
    "PSP":        {"emoji":"📱","color":"#48cae4","extensions":[".iso",".cso",".pbp"],           "emulator_key":"psp",      "rawg_platform":17},
    "Mega Drive": {"emoji":"🔥","color":"#f72585","extensions":[".md",".gen",".bin",".zip"],    "emulator_key":"megadrive","rawg_platform":167},
    "Saturn":     {"emoji":"🪐","color":"#ff9f1c","extensions":[".iso",".bin",".cue"],          "emulator_key":"saturn",   "rawg_platform":107},
}

RAWG_API_KEY  = "2db521236abd45be988b71c1015f1bc3"

# ─── RetroArch ───────────────────────────────────────────────────────────────
RA_CORES = {
    "SNES":       "snes9x_libretro.dll",
    "GBA":        "mgba_libretro.dll",
    "NDS":        "melonds_libretro.dll",
    "N64":        "mupen64plus_next_libretro.dll",
    "GameCube":   "dolphin_libretro.dll",
    "Game Boy":   "gambatte_libretro.dll",
    "PS1":        "duckstation_libretro.dll",
    "PS2":        "pcsx2_libretro.dll",
    "PSP":        "ppsspp_libretro.dll",
    "Mega Drive": "genesis_plus_gx_libretro.dll",
    "Saturn":     "mednafen_saturn_libretro.dll",
}

# ─── RetroAchievements API ───────────────────────────────────────────────────
RA_BASE    = "https://retroachievements.org/API"

RA_CONSOLE_IDS = {
    "SNES":       3,
    "GBA":        5,
    "NDS":        18,
    "N64":        2,
    "GameCube":   16,
    "Game Boy":   4,
    "PS1":        12,
    "PS2":        21,
    "PSP":        41,
    "Mega Drive": 1,
    "Saturn":     17,
}

def ra_search_game(game_name, console_name, ra_user="", ra_apikey=""):
    console_id = RA_CONSOLE_IDS.get(console_name)
    if not console_id or not ra_user or not ra_apikey:
        return None
    try:
        url = (f"{RA_BASE}/API_GetGameList.php"
               f"?z={ra_user}&y={ra_apikey}&i={console_id}&h=1")
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        games      = r.json()
        name_clean = sanitize_name(game_name).lower()
        best_id, best_score = None, 0
        for g in games:
            title_clean = sanitize_name(g.get("Title","")).lower()
            score = sum(1 for w in name_clean.split() if w in title_clean)
            if score > best_score:
                best_score = score
                best_id    = g.get("ID")
        return best_id if best_score > 0 else None
    except Exception:
        return None

def ra_get_achievements(ra_game_id, ra_user="", ra_apikey=""):
    if not ra_user or not ra_apikey:
        return None
    try:
        url = (f"{RA_BASE}/API_GetGameInfoAndUserProgress.php"
               f"?z={ra_user}&y={ra_apikey}&u={ra_user}&g={ra_game_id}")
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        data   = r.json()
        result = []
        for ach_id, a in data.get("Achievements", {}).items():
            result.append({
                "id":          ach_id,
                "title":       a.get("Title",""),
                "description": a.get("Description",""),
                "points":      a.get("Points", 0),
                "badge_url":   f"https://media.retroachievements.org/Badge/{a.get('BadgeName','')}.png",
                "unlocked":    a.get("DateEarned") is not None,
                "date_earned": a.get("DateEarned",""),
            })
        result.sort(key=lambda x: (not x["unlocked"], x["title"]))
        return result
    except Exception:
        return None

def ra_get_badge_image(badge_url, unlocked=True):
    try:
        if not unlocked:
            badge_url = badge_url.replace(".png", "_lock.png")
        r = requests.get(badge_url, timeout=6)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img.resize((48, 48), Image.LANCZOS)
    except Exception:
        pass
    return None
def load_config():
    default = {
        "roms_dir":       os.path.join(os.path.expanduser("~"), "ROMs"),
        "retroarch_path": r"C:\RetroArch-Win64\retroarch.exe",
        "cores_dir":      r"C:\RetroArch-Win64\cores",
        "covers_cache":   os.path.join(os.path.expanduser("~"), ".chvstxnexus_covers"),
        "favorites":      [],
        "ra_user":        "",
        "ra_apikey":      "",
        "first_run":      True,
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            for k, v in default.items():
                if k not in data:
                    data[k] = v
            return data
        except:
            pass
    return default

def check_branding_migration(cfg):
    """Fuerza el asistente de bienvenida si es la primera transición a Nexus."""
    if "nexus_first_run" not in cfg:
        cfg["nexus_first_run"] = True
        return True
    return cfg.get("first_run", True)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def load_playtime():
    if os.path.exists(PLAYTIME_FILE):
        try:
            with open(PLAYTIME_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_playtime(data):
    with open(PLAYTIME_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Portadas ─────────────────────────────────────────────────────────────────
def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def _create_desktop_shortcut(target_exe):
    """Crea un acceso directo en el escritorio usando PowerShell."""
    try:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
        icon_path = target_exe # Opcional: si el exe tiene icono
        
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

def get_cover_path(cache_dir, game_name):
    return os.path.join(cache_dir, f"{sanitize_name(game_name)}.jpg")

def download_cover(game_name, cache_dir, platform_id=None):
    cover_path = get_cover_path(cache_dir, game_name)
    if os.path.exists(cover_path):
        return cover_path
    os.makedirs(cache_dir, exist_ok=True)
    query   = sanitize_name(game_name)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

    # Fuente 1: RAWG API
    try:
        url = (f"https://api.rawg.io/api/games?search={requests.utils.quote(query)}"
               f"&key={RAWG_API_KEY}&page_size=5")
        if platform_id:
            url += f"&platforms={platform_id}"
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            for res in r.json().get("results", []):
                img_url = res.get("background_image")
                if img_url:
                    img_r = requests.get(img_url, headers=headers, timeout=8)
                    if img_r.status_code == 200:
                        img = Image.open(BytesIO(img_r.content)).convert("RGB")
                        img = img.resize((300, 200), Image.LANCZOS)
                        img.save(cover_path, "JPEG")
                        return cover_path
    except Exception:
        pass

    # Fuente 2: Bing Images
    try:
        q = requests.utils.quote(f"{query} game cover art")
        r = requests.get(f"https://www.bing.com/images/search?q={q}&first=1",
                         headers=headers, timeout=7)
        if r.status_code == 200:
            # Buscamos murl en los datos de imagen, manejando escape de comillas
            matches = re.findall(r'"murl":"(https?://[^"]+\.(?:jpg|jpeg|png))"', r.text)
            if not matches:
                # Intento 2 con comillas escapadas comunes en HTML
                matches = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png))&quot;', r.text)
            
            for img_url in matches[:10]:
                try:
                    img_r = requests.get(img_url, headers=headers, timeout=6)
                    if img_r.status_code == 200 and len(img_r.content) > 5000:
                        img = Image.open(BytesIO(img_r.content)).convert("RGB")
                        img = img.resize((300, 200), Image.LANCZOS)
                        img.save(cover_path, "JPEG")
                        return cover_path
                except Exception:
                    continue
    except Exception:
        pass

    return None

def fetch_game_info(game_name, platform_id=None):
    """Obtiene descripción, género, año y puntuación desde RAWG."""
    query   = sanitize_name(game_name)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = (f"https://api.rawg.io/api/games?search={requests.utils.quote(query)}"
               f"&key={RAWG_API_KEY}&page_size=1")
        if platform_id:
            url += f"&platforms={platform_id}"
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                g = results[0]
                desc = ""
                dr = requests.get(f"https://api.rawg.io/api/games/{g['id']}?key={RAWG_API_KEY}",
                                   headers=headers, timeout=6)
                if dr.status_code == 200:
                    raw = dr.json().get("description_raw", "")
                    desc = (raw[:400] + "...") if len(raw) > 400 else raw
                genres = ", ".join(ge["name"] for ge in g.get("genres", [])[:3])
                year   = g.get("released", "")[:4] if g.get("released") else "—"
                return {"desc": desc, "genres": genres, "year": year,
                        "rating": g.get("rating", 0), "name": g.get("name", game_name)}
    except Exception:
        pass
    return None

def make_placeholder(game_name, color, size=(300, 200)):
    img  = Image.new("RGB", size, "#0a0a0f")
    draw = ImageDraw.Draw(img)
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    for y in range(size[1]):
        a = 1 - y / size[1]
        draw.line([(0,y),(size[0],y)], fill=(int(r*a*0.5), int(g*a*0.5), int(b*a*0.5)))
    words = game_name.split()
    lines, cur = [], ""
    for w in words:
        if len(cur+" "+w) <= 18:
            cur = (cur+" "+w).strip()
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    y0 = size[1]//2 - len(lines)*14
    for line in lines:
        draw.text((size[0]//2 - len(line)*4, y0), line, fill=(240,236,227))
        y0 += 28
    return img

# ─── Aplicación ──────────────────────────────────────────────────────────────
class ChvstxNexus(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config          = load_config()
        self.playtime        = load_playtime()
        self._img_labels     = {}
        self.current_console = None
        self.current_view    = "library"
        self.games_list      = []
        self.update_url_exe  = None
        
        self.search_var      = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.filter_games())

        # Setup Window
        self.title(APP_NAME)
        self.geometry("1460x900")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_dark"])

        # Build UI and Load
        self._build_ui()
        self._select_console(list(CONSOLES.keys())[0])

        # Si es la primera vez (o primera vez en Nexus), mostrar el asistente
        if check_branding_migration(self.config):
            self.withdraw()  # Ocultar ventana principal
            self.after(200, self._show_welcome_wizard)
        
        # Buscar actualizaciones en segundo plano
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    # ════════ UI ════════════════════════════════════════════════════════
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=270, corner_radius=0,
                          fg_color=COLORS["bg_mid"],
                          border_width=1, border_color=COLORS["border"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkFrame(sb, fg_color="transparent")
        logo.grid(row=0, column=0, padx=20, pady=(28,4), sticky="ew")
        ctk.CTkLabel(logo, text="CHVSTX",    font=("Courier New",22,"bold"), text_color=COLORS["accent"]).pack(side="left")
        ctk.CTkLabel(logo, text=" NEXUS", font=("Courier New",22,"bold"), text_color=COLORS["text_bright"]).pack(side="left")

        ctk.CTkLabel(sb, text="— VISTAS —", font=("Courier New",9),
                     text_color=COLORS["text_dim"]).grid(row=1,column=0,padx=20,pady=(4,6),sticky="w")

        self.view_btns = {}
        for i,(label,key) in enumerate([("📚  Biblioteca","library"),("⭐  Favoritos","favorites"),("📊  Estadísticas","stats")]):
            b = ctk.CTkButton(sb, text=label, font=("Courier New",12,"bold"),
                              fg_color="transparent", hover_color=COLORS["bg_hover"],
                              text_color=COLORS["text_dim"], anchor="w", height=38, corner_radius=8,
                              command=lambda k=key: self._set_view(k))
            b.grid(row=2+i, column=0, padx=12, pady=2, sticky="ew")
            self.view_btns[key] = b

        ctk.CTkLabel(sb, text="— CONSOLAS —", font=("Courier New",9),
                     text_color=COLORS["text_dim"]).grid(row=6,column=0,padx=20,pady=(10,6),sticky="w")

        self.console_buttons = {}
        for i,(name,info) in enumerate(CONSOLES.items()):
            b = ctk.CTkButton(sb, text=f"  {info['emoji']}  {name}",
                              font=("Courier New",12,"bold"), fg_color="transparent",
                              hover_color=COLORS["bg_hover"], text_color=COLORS["text_dim"],
                              anchor="w", height=38, corner_radius=8,
                              command=lambda n=name: self._select_console(n))
            b.grid(row=7+i, column=0, padx=12, pady=2, sticky="ew")
            self.console_buttons[name] = b

        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).grid(
            row=7+len(CONSOLES), column=0, padx=12, pady=12, sticky="ew")

        ctk.CTkButton(sb, text="🌐  Descargas", font=("Courier New",12,"bold"),
                      fg_color=COLORS["accent"], hover_color=COLORS["accent2"],
                      text_color=COLORS["text_bright"], anchor="w",
                      command=self._open_homebrew_hub).grid(row=8+len(CONSOLES),column=0,padx=12,pady=(0,6),sticky="ew")

        ctk.CTkButton(sb, text="⚙  Configuración", font=("Courier New",12),
                      fg_color="transparent", hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_dim"], anchor="w",
                      command=self._open_settings).grid(row=9+len(CONSOLES),column=0,padx=12,pady=(0,20),sticky="ew")

    def _build_main(self):
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_mid"], corner_radius=0,
                           height=90, border_width=1, border_color=COLORS["border"])
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)
        inner.grid_columnconfigure(0, weight=1)

        self.console_title = ctk.CTkLabel(inner, text="", font=("Courier New",26,"bold"),
                                           text_color=COLORS["text_bright"])
        self.console_title.grid(row=0, column=0, padx=30, pady=(16,2), sticky="w")
        self.subtitle_label = ctk.CTkLabel(inner, text="", font=("Courier New",11),
                                            text_color=COLORS["text_dim"])
        self.subtitle_label.grid(row=1, column=0, padx=32, pady=(0,12), sticky="w")

        sf = ctk.CTkFrame(inner, fg_color="transparent")
        sf.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        self.search_entry = ctk.CTkEntry(sf,
            placeholder_text="🔍  Buscar juego...", textvariable=self.search_var,
            width=280, height=40, font=("Courier New",12),
            fg_color=COLORS["bg_card"], border_color=COLORS["border"], border_width=1,
            corner_radius=20, text_color=COLORS["text_bright"],
            placeholder_text_color=COLORS["text_dim"])
        self.search_entry.pack(side="left")

        self.update_btn = ctk.CTkButton(sf, text="⭐ Nueva versión", font=("Courier New",11,"bold"),
                                        fg_color=COLORS["green"], text_color=COLORS["bg_dark"],
                                        width=120, height=32, corner_radius=16,
                                        command=lambda: webbrowser.open(REPO_URL))
        # Se oculta por defecto

        # Status
        sb2 = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_mid"], height=30,
                            corner_radius=0, border_width=1, border_color=COLORS["border"])
        sb2.grid(row=1, column=0, sticky="ew")
        sb2.grid_propagate(False)
        self.status_label = ctk.CTkLabel(sb2, text="", font=("Courier New",10),
                                          text_color=COLORS["text_dim"])
        self.status_label.place(x=20, rely=0.5, anchor="w")

        # Content
        self.content = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.games_scroll = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"])
        self.games_scroll.grid(row=0, column=0, sticky="nsew")

        self.stats_frame = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"])

    def _check_for_updates(self):
        try:
            response = requests.get(UPDATE_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")
                if latest_version and latest_version != CURRENT_VERSION:
                    # Buscar el ejecutable en assets
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".exe"):
                            self.update_url_exe = asset.get("browser_download_url")
                            break
                    self.after(0, self._show_update_notification)
        except:
            pass

    def _show_update_notification(self):
        if hasattr(self, "update_btn"):
            self.update_btn.configure(text="🚀 Actualizar", command=self._start_auto_update)
            self.update_btn.pack(side="left", padx=(10,0))
            self._set_status(f"✨ ¡Nueva versión disponible!")

    def _start_auto_update(self):
        if not self.update_url_exe:
            messagebox.showinfo(APP_NAME, "No hay un archivo directo para actualizar. Visita el repositorio.")
            webbrowser.open(REPO_URL)
            return
        
        if messagebox.askyesno(APP_NAME, "¿Deseas descargar e instalar la nueva actualización ahora?"):
            self.update_btn.configure(state="disabled", text="Descargando...")
            threading.Thread(target=self._download_update_thread, daemon=True).start()

    def _download_update_thread(self):
        try:
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, "Nexus_Update.exe")
            
            self._set_status("Descargando actualización...")
            r = requests.get(self.update_url_exe, stream=True, timeout=30)
            if r.status_code == 200:
                with open(new_exe_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                self.after(0, lambda: self._apply_update_and_restart(new_exe_path))
            else:
                self.after(0, lambda: messagebox.showerror("Error", "No se pudo descargar el archivo."))
                self.after(0, lambda: self.update_btn.configure(state="normal", text="🚀 Reintentar"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Fallo en la descarga: {e}"))
            self.after(0, lambda: self.update_btn.configure(state="normal", text="🚀 Reintentar"))

    def _apply_update_and_restart(self, new_exe_path):
        current_exe = sys.executable if getattr(sys, 'frozen', False) else None
        
        if not current_exe:
            messagebox.showinfo(APP_NAME, "Actualización descargada. Ejecútala manualmente desde:\n" + new_exe_path)
            # Abrir carpeta del archivo
            subprocess.run(f'explorer /select,"{new_exe_path}"')
            return

        # Script Batch para el intercambio de archivos (más robusto)
        bat_path = os.path.join(tempfile.gettempdir(), "nexus_updater.bat")
        exe_name = os.path.basename(current_exe)
        with open(bat_path, "w") as f:
            f.write(f"@echo off\n")
            f.write(f"title Actualizando Chvstx Nexus...\n")
            f.write(f"echo Esperando a que la aplicacion se cierre...\n")
            f.write(f"timeout /t 3 /nobreak > nul\n")
            f.write(f"taskkill /f /im {exe_name} > nul 2>&1\n") # Asegurar cierre
            f.write(f":retry\n")
            f.write(f'move /y "{new_exe_path}" "{current_exe}"\n')
            f.write(f"if errorlevel 1 (\n")
            f.write(f"  echo El archivo esta bloqueado, reintentando en 1 segundo...\n")
            f.write(f"  timeout /t 1 /nobreak > nul\n")
            f.write(f"  goto retry\n")
            f.write(f")\n")
            f.write(f'start "" "{current_exe}"\n')
            f.write(f'del "%~f0"\n')

        self._set_status("Reiniciando para aplicar la nueva versión de Nexus...")
        subprocess.Popen([bat_path], shell=True)
        self.quit()
        sys.exit()

    # ════════ Vistas ════════════════════════════════════════════════════
    def _set_view(self, view):
        self.current_view = view
        for k, b in self.view_btns.items():
            if k == view:
                b.configure(fg_color=COLORS["bg_hover"], text_color=COLORS["accent"],
                            border_width=1, border_color=COLORS["accent"])
            else:
                b.configure(fg_color="transparent", text_color=COLORS["text_dim"], border_width=0)

        if view == "library":
            self.stats_frame.grid_remove()
            self.games_scroll.grid(row=0, column=0, sticky="nsew")
            self.search_entry.configure(state="normal")
            if self.current_console:
                self._select_console(self.current_console)
        elif view == "favorites":
            self.stats_frame.grid_remove()
            self.games_scroll.grid(row=0, column=0, sticky="nsew")
            self.search_entry.configure(state="normal")
            self._show_favorites()
        elif view == "stats":
            self.games_scroll.grid_remove()
            self.stats_frame.grid(row=0, column=0, sticky="nsew")
            self.search_entry.configure(state="disabled")
            self._show_stats()

    # ── Favoritos ─────────────────────────────────────────────────────
    def _show_favorites(self):
        self.console_title.configure(text="⭐  Favoritos", text_color=COLORS["yellow"])
        favs = self.config.get("favorites", [])
        self.subtitle_label.configure(text=f"{len(favs)} juego{'s' if len(favs)!=1 else ''} en favoritos")
        self._clear_scroll()
        if not favs:
            ctk.CTkLabel(self.games_scroll,
                text="No tienes favoritos aún.\nPulsa ★ en cualquier juego para añadirlo.",
                font=("Courier New",13), text_color=COLORS["text_dim"], justify="center"
            ).pack(expand=True, pady=80)
            return
        cols = 5
        self.games_scroll.grid_columnconfigure(tuple(range(cols)), weight=1)
        for i, entry in enumerate(favs):
            r, c = divmod(i, cols)
            card = self._make_game_card(entry["file"], entry["console"])
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        threading.Thread(target=self._load_covers_for_list,
                         args=([e["file"] for e in favs], [e["console"] for e in favs]),
                         daemon=True).start()

    # ── Estadísticas ─────────────────────────────────────────────────
    def _show_stats(self):
        self.console_title.configure(text="📊  Estadísticas", text_color=COLORS["green"])
        self.subtitle_label.configure(text="Resumen de tu actividad de juego")
        for w in self.stats_frame.winfo_children():
            w.destroy()

        if not self.playtime:
            ctk.CTkLabel(self.stats_frame,
                text="Aún no hay datos de tiempo de juego.\nJuega a algunos juegos primero.",
                font=("Courier New",13), text_color=COLORS["text_dim"], justify="center"
            ).pack(pady=80)
            return

        total_secs  = sum(v.get("total_secs",0) for v in self.playtime.values())
        total_h, rm = divmod(total_secs//60, 60)

        # Cards resumen
        summary = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        summary.pack(fill="x", padx=24, pady=(24,12))
        for label, value, color in [
            ("TIEMPO TOTAL",    f"{total_h}h {rm}m",           COLORS["accent"]),
            ("JUEGOS JUGADOS",  str(len(self.playtime)),        COLORS["green"]),
            ("FAVORITOS",       str(len(self.config.get("favorites",[]))), COLORS["yellow"]),
        ]:
            card = ctk.CTkFrame(summary, fg_color=COLORS["bg_card"], corner_radius=12,
                                border_width=1, border_color=COLORS["border"])
            card.pack(side="left", padx=8, ipadx=20, ipady=10, expand=True, fill="x")
            ctk.CTkLabel(card, text=value, font=("Courier New",28,"bold"), text_color=color).pack(pady=(14,2))
            ctk.CTkLabel(card, text=label, font=("Courier New",10), text_color=COLORS["text_dim"]).pack(pady=(0,14))

        ctk.CTkLabel(self.stats_frame, text="— TOP JUEGOS POR TIEMPO —",
                     font=("Courier New",11), text_color=COLORS["text_dim"]
        ).pack(padx=24, pady=(16,8), anchor="w")

        sorted_games = sorted(self.playtime.items(),
                              key=lambda x: x[1].get("total_secs",0), reverse=True)[:15]
        max_secs = max((v.get("total_secs",1) for _,v in sorted_games), default=1)

        for game_id, data in sorted_games:
            secs     = data.get("total_secs", 0)
            h, m     = divmod(secs//60, 60)
            sessions = data.get("sessions", 0)
            last     = data.get("last_played","")[:10] if data.get("last_played") else "—"
            console  = data.get("console","")
            color    = CONSOLES.get(console,{}).get("color", COLORS["accent"])

            row = ctk.CTkFrame(self.stats_frame, fg_color=COLORS["bg_card"], corner_radius=10,
                               border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", padx=24, pady=3)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=14, pady=10)

            nr = ctk.CTkFrame(left, fg_color="transparent")
            nr.pack(fill="x")
            ctk.CTkLabel(nr, text=data.get("name", game_id),
                         font=("Courier New",12,"bold"), text_color=COLORS["text_bright"]).pack(side="left")
            if console:
                ctk.CTkLabel(nr, text=f"  {CONSOLES.get(console,{}).get('emoji','')} {console}",
                             font=("Courier New",10), text_color=color).pack(side="left", padx=6)

            bar_bg = ctk.CTkFrame(left, height=6, fg_color=COLORS["bg_hover"], corner_radius=3)
            bar_bg.pack(fill="x", pady=(4,2))
            bar_fill = ctk.CTkFrame(bar_bg, height=6, fg_color=color, corner_radius=3)
            bar_fill.place(relx=0, rely=0, relwidth=secs/max_secs, relheight=1)

            ctk.CTkLabel(left,
                text=f"Última vez: {last}  ·  {sessions} sesión{'es' if sessions!=1 else ''}",
                font=("Courier New",9), text_color=COLORS["text_dim"]).pack(anchor="w")

            ctk.CTkLabel(row, text=f"{h}h {m:02d}m",
                         font=("Courier New",14,"bold"), text_color=color).pack(side="right", padx=20)

    # ════════ Consola ════════════════════════════════════════════════════
    def _select_console(self, name):
        self.current_console = name
        info = CONSOLES[name]
        self.current_view = "library"

        for n, b in self.console_buttons.items():
            if n == name:
                b.configure(fg_color=COLORS["bg_hover"], text_color=info["color"],
                            border_width=1, border_color=info["color"])
            else:
                b.configure(fg_color="transparent", text_color=COLORS["text_dim"], border_width=0)
        for b in self.view_btns.values():
            b.configure(fg_color="transparent", text_color=COLORS["text_dim"], border_width=0)

        self.stats_frame.grid_remove()
        self.games_scroll.grid(row=0, column=0, sticky="nsew")
        self.search_entry.configure(state="normal")
        self.console_title.configure(text=f"{info['emoji']}  {name}", text_color=info["color"])
        self.search_var.set("")
        self._load_games()

    def _load_games(self):
        if not self.current_console: return
        info        = CONSOLES[self.current_console]
        console_dir = os.path.join(self.config.get("roms_dir",""), self.current_console)
        self.games_list = []
        if os.path.isdir(console_dir):
            for f in sorted(os.listdir(console_dir)):
                if os.path.splitext(f)[1].lower() in info["extensions"]:
                    self.games_list.append(f)
        count = len(self.games_list)
        self.subtitle_label.configure(
            text=f"{count} juego{'s' if count!=1 else ''} encontrado{'s' if count!=1 else ''}")
        self.filter_games()

    def filter_games(self):
        if self.current_view != "library": return
        q        = self.search_var.get().lower()
        filtered = [g for g in self.games_list if q in g.lower()]
        self._render_games(filtered)

    def _clear_scroll(self):
        for w in self.games_scroll.winfo_children():
            w.destroy()
        self._img_labels = {}

    def _render_games(self, games):
        self._clear_scroll()
        if not games:
            ctk.CTkLabel(self.games_scroll,
                text="No se encontraron juegos.\n\nConfigura la carpeta de ROMs en ⚙ Configuración.",
                font=("Courier New",13), text_color=COLORS["text_dim"], justify="center"
            ).pack(expand=True, pady=80)
            return
        cols = 5
        self.games_scroll.grid_columnconfigure(tuple(range(cols)), weight=1)
        for i, gf in enumerate(games):
            r, c = divmod(i, cols)
            card = self._make_game_card(gf, self.current_console)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        threading.Thread(
            target=self._load_covers_for_list,
            args=(list(games), [self.current_console]*len(games)),
            daemon=True
        ).start()

    # ── Card ────────────────────────────────────────────────────────────
    def _make_game_card(self, game_file, console_name):
        info   = CONSOLES.get(console_name, list(CONSOLES.values())[0])
        name   = os.path.splitext(game_file)[0]
        is_fav = any(f["file"]==game_file and f["console"]==console_name
                     for f in self.config.get("favorites",[]))

        # Card container with glass-like effect
        card = ctk.CTkFrame(self.games_scroll, fg_color=COLORS["bg_card"], corner_radius=15,
                            border_width=2, border_color=COLORS["border"], cursor="hand2")

        img_label = ctk.CTkLabel(card, text="", height=160)
        img_label.pack(fill="x", padx=2, pady=2)
        img_label._game_file = game_file
        self._img_labels[game_file] = img_label
        
        ph    = make_placeholder(name, info["color"], (260,160))
        ph_tk = ctk.CTkImage(ph, size=(260,160))
        img_label.configure(image=ph_tk)
        img_label.image = ph_tk

        # Content area
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=(8,12))

        name_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        name_row.pack(fill="x")
        
        name_label = ctk.CTkLabel(name_row, text=name.upper(), font=("Helvetica",11,"bold"),
                                   text_color=COLORS["text_bright"], wraplength=180,
                                   justify="left", anchor="w")
        name_label.pack(side="left", fill="x", expand=True)

        fav_btn = ctk.CTkButton(name_row,
            text=("❤" if is_fav else "♡"), width=28, height=28,
            font=("Helvetica",16), fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=(COLORS["red"] if is_fav else COLORS["text_dim"]),
            command=lambda gf=game_file, cn=console_name: self._toggle_favorite(gf, cn))
        fav_btn.pack(side="right")

        game_id = f"{console_name}::{game_file}"
        secs    = self.playtime.get(game_id,{}).get("total_secs",0)
        h, m    = divmod(secs//60, 60)
        pt_text = (f"⌛ {h}h {m:02d}m" if secs > 0 else "⌛ NEW")

        bottom = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom.pack(fill="x", pady=(4,0))
        
        # Badge-like console indicator
        console_badge = ctk.CTkFrame(bottom, fg_color=info["color"], corner_radius=10, height=18)
        console_badge.pack(side="left")
        ctk.CTkLabel(console_badge, text=f" {info['emoji']} {console_name} ",
                     font=("Helvetica",9,"bold"), text_color="#ffffff").pack(padx=6)
        
        ctk.CTkLabel(bottom, text=pt_text,
                     font=("Helvetica",10), text_color=COLORS["accent"]).pack(side="right")

        def on_enter(e):
            card.configure(border_color=COLORS["accent"], fg_color=COLORS["bg_hover"])
            name_label.configure(text_color=COLORS["accent"])
        def on_leave(e):
            card.configure(border_color=COLORS["border"], fg_color=COLORS["bg_card"])
            name_label.configure(text_color=COLORS["text_bright"])
        def on_click(e, gf=game_file, cn=console_name): self._open_game_detail(gf, cn)

        for w in [card, img_label, name_label, bottom, content_frame, name_row]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return card

    # ════════ Detalle de juego ═══════════════════════════════════════════
    def _open_game_detail(self, game_file, console_name):
        win = ctk.CTkToplevel(self)
        win.title(os.path.splitext(game_file)[0])
        win.geometry("700x530")
        win.configure(fg_color=COLORS["bg_dark"])
        win.grab_set()

        info = CONSOLES.get(console_name, list(CONSOLES.values())[0])
        name = os.path.splitext(game_file)[0]

        left = ctk.CTkFrame(win, fg_color="transparent", width=280)
        left.pack(side="left", fill="y", padx=20, pady=20)
        left.pack_propagate(False)
        right = ctk.CTkFrame(win, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(0,20), pady=20)

        # Portada
        cache_dir  = self.config.get("covers_cache","")
        cover_path = get_cover_path(cache_dir, name)
        try:
            img = Image.open(cover_path).resize((260,180), Image.LANCZOS) if os.path.exists(cover_path) \
                  else make_placeholder(name, info["color"], (260,180))
        except:
            img = make_placeholder(name, info["color"], (260,180))
        tk_img = ctk.CTkImage(img, size=(260,180))
        lbl = ctk.CTkLabel(left, image=tk_img, text="")
        lbl.pack()
        lbl.image = tk_img

        ctk.CTkLabel(left, text=f"{info['emoji']} {console_name}",
                     font=("Courier New",12,"bold"), text_color=info["color"]).pack(pady=(10,2))

        game_id  = f"{console_name}::{game_file}"
        pt       = self.playtime.get(game_id,{})
        secs     = pt.get("total_secs",0)
        h, m     = divmod(secs//60, 60)
        sessions = pt.get("sessions",0)
        ctk.CTkLabel(left, text=f"⏱  {h}h {m:02d}m jugados",
                     font=("Courier New",11), text_color=COLORS["text_dim"]).pack(pady=2)
        ctk.CTkLabel(left, text=f"🎮  {sessions} sesión{'es' if sessions!=1 else ''}",
                     font=("Courier New",11), text_color=COLORS["text_dim"]).pack(pady=2)

        # Favorito
        is_fav = any(f["file"]==game_file and f["console"]==console_name
                     for f in self.config.get("favorites",[]))
        def toggle_fav():
            self._toggle_favorite(game_file, console_name)
            nf = any(f["file"]==game_file and f["console"]==console_name
                     for f in self.config.get("favorites",[]))
            fav_b.configure(text="★ En favoritos" if nf else "☆ Añadir a favoritos",
                            text_color=COLORS["yellow"] if nf else COLORS["text_dim"])
        fav_b = ctk.CTkButton(left,
            text="★ En favoritos" if is_fav else "☆ Añadir a favoritos",
            font=("Courier New",11), fg_color="transparent",
            hover_color=COLORS["bg_hover"], border_width=1, border_color=COLORS["border"],
            text_color=COLORS["yellow"] if is_fav else COLORS["text_dim"],
            command=toggle_fav)
        fav_b.pack(pady=(10,0), fill="x")

        # Derecha
        ctk.CTkLabel(right, text=name, font=("Courier New",18,"bold"),
                     text_color=COLORS["text_bright"], wraplength=380, justify="left").pack(anchor="w")

        info_frame = ctk.CTkFrame(right, fg_color=COLORS["bg_card"], corner_radius=10,
                                   border_width=1, border_color=COLORS["border"])
        info_frame.pack(fill="x", pady=10)
        loading = ctk.CTkLabel(info_frame, text="Cargando información...",
                               font=("Courier New",11), text_color=COLORS["text_dim"])
        loading.pack(pady=20)

        def load_info():
            data = fetch_game_info(name, info.get("rawg_platform"))
            def update():
                if not win.winfo_exists(): return
                loading.destroy()
                if data:
                    for lbl_text, val, col in [
                        ("AÑO",       data["year"],                                          COLORS["text_bright"]),
                        ("GÉNEROS",   data["genres"] or "—",                                 COLORS["text_bright"]),
                        ("RATING",    f"{'⭐'*int(round(data['rating']))} ({data['rating']:.1f}/5)" if data["rating"] else "—", COLORS["yellow"]),
                    ]:
                        rr = ctk.CTkFrame(info_frame, fg_color="transparent")
                        rr.pack(fill="x", padx=14, pady=3)
                        ctk.CTkLabel(rr, text=lbl_text, font=("Courier New",9),
                                     text_color=COLORS["text_dim"], width=80, anchor="w").pack(side="left")
                        ctk.CTkLabel(rr, text=val, font=("Courier New",11),
                                     text_color=col, anchor="w").pack(side="left")
                    if data["desc"]:
                        ctk.CTkLabel(info_frame, text=data["desc"], font=("Courier New",10),
                                     text_color=COLORS["text_dim"], wraplength=360, justify="left"
                        ).pack(padx=14, pady=(4,14))
                else:
                    ctk.CTkLabel(info_frame, text="No se encontró información en línea.",
                                 font=("Courier New",11), text_color=COLORS["text_dim"]).pack(pady=14)
            win.after(0, update)
        threading.Thread(target=load_info, daemon=True).start()

        def launch():
            win.destroy()
            self._launch_game(game_file, console_name)
        ctk.CTkButton(right, text="▶  JUGAR AHORA", font=("Courier New",14,"bold"),
                      fg_color=COLORS["accent"], hover_color=COLORS["accent2"],
                      height=46, command=launch).pack(fill="x", pady=(8,0))

        def rename():
            new_name = ctk.CTkInputDialog(
                text="Nuevo nombre (sin extensión):", title="Renombrar").get_input()
            if not new_name or not new_name.strip(): return
            ext      = os.path.splitext(game_file)[1]
            old_path = os.path.join(self.config.get("roms_dir",""), console_name, game_file)
            new_path = os.path.join(self.config.get("roms_dir",""), console_name, new_name.strip()+ext)
            try:
                os.rename(old_path, new_path)
                win.destroy()
                self._load_games()
                self._set_status(f"✓  Renombrado a {new_name.strip()+ext}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ctk.CTkButton(right, text="✏  Renombrar", font=("Courier New",11),
                      fg_color="transparent", hover_color=COLORS["bg_hover"],
                      border_width=1, border_color=COLORS["border"],
                      text_color=COLORS["text_dim"], command=rename).pack(fill="x", pady=(6,0))

        ctk.CTkButton(right, text="🏆  Ver logros (RetroAchievements)",
                      font=("Courier New",11),
                      fg_color="transparent", hover_color=COLORS["bg_hover"],
                      border_width=1, border_color=COLORS["yellow"],
                      text_color=COLORS["yellow"],
                      command=lambda: self._open_achievements(game_file, console_name)
        ).pack(fill="x", pady=(6,0))

    # ════════ RetroAchievements ══════════════════════════════════════════
    def _open_achievements(self, game_file, console_name):
        name = os.path.splitext(game_file)[0]

        win = ctk.CTkToplevel(self)
        win.title(f"🏆 Logros — {name}")
        win.geometry("660x700")
        win.configure(fg_color=COLORS["bg_dark"])
        win.grab_set()

        # Header
        hdr = ctk.CTkFrame(win, fg_color=COLORS["bg_mid"], corner_radius=0,
                           border_width=1, border_color=COLORS["border"])
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🏆  RetroAchievements",
                     font=("Courier New",18,"bold"), text_color=COLORS["yellow"]
        ).pack(side="left", padx=20, pady=14)
        ra_user_cfg = self.config.get("ra_user", "")
        ctk.CTkLabel(hdr, text=f"👤 {ra_user_cfg or 'Sin configurar'}",
                     font=("Courier New",11), text_color=COLORS["text_dim"]
        ).pack(side="right", padx=20)

        ctk.CTkLabel(win, text=name, font=("Courier New",12),
                     text_color=COLORS["text_dim"]).pack(pady=(8,4))

        # Resumen (se rellena al cargar)
        summary_frame = ctk.CTkFrame(win, fg_color=COLORS["bg_card"], corner_radius=10,
                                      border_width=1, border_color=COLORS["border"])
        summary_frame.pack(fill="x", padx=16, pady=(0,8))
        summary_lbl = ctk.CTkLabel(summary_frame,
                                    text="Buscando juego en RetroAchievements...",
                                    font=("Courier New",11), text_color=COLORS["text_dim"])
        summary_lbl.pack(pady=12)

        # Scroll
        scroll = ctk.CTkScrollableFrame(win, fg_color=COLORS["bg_dark"],
                                         scrollbar_button_color=COLORS["border"],
                                         scrollbar_button_hover_color=COLORS["yellow"])
        scroll.pack(fill="both", expand=True, padx=16, pady=(0,8))

        loading_lbl = ctk.CTkLabel(scroll, text="⏳  Conectando con RetroAchievements...",
                                    font=("Courier New",12), text_color=COLORS["text_dim"])
        loading_lbl.pack(pady=40)

        def load_data():
            ra_user   = self.config.get("ra_user", "")
            ra_apikey = self.config.get("ra_apikey", "")
            if not ra_user or not ra_apikey:
                win.after(0, _show_not_configured)
                return
            ra_id = ra_search_game(name, console_name, ra_user, ra_apikey)
            if not ra_id:
                win.after(0, _show_not_found)
                return
            achievements = ra_get_achievements(ra_id, ra_user, ra_apikey)
            if achievements is None:
                win.after(0, _show_error)
                return
            win.after(0, lambda: _render(achievements))

        def _show_not_configured():
            if not win.winfo_exists(): return
            loading_lbl.configure(
                text="⚙️  No has configurado tu cuenta de RetroAchievements.\n\n"
                     "Ve a  ⚙ Configuración  e introduce tu usuario y API Key.",
                justify="center", text_color=COLORS["yellow"])
            summary_lbl.configure(text="Cuenta no configurada")

        def _show_not_found():
            if not win.winfo_exists(): return
            loading_lbl.configure(
                text=f"❌  No se encontró '{name}' en RetroAchievements.\n\n"
                     f"Puede que el juego no tenga logros o que el nombre no coincida.",
                justify="center")
            summary_lbl.configure(text="Juego no encontrado")

        def _show_error():
            if not win.winfo_exists(): return
            loading_lbl.configure(
                text="❌  Error conectando con RetroAchievements.\nComprueba tu conexión.")
            summary_lbl.configure(text="Error de conexión")

        def _render(achievements):
            if not win.winfo_exists(): return
            loading_lbl.destroy()

            total         = len(achievements)
            unlocked      = sum(1 for a in achievements if a["unlocked"])
            points_earned = sum(a["points"] for a in achievements if a["unlocked"])
            points_total  = sum(a["points"] for a in achievements)
            pct           = int(unlocked / total * 100) if total else 0

            # Rellenar resumen
            for w in summary_frame.winfo_children(): w.destroy()
            cols_f = ctk.CTkFrame(summary_frame, fg_color="transparent")
            cols_f.pack(fill="x", padx=16, pady=10)
            for label, value, color in [
                ("LOGROS",      f"{unlocked}/{total}",          COLORS["yellow"]),
                ("PUNTOS",      f"{points_earned}/{points_total}", COLORS["green"]),
                ("COMPLETADO",  f"{pct}%",                      COLORS["accent"]),
            ]:
                c = ctk.CTkFrame(cols_f, fg_color="transparent")
                c.pack(side="left", expand=True)
                ctk.CTkLabel(c, text=value, font=("Courier New",20,"bold"),
                             text_color=color).pack()
                ctk.CTkLabel(c, text=label, font=("Courier New",9),
                             text_color=COLORS["text_dim"]).pack()

            bar_bg = ctk.CTkFrame(summary_frame, height=8,
                                   fg_color=COLORS["bg_hover"], corner_radius=4)
            bar_bg.pack(fill="x", padx=16, pady=(0,10))
            if pct > 0:
                ctk.CTkFrame(bar_bg, height=8, fg_color=COLORS["yellow"], corner_radius=4
                ).place(relx=0, rely=0, relwidth=pct/100, relheight=1)

            # Listas
            unlocked_list = [a for a in achievements if a["unlocked"]]
            locked_list   = [a for a in achievements if not a["unlocked"]]

            if unlocked_list:
                ctk.CTkLabel(scroll, text=f"— DESBLOQUEADOS ({len(unlocked_list)}) —",
                             font=("Courier New",9), text_color=COLORS["green"]
                ).pack(anchor="w", padx=8, pady=(8,4))
                for a in unlocked_list:
                    _make_row(a)
            if locked_list:
                ctk.CTkLabel(scroll, text=f"— BLOQUEADOS ({len(locked_list)}) —",
                             font=("Courier New",9), text_color=COLORS["text_dim"]
                ).pack(anchor="w", padx=8, pady=(12,4))
                for a in locked_list:
                    _make_row(a)

        def _make_row(a):
            row = ctk.CTkFrame(scroll,
                fg_color=COLORS["bg_card"] if a["unlocked"] else COLORS["bg_mid"],
                corner_radius=10, border_width=1,
                border_color=COLORS["yellow"] if a["unlocked"] else COLORS["border"])
            row.pack(fill="x", pady=3, padx=4)

            # Badge
            badge_frame = ctk.CTkFrame(row, width=60, height=60,
                                        fg_color=COLORS["bg_hover"], corner_radius=8)
            badge_frame.pack(side="left", padx=10, pady=8)
            badge_frame.pack_propagate(False)
            badge_lbl = ctk.CTkLabel(badge_frame,
                text="🔒" if not a["unlocked"] else "⏳", font=("Courier New",22))
            badge_lbl.place(relx=0.5, rely=0.5, anchor="center")

            def load_badge(url=a["badge_url"], unlocked=a["unlocked"],
                           lbl=badge_lbl, frm=badge_frame):
                img = ra_get_badge_image(url, unlocked)
                if img and frm.winfo_exists():
                    tk_img = ctk.CTkImage(img, size=(48,48))
                    frm.after(0, lambda i=tk_img: (
                        lbl.configure(image=i, text=""),
                        setattr(lbl, "image", i)))
            threading.Thread(target=load_badge, daemon=True).start()

            # Texto
            txt = ctk.CTkFrame(row, fg_color="transparent")
            txt.pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(txt, text=a["title"], font=("Courier New",12,"bold"),
                         text_color=COLORS["yellow"] if a["unlocked"] else COLORS["text_bright"],
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(txt, text=a["description"], font=("Courier New",10),
                         text_color=COLORS["text_dim"], anchor="w", wraplength=380
            ).pack(anchor="w")
            if a["unlocked"] and a["date_earned"]:
                ctk.CTkLabel(txt, text=f"✓ Desbloqueado el {a['date_earned'][:10]}",
                             font=("Courier New",9), text_color=COLORS["green"]
                ).pack(anchor="w", pady=(2,0))

            # Puntos
            ctk.CTkLabel(row, text=f"{a['points']}p",
                         font=("Courier New",11,"bold"),
                         text_color=COLORS["yellow"] if a["unlocked"] else COLORS["text_dim"]
            ).pack(side="right", padx=14)

        # Botón refrescar
        def do_refresh():
            for w in scroll.winfo_children(): w.destroy()
            ctk.CTkLabel(scroll, text="⏳  Actualizando...",
                font=("Courier New",12), text_color=COLORS["text_dim"]).pack(pady=40)
            threading.Thread(target=load_data, daemon=True).start()

        ctk.CTkButton(win, text="🔄  Actualizar desde RetroAchievements",
                      font=("Courier New",10), fg_color="transparent",
                      hover_color=COLORS["bg_hover"], border_width=1,
                      border_color=COLORS["border"], text_color=COLORS["text_dim"],
                      command=do_refresh).pack(pady=(0,12))

        threading.Thread(target=load_data, daemon=True).start()
    def _toggle_favorite(self, game_file, console_name):
        favs   = self.config.setdefault("favorites", [])
        exists = any(f["file"]==game_file and f["console"]==console_name for f in favs)
        if exists:
            self.config["favorites"] = [
                f for f in favs
                if not (f["file"]==game_file and f["console"]==console_name)]
            self._set_status(f"Eliminado de favoritos: {os.path.splitext(game_file)[0]}")
        else:
            favs.append({"file": game_file, "console": console_name})
            self._set_status(f"★  Añadido a favoritos: {os.path.splitext(game_file)[0]}")
        save_config(self.config)
        if self.current_view == "library":
            self.filter_games()
        elif self.current_view == "favorites":
            self._show_favorites()

    # ════════ Lanzar + tiempo jugado ════════════════════════════════════
    def _launch_game(self, game_file, console_name=None):
        cn = console_name or self.current_console

        retroarch = self.config.get("retroarch_path", "")
        cores_dir = self.config.get("cores_dir", "")

        if not retroarch or not os.path.exists(retroarch):
            messagebox.showwarning("RetroArch no encontrado",
                f"No se encontró retroarch.exe.\nVe a ⚙ Configuración y verifica la ruta.")
            return

        core_file = RA_CORES.get(cn)
        if not core_file:
            messagebox.showerror("Core no definido",
                f"No hay core configurado para {cn}.")
            return

        core_path = os.path.join(cores_dir, core_file)
        if not os.path.exists(core_path):
            messagebox.showwarning("Core no instalado",
                f"El core para {cn} no está instalado:\n{core_file}\n\n"
                f"Descárgalo desde RetroArch:\n"
                f"Menú principal → Gestión de cores → {cn}")
            return

        rom_path = os.path.join(self.config.get("roms_dir",""), cn, game_file)
        if not os.path.exists(rom_path):
            messagebox.showerror("Error", f"Archivo no encontrado:\n{rom_path}")
            return

        name       = os.path.splitext(game_file)[0]
        game_id    = f"{cn}::{game_file}"
        start_time = time.time()
        self._set_status(f"▶  Lanzando {name} con RetroArch ({core_file})...")

        def monitor(proc):
            proc.wait()
            elapsed = int(time.time() - start_time)
            entry   = self.playtime.setdefault(game_id, {"total_secs":0,"sessions":0})
            entry["total_secs"]  += elapsed
            entry["sessions"]    += 1
            entry["last_played"]  = datetime.datetime.now().isoformat()
            entry["console"]      = cn
            entry["name"]         = name
            save_playtime(self.playtime)
            h, m = divmod(elapsed//60, 60)
            self.after(0, lambda: self._set_status(
                f"✓  Sesión terminada: {name} ({h}h {m:02d}m)"))

        try:
            proc = subprocess.Popen([retroarch, "-L", core_path, rom_path])
            threading.Thread(target=monitor, args=(proc,), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error al lanzar RetroArch", str(e))

    # ════════ Portadas ═══════════════════════════════════════════════════
    def _load_covers_for_list(self, game_files, consoles):
        cache_dir = self.config.get("covers_cache","")
        os.makedirs(cache_dir, exist_ok=True)
        snapshot_console = self.current_console

        for game_file, cn in zip(game_files, consoles):
            if self.current_console != snapshot_console: break
            name        = os.path.splitext(game_file)[0]
            cover_path  = get_cover_path(cache_dir, name)
            platform_id = CONSOLES.get(cn,{}).get("rawg_platform")
            if not os.path.exists(cover_path):
                self._set_status(f"Descargando portada: {name}...")
                result = download_cover(name, cache_dir, platform_id)
            else:
                result = cover_path
            if result and os.path.exists(result):
                try:
                    img = Image.open(result).resize((260,150), Image.LANCZOS)
                    self.after(0, lambda gf=game_file, i=img: self._update_cover(gf, i))
                except:
                    pass
        self.after(0, lambda: self._set_status(""))

    def _update_cover(self, game_file, img):
        label = self._img_labels.get(game_file)
        if label:
            try:
                if label.winfo_exists():
                    tk_img = ctk.CTkImage(img, size=(260,150))
                    label.configure(image=tk_img)
                    label.image = tk_img
            except:
                pass

    def _set_status(self, text):
        self.status_label.configure(text=text)

    # ════════ Descargas (Online Hub) ════════════════════════════════════
    def _open_homebrew_hub(self):
        win = ctk.CTkToplevel(self)
        win.title("🌐 Hub de Descargas Online")
        win.geometry("920x700")
        win.configure(fg_color=COLORS["bg_dark"])
        win.grab_set()

        # ── Fuentes verificadas ──────────────────────────────────────────
        # Los repos tienen carpetas entries/<slug>/game.json + archivos ROM
        # Los archivos se sirven directamente desde hh3.gbdev.io/entries/
        HB_REPOS = {
            "Retrostic (Todas las consolas)": {
                "type": "retrostic"
            },
            "Homebrew (Game Boy)": {
                "type": "github",
                "api":  "https://api.github.com/repos/gbdev/database/contents/entries",
                "raw":  "https://raw.githubusercontent.com/gbdev/database/master/entries",
                "cdn":  "https://hh3.gbdev.io/entries",  # servidor que sirve los archivos
            },
            "Homebrew (GBA)": {
                "type": "github",
                "api":  "https://api.github.com/repos/gbadev-org/games/contents/entries",
                "raw":  "https://raw.githubusercontent.com/gbadev-org/games/main/entries",
                "cdn":  "https://hh3.gbdev.io/entries",
            },
        }
        VALID_EXTS = (".gb", ".gbc", ".gba", ".nes", ".zip", ".smc", ".sfc", ".nds", ".7z", ".rar", ".bin")

        # ── Header ──────────────────────────────────────────────────────
        ctk.CTkLabel(win, text="🌐  DESCARGAS (ONLINE)", font=("Courier New",20,"bold"),
                     text_color=COLORS["accent"]).pack(pady=(20,2))
        ctk.CTkLabel(win, text="Busca y descarga ROMs desde varias fuentes",
                     font=("Courier New",11), text_color=COLORS["text_dim"]).pack(pady=(0,14))

        # ── Controles ───────────────────────────────────────────────────
        top = ctk.CTkFrame(win, fg_color=COLORS["bg_mid"],
                           border_width=1, border_color=COLORS["border"], corner_radius=10)
        top.pack(fill="x", padx=20, pady=(0,10))
        row1 = ctk.CTkFrame(top, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(14,6))

        ctk.CTkLabel(row1, text="Fuente:", font=("Courier New",11),
                     text_color=COLORS["text_dim"], width=70, anchor="w").pack(side="left")
        default_con = "Retrostic (Todas las consolas)"
        console_var = tk.StringVar(value=default_con)
        ctk.CTkOptionMenu(row1, variable=console_var, values=list(HB_REPOS.keys()),
                          font=("Courier New",11), fg_color=COLORS["bg_card"],
                          button_color=COLORS["accent"], button_hover_color=COLORS["accent2"],
                          dropdown_fg_color=COLORS["bg_card"],
                          text_color=COLORS["text_bright"], width=160
        ).pack(side="left", padx=(0,20))

        search_var = tk.StringVar()
        ctk.CTkLabel(row1, text="Buscar:", font=("Courier New",11),
                     text_color=COLORS["text_dim"], width=60, anchor="w").pack(side="left")
        ctk.CTkEntry(row1, textvariable=search_var, width=250, font=("Courier New",11),
                     fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                     text_color=COLORS["text_bright"],
                     placeholder_text="nombre del juego...").pack(side="left", padx=(0,10))

        status_lbl = ctk.CTkLabel(top, text="", font=("Courier New",10),
                                   text_color=COLORS["text_dim"])
        status_lbl.pack(anchor="w", padx=16, pady=(0,10))

        # ── Lista ────────────────────────────────────────────────────────
        list_frame = ctk.CTkScrollableFrame(win, fg_color=COLORS["bg_mid"],
                                             scrollbar_button_color=COLORS["border"],
                                             scrollbar_button_hover_color=COLORS["accent"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0,12))
        list_frame.grid_columnconfigure(0, weight=1)

        def set_status(txt, color=None):
            win.after(0, lambda: status_lbl.configure(
                text=txt, text_color=color or COLORS["text_dim"]))

        def clear_list():
            for w in list_frame.winfo_children():
                w.destroy()

        def fetch_games():
            win.after(0, clear_list)
            console = console_var.get()
            query   = search_var.get().strip().lower()
            repo    = HB_REPOS[console]
            headers = {"User-Agent": f"{APP_NAME}/1.0",
                       "Accept": "application/vnd.github+json"}

            set_status(f"⏳ Buscando en {console}...")

            try:
                if repo.get("type") == "retrostic":
                    if not query:
                        set_status("Por favor, escribe un nombre para buscar en Retrostic.", COLORS["yellow"])
                        return
                    
                    url = f"https://www.retrostic.com/search?search_term_string={requests.utils.quote(query)}"
                    r = requests.get(url, headers=headers, timeout=15)
                    r.raise_for_status()
                    
                    soup = BeautifulSoup(r.text, 'html.parser')
                    nodes = soup.find_all('a', href=lambda href: href and '/roms/' in href)
                    
                    games = []
                    seen_urls = set()
                    for node in nodes:
                        href = node['href']
                        if href == '/roms/mame' or href == '/roms/snes' or href == '/roms/ps-1' or href == '/roms/nds': continue # ignore console links
                        if href in seen_urls: continue
                        
                        text = node.text.strip()
                        if not text: continue
                        
                        seen_urls.add(href)
                        slug = href.split('/')[-1]
                        games.append({
                            "_slug": slug,
                            "_repo": repo,
                            "title": text,
                            "author": "Retrostic",
                            "description": "Juego encontrado en Retrostic. Listo para descargar.",
                            "tags": [href.split('/')[2].upper() if len(href.split('/')) > 2 else ""],
                            "files": [{"url": f"https://www.retrostic.com{href}"}]
                        })
                    
                    if not games:
                        win.after(0, lambda: ctk.CTkLabel(list_frame,
                            text=f"No se encontraron resultados para '{query}' en Retrostic.",
                            font=("Courier New",12), text_color=COLORS["text_dim"]
                        ).pack(pady=40))
                        set_status("Sin resultados en Retrostic.")
                        return

                else:
                    # Paso 1: listar carpetas de entries via GitHub API
                    r = requests.get(repo["api"], headers=headers, timeout=15)
                    r.raise_for_status()
                    entries = [e for e in r.json() if e["type"] == "dir"]

                    # Filtrar por búsqueda sobre el slug/nombre de carpeta
                    if query:
                        entries = [e for e in entries if query in e["name"].lower()]

                    entries = entries[:60]
                    total = len(entries)

                    if not total:
                        win.after(0, lambda: ctk.CTkLabel(list_frame,
                            text=f"No se encontraron juegos para '{query}'.",
                            font=("Courier New",12), text_color=COLORS["text_dim"]
                        ).pack(pady=40))
                        set_status("Sin resultados.")
                        return

                    set_status(f"⏳ Descargando metadatos de {total} juegos...")
                    games = []
                    for i, entry in enumerate(entries):
                        slug     = entry["name"]
                        json_url = f"{repo['raw']}/{slug}/game.json"
                        try:
                            jr = requests.get(json_url, headers=headers, timeout=8)
                            if jr.status_code == 200:
                                gdata = jr.json()
                                gdata["_slug"] = slug
                                gdata["_repo"] = repo
                                games.append(gdata)
                        except Exception:
                            pass
                        if i % 10 == 0:
                            set_status(f"⏳ Cargando {i+1}/{total}...")

                set_status(f"✓  {len(games)} juegos cargados", COLORS["green"])
                win.after(0, lambda g=games: _render(g))

            except Exception as e:
                set_status(f"✗ Error: {e}", COLORS["red"])

        def _render(games):
            clear_list()
            for idx, game in enumerate(games):
                slug   = game.get("_slug", "")
                repo   = game.get("_repo", {})
                title  = game.get("title", slug)
                a      = game.get("author", {})
                author = a.get("name", str(a)) if isinstance(a, dict) else str(a)
                desc   = (game.get("description","") or "")[:110]
                tags   = ", ".join(game.get("tags", [])[:4])

                # Buscar ROM en files[]
                dl_url = None
                if repo.get("type") == "retrostic":
                    dl_url = game.get("files", [{}])[0].get("url")
                else:
                    for f in game.get("files", []):
                        fname = f.get("filename","") or f.get("url","")
                        if not fname:
                            continue
                        if fname.startswith("http"):
                            dl_url = fname
                            break
                        elif any(fname.lower().endswith(e) for e in VALID_EXTS):
                            # Intentar primero CDN, fallback a raw GitHub
                            dl_url = f"{repo.get('cdn','')}/{slug}/{fname}"
                            break

                card = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_card"], corner_radius=10,
                                    border_width=1, border_color=COLORS["border"])
                card.grid(row=idx, column=0, padx=6, pady=4, sticky="ew")
                card.grid_columnconfigure(0, weight=1)

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.grid(row=0, column=0, padx=14, pady=10, sticky="ew")
                ctk.CTkLabel(info, text=title, font=("Courier New",12,"bold"),
                             text_color=COLORS["text_bright"], anchor="w").pack(anchor="w")
                ctk.CTkLabel(info, text=f"👤 {author}   🏷 {tags or '—'}",
                             font=("Courier New",9), text_color=COLORS["accent2"]).pack(anchor="w")
                if desc:
                    ctk.CTkLabel(info, text=desc, font=("Courier New",9),
                                 text_color=COLORS["text_dim"], wraplength=560,
                                 justify="left").pack(anchor="w", pady=(2,0))

                btn_col = ctk.CTkFrame(card, fg_color="transparent")
                btn_col.grid(row=0, column=1, padx=12, pady=10)

                console_name = console_var.get()
                if dl_url:
                    # En Retrostic le pasamos el console para intentar deducirlo
                    cns = console_name
                    if repo.get("type") == "retrostic" and tags:
                        cns = tags
                    
                    ctk.CTkButton(btn_col, text="⬇ Descargar",
                                  font=("Courier New",11,"bold"),
                                  fg_color=COLORS["accent"], hover_color=COLORS["accent2"],
                                  width=130, height=34,
                                  command=lambda u=dl_url, t=title, c=cns, s=slug, rp=repo:
                                      _download(u, t, c, s, rp)
                    ).pack()
                else:
                    ctk.CTkLabel(btn_col, text="Sin descarga\ndirecta",
                                 font=("Courier New",9), text_color=COLORS["text_dim"],
                                 justify="center").pack()

        def _download(url, title, console_name, slug, repo):
            roms_dir = self.config.get("roms_dir", os.path.expanduser("~/ROMs"))
            # Buscar si el rawg tag o tag deducido encaja con nuestras consolas conocidas
            dest_console = self.current_console
            for cn, info in CONSOLES.items():
                if console_name and (cn.lower() in console_name.lower() or info.get("emulator_key","") in console_name.lower()):
                    dest_console = cn
                    break
            
            dest_dir = os.path.join(roms_dir, dest_console)
            os.makedirs(dest_dir, exist_ok=True)
            
            set_status(f"⬇ Procesando descarga de {title}...", COLORS["yellow"])

            def do():
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    import cloudscraper
                    session = cloudscraper.create_scraper()
                    
                    if repo.get("type") == "retrostic":
                        headers["Referer"] = "https://www.retrostic.com/"
                        
                        # Post a Retrostic para sacar el Link
                        r_page = session.get(url, headers=headers, timeout=15)
                        r_page.raise_for_status()
                        soup = BeautifulSoup(r_page.text, 'html.parser')
                        inputs = soup.find_all('input', type='hidden')
                        data = {}
                        for inp in inputs:
                            name = inp.get('name')
                            val = inp.get('value')
                            if name: data[name] = val
                            
                        # Si no hay session, problable no es retrostic valido
                        if "session" not in data:
                            raise Exception("No se encontró el token de descarga en la página.")
                            
                        dl_post = url + "/download"
                        set_status(f"⬇ Obteniendo link final para {title}...", COLORS["yellow"])
                        r_post = session.post(dl_post, data=data, headers=headers, timeout=15)
                        r_post.raise_for_status()
                        soup_post = BeautifulSoup(r_post.text, 'html.parser')
                        
                        found_url = None
                        for s in soup_post.find_all('script'):
                            content = s.string
                            if content and ('http' in content):
                                match = re.search(r'(https?://[^\'"]+\.(?:zip|7z|rar|bin|smc|iso|nds|n64|z64))', content, re.IGNORECASE)
                                if match:
                                    found_url = match.group(1)
                                    break
                                    
                        if not found_url:
                            raise Exception("No se pudo extraer el enlace del script de Retrostic.")
                        
                        target_url = found_url
                        import urllib.parse
                        filename = urllib.parse.unquote(target_url.split("/")[-1])
                    else:
                        target_url = url
                        filename = url.split("/")[-1] or f"{sanitize_name(title)}.zip"
                        
                    filepath = os.path.join(dest_dir, filename)
                    set_status(f"⬇ Descargando {filename} en {dest_console}...", COLORS["yellow"])
                    
                    r = session.get(target_url, headers=headers, timeout=30, stream=True)
                    # Si el CDN falla, intentar raw GitHub (solo en caso de homebrew hub)
                    if r.status_code == 404 and "hh3.gbdev.io" in target_url and repo.get("type") != "retrostic":
                        fallback = target_url.replace(repo.get("cdn",""), repo.get("raw",""))
                        r = session.get(fallback, headers=headers, timeout=30, stream=True)
                        
                    r.raise_for_status()
                    total_mb = int(r.headers.get('content-length', 0)) / (1024*1024)
                    
                    with open(filepath, "wb") as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    
                    set_status(f"✓  '{title}' guardado correctamente.", COLORS["green"])
                            
                    if dest_console == self.current_console:
                        self.after(0, self._load_games)
                except Exception as e:
                    set_status(f"✗ Error: {e}", COLORS["red"])

            threading.Thread(target=do, daemon=True).start()

        ctk.CTkButton(row1, text="🔍 Buscar", font=("Courier New",11,"bold"),
                      fg_color=COLORS["accent"], hover_color=COLORS["accent2"],
                      width=100, height=34,
                      command=lambda: threading.Thread(target=fetch_games, daemon=True).start()
        ).pack(side="left")

        threading.Thread(target=fetch_games, daemon=True).start()

    def _install_retroarch(self, ra_var, cores_var, refresh_fn, settings_win):
        default_dir = r"C:\RetroArch-Win64"
        if not messagebox.askyesno("Instalar RetroArch", 
            f"¿Deseas descargar e instalar RetroArch 1.17.0 y todos los cores necesarios en:\n{default_dir}\n\nEsto puede tardar unos minutos.", parent=settings_win):
            return
            
        win = ctk.CTkToplevel(self)
        win.title("Instalador Automático")
        win.geometry("450x220")
        win.configure(fg_color=COLORS["bg_dark"])
        win.grab_set()
        
        lbl = ctk.CTkLabel(win, text="Preparando instalación...", font=("Courier New", 12), text_color=COLORS["text_bright"])
        lbl.pack(pady=(30, 10))
        
        progress = ctk.CTkProgressBar(win, width=350, fg_color=COLORS["bg_mid"], progress_color=COLORS["accent"])
        progress.pack(pady=10)
        progress.set(0)
        
        def worker():
            try:
                # 1. Bajar RetroArch Installer (EXE)
                win.after(0, lambda: lbl.configure(text="Descargando Instalador (1.19.1)..."))
                
                # Usamos el instalador oficial de Buildbot (Inno Setup)
                ra_url = "https://buildbot.libretro.com/stable/1.19.1/windows/x86_64/RetroArch-Win64-setup.exe"
                setup_path = os.path.join(os.path.expanduser("~"), "RetroArch_Setup.exe")
                
                r = requests.get(ra_url, stream=True, timeout=30)
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(setup_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                win.after(0, lambda d=downloaded, t=total_size: progress.set((d / t) * 0.4))
                                
                # 2. Ejecutar Instalación Silenciosa (Solicitando permisos de administrador)
                win.after(0, lambda: lbl.configure(text="Ejecutando instalación... (acepta el aviso de Windows)"))
                try:
                    # Usamos PowerShell para disparar el UAC (Aviso de administrador) y esperar
                    ps_command = f'Start-Process -FilePath "{setup_path}" -ArgumentList "/VERYSILENT", "/DIR=\\\"{default_dir}\\\"", "/SP-", "/NORESTART" -Verb RunAs -Wait'
                    subprocess.run(["powershell", "-Command", ps_command], check=True, shell=True)
                except Exception as ex:
                    print(f"Error ejecutando instalador EXE con elevación: {ex}")
                    # Si falla o el usuario cancela, intentamos abrirlo normal (aunque probablemente pida UAC igual)
                    win.after(0, lambda: lbl.configure(text="Se requieren permisos, abriendo instalador manual..."))
                    subprocess.run([setup_path, f"/DIR={default_dir}"], shell=True)
                
                try: os.remove(setup_path)
                except: pass
                
                # 3. Descargar Cores
                cores_dest = os.path.join(default_dir, "cores")
                os.makedirs(cores_dest, exist_ok=True)
                total_cores = len(RA_CORES)
                
                for i, (console, core_dll) in enumerate(RA_CORES.items()):
                    win.after(0, lambda c=console: lbl.configure(text=f"Descargando core: {c}..."))
                    core_zip_url = f"https://buildbot.libretro.com/nightly/windows/x86_64/latest/{core_dll}.zip"
                    core_zip_path = os.path.join(cores_dest, f"{core_dll}.zip")
                    
                    try:
                        cr = requests.get(core_zip_url, timeout=15)
                        if cr.status_code == 200:
                            with open(core_zip_path, 'wb') as f:
                                f.write(cr.content)
                            with zipfile.ZipFile(core_zip_path, 'r') as zip_ref:
                                zip_ref.extractall(cores_dest)
                            try: os.remove(core_zip_path)
                            except: pass
                    except Exception as ce:
                        print(f"Error con {core_dll}: {ce}")
                        
                    win.after(0, lambda idx=i: progress.set(0.4 + (0.6 * ((idx + 1) / total_cores))))
                
                # 4. Finalizado
                win.after(0, lambda: lbl.configure(text="¡Instalación completada exitosamente!", text_color=COLORS["green"]))
                win.after(0, lambda: progress.set(1.0))
                
                def update_ui():
                    ra_var.set(os.path.join(default_dir, "retroarch.exe"))
                    cores_var.set(cores_dest)
                    refresh_fn(cores_dest)
                    self.config["retroarch_path"] = ra_var.get()
                    self.config["cores_dir"] = cores_var.get()
                    save_config(self.config)
                    win.after(2000, win.destroy)
                    # Mostrar asistente de logros tras cerrar el instalador
                    self.after(2100, self._show_achievements_assistant)
                    
                win.after(0, update_ui)
                
            except Exception as e:
                print(f"Error en instalación: {e}")
                import traceback
                traceback.print_exc()
                def show_err(err=e):
                    lbl.configure(text=f"Error: {err}", text_color=COLORS["red"])
                    messagebox.showerror("Error de instalación", f"Ocurrió un error:\n{err}", parent=win)
                win.after(0, show_err)

        threading.Thread(target=worker, daemon=True).start()

    def _show_welcome_wizard(self):
        win = ctk.CTkToplevel(self)
        win.title(f"📦 Bienvenido a {APP_NAME}")
        win.geometry("750x720")
        win.configure(fg_color=COLORS["bg_dark"])
        win.attributes("-topmost", True)
        win.grab_set()

        self.setup_step = 0
        self.install_mode = "standard"

        def on_close():
            if self.setup_step < 5:
                if messagebox.askyesno("Salir", "¿Deseas salir del asistente? Se mostrará la app pero sin configurar.", parent=win):
                    self.deiconify()
                    win.destroy()
            else:
                self.deiconify()
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        main_container = ctk.CTkFrame(win, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        def clear_container():
            for w in main_container.winfo_children(): w.destroy()

        def next_step():
            self.setup_step += 1
            show_step()

        def show_step():
            clear_container()
            if self.setup_step == 0: step_intro()
            elif self.setup_step == 1: step_install_type()
            elif self.setup_step == 2: step_folders()
            elif self.setup_step == 3: step_retroarch()
            elif self.setup_step == 4: step_achievements()
            elif self.setup_step == 5: step_finish()

        def step_intro():
            header = ctk.CTkFrame(main_container, fg_color=COLORS["bg_mid"], height=120, corner_radius=0)
            header.pack(fill="x")
            ctk.CTkLabel(header, text=f"✨ BIENVENIDO A {APP_NAME.upper()}", 
                         font=("Courier New", 26, "bold"), text_color=COLORS["accent"]).pack(pady=40)
            body = ctk.CTkFrame(main_container, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=50, pady=30)
            ctk.CTkLabel(body, text="Tu centro de emulación premium.\nConfiguraremos todo para que empieces a jugar en segundos.",
                         font=("Courier New", 14), text_color=COLORS["text_bright"], justify="center").pack(pady=20)
            for icon, desc in [("🎨 Interfaz Moderna", "Diseño KH premium."), ("🌐 Descargas Directas", "ROMs al instante."), 
                               ("🏆 Logros Integrados", "Soporte RetroAchievements."), ("⚙️ Auto-Setup", "Instalamos RetroArch por ti.")]:
                f = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=10, height=50)
                f.pack(fill="x", pady=5)
                ctk.CTkLabel(f, text=icon, font=("Courier New", 12, "bold"), text_color=COLORS["yellow"], width=180).pack(side="left", padx=15)
                ctk.CTkLabel(f, text=desc, font=("Courier New", 11), text_color=COLORS["text_dim"]).pack(side="left")
            ctk.CTkButton(main_container, text="Comenzar →", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 14, "bold"), height=45, width=200, command=next_step).pack(pady=30)

        def step_install_type():
            ctk.CTkLabel(main_container, text="💾 Instalación de Nexus", font=("Courier New", 18, "bold"), text_color=COLORS["accent"]).pack(pady=(40, 10))
            ctk.CTkLabel(main_container, text="Elige cómo quieres configurar el programa.", font=("Courier New", 11), text_color=COLORS["text_dim"]).pack(pady=(0, 30))
            cards = ctk.CTkFrame(main_container, fg_color="transparent")
            cards.pack(fill="x", padx=40)
            std = ctk.CTkFrame(cards, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            std.pack(fill="x", pady=10)
            ctk.CTkLabel(std, text="🏠 Instalación Estándar", font=("Courier New", 13, "bold"), text_color=COLORS["green"]).pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(std, text="Copia el programa a tu PC y crea un acceso directo en el escritorio.", font=("Courier New", 10), text_color=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(0, 15))
            def_path = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ChvstxNexus")
            path_var = tk.StringVar(value=def_path)
            row = ctk.CTkFrame(std, fg_color="transparent"); row.pack(fill="x", padx=20, pady=(0, 15))
            ctk.CTkEntry(row, textvariable=path_var, font=("Courier New", 10), height=30).pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(row, text="...", width=40, command=lambda: path_var.set(filedialog.askdirectory() or path_var.get())).pack(side="right")
            def do_std():
                try:
                    target = path_var.get(); os.makedirs(target, exist_ok=True)
                    current_exe = sys.executable if getattr(sys, 'frozen', False) else None
                    if current_exe:
                        dest_exe = os.path.join(target, os.path.basename(current_exe))
                        if os.path.abspath(current_exe) != os.path.abspath(dest_exe): shutil.copy2(current_exe, dest_exe)
                        _create_desktop_shortcut(dest_exe)
                    self.config["first_run"] = False # Marcar como instalado
                    save_config(self.config)
                    next_step()
                except Exception as e: messagebox.showerror("Error", f"Error: {e}")
            ctk.CTkButton(std, text="Instalar y Continuar", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 11, "bold"), command=do_std).pack(pady=(0, 15))
            port = ctk.CTkFrame(cards, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            port.pack(fill="x", pady=10)
            ctk.CTkLabel(port, text="💾 Modo Portable", font=("Courier New", 13, "bold"), text_color=COLORS["yellow"]).pack(anchor="w", padx=20, pady=(15, 5))
            def do_port():
                try:
                    with open(PORTABLE_FILE, "w") as f: f.write("1")
                    messagebox.showinfo(APP_NAME, "Modo portable activado. Reinciciando...")
                    subprocess.Popen([sys.executable] + (sys.argv[1:] if getattr(sys, 'frozen', False) else [__file__] + sys.argv[1:]))
                    sys.exit()
                except Exception as e: messagebox.showerror("Error", f"Error: {e}")
            ctk.CTkButton(port, text="Usar Portable", font=("Courier New", 11), command=do_port).pack(pady=(0, 15))

        def step_folders():
            ctk.CTkLabel(main_container, text="📁 Tus Carpetas", font=("Courier New", 18, "bold"), text_color=COLORS["accent"]).pack(pady=(40, 10))
            f = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], corner_radius=12)
            f.pack(fill="x", padx=40, pady=25)
            rom_v = tk.StringVar(value=self.config.get("roms_dir", ""))
            ctk.CTkLabel(f, text="¿Dónde guardas tus ROMs?", font=("Courier New", 12, "bold")).pack(anchor="w")
            r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", pady=(5, 15))
            ctk.CTkEntry(r, textvariable=rom_v, font=("Courier New", 10)).pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(r, text="...", width=40, command=lambda: rom_v.set(filedialog.askdirectory() or rom_v.get())).pack(side="right")
            def save(): self.config["roms_dir"] = rom_v.get(); next_step()
            ctk.CTkButton(main_container, text="Siguiente →", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 12, "bold"), command=save).pack(pady=30)

        def step_retroarch():
            ctk.CTkLabel(main_container, text="🕹️ Emulación", font=("Courier New", 18, "bold"), text_color=COLORS["accent"]).pack(pady=(40, 10))
            ctk.CTkLabel(main_container, text="Se recomienda instalar RetroArch automáticamente.", font=("Courier New", 11), text_color=COLORS["text_dim"]).pack(pady=(0, 30))
            auto = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            auto.pack(fill="x", padx=40)
            ctk.CTkLabel(auto, text="📥 Instalación Silenciosa", font=("Courier New", 13, "bold"), text_color=COLORS["green"]).pack(anchor="w", padx=20, pady=(15, 5))
            def do_auto(): self._install_retroarch(tk.StringVar(), tk.StringVar(), lambda p: next_step(), win)
            ctk.CTkButton(auto, text="Instalar Ahora", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 11, "bold"), command=do_auto).pack(pady=(0, 15))
            ctk.CTkButton(main_container, text="Configurar después", fg_color="transparent", text_color=COLORS["text_dim"], command=next_step).pack(pady=20)

        def step_achievements():
            ctk.CTkLabel(main_container, text="🏆 Logros", font=("Courier New", 18, "bold"), text_color=COLORS["accent"]).pack(pady=(40, 10))
            f = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], corner_radius=12)
            f.pack(fill="x", padx=40, pady=25)
            u_v, k_v = tk.StringVar(value=self.config.get("ra_user", "")), tk.StringVar(value=self.config.get("ra_apikey", ""))
            ctk.CTkLabel(f, text="Usuario").pack(anchor="w")
            ctk.CTkEntry(f, textvariable=u_v).pack(fill="x", pady=(5, 10))
            ctk.CTkLabel(f, text="API Key").pack(anchor="w")
            ctk.CTkEntry(f, textvariable=k_v, show="*").pack(fill="x", pady=(5, 10))
            def save(): self.config["ra_user"] = u_v.get().strip(); self.config["ra_apikey"] = k_v.get().strip(); next_step()
            ctk.CTkButton(main_container, text="Finalizar →", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 12, "bold"), command=save).pack(pady=30)

        def step_finish():
            ctk.CTkLabel(main_container, text="✨ ¡Todo listo!", font=("Courier New", 22, "bold"), text_color=COLORS["green"]).pack(pady=60)
            self.config["first_run"] = False; self.config["nexus_first_run"] = False; save_config(self.config)
            ctk.CTkButton(main_container, text="🚀 Entrar al Nexus", fg_color=COLORS["accent"], text_color=COLORS["bg_dark"], font=("Courier New", 15, "bold"), height=50, width=250, command=win.destroy).pack(pady=20)
            def on_dest(e): self.deiconify(); self._load_games()
            win.bind("<Destroy>", on_dest)

        show_step()

    def _perform_uninstallation(self):
        """Borra toda la configuración y datos del programa."""
        if not messagebox.askyesno("Confirmar Desinstalación", 
                                   f"¿Estás seguro de que deseas desinstalar {APP_NAME}?\n\nEsto eliminará toda tu configuración, carátulas y el acceso directo del escritorio.",
                                   parent=self):
            return
        
        if not messagebox.askyesno("ADVERTENCIA FINAL", 
                                   "Esta acción no se puede deshacer. Se borrarán todos los datos locales de la aplicación. Los juegos NO se borrarán.",
                                   parent=self):
            return

        try:
            # 1. Borrar archivos de config
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            if os.path.exists(PLAYTIME_FILE): os.remove(PLAYTIME_FILE)
            
            # 2. Borrar caché de carátulas
            cache_dir = self.config.get("covers_cache")
            if cache_dir and os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir, ignore_errors=True)
            
            # 3. Borrar acceso directo
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut = os.path.join(desktop, f"{APP_NAME}.lnk")
            if os.path.exists(shortcut): os.remove(shortcut)
            
            # 4. Si hay archivo portable, borrarlo
            if os.path.exists(PORTABLE_FILE): os.remove(PORTABLE_FILE)

            messagebox.showinfo(APP_NAME, "Desinstalación completada. La aplicación se cerrará ahora.")
            self.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la desinstalación: {e}")

    # ════════ Configuración ══════════════════════════════════════════════
    def _open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Configuración")
        win.geometry("740x680")
        win.configure(fg_color=COLORS["bg_dark"])
        win.grab_set()

        ctk.CTkLabel(win, text="CONFIGURACIÓN", font=("Courier New",20,"bold"),
                     text_color=COLORS["accent"]).pack(pady=(24,4))
        ctk.CTkLabel(win, text="RetroArch y rutas de ROMs",
                     font=("Courier New",11), text_color=COLORS["text_dim"]).pack(pady=(0,16))

        scroll = ctk.CTkScrollableFrame(win, fg_color=COLORS["bg_mid"])
        scroll.pack(fill="both", expand=True, padx=20)

        # ── RetroArch exe ──
        ctk.CTkLabel(scroll, text="🕹️  RetroArch",
                     font=("Courier New",13,"bold"), text_color=COLORS["text_bright"]
        ).pack(anchor="w", padx=16, pady=(16,4))

        ra_row = ctk.CTkFrame(scroll, fg_color="transparent")
        ra_row.pack(fill="x", padx=16, pady=(0,4))
        ctk.CTkLabel(ra_row, text="retroarch.exe", font=("Courier New",10),
                     text_color=COLORS["text_dim"], width=110, anchor="w").pack(side="left")
        ra_var = tk.StringVar(value=self.config.get("retroarch_path",""))
        ctk.CTkEntry(ra_row, textvariable=ra_var, width=420, font=("Courier New",10),
                     fg_color=COLORS["bg_card"], text_color=COLORS["text_bright"],
                     border_color=COLORS["border"]).pack(side="left", padx=(0,8))
        def browse_ra():
            p = filedialog.askopenfilename(
                initialdir=r"C:\RetroArch-Win64",
                filetypes=[("RetroArch","retroarch.exe"),("Ejecutables","*.exe"),("Todos","*.*")])
            if p: ra_var.set(p)
        ctk.CTkButton(ra_row, text="...", width=40, font=("Courier New",11),
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      border_width=1, border_color=COLORS["border"],
                      command=browse_ra).pack(side="left")

        cores_row = ctk.CTkFrame(scroll, fg_color="transparent")
        cores_row.pack(fill="x", padx=16, pady=(4,12))
        ctk.CTkLabel(cores_row, text="Carpeta cores", font=("Courier New",10),
                     text_color=COLORS["text_dim"], width=110, anchor="w").pack(side="left")
        cores_var = tk.StringVar(value=self.config.get("cores_dir",""))
        ctk.CTkEntry(cores_row, textvariable=cores_var, width=420, font=("Courier New",10),
                     fg_color=COLORS["bg_card"], text_color=COLORS["text_bright"],
                     border_color=COLORS["border"]).pack(side="left", padx=(0,8))
        def browse_cores():
            d = filedialog.askdirectory(initialdir=r"C:\RetroArch-Win64")
            if d: cores_var.set(d)
        ctk.CTkButton(cores_row, text="...", width=40, font=("Courier New",11),
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      border_width=1, border_color=COLORS["border"],
                      command=browse_cores).pack(side="left")

        # ── Estado de cores ──
        ctk.CTkLabel(scroll, text="📦  Estado de cores instalados",
                     font=("Courier New",13,"bold"), text_color=COLORS["text_bright"]
        ).pack(anchor="w", padx=16, pady=(8,4))

        cores_status = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10,
                                     border_width=1, border_color=COLORS["border"])
        cores_status.pack(fill="x", padx=16, pady=(0,12))

        def refresh_cores_status(cores_path=None):
            for w in cores_status.winfo_children():
                w.destroy()
            cd = cores_path or cores_var.get()
            for cn, core_file in RA_CORES.items():
                core_full = os.path.join(cd, core_file)
                installed = os.path.exists(core_full)
                info      = CONSOLES.get(cn, {})
                row = ctk.CTkFrame(cores_status, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=3)
                ctk.CTkLabel(row, text=f"{info.get('emoji','')} {cn}",
                             font=("Courier New",11), text_color=info.get("color","#fff"),
                             width=130, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=core_file, font=("Courier New",9),
                             text_color=COLORS["text_dim"]).pack(side="left")
                status_text  = "✓ Instalado" if installed else "✗ No encontrado"
                status_color = COLORS["green"] if installed else COLORS["red"]
                ctk.CTkLabel(row, text=status_text, font=("Courier New",10,"bold"),
                             text_color=status_color).pack(side="right")

        refresh_cores_status(self.config.get("cores_dir",""))

        ctk.CTkButton(scroll, text="🔍  Verificar cores", font=("Courier New",10),
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      border_width=1, border_color=COLORS["border"],
                      command=refresh_cores_status).pack(pady=12)

        # Línea de versión
        version_f = ctk.CTkFrame(win, fg_color="transparent")
        version_f.pack(side="bottom", fill="x", pady=10)
        ctk.CTkLabel(version_f, text=f"{APP_NAME} v{CURRENT_VERSION}", 
                     font=("Courier New", 10), text_color=COLORS["text_dim"]).pack()


        # ── Instalación Automática ──
        ctk.CTkLabel(scroll, text="📦  Instalación de RetroArch y Cores",
                     font=("Courier New",13,"bold"), text_color=COLORS["accent"]
        ).pack(anchor="w", padx=16, pady=(8,4))
        
        install_row = ctk.CTkFrame(scroll, fg_color="transparent")
        install_row.pack(fill="x", padx=16, pady=(0,12))
        ctk.CTkLabel(install_row, text="¿No tienes RetroArch? Instálalo automáticamente en tu PC:", 
                     font=("Courier New",10), text_color=COLORS["text_dim"], 
                     anchor="w").pack(side="left")
        ctk.CTkButton(install_row, text="⬇ Instalar ahora", font=("Courier New",11,"bold"),
                      fg_color=COLORS["accent"], hover_color=COLORS["accent2"], height=30,
                      command=lambda: self._install_retroarch(ra_var, cores_var, refresh_cores_status, win)
        ).pack(side="left", padx=20)

        # ── Carpeta ROMs ──
        ctk.CTkLabel(scroll, text="📁  Carpeta de ROMs",
                     font=("Courier New",13,"bold"), text_color=COLORS["text_bright"]
        ).pack(anchor="w", padx=16, pady=(8,4))
        roms_row = ctk.CTkFrame(scroll, fg_color="transparent")
        roms_row.pack(fill="x", padx=16, pady=(0,16))
        roms_var = tk.StringVar(value=self.config.get("roms_dir",""))
        ctk.CTkEntry(roms_row, textvariable=roms_var, width=490, font=("Courier New",11),
                     fg_color=COLORS["bg_card"], text_color=COLORS["text_bright"],
                     border_color=COLORS["border"]).pack(side="left", padx=(0,8))
        ctk.CTkButton(roms_row, text="Explorar", width=90, font=("Courier New",11),
                      fg_color=COLORS["accent"], hover_color=COLORS["accent2"],
                      command=lambda: roms_var.set(filedialog.askdirectory() or roms_var.get())
        ).pack(side="left")

        # ── RetroAchievements ──
        ctk.CTkLabel(scroll, text="🏆  RetroAchievements",
                     font=("Courier New",13,"bold"), text_color=COLORS["text_bright"]
        ).pack(anchor="w", padx=16, pady=(8,2))
        ctk.CTkLabel(scroll,
                     text="Introduce tu usuario y API Key de retroachievements.org para ver tus logros.",
                     font=("Courier New",9), text_color=COLORS["text_dim"]
        ).pack(anchor="w", padx=16, pady=(0,6))

        ra_user_row = ctk.CTkFrame(scroll, fg_color="transparent")
        ra_user_row.pack(fill="x", padx=16, pady=(0,4))
        ctk.CTkLabel(ra_user_row, text="Usuario", font=("Courier New",10),
                     text_color=COLORS["text_dim"], width=110, anchor="w").pack(side="left")
        ra_user_var = tk.StringVar(value=self.config.get("ra_user", ""))
        ctk.CTkEntry(ra_user_row, textvariable=ra_user_var, width=420, font=("Courier New",10),
                     placeholder_text="Tu usuario de RetroAchievements",
                     fg_color=COLORS["bg_card"], text_color=COLORS["text_bright"],
                     border_color=COLORS["border"]).pack(side="left")

        ra_apikey_row = ctk.CTkFrame(scroll, fg_color="transparent")
        ra_apikey_row.pack(fill="x", padx=16, pady=(0,16))
        ctk.CTkLabel(ra_apikey_row, text="API Key", font=("Courier New",10),
                     text_color=COLORS["text_dim"], width=110, anchor="w").pack(side="left")
        ra_apikey_var = tk.StringVar(value=self.config.get("ra_apikey", ""))
        ctk.CTkEntry(ra_apikey_row, textvariable=ra_apikey_var, width=420, font=("Courier New",10),
                     placeholder_text="Tu API Key (retroachievements.org → Configuración → API Key)",
                     fg_color=COLORS["bg_card"], text_color=COLORS["text_bright"],
                     border_color=COLORS["border"], show="*").pack(side="left")

        # ── Peligro ──
        ctk.CTkLabel(scroll, text="⚠️  Zona de Peligro", font=("Courier New",13,"bold"), text_color=COLORS["red"]).pack(anchor="w", padx=16, pady=(20,4))
        ctk.CTkButton(scroll, text="🗑️  Desinstalar aplicación y borrar datos", 
                      font=("Courier New",11,"bold"), fg_color="transparent", border_width=1, border_color=COLORS["red"],
                      text_color=COLORS["red"], hover_color="#330000", height=36,
                      command=self._perform_uninstallation).pack(padx=16, pady=(0,20))

        def save():
            self.config["retroarch_path"] = ra_var.get()
            self.config["cores_dir"]      = cores_var.get()
            self.config["roms_dir"]       = roms_var.get()
            self.config["ra_user"]        = ra_user_var.get().strip()
            self.config["ra_apikey"]      = ra_apikey_var.get().strip()
            # Limpiar clave antigua si existía
            self.config.pop("emulators", None)
            save_config(self.config)
            win.destroy()
            self._load_games()
            self._set_status("✓  Configuración guardada")

        ctk.CTkButton(win, text="💾  Guardar configuración",
                      font=("Courier New",13,"bold"), fg_color=COLORS["accent"],
                      hover_color=COLORS["accent2"], height=44, command=save).pack(pady=16)


if __name__ == "__main__":
    app = ChvstxNexus()
    app.mainloop()