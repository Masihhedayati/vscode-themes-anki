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

def initialize_addon():
    """Initialize the VS Code Themes addon"""
    global theme_mgr
    
    print("🚀 Initializing VS Code Themes addon...")
    
    try:
        # Get addon directory and config
        print("📁 Setting up addon directory and config...")
        addon_dir = os.path.dirname(__file__)
        print(f"📂 Addon directory: {addon_dir}")
        
        # Load configuration with defaults
        try:
            config = mw.addonManager.getConfig(__name__) or {}
            print(f"⚙️ Config loaded: {config}")
        except Exception as e:
            print(f"⚠️ Config load failed: {e}, using defaults")
            config = {
                "current_theme": "one_dark_pro",
                "apply_to_cards": True,
                "apply_to_ui": True,
                "use_custom_titlebar": False,
                "custom_css": ""
            }
        
        # Initialize the theme manager with correct parameters
        print("📁 Initializing theme manager...")
        theme_mgr = theme_manager.ThemeManager(addon_dir, config, __name__)
        print(f"✅ Theme manager initialized with {len(theme_mgr.themes)} themes")
        
        # Register hooks with validation
        print("🔗 Registering hooks...")
        hook_registered = False
        
        try:
            if hasattr(gui_hooks, 'webview_will_set_content'):
                gui_hooks.webview_will_set_content.append(lambda web_content, context: inject_theme_css(web_content, context))
                print("✅ Webview hook registered")
                hook_registered = True
            else:
                print("⚠️ Webview hook not available")
        except Exception as e:
            print(f"⚠️ Hook registration failed: {e}")
        
        if not hook_registered:
            print("⚠️ No hooks registered - theming may be limited")
        
        # Add to tools menu
        print("📋 Adding to Anki tools menu...")
        action = QAction("VS Code Themes", mw)
        action.triggered.connect(show_theme_dialog)
        mw.form.menuTools.addAction(action)
        print("✅ Menu item added")
        
        # Apply initial theme
        print("🎨 Applying initial theme...")
        try:
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
    """Inject theme CSS into web content"""
    global theme_mgr
    try:
        print(f"🌐 CSS injection called for context: {context}")
        print(f"🔍 Context type: {type(context)}")
        print(f"🔍 Context string representation: {str(context)}")
        
        if not theme_mgr:
            print("⚠️ Theme manager not initialized, skipping CSS injection")
            return
        
        # Get theme CSS
        css = theme_mgr.get_current_theme_css()
        if not css:
            print("⚠️ No CSS available from theme manager")
            return
        
        context_str = str(context).lower()
        print(f"🔍 Context string (lowercase): {context_str}")
        
        # Handle different contexts with appropriate CSS
        if any(skip_context in context_str for skip_context in ["card_layout", "clayout", "editor"]):
            print(f"⚠️ Skipping CSS injection for context: {context}")
            return
        elif "reviewer" in context_str:
            # For reviewer, use safe CSS that only targets interface elements
            print(f"🎨 REVIEWER CONTEXT DETECTED - Injecting reviewer-safe CSS")
            reviewer_css = theme_mgr.get_reviewer_safe_css()
            print(f"🔍 Reviewer CSS length: {len(reviewer_css)} characters")
            print(f"🔍 First 200 chars of reviewer CSS: {reviewer_css[:200]}...")
            web_content.head += f'<style id="vscode-theme-reviewer">{reviewer_css}</style>'
            print("✅ Reviewer CSS injection completed")
        else:
            # For other contexts, use full CSS
            print(f"🎨 NON-REVIEWER CONTEXT - Injecting full CSS for context: {context}")
            print(f"🔍 Full CSS length: {len(css)} characters") 
            web_content.head += f'<style id="vscode-theme-main">{css}</style>'
            print("✅ Full CSS injection completed")
        
        # Inject custom CSS if available (always safe)
        custom_css = theme_mgr.config.get("custom_css", "")
        if custom_css:
            print(f"🎨 Also injecting {len(custom_css)} characters of custom CSS")
            web_content.head += f'<style id="vscode-theme-custom-css">{custom_css}</style>'
        
        # Debug: Print what we actually injected
        print(f"🔍 Final web_content.head length: {len(web_content.head)} characters")
        print("✅ CSS injection completed successfully")
        
    except Exception as e:
        print(f"❌ CSS injection failed: {e}")
        import traceback
        traceback.print_exc()

# Initialize the addon
initialize_addon()
