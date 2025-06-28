# VS Code Themes for Anki
# Main addon entry point

from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import json
import os
from typing import Dict, Any, Optional

from . import theme_manager
from . import ui
from . import theme_converter

# Addon directory
addon_dir = os.path.dirname(__file__)

def initialize_addon():
    """Initialize the VS Code Themes addon"""
    # Load configuration
    config = mw.addonManager.getConfig(__name__)
    if config is None:
        config = {
            "current_theme": "one_dark_pro",
            "apply_to_cards": True,
            "apply_to_ui": True,
            "use_custom_titlebar": False,
            "custom_css": ""
        }
        mw.addonManager.writeConfig(__name__, config)
    
    # Initialize theme manager
    theme_mgr = theme_manager.ThemeManager(addon_dir, config)
    
    # Apply current theme on startup - MUST happen early!
    theme_mgr.apply_current_theme()
    
    # Force immediate application to ensure it takes effect
    QTimer.singleShot(100, lambda: theme_mgr.apply_current_theme())
    
    # Add menu action
    action = QAction("VS Code Themes", mw)
    qconnect(action.triggered, lambda: show_theme_dialog(theme_mgr))
    mw.form.menuTools.addAction(action)
    
    # Register hooks for theme application
    gui_hooks.webview_will_set_content.append(lambda web_content, context: inject_theme_css(web_content, context, theme_mgr))
    gui_hooks.profile_did_open.append(lambda: theme_mgr.apply_current_theme())
    
    # Also hook into main window show event
    if hasattr(gui_hooks, 'main_window_did_init'):
        gui_hooks.main_window_did_init.append(lambda: theme_mgr.apply_current_theme())

def show_theme_dialog(theme_mgr):
    """Show the theme selection dialog"""
    dialog = ui.ThemeDialog(mw, theme_mgr)
    if dialog.exec():
        # Force refresh all webviews after theme change
        refresh_all_webviews()

def refresh_all_webviews():
    """Force refresh all webviews in Anki"""
    if not mw:
        return
    
    # Refresh main window webview
    if hasattr(mw, 'web') and mw.web:
        mw.web.eval("location.reload();")
    
    # Refresh reviewer if open
    if mw.reviewer and hasattr(mw.reviewer, 'web') and mw.reviewer.web:
        mw.reviewer.refresh_if_needed()
    
    # Refresh editor if open
    if mw.col and hasattr(mw, 'editor') and mw.editor:
        mw.editor.loadNoteKeepingFocus()
    
    # Reset and refresh the main window
    mw.reset()

def inject_theme_css(web_content, context, theme_mgr):
    """Inject theme CSS into webviews"""
    # Always inject CSS for deck browser, even if apply_to_cards is false
    if hasattr(context, 'objectName') and context.objectName() == "deckbrowser":
        apply_css = True
    else:
        apply_css = theme_mgr.config.get("apply_to_cards", True)
    
    if not apply_css:
        return
    
    theme_css = theme_mgr.get_current_theme_css()
    if theme_css:
        # Add theme CSS to the webview
        addon_package = mw.addonManager.addonFromModule(__name__)
        
        # Inject inline CSS
        web_content.head += f"""
        <style id="vscode-theme-css">
        {theme_css}
        </style>
        """
        
        # Add custom CSS if any
        custom_css = theme_mgr.config.get("custom_css", "")
        if custom_css:
            web_content.head += f"""
            <style id="vscode-theme-custom-css">
            {custom_css}
            </style>
            """

# Initialize the addon
initialize_addon()