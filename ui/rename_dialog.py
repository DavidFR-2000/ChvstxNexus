import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

from core.config import COLORS
from core.retroarch import ra_get_console_games

class FetchGamesWorker(QThread):
    finished = Signal(list)
    def __init__(self, console_name, user, apikey):
        super().__init__()
        self.console_name = console_name
        self.user = user
        self.apikey = apikey
    def run(self):
        data = ra_get_console_games(self.console_name, self.user, self.apikey)
        self.finished.emit(data or [])

class RenameDialog(QDialog):
    renamed = Signal(str, str) # old_file, new_file

    def __init__(self, current_file, console_name, config, parent=None):
        super().__init__(parent)
        self.current_file = current_file
        self.console_name = console_name
        self.config = config
        self.games_cache = []
        
        self.setWindowTitle("Renombrar Juego (Sincronización RA)")
        self.setFixedSize(450, 480)
        self.setStyleSheet(f"background-color: {COLORS['bg_mid']}; color: {COLORS['text_bright']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl = QLabel(f"Renombrar: {current_file}")
        lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['accent']};")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Escribe para buscar sugerencias exactas...")
        self.input_name.setStyleSheet(f"background-color: {COLORS['bg_dark']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 10px; font-size: 14px;")
        self.input_name.textChanged.connect(self._filter_list)
        layout.addWidget(self.input_name)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"background-color: {COLORS['bg_dark']}; border: 1px solid {COLORS['border']}; border-radius: 6px; outline: none; padding: 5px;")
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self.status_lbl = QLabel("Cargando catálogo oficial de RetroAchievements...")
        self.status_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        layout.addWidget(self.status_lbl)
        
        h_btn = QHBoxLayout()
        h_btn.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(f"background-color: transparent; border: 1px solid {COLORS['text_dim']}; border-radius: 6px; padding: 8px 20px;")
        btn_cancel.clicked.connect(self.reject)
        h_btn.addWidget(btn_cancel)
        
        btn_apply = QPushButton("Aplicar Nombre")
        btn_apply.setStyleSheet(f"background-color: {COLORS['accent']}; color: {COLORS['bg_dark']}; font-weight: bold; border-radius: 6px; padding: 8px 20px;")
        btn_apply.clicked.connect(self.apply_rename)
        h_btn.addWidget(btn_apply)
        
        layout.addLayout(h_btn)
        
        self._fetch_games()

    def _fetch_games(self):
        u = self.config.get("ra_user", "")
        p = self.config.get("ra_apikey", "")
        if not u or not p:
            self.status_lbl.setText("RetroAchievements no configurado. Solo renombrado local.")
            return
            
        self.worker = FetchGamesWorker(self.console_name, u, p)
        self.worker.finished.connect(self._on_games_fetched)
        self.worker.start()

    def _on_games_fetched(self, games):
        self.games_cache = games
        self.status_lbl.setText(f"Catálogo cargado: {len(games)} juegos oficiales encontrados.")
        self._filter_list("")

    def _filter_list(self, text):
        self.list_widget.clear()
        query = text.lower()
        count = 0
        for g in self.games_cache:
            title = g.get("Title", "")
            if query in title.lower():
                item = QListWidgetItem(title)
                self.list_widget.addItem(item)
                count += 1
                if count > 100: break # perf cap

    def _on_item_clicked(self, item):
        self.input_name.setText(item.text())

    def apply_rename(self):
        import re
        new_name = self.input_name.text().strip()
        # Remove invalid Windows filename characters
        new_name = re.sub(r'[\\/*?:"<>|]', '-', new_name).replace('--', '-').strip()
        
        if not new_name:
            QMessageBox.warning(self, "Error", "El nombre es inválido tras limpiar caracteres.")
            return
            
        ext = os.path.splitext(self.current_file)[1]
        new_file = new_name + ext
        
        roms_dir = self.config.get("roms_dir", "")
        old_path = os.path.join(roms_dir, self.console_name, self.current_file)
        new_path = os.path.join(roms_dir, self.console_name, new_file)
        
        if os.path.exists(new_path):
            QMessageBox.warning(self, "Error", "Ya existe un juego con ese nombre.")
            return
            
        try:
            os.rename(old_path, new_path)
            self.renamed.emit(self.current_file, new_file)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo renombrar el archivo:\n{e}")
