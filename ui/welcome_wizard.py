import os
import requests
import py7zr
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from PySide6.QtGui import QIcon, QFont, QPixmap, QDesktopServices
from ui.theme import COLORS
from core.config import load_config, save_config

class RetroArchDownloadWorker(QtCore.QThread):
    progress = QtCore.Signal(int, str)
    finished_dl = QtCore.Signal(bool, str)

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        self.url = "https://buildbot.libretro.com/stable/1.19.1/windows/x86_64/RetroArch.7z"

    def run(self):
        try:
            self.progress.emit(0, "Descargando RetroArch (puede tardar un poco)...")
            r = requests.get(self.url, stream=True, timeout=15)
            r.raise_for_status()
            
            total_length = r.headers.get('content-length')
            archive_path = os.path.join(os.path.expanduser("~"), "RetroArch_temp.7z")
            
            if total_length is None: # no content length header
                with open(archive_path, 'wb') as f:
                    f.write(r.content)
            else:
                dl = 0
                total_length = int(total_length)
                with open(archive_path, 'wb') as f:
                    for data in r.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        self.progress.emit(done, f"Descargando... {dl//1024//1024}MB / {total_length//1024//1024}MB")
            
            self.progress.emit(50, "Extrayendo archivos (por favor, espera)...")
            
            # Extract
            os.makedirs(self.target_dir, exist_ok=True)
            with py7zr.SevenZipFile(archive_path, mode='r') as z:
                dest_real = os.path.realpath(self.target_dir)
                for member in z.getnames():
                    target = os.path.realpath(os.path.join(dest_real, member))
                    if not target.startswith(dest_real + os.sep) and target != dest_real:
                        raise Exception(f"Path Traversal evitado instalando RA: {member}")
                # py7zr doesn't offer easy progress callbacks per file in a simple way, so we just wait
                z.extractall(path=self.target_dir)
            
            # Clean up
            try:
                os.remove(archive_path)
            except Exception as e:
                import logging
                logging.error(f"No se pudo limpiar el archivo temporal del wizard: {e}")
                
            # Buscar el retroarch.exe dentro, a veces viene en subcarpeta RetroArch-Win64
            exe_path = os.path.join(self.target_dir, "retroarch.exe")
            if not os.path.exists(exe_path):
                # Probablemente está en C:\RetroArch-Win64\RetroArch-Win64\retroarch.exe
                sub_exe = os.path.join(self.target_dir, "RetroArch-Win64", "retroarch.exe")
                if os.path.exists(sub_exe):
                    exe_path = sub_exe
                    
            self.progress.emit(100, "¡Completado!")
            self.finished_dl.emit(True, exe_path)
            
        except Exception as e:
            self.finished_dl.emit(False, str(e))


class WelcomeWizard(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración Inicial - Chvstx Nexus")
        self.setFixedSize(650, 450)
        self.config = load_config()
        self._setup_ui()
        self.ra_exe_path = ""

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_bright']};")

        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)

        self._build_page1_welcome()
        self._build_page2_retroarch()
        self._build_page3_retroachievements()

        # Bottom Bar
        self.bottom_bar = QtWidgets.QFrame()
        self.bottom_bar.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-top: 1px solid {COLORS['border']};")
        self.bottom_bar.setFixedHeight(60)
        bb_layout = QtWidgets.QHBoxLayout(self.bottom_bar)
        
        self.btn_back = QtWidgets.QPushButton("Atrás")
        self.btn_back.clicked.connect(self._go_back)
        self.btn_back.hide()
        self._style_btn(self.btn_back)
        
        self.btn_next = QtWidgets.QPushButton("Siguiente")
        self.btn_next.clicked.connect(self._go_next)
        self._style_btn(self.btn_next, primary=True)

        bb_layout.addWidget(self.btn_back)
        bb_layout.addStretch()
        bb_layout.addWidget(self.btn_next)
        
        main_layout.addWidget(self.bottom_bar)

    def _style_btn(self, btn, primary=False):
        btn.setFixedSize(120, 36)
        if primary:
            btn.setStyleSheet(f"background-color: {COLORS['accent']}; color: {COLORS['bg_dark']}; font-weight: bold; border-radius: 6px;")
        else:
            btn.setStyleSheet(f"background-color: {COLORS['bg_hover']}; color: {COLORS['text_bright']}; border: 1px solid {COLORS['border']}; border-radius: 6px;")
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def _build_page1_welcome(self):
        page = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout(page)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QtWidgets.QLabel("Bienvenido a Chvstx Nexus 🚀")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['accent']};")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        desc = QtWidgets.QLabel(
            "Tu nueva estación central de emulación ha sido instalada correctamente.\n\n"
            "Antes de empezar a jugar, vamos a configurar los motores de emulación\n"
            "y tu cuenta de logros retro en menos de 1 minuto.\n\n"
            "Haz clic en Siguiente para comenzar."
        )
        desc.setStyleSheet(f"font-size: 14px; color: {COLORS['text_dim']};")
        desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        l.addStretch()
        l.addWidget(title)
        l.addSpacing(20)
        l.addWidget(desc)
        l.addStretch()
        
        self.stack.addWidget(page)

    def _build_page2_retroarch(self):
        page = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout(page)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QtWidgets.QLabel("Motor RetroArch 🎮")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['accent']};")
        
        desc = QtWidgets.QLabel(
            "Chvstx Nexus utiliza RetroArch por debajo para ejecutar los de juegos.\n"
            "Si no lo tienes, podemos descargarlo e instalarlo ahora mismo de forma automática."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 14px; color: {COLORS['text_dim']};")
        
        self.btn_install_ra = QtWidgets.QPushButton("Descargar e Instalar RetroArch Automáticamente")
        self.btn_install_ra.setFixedHeight(45)
        self.btn_install_ra.setStyleSheet(f"background-color: {COLORS['green']}; color: {COLORS['bg_dark']}; font-weight: bold; font-size: 14px; border-radius: 6px;")
        self.btn_install_ra.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_install_ra.clicked.connect(self._install_retroarch)
        
        # O elegir manual
        self.btn_manual_ra = QtWidgets.QPushButton("Ya lo tengo instalado, elegir mi retroarch.exe")
        self._style_btn(self.btn_manual_ra)
        self.btn_manual_ra.setFixedWidth(300)
        self.btn_manual_ra.clicked.connect(self._select_retroarch_manual)
        
        self.ra_status = QtWidgets.QLabel("")
        self.ra_status.setStyleSheet(f"color: {COLORS['yellow']};")
        
        self.ra_progress = QtWidgets.QProgressBar()
        self.ra_progress.setFixedHeight(10)
        self.ra_progress.setTextVisible(False)
        self.ra_progress.setStyleSheet(f"QProgressBar {{ background-color: {COLORS['bg_mid']}; border: none; border-radius: 5px; }} QProgressBar::chunk {{ background-color: {COLORS['accent']}; border-radius: 5px; }}")
        self.ra_progress.hide()
        
        l.addWidget(title)
        l.addSpacing(10)
        l.addWidget(desc)
        l.addSpacing(30)
        l.addWidget(self.btn_install_ra)
        l.addSpacing(10)
        l.addWidget(self.btn_manual_ra, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        l.addSpacing(20)
        l.addWidget(self.ra_status)
        l.addWidget(self.ra_progress)
        l.addStretch()
        
        self.stack.addWidget(page)

    def _build_page3_retroachievements(self):
        page = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout(page)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QtWidgets.QLabel("RetroAchievements 🏆")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['accent']};")
        
        desc = QtWidgets.QLabel(
            "Conecta tu cuenta para desbloquear trofeos en juegos clásicos.\n"
            "Si no tienes cuenta, puedes crearla en retroachievements.org.\n"
            "Para obtener tu API Key, ve a Configuración (Settings) en su web y busca 'API Key'."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 14px; color: {COLORS['text_dim']};")
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(15)
        
        lbl_user = QtWidgets.QLabel("Usuario:")
        self.inp_ra_user = QtWidgets.QLineEdit()
        self.inp_ra_user.setFixedHeight(35)
        self.inp_ra_user.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border: 1px solid {COLORS['border']}; border-radius: 5px; padding: 5px;")
        
        lbl_api = QtWidgets.QLabel("API Key:")
        self.inp_ra_api = QtWidgets.QLineEdit()
        self.inp_ra_api.setFixedHeight(35)
        self.inp_ra_api.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border: 1px solid {COLORS['border']}; border-radius: 5px; padding: 5px;")
        
        form_layout.addRow(lbl_user, self.inp_ra_user)
        form_layout.addRow(lbl_api, self.inp_ra_api)
        
        btn_link = QtWidgets.QPushButton("Abrir RetroAchievements.org")
        self._style_btn(btn_link)
        btn_link.setFixedWidth(200)
        btn_link.clicked.connect(lambda: QDesktopServices.openUrl(QtCore.QUrl("https://retroachievements.org/controlpanel.php")))
        
        l.addWidget(title)
        l.addSpacing(10)
        l.addWidget(desc)
        l.addSpacing(20)
        l.addWidget(btn_link)
        l.addSpacing(20)
        l.addLayout(form_layout)
        l.addStretch()
        
        self.stack.addWidget(page)

    def _install_retroarch(self):
        target_dir = r"C:\RetroArch-Win64"
        self.btn_install_ra.setEnabled(False)
        self.btn_manual_ra.setEnabled(False)
        self.btn_next.setEnabled(False)
        self.btn_back.setEnabled(False)
        
        self.ra_progress.show()
        self.ra_progress.setValue(0)
        
        self.worker = RetroArchDownloadWorker(target_dir)
        self.worker.progress.connect(self._on_ra_progress)
        self.worker.finished_dl.connect(self._on_ra_finished)
        self.worker.start()

    def _on_ra_progress(self, val, text):
        self.ra_progress.setValue(val)
        self.ra_status.setText(text)

    def _on_ra_finished(self, success, result):
        self.btn_install_ra.setEnabled(True)
        self.btn_manual_ra.setEnabled(True)
        self.btn_next.setEnabled(True)
        self.btn_back.setEnabled(True)
        
        if success:
            self.ra_exe_path = result
            self.ra_status.setText(f"¡Instalado con éxito en {result}!")
            self.ra_status.setStyleSheet(f"color: {COLORS['green']};")
        else:
            self.ra_status.setText(f"Error: {result}")
            self.ra_status.setStyleSheet(f"color: {COLORS['red']};")

    def _select_retroarch_manual(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar retroarch.exe", "C:\\", "Ejecutable (retroarch.exe)")
        if path:
            self.ra_exe_path = path
            self.ra_status.setText(f"RetroArch seleccionado: {path}")
            self.ra_status.setStyleSheet(f"color: {COLORS['green']};")

    def _go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self._update_buttons()

    def _go_next(self):
        idx = self.stack.currentIndex()
        if idx == self.stack.count() - 1:
            self._finish_wizard()
        else:
            if idx == 1 and not self.ra_exe_path:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor instala o selecciona RetroArch antes de continuar.")
                return
            self.stack.setCurrentIndex(idx + 1)
        self._update_buttons()

    def _update_buttons(self):
        idx = self.stack.currentIndex()
        self.btn_back.setVisible(idx > 0)
        if idx == self.stack.count() - 1:
            self.btn_next.setText("¡Finalizar y Jugar!")
        else:
            self.btn_next.setText("Siguiente")

    def _finish_wizard(self):
        # Guardar todo
        self.config['nexus_first_run'] = False
        self.config['first_run'] = False
        if self.ra_exe_path:
            self.config['retroarch_path'] = os.path.normpath(self.ra_exe_path)
            # Deducir cores_dir
            cores = os.path.join(os.path.dirname(self.ra_exe_path), "cores")
            if os.path.exists(cores):
                self.config['cores_dir'] = cores
                
        user = self.inp_ra_user.text().strip()
        api = self.inp_ra_api.text().strip()
        if user and api:
            self.config['ra_user'] = user
            self.config['ra_apikey'] = api
            
        save_config(self.config)
        self.accept()
