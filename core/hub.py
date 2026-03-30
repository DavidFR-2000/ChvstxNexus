import requests
from bs4 import BeautifulSoup
import re

HB_REPOS = {
    "Retrostic (Todas las consolas)": {"type": "retrostic"},
    "R-Roms (NES)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20Entertainment%20System%20(Headered)/"},
    "R-Roms (SNES)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/"},
    "R-Roms (N64)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%2064%20(BigEndian)/"},
    "R-Roms (GameCube)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/"},
    "R-Roms (Wii)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/"},
    "R-Roms (Game Boy)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/"},
    "R-Roms (GBC)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/"},
    "R-Roms (GBA)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/"},
    "R-Roms (NDS)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20(Decrypted)/"},
    "R-Roms (Master System)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Sega%20-%20Master%20System%20-%20Mark%20III/"},
    "R-Roms (Game Gear)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Sega%20-%20Game%20Gear/"},
    "R-Roms (Mega Drive)": {"type": "myrient", "url": "https://myrient.erista.me/files/No-Intro/Sega%20-%20Mega%20Drive%20-%20Genesis/"},
    "R-Roms (Saturn)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sega%20-%20Saturn/"},
    "R-Roms (Dreamcast)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sega%20-%20Dreamcast/"},
    "R-Roms (PS1)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation/"},
    "R-Roms (PS2)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202/"},
    "R-Roms (PS3)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%203/"},
    "R-Roms (PSP)": {"type": "myrient", "url": "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20Portable/"},
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

VALID_EXTS = (".gb", ".gbc", ".gba", ".nes", ".zip", ".smc", ".sfc", ".nds", ".7z", ".rar", ".bin", ".iso", ".chd", ".rvz")

def search_hub_games(console_name: str, query: str):
    """
    Searches for games in the given Hub console repo.
    Returns a list of dictionaries with game data.
    """
    repo = HB_REPOS.get(console_name)
    if not repo:
        return []
        
    headers = {"User-Agent": "ChvstxNexus/2.0", "Accept": "application/vnd.github+json"}
    query = query.strip().lower()
    
    if repo.get("type") == "retrostic":
        if not query:
            raise ValueError("Por favor, escribe un nombre para buscar en Retrostic.")
            
        url = f"https://www.retrostic.com/search?search_term_string={requests.utils.quote(query)}"
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        nodes = soup.find_all('a', href=lambda href: href and '/roms/' in href)
        
        games = []
        seen_urls = set()
        for node in nodes:
            href = node['href']
            if len(href.split('/')) <= 3: continue
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
        return games

    elif repo.get("type") == "myrient":
        if not query:
            raise ValueError("Escribe un juego para buscar en esta consola de R-Roms.")
            
        url = repo["url"]
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        nodes = soup.find_all('a', href=True)
        
        games = []
        valid_exts_myrient = (".zip", ".7z", ".rar", ".rvz")
        
        for node in nodes:
            filename = requests.utils.unquote(node['href'])
            if not any(filename.lower().endswith(e) for e in valid_exts_myrient):
                continue
            
            if query in filename.lower():
                title = filename.rsplit('.', 1)[0]
                dl_link = url + node['href']
                games.append({
                    "_slug": filename,
                    "_repo": repo,
                    "title": title,
                    "author": "R-Roms/Myrient",
                    "description": f"Encontrado en {console_name}. Archivo: {filename}",
                    "tags": [console_name.split(" ")[-1].upper()],
                    "files": [{"url": dl_link}]
                })
                if len(games) >= 50:
                    break
        return games

    else:
        # Github Homebrew
        r = requests.get(repo["api"], headers=headers, timeout=15)
        r.raise_for_status()
        entries = [e for e in r.json() if e["type"] == "dir"]
        
        if query:
            entries = [e for e in entries if query in e["name"].lower()]
            
        entries = entries[:60]
        games = []
        for e in entries:
            slug = e["name"]
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
        return games

def get_download_url(game: dict) -> str:
    repo = game.get("_repo", {})
    slug = game.get("_slug", "")
    
    if repo.get("type") == "retrostic":
        return game.get("files", [{}])[0].get("url")
        
    for f in game.get("files", []):
        fname = f.get("filename", "") or f.get("url", "")
        if not fname: continue
        if fname.startswith("http"):
            return fname
        elif any(fname.lower().endswith(e) for e in VALID_EXTS):
            return f"{repo.get('cdn','')}/{slug}/{fname}"
    return None
