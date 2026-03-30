import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from ui.theme import COLORS
from ui.flow_layout import FlowLayout
from core.hub import HB_REPOS, get_download_url
from ui.workers import HubSearchWorker, HubDownloadWorker

class DownloaderView(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
        self.search_worker = None
        self.download_worker = None

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QtWidgets.QFrame()
        header.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-bottom: 1px solid {COLORS['border']};")
        header.setFixedHeight(90)
        h_layout = QtWidgets.QVBoxLayout(header)
        h_layout.setContentsMargins(30, 16, 30, 12)
        
        title = QtWidgets.QLabel("🌐  DESCARGAS (ONLINE)")
        title.setStyleSheet(f"font-family: 'Courier New'; font-size: 26px; font-weight: bold; color: {COLORS['accent']}; border: none;")
        h_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Busca y descarga ROMs directamente desde servidores online")
        subtitle.setStyleSheet(f"font-family: 'Courier New'; font-size: 11px; color: {COLORS['text_dim']}; border: none;")
        h_layout.addWidget(subtitle)
        layout.addWidget(header)

        # Controls Menu
        controls_group = QtWidgets.QFrame()
        controls_group.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border: 1px solid {COLORS['border']}; border-radius: 10px;")
        controls_layout = QtWidgets.QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(20, 15, 20, 15)
        
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(QtWidgets.QLabel("Fuente:"))
        self.source_combo = QtWidgets.QComboBox()
        self.source_combo.addItems(list(HB_REPOS.keys()))
        self.source_combo.setFixedWidth(240)
        row1.addWidget(self.source_combo)
        
        row1.addSpacing(20)
        row1.addWidget(QtWidgets.QLabel("Buscar:"))
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("nombre del juego...")
        self.search_input.setFixedWidth(280)
        self.search_input.returnPressed.connect(self._start_search)
        row1.addWidget(self.search_input)
        
        row1.addSpacing(20)
        search_btn = QtWidgets.QPushButton("🔍 Buscar")
        search_btn.setFixedSize(100, 36)
        search_btn.setStyleSheet(f"background-color: {COLORS['accent']}; color: {COLORS['bg_dark']}; font-weight: bold; border-radius: 6px;")
        search_btn.clicked.connect(self._start_search)
        row1.addWidget(search_btn)
        row1.addStretch()
        controls_layout.addLayout(row1)

        self.status_label = QtWidgets.QLabel("Listo")
        self.status_label.setStyleSheet(f"color: {COLORS['text_dim']}; margin-top: 10px; border: none;")
        controls_layout.addWidget(self.status_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"QProgressBar {{ background-color: {COLORS['bg_dark']}; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {COLORS['accent']}; border-radius: 4px; }}")
        self.progress_bar.hide()
        controls_layout.addWidget(self.progress_bar)
        
        # Add controls to layout but give it some margin
        ct = QtWidgets.QWidget()
        ct_lay = QtWidgets.QVBoxLayout(ct)
        ct_lay.setContentsMargins(20, 20, 20, 10)
        ct_lay.addWidget(controls_group)
        layout.addWidget(ct)

        # Results scroll area
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        layout.addWidget(self.scroll, stretch=1)

        self.results_container = QtWidgets.QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.scroll.setWidget(self.results_container)
        
        self.flow_layout = FlowLayout(self.results_container, margin=20, hSpacing=20, vSpacing=20)

    def _start_search(self):
        query = self.search_input.text().strip()
        console_name = self.source_combo.currentText()
        if not query and HB_REPOS.get(console_name, {}).get("type") in ("retrostic", "myrient"):
            self._set_status("Por favor, introduce un término de búsqueda para esta fuente.", COLORS["yellow"])
            return

        self._clear_results()
        self._set_status(f"⏳ Buscando en {console_name}...", COLORS["text_bright"])
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()

        if self.search_worker:
            self.search_worker.quit()
        self.search_worker = HubSearchWorker(console_name, query)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.error.connect(self._on_search_error)
        self.search_worker.start()

    def _clear_results(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _set_status(self, msg, color=COLORS["text_dim"]):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color}; margin-top: 10px; border: none;")

    def _on_search_finished(self, games):
        self.progress_bar.hide()
        self._set_status(f"✓ {len(games)} juegos encontrados.", COLORS["green"])
        if not games:
            lbl = QtWidgets.QLabel("No se encontraron resultados.")
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 14px; margin-top: 40px;")
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.flow_layout.addWidget(lbl)
            return
            
        for g in games:
            self.flow_layout.addWidget(self._create_game_card(g))

    def _on_search_error(self, err):
        self.progress_bar.hide()
        self._set_status(f"✗ Error: {err}", COLORS["red"])

    def _create_game_card(self, game):
        card = QtWidgets.QFrame()
        card.setFixedSize(300, 150)
        card.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px;")
        
        l = QtWidgets.QVBoxLayout(card)
        l.setContentsMargins(15, 15, 15, 15)
        
        title = QtWidgets.QLabel(game.get("title", game.get("_slug", "Unknown")))
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_bright']}; border: none;")
        l.addWidget(title)
        
        author = game.get("author", "")
        author_str = author.get("name", str(author)) if isinstance(author, dict) else str(author)
        tags = ", ".join(game.get("tags", [])[:3])
        sub = QtWidgets.QLabel(f"👤 {author_str} | 🏷 {tags}")
        sub.setStyleSheet(f"font-size: 10px; color: {COLORS['accent2']}; border: none;")
        l.addWidget(sub)
        
        l.addStretch()
        
        dl_url = get_download_url(game)
        if dl_url:
            btn = QtWidgets.QPushButton("⬇ Descargar")
            btn.setFixedHeight(32)
            btn.setStyleSheet(f"background-color: {COLORS['accent']}; color: {COLORS['bg_dark']}; font-weight: bold; border-radius: 6px;")
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            
            repo = game.get("_repo", {})
            cns = self.source_combo.currentText()
            if repo.get("type") in ("retrostic", "myrient") and game.get("tags"):
                cns = game.get("tags")[0]

            btn.clicked.connect(lambda _, u=dl_url, t=game.get("title", ""), c=cns, s=game.get("_slug",""), rp=repo: self._start_download(u, t, c, s, rp))
            l.addWidget(btn)
        else:
            lbl = QtWidgets.QLabel("Sin descarga directa")
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"font-size: 10px; color: {COLORS['text_dim']}; border: none;")
            l.addWidget(lbl)
            
        return card

    def _start_download(self, url, title, console_name, slug, repo):
        # Determine logical local category
        dest_console = "Descargas"
        from ui.main_window import CONSOLES
        for cn, info in CONSOLES.items():
            if console_name and (cn.lower() in console_name.lower() or info.get("emulator_key","") in console_name.lower()):
                dest_console = cn
                break
                
        import os
        roms_dir = self.main_window.config.get("roms_dir", os.path.expanduser("~/ROMs"))
        dest_dir = os.path.join(roms_dir, dest_console)
        
        if self.download_worker and self.download_worker.isRunning():
            self._set_status("Ya hay una descarga en curso. Espera a que termine.", COLORS["red"])
            return

        self._set_status(f"⬇ Procesando descarga de {title} a {dest_console}...", COLORS["yellow"])
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        info = CONSOLES.get(dest_console, {})
        exts = info.get("extensions", [])
        
        self.download_worker = HubDownloadWorker(url, dest_dir, title, repo, exts)
        self.download_worker.progress.connect(self._on_download_progress)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.start()

    def _on_download_progress(self, pct, downloaded_mb, total_mb):
        self.progress_bar.setValue(int(pct * 100))
        self._set_status(f"⬇ Descargando... {downloaded_mb:.1f} MB / {total_mb:.1f} MB", COLORS["yellow"])

    def _on_download_finished(self, success, msg):
        self.progress_bar.hide()
        if success:
            self._set_status(f"✓ {msg}", COLORS["green"])
            from ui.library_view import LibraryView
            if isinstance(self.main_window.current_view_widget, LibraryView):
                self.main_window.filter_games()
        else:
            self._set_status(f"✗ Error: {msg}", COLORS["red"])
