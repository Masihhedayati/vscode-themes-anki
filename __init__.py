# VS Code Themes for Anki
# Main addon entry point

import os
from aqt import mw, gui_hooks
from aqt.utils import qconnect, showInfo
from aqt.qt import QAction
from anki.cards import Card
from anki.decks import DeckManager
from anki.notes import Note
from aqt.browser import Browser
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from . import theme_manager
from . import ui

addon_dir = os.path.dirname(__file__)
theme_mgr = None
hooks_registered = False

def cleanup_hooks():
    """Properly clean up hooks when addon unloads"""
    global hooks_registered
    try:
        if hooks_registered and hasattr(gui_hooks, 'webview_will_set_content'):
            gui_hooks.webview_will_set_content.remove(inject_theme_css)
            print("🧹 Hook cleanup completed")
            hooks_registered = False
    except Exception as e:
        print(f"⚠️ Hook cleanup failed: {e}")

def initialize_addon():
    """Initialize the VS Code Themes addon"""
    global theme_mgr
    
    print("🚀 Initializing VS Code Themes addon...")
    
    try:
        # Get addon directory and config
        print("📁 Setting up addon directory and config...")
        addon_dir = os.path.dirname(__file__)
        print(f"📂 Addon directory: {addon_dir}")
        
        # Load configuration with fallback handling
        print("⚙️ Loading configuration...")
        config = {}
        try:
            config = mw.addonManager.getConfig(__name__)
            if not config:
                config = {}
        except Exception as e:
            print(f"⚠️ Config load failed: {e}, using defaults")
            config = {}
            
        # Merge with default config to ensure all keys exist
        default_config = {
            "current_theme": "one_dark_pro",
            "apply_to_cards": True,
            "apply_to_ui": True,
            "system_titlebar_theming": True,  # Enable native title bar theming
            "custom_css": ""
        }
        config = {**default_config, **config}
        
        # Initialize the theme manager with error handling
        print("📁 Initializing theme manager...")
        try:
            theme_mgr = theme_manager.ThemeManager(addon_dir, config, __name__)
            print(f"✅ Theme manager initialized with {len(theme_mgr.themes)} themes")
        except ValueError as e:
            print(f"❌ Theme manager initialization failed: {e}")
            showInfo(f"VS Code Themes addon failed to initialize: {e}")
            return
        except Exception as e:
            print(f"❌ Unexpected error initializing theme manager: {e}")
            import traceback
            traceback.print_exc()
            showInfo(f"VS Code Themes addon failed to initialize: {e}")
            return
        
        # Register hooks with validation
        print("🔗 Registering hooks...")
        global hooks_registered
        
        try:
            if hasattr(gui_hooks, 'webview_will_set_content'):
                gui_hooks.webview_will_set_content.append(inject_theme_css)
                hooks_registered = True
                print("✅ Webview hook registered")
            else:
                print("⚠️ Webview hook not available")
        except Exception as e:
            print(f"⚠️ Hook registration failed: {e}")
        
        if not hooks_registered:
            print("⚠️ No hooks registered - theming may be limited")
        
        # Add to tools menu with error handling
        print("📋 Adding to Anki tools menu...")
        try:
            action = QAction("VS Code Themes", mw)
            action.triggered.connect(show_theme_dialog)
            mw.form.menuTools.addAction(action)
            print("✅ Menu item added")
        except Exception as e:
            print(f"⚠️ Menu setup failed: {e}")
        
        # Setup system title bar theming if enabled (macOS) with error handling
        print("🎨 Checking system title bar theming settings...")
        try:
            system_titlebar_theming = config.get("system_titlebar_theming", True)
            if system_titlebar_theming:
                from . import system_titlebar
                print("✅ System title bar theming module loaded")
            else:
                print("ℹ️ System title bar theming disabled in config")
        except ImportError as e:
            print(f"⚠️ System title bar theming not available: {e}")
        except Exception as e:
            print(f"⚠️ System title bar theming setup failed: {e}")
        
        # Initialize addon conflict resolution system
        print("🔧 Initializing addon conflict resolution...")
        try:
            # Import and test conflict manager availability
            from .addon_conflict_manager import get_conflict_manager, resolve_all_conflicts
            
            # Initialize conflict manager with current config
            conflict_manager = get_conflict_manager(config)
            
            # Perform initial conflict detection (without resolution)
            conflicts = conflict_manager.detect_conflicting_addons()
            critical_conflicts = [c for c in conflicts if c['enabled'] and c['conflict_level'] == 'CRITICAL']
            
            if critical_conflicts:
                print(f"⚠️ Detected {len(critical_conflicts)} critical addon conflicts")
                print("🔧 Conflicts will be resolved during theme application")
            else:
                print("✅ No critical addon conflicts detected")
                
        except ImportError as e:
            print(f"⚠️ Addon conflict manager not available: {e}")
        except Exception as e:
            print(f"⚠️ Conflict manager initialization failed: {e}")
        
        # Apply initial theme with error handling
        print("🎨 Applying initial theme...")
        try:
            if theme_mgr:
                theme_mgr.apply_current_theme()
                print("✅ Initial theme applied")
        except Exception as e:
            print(f"⚠️ Initial theme application failed: {e}")
            print("🔄 Theme will be applied when dialog is opened")
        
        print("🎉 VS Code Themes addon initialization completed!")
        
    except Exception as e:
        print(f"❌ Addon initialization failed: {e}")
        import traceback
        traceback.print_exc()
        # Don't show error dialog for initialization failures to avoid startup interruption
        print("🔄 Addon will operate in limited mode")

def show_theme_dialog():
    """Show the theme selection dialog"""
    global theme_mgr
    
    if not theme_mgr:
        showInfo("Theme manager not initialized. Please restart Anki.")
        return
        
    try:
        print("🎨 Opening theme dialog...")
        from .ui import ThemeDialog
        dialog = ThemeDialog(mw, theme_mgr)
        dialog.exec()
    except Exception as e:
        print(f"❌ Error opening theme dialog: {e}")
        showInfo(f"Error opening theme dialog: {e}")

def inject_theme_css(web_content, context):
    """Inject theme CSS into web content with context awareness and error handling"""
    global theme_mgr
    
    # Early return with error handling if theme manager not ready
    if not theme_mgr:
        print("⚠️ Theme manager not initialized, skipping CSS injection")
        return
    
    try:
        print(f"🌐 CSS injection called for context: {context}")
        context_str = str(context).lower()
        print(f"🔍 Context string (lowercase): {context_str}")
        
        # Context-aware filtering to protect card content (Phase 2 improvement)
        unsafe_contexts = ["card_layout", "clayout", "editor", "card_", "note_"]
        if any(unsafe in context_str for unsafe in unsafe_contexts):
            print(f"🛡️ Skipping CSS injection for protected context: {context}")
            return
        
        # Enhanced context detection for better CSS application
        css = None
        style_id = "vscode-theme-default"
        
        try:
            # Detect specific context types for targeted CSS
            if "reviewer" in context_str:
                print(f"🎨 REVIEWER CONTEXT - Injecting reviewer-safe CSS")
                css = theme_mgr.get_reviewer_safe_css()
                style_id = "vscode-theme-reviewer"
            elif any(ctx in context_str for ctx in ["deckbrowser", "browser", "main"]):
                print(f"🎨 DECK BROWSER CONTEXT - Injecting full CSS")
                css = theme_mgr.get_current_theme_css()
                style_id = "vscode-theme-deckbrowser"
            elif "overview" in context_str:
                print(f"🎨 OVERVIEW CONTEXT - Injecting full CSS")
                css = theme_mgr.get_current_theme_css()
                style_id = "vscode-theme-overview"
            else:
                print(f"🎨 GENERAL CONTEXT - Injecting full CSS for: {context}")
                css = theme_mgr.get_current_theme_css()
                style_id = "vscode-theme-general"
                
            if not css:
                print("⚠️ No CSS available from theme manager")
                return
                
            print(f"🔍 CSS length: {len(css)} characters")
            
            # Inject main theme CSS
            web_content.head += f'<style id="{style_id}">{css}</style>'
            print(f"✅ {style_id} CSS injection completed")
            
            # Inject custom CSS if available (always safe)
            custom_css = theme_mgr.config.get("custom_css", "")
            if custom_css:
                print(f"🎨 Injecting {len(custom_css)} characters of custom CSS")
                web_content.head += f'<style id="vscode-theme-custom-css">{custom_css}</style>'
                
        except AttributeError as e:
            print(f"⚠️ Theme manager method not available: {e}")
        except Exception as e:
            print(f"⚠️ CSS generation failed: {e}")
            # Try fallback CSS
            try:
                fallback_css = "/* VS Code Theme: Error loading theme, using minimal fallback */ body { background: #1e1e1e; color: #cccccc; }"
                web_content.head += f'<style id="vscode-theme-fallback">{fallback_css}</style>'
                print("🔄 Applied fallback CSS")
            except:
                print("❌ Even fallback CSS failed")
        
        print(f"🔍 Final web_content.head length: {len(web_content.head)} characters")
        print("✅ CSS injection process completed")
        
    except Exception as e:
        print(f"❌ CSS injection failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        # Don't re-raise to prevent breaking Anki's webview loading

# Initialize the addon
initialize_addon()
