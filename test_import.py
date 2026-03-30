import traceback
import sys
from PySide6.QtWidgets import QApplication

def test():
    try:
        app = QApplication(sys.argv)
        from ui.achievements_dialog import AchievementsDialog
        print("Import OK")
        
        # provide dummy creds so it attempts hitting retroachievements
        config = {"ra_user": "dummy", "ra_apikey": "dummy"}
        dlg = AchievementsDialog("dummy.bin", "PS1", config)
        dlg.show()
        print("Instantiation OK")
        
        # quit app after 3 secs
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, app.quit)
        
        app.exec()
        print("Event loop finished OK")
    except Exception as e:
        print("ERROR:", traceback.format_exc())

test()
