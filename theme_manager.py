# Theme Manager - Handles loading and applying themes

import json
import os
from typing import Dict, Any, Optional
from aqt import mw
from aqt.theme import theme_manager as anki_theme_manager
from aqt.qt import QApplication, QWidget, Qt, QVBoxLayout, QHBoxLayout, QGridLayout, QLayoutItem, QTimer

# Import our new Anki theme integration service
try:
    from .anki_theme_integration import anki_theme_integration, ThemeClassificationService
except ImportError:
    # Fallback if import fails
    anki_theme_integration = None
    ThemeClassificationService = None
    print("⚠️ Anki theme integration service not available")

# Import permanent theme consistency fix
try:
    from .permanent_theme_consistency_fix import permanent_fix_manager, apply_permanent_theme_fix
    PERMANENT_FIX_AVAILABLE = True
    print("✅ Permanent theme consistency fix loaded")
except ImportError as e:
    permanent_fix_manager = None
    apply_permanent_theme_fix = None
    PERMANENT_FIX_AVAILABLE = False
    print(f"⚠️ Permanent theme consistency fix not available: {e}")

# Import addon conflict manager
try:
    from .addon_conflict_manager import get_conflict_manager, resolve_all_conflicts
    CONFLICT_MANAGER_AVAILABLE = True
    print("✅ Addon conflict manager loaded")
except ImportError as e:
    get_conflict_manager = None
    resolve_all_conflicts = None
    CONFLICT_MANAGER_AVAILABLE = False
    print(f"⚠️ Addon conflict manager not available: {e}")

class ThemeManager:
    def __init__(self, addon_dir: str, config: Dict[str, Any], addon_module_name: str = None):
        print(f"🎨 Initializing ThemeManager...")
        print(f"📂 Addon dir: {addon_dir}")
        print(f"⚙️ Config: {config}")
        print(f"🏷️ Module name: {addon_module_name}")
        
        # Validate critical parameters
        if not addon_module_name:
            raise ValueError("addon_module_name is required for configuration persistence")
        
        self.addon_dir = addon_dir
        self.themes_dir = os.path.join(addon_dir, "themes")
        self.config = config
        self.addon_module_name = addon_module_name
        self.themes = {}
        
        # Enhanced caching system for performance (Phase 2 improvement)
        self._css_cache = {}  # Cache per theme_id
        self._qt_stylesheet_cache = {}  # Cache per theme_id  
        self._reviewer_css_cache = {}  # Cache per theme_id
        self._current_theme_id = None
        self._cache_version = 1  # Increment to invalidate all caches
        
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
                "custom_css": "",
                "glass_navbar_enabled": True,
                "auto_sync_anki_theme": True  # NEW: Enable automatic Anki theme sync by default
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
            self.save_config()
            
            # Invalidate all caches when config changes (Phase 2 improvement)
            self._invalidate_all_caches()

            # Apply theme immediately - no additional refresh needed
            self.apply_current_theme()
            
        except Exception as e:
            print(f"Error updating config: {e}")
    
    def save_config(self):
        """Save current configuration to Anki's addon manager"""
        try:
            if mw and self.addon_module_name:
                mw.addonManager.writeConfig(self.addon_module_name, self.config)
                print("✅ Configuration saved")
            else:
                print("⚠️ Cannot save config: mw or addon_module_name not available")
        except Exception as e:
            print(f"❌ Error saving config: {e}")

    def get_current_theme_css(self) -> str:
        """Get CSS for current theme with caching for performance"""
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        
        # Check cache first (Phase 2 performance improvement)
        cache_key = self._get_cache_key(current_theme_id, "main")
        if cache_key in self._css_cache:
            print(f"💨 Using cached CSS for {current_theme_id}")
            return self._css_cache[cache_key]
        
        print(f"🔨 Generating unified CSS for {current_theme_id}")
        css = self._generate_theme_css(current_theme_id, "general")
        
        # Cache the result
        self._css_cache[cache_key] = css
        print(f"💾 Cached CSS for {current_theme_id} ({len(css)} chars)")
        
        return css
    
    def _generate_theme_css(self, theme_id: str, context_type: str = "general") -> str:
        """Generate unified, consistent CSS for specific theme and context"""
        theme = self.themes.get(theme_id)
        if not theme:
            print(f"⚠️ Theme {theme_id} not found")
            return ""
        
        colors = theme.get("colors", {})
        if not colors:
            print(f"⚠️ No colors found in theme {theme_id}")
            return ""
        
        print(f"🎨 Generating unified CSS for {theme_id} (context: {context_type})")
        
        # Build unified CSS with consistent structure
        css_parts = []
        
        # 1. CSS Variables for consistency
        css_parts.append(self._generate_unified_css_variables(colors))
        
        # 2. Base interface styling 
        css_parts.append(self._generate_base_interface_css())
        
        # 3. Context-specific styling
        if context_type != "general":
            context_css = self._generate_context_specific_css(context_type)
            if context_css:
                css_parts.append(context_css)
        else:
            # For general contexts, include all common context styles
            css_parts.append(self._generate_context_specific_css("deckbrowser"))
            css_parts.append(self._generate_context_specific_css("overview"))
        
        # Combine all parts
        unified_css = "\n".join(css_parts)
        
        print(f"✅ Generated unified CSS: {len(unified_css)} characters")
        return unified_css.strip()

    def apply_current_theme(self):
        """Apply the current theme with proper error handling"""
        print("🎨 Starting theme application...")
        try:
            # STEP 1: RESOLVE ADDON CONFLICTS FIRST
            if CONFLICT_MANAGER_AVAILABLE:
                print("🔧 Checking for addon conflicts before theme application...")
                try:
                    conflict_manager = get_conflict_manager(self.config)
                    conflicts_resolved = conflict_manager.resolve_conflicts_automatically()
                    
                    if conflicts_resolved:
                        print("✅ All critical addon conflicts resolved")
                    else:
                        print("⚠️ Some conflicts remain, nuclear CSS will be applied")
                    
                    # Start monitoring for future conflicts
                    if not conflict_manager.monitoring_active:
                        conflict_manager.start_conflict_monitoring()
                        
                except Exception as e:
                    print(f"⚠️ Conflict resolution failed, continuing with theme application: {e}")
            else:
                print("ℹ️ Addon conflict manager not available, skipping conflict resolution")
            
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
            
            # 1. Always generate CSS for web content injection (using cached version)
            css = self.get_current_theme_css()
            print(f"🌐 Web CSS ready: {len(css)} characters")
            
            # 2. Update system title bar to match theme (macOS)
            try:
                from . import system_titlebar
                system_titlebar.system_titlebar_themer.apply_theme_to_titlebar(colors)
                print("✅ System title bar updated to match theme")
            except Exception as e:
                print(f"⚠️ System title bar theming failed: {e}")
            
            # 3. Update glass navigation bar if enabled (secondary feature)
            try:
                from . import custom_navbar
                glass_navbar_enabled = self.config.get("glass_navbar_enabled", False)
                if glass_navbar_enabled and custom_navbar.navbar_manager.navbar:
                    print("🌟 Updating glass navigation bar with theme colors...")
                    custom_navbar.navbar_manager.update_theme(colors)
                    print("✅ Glass navigation bar updated")
                else:
                    print("ℹ️ Glass navigation bar not enabled or not created")
            except Exception as e:
                print(f"⚠️ Glass navigation bar update failed: {e}")
            
            # 4. Apply Qt styling if enabled
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
                    
                    # Enhanced Anki theme synchronization
                    try:
                        auto_sync_enabled = self.config.get("auto_sync_anki_theme", True)
                        
                        if auto_sync_enabled and anki_theme_integration:
                            # Use new comprehensive sync service
                            sync_success = anki_theme_integration.sync_anki_theme(theme)
                            if sync_success:
                                print("✅ Advanced Anki theme sync completed")
                            else:
                                print("⚠️ Advanced sync failed, trying fallback method")
                                # Fallback to original method
                                is_dark = theme.get("type", "dark") == "dark"
                                if hasattr(anki_theme_manager, 'set_night_mode'):
                                    anki_theme_manager.set_night_mode(is_dark)
                                    print(f"✅ Fallback Anki night mode: {is_dark}")
                        else:
                            # Original method when auto-sync is disabled
                            is_dark = theme.get("type", "dark") == "dark"
                            if hasattr(anki_theme_manager, 'set_night_mode'):
                                anki_theme_manager.set_night_mode(is_dark)
                                print(f"✅ Basic Anki night mode: {is_dark}")
                            else:
                                print("ℹ️ Anki night mode not available")
                                
                    except Exception as e:
                        print(f"⚠️ Anki theme sync failed: {e}")
                        # Ultimate fallback
                        try:
                            is_dark = theme.get("type", "dark") == "dark"
                            if hasattr(anki_theme_manager, 'set_night_mode'):
                                anki_theme_manager.set_night_mode(is_dark)
                                print(f"✅ Emergency fallback night mode: {is_dark}")
                        except Exception as e2:
                            print(f"❌ All Anki theme sync methods failed: {e2}")
                    
                    # PERMANENT THEME CONSISTENCY FIX
                    try:
                        if PERMANENT_FIX_AVAILABLE and permanent_fix_manager:
                            print("🔧 Applying permanent theme consistency fix...")
                            fix_success = permanent_fix_manager.apply_permanent_fix(self)
                            if fix_success:
                                print("✅ Permanent consistency fix applied successfully")
                            else:
                                print("⚠️ Permanent fix had issues, but basic theme still applied")
                        else:
                            print("ℹ️ Permanent fix not available, using standard theme application")
                            
                    except Exception as e:
                        print(f"⚠️ Permanent fix error: {e}")
                        # Don't let permanent fix errors break basic theme application
                        print("🔄 Continuing with standard theme application")
                    
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

    def _generate_qt_stylesheet(self, colors: Dict[str, str]) -> str:
        """Generate Qt stylesheet with caching for application-level theming"""
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        
        # Check cache first (Phase 2 performance improvement)
        cache_key = self._get_cache_key(current_theme_id, "qt")
        if cache_key in self._qt_stylesheet_cache:
            print(f"💨 Using cached Qt stylesheet for {current_theme_id}")
            return self._qt_stylesheet_cache[cache_key]
        
        print(f"🔨 Generating Qt stylesheet for {current_theme_id}")
        
        qt_stylesheet = self._build_qt_stylesheet(colors)
        
        # Cache the result
        self._qt_stylesheet_cache[cache_key] = qt_stylesheet
        print(f"💾 Cached Qt stylesheet for {current_theme_id} ({len(qt_stylesheet)} chars)")
        
        return qt_stylesheet
    
    def _build_qt_stylesheet(self, colors: Dict[str, str]) -> str:
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
        """Generate CSS safe for card reviewer with caching - only targets interface elements, not card content"""
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        
        # Check cache first (Phase 2 performance improvement)
        cache_key = self._get_cache_key(current_theme_id, "reviewer")
        if cache_key in self._reviewer_css_cache:
            print(f"💨 Using cached reviewer CSS for {current_theme_id}")
            return self._reviewer_css_cache[cache_key]
        
        print(f"🔨 Generating unified reviewer CSS for {current_theme_id}")
        
        # Use the unified CSS generation system with reviewer context
        reviewer_css = self._generate_theme_css(current_theme_id, "reviewer")
        
        # Cache the result
        self._reviewer_css_cache[cache_key] = reviewer_css
        print(f"💾 Cached reviewer CSS for {current_theme_id} ({len(reviewer_css)} chars)")
        
        return reviewer_css

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

    def _invalidate_all_caches(self):
        """Invalidate all CSS caches when configuration changes"""
        print("🧹 Invalidating all CSS caches")
        self._css_cache.clear()
        self._qt_stylesheet_cache.clear()
        self._reviewer_css_cache.clear()
        self._cache_version += 1
        print(f"✅ All caches cleared, version bumped to {self._cache_version}")
        
    def force_theme_refresh(self):
        """Force immediate theme refresh with cache invalidation"""
        print("🔄 Forcing theme refresh...")
        self._invalidate_all_caches()
        self.apply_current_theme()
        print("✅ Theme refresh completed")
    
    def _invalidate_theme_cache(self, theme_id: str):
        """Invalidate caches for a specific theme"""
        print(f"🧹 Invalidating cache for theme: {theme_id}")
        self._css_cache.pop(theme_id, None)
        self._qt_stylesheet_cache.pop(theme_id, None)
        self._reviewer_css_cache.pop(theme_id, None)
    
    def _get_cache_key(self, theme_id: str, css_type: str) -> str:
        """Generate cache key including version for cache invalidation"""
        return f"{theme_id}_{css_type}_v{self._cache_version}"

    def _generate_unified_css_variables(self, colors: Dict[str, str]) -> str:
        """Generate CSS custom properties for consistent theming across all contexts"""
        return f"""
            :root {{
                /* Core theme colors */
                --vscode-bg-primary: {colors.get('editor.background', '#282c34')};
                --vscode-bg-secondary: {colors.get('sideBar.background', '#21252b')};
                --vscode-bg-tertiary: {colors.get('input.background', '#1e2227')};
                --vscode-fg-primary: {colors.get('editor.foreground', '#abb2bf')};
                --vscode-fg-secondary: {colors.get('editorLineNumber.foreground', '#5c6370')};
                --vscode-border: {colors.get('editorGroup.border', '#181a1f')};
                --vscode-focus: {colors.get('focusBorder', '#007acc')};
                
                /* Interactive elements */
                --vscode-button-bg: {colors.get('button.background', '#404754')};
                --vscode-button-fg: {colors.get('button.foreground', '#ffffff')};
                --vscode-button-hover: {colors.get('button.hoverBackground', '#5a6375')};
                --vscode-link: {colors.get('textLink.foreground', '#61afef')};
                --vscode-link-hover: {colors.get('textLink.activeForeground', colors.get('textLink.foreground', '#61afef'))};
                
                /* States */
                --vscode-hover-bg: {colors.get('list.hoverBackground', '#2c323c')};
                --vscode-selection-bg: {colors.get('editor.selectionBackground', '#3e4451')};
                --vscode-active-bg: {colors.get('list.activeSelectionBackground', '#2c323c')};
                
                /* Scrollbars */
                --vscode-scrollbar-bg: {colors.get('scrollbar.shadow', 'transparent')};
                --vscode-scrollbar-thumb: {colors.get('scrollbarSlider.background', '#4e566680')};
                --vscode-scrollbar-thumb-hover: {colors.get('scrollbarSlider.hoverBackground', '#5a637580')};
            }}
        """

    def _generate_base_interface_css(self) -> str:
        """Generate base CSS that applies to all interface elements consistently"""
        return """
            /* UNIFIED BASE STYLING FOR ALL ANKI INTERFACES */
            html, body {
                background-color: var(--vscode-bg-primary) !important;
                color: var(--vscode-fg-primary) !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* CONSISTENT BUTTON STYLING */
            button, input[type="button"], input[type="submit"], .btn {
                background-color: var(--vscode-button-bg) !important;
                color: var(--vscode-button-fg) !important;
                border: 1px solid var(--vscode-border) !important;
                border-radius: 4px !important;
                padding: 6px 12px !important;
                margin: 2px !important;
                font-family: inherit !important;
                font-size: inherit !important;
                cursor: pointer;
                text-shadow: none !important;
                box-shadow: none !important;
            }
            
            button:hover, input[type="button"]:hover, input[type="submit"]:hover, .btn:hover {
                background-color: var(--vscode-button-hover) !important;
                color: var(--vscode-button-fg) !important;
            }
            
            button:focus, input[type="button"]:focus, input[type="submit"]:focus, .btn:focus {
                outline: 2px solid var(--vscode-focus) !important;
                outline-offset: 2px !important;
            }
            
            /* CONSISTENT LINK STYLING */
            a, a:link, a:visited {
                color: var(--vscode-link) !important;
                text-decoration: none;
            }
            
            a:hover, a:active {
                color: var(--vscode-link-hover) !important;
                text-decoration: underline;
            }
            
            /* CONSISTENT FORM ELEMENTS */
            input, select, textarea {
                background-color: var(--vscode-bg-tertiary) !important;
                color: var(--vscode-fg-primary) !important;
                border: 1px solid var(--vscode-border) !important;
                border-radius: 4px;
                padding: 6px;
            }
            
            input:focus, select:focus, textarea:focus {
                border-color: var(--vscode-focus) !important;
                outline: none;
                box-shadow: 0 0 0 2px var(--vscode-focus)40 !important;
            }
            
            /* CONSISTENT SCROLLBARS */
            ::-webkit-scrollbar {
                width: 12px;
                height: 12px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--vscode-bg-primary);
            }
            
            ::-webkit-scrollbar-thumb {
                background-color: var(--vscode-scrollbar-thumb);
                border-radius: 6px;
                border: 2px solid var(--vscode-bg-primary);
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background-color: var(--vscode-scrollbar-thumb-hover);
            }
        """

    def _generate_context_specific_css(self, context_type: str) -> str:
        """Generate CSS specific to different Anki contexts"""
        if context_type == "deckbrowser":
            return """
                /* DECK BROWSER SPECIFIC STYLING */
                body.deckbrowser {
                    background-color: var(--vscode-bg-primary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
                
                body.deckbrowser table {
                    background-color: var(--vscode-bg-primary) !important;
                    border-collapse: collapse !important;
                    width: 100% !important;
                }
                
                body.deckbrowser table tr {
                    background-color: var(--vscode-bg-primary) !important;
                    border-bottom: 1px solid var(--vscode-border) !important;
                }
                
                body.deckbrowser table tr:hover {
                    background-color: var(--vscode-hover-bg) !important;
                }
                
                body.deckbrowser table tr:first-child {
                    background-color: var(--vscode-bg-secondary) !important;
                    font-weight: bold;
                }
                
                body.deckbrowser table td, body.deckbrowser table th {
                    background-color: transparent !important;
                    color: var(--vscode-fg-primary) !important;
                    padding: 8px !important;
                    border-color: var(--vscode-border) !important;
                }
            """
        elif context_type == "overview":
            return """
                /* OVERVIEW SCREEN STYLING */
                body.overview {
                    background-color: var(--vscode-bg-primary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
                
                body.overview .description {
                    background-color: var(--vscode-bg-secondary) !important;
                    color: var(--vscode-fg-primary) !important;
                    border: 1px solid var(--vscode-border) !important;
                    border-radius: 4px;
                    padding: 12px;
                    margin: 10px 0;
                }
                
                body.overview .review-data {
                    background-color: var(--vscode-bg-primary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
            """
        elif context_type == "reviewer":
            return """
                /* REVIEWER INTERFACE STYLING WITH REFINED CARD CONTENT HANDLING */
                
                /* Theme the main card container and interface areas */
                html, body {
                    background-color: var(--vscode-bg-primary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
                
                /* Card container - theme the background but preserve content */
                #qa {
                    background-color: var(--vscode-bg-primary) !important;
                    padding: 20px !important;
                }
                
                /* Middle section theming */
                #middle {
                    background-color: var(--vscode-bg-primary) !important;
                }
                
                /* IMPROVED BOTTOM BAR with better padding */
                #bottomLeft, #bottomCenter, #bottomRight, 
                .bottom, #bottom, .bottom-area, .reviewer-bottom {
                    background-color: var(--vscode-bg-secondary) !important;
                    border-top: 1px solid var(--vscode-border) !important;
                    padding: 16px 20px !important;  /* Increased from 8px to 16px */
                    margin: 0 !important;
                }
                
                /* Better button spacing in bottom bar */
                #bottomLeft button, #bottomCenter button, #bottomRight button,
                .bottom button, #bottom button {
                    margin: 4px 8px !important;  /* More generous margins */
                    padding: 8px 16px !important;  /* Better button padding */
                    background-color: var(--vscode-button-bg) !important;
                    color: var(--vscode-button-fg) !important;
                    border: 1px solid var(--vscode-border) !important;
                    border-radius: 4px !important;
                }
                
                #bottomLeft button:hover, #bottomCenter button:hover, #bottomRight button:hover,
                .bottom button:hover, #bottom button:hover {
                    background-color: var(--vscode-button-hover) !important;
                }
                
                /* Top navigation area with better padding */
                .toolbar, #header, .nav-bar, #topNav {
                    background-color: var(--vscode-bg-secondary) !important;
                    color: var(--vscode-fg-primary) !important;
                    border-bottom: 1px solid var(--vscode-border) !important;
                    padding: 12px 20px !important;  /* Better header padding */
                }
                
                /* Sidebar and info panels */
                .sidebar, .side-panel, .info, .status, .reviewer-info {
                    background-color: var(--vscode-bg-secondary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
                
                /* Card container should use theme colors for background */
                .card {
                    background-color: transparent !important;  /* Let parent background show through */
                }
                
                /* Specific targeting for medical content layout */
                body.card {
                    background-color: var(--vscode-bg-primary) !important;
                    color: var(--vscode-fg-primary) !important;
                }
                
                /* REFINED CARD CONTENT PROTECTION - Only protect actual text content */
                .card-content, .question .card-text, .answer .card-text,
                .card p, .card div[style*="font"], .card span[style*="font"] {
                    /* Preserve specific card text styling - but allow container theming */
                }
            """
        else:
            return ""
    
    def get_theme_classification_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive theme classification statistics.
        
        Returns:
            Dictionary with theme classification information
        """
        if not ThemeClassificationService:
            return {"error": "Theme classification service not available"}
        
        try:
            stats = ThemeClassificationService.get_theme_statistics(self.themes)
            print(f"📊 Theme Statistics:")
            print(f"   Total themes: {stats['total_themes']}")
            print(f"   Dark themes: {stats['dark_themes']} ({stats['dark_percentage']:.1f}%)")
            print(f"   Light themes: {stats['light_themes']} ({stats['light_percentage']:.1f}%)")
            return stats
        except Exception as e:
            print(f"❌ Error getting theme statistics: {e}")
            return {"error": str(e)}
    
    def classify_current_theme(self) -> str:
        """
        Get the light/dark classification of the current theme.
        
        Returns:
            'light' or 'dark' or 'unknown'
        """
        if not ThemeClassificationService:
            return 'unknown'
        
        try:
            current_theme_id = self.config.get("current_theme", "one_dark_pro")
            classification = ThemeClassificationService.get_theme_type_for_anki(
                current_theme_id, self.themes
            )
            print(f"🎨 Current theme '{current_theme_id}' classified as: {classification}")
            return classification
        except Exception as e:
            print(f"❌ Error classifying current theme: {e}")
            return 'unknown'
    
    def get_anki_sync_status(self) -> Dict[str, Any]:
        """
        Get comprehensive Anki theme sync status.
        
        Returns:
            Dictionary with sync status information
        """
        if not anki_theme_integration:
            return {"error": "Anki theme integration service not available"}
        
        try:
            sync_status = anki_theme_integration.get_theme_sync_status()
            sync_status['config_enabled'] = self.config.get("auto_sync_anki_theme", True)
            sync_status['current_vs_code_theme_type'] = self.classify_current_theme()
            
            print(f"🔍 Anki Sync Status:")
            print(f"   Auto-sync enabled: {sync_status['config_enabled']}")
            print(f"   Current Anki mode: {'dark' if sync_status.get('current_anki_night_mode') else 'light'}")
            print(f"   VS Code theme type: {sync_status['current_vs_code_theme_type']}")
            
            return sync_status
        except Exception as e:
            print(f"❌ Error getting sync status: {e}")
            return {"error": str(e)}
    
    def apply_permanent_consistency_fix(self) -> bool:
        """
        Manually apply the permanent theme consistency fix.
        
        This method can be called directly to force apply the permanent fix
        in case of theme inconsistency issues.
        
        Returns:
            bool: True if fix was applied successfully
        """
        try:
            if PERMANENT_FIX_AVAILABLE and permanent_fix_manager:
                print("🛠️ Manually applying permanent theme consistency fix...")
                fix_success = permanent_fix_manager.apply_permanent_fix(self)
                if fix_success:
                    print("✅ Manual permanent fix applied successfully")
                    return True
                else:
                    print("❌ Manual permanent fix failed")
                    return False
            else:
                print("❌ Permanent fix not available")
                return False
                
        except Exception as e:
            print(f"💥 Error applying manual permanent fix: {e}")
            return False
    
    def diagnose_theme_consistency(self) -> bool:
        """
        Run diagnostic on theme consistency and automatically fix issues.
        
        Returns:
            bool: True if diagnosis and any needed fixes were successful
        """
        try:
            print("🔍 Running theme consistency diagnosis...")
            
            # Check if permanent fix is available
            if not PERMANENT_FIX_AVAILABLE:
                print("❌ Permanent fix system not available")
                return False
            
            # Check theme manager state
            current_theme = self.get_current_theme()
            if not current_theme:
                print("❌ No current theme available")
                return False
            
            # Check CSS generation
            css = self.get_current_theme_css()
            if not css:
                print("❌ CSS generation failed")
                return False
            
            # Check for CSS variables and specificity
            has_css_vars = '--vscode-bg-primary' in css
            has_high_specificity = 'html body' in css
            
            print(f"📊 CSS Variables present: {has_css_vars}")
            print(f"📊 High specificity selectors: {has_high_specificity}")
            
            # Apply fix if needed
            if not has_css_vars or not has_high_specificity:
                print("🔧 Issues detected, applying permanent fix...")
                return self.apply_permanent_consistency_fix()
            else:
                print("✅ Theme consistency appears healthy")
                return True
                
        except Exception as e:
            print(f"💥 Diagnosis error: {e}")
            return False
    
    def get_addon_conflict_report(self) -> Dict[str, Any]:
        """Get comprehensive report of addon conflicts and their status"""
        if not CONFLICT_MANAGER_AVAILABLE:
            return {
                'available': False,
                'error': 'Conflict manager not available'
            }
        
        try:
            conflict_manager = get_conflict_manager(self.config)
            report = conflict_manager.get_conflict_report()
            report['available'] = True
            return report
        except Exception as e:
            return {
                'available': False,
                'error': f'Failed to get conflict report: {e}'
            }
    
    def resolve_addon_conflicts_manually(self) -> bool:
        """Manually trigger addon conflict resolution"""
        if not CONFLICT_MANAGER_AVAILABLE:
            print("❌ Conflict manager not available")
            return False
        
        try:
            print("🔧 Manually resolving addon conflicts...")
            conflict_manager = get_conflict_manager(self.config)
            success = conflict_manager.resolve_conflicts_automatically()
            
            if success:
                print("✅ Manual conflict resolution completed successfully")
                # Re-apply theme after conflict resolution
                self.apply_current_theme()
            else:
                print("⚠️ Some conflicts could not be resolved automatically")
            
            return success
        except Exception as e:
            print(f"❌ Manual conflict resolution failed: {e}")
            return False
    
    def apply_nuclear_css_emergency(self) -> bool:
        """Emergency function to apply nuclear CSS for addon conflicts"""
        if not CONFLICT_MANAGER_AVAILABLE:
            print("❌ Conflict manager not available")
            return False
        
        try:
            print("🚀 Applying emergency nuclear CSS...")
            conflict_manager = get_conflict_manager(self.config)
            success = conflict_manager.apply_nuclear_css()
            
            if success:
                print("✅ Emergency nuclear CSS applied successfully")
            
            return success
        except Exception as e:
            print(f"❌ Emergency nuclear CSS failed: {e}")
            return False
