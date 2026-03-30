import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QCursor, QPixmap, QColor
from PySide6.QtCore import Qt, Signal, QSize

from core.config import COLORS, CONSOLES
from core.scraper import get_cover_path
from core.utils import sanitize_name
from ui.flow_layout import FlowLayout

class GameCard(QFrame):
    clicked = Signal(str, str) # game_file, console_name
    favorite_toggled = Signal(str, str)

    def __init__(self, game_file, console_name, is_fav, pt_text, covers_cache):
        super().__init__()
        self.game_file = game_file
        self.console_name = console_name
        self.is_fav = is_fav
        self.info = CONSOLES.get(console_name, list(CONSOLES.values())[0])
        self.covers_cache = covers_cache
        
        self.setObjectName("GameCard")
        self.setFixedSize(160, 260)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        
        # Image
        self.img_label = QLabel()
        self.img_label.setFixedSize(144, 200)
        self.img_label.setStyleSheet(f"background-color: {COLORS['bg_card']}; border-radius: 6px;")
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        
        self.load_image()
        
        # Title row
        title_row = QWidget()
        t_layout = QHBoxLayout(title_row)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_layout.setSpacing(2)
        
        name = os.path.splitext(game_file)[0]
        if len(name) > 17: name = name[:15] + "..."
        self.title_lbl = QLabel(name)
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['text_bright']};")
        self.title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        t_layout.addWidget(self.title_lbl, 1)
        
        self.btn_fav = QPushButton("❤" if is_fav else "♡")
        self.btn_fav.setFixedSize(24, 24)
        self.btn_fav.setStyleSheet(f"font-size: 14px; color: {COLORS['red'] if is_fav else COLORS['text_dim']}; background: transparent; padding: 0px;")
        self.btn_fav.clicked.connect(self.toggle_fav)
        t_layout.addWidget(self.btn_fav)
        
        layout.addWidget(title_row)
        
        # Console badge & playtime
        bottom_row = QWidget()
        b_layout = QHBoxLayout(bottom_row)
        b_layout.setContentsMargins(0, 0, 0, 0)
        
        badge = QLabel(self.info['emoji'])
        badge.setStyleSheet(f"font-size: 10px; color: {self.info['color']};")
        b_layout.addWidget(badge)
        
        b_layout.addStretch()
        
        pt_lbl = QLabel(pt_text)
        pt_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 10px; font-weight: bold;")
        b_layout.addWidget(pt_lbl)
        
        layout.addWidget(bottom_row)

    def load_image(self):
        name = os.path.splitext(self.game_file)[0]
        path = get_cover_path(self.covers_cache, name)
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.img_label.setPixmap(pix.scaled(144, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                return
                
        self.img_label.setText("Cargando...")
        self.img_label.setStyleSheet(f"color: {COLORS['text_dim']}; background-color: {COLORS['bg_mid']}; border-radius: 6px;")
        
        from ui.workers import CoverDownloadWorker
        self.worker = CoverDownloadWorker(name, self.covers_cache, self.info.get("rawg_platform"), self.console_name)
        self.worker.finished.connect(self._on_cover_downloaded)
        self.worker.start()
        
    def _on_cover_downloaded(self, name, path):
        if path and os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.img_label.setPixmap(pix.scaled(144, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                self.img_label.setStyleSheet(f"background-color: transparent;")
        else:
            self.img_label.setText("No Cover")

    def toggle_fav(self):
        self.is_fav = not self.is_fav
        self.btn_fav.setText("❤" if self.is_fav else "♡")
        self.btn_fav.setStyleSheet(f"font-size: 14px; color: {COLORS['red'] if self.is_fav else COLORS['text_dim']}; background: transparent; padding: 0px;")
        self.favorite_toggled.emit(self.game_file, self.console_name)

    def enterEvent(self, event):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        c = QColor(COLORS["accent"])
        c.setAlpha(180)
        shadow.setColor(c)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setGraphicsEffect(None)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game_file, self.console_name)


class LibraryView(QWidget):
    game_selected = Signal(str, str)
    favorite_toggled = Signal(str, str)

    def __init__(self, config, playtime):
        super().__init__()
        self.config = config
        self.playtime = playtime
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content_widget = QWidget()
        self.content_layout = FlowLayout(self.content_widget, margin=25, hSpacing=15, vSpacing=20)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

    def clear(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def render_games(self, games, console_name):
        self.clear()
        
        if not games:
            lbl = QLabel("No se encontraron juegos.")
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(lbl)
            return

        favs = self.config.get("favorites", [])
        cache = self.config.get("covers_cache", "")
        
        for gf in games:
            is_fav = any(f["file"] == gf and f["console"] == console_name for f in favs)
            game_id = f"{console_name}::{gf}"
            secs = self.playtime.get(game_id, {}).get("total_secs", 0)
            h, m = divmod(secs // 60, 60)
            pt_text = f"⌛ {h}h {m:02d}m" if secs > 0 else "NUEVO"
            
            card = GameCard(gf, console_name, is_fav, pt_text, cache)
            card.clicked.connect(self.game_selected.emit)
            card.favorite_toggled.connect(self.favorite_toggled.emit)
            self.content_layout.addWidget(card)
