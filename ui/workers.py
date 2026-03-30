from PySide6.QtCore import QThread, Signal
from core.scraper import fetch_game_info, download_cover

class GameInfoWorker(QThread):
    finished = Signal(object)
    
    def __init__(self, game_name, platform_id, console_name):
        super().__init__()
        self.game_name = game_name
        self.platform_id = platform_id
        self.console_name = console_name
        
    def run(self):
        try:
            data = fetch_game_info(self.game_name, self.platform_id, self.console_name)
            self.finished.emit(data)
        except Exception:
            self.finished.emit(None)

InfoWorker = GameInfoWorker

class AchWorker(QThread):
    finished = Signal(dict)
    def __init__(self, game_id, user, apikey):
        super().__init__()
        self.game_id = game_id
        self.user = user
        self.apikey = apikey
    def run(self):
        from core.retroarch import ra_get_achievements
        try:
            data = ra_get_achievements(self.game_id, self.user, self.apikey)
            self.finished.emit(data or {})
        except:
            self.finished.emit({})

class RAStatsWorker(QThread):
    finished = Signal(dict)
    
    def __init__(self, user, apikey):
        super().__init__()
        self.user = user
        self.apikey = apikey

    def run(self):
        from core.retroarch import ra_get_user_summary
        data = ra_get_user_summary(self.user, self.apikey)
        self.finished.emit(data or {})

class CoverDownloadWorker(QThread):
    finished = Signal(str, str) # title, path
    
    def __init__(self, game_name, cache_dir, platform_id, console_name):
        super().__init__()
        self.game_name = game_name
        self.cache_dir = cache_dir
        self.platform_id = platform_id
        self.console_name = console_name
        
    def run(self):
        path = download_cover(self.game_name, self.cache_dir, self.platform_id, self.console_name)
        self.finished.emit(self.game_name, path if path else "")

class HubSearchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, console_name, query):
        super().__init__()
        self.console_name = console_name
        self.query = query
        
    def run(self):
        from core.hub import search_hub_games
        try:
            games = search_hub_games(self.console_name, self.query)
            self.finished.emit(games)
        except Exception as e:
            self.error.emit(str(e))

class HubDownloadWorker(QThread):
    progress = Signal(float, float, float) # pct, downloaded_mb, total_mb
    finished = Signal(bool, str) # success, msg
    
    def __init__(self, url, dest_dir, filename, repo, allowed_extensions=None):
        super().__init__()
        self.url = url
        self.dest_dir = dest_dir
        self.filename = filename
        self.repo = repo
        self.allowed_extensions = allowed_extensions or []
        
    def run(self):
        import os, time, re
        from core.utils import sanitize_name
        try:
            os.makedirs(self.dest_dir, exist_ok=True)
            import cloudscraper
            session = cloudscraper.create_scraper()
            headers = {"User-Agent": "Mozilla/5.0"}
            
            target_url = self.url
            if self.repo.get("type") == "retrostic":
                headers["Referer"] = "https://www.retrostic.com/"
                r_page = session.get(self.url, headers=headers, timeout=15)
                r_page.raise_for_status()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r_page.text, 'html.parser')
                data = {inp.get('name'): inp.get('value') for inp in soup.find_all('input', type='hidden') if inp.get('name')}
                if "session" not in data:
                    raise Exception("Fallo al autenticar la descarga en Retrostic")
                
                r_post = session.post(self.url + "/download", data=data, headers=headers, timeout=15)
                r_post.raise_for_status()
                soup_post = BeautifulSoup(r_post.text, 'html.parser')
                found = None
                for s in soup_post.find_all('script'):
                    if s.string and 'http' in s.string:
                        m = re.search(r'(https?://[^\'"]+\.(?:zip|7z|rar|bin|smc|iso|nds|n64|z64))', s.string, re.IGNORECASE)
                        if m:
                            found = m.group(1)
                            break
                if not found:
                    raise Exception("No se extrajo enlace de Retrostic")
                target_url = found
                import urllib.parse
                self.filename = urllib.parse.unquote(target_url.split("/")[-1])
            else:
                import urllib.parse
                self.filename = urllib.parse.unquote(self.url.split("/")[-1]) or f"{sanitize_name(self.filename)}.zip"
            
            filepath = os.path.join(self.dest_dir, self.filename)
            r = session.get(target_url, headers=headers, timeout=30, stream=True)
            if r.status_code == 404 and "hh3.gbdev.io" in target_url and self.repo.get("type") != "retrostic":
                fallback = target_url.replace(self.repo.get("cdn",""), self.repo.get("raw",""))
                r = session.get(fallback, headers=headers, timeout=30, stream=True)
            r.raise_for_status()
            
            total_bytes = int(r.headers.get('content-length', 0))
            total_mb = total_bytes / (1024*1024) if total_bytes else 0
            
            downloaded = 0
            last_t = time.time()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes > 0:
                            now = time.time()
                            if now - last_t > 0.15:
                                last_t = now
                                down_mb = downloaded / (1024*1024)
                                self.progress.emit(downloaded / total_bytes, down_mb, total_mb)
            
            
            # Subdirectories and Auto-Extraction Logic
            ext = os.path.splitext(self.filename)[1].lower()
            if ext and ext not in self.allowed_extensions and ext in (".zip", ".7z", ".rar"):
                self.progress.emit(1.0, down_mb, total_mb) # Force 100%
                self.finished.emit(True, f"Descargado. Extrayendo {self.filename}...")
                
                try:
                    if ext == ".zip":
                        import zipfile
                        with zipfile.ZipFile(filepath, 'r') as z:
                            z.extractall(self.dest_dir)
                    elif ext == ".7z":
                        import py7zr
                        with py7zr.SevenZipFile(filepath, mode='r') as z:
                            z.extractall(path=self.dest_dir)
                    elif ext == ".rar":
                        import rarfile
                        with rarfile.RarFile(filepath, 'r') as r:
                            r.extractall(self.dest_dir)
                            
                    os.remove(filepath)
                    self.finished.emit(True, f"Completado y extraído: {title}")
                    return
                except Exception as e:
                    self.finished.emit(False, f"Descargado, pero falló la extracción: {e}")
                    return
            
            self.finished.emit(True, f"Descargado: {self.filename}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e))
