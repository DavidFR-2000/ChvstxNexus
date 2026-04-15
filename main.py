import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.theme import get_stylesheet
from ui.main_window import MainWindow
from ui.welcome_wizard import WelcomeWizard
from core.config import load_config, check_branding_migration

if __name__ == "__main__":
    try:
        myappid = 'chvstxnexus.app.v4'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QApplication(sys.argv)
    
    # Get the project root path relative to main.py or PyInstaller's Temp Dir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        ROOT_PATH = sys._MEIPASS
    else:
        ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    # Set application icon using .ico which is better for Windows taskbar
    icon_path = os.path.join(ROOT_PATH, "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(ROOT_PATH, "app_icon.png")
        
    app_icon = QIcon(icon_path)
    if os.path.exists(icon_path):
        app.setWindowIcon(app_icon)
    
    # Apply dark theme
    app.setStyleSheet(get_stylesheet())
    
    cfg = load_config()
    
    if check_branding_migration(cfg):
        wizard = WelcomeWizard()
        if wizard.exec() != 1:  # 1 is QDialog.Accepted
            sys.exit(0)  # User closed the wizard without finishing
    
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())
