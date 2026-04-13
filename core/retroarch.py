import os
import requests
from io import BytesIO
from PIL import Image

RA_BASE = "https://retroachievements.org/API"

RA_CONSOLE_IDS = {
    "Arcade (MAME)": 53,
    "Atari 2600": 25,
    "NES":        7,
    "SNES":       3,
    "N64":        2,
    "GameCube":   16,
    "Game Boy":   4,
    "GBA":        5,
    "NDS":        18,
    "Master System": 9,
    "Mega Drive": 1,
    "Saturn":     17,
    "PS1":        12,
    "PS2":        21,
    "PSP":        41,
}

from core.utils import sanitize_name

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
        games = r.json()
        name_clean = sanitize_name(game_name).lower()
        best_id, best_score = None, 0
        for g in games:
            title_clean = sanitize_name(g.get("Title", "")).lower()
            score = sum(1 for w in name_clean.split() if w in title_clean)
            if score > best_score:
                best_score = score
                best_id = g.get("ID")
        return best_id if best_score > 0 else None
    except Exception as e:
        import logging
        logging.error(f"Error RA search_game: {e}")
        return None

def ra_get_console_games(console_name, ra_user="", ra_apikey=""):
    console_id = RA_CONSOLE_IDS.get(console_name)
    if not console_id or not ra_user or not ra_apikey:
        return []
    try:
        url = (f"{RA_BASE}/API_GetGameList.php"
               f"?z={ra_user}&y={ra_apikey}&i={console_id}&h=1")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        import logging
        logging.error(f"Error RA get_console_games: {e}")
    return []

def ra_get_achievements(ra_game_id, ra_user="", ra_apikey=""):
    if not ra_user or not ra_apikey:
        return None
    try:
        url = (f"{RA_BASE}/API_GetGameInfoAndUserProgress.php"
               f"?z={ra_user}&y={ra_apikey}&u={ra_user}&g={ra_game_id}")
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        result = []
        for ach_id, a in data.get("Achievements", {}).items():
            result.append({
                "id":          ach_id,
                "title":       a.get("Title", ""),
                "description": a.get("Description", ""),
                "points":      a.get("Points", 0),
                "badge_url":   f"https://media.retroachievements.org/Badge/{a.get('BadgeName', '')}.png",
                "unlocked":    a.get("DateEarned") is not None,
                "date_earned": a.get("DateEarned", ""),
            })
        result.sort(key=lambda x: (not x["unlocked"], x["title"]))
        return result
    except Exception as e:
        import logging
        logging.error(f"Error RA get_achievements: {e}")
        return None

def ra_get_badge_image(badge_url, unlocked=True):
    try:
        if not unlocked:
            badge_url = badge_url.replace(".png", "_lock.png")
        r = requests.get(badge_url, timeout=6)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img.resize((48, 48), Image.Resampling.LANCZOS)
    except Exception as e:
        import logging
        logging.warning(f"Error RA get_badge: {e}")
    return None

def ra_get_user_summary(ra_user, ra_apikey):
    if not ra_user or not ra_apikey:
        return None
    try:
        url = (f"{RA_BASE}/API_GetUserSummary.php"
               f"?z={ra_user}&y={ra_apikey}&u={ra_user}&g=100&a=5")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        import logging
        logging.error(f"Error RA get_user_summary: {e}")
    return None
