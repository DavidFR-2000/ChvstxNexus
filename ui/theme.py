from core.config import COLORS

def get_stylesheet():
    return f"""
    QWidget {{
        background-color: {COLORS['bg_dark']};
        color: {COLORS['text_bright']};
        font-family: "Segoe UI", "Courier New";
    }}
    
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}
    
    QFrame#TopNav {{
        background-color: transparent;
        border: none;
    }}
    
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background: {COLORS['bg_dark']};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['border']};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['accent']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px; background: none;
    }}
    
    QScrollBar:horizontal {{
        background: {COLORS['bg_dark']};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['border']};
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['accent']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px; background: none;
    }}

    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_dim']};
        border: none;
        border-radius: 8px;
        padding: 6px 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
    }}
    QPushButton#ConsoleButtonActive {{
        background-color: {COLORS['bg_hover']};
        border: 1px solid {COLORS['accent']};
        color: {COLORS['accent']};
    }}
    
    QLineEdit {{
        background-color: {COLORS['bg_mid']};
        color: {COLORS['text_bright']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 6px 12px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLORS['accent']};
    }}
    
    QComboBox {{
        background-color: {COLORS['bg_mid']};
        color: {COLORS['text_bright']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 4px 10px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_mid']};
        color: {COLORS['text_bright']};
        selection-background-color: {COLORS['bg_hover']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        outline: none;
    }}
    
    QCheckBox {{
        spacing: 8px;
        color: {COLORS['text_bright']};
        font-weight: bold;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['bg_mid']};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {COLORS['accent']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['accent']};
        border: 1px solid {COLORS['accent']};
    }}

    QProgressBar {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['bg_mid']};
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['accent']};
        border-radius: 3px;
    }}

    /* Card Styles */
    QFrame#ContainerBox {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
    }}
    
    QFrame#GameCard {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
    }}
    QFrame#GameCard:hover {{
        background-color: {COLORS['bg_hover']};
        border: 1px solid {COLORS['accent']};
    }}
    """
