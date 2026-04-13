import os
import json
import sys

# ─── Configuración Global ────────────────────────────────────────────────────
CURRENT_VERSION = "4.0.1"
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

import logging
LOG_FILE = os.path.join(CONFIG_DIR, "nexus_debug.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)


# ─── Apariencia ──────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":     "#121212",  # Fondo oscuro premium
    "bg_mid":      "#1e1e20",  # Paneles y nav
    "bg_card":     "#262628",  # Fondo de tarjeta subyacente
    "bg_hover":    "#323235",  # Hover sutil
    "accent":      "#00e5ff",  # Cyan neón (RetroFlow Vibe)
    "accent2":     "#00b3cc",  # Cyan secundario
    "secondary":   "#b388ff",  # Morado acento secundario
    "text_bright": "#ffffff",
    "text_dim":    "#a0a0a5",
    "border":      "#2a2a2d",
    "green":       "#00ff9d",
    "yellow":      "#00e5ff",  # ¡AMARILLO ELIMINADO! Sustituido por Cyan en las variables antiguas para no romper nada.
    "red":         "#ff0055",
    "glass":       "rgba(255, 255, 255, 0.05)",
}

CONSOLES = {
    # Arcade & Early Home
    "Arcade (MAME)": {"emoji":"👾","color":"#ff0033","extensions":[".zip",".7z"],              "emulator_key":"mame",     "rawg_platform":111},
    "Atari 2600": {"emoji":"📺","color":"#c19a6b","extensions":[".a26",".bin",".rom",".zip"],"emulator_key":"atari2600","rawg_platform":23},
    
    # Nintendo
    "NES":        {"emoji":"🟥","color":"#e63946","extensions":[".nes",".zip"],                 "emulator_key":"nes",      "rawg_platform":49},
    "SNES":       {"emoji":"🎮","color":"#9b5de5","extensions":[".sfc",".smc",".zip"],         "emulator_key":"snes",     "rawg_platform":10},
    "N64":        {"emoji":"🟡","color":"#f9c74f","extensions":[".z64",".n64",".v64",".zip"],   "emulator_key":"n64",      "rawg_platform":83},
    "GameCube":   {"emoji":"🟣","color":"#c77dff","extensions":[".iso",".gcm",".rvz"],          "emulator_key":"gamecube", "rawg_platform":105},
    "Game Boy":   {"emoji":"🟩","color":"#80b918","extensions":[".gb",".zip"],                  "emulator_key":"gb",       "rawg_platform":26},
    "Game Boy Color":{"emoji":"🟪","color":"#b5179e","extensions":[".gbc",".zip"],               "emulator_key":"gbc",      "rawg_platform":43},
    "GBA":        {"emoji":"🕹️","color":"#00b4d8","extensions":[".gba",".zip"],                "emulator_key":"gba",      "rawg_platform":24},
    "NDS":        {"emoji":"📟","color":"#4cc9f0","extensions":[".nds",".zip"],                 "emulator_key":"nds",      "rawg_platform":77},
    "Wii":        {"emoji":"📺","color":"#00b4d8","extensions":[".iso",".wbfs",".rvz"],         "emulator_key":"wii",      "rawg_platform":11},
    
    # Sega
    "Master System":{"emoji":"⬛","color":"#d90429","extensions":[".sms",".zip"],               "emulator_key":"mastersystem","rawg_platform":74},
    "Game Gear":  {"emoji":"🌈","color":"#3f37c9","extensions":[".gg",".zip"],                  "emulator_key":"gamegear", "rawg_platform":77},
    "Mega Drive": {"emoji":"🔥","color":"#f72585","extensions":[".md",".gen",".bin",".zip"],    "emulator_key":"megadrive","rawg_platform":167},
    "Saturn":     {"emoji":"🪐","color":"#ff9f1c","extensions":[".iso",".bin",".cue",".m3u"],   "emulator_key":"saturn",   "rawg_platform":107},
    "Dreamcast":  {"emoji":"🌀","color":"#fca311","extensions":[".cdi",".gdi",".chd"],          "emulator_key":"dreamcast","rawg_platform":106},
    
    # Sony PlayStation
    "PS1":        {"emoji":"🎯","color":"#0066cc","extensions":[".bin",".cue",".iso",".img",".chd",".m3u"],"emulator_key":"ps1","rawg_platform":27},
    "PS2":        {"emoji":"⚡","color":"#4361ee","extensions":[".iso",".bin",".img",".chd"],"emulator_key":"ps2",      "rawg_platform":15},
    "PS3":        {"emoji":"🔴","color":"#b5179e","extensions":[".iso",".bin",".img"],"emulator_key":"ps3",      "rawg_platform":16},
    "PSP":        {"emoji":"📱","color":"#48cae4","extensions":[".iso",".cso",".pbp",".chd"],"emulator_key":"psp",      "rawg_platform":17},
}

RAWG_API_KEY  = "2db521236abd45be988b71c1015f1bc3"

RA_CORES = {
    "Arcade (MAME)": ["mame_libretro.dll", "mame2003_plus_libretro.dll", "fbneo_libretro.dll"],
    "Atari 2600":    ["stella_libretro.dll"],
    "NES":           ["mesen_libretro.dll", "fceumm_libretro.dll", "nestopia_libretro.dll"],
    "SNES":          ["snes9x_libretro.dll", "bsnes_libretro.dll"],
    "GBA":           ["mgba_libretro.dll", "vbam_libretro.dll"],
    "NDS":           ["melonds_libretro.dll", "desmume_libretro.dll"],
    "N64":           ["mupen64plus_next_libretro.dll", "parallel_n64_libretro.dll"],
    "GameCube":      ["dolphin_libretro.dll"],
    "Wii":           ["dolphin_libretro.dll"],
    "Game Boy":      ["gambatte_libretro.dll", "sameboy_libretro.dll", "gearboy_libretro.dll"],
    "Game Boy Color":["gambatte_libretro.dll", "sameboy_libretro.dll"],
    "Master System": ["genesis_plus_gx_libretro.dll", "picodrive_libretro.dll"],
    "Game Gear":     ["genesis_plus_gx_libretro.dll", "gearsystem_libretro.dll"],
    "Mega Drive":    ["genesis_plus_gx_libretro.dll", "picodrive_libretro.dll"],
    "Saturn":        ["mednafen_saturn_libretro.dll", "yabause_libretro.dll", "kronos_libretro.dll"],
    "Dreamcast":     ["flycast_libretro.dll"],
    "PS1":           ["duckstation_libretro.dll", "pcsx_rearmed_libretro.dll", "mednafen_psx_hw_libretro.dll", "mednafen_psx_libretro.dll", "swanstation_libretro.dll"],
    "PS2":           ["lrps2_libretro.dll", "pcsx2_libretro.dll", "play_libretro.dll"],
    "PS3":           ["rpcs3_libretro.dll"],
    "PSP":           ["ppsspp_libretro.dll"],
}

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
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in default.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
    return default

def check_branding_migration(cfg):
    """Fuerza el asistente de bienvenida si es la primera transición a Nexus."""
    if "nexus_first_run" not in cfg:
        cfg["nexus_first_run"] = True
        return True
    return cfg.get("first_run", True)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_playtime():
    if os.path.exists(PLAYTIME_FILE):
        try:
            with open(PLAYTIME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load playtime file: {e}")
    return {}

def save_playtime(data):
    with open(PLAYTIME_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
