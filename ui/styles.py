"""
Z32 Nexus - Cyberpunk Theme Stylesheet
Dark mode with terminal green/amber accents
"""


def get_stylesheet(theme_color: str = '#00ff41') -> str:
    """
    Generate the cyberpunk stylesheet with the given accent color.
    Default: Matrix Green (#00ff41)
    Alternative: Amber (#ffb000)
    """
    
    # Color palette
    bg_dark = '#0f0f0f'
    bg_medium = '#1a1a1a'
    bg_light = '#252525'
    text_primary = theme_color
    text_secondary = '#888888'
    border_color = '#333333'
    hover_color = '#2a2a2a'
    selected_color = '#3a3a3a'
    danger_color = '#ff4444'
    success_color = '#44ff44'
    warning_color = '#ffaa00'
    
    return f"""
    /* ============================================ */
    /* GLOBAL STYLES                                */
    /* ============================================ */
    
    QWidget {{
        background-color: {bg_dark};
        color: {text_primary};
        font-family: 'Consolas', 'JetBrains Mono', 'Courier New', monospace;
        font-size: 14px;
    }}
    
    QMainWindow {{
        background-color: {bg_dark};
    }}
    
    /* ============================================ */
    /* BUTTONS                                      */
    /* ============================================ */
    
    QPushButton {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 8px 16px;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {hover_color};
        border-color: {text_primary};
        box-shadow: 0 0 10px {text_primary};
    }}
    
    QPushButton:pressed {{
        background-color: {selected_color};
    }}
    
    QPushButton:disabled {{
        background-color: {bg_dark};
        color: {text_secondary};
        border-color: {border_color};
    }}
    
    QPushButton#dangerButton {{
        border-color: {danger_color};
        color: {danger_color};
    }}
    
    QPushButton#dangerButton:hover {{
        background-color: rgba(255, 68, 68, 0.2);
    }}
    
    QPushButton#successButton {{
        border-color: {success_color};
        color: {success_color};
    }}
    
    QPushButton#successButton:hover {{
        background-color: rgba(68, 255, 68, 0.2);
    }}
    
    /* ============================================ */
    /* LABELS                                       */
    /* ============================================ */
    
    QLabel {{
        color: {text_primary};
        background-color: transparent;
    }}
    
    QLabel#title {{
        font-size: 24px;
        font-weight: bold;
    }}
    
    QLabel#subtitle {{
        font-size: 16px;
        color: {text_secondary};
    }}
    
    QLabel#statLabel {{
        font-size: 32px;
        font-weight: bold;
    }}
    
    /* ============================================ */
    /* TEXT INPUTS                                  */
    /* ============================================ */
    
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 8px;
        selection-background-color: {text_primary};
        selection-color: {bg_dark};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {text_primary};
    }}
    
    /* ============================================ */
    /* TABS                                         */
    /* ============================================ */
    
    QTabWidget::pane {{
        border: 1px solid {border_color};
        background-color: {bg_dark};
        border-radius: 4px;
    }}
    
    QTabBar::tab {{
        background-color: {bg_medium};
        color: {text_secondary};
        border: 1px solid {border_color};
        border-bottom: none;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {bg_dark};
        color: {text_primary};
        border-bottom: 2px solid {text_primary};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {hover_color};
    }}
    
    /* ============================================ */
    /* LISTS & TABLES                               */
    /* ============================================ */
    
    QListWidget, QTableWidget {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 4px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {border_color};
    }}
    
    QListWidget::item:hover {{
        background-color: {hover_color};
    }}
    
    QListWidget::item:selected {{
        background-color: {selected_color};
        border-left: 3px solid {text_primary};
    }}
    
    QHeaderView::section {{
        background-color: {bg_medium};
        color: {text_primary};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {border_color};
    }}
    
    /* ============================================ */
    /* SCROLLBARS                                   */
    /* ============================================ */
    
    QScrollBar:vertical {{
        background-color: {bg_dark};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {border_color};
        min-height: 30px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {text_secondary};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {bg_dark};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {border_color};
        min-width: 30px;
        border-radius: 6px;
    }}
    
    /* ============================================ */
    /* CHECKBOXES                                   */
    /* ============================================ */
    
    QCheckBox {{
        spacing: 8px;
        color: {text_primary};
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {border_color};
        border-radius: 4px;
        background-color: {bg_medium};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {text_primary};
        border-color: {text_primary};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {text_primary};
    }}
    
    /* ============================================ */
    /* PROGRESS BARS                                */
    /* ============================================ */
    
    QProgressBar {{
        background-color: {bg_medium};
        border: 1px solid {border_color};
        border-radius: 4px;
        height: 20px;
        text-align: center;
        color: {text_primary};
    }}
    
    QProgressBar::chunk {{
        background-color: {text_primary};
        border-radius: 3px;
    }}
    
    /* ============================================ */
    /* SLIDERS                                      */
    /* ============================================ */
    
    QSlider::groove:horizontal {{
        background-color: {bg_medium};
        height: 8px;
        border-radius: 4px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {text_primary};
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }}
    
    QSlider::sub-page:horizontal {{
        background-color: {text_primary};
        border-radius: 4px;
    }}
    
    /* ============================================ */
    /* SPINBOX                                      */
    /* ============================================ */
    
    QSpinBox, QDoubleSpinBox {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    
    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {bg_light};
        border: none;
        width: 20px;
    }}
    
    /* ============================================ */
    /* COMBOBOX                                     */
    /* ============================================ */
    
    QComboBox {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 8px;
        min-width: 100px;
    }}
    
    QComboBox:hover {{
        border-color: {text_primary};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {bg_medium};
        color: {text_primary};
        selection-background-color: {selected_color};
        border: 1px solid {border_color};
    }}
    
    /* ============================================ */
    /* MENUS                                        */
    /* ============================================ */
    
    QMenuBar {{
        background-color: {bg_dark};
        color: {text_primary};
        border-bottom: 1px solid {border_color};
    }}
    
    QMenuBar::item {{
        padding: 8px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {hover_color};
    }}
    
    QMenu {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {border_color};
    }}
    
    QMenu::item {{
        padding: 8px 30px;
    }}
    
    QMenu::item:selected {{
        background-color: {selected_color};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {border_color};
        margin: 4px 10px;
    }}
    
    /* ============================================ */
    /* TOOLTIPS                                     */
    /* ============================================ */
    
    QToolTip {{
        background-color: {bg_medium};
        color: {text_primary};
        border: 1px solid {text_primary};
        padding: 4px 8px;
    }}
    
    /* ============================================ */
    /* GROUP BOX                                    */
    /* ============================================ */
    
    QGroupBox {{
        border: 1px solid {border_color};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 8px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {text_primary};
    }}
    
    /* ============================================ */
    /* STATUS BAR                                   */
    /* ============================================ */
    
    QStatusBar {{
        background-color: {bg_medium};
        color: {text_secondary};
        border-top: 1px solid {border_color};
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    """


# Preset themes
THEMES = {
    'matrix': '#00ff41',
    'amber': '#ffb000',
    'ocean': '#00d4ff',
    'blood': '#ff3333',
    'purple': '#aa55ff',
    'ice': '#88ffff',
}


def get_theme_color(theme_name: str) -> str:
    """Get the color for a theme name"""
    return THEMES.get(theme_name.lower(), THEMES['matrix'])
