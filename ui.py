# UI Module - Theme selection dialog and settings

from aqt.qt import *
from aqt.utils import showInfo, tooltip
from typing import Dict, Any
import json

class ThemeDialog(QDialog):
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("VS Code Themes for Anki")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Theme selection
        theme_group = QGroupBox("Select Theme")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        # Theme list
        self.theme_list = QListWidget()
        self.theme_list.itemClicked.connect(self.on_theme_selected)
        theme_layout.addWidget(self.theme_list)
        
        # Theme preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText("""// VS Code Theme Preview
function example() {
    const message = "Hello, Anki!";
    console.log(message);
    return 42;
}

/* This is a comment */
const numbers = [1, 2, 3, 4, 5];
const result = numbers.map(n => n * 2);""")
        theme_layout.addWidget(QLabel("Preview:"))
        theme_layout.addWidget(self.preview_text)
        
        layout.addWidget(theme_group)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)
        
        self.apply_to_cards_cb = QCheckBox("Apply theme to cards")
        self.apply_to_ui_cb = QCheckBox("Apply theme to Anki UI (requires restart)")
        self.use_custom_titlebar_cb = QCheckBox("Use custom title bar (hides system title bar)")
        
        settings_layout.addWidget(self.apply_to_cards_cb)
        settings_layout.addWidget(self.apply_to_ui_cb)
        settings_layout.addWidget(self.use_custom_titlebar_cb)
        
        layout.addWidget(settings_group)
        
        # Custom CSS
        custom_css_group = QGroupBox("Custom CSS (Advanced)")
        custom_css_layout = QVBoxLayout()
        custom_css_group.setLayout(custom_css_layout)
        
        self.custom_css_text = QPlainTextEdit()
        self.custom_css_text.setMaximumHeight(100)
        self.custom_css_text.setPlaceholderText("Enter custom CSS here...")
        custom_css_layout.addWidget(self.custom_css_text)
        
        layout.addWidget(custom_css_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import VS Code Theme...")
        self.import_button.clicked.connect(self.import_theme)
        button_layout.addWidget(self.import_button)
        
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def load_current_settings(self):
        """Load current settings into the dialog"""
        # Populate theme list
        themes = self.theme_manager.get_available_themes()
        current_theme = self.theme_manager.config.get("current_theme", "")
        
        for theme_id, theme_name in themes.items():
            item = QListWidgetItem(theme_name)
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            self.theme_list.addItem(item)
            
            if theme_id == current_theme:
                self.theme_list.setCurrentItem(item)
                self.update_preview(theme_id)
        
        # Load checkboxes
        self.apply_to_cards_cb.setChecked(
            self.theme_manager.config.get("apply_to_cards", True)
        )
        self.apply_to_ui_cb.setChecked(
            self.theme_manager.config.get("apply_to_ui", True)
        )
        self.use_custom_titlebar_cb.setChecked(
            self.theme_manager.config.get("use_custom_titlebar", False)
        )
        
        # Load custom CSS
        self.custom_css_text.setPlainText(
            self.theme_manager.config.get("custom_css", "")
        )
    
    def on_theme_selected(self, item):
        """Handle theme selection"""
        theme_id = item.data(Qt.ItemDataRole.UserRole)
        self.update_preview(theme_id)
    
    def update_preview(self, theme_id: str):
        """Update the preview with the selected theme colors"""
        theme = self.theme_manager.themes.get(theme_id)
        if not theme:
            return
        
        colors = theme.get("colors", {})
        
        # Apply basic colors to preview
        bg_color = colors.get('editor.background', '#282c34')
        fg_color = colors.get('editor.foreground', '#abb2bf')
        
        # Create a simple preview style
        preview_style = f"""
        QTextEdit {{
            background-color: {bg_color};
            color: {fg_color};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            padding: 10px;
        }}
        """
        
        self.preview_text.setStyleSheet(preview_style)
    
    def apply_settings(self):
        """Apply the selected settings"""
        # Get selected theme
        current_item = self.theme_list.currentItem()
        if current_item:
            theme_id = current_item.data(Qt.ItemDataRole.UserRole)
            
            # Update configuration
            new_config = {
                "current_theme": theme_id,
                "apply_to_cards": self.apply_to_cards_cb.isChecked(),
                "apply_to_ui": self.apply_to_ui_cb.isChecked(),
                "use_custom_titlebar": self.use_custom_titlebar_cb.isChecked(),
                "custom_css": self.custom_css_text.toPlainText()
            }
            
            self.theme_manager.update_config(new_config)
            
            # Show success message
            if self.apply_to_ui_cb.isChecked():
                tooltip("Theme applied! Please restart Anki for UI changes to take full effect.")
            else:
                tooltip("Theme applied!")
            
            self.accept()
        else:
            showInfo("Please select a theme.")
    
    def import_theme(self):
        """Import a VS Code theme from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select VS Code Theme JSON File",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    theme_data = json.load(f)
                
                # Validate theme structure
                if "colors" not in theme_data:
                    showInfo("Invalid theme file: missing 'colors' section")
                    return
                
                # Get theme name
                theme_name = theme_data.get("name", "Imported Theme")
                
                # Save theme
                import os
                theme_id = os.path.basename(file_path)[:-5].lower().replace(" ", "_")
                theme_path = os.path.join(self.theme_manager.themes_dir, f"{theme_id}.json")
                
                with open(theme_path, 'w') as f:
                    json.dump(theme_data, f, indent=2)
                
                # Reload themes
                self.theme_manager.load_themes()
                
                # Refresh theme list
                self.theme_list.clear()
                self.load_current_settings()
                
                tooltip(f"Theme '{theme_name}' imported successfully!")
                
            except Exception as e:
                showInfo(f"Error importing theme: {str(e)}")