# Theme Manager - Handles loading and applying themes

import json
import os
from typing import Dict, Any, Optional
from aqt import mw
from aqt.theme import theme_manager as anki_theme_manager
from aqt.qt import QApplication, QWidget, Qt, QVBoxLayout, QHBoxLayout, QGridLayout, QLayoutItem, QTimer
from .custom_titlebar import apply_custom_titlebar

class ThemeManager:
    def __init__(self, addon_dir: str, config: Dict[str, Any], addon_module_name: str = None):
        print(f"🎨 Initializing ThemeManager...")
        print(f"📂 Addon dir: {addon_dir}")
        print(f"⚙️ Config: {config}")
        
        self.addon_dir = addon_dir
        self.themes_dir = os.path.join(addon_dir, "themes")
        self.config = config
        self.addon_module_name = addon_module_name
        self.themes = {}
        self._css_cache = None
        self._qt_stylesheet_cache = None
        self._current_theme_id_cache = None
        
        # Theme validator is optional - if it fails to load, we'll use basic validation
        self.validator = None
        
        print("📚 Loading themes...")
        self.load_themes()
        print(f"✅ ThemeManager initialized with {len(self.themes)} themes")

    def load_themes(self):
        """Load and validate themes from the themes directory"""
        try:
            if not os.path.exists(self.themes_dir):
                os.makedirs(self.themes_dir)
                return
            
            excluded_files = {'themes_metadata.json', 'validation_report.json'}
            theme_count = 0
            
            for filename in os.listdir(self.themes_dir):
                if filename.endswith('.json') and filename not in excluded_files and not filename.endswith('.backup'):
                    theme_path = os.path.join(self.themes_dir, filename)
                    try:
                        with open(theme_path, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                        
                        # Basic validation - only check essential requirements
                        if self._is_valid_theme(theme_data):
                            theme_id = filename[:-5]  # Remove .json extension
                            self.themes[theme_id] = theme_data
                            theme_count += 1
                            print(f"✅ Loaded theme: {theme_data.get('name', theme_id)}")
                        else:
                            print(f"⚠️ Skipped invalid theme: {filename}")
                            
                    except Exception as e:
                        print(f"❌ Error loading theme {filename}: {e}")
                        
            print(f"📚 Loaded {theme_count} themes successfully")
            
            # Ensure we have at least one fallback theme if no themes loaded
            if not self.themes:
                print("⚠️ No themes loaded, creating fallback theme")
                self._create_fallback_theme()
                
        except Exception as e:
            print(f"Error in load_themes: {e}")
            # Ensure we have at least one fallback theme
            if not self.themes:
                self._create_fallback_theme()

    def _is_valid_theme(self, theme_data):
        """Basic theme validation - only essential requirements"""
        try:
            # Must be a dictionary
            if not isinstance(theme_data, dict):
                return False
            
            # Must have colors section
            if 'colors' not in theme_data:
                return False
            
            colors = theme_data['colors']
            if not isinstance(colors, dict):
                return False
            
            # Must have at least some essential editor colors
            essential_colors = ['editor.background', 'editor.foreground']
            has_essential = any(color in colors for color in essential_colors)
            
            if not has_essential:
                return False
            
            # Optional: Add theme name if missing
            if 'name' not in theme_data:
                theme_data['name'] = "Unnamed Theme"
            
            # Optional: Add theme type if missing
            if 'type' not in theme_data:
                # Guess based on background color
                bg_color = colors.get('editor.background', '#000000')
                if bg_color.startswith('#') and len(bg_color) >= 7:
                    try:
                        r = int(bg_color[1:3], 16)
                        g = int(bg_color[3:5], 16) 
                        b = int(bg_color[5:7], 16)
                        brightness = (r * 299 + g * 587 + b * 114) / 1000
                        theme_data['type'] = "light" if brightness > 127 else "dark"
                    except:
                        theme_data['type'] = "dark"
                else:
                    theme_data['type'] = "dark"
            
            return True
            
        except Exception as e:
            print(f"Theme validation error: {e}")
            return False

    def _create_fallback_theme(self):
        """Create a basic fallback theme if no themes are available"""
        fallback_theme = {
            "name": "Default Dark",
            "type": "dark",
            "colors": {
                "editor.background": "#282c34",
                "editor.foreground": "#abb2bf",
                "editorGroup.border": "#181a1f",
                "button.background": "#404754",
                "button.foreground": "#ffffff",
                "button.hoverBackground": "#5a6375",
                "input.background": "#1e2227",
                "sideBar.background": "#21252b",
                "list.hoverBackground": "#2c323c",
                "focusBorder": "#007acc",
                "editor.selectionBackground": "#3e4451"
            }
        }
        self.themes["default_dark"] = fallback_theme
        print("Created fallback theme due to theme loading issues")

    def get_available_themes(self) -> Dict[str, str]:
        result = {}
        for theme_id, theme_data in self.themes.items():
            if isinstance(theme_data, dict) and 'name' in theme_data:
                result[theme_id] = theme_data.get("name", theme_id)
        return result

    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        return self.themes.get(current_theme_id)

    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration with validation and fallbacks"""
        try:
            # Ensure required config keys with defaults
            default_config = {
                "current_theme": "one_dark_pro",
                "apply_to_cards": True,
                "apply_to_ui": True,
                "use_custom_titlebar": False,
                "custom_css": ""
            }
            
            # Merge with defaults to ensure all keys are present
            validated_config = {**default_config, **new_config}
            
            # Validate theme exists
            if validated_config["current_theme"] not in self.themes:
                print(f"Warning: Theme '{validated_config['current_theme']}' not found, falling back to default")
                if "default_dark" in self.themes:
                    validated_config["current_theme"] = "default_dark"
                elif self.themes:
                    validated_config["current_theme"] = next(iter(self.themes.keys()))
                else:
                    print("Error: No themes available!")
                    return
            
            self.config = validated_config
            
            if mw and self.addon_module_name:
                mw.addonManager.writeConfig(self.addon_module_name, self.config)
            
            # Invalidate cache
            self._css_cache = None
            self._qt_stylesheet_cache = None
            self._current_theme_id_cache = None

            # Apply theme immediately - no additional refresh needed
            self.apply_current_theme()
            
        except Exception as e:
            print(f"Error updating config: {e}")

    def get_current_theme_css(self) -> str:
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        if self._css_cache and self._current_theme_id_cache == current_theme_id:
            return self._css_cache

        theme = self.get_current_theme()
        if not theme:
            return ""
        colors = theme.get("colors", {})
        
        # Define conservative CSS that only targets essential elements
        bg_color = colors.get('editor.background', '#282c34')
        fg_color = colors.get('editor.foreground', '#abb2bf')
        
        css = f"""
            /* CONSERVATIVE STYLING - Only essential elements */
            :root {{
                --bg-color: {bg_color};
                --fg-color: {fg_color};
                --border-color: {colors.get('editorGroup.border', '#181a1f')};
                --button-bg: {colors.get('button.background', '#404754')};
                --button-fg: {colors.get('button.foreground', '#ffffff')};
                --button-hover-bg: {colors.get('button.hoverBackground', '#5a6375')};
                --link-fg: {colors.get('textLink.foreground', '#61afef')};
                --hover-bg: {colors.get('list.hoverBackground', '#2c323c')};
                --sidebar-bg: {colors.get('sideBar.background', '#21252b')};
            }}
            
            /* MAIN BACKGROUND ONLY */
            html, body {{
                background-color: {bg_color} !important;
                color: {fg_color} !important;
            }}
            
            /* DECK BROWSER SPECIFIC STYLING */
            body.deckbrowser {{
                background-color: {bg_color} !important;
                color: {fg_color} !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* TABLE STYLING - Deck list */
            body.deckbrowser table,
            body.deckbrowser table tr,
            body.deckbrowser table td,
            body.deckbrowser table th {{
                background-color: {bg_color} !important;
                color: {fg_color} !important;
                border-color: {colors.get('editorGroup.border', '#181a1f')} !important;
            }}
            
            body.deckbrowser table[cellspacing="0"][cellpadding="3"] {{
                border-spacing: 0 !important;
                border-collapse: collapse !important;
                margin-top: 0 !important;
                background-color: {bg_color} !important;
            }}
            
            /* DECK ROW STYLING */
            body.deckbrowser table tr {{
                background-color: {bg_color} !important;
            }}
            
            body.deckbrowser table tr:hover {{
                background-color: {colors.get('list.hoverBackground', '#2c323c')} !important;
            }}
            
            body.deckbrowser table tr:first-child td {{
                border-bottom: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                font-weight: bold;
                background-color: {colors.get('sideBar.background', '#21252b')} !important;
            }}
            
            /* DECK NAME AND COUNT STYLING */
            body.deckbrowser table td {{
                padding: 8px !important;
                background-color: transparent !important;
                color: {fg_color} !important;
            }}
            
            /* LINKS AND BUTTONS */
            a, a:link, a:visited {{
                color: {colors.get('textLink.foreground', '#61afef')} !important;
                text-decoration: none;
            }}
            
            a:hover {{
                color: {colors.get('textLink.activeForeground', colors.get('textLink.foreground', '#61afef'))} !important;
            }}
            
            button, input[type="button"], input[type="submit"] {{
                background-color: {colors.get('button.background', '#404754')} !important;
                color: {colors.get('button.foreground', '#ffffff')} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            
            button:hover {{
                background-color: {colors.get('button.hoverBackground', '#5a6375')} !important;
            }}
            
            /* OVERVIEW SCREEN STYLING */
            body.overview {{
                background-color: {bg_color} !important;
                color: {fg_color} !important;
            }}
            
            /* FORM ELEMENTS */
            input, select, textarea {{
                background-color: {colors.get('input.background', '#1e2227')} !important;
                color: {fg_color} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                border-radius: 4px;
                padding: 6px;
            }}
            
            /* DIALOGS AND MENUS */
            .menu, .dialog, .popup {{
                background-color: {bg_color} !important;
                color: {fg_color} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
            }}
            
            /* SCROLLBARS */
            ::-webkit-scrollbar {{ width: 12px; height: 12px; }}
            ::-webkit-scrollbar-track {{ background: {bg_color}; }}
            ::-webkit-scrollbar-thumb {{ 
                background-color: {colors.get('scrollbarSlider.background', '#4e566680')}; 
                border-radius: 6px; 
            }}
            ::-webkit-scrollbar-thumb:hover {{ 
                background-color: {colors.get('scrollbarSlider.hoverBackground', '#5a637580')}; 
            }}
        """
        self._css_cache = css
        self._current_theme_id_cache = current_theme_id
        return css

    def apply_current_theme(self):
        """Apply the current theme with proper error handling"""
        print("🎨 Starting theme application...")
        try:
            current_theme_id = self.config.get("current_theme", "one_dark_pro")
            print(f"🎨 Current theme ID: {current_theme_id}")
            
            theme = self.get_current_theme()
            if not theme:
                print(f"❌ Warning: Theme '{current_theme_id}' not found")
                # Try to use any available theme
                if self.themes:
                    fallback_id = next(iter(self.themes.keys()))
                    print(f"🔄 Falling back to: {fallback_id}")
                    self.config["current_theme"] = fallback_id
                    theme = self.themes[fallback_id]
                else:
                    print("❌ No themes available at all!")
                    return
            
            print(f"✅ Theme found: {theme.get('name', 'Unknown')}")
            colors = theme.get("colors", {})
            print(f"🎨 Theme has {len(colors)} colors")
            
            # Check if UI application is enabled
            apply_to_ui = self.config.get("apply_to_ui", True)
            print(f"🎨 Apply to UI: {apply_to_ui}")
            
            # 1. Always generate CSS for web content injection
            self._css_cache = None  # Force regeneration
            css = self.get_current_theme_css()
            print(f"🌐 Web CSS generated: {len(css)} characters")
            
            # 2. Apply Qt styling if enabled
            if apply_to_ui:
                print("🎨 Generating and applying Qt stylesheet...")
                try:
                    if self._qt_stylesheet_cache and self._current_theme_id_cache == current_theme_id:
                        qt_stylesheet = self._qt_stylesheet_cache
                        print("✅ Using cached Qt stylesheet")
                    else:
                        qt_stylesheet = self._generate_qt_stylesheet(colors)
                        self._qt_stylesheet_cache = qt_stylesheet
                        self._current_theme_id_cache = current_theme_id
                        print(f"✅ Generated new Qt stylesheet ({len(qt_stylesheet)} chars)")

                    # Apply to QApplication if available
                    app_applied = False
                    try:
                        app = QApplication.instance()
                        if app:
                            app.setStyleSheet(qt_stylesheet)
                            app_applied = True
                            print("✅ Applied stylesheet to QApplication")
                        else:
                            print("⚠️ QApplication instance not found")
                    except Exception as e:
                        print(f"⚠️ QApplication styling failed: {e}")
                    
                    # Apply to main window if available  
                    mw_applied = False
                    try:
                        if mw:
                            mw.setStyleSheet(qt_stylesheet)
                            mw_applied = True
                            print("✅ Applied stylesheet to main window")
                        else:
                            print("⚠️ Main window (mw) not available")
                    except Exception as e:
                        print(f"⚠️ Main window styling failed: {e}")
                    
                    if app_applied or mw_applied:
                        print("✅ Qt styling applied successfully!")
                    else:
                        print("⚠️ Qt styling failed - using CSS-only mode")
                    
                    # Set Anki night mode if possible
                    try:
                        is_dark = theme.get("type", "dark") == "dark"
                        if hasattr(anki_theme_manager, 'set_night_mode'):
                            anki_theme_manager.set_night_mode(is_dark)
                            print(f"✅ Set Anki night mode: {is_dark}")
                        else:
                            print("ℹ️ Anki night mode not available")
                    except Exception as e:
                        print(f"⚠️ Night mode setting failed: {e}")
                    
                except Exception as e:
                    print(f"❌ Qt styling completely failed: {e}")
                    print("🔄 Falling back to CSS-only mode")
            else:
                print("ℹ️ Qt UI theming disabled in config")
            
            print("🎨 Theme application completed!")
                    
        except Exception as e:
            print(f"❌ Error applying theme: {e}")
            import traceback
            traceback.print_exc()

    def _apply_custom_titlebar(self, window, colors):
        try:
            titlebar = apply_custom_titlebar(window, colors)
            window._custom_titlebar_applied = True
            window._custom_titlebar_widget = titlebar
        except Exception as e:
            print(f"Failed to apply custom title bar: {e}")

    def _generate_qt_stylesheet(self, colors: Dict[str, str]) -> str:
        # Color Palette
        bg = colors.get('editor.background', '#282c34')
        fg = colors.get('editor.foreground', '#abb2bf')
        border = colors.get('editorGroup.border', '#181a1f')
        selection_bg = colors.get('editor.selectionBackground', '#3e4451')
        hover_bg = colors.get('list.hoverBackground', '#2c323c')
        
        button_bg = colors.get('button.background', '#404754')
        button_fg = colors.get('button.foreground', '#ffffff')
        button_hover = colors.get('button.hoverBackground', '#5a6375')
        
        input_bg = colors.get('input.background', '#1e2227')
        sidebar_bg = colors.get('sideBar.background', '#21252b')
        focus_border = colors.get('focusBorder', '#007acc')
        
        # Consistent Sizing
        radius = "4px"
        
        return f"""
            /* --- GLOBAL --- */
            QWidget {{
                background-color: {bg};
                color: {fg};
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }}
            QMainWindow, QDialog {{
                background-color: {bg};
            }}
            QToolTip {{
                background-color: {sidebar_bg};
                color: {fg};
                border: 1px solid {border};
                padding: 5px;
            }}

            /* --- BUTTONS --- */
            QPushButton {{
                background-color: {button_bg};
                color: {button_fg};
                padding: 8px 12px;
                border-radius: {radius};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {selection_bg};
            }}
            QPushButton:focus {{
                border: 1px solid {focus_border};
            }}

            /* --- BOTTOM BAR (REVIEWER) --- */
            QWidget#bottomArea, QFrame#BottomBar, QWidget[objectName="bottom"], 
            QFrame[objectName="bottomArea"], QToolBar#reviewer-toolbar {{
                background-color: {sidebar_bg} !important;
                border-top: 1px solid {border} !important;
                border-bottom: none !important;
                border-left: none !important;
                border-right: none !important;
            }}
            
            /* REVIEWER BOTTOM BUTTONS */
            QWidget#bottomArea QPushButton, QFrame#BottomBar QPushButton,
            QWidget[objectName="bottom"] QPushButton, QFrame[objectName="bottomArea"] QPushButton {{
                background-color: {button_bg} !important;
                color: {button_fg} !important;
                min-height: 28px !important;
                border: 1px solid {border} !important;
                border-radius: {radius} !important;
                padding: 6px 12px !important;
                margin: 2px !important;
            }}
            
            QWidget#bottomArea QPushButton:hover, QFrame#BottomBar QPushButton:hover,
            QWidget[objectName="bottom"] QPushButton:hover, QFrame[objectName="bottomArea"] QPushButton:hover {{
                background-color: {button_hover} !important;
            }}
            
            QWidget#bottomArea QPushButton:pressed, QFrame#BottomBar QPushButton:pressed,
            QWidget[objectName="bottom"] QPushButton:pressed, QFrame[objectName="bottomArea"] QPushButton:pressed {{
                background-color: {selection_bg} !important;
            }}

            /* --- STATUS BAR & COUNTERS --- */
            QStatusBar {{
                background-color: {sidebar_bg};
                border-top: 1px solid {border};
            }}
            /* This targets the answer count area */
            .night_mode .card-counts, .card-counts {{
                background-color: {sidebar_bg} !important;
                padding: 2px 5px;
            }}

            /* --- INPUTS & FIELDS --- */
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {{
                background-color: {input_bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: {radius};
                padding: 5px;
                selection-background-color: {selection_bg};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
                border: 1px solid {focus_border};
            }}
            QComboBox {{
                background-color: {input_bg};
                border: 1px solid {border};
                border-radius: {radius};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                border: 1px solid {border};
                selection-background-color: {selection_bg};
            }}

            /* --- MENUS --- */
            QMenuBar {{
                background-color: {sidebar_bg};
            }}
            QMenuBar::item:selected {{
                background-color: {hover_bg};
            }}
            QMenu {{
                background-color: {sidebar_bg};
                border: 1px solid {border};
            }}
            QMenu::item:selected {{
                background-color: {hover_bg};
            }}

            /* --- SCROLLBARS --- */
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar:horizontal {{ height: 10px; }}
            QScrollBar::handle {{
                background: {button_bg};
                border-radius: 5px;
            }}
            QScrollBar::handle:hover {{
                background: {button_hover};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
                width: 0px;
            }}

            /* --- OTHER WIDGETS --- */
            QGroupBox {{
                border: 1px solid {border};
                border-radius: {radius};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QTabWidget::pane {{
                border-top: 1px solid {border};
            }}
            QTabBar::tab:selected {{
                background: {bg};
                border: 1px solid {border};
                border-bottom-color: {bg};
            }}
            QTabBar::tab:!selected {{
                background: {sidebar_bg};
                border: 1px solid {border};
            }}
            QSplitter::handle {{
                background-color: {border};
                width: 1px;
                height: 1px;
            }}
            QProgressBar {{
                border: 1px solid {border};
                border-radius: {radius};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {focus_border};
                border-radius: {radius};
            }}
            QDockWidget {{
                background-color: {sidebar_bg};
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }}
            QDockWidget::title {{
                background-color: {sidebar_bg};
                border-bottom: 1px solid {border};
                padding: 4px;
            }}
        """

    def get_reviewer_safe_css(self) -> str:
        """Generate CSS safe for card reviewer - only targets interface elements, not card content"""
        theme = self.get_current_theme()
        if not theme:
            return ""
        
        colors = theme.get("colors", {})
        
        # Get essential colors with fallbacks
        bg_color = colors.get("editor.background", "#1e1e1e")
        fg_color = colors.get("editor.foreground", "#cccccc") 
        button_bg = colors.get("button.background", "#0e639c")
        button_fg = colors.get("button.foreground", "#ffffff")
        button_hover = colors.get("button.hoverBackground", "#1177bb")
        border_color = colors.get("editorGroup.border", "#444444")
        input_bg = colors.get("input.background", "#2d2d30")
        
        # CSS that only targets reviewer interface, NOT card content
        # Using high specificity and !important to override Anki's default styles
        reviewer_css = f"""
/* AGGRESSIVE Reviewer interface styling - HIGH SPECIFICITY to override Anki defaults */

/* Body and HTML - force background consistency */
html, html body {{
    background-color: {bg_color} !important;
    color: {fg_color} !important;
}}

/* ALL possible button containers in reviewer */
html body #bottomLeft,
html body #bottomCenter, 
html body #bottomRight,
html body .bottom,
html body #bottom,
html body .bottom-area,
html body .reviewer-bottom,
body #bottomLeft,
body #bottomCenter, 
body #bottomRight,
body .bottom,
body #bottom {{
    background-color: {bg_color} !important;
    border-top: 1px solid {border_color} !important;
    padding: 8px !important;
    margin: 0 !important;
}}

/* ALL possible buttons - maximum specificity */
html body #bottomLeft button,
html body #bottomCenter button,
html body #bottomRight button,
html body .bottom button,
html body #bottom button,
html body button.btn,
html body .reviewer-button,
html body input[type="button"],
html body input[type="submit"],
body #bottomLeft button,
body #bottomCenter button,
body #bottomRight button,
body .bottom button,
body #bottom button,
body button,
#bottomLeft button,
#bottomCenter button,
#bottomRight button,
.bottom button,
#bottom button,
button {{
    background-color: {button_bg} !important;
    color: {button_fg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 4px !important;
    padding: 6px 12px !important;
    margin: 2px !important;
    font-family: inherit !important;
    font-size: inherit !important;
    text-shadow: none !important;
    box-shadow: none !important;
}}

/* Button hover states - maximum specificity */
html body #bottomLeft button:hover,
html body #bottomCenter button:hover,
html body #bottomRight button:hover,
html body .bottom button:hover,
html body #bottom button:hover,
html body button.btn:hover,
html body .reviewer-button:hover,
html body input[type="button"]:hover,
html body input[type="submit"]:hover,
body button:hover,
button:hover {{
    background-color: {button_hover} !important;
    color: {button_fg} !important;
}}

/* Top navigation and toolbar areas */
html body .toolbar,
html body #header,
html body .nav-bar,
html body #topNav,
body .toolbar,
body #header,
.toolbar,
#header {{
    background-color: {bg_color} !important;
    color: {fg_color} !important;
    border-bottom: 1px solid {border_color} !important;
}}

/* Any remaining interface elements */
html body .sidebar,
html body .side-panel,
html body .info,
html body .status,
html body .reviewer-info {{
    background-color: {bg_color} !important;
    color: {fg_color} !important;
}}

/* Input fields - high specificity */
html body input[type="text"],
html body input[type="search"],
html body textarea,
body input,
input {{
    background-color: {input_bg} !important;
    color: {fg_color} !important;
    border: 1px solid {border_color} !important;
}}

/* Force override any lingering default styling */
* {{
    /* Apply to everything except card content areas */
}}

*:not(#qa):not(.card):not(.question):not(.answer):not(.card-content):not(#middle) {{
    /* Force background consistency for all non-card elements */
    background-color: {bg_color} !important;
    color: {fg_color} !important;
}}

/* Explicitly protect card content from any changes */
#qa,
#qa *,
.card,
.card *,
.question,
.question *,
.answer,
.answer *,
.card-content,
.card-content *,
#middle,
#middle * {{
    /* Deliberately no styling - preserve card content exactly */
    background-color: unset !important;
    color: unset !important;
}}

/* Focus states */
html body button:focus,
html body input:focus {{
    outline: 2px solid {button_bg} !important;
    outline-offset: 2px !important;
}}
"""
        
        return reviewer_css.strip()

    def debug_reviewer_context(self):
        """Debug function to inspect reviewer context and CSS application"""
        print("🔍 === REVIEWER DEBUG ANALYSIS ===")
        
        try:
            # Check if we have a current theme
            theme = self.get_current_theme()
            if not theme:
                print("❌ No current theme found")
                return
            
            print(f"✅ Current theme: {theme.get('name', 'Unknown')}")
            
            # Generate and show reviewer CSS
            reviewer_css = self.get_reviewer_safe_css()
            print(f"✅ Generated reviewer CSS: {len(reviewer_css)} characters")
            
            # Check config
            print(f"⚙️ Config apply_to_ui: {self.config.get('apply_to_ui', 'NOT SET')}")
            print(f"⚙️ Config apply_to_cards: {self.config.get('apply_to_cards', 'NOT SET')}")
            
            # Check if mw is available and try to get current screen info
            try:
                if mw and hasattr(mw, 'state'):
                    print(f"🔍 Anki main window state: {mw.state}")
                if mw and hasattr(mw, 'reviewer') and mw.reviewer:
                    print("🔍 Reviewer object exists")
                    if hasattr(mw.reviewer, 'web') and mw.reviewer.web:
                        print("🔍 Reviewer web object exists")
                        # Try to get some info about the web content
                        try:
                            web = mw.reviewer.web
                            print(f"🔍 Reviewer web title: {web.title()}")
                        except Exception as e:
                            print(f"⚠️ Couldn't get web info: {e}")
                else:
                    print("⚠️ No reviewer object found")
            except Exception as e:
                print(f"⚠️ Error inspecting Anki state: {e}")
            
            # Show first part of reviewer CSS for inspection
            print("🔍 First 500 characters of reviewer CSS:")
            print("-" * 50)
            print(reviewer_css[:500])
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Debug analysis failed: {e}")
            import traceback
            traceback.print_exc()
