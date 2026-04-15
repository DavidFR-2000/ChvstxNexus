from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os
import sys
from core.config import BASE_PATH

app = QApplication(sys.argv)
icon_path = os.path.join(BASE_PATH, 'app_icon.ico')
print(f"Path: {icon_path}")
print(f"Exists? {os.path.exists(icon_path)}")
icon = QIcon(icon_path)
print(f"Is null? {icon.isNull()}")
