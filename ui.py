# UI Module - Theme selection dialog and settings

from aqt.qt import *
from aqt.utils import showInfo, tooltip
from typing import Dict, Any, Optional
import json

class ThemeDialog(QDialog):
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("VS Code Themes for Anki")
        self.setModal(True)
        self.resize(800, 650)  # Increased size for better preview
        
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
        
        self.theme_list = QListWidget()
        self.theme_list.itemClicked.connect(self.on_theme_selected)
        # Fix: Add keyboard navigation support
        self.theme_list.currentItemChanged.connect(self.on_theme_changed_keyboard)
        theme_layout.addWidget(self.theme_list)
        
        # Enhanced Preview System
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        theme_layout.addWidget(preview_label)
        
        # Create WebView for comprehensive preview
        try:
            from aqt.webview import AnkiWebView
            self.preview_web = AnkiWebView(parent=self)
            self.preview_web.setMinimumHeight(200)
            self.preview_web.setMaximumHeight(300)
            theme_layout.addWidget(self.preview_web)
            self.webview_available = True
        except ImportError:
            # Fallback to enhanced QTextEdit if WebView not available
            self.preview_text = QTextEdit()
            self.preview_text.setReadOnly(True)
            self.preview_text.setMaximumHeight(200)
            self.preview_text.setPlainText(self.get_fallback_preview_text())
            theme_layout.addWidget(self.preview_text)
            self.webview_available = False
        
        layout.addWidget(theme_group)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)
        
        self.apply_to_cards_cb = QCheckBox("Apply theme to cards")
        self.apply_to_ui_cb = QCheckBox("Apply theme to Anki UI (requires restart)")
        self.system_titlebar_cb = QCheckBox("🎨 Theme macOS title bar colors (matches theme)")
        
        # NEW: Automatic Anki theme sync option
        self.auto_sync_anki_theme_cb = QCheckBox("🔄 Automatically change Anki theme to match (Light/Dark)")
        
        # System title bar info
        titlebar_info = QLabel("💡 This option colors the native macOS title bar to match your theme colors!")
        titlebar_info.setWordWrap(True)
        titlebar_info.setStyleSheet("color: #666; font-size: 11px; margin: 5px 0;")
        
        # Auto sync info  
        auto_sync_info = QLabel("💡 When enabled, selecting a dark VS Code theme automatically switches Anki to dark mode!")
        auto_sync_info.setWordWrap(True)
        auto_sync_info.setStyleSheet("color: #666; font-size: 11px; margin: 5px 0;")
        
        settings_layout.addWidget(self.apply_to_cards_cb)
        settings_layout.addWidget(self.apply_to_ui_cb)
        settings_layout.addWidget(self.system_titlebar_cb)
        settings_layout.addWidget(titlebar_info)
        settings_layout.addWidget(self.auto_sync_anki_theme_cb)
        settings_layout.addWidget(auto_sync_info)
        
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
        
        # Add debug button
        self.debug_button = QPushButton("Debug Reviewer")
        self.debug_button.clicked.connect(self.debug_reviewer)
        self.debug_button.setToolTip("Analyze reviewer theming issues (check console for output)")
        button_layout.addWidget(self.debug_button)
        
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def get_fallback_preview_text(self):
        """Fallback preview text for when WebView is not available"""
        return """// VS Code Theme Preview
function example() {
    const message = "Hello, Anki!";
    console.log(message);
    return 42;
}

/* This is a comment */
const numbers = [1, 2, 3, 4, 5];
const result = numbers.map(n => n * 2);

// Enhanced preview showing more elements
class ThemePreview {
    constructor() {
        this.name = "VS Code Theme";
        this.isActive = true;
    }
    
    render() {
        return `Theme: ${this.name}`;
    }
}"""

    def get_comprehensive_preview_html(self, theme_id: str):
        """Generate comprehensive HTML preview for the theme"""
        theme = self.theme_manager.themes.get(theme_id)
        if not theme:
            return "<div>Theme not found</div>"
        
        colors = theme.get("colors", {})
        token_colors = theme.get("tokenColors", [])
        
        # Extract key colors with fallbacks
        bg_primary = colors.get('editor.background', '#282c34')
        bg_secondary = colors.get('sideBar.background', colors.get('activityBar.background', bg_primary))
        fg_primary = colors.get('editor.foreground', '#abb2bf')
        fg_secondary = colors.get('sideBar.foreground', fg_primary)
        accent_color = colors.get('focusBorder', colors.get('button.background', '#007acc'))
        button_bg = colors.get('button.background', accent_color)
        button_fg = colors.get('button.foreground', '#ffffff')
        selection_bg = colors.get('editor.selectionBackground', colors.get('list.activeSelectionBackground', '#3a3d41'))
        border_color = colors.get('panel.border', colors.get('editor.lineHighlightBorder', '#2c313a'))
        
        # Generate syntax highlighting colors
        syntax_colors = {}
        for token in token_colors:
            if isinstance(token, dict) and 'scope' in token and 'settings' in token:
                settings = token['settings']
                if 'foreground' in settings:
                    scope = token['scope']
                    if isinstance(scope, str):
                        if 'keyword' in scope:
                            syntax_colors['keyword'] = settings['foreground']
                        elif 'string' in scope:
                            syntax_colors['string'] = settings['foreground']
                        elif 'comment' in scope:
                            syntax_colors['comment'] = settings['foreground']
                        elif 'function' in scope:
                            syntax_colors['function'] = settings['foreground']
        
        # Fallback syntax colors if not found
        syntax_colors.setdefault('keyword', '#c678dd')
        syntax_colors.setdefault('string', '#98c379')
        syntax_colors.setdefault('comment', '#5c6370')
        syntax_colors.setdefault('function', '#61afef')
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: {bg_primary};
                    color: {fg_primary};
                    margin: 0;
                    padding: 15px;
                    font-size: 13px;
                    line-height: 1.4;
                }}
                
                .preview-container {{
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }}
                
                .header {{
                    background: {bg_secondary};
                    padding: 10px 15px;
                    border-radius: 6px;
                    border: 1px solid {border_color};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .header h3 {{
                    margin: 0;
                    color: {fg_primary};
                    font-size: 14px;
                    font-weight: 600;
                }}
                
                .buttons {{
                    display: flex;
                    gap: 8px;
                }}
                
                .btn {{
                    background: {button_bg};
                    color: {button_fg};
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: opacity 0.2s;
                }}
                
                .btn:hover {{
                    opacity: 0.8;
                }}
                
                .btn-secondary {{
                    background: {bg_secondary};
                    color: {fg_secondary};
                    border: 1px solid {border_color};
                }}
                
                .code-section {{
                    background: {bg_primary};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 15px;
                    font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
                    font-size: 12px;
                    line-height: 1.5;
                    overflow: auto;
                }}
                
                .keyword {{ color: {syntax_colors['keyword']}; font-weight: bold; }}
                .string {{ color: {syntax_colors['string']}; }}
                .comment {{ color: {syntax_colors['comment']}; font-style: italic; }}
                .function {{ color: {syntax_colors['function']}; }}
                .number {{ color: #d19a66; }}
                .operator {{ color: #56b6c2; }}
                
                .interface-elements {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}
                
                .panel {{
                    background: {bg_secondary};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 12px;
                }}
                
                .panel h4 {{
                    margin: 0 0 8px 0;
                    color: {fg_primary};
                    font-size: 12px;
                    font-weight: 600;
                }}
                
                .list-item {{
                    padding: 4px 8px;
                    border-radius: 3px;
                    margin: 2px 0;
                    color: {fg_secondary};
                    font-size: 11px;
                }}
                
                .list-item.selected {{
                    background: {selection_bg};
                    color: {fg_primary};
                }}
                
                .status-bar {{
                    background: {bg_secondary};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 8px 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 11px;
                }}
                
                .accent {{ color: {accent_color}; }}
                .theme-name {{
                    color: {accent_color};
                    font-weight: 600;
                    font-size: 16px;
                    text-align: center;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="preview-container">
                <div class="theme-name">🎨 {theme.get('displayName', theme_id)}</div>
                
                <div class="header">
                    <h3>📝 Anki Interface Preview</h3>
                    <div class="buttons">
                        <button class="btn">Study Now</button>
                        <button class="btn btn-secondary">Browse</button>
                        <button class="btn btn-secondary">Add</button>
                    </div>
                </div>
                
                <div class="code-section">
<span class="comment">/* Theme Code Preview */</span>
<span class="keyword">function</span> <span class="function">studyCards</span>() {{
    <span class="keyword">const</span> <span class="string">"Today's session"</span>;
    <span class="keyword">let</span> progress = <span class="number">75</span>;
    
    <span class="comment">// Your learning journey continues...</span>
    <span class="keyword">if</span> (progress <span class="operator">></span> <span class="number">50</span>) {{
        <span class="function">showSuccess</span>(<span class="string">"Great progress!"</span>);
    }}
    
    <span class="keyword">return</span> <span class="string">"Ready to learn more"</span>;
}}
                </div>
                
                <div class="interface-elements">
                    <div class="panel">
                        <h4>📚 Deck Browser</h4>
                        <div class="list-item selected">🧠 Medical Terminology (25 due)</div>
                        <div class="list-item">📖 Language Learning (12 due)</div>
                        <div class="list-item">⚗️ Chemistry (8 due)</div>
                        <div class="list-item">🗺️ Geography (15 due)</div>
                    </div>
                    
                    <div class="panel">
                        <h4>🎯 Study Options</h4>
                        <div class="list-item">🔄 Review scheduled cards</div>
                        <div class="list-item selected">✨ Learn new cards</div>
                        <div class="list-item">📊 View statistics</div>
                        <div class="list-item">⚙️ Deck options</div>
                    </div>
                </div>
                
                <div class="status-bar">
                    <span>📈 <span class="accent">Progress:</span> 45 cards studied today</span>
                    <span>⭐ <span class="accent">Streak:</span> 12 days</span>
                    <span>🎯 <span class="accent">Accuracy:</span> 87%</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
        
    def load_current_settings(self):
        """Load current settings into the dialog"""
        themes = self.theme_manager.get_available_themes()
        current_theme = self.theme_manager.config.get("current_theme", "")
        
        for theme_id, theme_name in themes.items():
            item = QListWidgetItem(theme_name)
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            self.theme_list.addItem(item)
            
            if theme_id == current_theme:
                self.theme_list.setCurrentItem(item)
                self.update_preview(theme_id)
        
        self.apply_to_cards_cb.setChecked(self.theme_manager.config.get("apply_to_cards", True))
        self.apply_to_ui_cb.setChecked(self.theme_manager.config.get("apply_to_ui", True))
        self.system_titlebar_cb.setChecked(self.theme_manager.config.get("system_titlebar_theming", True))
        self.auto_sync_anki_theme_cb.setChecked(self.theme_manager.config.get("auto_sync_anki_theme", True))
        self.custom_css_text.setPlainText(self.theme_manager.config.get("custom_css", ""))
    
    def on_theme_selected(self, item):
        """Handle theme selection (mouse click)"""
        theme_id = item.data(Qt.ItemDataRole.UserRole)
        self.update_preview(theme_id)
    
    def on_theme_changed_keyboard(self, current, previous):
        """Handle theme selection via keyboard navigation"""
        if current:
            theme_id = current.data(Qt.ItemDataRole.UserRole)
            self.update_preview(theme_id)
    
    def update_preview(self, theme_id: str):
        """Update the preview with the selected theme colors"""
        if self.webview_available:
            # Use comprehensive HTML preview
            html_content = self.get_comprehensive_preview_html(theme_id)
            self.preview_web.setHtml(html_content)
        else:
            # Fallback to styled QTextEdit
            theme = self.theme_manager.themes.get(theme_id)
            if not theme:
                return
            
            colors = theme.get("colors", {})
            bg_color = colors.get('editor.background', '#282c34')
            fg_color = colors.get('editor.foreground', '#abb2bf')
            
            preview_style = f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {fg_color};
                font-family: 'Fira Code', 'Monaco', 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 15px;
                border: 1px solid #3a3d41;
                border-radius: 6px;
            }}
            """
            self.preview_text.setStyleSheet(preview_style)
    
    def get_selected_theme(self) -> Optional[str]:
        """Get the currently selected theme ID"""
        current_item = self.theme_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def apply_settings(self):
        """Apply the selected settings"""
        try:
            theme_id = self.get_selected_theme()
            if theme_id:
                # Check if system title bar setting changed
                old_titlebar_setting = self.theme_manager.config.get("system_titlebar_theming", True)
                new_titlebar_setting = self.system_titlebar_cb.isChecked()
                titlebar_changed = old_titlebar_setting != new_titlebar_setting
                
                new_config = {
                    "current_theme": theme_id,
                    "apply_to_cards": self.apply_to_cards_cb.isChecked(),
                    "apply_to_ui": self.apply_to_ui_cb.isChecked(),
                    "system_titlebar_theming": new_titlebar_setting,
                    "auto_sync_anki_theme": self.auto_sync_anki_theme_cb.isChecked(),
                    "custom_css": self.custom_css_text.toPlainText()
                }
                
                # Update theme manager configuration
                self.theme_manager.config.update(new_config)
                self.theme_manager.save_config()
                
                # Apply the theme with new settings
                try:
                    self.theme_manager.apply_current_theme()
                    
                    # Provide feedback based on what changed
                    if titlebar_changed:
                        showInfo(f"✅ Settings applied! \n\n"
                               f"The system title bar setting changed. "
                               f"Please restart Anki to see the changes take effect.\n\n"
                               f"🎨 Theme colors have been updated immediately.")
                    else:
                        showInfo("✅ Theme applied successfully!")
                        
                except Exception as e:
                    showInfo(f"⚠️ Theme applied but with warnings: {str(e)}")
                    
                self.accept()
            else:
                showInfo("Please select a theme.")
        except Exception as e:
            showInfo(f"Failed to apply theme: {e}")
    
    def debug_reviewer(self):
        """Trigger reviewer debugging analysis"""
        print("🔍 USER TRIGGERED REVIEWER DEBUG")
        try:
            self.theme_manager.debug_reviewer_context()
            tooltip("Debug analysis completed - check console output")
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            showInfo(f"Debug failed: {e}")

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
                
                if "colors" not in theme_data:
                    showInfo("Invalid theme file: missing 'colors' section")
                    return
                
                theme_name = theme_data.get("name", "Imported Theme")
                
                import os
                theme_id = os.path.basename(file_path)[:-5].lower().replace(" ", "_")
                theme_path = os.path.join(self.theme_manager.themes_dir, f"{theme_id}.json")
                
                with open(theme_path, 'w') as f:
                    json.dump(theme_data, f, indent=2)
                
                self.theme_manager.load_themes()
                
                self.theme_list.clear()
                self.load_current_settings()
                
                tooltip(f"Theme '{theme_name}' imported successfully!")
                
            except Exception as e:
                showInfo(f"Error importing theme: {str(e)}")
