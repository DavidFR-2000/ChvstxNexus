import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage

from core.config import COLORS, CONSOLES
from ui.workers import RAStatsWorker, AchWorker

class ProfileWorker(RAStatsWorker):
    pass

class ProfileAvatarWorker(AchWorker):
    # Reusing QThread pattern, but for avatar fetching
    pass

class StatsView(QWidget):
    def __init__(self, config, playtime, favorites_count):
        super().__init__()
        self.config = config
        self.playtime = playtime
        self.favs_count = favorites_count
        self.ra_user = config.get("ra_user", "")
        self.ra_apikey = config.get("ra_apikey", "")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"background-color: transparent; border: none;")
        
        self.content = QWidget()
        self.v_layout = QVBoxLayout(self.content)
        self.v_layout.setContentsMargins(50, 20, 50, 40)
        self.v_layout.setAlignment(Qt.AlignTop)
        
        self.build_profile_header()
        self.build_playtime_list()
        
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        
        if self.ra_user and self.ra_apikey:
            self.worker = RAStatsWorker(self.ra_user, self.ra_apikey)
            self.worker.finished.connect(self._on_profile_loaded)
            self.worker.start()

    def build_profile_header(self):
        self.header = QFrame()
        self.header.setObjectName("ContainerBox")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(30, 30, 30, 30)
        h_layout.setSpacing(25)
        
        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(100, 100)
        self.avatar_lbl.setStyleSheet(f"background-color: {COLORS['bg_hover']}; border-radius: 50px;")
        h_layout.addWidget(self.avatar_lbl)
        
        info_w = QWidget()
        i_l = QVBoxLayout(info_w)
        i_l.setContentsMargins(0, 0, 0, 0)
        
        self.name_lbl = QLabel(self.ra_user if self.ra_user else "Jugador Local")
        self.name_lbl.setStyleSheet(f"color: {COLORS['text_bright']}; font-size: 28px; font-weight: 900;")
        i_l.addWidget(self.name_lbl)
        
        self.rank_lbl = QLabel("Sin conexión a RetroAchievements")
        self.rank_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 14px;")
        i_l.addWidget(self.rank_lbl)
        
        h_layout.addWidget(info_w, 1)
        
        # Local Stats inside header right
        loc_w = QWidget()
        l_l = QVBoxLayout(loc_w)
        l_l.setAlignment(Qt.AlignCenter)
        secs = sum(v.get("total_secs", 0) for v in self.playtime.values())
        h, m = divmod(secs // 60, 60)
        l_l.addWidget(QLabel(f"⏱ {h}h {m}m", styleSheet=f"color: {COLORS['accent']}; font-size: 20px; font-weight: bold;"))
        l_l.addWidget(QLabel(f"🎮 {len(self.playtime)} Jugados", styleSheet=f"color: {COLORS['accent']}; font-size: 14px; font-weight: bold;"))
        l_l.addWidget(QLabel(f"⭐ {self.favs_count} Favoritos", styleSheet=f"color: {COLORS['yellow']}; font-size: 14px; font-weight: bold;"))
        h_layout.addWidget(loc_w)
        
        self.v_layout.addWidget(self.header)
        self.v_layout.addSpacing(20)

    def _on_profile_loaded(self, data):
        if not data: return
        pts = data.get("TotalPoints", 0)
        rank = data.get("Rank", "N/A")
        status = data.get("Status", "Desconocido")
        self.rank_lbl.setText(f"🏆 Puntos: {pts}   |   🌍 Rango Global: #{rank}   |   {status}")
        self.rank_lbl.setStyleSheet(f"color: {COLORS['green']}; font-size: 14px; font-weight: bold;")
        
        pic = data.get("UserPic")
        if pic:
            url = f"https://media.retroachievements.org{pic}"
            # Quick sync fetch for avatar (it's very small)
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    img = QImage()
                    img.loadFromData(r.content)
                    pix = QPixmap.fromImage(img)
                    self.avatar_lbl.setPixmap(pix.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                    self.avatar_lbl.setStyleSheet("border-radius: 50px;")
            except Exception as e:
                import logging
                logging.warning(f"Error aplicando radio de borde en avatar: {e}")
            
        self.recent_games = data.get("RecentGames", {})
        self._refresh_playtime_achievements()

    def build_playtime_list(self):
        lbl_top = QLabel("— HISTORIAL Y LOGROS —")
        lbl_top.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 14px; font-weight: bold; margin-top: 10px;")
        self.v_layout.addWidget(lbl_top)
        
        sorted_games = sorted(self.playtime.items(), key=lambda x: x[1].get("total_secs", 0), reverse=True)
        self.game_rows = []
        
        for game_id, data in sorted_games:
            secs = data.get("total_secs", 0)
            h, m = divmod(secs // 60, 60)
            console = data.get("console", "")
            
            row = QFrame()
            row.setObjectName("ContainerBox")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(20, 15, 20, 15)
            
            name_lbl = QLabel(f"{data.get('name', game_id)}")
            name_lbl.setStyleSheet(f"font-weight: bold; color: {COLORS['text_bright']}; font-size: 16px;")
            rl.addWidget(name_lbl, 1)
            
            # Placeholder for dynamic achievements
            ach_lbl = QLabel(f"🎮 {console}")
            ach_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 13px; font-weight: bold;")
            rl.addWidget(ach_lbl)
            
            time_lbl = QLabel(f"⏱ {h}h {m:02d}m")
            time_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 16px; font-weight: bold; margin-left: 20px;")
            rl.addWidget(time_lbl)
            
            self.v_layout.addWidget(row)
            self.game_rows.append({"id": game_id, "name": data.get('name'), "lbl": ach_lbl, "console": console})

    def _refresh_playtime_achievements(self):
        if not hasattr(self, "recent_games"): return
        # Associate RecentGames info with our library names
        for row in self.game_rows:
            # simple match attempt
            name = row["name"].lower()
            best_match = None
            for rg_id, rg_data in self.recent_games.items():
                if name[:10] in rg_data.get("Title", "").lower():
                    best_match = rg_data
                    break
            
            if best_match:
                tot = int(best_match.get("NumPossibleAchievements", 0))
                done = int(best_match.get("NumAwardedToUser", 0))
                if tot > 0:
                    row["lbl"].setText(f"🏆 {done}/{tot} Logros")
                    row["lbl"].setStyleSheet(f"color: {COLORS['green'] if done>0 else COLORS['text_dim']}; font-size: 13px; font-weight: bold;")
