import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from core.config import COLORS
from core.retroarch import ra_search_game, ra_get_achievements, ra_get_badge_image

# Prevenir crash si se cierra la ventana durante una descarga (los QThreads no se deben destruir si están corriendo)
_global_detached_workers = []

class AchWorker(QThread):
    finished = Signal(list)

    
    def __init__(self, game_name, console_name, user, apikey):
        super().__init__()
        self.game_name = game_name
        self.console_name = console_name
        self.user = user
        self.apikey = apikey
        
    def run(self):
        game_id = ra_search_game(self.game_name, self.console_name, self.user, self.apikey)
        if game_id:
            achs = ra_get_achievements(game_id, self.user, self.apikey)
            self.finished.emit(achs if achs else [])
        else:
            self.finished.emit([])

class BadgeWorker(QThread):
    finished = Signal(str, object)
    
    def __init__(self, ach_id, url, unlocked):
        super().__init__()
        self.ach_id = ach_id
        self.url = url
        self.unlocked = unlocked
        
    def run(self):
        img_pil = ra_get_badge_image(self.url, self.unlocked)
        self.finished.emit(self.ach_id, img_pil)

class AchievementsDialog(QDialog):
    def __init__(self, game_file, console_name, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.name = os.path.splitext(game_file)[0]
        self.console_name = console_name
        
        self.setWindowTitle(f"Logros: {self.name}")
        self.setFixedSize(650, 600)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_bright']}; font-family: 'Segoe UI';")
        
        layout = QVBoxLayout(self)
        
        title = QLabel(f"🏆 Logros de {self.name}")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['accent']};")
        layout.addWidget(title)
        
        self.status = QLabel("Buscando logros en RetroAchievements...")
        self.status.setStyleSheet(f"color: {COLORS['text_dim']}; font-style: italic;")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.scroll.hide()
        
        self.content = QWidget()
        self.v_layout = QVBoxLayout(self.content)
        self.v_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.content)
        
        layout.addWidget(self.scroll, 1)
        
        # Iniciar busqueda
        u = self.config.get("ra_user", "")
        p = self.config.get("ra_apikey", "")
        if not u or not p:
            self.status.setText("Usuario o API Key de RetroAchievements no configurados.\nVe a Ajustes para configurarlo.")
            return
            
        self.worker = AchWorker(self.name, self.console_name, u, p)
        self.worker.finished.connect(self.on_achievements_loaded)
        self.worker.start()

    def on_achievements_loaded(self, achs):
        if not achs:
            self.status.setText("No se encontraron logros para este juego.")
            return
            
        self.status.hide()
        self.scroll.show()
        
        unlocked_count = sum(1 for a in achs if a["unlocked"])
        total_pts = sum(int(a.get("points", 0)) for a in achs if a["unlocked"])
        
        summary = QLabel(f"Progreso: {unlocked_count}/{len(achs)} logros desbloqueados ({total_pts} PTS)")
        summary.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['green']}; margin-bottom: 10px;")
        self.v_layout.addWidget(summary)
        
        self.badge_labels = {}
        self.active_workers = []
        
        for a in achs:
            box = QFrame()
            box.setObjectName("ContainerBox")
            box.setStyleSheet(f"QFrame#ContainerBox {{ background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['accent'] if a['unlocked'] else COLORS['border']}; border-radius: 8px; }}")
            
            h_layout = QHBoxLayout(box)
            h_layout.setContentsMargins(15, 15, 15, 15)
            
            badge = QLabel()
            badge.setFixedSize(48, 48)
            badge.setStyleSheet("background-color: transparent;")
            h_layout.addWidget(badge)
            self.badge_labels[a["id"]] = badge
            
            info = QWidget()
            v_info = QVBoxLayout(info)
            v_info.setContentsMargins(0, 0, 0, 0)
            
            t = QLabel(a['title'])
            t.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_bright'] if a['unlocked'] else COLORS['text_dim']};")
            v_info.addWidget(t)
            
            d = QLabel(a['description'])
            d.setStyleSheet(f"font-size: 12px; color: {COLORS['text_dim']};")
            d.setWordWrap(True)
            v_info.addWidget(d)
            
            if a["unlocked"] and a["date_earned"]:
                dt = QLabel(f"Obtenido: {a['date_earned']}")
                dt.setStyleSheet(f"font-size: 11px; color: {COLORS['green']}; font-weight: bold;")
                v_info.addWidget(dt)
                
            h_layout.addWidget(info, 1)
            
            pts = QLabel(f"{a['points']} PTS")
            pts.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['yellow']};")
            h_layout.addWidget(pts)
            
            self.v_layout.addWidget(box)
            
            bw = BadgeWorker(a["id"], a["badge_url"], a["unlocked"])
            bw.finished.connect(self.on_badge_loaded)
            self.active_workers.append(bw)
            bw.start()

    def on_badge_loaded(self, ach_id, img_pil):
        if not img_pil: return
        try:
            from PySide6.QtGui import QImage, QPixmap
            data = img_pil.tobytes("raw", "RGBA")
            qim = QImage(data, img_pil.size[0], img_pil.size[1], QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qim)
            if ach_id in self.badge_labels:
                self.badge_labels[ach_id].setPixmap(pix)
        except:
            pass

    def reject(self):
        global _global_detached_workers
        if hasattr(self, "worker"):
            self.worker.finished.disconnect()
            _global_detached_workers.append(self.worker)
            
        for w in getattr(self, "active_workers", []):
            try: w.finished.disconnect()
            except: pass
            _global_detached_workers.append(w)
            
        super().reject()
