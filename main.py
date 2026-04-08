import sys
import os
from PySide6.QtWidgets import QApplication
from ui.theme import get_stylesheet
from ui.main_window import MainWindow
from ui.welcome_wizard import WelcomeWizard
from core.config import load_config, check_branding_migration

if __name__ == "__main__":
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet(get_stylesheet())
    
    cfg = load_config()
    
    if check_branding_migration(cfg):
        wizard = WelcomeWizard()
        if wizard.exec() != 1:  # 1 is QDialog.Accepted
            sys.exit(0)  # User closed the wizard without finishing
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
