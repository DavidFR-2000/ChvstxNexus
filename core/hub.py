import requests
from bs4 import BeautifulSoup
import re

HB_REPOS = {
    "Retrostic (Todas las consolas)": {"type": "retrostic"},
    "Axekin (NES)": {"type": "axekin", "system": "1"},
    "Axekin (SNES)": {"type": "axekin", "system": "2"},
    "Axekin (N64)": {"type": "axekin", "system": "3"},
    "Axekin (GameCube)": {"type": "axekin", "system": "4"},
    "Axekin (Wii)": {"type": "axekin", "system": "5"},
    "Axekin (Game Boy)": {"type": "axekin", "system": "8"},
    "Axekin (GBC)": {"type": "axekin", "system": "9"},
    "Axekin (GBA)": {"type": "axekin", "system": "10"},
    "Axekin (NDS)": {"type": "axekin", "system": "11"},
    "Axekin (Master System)": {"type": "axekin", "system": "24"},
    "Axekin (Game Gear)": {"type": "axekin", "system": "28"},
    "Axekin (Mega Drive)": {"type": "axekin", "system": "25"},
    "Axekin (Saturn)": {"type": "axekin", "system": "26"},
    "Axekin (Dreamcast)": {"type": "axekin", "system": "27"},
    "Axekin (PS1)": {"type": "axekin", "system": "13"},
    "Axekin (PS2)": {"type": "axekin", "system": "14"},
    "Axekin (PS3)": {"type": "axekin", "system": "15"},
    "Axekin (PSP)": {"type": "axekin", "system": "18"},
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

    elif repo.get("type") == "axekin":
        if not query:
            raise ValueError("Escribe un juego para buscar en esta consola de Axekin.")
            
        system = repo.get("system")
        url = f"https://www.axekin.com/games?platform={system}&search={requests.utils.quote(query)}"
        
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        games = []
        for a in soup.find_all('a', href=re.compile(r'^/games/.+')):
            title = a.get_text(strip=True)
            if not title or title.lower() in ("browse", "view all"):
                continue
            
            slug = a['href'].split('/games/')[-1]
            if not slug or '?' in slug:
                continue
                
            dl_link = f"https://www.axekin.com/games/{slug}"
            
            if any(g["_slug"] == slug for g in games):
                continue
                
            games.append({
                "_slug": slug,
                "_repo": repo,
                "title": title,
                "author": f"Axekin (Dir)",
                "description": f"Encontrado en Axekin. ID: {slug}",
                "tags": [console_name.split(" ")[-1].replace(")", "")],
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
            except Exception as e:
                import logging
                logging.warning(f"Error cargando detalle json de juego {slug}: {e}")
        return games

def get_download_url(game: dict) -> str:
    repo = game.get("_repo", {})
    slug = game.get("_slug", "")
    
    if repo.get("type") in ("retrostic", "axekin"):
        return game.get("files", [{}])[0].get("url")
        
    for f in game.get("files", []):
        fname = f.get("filename", "") or f.get("url", "")
        if not fname: continue
        if fname.startswith("http"):
            return fname
        elif any(fname.lower().endswith(e) for e in VALID_EXTS):
            return f"{repo.get('cdn','')}/{slug}/{fname}"
    return None
