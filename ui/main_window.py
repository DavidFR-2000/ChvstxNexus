import os
import sys
import subprocess
import time
import datetime
import threading
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QScrollArea, QFrame, QMessageBox, QScroller
)
from PySide6.QtCore import Qt, QTimer, Signal

from core.config import COLORS, CONSOLES, RA_CORES, load_config, save_config, load_playtime, save_playtime
from ui.library_view import LibraryView
from ui.settings_view import SettingsView
from ui.stats_view import StatsView
from ui.game_dialog import GameDialog
from ui.downloader_view import DownloaderView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.playtime = load_playtime()
        self.current_console = None
        self.games_list = []
        
        self.setWindowTitle("Chvstx Nexus")
        self.resize(1460, 900)
        self.setMinimumSize(1100, 700)
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._build_top_nav()
        
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_stack, 1)
        
        self.current_view_widget = None
        self.active_downloads = []
        self._build_downloads_panel()
        
        active = self.config.get("active_consoles", [])
        if active and active[0] in CONSOLES:
            self.select_console(active[0])
        else:
            self.open_settings()
            
        self._check_updates()

    def _build_top_nav(self):
        self.nav = QWidget()
        self.nav.setObjectName("TopNav")
        self.nav.setFixedHeight(80)
        nav_layout = QHBoxLayout(self.nav)
        nav_layout.setContentsMargins(40, 15, 40, 15)
        nav_layout.setSpacing(35)
        
        # Logo
        logo_lbl = QLabel("CHVSTX NEXUS")
        logo_lbl.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {COLORS['text_bright']}; letter-spacing: 2px;")
        nav_layout.addWidget(logo_lbl)
        
        # Categories
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(65)
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QScroller.grabGesture(self.cat_scroll.viewport(), QScroller.LeftMouseButtonGesture)
        
        self.cat_content = QWidget()
        self.cat_layout = QHBoxLayout(self.cat_content)
        self.cat_layout.setContentsMargins(0, 5, 0, 5)
        
        self.console_buttons = {}
        self._populate_consoles()
        
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setWidget(self.cat_content)
        nav_layout.addWidget(self.cat_scroll, 1)
        
        # Actions
        actions = QWidget()
        act_layout = QHBoxLayout(actions)
        act_layout.setContentsMargins(0,0,0,0)
        act_layout.setSpacing(15)
        
        self.fav_btn = QPushButton("⭐")
        self.fav_btn.setObjectName("NavAction")
        self.fav_btn.setToolTip("Favoritos")
        self.fav_btn.setStyleSheet(f"font-size: 20px; background-color: {COLORS['bg_card']}; border-radius: 20px; width: 40px; height: 40px;")
        self.fav_btn.clicked.connect(self.show_favorites)
        act_layout.addWidget(self.fav_btn)
        
        self.stat_btn = QPushButton("📊")
        self.stat_btn.setObjectName("NavAction")
        self.stat_btn.setToolTip("Estadísticas")
        self.stat_btn.setStyleSheet(f"font-size: 20px; background-color: {COLORS['bg_card']}; border-radius: 20px; width: 40px; height: 40px;")
        self.stat_btn.clicked.connect(self.show_stats)
        act_layout.addWidget(self.stat_btn)
        
        self.hub_btn = QPushButton("🌐")
        self.hub_btn.setObjectName("NavAction")
        self.hub_btn.setToolTip("Hub de Descargas")
        self.hub_btn.setStyleSheet(f"font-size: 20px; background-color: {COLORS['bg_card']}; border-radius: 20px; width: 40px; height: 40px; color: {COLORS['accent']};")
        self.hub_btn.clicked.connect(self.show_hub)
        act_layout.addWidget(self.hub_btn)
        
        self.set_btn = QPushButton("⚙")
        self.set_btn.setObjectName("NavAction")
        self.set_btn.setToolTip("Ajustes")
        self.set_btn.setStyleSheet(f"font-size: 20px; background-color: {COLORS['bg_card']}; border-radius: 20px; width: 40px; height: 40px;")
        self.set_btn.clicked.connect(self.open_settings)
        act_layout.addWidget(self.set_btn)
        
        nav_layout.addWidget(actions)
        self.main_layout.addWidget(self.nav)

    def _populate_consoles(self):
        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        self.console_buttons.clear()
        for c in self.config.get("active_consoles", []):
            if c not in CONSOLES: continue
            info = CONSOLES[c]
            btn = QPushButton(f"{info['emoji']} {c}")
            btn.setStyleSheet(f"font-size: 14px; color: {COLORS['text_dim']}; font-weight: bold;")
            btn.clicked.connect(lambda checked, name=c: self.select_console(name))
            self.cat_layout.addWidget(btn)
            self.console_buttons[c] = btn
        self.cat_layout.addStretch()

    def set_content(self, widget):
        if self.current_view_widget:
            self.current_view_widget.setParent(None)
            self.current_view_widget.deleteLater()
        self.current_view_widget = widget
        self.content_layout.addWidget(self.current_view_widget)

    def select_console(self, name):
        self.current_console = name
        for c, btn in self.console_buttons.items():
            if c == name:
                btn.setObjectName("ConsoleButtonActive")
                btn.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['accent']}; background-color: {COLORS['bg_card']}; border: 2px solid {COLORS['accent']}; border-radius: 16px; padding: 6px 18px;")
            else:
                btn.setObjectName("")
                btn.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_dim']}; border: none; background: transparent; padding: 6px 18px;")
        
        # Load View
        view = LibraryView(self.config, self.playtime)
        view.game_selected.connect(self.open_game_dialog)
        view.favorite_toggled.connect(self.toggle_favorite)
        self.set_content(view)
        
        self.filter_games()

    def show_favorites(self):
        self.current_console = None
        for c, btn in self.console_buttons.items():
            btn.setObjectName("")
            btn.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_dim']}; border: none; background: transparent; padding: 6px 18px;")
            
        view = LibraryView(self.config, self.playtime)
        view.game_selected.connect(self.open_game_dialog)
        view.favorite_toggled.connect(self.toggle_favorite)
        self.set_content(view)
        
        favs = self.config.get("favorites", [])
        games = [f["file"] for f in favs]
        console_map = {f["file"]: f["console"] for f in favs}
        
        # Render multiple consoles mixed (LibraryView supports this by receiving console_name via override or loop)
        # Because we need different consoles, we will re-implement a _render_favorites method in our logic
        view.clear()
        
        if not favs:
            lbl = QLabel("No tienes favoritos aún.\nPulsa ★ en cualquier juego para añadirlo.")
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            view.content_layout.addWidget(lbl)
            return

        from ui.library_view import GameCard
        cache = self.config.get("covers_cache", "")
        for f in favs:
            gf = f["file"]
            cn = f["console"]
            game_id = f"{cn}::{gf}"
            secs = self.playtime.get(game_id, {}).get("total_secs", 0)
            h, m = divmod(secs // 60, 60)
            pt_text = f"⌛ {h}h {m:02d}m" if secs > 0 else "⌛ NEW"
            
            card = GameCard(gf, cn, True, pt_text, cache)
            card.clicked.connect(self.open_game_dialog)
            card.favorite_toggled.connect(self.toggle_favorite)
            view.content_layout.addWidget(card)

    def show_stats(self):
        self.current_console = None
        for c, btn in self.console_buttons.items():
            btn.setObjectName("")
            btn.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_dim']}; border: none; background: transparent; padding: 6px 18px;")
        
        view = StatsView(self.config, self.playtime, len(self.config.get("favorites", [])))
        self.set_content(view)

    def show_hub(self):
        self.current_console = None
        for c, btn in self.console_buttons.items():
            btn.setObjectName("")
            btn.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['text_dim']}; border: none; background: transparent; padding: 6px 18px;")
        
        view = DownloaderView(self)
        self.set_content(view)

    def open_settings(self):
        view = SettingsView(self.config)
        view.close_requested.connect(self._close_settings)
        view.config_saved.connect(self._reload_settings)
        self.set_content(view)

    def _close_settings(self):
        active = self.config.get("active_consoles", [])
        if self.current_console in active:
            self.select_console(self.current_console)
        elif active and active[0] in CONSOLES:
            self.select_console(active[0])
        else:
            self.show_favorites()

    def _reload_settings(self):
        self._populate_consoles()
        self._close_settings()

    def filter_games(self):
        if not getattr(self, "current_console", None): return
        if not isinstance(self.current_view_widget, LibraryView): return
        
        info = CONSOLES[self.current_console]
        dir_path = os.path.join(self.config.get("roms_dir", ""), self.current_console)
        
        games = []
        if os.path.isdir(dir_path):
            for root, _, files in os.walk(dir_path):
                for f in files:
                    if os.path.splitext(f)[1].lower() in info["extensions"]:
                        rel_path = os.path.relpath(os.path.join(root, f), dir_path)
                        # Ensure cross-platform slashes for saved favorites/playtime ID mapping
                        rel_path = rel_path.replace("\\", "/")
                        games.append(rel_path)
                        
        self.games_list = sorted(games)
        self.current_view_widget.render_games(self.games_list, self.current_console)

    def toggle_favorite(self, game_file, console_name):
        favs = self.config.setdefault("favorites", [])
        match = next((f for f in favs if f["file"] == game_file and f["console"] == console_name), None)
        if match:
            favs.remove(match)
        else:
            favs.append({"file": game_file, "console": console_name})
        save_config(self.config)

    def open_game_dialog(self, game_file, console_name):
        dialog = GameDialog(game_file, console_name, self.config, self.playtime, self)
        dialog.launch_game.connect(self.launch_game)
        dialog.toggle_fav.connect(self.toggle_favorite)
        dialog.reload_cover.connect(self.reload_cover)
        dialog.rename_game.connect(self.rename_game)
        dialog.exec()

    def reload_cover(self, game_file, console_name):
        cache = self.config.get("covers_cache", "")
        from core.utils import sanitize_name
        import os
        name = os.path.splitext(game_file)[0]
        path = os.path.join(cache, f"{sanitize_name(name)}.jpg")
        if os.path.exists(path):
            try: os.remove(path)
            except: pass
            
        from ui.workers import CoverDownloadWorker
        info = CONSOLES.get(console_name, {})
        self.cover_worker = CoverDownloadWorker(name, cache, info.get("rawg_platform"), console_name)
        
        def on_download_done(n, p):
            if self.current_console == console_name:
                self.filter_games()
            else:
                self.show_favorites()
                
        self.cover_worker.finished.connect(on_download_done)
        self.cover_worker.start()

    def rename_game(self, game_file, console_name):
        if self.current_console == console_name:
            self.filter_games()
        else:
            self.show_favorites()

    def launch_game(self, game_file, console_name):
        retroarch = self.config.get("retroarch_path", "")
        cores_dir = self.config.get("cores_dir", "")

        if not retroarch or not os.path.exists(retroarch):
            QMessageBox.warning(self, "RetroArch no encontrado", "Verifica la ruta en Configuración.")
            return

        available_cores = RA_CORES.get(console_name, [])
        if not available_cores: return

        core_prefs = self.config.get("core_preferences", {})
        preferred = core_prefs.get(console_name)
        core_file = preferred if preferred in available_cores else available_cores[0]

        core_path = os.path.join(cores_dir, core_file)
        if not os.path.exists(core_path):
            QMessageBox.warning(self, "Core no instalado", f"Falta el core {core_file}.")
            return

        rom_path = os.path.join(self.config.get("roms_dir", ""), console_name, game_file)
        if not os.path.exists(rom_path):
            QMessageBox.warning(self, "ROM no encontrada", f"No se encontró: {rom_path}")
            return

        game_id = f"{console_name}::{game_file}"
        name = os.path.splitext(game_file)[0]
        start_time = time.time()

        import threading
        def monitor(proc):
            proc.wait()
            elapsed = int(time.time() - start_time)
            entry = self.playtime.setdefault(game_id, {"total_secs": 0, "sessions": 0})
            entry["total_secs"] += elapsed
            entry["sessions"] += 1
            entry["last_played"] = datetime.datetime.now().isoformat()
            entry["console"] = console_name
            entry["name"] = name
            save_playtime(self.playtime)

        try:
            cwd = os.path.dirname(retroarch)
            proc = subprocess.Popen([retroarch, "-L", core_path, rom_path], cwd=cwd)
            threading.Thread(target=monitor, args=(proc,), daemon=True).start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al lanzar RetroArch:\n{e}")

    def _build_downloads_panel(self):
        self.dl_panel = QWidget()
        self.dl_panel.setFixedHeight(250)
        self.dl_panel.setStyleSheet(f"border-top: 2px solid {COLORS['border']}; background-color: {COLORS['bg_mid']};")
        
        lay = QVBoxLayout(self.dl_panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: none;")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(15, 0, 15, 0)
        title = QLabel("📥 GESTOR DE DESCARGAS")
        title.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {COLORS['accent2']};")
        h_lay.addWidget(title)
        
        close_btn = QPushButton("Ocultar")
        close_btn.setStyleSheet(f"color: {COLORS['text_dim']}; border: none; font-size: 11px;")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.dl_panel.hide)
        h_lay.addWidget(close_btn)
        
        lay.addWidget(header)
        
        self.dl_scroll = QScrollArea()
        self.dl_scroll.setWidgetResizable(True)
        self.dl_scroll.setStyleSheet("border: none; background: transparent;")
        
        self.dl_container = QWidget()
        self.dl_container.setStyleSheet("background: transparent;")
        self.dl_layout = QVBoxLayout(self.dl_container)
        self.dl_layout.setContentsMargins(15, 15, 15, 15)
        self.dl_layout.setSpacing(10)
        self.dl_layout.addStretch()
        
        self.dl_scroll.setWidget(self.dl_container)
        lay.addWidget(self.dl_scroll)
        
        self.main_layout.addWidget(self.dl_panel)
        self.dl_panel.hide()

    def _create_transfer_row(self, title, dest_console, worker):
        import PySide6.QtWidgets as QtWidgets
        row = QtWidgets.QFrame()
        row.setStyleSheet(f"background-color: {COLORS['bg_dark']}; border: 1px solid {COLORS['border']}; border-radius: 8px;")
        row.setFixedHeight(75)
        
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(15, 10, 15, 10)
        
        info_lay = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(f"{title}")
        name_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {COLORS['text_bright']}; border: none;")
        
        status_lbl = QtWidgets.QLabel(f"Preparando descarga a {dest_console}...")
        status_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']}; border: none;")
        
        info_lay.addWidget(name_lbl)
        info_lay.addWidget(status_lbl)
        info_lay.addStretch()
        layout.addLayout(info_lay, stretch=3)
        
        prog_lay = QtWidgets.QVBoxLayout()
        from PySide6.QtWidgets import QProgressBar
        p_bar = QProgressBar()
        p_bar.setFixedHeight(8)
        p_bar.setTextVisible(False)
        p_bar.setStyleSheet(f"QProgressBar {{ background-color: {COLORS['bg_mid']}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {COLORS['accent']}; border-radius: 4px; }}")
        
        speed_lbl = QtWidgets.QLabel("0.0 B/s")
        speed_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['accent2']}; border: none; font-weight: bold;")
        speed_lbl.setAlignment(Qt.AlignRight)
        
        prog_lay.addStretch()
        prog_lay.addWidget(p_bar)
        prog_lay.addWidget(speed_lbl)
        prog_lay.addStretch()
        layout.addLayout(prog_lay, stretch=2)
        
        layout.addSpacing(10)
        cancel_btn = QPushButton("✕")
        cancel_btn.setFixedSize(30, 30)
        cancel_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; border: 1px solid {COLORS['border']}; color: {COLORS['text_dim']}; font-weight: bold; font-size: 14px; border-radius: 15px; }} QPushButton:hover {{ background-color: {COLORS['bg_hover']}; color: {COLORS['red']}; border-color: {COLORS['red']}; }}")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: getattr(worker, 'cancel')())
        layout.addWidget(cancel_btn)
        
        return row, name_lbl, status_lbl, p_bar, speed_lbl, cancel_btn

    def start_download(self, url, dest_dir, title, repo, exts, dest_console):
        from ui.workers import HubDownloadWorker
        worker = HubDownloadWorker(url, dest_dir, title, repo, exts)
        row_widget, name_lbl, status_lbl, p_bar, speed_lbl, cancel_btn = self._create_transfer_row(title, dest_console, worker)
        
        self.dl_layout.insertWidget(self.dl_layout.count() - 1, row_widget)
        self.dl_panel.show()
        
        self.active_downloads.append((worker, row_widget))
        
        worker.progress.connect(lambda pct, dmb, tmb, spd, pb=p_bar, sl=status_lbl, sp=speed_lbl: self._update_transfer_progress(pb, sl, sp, pct, dmb, tmb, spd))
        worker.finished.connect(lambda succ, msg, w=worker, rw=row_widget, sl=status_lbl, pb=p_bar, sp=speed_lbl, cb=cancel_btn: self._on_transfer_finished(w, rw, sl, pb, sp, cb, succ, msg))
        
        worker.start()

    def _update_transfer_progress(self, p_bar, status_lbl, speed_lbl, pct, downloaded_mb, total_mb, speed_str):
        p_bar.setValue(int(pct * 100))
        status_lbl.setText(f"Descargando... {downloaded_mb:.1f} MB / {total_mb:.1f} MB")
        speed_lbl.setText(speed_str)

    def _on_transfer_finished(self, worker, row_widget, status_lbl, p_bar, speed_lbl, cancel_btn, success, msg):
        speed_lbl.setText("")
        cancel_btn.hide()
        
        if worker in [w for w, r in self.active_downloads]:
            self.active_downloads = [(w, r) for w, r in self.active_downloads if w != worker]
            
        if success:
            p_bar.setValue(100)
            p_bar.setStyleSheet(f"QProgressBar {{ background-color: {COLORS['bg_mid']}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {COLORS['green']}; border-radius: 4px; }}")
            status_lbl.setText(f"✓ {msg}")
            status_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['green']}; border: none;")
            from ui.library_view import LibraryView
            if isinstance(self.current_view_widget, LibraryView):
                self.filter_games()
            
            QTimer.singleShot(3000, lambda: self._check_hide_dl_panel(row_widget))
        else:
            p_bar.setStyleSheet(f"QProgressBar {{ background-color: {COLORS['bg_mid']}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {COLORS['red']}; border-radius: 4px; }}")
            status_lbl.setText(f"✗ {msg}")
            status_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['red']}; border: none;")

    def _check_hide_dl_panel(self, row_widget):
        row_widget.deleteLater()
        if not self.active_downloads:
            self.dl_panel.hide()

    def _check_updates(self):
        from ui.workers import UpdateWorker
        self.update_w = UpdateWorker()
        self.update_w.update_available.connect(self._on_update_available)
        self.update_w.start()

    def _on_update_available(self, version, notes, dl_url):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Actualización Disponible", 
                                     f"¡Hay una nueva versión de Chvstx Nexus disponible (v{version})!\n\n¿Deseas descargarla e instalarla ahora?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from PySide6.QtWidgets import QProgressDialog
            self.upd_dlg = QProgressDialog("Descargando actualización...", "Cancelar", 0, 100, self)
            self.upd_dlg.setWindowTitle(f"Descargando v{version}")
            self.upd_dlg.setWindowModality(Qt.WindowModality.WindowModal)
            
            from ui.workers import UpdateDownloaderWorker
            self.upd_down_w = UpdateDownloaderWorker(dl_url)
            self.upd_down_w.progress.connect(self.upd_dlg.setValue)
            self.upd_down_w.finished.connect(self._on_update_downloaded)
            self.upd_dlg.canceled.connect(self.upd_down_w.terminate)
            self.upd_down_w.start()

    def _on_update_downloaded(self, success, path_or_err):
        from PySide6.QtWidgets import QMessageBox
        self.upd_dlg.close()
        if success:
            import os, sys
            QMessageBox.information(self, "Listo", "La actualización se ha descargado.\nSe cerrará la aplicación para instalar el parche.")
            os.startfile(path_or_err)
            sys.exit(0)
        else:
            QMessageBox.critical(self, "Error", f"No se pudo descargar la actualización:\n{path_or_err}")
