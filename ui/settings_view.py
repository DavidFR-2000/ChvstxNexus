import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QLineEdit, QFileDialog, QCheckBox,
    QComboBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from core.config import COLORS, CONSOLES, RA_CORES, save_config

class SettingsView(QWidget):
    close_requested = Signal()
    config_saved = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top Bar
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(40, 30, 40, 10)
        
        btn_back = QPushButton("◀ Volver a Biblioteca")
        btn_back.setStyleSheet(f"background-color: {COLORS['bg_card']}; font-size: 14px; font-weight: bold; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 10px 20px;")
        btn_back.clicked.connect(self.close_requested.emit)
        top_layout.addWidget(btn_back)
        
        top_layout.addStretch()
        
        lbl_title = QLabel("CONFIGURACIÓN DEL SISTEMA")
        lbl_title.setStyleSheet(f"color: {COLORS['text_bright']}; font-size: 22px; font-weight: 900; letter-spacing: 1px;")
        top_layout.addWidget(lbl_title)
        
        layout.addWidget(top_bar)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        self.v_layout = QVBoxLayout(content)
        self.v_layout.setContentsMargins(40, 20, 40, 40)
        self.v_layout.setSpacing(25)
        
        self.build_retroarch_section()
        self.build_roms_section()
        self.build_ra_section()
        self.build_emulators_section()
        self.build_danger_section()
        
        # Save Button
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_save = QPushButton("💾 Guardar y Aplicar Cambios")
        btn_save.setFixedWidth(300)
        btn_save.setStyleSheet(f"background-color: {COLORS['accent']}; color: {COLORS['bg_dark']}; font-size: 16px; font-weight: 900; padding: 15px; border-radius: 12px;")
        btn_save.clicked.connect(self.save)
        save_row.addWidget(btn_save)
        self.v_layout.addLayout(save_row)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _create_section_card(self, title, icon):
        card = QFrame()
        card.setObjectName("ContainerBox")
        card.setStyleSheet(f"QFrame#ContainerBox {{ background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 14px; }}")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        lbl = QLabel(f"{icon}  {title}")
        lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['accent']}; margin-bottom: 10px;")
        layout.addWidget(lbl)
        
        return card, layout

    def build_retroarch_section(self):
        card, layout = self._create_section_card("Motor RetroArch", "🕹️")
        
        # RA Path
        hl1 = QHBoxLayout()
        hl1.addWidget(QLabel("Ejecutable (retroarch.exe)", styleSheet="font-weight: bold; width: 180px;"))
        self.ra_path = QLineEdit(self.config.get("retroarch_path", ""))
        hl1.addWidget(self.ra_path, 1)
        btn1 = QPushButton("Examinar...")
        btn1.setStyleSheet(f"background-color: {COLORS['bg_hover']}; padding: 6px 15px;")
        btn1.clicked.connect(lambda: self.ra_path.setText(QFileDialog.getOpenFileName(self, "RetroArch EXE", r"C:\\", "Ejecutables (*.exe)")[0] or self.ra_path.text()))
        hl1.addWidget(btn1)
        layout.addLayout(hl1)
        
        # Cores Dir
        hl2 = QHBoxLayout()
        hl2.addWidget(QLabel("Directorio de Cores", styleSheet="font-weight: bold; width: 180px;"))
        self.cores_dir = QLineEdit(self.config.get("cores_dir", ""))
        hl2.addWidget(self.cores_dir, 1)
        btn2 = QPushButton("Examinar...")
        btn2.setStyleSheet(f"background-color: {COLORS['bg_hover']}; padding: 6px 15px;")
        btn2.clicked.connect(lambda: self.cores_dir.setText(QFileDialog.getExistingDirectory(self, "Carpeta Cores", r"C:\\") or self.cores_dir.text()))
        hl2.addWidget(btn2)
        layout.addLayout(hl2)
        
        # Check Cores Button
        btn_check = QPushButton("🔍 Analizar Cores Instalados")
        btn_check.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['accent']}; color: {COLORS['accent']}; padding: 8px 15px;")
        btn_check.clicked.connect(self.check_cores)
        
        hl3 = QHBoxLayout()
        hl3.addStretch()
        hl3.addWidget(btn_check)
        layout.addLayout(hl3)
        
        self.cores_results = QLabel("")
        self.cores_results.setStyleSheet(f"font-size: 13px; line-height: 150%; background-color: {COLORS['bg_dark']}; padding: 15px; border-radius: 8px;")
        self.cores_results.setWordWrap(True)
        self.cores_results.hide()
        layout.addWidget(self.cores_results)
        
        self.v_layout.addWidget(card)

    def check_cores(self):
        cores_path = self.cores_dir.text()
        if not os.path.exists(cores_path):
            self.cores_results.setText(f"<span style='color: {COLORS['red']}'>❌ Ruta de cores inválida.</span>")
            self.cores_results.show()
            return
            
        found = set(os.listdir(cores_path))
        missing = set()
        installed = set()
        
        for k, clist in RA_CORES.items():
            for c in clist:
                if c in found:
                    installed.add(c)
                else:
                    missing.add(c)
                    
        total = len(installed) + len(missing)
        html = f"<div style='color: {COLORS['text_bright']};'><b>Resultados del Análisis ({len(installed)} / {total} Cores Oficiales):</b><br><br>"
        
        if installed:
            html += f"<span style='color: {COLORS['green']}'><b>✅ Instalados ({len(installed)}):</b></span><br>"
            html += "<span style='color: " + COLORS['text_dim'] + "'>" + ", ".join(sorted(installed)) + "</span><br><br>"
            
        if missing:
            html += f"<span style='color: {COLORS['red']}'><b>❌ Faltantes ({len(missing)}):</b></span><br>"
            html += "<span style='color: " + COLORS['text_dim'] + "'>" + ", ".join(sorted(missing)) + "</span>"
        else:
            html += f"<span style='color: {COLORS['green']}'><b>¡Todos los Cores oficiales están instalados!</b></span>"
            
        html += "</div>"
        
        self.cores_results.setText(html)
        self.cores_results.show()

    def build_roms_section(self):
        card, layout = self._create_section_card("Directorio de Juegos", "📁")
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Carpeta Raíz de ROMs", styleSheet="font-weight: bold; width: 180px;"))
        self.roms_dir = QLineEdit(self.config.get("roms_dir", ""))
        hl.addWidget(self.roms_dir, 1)
        btn = QPushButton("Examinar...")
        btn.setStyleSheet(f"background-color: {COLORS['bg_hover']}; padding: 6px 15px;")
        btn.clicked.connect(lambda: self.roms_dir.setText(QFileDialog.getExistingDirectory(self, "Carpeta ROMs", r"C:\\") or self.roms_dir.text()))
        hl.addWidget(btn)
        layout.addLayout(hl)
        
        info = QLabel("* La carpeta debe contener subcarpetas con el nombre exacto de cada consola (ej: 'SNES', 'GBA').")
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-style: italic; font-size: 12px;")
        layout.addWidget(info)
        
        self.v_layout.addWidget(card)

    def build_ra_section(self):
        card, layout = self._create_section_card("Cuenta RetroAchievements", "🏆")
        
        hl1 = QHBoxLayout()
        hl1.addWidget(QLabel("Usuario Web", styleSheet="font-weight: bold; width: 180px;"))
        self.ra_user = QLineEdit(self.config.get("ra_user", ""))
        hl1.addWidget(self.ra_user, 1)
        layout.addLayout(hl1)
        
        hl2 = QHBoxLayout()
        hl2.addWidget(QLabel("Web API Key", styleSheet="font-weight: bold; width: 180px;"))
        self.ra_apikey = QLineEdit(self.config.get("ra_apikey", ""))
        self.ra_apikey.setEchoMode(QLineEdit.Password)
        hl2.addWidget(self.ra_apikey, 1)
        layout.addLayout(hl2)
        
        self.v_layout.addWidget(card)

    def build_emulators_section(self):
        card, layout = self._create_section_card("Consolas y Núcleos Activos", "📺")
        
        self.emu_switches = {}
        self.emu_combos = {}
        
        active = self.config.get("active_consoles", [])
        prefs = self.config.get("core_preferences", {})
        
        for cn, cores in RA_CORES.items():
            if not cores: continue
            
            row = QWidget()
            row.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-radius: 8px;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(15, 10, 15, 10)
            
            info = CONSOLES.get(cn, {})
            chk = QCheckBox(f"{info.get('emoji', '')}  {cn}")
            chk.setStyleSheet(f"color: {info.get('color', '#fff')}; font-size: 15px; font-weight: bold;")
            chk.setChecked(cn in active)
            hl.addWidget(chk)
            self.emu_switches[cn] = chk
            
            hl.addStretch()
            
            cmb = QComboBox()
            cmb.addItems(cores)
            cmb.setFixedWidth(250)
            pref = prefs.get(cn)
            if pref and pref in cores:
                cmb.setCurrentText(pref)
            hl.addWidget(cmb)
            self.emu_combos[cn] = cmb
            
            chk.toggled.connect(cmb.setEnabled)
            cmb.setEnabled(chk.isChecked())
            
            layout.addWidget(row)
            
        self.v_layout.addWidget(card)

    def build_danger_section(self):
        card, layout = self._create_section_card("Zona de Peligro", "⚠️")
        
        btn = QPushButton("Desinstalar Aplicación")
        btn.setStyleSheet(f"background-color: transparent; border: 2px solid {COLORS['red']}; color: {COLORS['red']}; padding: 12px; border-radius: 8px; font-weight: bold;")
        btn.clicked.connect(self.uninstall_app)
        layout.addWidget(btn)
        
        self.v_layout.addWidget(card)

    def uninstall_app(self):
        import sys, os, subprocess
        from PySide6.QtWidgets import QApplication
        
        reply = QMessageBox.warning(self, "Desinstalar Chvstx Nexus", 
            "¿Estás seguro de que quieres desinstalar la aplicación de tu PC?\n\nAl confirmar se cerrará el programa y se abrirá el desinstalador oficial.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
            uninstaller = os.path.join(base_dir, "unins000.exe")
            if os.path.exists(uninstaller):
                subprocess.Popen([uninstaller])
                QApplication.quit()
            else:
                QMessageBox.critical(self, "Error", "No se ha encontrado el desinstalador en el directorio base.\nLa aplicación no fue instalada correctamente o estás usando la versión portable.")

    def save(self):
        self.config["retroarch_path"] = self.ra_path.text()
        self.config["cores_dir"] = self.cores_dir.text()
        self.config["roms_dir"] = self.roms_dir.text()
        self.config["ra_user"] = self.ra_user.text()
        self.config["ra_apikey"] = self.ra_apikey.text()
        
        new_active = []
        new_prefs = {}
        for cn, chk in self.emu_switches.items():
            if chk.isChecked():
                new_active.append(cn)
                
        for cn, cmb in self.emu_combos.items():
            if self.emu_switches[cn].isChecked():
                new_prefs[cn] = cmb.currentText()
                
        self.config["active_consoles"] = new_active
        self.config["core_preferences"] = new_prefs
        
        save_config(self.config)
        self.config_saved.emit()
