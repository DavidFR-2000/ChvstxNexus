import os
import re
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from urllib.parse import quote

from core.utils import sanitize_name, clean_rom_name, name_similarity
from core.config import RAWG_API_KEY

def get_cover_path(cache_dir, game_name):
    return os.path.join(cache_dir, f"{sanitize_name(game_name)}.jpg")

def download_cover(game_name, cache_dir, platform_id=None, console_name=""):
    cover_path = get_cover_path(cache_dir, game_name)
    if os.path.exists(cover_path):
        return cover_path
    os.makedirs(cache_dir, exist_ok=True)
    clean_name = clean_rom_name(game_name)
    query = sanitize_name(clean_name)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

    # Fuente 1: RAWG API
    try:
        url = (f"https://api.rawg.io/api/games?search={quote(query)}"
               f"&key={RAWG_API_KEY}&page_size=5")
        if platform_id:
            url += f"&platforms={platform_id}"
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            results = r.json().get("results", [])
            scored = []
            for res in results:
                res_name = res.get("name", "")
                sim = name_similarity(clean_name, res_name)
                if sim >= 0.4 and res.get("background_image"):
                    scored.append((sim, res))
            scored.sort(key=lambda x: x[0], reverse=True)
            
            for sim, res in scored:
                img_url = res.get("background_image")
                if img_url:
                    try:
                        img_r = requests.get(img_url, headers=headers, timeout=8)
                        if img_r.status_code == 200:
                            img = Image.open(BytesIO(img_r.content)).convert("RGB")
                            img = ImageOps.pad(img, (300, 200), color="#0a0a0f")
                            img.save(cover_path, "JPEG")
                            return cover_path
                    except Exception as e:
                        import logging
                        logging.warning(f"Error guardando imagen RAWG de {clean_name}: {e}")
                        continue
    except Exception as e:
        import logging
        logging.warning(f"Error API RAWG info cover en {clean_name}: {e}")

    # Fuente 2: Bing Images
    try:
        console_hint = f" {console_name}" if console_name else ""
        q = quote(f"{query}{console_hint} game cover art box")
        r = requests.get(f"https://www.bing.com/images/search?q={q}&first=1",
                         headers=headers, timeout=7)
        if r.status_code == 200:
            matches = re.findall(r'"murl":"(https?://[^"]+\.(?:jpg|jpeg|png))"', r.text)
            if not matches:
                matches = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png))&quot;', r.text)
            
            for img_url in matches[:5]:
                try:
                    img_r = requests.get(img_url, headers=headers, timeout=6)
                    if img_r.status_code == 200 and len(img_r.content) > 5000:
                        img = Image.open(BytesIO(img_r.content)).convert("RGB")
                        img = ImageOps.pad(img, (300, 200), color="#0a0a0f")
                        img.save(cover_path, "JPEG")
                        return cover_path
                except Exception as e:
                    import logging
                    logging.warning(f"Error guardando imagen BING de {clean_name}: {e}")
                    continue
    except Exception as e:
        import logging
        logging.warning(f"Error API Bing Images search de {clean_name}: {e}")

    return None

def fetch_game_info(game_name, platform_id=None, console_name=""):
    clean_name = clean_rom_name(game_name)
    query      = sanitize_name(clean_name)
    headers    = {"User-Agent": "RetroLauncher/1.1 (https://github.com/)"}
    
    data = {"desc": "", "genres": "—", "year": "—", "rating": 0, "name": game_name}

    def get_wiki_desc(q, lang="es"):
        try:
            url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query", "list": "search", "srsearch": q,
                "format": "json", "utf8": 1, "srlimit": 5
            }
            res = requests.get(url, params=params, headers=headers, timeout=5)
            if res.status_code == 200:
                results = res.json().get("query", {}).get("search", [])
                if not results: return None, 0
                
                best_res = None
                max_sim = -1
                for r in results:
                    title = r["title"]
                    if "(desambiguación)" in title.lower() or "(disambiguation)" in title.lower(): continue
                    sim = name_similarity(clean_name, title)
                    if sim > max_sim:
                        max_sim = sim
                        best_res = r
                
                if best_res and max_sim > 0.35:
                    ext_params = {
                        "action": "query", "prop": "extracts", "exintro": 1,
                        "explaintext": 1, "titles": best_res["title"], "format": "json"
                    }
                    res2 = requests.get(url, params=ext_params, headers=headers, timeout=5)
                    pages = res2.json().get("query", {}).get("pages", {})
                    for _, pdata in pages.items():
                        ext = pdata.get("extract", "")
                        if ext:
                            desc = (ext[:500] + "...") if len(ext) > 500 else ext
                            return {"desc": desc, "name": best_res["title"]}, max_sim
        except Exception as e:
            import logging
            logging.warning(f"Error consultando Wikipedia para {query}: {e}")
        return None, 0

    wiki_data, sim_es = get_wiki_desc(f"{clean_name} {console_name} videojuego", "es")
    
    if not wiki_data or sim_es < 0.6:
        wiki_en, sim_en = get_wiki_desc(f"{clean_name} {console_name} video game", "en")
        if wiki_en and sim_en > sim_es:
            wiki_data = wiki_en
            
    if wiki_data:
        data["desc"] = wiki_data["desc"]
        data["name"] = wiki_data["name"]

    try:
        rawg_url = (f"https://api.rawg.io/api/games?search={quote(query)}"
                    f"&key={RAWG_API_KEY}&page_size=5")
        if platform_id: rawg_url += f"&platforms={platform_id}"
        
        r = requests.get(rawg_url, headers=headers, timeout=5)
        if r.status_code == 200:
            results = r.json().get("results", [])
            scored = sorted([(name_similarity(clean_name, res.get("name","")), res) 
                           for res in results if name_similarity(clean_name, res.get("name","")) > 0.4],
                          key=lambda x: x[0], reverse=True)
            
            if scored:
                g = scored[0][1]
                if not data["desc"]:
                    dr = requests.get(f"https://api.rawg.io/api/games/{g['id']}?key={RAWG_API_KEY}", timeout=5)
                    raw = dr.json().get("description_raw", "") if dr.status_code==200 else ""
                    data["desc"] = (raw[:450] + "...") if len(raw) > 450 else raw
                
                data["genres"] = ", ".join(ge["name"] for ge in g.get("genres", [])[:3])
                data["year"]   = g.get("released", "")[:4] if g.get("released") else "—"
                data["rating"] = g.get("rating", 0)
                if data["name"] == game_name: data["name"] = g.get("name")
    except Exception as e:
        import logging
        logging.warning(f"Error recolectando metadata extra RAWG para {query}: {e}")

    return data if (data["desc"] or data["rating"] > 0) else None

def make_placeholder(game_name, color, size=(300, 200)):
    from PIL import Image, ImageDraw
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
