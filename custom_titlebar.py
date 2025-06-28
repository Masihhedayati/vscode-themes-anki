# Custom Title Bar Widget
# Creates a custom title bar that matches VS Code themes

from aqt.qt import *
from aqt.qt import QEvent
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
        """Create the title bar UI - macOS style"""
        self.setFixedHeight(28)  # macOS title bars are slightly shorter
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)  # macOS has more horizontal padding
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Window controls (macOS style - on the left)
        self.close_btn = self.create_mac_button("close")
        self.minimize_btn = self.create_mac_button("minimize")
        self.maximize_btn = self.create_mac_button("maximize")
        
        # Add traffic light buttons
        layout.addWidget(self.close_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        
        # Add some space after buttons
        layout.addSpacing(16)
        
        # Window icon (optional)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        if self.parent_window and hasattr(self.parent_window, 'windowIcon'):
            icon = self.parent_window.windowIcon()
            if not icon.isNull():
                pixmap = icon.pixmap(16, 16)
                self.icon_label.setPixmap(pixmap)
        layout.addWidget(self.icon_label)
        layout.addSpacing(8)
        
        # Title label - centered
        self.title_label = QLabel("Anki")
        if self.parent_window:
            self.title_label.setText(self.parent_window.windowTitle())
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 1)  # Stretch factor 1 to center
        
        # Fast restart button on the right
        self.restart_btn = QPushButton("⟳")
        self.restart_btn.setFixedSize(24, 20)
        self.restart_btn.setToolTip("Fast Restart Anki (No Sync)")
        self.restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_btn.setObjectName("restart-button")
        layout.addWidget(self.restart_btn)
        
        # Small spacer
        layout.addSpacing(8)
        
        # Connect buttons
        self.minimize_btn.clicked.connect(self.minimize_window)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.close_window)
        self.restart_btn.clicked.connect(self.fast_restart)
        
        # Enable mouse tracking for window dragging
        self.setMouseTracking(True)
        
    def create_mac_button(self, button_type):
        """Create a macOS-style traffic light button"""
        btn = QPushButton()
        btn.setFixedSize(12, 12)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName(f"mac-{button_type}-button")
        
        # Store button type for styling
        btn.button_type = button_type
        
        return btn
    
    def create_window_button(self, text):
        """Create a window control button (fallback for non-mac style)"""
        btn = QPushButton(text)
        btn.setFixedSize(46, 30)
        btn.setFlat(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
        
    def apply_theme(self):
        """Apply VS Code theme colors to the title bar"""
        bg_color = self.theme_colors.get('titleBar.activeBackground', 
                                         self.theme_colors.get('sideBar.background', '#21252b'))
        fg_color = self.theme_colors.get('titleBar.activeForeground',
                                         self.theme_colors.get('sideBar.foreground', '#abb2bf'))
        border_color = self.theme_colors.get('titleBar.border',
                                            self.theme_colors.get('editorGroup.border', '#181a1f'))
        
        # Title bar background
        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
        """)
        
        # Title text - smaller and more subtle for macOS style
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {fg_color};
                font-size: 13px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
            }}
        """)
        
        # macOS-style traffic light buttons
        # Close button (red)
        self.close_btn.setStyleSheet(f"""
            QPushButton#mac-close-button {{
                background-color: #ff5f57;
                border: 1px solid #e0443e;
                border-radius: 6px;
            }}
            QPushButton#mac-close-button:hover {{
                background-color: #ff5f57;
                border-color: #c14542;
            }}
            QPushButton#mac-close-button:pressed {{
                background-color: #e0443e;
            }}
        """)
        
        # Minimize button (yellow)
        self.minimize_btn.setStyleSheet(f"""
            QPushButton#mac-minimize-button {{
                background-color: #ffbd2e;
                border: 1px solid #dfa023;
                border-radius: 6px;
            }}
            QPushButton#mac-minimize-button:hover {{
                background-color: #ffbd2e;
                border-color: #c08e28;
            }}
            QPushButton#mac-minimize-button:pressed {{
                background-color: #dfa023;
            }}
        """)
        
        # Maximize button (green)
        self.maximize_btn.setStyleSheet(f"""
            QPushButton#mac-maximize-button {{
                background-color: #28c940;
                border: 1px solid #1aab29;
                border-radius: 6px;
            }}
            QPushButton#mac-maximize-button:hover {{
                background-color: #28c940;
                border-color: #128622;
            }}
            QPushButton#mac-maximize-button:pressed {{
                background-color: #1aab29;
            }}
        """)
        
        # Restart button styling - subtle but visible
        self.restart_btn.setStyleSheet(f"""
            QPushButton#restart-button {{
                background-color: transparent;
                color: {fg_color};
                border: 1px solid transparent;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                opacity: 0.7;
            }}
            QPushButton#restart-button:hover {{
                background-color: {border_color}66;
                border-color: {border_color};
                opacity: 1.0;
            }}
            QPushButton#restart-button:pressed {{
                background-color: {border_color};
            }}
        """)
        
        # Add hover symbols (only visible on hover)
        self.setup_hover_effects()
    
    def setup_hover_effects(self):
        """Setup hover effects for traffic light buttons"""
        # Add symbols that appear on hover
        self.close_btn.setText("")
        self.minimize_btn.setText("")
        self.maximize_btn.setText("")
        
        # Install event filters for hover effects
        self.close_btn.installEventFilter(self)
        self.minimize_btn.installEventFilter(self)
        self.maximize_btn.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle hover events for traffic light buttons"""
        if event.type() == QEvent.Type.Enter:
            if obj == self.close_btn:
                obj.setText("×")
            elif obj == self.minimize_btn:
                obj.setText("−")
            elif obj == self.maximize_btn:
                obj.setText("⤢" if self.is_maximized else "⤡")
        elif event.type() == QEvent.Type.Leave:
            obj.setText("")
        
        return super().eventFilter(obj, event)
        
    def update_title(self, title):
        """Update the window title"""
        self.title_label.setText(title)
        
    def minimize_window(self):
        """Minimize the parent window"""
        if self.parent_window:
            self.parent_window.showMinimized()
            
    def toggle_maximize(self):
        """Toggle maximize/restore"""
        if self.parent_window:
            if self.is_maximized:
                self.parent_window.showNormal()
                self.is_maximized = False
            else:
                self.parent_window.showMaximized()
                self.is_maximized = True
                
    def close_window(self):
        """Close the parent window"""
        if self.parent_window:
            self.parent_window.close()
            
    def fast_restart(self):
        """Fast restart Anki without syncing"""
        try:
            import sys
            import os
            from aqt import mw
            from aqt.qt import QApplication
            
            if mw:
                # Disable sync for fast restart
                if hasattr(mw, 'col') and mw.col:
                    # Mark collection as not modified to skip sync
                    mw.col.modSchema(check=False)
                    mw.col.modified = False
                    mw.col.save()
                
                # Get current working directory and executable
                current_dir = os.getcwd()
                executable = sys.executable
                script = sys.argv[0]
                
                # Close Anki cleanly but quickly
                QApplication.instance().setQuitOnLastWindowClosed(True)
                mw.close()
                
                # Restart using the same executable and arguments
                os.chdir(current_dir)
                if sys.platform == "darwin":  # macOS
                    os.execv(executable, [executable] + sys.argv)
                else:
                    os.execv(executable, [executable] + sys.argv)
                    
        except Exception as e:
            # Fallback to regular close if restart fails
            print(f"Fast restart failed: {e}")
            if self.parent_window:
                self.parent_window.close()
            
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if we're not clicking on a button
            click_pos = event.position().toPoint()
            for btn in [self.close_btn, self.minimize_btn, self.maximize_btn]:
                if btn.geometry().contains(click_pos):
                    return
            
            self.mouse_pos = event.globalPosition().toPoint()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if self.mouse_pos and event.buttons() == Qt.MouseButton.LeftButton:
            if self.parent_window:
                # Calculate the movement
                delta = event.globalPosition().toPoint() - self.mouse_pos
                self.parent_window.move(self.parent_window.pos() + delta)
                self.mouse_pos = event.globalPosition().toPoint()
                event.accept()
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.mouse_pos = None
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if we're not clicking on a button
            click_pos = event.position().toPoint()
            for btn in [self.close_btn, self.minimize_btn, self.maximize_btn]:
                if btn.geometry().contains(click_pos):
                    return
            
            self.toggle_maximize()
            event.accept()


def apply_custom_titlebar(window, theme_colors):
    """Apply a custom title bar to a window"""
    # Store original window flags
    original_flags = window.windowFlags()
    
    # Remove system title bar
    window.setWindowFlags(original_flags | Qt.WindowType.FramelessWindowHint)
    
    # Get the current central widget
    central_widget = window.centralWidget()
    
    # Create a new container widget
    container = QWidget()
    container_layout = QVBoxLayout()
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)
    container.setLayout(container_layout)
    
    # Create and add custom title bar
    titlebar = CustomTitleBar(window, theme_colors)
    container_layout.addWidget(titlebar)
    
    # Add the original central widget
    if central_widget:
        container_layout.addWidget(central_widget)
    
    # Set the new container as central widget
    window.setCentralWidget(container)
    
    # Connect window title changes
    if hasattr(window, 'windowTitleChanged'):
        window.windowTitleChanged.connect(titlebar.update_title)
    
    return titlebar