# Custom Title Bar Widget
# Creates a custom title bar that matches VS Code themes

from aqt.qt import *
from typing import Optional

class CustomTitleBar(QWidget):
    def __init__(self, parent=None, theme_colors=None):
        super().__init__(parent)
        self.parent_window = parent
        self.theme_colors = theme_colors or {}
        self.mouse_pos = None
        self.is_maximized = False
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        self.setFixedHeight(30)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Themed traffic light buttons
        self.close_btn = self.create_themed_button("close")
        self.minimize_btn = self.create_themed_button("minimize")
        self.maximize_btn = self.create_themed_button("maximize")
        
        layout.addWidget(self.close_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        
        layout.addSpacing(10)
        
        self.title_label = QLabel("Anki")
        if self.parent_window:
            self.title_label.setText(self.parent_window.windowTitle())
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 1)
        
        self.minimize_btn.clicked.connect(self.minimize_window)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.close_window)
        
        self.setMouseTracking(True)

    def create_themed_button(self, button_type):
        btn = QPushButton()
        btn.setFixedSize(12, 12)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName(f"themed-{button_type}-button")
        return btn
        
    def apply_theme(self):
        bg_color = self.theme_colors.get('titleBar.activeBackground', '#21252b')
        fg_color = self.theme_colors.get('titleBar.activeForeground', '#abb2bf')
        border_color = self.theme_colors.get('titleBar.border', '#181a1f')
        
        # Use subtle, theme-aware colors for buttons
        close_color = self.theme_colors.get('statusBarItem.errorBackground', '#c74e39')
        min_color = self.theme_colors.get('statusBarItem.warningBackground', '#d9a326')
        max_color = self.theme_colors.get('gitDecoration.modifiedResourceForeground', '#81b88b')

        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
            QLabel {{
                color: {fg_color};
                font-size: 13px;
            }}
            QPushButton {{
                border-radius: 6px;
                border: none;
                background-color: transparent;
            }}
            QPushButton:hover {{
                filter: brightness(120%);
            }}
            #themed-close-button {{ background-color: {close_color}; }}
            #themed-minimize-button {{ background-color: {min_color}; }}
            #themed-maximize-button {{ background-color: {max_color}; }}
        """)
        
    def update_title(self, title):
        self.title_label.setText(title)
        
    def minimize_window(self):
        if self.parent_window: self.parent_window.showMinimized()
            
    def toggle_maximize(self):
        if self.parent_window:
            if self.is_maximized:
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
            self.is_maximized = not self.is_maximized
                
    def close_window(self):
        if self.parent_window: self.parent_window.close()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.mouse_pos and event.buttons() == Qt.MouseButton.LeftButton:
            if self.parent_window:
                delta = event.globalPosition().toPoint() - self.mouse_pos
                self.parent_window.move(self.parent_window.pos() + delta)
                self.mouse_pos = event.globalPosition().toPoint()
                
    def mouseReleaseEvent(self, event):
        self.mouse_pos = None
        
    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize()

def apply_custom_titlebar(window, theme_colors):
    original_flags = window.windowFlags()
    window.setWindowFlags(original_flags | Qt.WindowType.FramelessWindowHint)
    
    central_widget = window.centralWidget()
    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)
    
    titlebar = CustomTitleBar(window, theme_colors)
    container_layout.addWidget(titlebar)
    
    if central_widget:
        container_layout.addWidget(central_widget)
    
    window.setCentralWidget(container)
    
    if hasattr(window, 'windowTitleChanged'):
        window.windowTitleChanged.connect(titlebar.update_title)
    
    return titlebar
