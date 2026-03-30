import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QWidget, QProgressDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

from core.config import COLORS, CONSOLES
from core.scraper import get_cover_path, fetch_game_info
from core.bios import BiosDownloadWorker, needs_bios

class GameDialog(QDialog):
    launch_game = Signal(str, str)
    toggle_fav = Signal(str, str)
    rename_game = Signal(str, str)
    reload_cover = Signal(str, str)

    def __init__(self, game_file, console_name, config, playtime, parent=None):
        super().__init__(parent)
        self.game_file = game_file
        self.console_name = console_name
        self.config = config
        self.playtime = playtime
        self.name = os.path.splitext(game_file)[0]
        self.info = CONSOLES.get(console_name, list(CONSOLES.values())[0])
        
        self.setWindowTitle(self.name)
        self.setFixedSize(700, 530)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_bright']}; font-family: 'Courier New';")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left Panel
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        v_left = QVBoxLayout(left_panel)
        v_left.setContentsMargins(0, 0, 0, 0)
        
        self.cover_lbl = QLabel()
        self.cover_lbl.setFixedSize(260, 180)
        self.cover_lbl.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-radius: 8px;")
        self.cover_lbl.setAlignment(Qt.AlignCenter)
        self.load_cover()
        v_left.addWidget(self.cover_lbl)
        
        console_lbl = QLabel(f"{self.info['emoji']} {console_name}")
        console_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.info['color']};")
        v_left.addWidget(console_lbl)
        
        game_id = f"{console_name}::{game_file}"
        pt = playtime.get(game_id, {})
        secs = pt.get("total_secs", 0)
        h, m = divmod(secs // 60, 60)
        sessions = pt.get("sessions", 0)
        
        v_left.addWidget(QLabel(f"⏱  {h}h {m:02d}m jugados", styleSheet=f"color: {COLORS['text_dim']}; font-size: 12px;"))
        v_left.addWidget(QLabel(f"🎮  {sessions} sesiones", styleSheet=f"color: {COLORS['text_dim']}; font-size: 12px;"))
        
        self.ach_summary_lbl = QLabel("🏆 Logros: Verificando...")
        self.ach_summary_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px; font-weight: bold; margin-top: 10px; margin-bottom: 10px;")
        v_left.addWidget(self.ach_summary_lbl)
        
        self.is_fav = any(f["file"] == game_file and f["console"] == console_name for f in config.get("favorites", []))
        self.fav_btn = QPushButton("★ En favoritos" if self.is_fav else "☆ Añadir a favoritos")
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                color: {COLORS['yellow'] if self.is_fav else COLORS['text_dim']};
            }}
            QPushButton:hover {{ background-color: {COLORS['bg_hover']}; }}
        """)
        self.fav_btn.clicked.connect(self._on_fav_clicked)
        v_left.addWidget(self.fav_btn)
        
        v_left.addStretch()
        layout.addWidget(left_panel)
        
        # Right Panel
        right_panel = QWidget()
        v_right = QVBoxLayout(right_panel)
        v_right.setContentsMargins(20, 0, 0, 0)
        
        title_lbl = QLabel(self.name)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_lbl.setWordWrap(True)
        v_right.addWidget(title_lbl)
        
        # Info box
        self.info_box = QFrame()
        self.info_box.setObjectName("ContainerBox")
        v_info = QVBoxLayout(self.info_box)
        
        self.desc_lbl = QLabel("Cargando información...")
        self.desc_lbl.setStyleSheet(f"color: {COLORS['text_dim']};")
        self.desc_lbl.setWordWrap(True)
        v_info.addWidget(self.desc_lbl)
        
        self.fetch_game_info()
        
        v_right.addWidget(self.info_box)
        v_right.addStretch()
        
        # Buttons
        play_btn = QPushButton("▶  JUGAR AHORA")
        play_btn.setObjectName("PlayButton")
        play_btn.setFixedHeight(46)
        play_btn.setStyleSheet(f"""
            QPushButton#PlayButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
                font-size: 15px; font-weight: bold; border-radius: 12px;
            }}
            QPushButton#PlayButton:hover {{ background-color: {COLORS['accent2']}; }}
        """)
        play_btn.clicked.connect(self._on_play_clicked)
        v_right.addWidget(play_btn)
        
        btn_style = f"QPushButton {{ border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 6px; color: {COLORS['text_dim']}; }} QPushButton:hover {{ background-color: {COLORS['bg_hover']}; }}"
        
        ren_btn = QPushButton("✏  Renombrar")
        ren_btn.setStyleSheet(btn_style)
        ren_btn.clicked.connect(self._on_rename_clicked)
        v_right.addWidget(ren_btn)
        
        ach_btn = QPushButton("🏆  Ver logros (RetroAchievements)")
        ach_btn.setStyleSheet(f"QPushButton {{ border: 1px solid {COLORS['accent']}; border-radius: 8px; padding: 6px; color: {COLORS['accent']}; }} QPushButton:hover {{ background-color: {COLORS['bg_hover']}; }}")
        ach_btn.clicked.connect(self._open_achievements)
        v_right.addWidget(ach_btn)
        
        rel_btn = QPushButton("🖼️  Recargar Carátula")
        rel_btn.setStyleSheet(btn_style)
        rel_btn.clicked.connect(lambda: (self.accept(), self.reload_cover.emit(game_file, console_name)))
        v_right.addWidget(rel_btn)
        
        layout.addWidget(right_panel, 1)

    def _on_play_clicked(self):
        retroarch_path = self.config.get("retroarch_path", "")
        retroarch_dir = os.path.dirname(retroarch_path) if retroarch_path else ""
        system_dir = os.path.join(retroarch_dir, "system") if retroarch_dir else "system"
        if needs_bios(self.console_name, system_dir):
            self.progress_dlg = QProgressDialog("Verificando BIOS...", "Cancelar", 0, 100, self)
            self.progress_dlg.setWindowTitle("Descarga de BIOS")
            self.progress_dlg.setWindowModality(Qt.WindowModal)
            self.progress_dlg.setMinimumDuration(0)
            self.progress_dlg.canceled.connect(self._on_bios_cancel)
            
            self.bios_worker = BiosDownloadWorker(self.console_name, system_dir)
            self.bios_worker.progress.connect(self._on_bios_progress)
            self.bios_worker.finished.connect(self._on_bios_finish)
            self.bios_worker.start()
        else:
            self._trigger_launch()

    def _on_bios_cancel(self):
        if hasattr(self, "bios_worker"):
            self.bios_worker.terminate()

    def _on_bios_progress(self, msg, pct):
        self.progress_dlg.setLabelText(msg)
        self.progress_dlg.setValue(pct)

    def _on_bios_finish(self, success, msg):
        self.progress_dlg.close()
        if success:
            self._trigger_launch()
        else:
            QMessageBox.critical(self, "Error BIOS", msg)

    def _trigger_launch(self):
        self.launch_game.emit(self.game_file, self.console_name)
        self.accept()

    def _on_rename_clicked(self):
        from ui.rename_dialog import RenameDialog
        dlg = RenameDialog(self.game_file, self.console_name, self.config, self)
        if dlg.exec():
            self.accept()
            self.rename_game.emit(self.game_file, self.console_name)

    def _open_achievements(self):
        from ui.achievements_dialog import AchievementsDialog
        dlg = AchievementsDialog(self.game_file, self.console_name, self.config, self)
        dlg.exec()

    def load_cover(self):
        cache = self.config.get("covers_cache", "")
        path = get_cover_path(cache, self.name)
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.cover_lbl.setPixmap(pix.scaled(260, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        self.cover_lbl.setText("No Cover")

    def _on_fav_clicked(self):
        self.is_fav = not self.is_fav
        self.fav_btn.setText("★ En favoritos" if self.is_fav else "☆ Añadir a favoritos")
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                color: {COLORS['yellow'] if self.is_fav else COLORS['text_dim']};
            }}
            QPushButton:hover {{ background-color: {COLORS['bg_hover']}; }}
        """)
        self.toggle_fav.emit(self.game_file, self.console_name)

    def fetch_game_info(self):
        from ui.workers import GameInfoWorker
        self.info_worker = GameInfoWorker(self.name, self.info.get("rawg_platform"), self.console_name)
        self.info_worker.finished.connect(self._update_info)
        self.info_worker.start()
        
        self.fetch_achievements_summary()

    def fetch_achievements_summary(self):
        u = self.config.get("ra_user", "")
        p = self.config.get("ra_apikey", "")
        if not u or not p:
            self.ach_summary_lbl.setText("🏆 Logros: No configurado")
            return
        
        from ui.achievements_dialog import AchWorker
        self.ach_worker = AchWorker(self.name, self.console_name, u, p)
        self.ach_worker.finished.connect(self._on_ach_summary)
        self.ach_worker.start()

    def _on_ach_summary(self, achs):
        if not achs:
            self.ach_summary_lbl.setText("🏆 Logros: No soportado")
            return
        unlocked = sum(1 for a in achs if a["unlocked"])
        self.ach_summary_lbl.setText(f"🏆 Logros: {unlocked}/{len(achs)} Completados")
        self.ach_summary_lbl.setStyleSheet(f"color: {COLORS['green'] if unlocked > 0 else COLORS['accent']}; font-size: 12px; font-weight: bold; margin-top: 10px; margin-bottom: 10px;")

    def _update_info(self, data):
        if data:
            text = f"<b>AÑO:</b> {data['year']}<br>" \
                   f"<b>GÉNEROS:</b> {data['genres']}<br>" \
                   f"<b>RATING:</b> {'⭐'*int(round(float(data['rating'])))} ({float(data['rating']):.1f}/5) <br><br>" \
                   f"{data['desc']}"
            self.desc_lbl.setText(text)
        else:
            self.desc_lbl.setText("No se encontró información en línea.")
