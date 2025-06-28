# Theme Manager - Handles loading and applying themes

import json
import os
from typing import Dict, Any, Optional
from aqt import mw
from aqt.theme import theme_manager as anki_theme_manager
from aqt.qt import QApplication, QWidget, Qt, QVBoxLayout, QHBoxLayout, QGridLayout, QLayoutItem
from .custom_titlebar import apply_custom_titlebar

class ThemeManager:
    def __init__(self, addon_dir: str, config: Dict[str, Any]):
        self.addon_dir = addon_dir
        self.themes_dir = os.path.join(addon_dir, "themes")
        self.config = config
        self.themes = {}
        self.current_theme = None
        
        # Load all available themes
        self.load_themes()
        
    def load_themes(self):
        """Load all theme JSON files from the themes directory"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            return
            
        for filename in os.listdir(self.themes_dir):
            if filename.endswith('.json'):
                theme_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.themes_dir, filename), 'r') as f:
                        self.themes[theme_id] = json.load(f)
                except Exception as e:
                    print(f"Error loading theme {filename}: {e}")
    
    def get_available_themes(self) -> Dict[str, str]:
        """Return a dictionary of theme IDs and display names"""
        return {theme_id: theme_data.get("name", theme_id) 
                for theme_id, theme_data in self.themes.items()}
    
    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected theme data"""
        current_theme_id = self.config.get("current_theme", "one_dark_pro")
        return self.themes.get(current_theme_id)
    
    def get_current_theme_css(self) -> str:
        """Generate CSS for the current theme"""
        theme = self.get_current_theme()
        if not theme:
            return ""
        
        colors = theme.get("colors", {})
        css_parts = []
        
        # Card styling
        if self.config.get("apply_to_cards", True):
            css_parts.append(f"""
            /* VS Code Theme - Comprehensive Card Styling */
            
            /* Root HTML and body */
            html {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            body {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }}
            
            /* Card container and all divs */
            .card, div {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            .card.night_mode {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            /* All text elements */
            p, span, h1, h2, h3, h4, h5, h6, li, td, th {{
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            /* Headers */
            h1, h2, h3, h4, h5, h6 {{
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                border-bottom-color: {colors.get('editorGroup.border', '#181a1f')} !important;
            }}
            
            /* Links */
            a {{
                color: {colors.get('textLink.foreground', '#61afef')} !important;
                text-decoration: none;
            }}
            
            a:hover {{
                color: {colors.get('textLink.activeForeground', '#528bff')} !important;
                text-decoration: underline;
            }}
            
            /* Code blocks and inline code */
            pre, code, tt {{
                background-color: {colors.get('editor.lineHighlightBackground', '#2c313c')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }}
            
            pre {{
                padding: 1em;
                overflow-x: auto;
            }}
            
            /* Tables */
            table {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                border-collapse: collapse;
                width: 100%;
            }}
            
            th, td {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                padding: 8px;
            }}
            
            th {{
                background-color: {colors.get('editor.lineHighlightBackground', '#2c313c')} !important;
                font-weight: bold;
            }}
            
            tr:hover {{
                background-color: {colors.get('editor.lineHighlightBackground', '#2c313c')} !important;
            }}
            
            /* Lists */
            ul, ol {{
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            /* Blockquotes */
            blockquote {{
                border-left: 4px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                background-color: {colors.get('editor.lineHighlightBackground', '#2c313c')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                padding: 0.5em 1em;
                margin: 0.5em 0;
            }}
            
            /* Horizontal rules */
            hr {{
                border: none;
                border-top: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                margin: 1em 0;
            }}
            
            /* Images */
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                border-radius: 3px;
            }}
            
            /* Selection */
            ::selection {{
                background-color: {colors.get('editor.selectionBackground', '#3e4451')} !important;
                color: {colors.get('editor.selectionForeground', '#ffffff')} !important;
            }}
            
            ::-moz-selection {{
                background-color: {colors.get('editor.selectionBackground', '#3e4451')} !important;
                color: {colors.get('editor.selectionForeground', '#ffffff')} !important;
            }}
            
            /* Cloze deletions */
            .cloze {{
                font-weight: bold;
                color: {colors.get('terminal.ansiCyan', '#56b6c2')} !important;
                background-color: {colors.get('editor.lineHighlightBackground', '#2c313c')} !important;
                padding: 0.1em 0.3em;
                border-radius: 3px;
            }}
            
            /* Type answer input */
            #typeans {{
                background-color: {colors.get('input.background', '#1e2227')} !important;
                color: {colors.get('input.foreground', '#abb2bf')} !important;
                border: 1px solid {colors.get('input.border', '#181a1f')} !important;
                padding: 8px;
                border-radius: 3px;
                font-family: inherit;
                font-size: inherit;
                width: 100%;
                box-sizing: border-box;
            }}
            
            #typeans:focus {{
                outline: none;
                border-color: {colors.get('focusBorder', '#007acc')} !important;
            }}
            
            /* Anki buttons in cards */
            button {{
                background-color: {colors.get('button.background', '#404754')} !important;
                color: {colors.get('button.foreground', '#ffffff')} !important;
                border: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                padding: 6px 12px;
                border-radius: 3px;
                cursor: pointer;
            }}
            
            button:hover {{
                background-color: {colors.get('editor.selectionBackground', '#3e4451')} !important;
            }}
            
            /* Input fields */
            input[type="text"], input[type="number"], textarea {{
                background-color: {colors.get('input.background', '#1e2227')} !important;
                color: {colors.get('input.foreground', '#abb2bf')} !important;
                border: 1px solid {colors.get('input.border', '#181a1f')} !important;
                padding: 4px 8px;
                border-radius: 3px;
            }}
            
            /* Any other elements */
            * {{
                border-color: {colors.get('editorGroup.border', '#181a1f')} !important;
            }}
            
            /* Scrollbars in webview */
            ::-webkit-scrollbar {{
                width: 12px;
                height: 12px;
                background-color: {colors.get('editor.background', '#282c34')} !important;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background-color: {colors.get('scrollbarSlider.background', '#4e566680')} !important;
                border-radius: 6px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background-color: {colors.get('scrollbarSlider.hoverBackground', '#5a637580')} !important;
            }}
            
            /* MathJax */
            .MathJax, .MathJax_Display {{
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
            }}
            
            /* Fields for editing */
            .field {{
                background-color: {colors.get('input.background', '#1e2227')} !important;
                color: {colors.get('input.foreground', '#abb2bf')} !important;
                border: 1px solid {colors.get('input.border', '#181a1f')} !important;
            }}
            
            /* ===== DECK BROWSER SPECIFIC STYLING ===== */
            /* PHASE 1: HTML Content Control - Target Anki's actual HTML structure */
            
            /* Main deck browser container */
            body.deckbrowser, body#deckbrowser, .deckbrowser-web-view {{
                background-color: {colors.get('editor.background', '#282c34')} !important;
                color: {colors.get('editor.foreground', '#abb2bf')} !important;
                padding: 16px !important;
                margin: 0 !important;
            }}
            
            /* Statistics Grid Layout - AGGRESSIVE two-column layout */
            body.deckbrowser center > table,
            body#deckbrowser center > table,
            body.deckbrowser table:not(.deck-table),
            body#deckbrowser table:not(.deck-table),
            .stats-table {{
                display: grid !important;
                grid-template-columns: 140px auto !important;
                grid-column-gap: 16px !important;
                grid-row-gap: 4px !important;
                width: 280px !important;
                margin: 0 auto 20px auto !important;
                padding: 16px !important;
                background-color: {colors.get('input.background', '#1e2227')} !important;
                border: 1px solid {colors.get('input.border', '#181a1f')} !important;
                border-radius: 6px !important;
                align-items: center !important;
            }}
            
            /* Convert table rows to grid items */
            body.deckbrowser center > table > tbody,
            body.deckbrowser center > table > tr {{
                display: contents !important;
            }}
            
            /* Statistics cells - Grid items */
            body.deckbrowser center > table td,
            body#deckbrowser center > table td {{
                display: block !important;
                padding: 6px 12px !important;
                margin: 2px 0 !important;
                background-color: transparent !important;
            }}
            
            /* Statistics labels (left column) - Consistent width */
            body.deckbrowser center > table td:nth-child(odd),
            body#deckbrowser center > table td:nth-child(odd) {{
                text-align: left !important;
                font-weight: normal !important;
                opacity: 0.9 !important;
                padding-right: 16px !important;
            }}
            
            /* Statistics numbers (right column) - Perfect monospace alignment */
            body.deckbrowser center > table td:nth-child(even),
            body#deckbrowser center > table td:nth-child(even),
            body.deckbrowser table:not(.deck-table) td:nth-child(even),
            body#deckbrowser table:not(.deck-table) td:nth-child(even) {{
                text-align: right !important;
                font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace !important;
                font-variant-numeric: tabular-nums !important;
                font-feature-settings: "tnum", "lnum" !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                background-color: {colors.get('editor.background', '#282c34')} !important;
                border: 1px solid {colors.get('focusBorder', '#007acc')}44 !important;
                border-radius: 3px !important;
                padding: 4px 8px !important;
                min-width: 100px !important;
                width: 100px !important;
                display: flex !important;
                justify-content: flex-end !important;
                align-items: center !important;
                white-space: nowrap !important;
            }}
            
            /* Fix center tag behavior */
            body.deckbrowser center,
            body#deckbrowser center {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                width: 100% !important;
            }}
            
            /* HTML Buttons in deck browser */
            body.deckbrowser button,
            body#deckbrowser button,
            body.deckbrowser input[type="button"],
            body#deckbrowser input[type="button"] {{
                display: inline-block !important;
                min-width: 160px !important;
                height: 36px !important;
                line-height: 36px !important;
                padding: 0 16px !important;
                margin: 4px !important;
                background-color: {colors.get('button.background', '#404754')} !important;
                color: {colors.get('button.foreground', '#ffffff')} !important;
                border: none !important;
                border-radius: 4px !important;
                font-size: 14px !important;
                font-weight: normal !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                cursor: pointer !important;
                text-align: center !important;
                vertical-align: middle !important;
                box-sizing: border-box !important;
                transition: opacity 0.2s !important;
            }}
            
            body.deckbrowser button:hover,
            body#deckbrowser button:hover {{
                opacity: 0.8 !important;
                background-color: {colors.get('button.hoverBackground', '#4e5766')} !important;
            }}
            
            /* BUTTON PANEL - Perfect alignment and consistent styling */
            body.deckbrowser center > button,
            body#deckbrowser center > button,
            body.deckbrowser .study-button,
            body#deckbrowser .study-button {{
                margin: 4px !important;
            }}
            
            /* Button container - ensure proper layout */
            body.deckbrowser .button-container,
            body#deckbrowser .button-container,
            body.deckbrowser center,
            body#deckbrowser center {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                gap: 12px !important;
                width: 100% !important;
            }}
            
            /* Study buttons (Study Now, Smart Search) - IDENTICAL sizing */
            body.deckbrowser button[onclick*="study"], 
            body#deckbrowser button[onclick*="study"],
            body.deckbrowser button[onclick*="browse"],
            body#deckbrowser button[onclick*="browse"],
            body.deckbrowser .study-now-button,
            body#deckbrowser .study-now-button,
            body.deckbrowser .smart-search-button,
            body#deckbrowser .smart-search-button {{
                display: inline-flex !important;
                width: 200px !important;
                height: 36px !important;
                padding: 0 16px !important;
                margin: 2px !important;
                justify-content: center !important;
                align-items: center !important;
                text-align: center !important;
                vertical-align: middle !important;
                box-sizing: border-box !important;
                flex-shrink: 0 !important;
            }}
            
            /* Deck list table - Remove header gap */
            body.deckbrowser table,
            body#deckbrowser table,
            .deck-table {{
                border-collapse: collapse !important;
                border-spacing: 0 !important;
                margin-top: 0 !important;
            }}
            
            /* Table header (Deck, Due, New, etc.) */
            body.deckbrowser th,
            body#deckbrowser th,
            body.deckbrowser thead,
            body#deckbrowser thead {{
                background-color: {colors.get('sideBar.background', '#21252b')} !important;
                color: {colors.get('sideBar.foreground', '#abb2bf')} !important;
                padding: 8px 12px !important;
                margin: 0 !important;
                border-bottom: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                font-weight: normal !important;
                opacity: 0.9 !important;
            }}
            
            /* Remove any gaps from tbody */
            body.deckbrowser tbody,
            body#deckbrowser tbody {{
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* First row after header - Remove top margin/padding */
            body.deckbrowser tbody tr:first-child,
            body#deckbrowser tbody tr:first-child {{
                margin-top: 0 !important;
                padding-top: 0 !important;
            }}
            
            /* Individual deck rows */
            body.deckbrowser tr,
            body#deckbrowser tr,
            tr.deck-row {{
                border-bottom: 1px solid {colors.get('editorGroup.border', '#181a1f')}22 !important;
                margin: 0 !important;
            }}
            
            /* Deck row cells */
            body.deckbrowser td,
            body#deckbrowser td {{
                padding: 12px !important;
                margin: 0 !important;
            }}
            
            /* Calendar in deck browser */
            .deck-browser .calendar-widget,
            #deck-browser .calendar-widget {{
                margin: 16px auto !important;
                max-width: 300px !important;
            }}
            
            /* Status bar at bottom */
            .deck-browser .status-bar,
            #deck-browser .status-bar,
            .bottom-bar {{
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                background-color: {colors.get('sideBar.background', '#21252b')} !important;
                border-top: 1px solid {colors.get('editorGroup.border', '#181a1f')} !important;
                padding: 8px 16px !important;
                font-size: 12px !important;
                opacity: 0.8 !important;
            }}
            """)
        
        # Add syntax highlighting if available
        token_colors = theme.get("tokenColors", [])
        if token_colors:
            css_parts.append(self._generate_syntax_highlighting_css(token_colors))
        
        return "\n".join(css_parts)
    
    def _generate_syntax_highlighting_css(self, token_colors: list) -> str:
        """Generate CSS for syntax highlighting based on token colors"""
        css_parts = ["\n/* Syntax Highlighting */"]
        
        # Map common TextMate scopes to CSS classes
        scope_to_class = {
            "comment": ".hljs-comment, .comment",
            "string": ".hljs-string, .string",
            "keyword": ".hljs-keyword, .keyword",
            "variable": ".hljs-variable, .variable",
            "function": ".hljs-function, .function",
            "number": ".hljs-number, .number",
            "operator": ".hljs-operator, .operator",
            "constant": ".hljs-literal, .constant",
            "class": ".hljs-class, .class",
            "type": ".hljs-type, .type"
        }
        
        for token in token_colors:
            if "scope" in token and "settings" in token:
                scopes = token["scope"] if isinstance(token["scope"], list) else [token["scope"]]
                settings = token["settings"]
                
                for scope in scopes:
                    # Find matching CSS class
                    for scope_prefix, css_class in scope_to_class.items():
                        if scope.startswith(scope_prefix):
                            styles = []
                            if "foreground" in settings:
                                styles.append(f"color: {settings['foreground']} !important")
                            if "fontStyle" in settings:
                                if "italic" in settings["fontStyle"]:
                                    styles.append("font-style: italic")
                                if "bold" in settings["fontStyle"]:
                                    styles.append("font-weight: bold")
                            
                            if styles:
                                css_parts.append(f".card {css_class} {{ {'; '.join(styles)}; }}")
                            break
        
        return "\n".join(css_parts)
    
    def apply_current_theme(self):
        """Apply the current theme to Anki's UI"""
        theme = self.get_current_theme()
        if not theme:
            return
        
        colors = theme.get("colors", {})
        
        # Always generate the stylesheet to ensure it's available
        qt_stylesheet = self._generate_qt_stylesheet(colors)
        
        # Apply to UI if enabled
        if self.config.get("apply_to_ui", True):
            # Get the application instance FIRST
            app = QApplication.instance()
            if app:
                # Apply to the entire application - this is critical!
                app.setStyleSheet(qt_stylesheet)
            
            # Apply to main window
            if mw:
                # Apply custom title bar if enabled
                if self.config.get("use_custom_titlebar", True):
                    self._apply_custom_titlebar(mw, colors)
                
                # Force theme update
                is_dark = theme.get("type", "dark") == "dark"
                if hasattr(anki_theme_manager, 'set_night_mode'):
                    anki_theme_manager.set_night_mode(is_dark)
                
                # Refresh all open windows
                self._refresh_all_windows()
                
                # Fix deck list layout gaps
                self._hook_deck_browser_widgets()
                
                # Force webview refresh
                if hasattr(mw, 'web') and mw.web:
                    mw.web.eval("document.body.style.backgroundColor = document.body.style.backgroundColor;")
                
                # Update all child widgets
                self._update_all_widgets(mw)
    
    def _refresh_all_windows(self):
        """Refresh all open Anki windows"""
        if not mw:
            return
            
        # Get the app instance
        app = QApplication.instance()
        if not app:
            return
            
        # Refresh all top-level widgets
        for widget in app.topLevelWidgets():
            if widget.isVisible():
                # Don't set stylesheet on individual widgets - let app stylesheet cascade
                widget.update()
                widget.repaint()
                
                # Force style recalculation
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                
                # Update all children
                self._update_all_widgets(widget)
    
    def _update_all_widgets(self, parent_widget):
        """Recursively update all child widgets"""
        if not parent_widget:
            return
            
        # Update the parent widget
        parent_widget.update()
        
        # Update all children
        for child in parent_widget.findChildren(QWidget):
            child.update()
            child.style().unpolish(child)
            child.style().polish(child)
    
    def _apply_custom_titlebar(self, window, colors):
        """Apply custom title bar to a window"""
        # Check if we already have a custom title bar
        if hasattr(window, '_custom_titlebar_applied'):
            # Just update the colors
            if hasattr(window, '_custom_titlebar_widget'):
                window._custom_titlebar_widget.theme_colors = colors
                window._custom_titlebar_widget.apply_theme()
            return
        
        try:
            # Apply the custom title bar
            titlebar = apply_custom_titlebar(window, colors)
            
            # Mark as applied and store reference
            window._custom_titlebar_applied = True
            window._custom_titlebar_widget = titlebar
            
        except Exception as e:
            # If something goes wrong, don't break Anki
            print(f"Failed to apply custom title bar: {e}")
    
    def _generate_qt_stylesheet(self, colors: Dict[str, str]) -> str:
        """Generate Qt stylesheet from VS Code theme colors"""
        # Map VS Code colors to Qt elements - using actual theme colors
        bg_color = colors.get('editor.background', '#282c34')
        fg_color = colors.get('editor.foreground', '#abb2bf')
        border_color = colors.get('editorGroup.border', '#181a1f')
        selection_bg = colors.get('editor.selectionBackground', '#3e4451')
        
        # Use actual button colors from theme
        button_bg = colors.get('button.background', '#404754')
        button_fg = colors.get('button.foreground', '#ffffff')
        button_hover_bg = colors.get('button.hoverBackground', colors.get('list.hoverBackground', '#2c323c'))
        
        # Secondary button colors
        button_secondary_bg = colors.get('button.secondaryBackground', button_bg)
        button_secondary_fg = colors.get('button.secondaryForeground', button_fg)
        
        input_bg = colors.get('input.background', '#1e2227')
        input_fg = colors.get('input.foreground', '#abb2bf')
        input_border = colors.get('input.border', border_color)
        
        sidebar_bg = colors.get('sideBar.background', '#21252b')
        sidebar_fg = colors.get('sideBar.foreground', '#abb2bf')
        list_hover_bg = colors.get('list.hoverBackground', '#2c323c')
        list_active_bg = colors.get('list.activeSelectionBackground', '#2c323c')
        list_active_fg = colors.get('list.activeSelectionForeground', '#d7dae0')
        
        # Tab colors
        tab_bg = colors.get('tab.inactiveBackground', '#21252b')
        tab_fg = colors.get('tab.inactiveForeground', '#5c6370')
        tab_active_bg = colors.get('tab.activeBackground', '#282c34')
        tab_active_fg = colors.get('tab.activeForeground', '#d7dae0')
        tab_border = colors.get('tab.border', border_color)
        
        # Title bar colors
        titlebar_bg = colors.get('titleBar.activeBackground', bg_color)
        titlebar_fg = colors.get('titleBar.activeForeground', fg_color)
        titlebar_inactive_bg = colors.get('titleBar.inactiveBackground', titlebar_bg)
        titlebar_inactive_fg = colors.get('titleBar.inactiveForeground', titlebar_fg)
        
        # Activity bar colors - using monochromatic scheme
        activity_bg = colors.get('activityBar.background', sidebar_bg)
        activity_fg = colors.get('activityBar.foreground', fg_color)
        # Use focus border color for accents instead of badge colors
        accent_color = colors.get('focusBorder', colors.get('terminal.ansiCyan', '#56b6c2'))
        accent_fg = colors.get('contrastBorder', fg_color)
        
        # Status bar colors
        statusbar_bg = colors.get('statusBar.background', '#007acc')
        statusbar_fg = colors.get('statusBar.foreground', '#ffffff')
        
        scrollbar_bg = colors.get('scrollbarSlider.background', '#4e566680')
        scrollbar_hover_bg = colors.get('scrollbarSlider.hoverBackground', '#5a637580')
        
        # Focus colors
        focus_border = colors.get('focusBorder', '#007acc')
        
        # Typography scale
        font_size_large = '16px'
        font_size_normal = '14px'
        font_size_small = '13px'
        font_size_tiny = '12px'
        
        # Opacity scale for text hierarchy - WCAG compliant
        opacity_primary = '1.0'
        opacity_secondary = '0.87'  # Ensures 7:1 contrast ratio
        opacity_tertiary = '0.75'   # Ensures 4.5:1 contrast ratio
        opacity_disabled = '0.6'    # Minimum for disabled state
        
        # 8px grid system
        spacing_unit = '8px'
        spacing_small = '8px'
        spacing_medium = '16px'
        spacing_large = '24px'
        spacing_xlarge = '32px'
        
        return f"""
        /* VS Code Theme - Comprehensive UI Styling */
        
        /* Root application styling - FORCE everything dark */
        QApplication {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* Force ALL QWidgets to be dark */
        * {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        
        /* Target ANY white backgrounds */
        QWidget[style*="background-color: white"], 
        QWidget[style*="background-color:#fff"],
        QWidget[style*="background-color: #fff"],
        QWidget[style*="background: white"],
        *[style*="background-color: white"] {{
            background-color: {bg_color} !important;
            background: {bg_color} !important;
        }}
        
        /* Global widget styling - affects ALL widgets */
        QWidget {{
            background-color: {bg_color};
            color: {fg_color};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-weight: normal;
            font-size: {font_size_normal};
            line-height: 1.5;
        }}
        
        /* Main windows and dialogs */
        QMainWindow {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
        }}
        
        QDialog {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
        }}
        
        /* Window title bar (platform-specific) */
        QMainWindow::title {{
            background-color: {titlebar_bg};
            color: {titlebar_fg};
            padding: 0px;
        }}
        
        /* Anki Main Window specific - Force dark theme */
        MainWindow, AnkiQt {{
            background-color: {bg_color} !important;
        }}
        
        /* Fix white top bar - all possible selectors */
        #header, .header, #topbar, .topbar, #top, .top {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            border: none !important;
        }}
        
        /* Main window top area */
        QMainWindow > QWidget {{
            background-color: {bg_color} !important;
        }}
        
        /* Anki's main toolbar area */
        QMainWindow QToolBar {{
            background-color: {bg_color} !important;
            border: none !important;
            padding: {spacing_small};
        }}
        
        /* Force all widgets in main window */
        MainWindow *, AnkiQt * {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        
        /* Anki deck browser */
        DeckBrowser {{
            background-color: {bg_color};
        }}
        
        /* Anki toolbar specific */
        #toolbar, .toolbar {{
            background-color: {bg_color};
            border-bottom: 1px solid {border_color};
        }}
        
        /* Dock widgets (browser, etc) */
        QDockWidget {{
            background-color: {sidebar_bg};
            color: {sidebar_fg};
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
        }}
        
        QDockWidget::title {{
            background-color: {sidebar_bg};
            color: {sidebar_fg};
            padding: 4px;
            border: none;
        }}
        
        /* Splitters */
        QSplitter::handle {{
            background-color: {border_color};
        }}
        
        /* Tab widgets */
        QTabWidget::pane {{
            background-color: {bg_color};
            border: none;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {tab_fg};
            padding: 8px 12px;
            margin: 0px;
            border: none;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            background-color: transparent;
            color: {tab_active_fg};
            border-bottom: 2px solid {focus_border};
        }}
        
        QTabBar::tab:hover {{
            background-color: {list_hover_bg};
            color: {tab_active_fg};
        }}
        
        /* Menu bar and menus */
        QMenuBar {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
        }}
        
        QMenuBar::item {{
            padding: 4px 8px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {selection_bg};
        }}
        
        QMenu {{
            background-color: {sidebar_bg};
            color: {fg_color};
            border: 1px solid {border_color};
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 4px 20px;
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {list_hover_bg};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {border_color};
            margin: 4px 0px;
        }}
        
        /* Tool bars */
        QToolBar {{
            background-color: {bg_color} !important;
            border: none !important;
            padding: 8px;
            spacing: 4px;
        }}
        
        QToolBar::separator {{
            background-color: {border_color};
            width: 1px;
            margin: 4px;
        }}
        
        /* Aggressively target ALL possible header/top bar elements */
        #header, .header, #topbar, .topbar, #top, .top,
        QWidget[objectName="header"], QWidget[class*="header"],
        QWidget[objectName="topbar"], QWidget[class*="topbar"],
        MainWindow > QWidget:first-of-type,
        AnkiQt > QWidget:first-of-type,
        QMainWindow > QMenuBar,
        QMainWindow > QToolBar {{
            background-color: {sidebar_bg} !important;
            color: {fg_color} !important;
        }}
        
        /* Force theme on ALL widgets */
        QWidget {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        
        /* Override any hardcoded white backgrounds */
        QWidget[style*="background: white"],
        QWidget[style*="background-color: white"],
        QWidget[style*="background:#fff"],
        QWidget[style*="background-color:#fff"],
        QWidget[style*="background: #ffffff"],
        QWidget[style*="background-color: #ffffff"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* ALL toolbar buttons - FORCE unified 32px height */
        QToolButton {{
            background-color: {button_bg} !important;
            color: {fg_color} !important;
            border: none !important;
            padding: {spacing_small} !important;
            border-radius: 2px !important;
            min-height: {spacing_xlarge} !important;
            max-height: {spacing_xlarge} !important;
            height: {spacing_xlarge} !important;
            font-size: {font_size_normal} !important;
            margin: 2px !important;
            text-align: center !important;
            vertical-align: middle !important;
        }}
        
        QToolButton:hover {{
            background-color: {list_hover_bg};
            opacity: 0.9;
        }}
        
        QToolButton:pressed {{
            background-color: {list_hover_bg};
            opacity: 0.7;
        }}
        
        QToolButton:checked {{
            background-color: {list_active_bg};
            border-left: 2px solid {accent_color};
            padding-left: 6px;
        }}
        
        /* Icon-only toolbar buttons */
        QToolButton[text=""], QToolButton:!text {{
            min-width: {spacing_xlarge};
            max-width: {spacing_xlarge};
        }}
        
        /* Text toolbar buttons */
        QToolButton[text]:not([text=""]) {{
            min-width: auto;
            padding: {spacing_small} {spacing_medium};
        }}
        
        /* Dropdown toolbar buttons */
        QToolButton::menu-button {{
            width: 16px;
            border: none;
            padding: 0;
        }}
        
        QToolButton::menu-arrow {{
            image: none;
            width: 8px;
            height: 8px;
            background-color: {fg_color};
            subcontrol-origin: padding;
            subcontrol-position: center right;
            margin-right: 4px;
        }}
        
        /* Buttons - Minimalist Design with Grid System */
        QPushButton {{
            background-color: {button_bg};
            color: {button_fg};
            border: none;
            padding: {spacing_small} {spacing_medium};
            border-radius: 2px;
            font-weight: normal;
            min-height: {spacing_xlarge};
            font-size: {font_size_normal};
        }}
        
        QPushButton:hover {{
            background-color: {button_bg};
            opacity: 0.8;
        }}
        
        QPushButton:pressed {{
            background-color: {button_bg};
            opacity: 0.6;
        }}
        
        QPushButton:focus {{
            outline: 1px solid {focus_border};
            outline-offset: 2px;
        }}
        
        QPushButton:default {{
            background-color: {button_bg};
            font-weight: normal;
        }}
        
        QPushButton:disabled {{
            background-color: {sidebar_bg};
            color: {fg_color};
            opacity: {opacity_disabled};
        }}
        
        /* Secondary buttons */
        QPushButton[flat="true"] {{
            background-color: transparent;
            color: {button_secondary_fg};
            border: none;
        }}
        
        QPushButton[flat="true"]:hover {{
            background-color: {list_hover_bg};
            opacity: 0.8;
        }}
        
        /* PHASE 2: Qt Widget Button Alignment - Consistent dimensions */
        /* All Anki deck browser buttons - Force identical sizing */
        #studyButton, .studyButton,
        #smartSearchButton, .smartSearchButton,
        #addButton, .addButton,
        #browseButton, .browseButton,
        QPushButton[objectName="studyButton"],
        QPushButton[objectName="smartSearchButton"],
        QPushButton[objectName="addButton"],
        QPushButton[objectName="browseButton"] {{
            background-color: {button_bg} !important;
            color: {button_fg} !important;
            border: none !important;
            min-width: 160px !important;
            max-width: 160px !important;
            width: 160px !important;
            min-height: 36px !important;
            max-height: 36px !important;
            height: 36px !important;
            padding: 0 16px !important;
            margin: 4px !important;
            font-size: {font_size_normal} !important;
            font-weight: normal !important;
            text-align: center !important;
            vertical-align: middle !important;
            border-radius: 4px !important;
        }}
        
        /* Hover states for all deck browser buttons */
        #studyButton:hover, .studyButton:hover,
        #smartSearchButton:hover, .smartSearchButton:hover,
        #addButton:hover, .addButton:hover,
        #browseButton:hover, .browseButton:hover {{
            background-color: {button_hover_bg} !important;
            opacity: 0.9 !important;
        }}
        
        /* Fix button layout container if it's a Qt widget */
        QWidget[objectName="studyArea"],
        QWidget#studyArea {{
            qproperty-layoutDirection: LeftToRight;
            qproperty-layoutSpacing: 8;
            min-height: 50px !important;
            padding: 8px !important;
        }}
        
        /* Tool buttons with text - Unified styling */
        QToolButton[popupMode="1"] {{
            background-color: {button_bg};
            color: {button_fg};
            border: none;
            padding: {spacing_small} {spacing_medium};
            border-radius: 2px;
            min-height: {spacing_xlarge};
            font-size: {font_size_normal};
        }}
        
        QToolButton[popupMode="1"]:hover {{
            background-color: {button_bg};
            opacity: 0.8;
        }}
        
        /* Input fields - Grid aligned */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {input_bg};
            color: {input_fg};
            border: 1px solid {border_color};
            padding: {spacing_small};
            border-radius: 2px;
            selection-background-color: {selection_bg};
            font-size: {font_size_normal};
            min-height: {spacing_xlarge};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {focus_border};
            outline: none;
        }}
        
        /* Spin boxes */
        QSpinBox, QDoubleSpinBox {{
            background-color: {input_bg};
            color: {input_fg};
            border: 1px solid {border_color};
            padding: 8px;
            border-radius: 2px;
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {button_bg};
            border: none;
            width: 16px;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {selection_bg};
        }}
        
        /* Combo boxes */
        QComboBox {{
            background-color: {input_bg};
            color: {input_fg};
            border: 1px solid {border_color};
            padding: 8px;
            border-radius: 2px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {fg_color};
            margin-right: 4px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {sidebar_bg};
            color: {fg_color};
            border: 1px solid {border_color};
            selection-background-color: {selection_bg};
        }}
        
        /* List, tree and table widgets - improved visual hierarchy */
        QListWidget, QTreeWidget, QTableWidget, QListView, QTreeView, QTableView {{
            background-color: {bg_color};
            color: {fg_color};
            border: none;
            outline: none;
            alternate-background-color: {sidebar_bg};
            selection-background-color: {list_active_bg};
            selection-color: {list_active_fg};
        }}
        
        QListWidget::item, QTreeWidget::item, QTableWidget::item {{
            padding: 12px 16px;
            border-bottom: 1px solid {border_color}33;
            min-height: 32px;
        }}
        
        QListWidget::item:alternate, QTreeWidget::item:alternate {{
            background-color: {sidebar_bg}33;
        }}
        
        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {list_hover_bg}66;
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {list_active_bg};
            color: {list_active_fg};
            border-left: 3px solid {accent_color};
            padding-left: 13px;
        }}
        
        /* Headers */
        QHeaderView::section {{
            background-color: {sidebar_bg};
            color: {fg_color};
            padding: 4px;
            border: none;
            border-right: 1px solid {border_color};
            border-bottom: 1px solid {border_color};
        }}
        
        /* Scroll bars */
        QScrollBar {{
            background-color: {bg_color};
            border: none;
        }}
        
        QScrollBar:vertical {{
            width: 12px;
        }}
        
        QScrollBar:horizontal {{
            height: 12px;
        }}
        
        QScrollBar::handle {{
            background-color: {scrollbar_bg};
            border-radius: 6px;
            min-height: 20px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:hover {{
            background-color: {scrollbar_hover_bg};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
            border: none;
        }}
        
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
        
        /* Checkboxes and radio buttons */
        QCheckBox, QRadioButton {{
            color: {fg_color};
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            background-color: {input_bg};
            border: 1px solid {border_color};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors.get('checkbox.background', '#007acc')};
            border-color: {colors.get('checkbox.background', '#007acc')};
        }}
        
        QRadioButton::indicator {{
            border-radius: 8px;
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors.get('checkbox.background', '#007acc')};
            border-color: {colors.get('checkbox.background', '#007acc')};
        }}
        
        /* Progress bars */
        QProgressBar {{
            background-color: {input_bg};
            border: none;
            border-radius: 2px;
            text-align: center;
            color: {fg_color};
            height: 4px;
        }}
        
        QProgressBar::chunk {{
            background-color: {focus_border};
            border-radius: 2px;
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            background-color: {input_bg};
            height: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {button_bg};
            border: 1px solid {border_color};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {selection_bg};
        }}
        
        /* Group boxes */
        QGroupBox {{
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 2px;
            margin-top: 8px;
            padding-top: 8px;
            color: {fg_color};
            font-weight: normal;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            background-color: {bg_color};
            color: {fg_color};
            font-weight: normal;
        }}
        
        /* Labels - with typography hierarchy */
        QLabel {{
            color: {fg_color};
            background-color: transparent;
            font-size: {font_size_normal};
        }}
        
        /* Headers and titles */
        QLabel[objectName^="title"], QLabel.title {{
            font-size: {font_size_large};
            color: {fg_color};
            opacity: {opacity_primary};
        }}
        
        /* Secondary text */
        QLabel[objectName^="subtitle"], QLabel.subtitle {{
            font-size: {font_size_small};
            color: {fg_color};
            opacity: {opacity_secondary};
        }}
        
        /* Small/helper text */
        QLabel[objectName^="caption"], QLabel.caption {{
            font-size: {font_size_tiny};
            color: {fg_color};
            opacity: {opacity_tertiary};
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {colors.get('statusBar.background', '#007acc')};
            color: {colors.get('statusBar.foreground', '#ffffff')};
            border: none;
        }}
        
        /* CRITICAL: Modal and Dialog Styling - Fix white modals */
        QMessageBox, QInputDialog, QErrorMessage, QColorDialog, QFileDialog, QFontDialog, QProgressDialog {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color};
        }}
        
        QMessageBox QLabel, QInputDialog QLabel {{
            background-color: transparent !important;
            color: {fg_color} !important;
            font-size: {font_size_normal};
        }}
        
        QMessageBox QPushButton, QInputDialog QPushButton, QDialogButtonBox QPushButton {{
            background-color: {button_bg} !important;
            color: {button_fg} !important;
            border: none !important;
            padding: {spacing_small} {spacing_medium} !important;
            min-height: {spacing_xlarge} !important;
            min-width: 80px !important;
            font-size: {font_size_normal} !important;
        }}
        
        QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {{
            background-color: {list_hover_bg} !important;
        }}
        
        /* Modal backgrounds and overlays */
        QWidget[windowModality="2"], QDialog[windowModality="2"] {{
            background-color: {bg_color} !important;
        }}
        
        /* Popup widgets (like AMBOSS popups) */
        QWidget[windowType="Popup"], QFrame[windowType="Popup"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color} !important;
        }}
        
        /* Any floating widget */
        QWidget[windowFlags*="Popup"], QWidget[windowFlags*="Tool"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* Tool tips */
        QToolTip {{
            background-color: {sidebar_bg};
            color: {fg_color};
            border: 1px solid {border_color};
            padding: {spacing_small};
            font-size: {font_size_small};
        }}
        
        /* Menus and context menus - comprehensive */
        QMenu {{
            background-color: {sidebar_bg} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color};
            padding: {spacing_unit};
        }}
        
        QMenu::item {{
            padding: {spacing_small} {spacing_large};
            min-height: {spacing_large};
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {list_hover_bg};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {border_color}44;
            margin: {spacing_small} 0;
        }}
        
        QMenu::icon {{
            padding-left: {spacing_small};
        }}
        
        /* Splitters - make them visible but subtle */
        QSplitter::handle {{
            background-color: {border_color}44;
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {accent_color}44;
        }}
        
        /* Context menus */
        QWidget#qt_edit_menu {{
            background-color: {sidebar_bg};
            color: {fg_color};
            border: 1px solid {border_color};
        }}
        
        /* Dropdown menus */
        QComboBox QAbstractItemView {{
            background-color: {sidebar_bg} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color};
            selection-background-color: {list_active_bg};
            padding: {spacing_unit};
        }}
        
        QComboBox QAbstractItemView::item {{
            min-height: {spacing_large};
            padding: {spacing_small};
        }}
        
        /* Calendar widgets if any */
        QCalendarWidget {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        
        QCalendarWidget QAbstractItemView {{
            background-color: {bg_color};
            color: {fg_color};
            selection-background-color: {list_active_bg};
        }}
        
        /* Any floating or popup widget */
        QWidget[windowType="5"], QWidget[windowType="9"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color};
        }}
        
        /* Anki-specific elements */
        #fields {{
            background-color: {bg_color};
        }}
        
        #fieldsArea {{
            background-color: {bg_color};
        }}
        
        /* CRITICAL: Title bar color cannot be changed via Qt stylesheets.
           The OS controls the window chrome (title bar with close/minimize/maximize).
           Everything else in the window will be themed. */
        
        /* Anki Main Window and Deck Browser - Force theme everywhere */
        MainWindow, AnkiQt, DeckBrowser, QMainWindow {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* Force ALL widgets to inherit theme */
        MainWindow *, AnkiQt *, DeckBrowser * {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* Main deck browser area */
        .deckbrowser, #deckbrowser {{
            background-color: {bg_color} !important;
            padding: {spacing_large} !important;
        }}
        
        /* Statistics Panel - Grid Layout with Fixed Columns */
        /* Target the actual stats container */
        .stats, #stats, QWidget[class*="stats"] {{
            padding: {spacing_medium} !important;
            margin: {spacing_medium} 0 !important;
        }}
        
        /* Force ALL QLabels to have consistent base styling */
        QLabel {{
            background-color: transparent !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-size: {font_size_normal} !important;
            padding: 2px 4px !important;
            margin: 2px !important;
        }}
        
        /* Statistics labels - Left aligned, fixed width */
        QLabel[buddy], /* Labels with buddy relationships */
        .dueLabel, .newLabel, .reviewLabel, /* Specific stat labels */
        QLabel:contains("Due"), QLabel:contains("New"), QLabel:contains("Review") {{
            text-align: left !important;
            min-width: 120px !important;
            max-width: 120px !important;
            padding-right: {spacing_medium} !important;
        }}
        
        /* Statistics numbers - Right aligned monospace */
        .dueCount, .newCount, .reviewCount, /* Specific stat counts */
        QLabel[class*="count"], QLabel[class*="Count"],
        QLabel:matches(QRegExp("^\\s*\\d+\\s*$")) {{
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace !important;
            text-align: right !important;
            min-width: 80px !important;
            font-variant-numeric: tabular-nums !important;
            background-color: {input_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 4px !important;
            padding: 4px 8px !important;
        }}
        
        /* PHASE 3: Unified study area styling */
        #studyArea, .studyArea, QWidget[objectName="studyArea"] {{
            background-color: {bg_color} !important;
            padding: 16px !important;
            margin: 8px 0 !important;
            qproperty-alignment: AlignCenter;
        }}
        
        /* Ensure all deck browser buttons have consistent styling */
        #studyArea QPushButton,
        #studyArea QToolButton,
        .studyArea QPushButton,
        .studyArea QToolButton {{
            min-width: 160px !important;
            max-width: 160px !important;
            width: 160px !important;
            min-height: 36px !important;
            max-height: 36px !important;
            height: 36px !important;
            margin: 4px !important;
            padding: 0 16px !important;
            font-size: {font_size_normal} !important;
            font-weight: normal !important;
            text-align: center !important;
            background-color: {button_bg} !important;
            color: {button_fg} !important;
            border: none !important;
            border-radius: 4px !important;
        }}
        
        /* Button hover states */
        #studyArea QPushButton:hover,
        #studyArea QToolButton:hover,
        .studyArea QPushButton:hover,
        .studyArea QToolButton:hover {{
            background-color: {button_hover_bg} !important;
            opacity: 0.9 !important;
        }}
        
        /* Calendar widget centering */
        QCalendarWidget {{
            margin-left: auto !important;
            margin-right: auto !important;
            margin-top: {spacing_medium} !important;
            margin-bottom: {spacing_medium} !important;
            max-width: 300px !important;
            min-width: 250px !important;
        }}
        
        /* Calendar navigation bar */
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {sidebar_bg} !important;
            padding: {spacing_small} !important;
        }}
        
        /* Calendar cells */
        QCalendarWidget QTableView {{
            background-color: {bg_color} !important;
            selection-background-color: {list_active_bg} !important;
            selection-color: {list_active_fg} !important;
        }}
        
        /* Calendar header */
        QCalendarWidget QHeaderView::section {{
            background-color: {sidebar_bg} !important;
            padding: {spacing_unit} !important;
            font-size: {font_size_small} !important;
        }}
        
        /* Bottom stats bar alignment */
        DeckBrowser QStatusBar,
        DeckBrowser QWidget[objectName="bottomStats"],
        QStatusBar {{
            background-color: {sidebar_bg} !important;
            padding: {spacing_small} {spacing_xlarge} !important;
            margin: 0 !important;
            min-height: {spacing_large} !important;
            max-height: {spacing_large} !important;
            border-top: 1px solid {border_color} !important;
        }}
        
        /* Status bar items - consistent spacing */
        QStatusBar::item {{
            border: none !important;
            padding: 0 {spacing_medium} !important;
        }}
        
        /* Status bar labels */
        QStatusBar QLabel {{
            padding: 0 {spacing_small} !important;
            margin: 0 !important;
            font-size: {font_size_small} !important;
            opacity: {opacity_secondary};
        }}
        
        /* Status bar permanent widgets */
        QStatusBar QPushButton {{
            max-height: {spacing_medium} !important;
            padding: 2px {spacing_small} !important;
            margin: 0 !important;
            font-size: {font_size_small} !important;
        }}
        
        /* Anki Deck List - NO GAPS, improved hierarchy */
        #deckList {{
            background-color: {bg_color};
            border: none;
            spacing: 0;
            margin: 0;
            padding: 0;
        }}
        
        #deckList QListWidget {{
            background-color: {bg_color};
            alternate-background-color: {sidebar_bg}22;
            margin: 0;
            padding: 0;
            spacing: 0;
        }}
        
        #deckList QListWidget::item {{
            padding: 16px;
            border-bottom: 1px solid {border_color}22;
            min-height: 48px;
            margin: 0;
        }}
        
        #deckList QListWidget::item:hover {{
            background-color: {list_hover_bg}44;
        }}
        
        /* AGGRESSIVE gap removal - target all possible deck list containers */
        QWidget[objectName*="deck"], QWidget[class*="deck"], 
        QWidget[objectName*="Deck"], QWidget[class*="Deck"] {{
            margin: 0 !important;
            padding: 0 !important;
            spacing: 0 !important;
        }}
        
        /* Remove gaps from main window deck area */
        QMainWindow QWidget[objectName="centralwidget"] {{
            margin: 0;
            padding: 0;
        }}
        
        /* Anki Study Screen */
        #studyArea {{
            background-color: {bg_color};
        }}
        
        /* Anki Reviewer Buttons - Unified Monochromatic Design */
        #againButton, #hardButton, #goodButton, #easyButton {{
            background-color: {button_bg};
            color: {fg_color};
            border: none;
            padding: {spacing_small} {spacing_medium};
            min-height: {spacing_xlarge};
            font-size: {font_size_normal};
            margin: 0 {spacing_unit};
        }}
        
        #againButton {{
            opacity: {opacity_tertiary};
        }}
        
        #hardButton {{
            opacity: {opacity_secondary};
        }}
        
        #goodButton {{
            opacity: {opacity_primary};
            border: 1px solid {accent_color}33;
        }}
        
        #easyButton {{
            opacity: {opacity_primary};
        }}
        
        #againButton:hover, #hardButton:hover, #goodButton:hover, #easyButton:hover {{
            background-color: {list_hover_bg};
            opacity: 1.0;
        }}
        
        #goodButton:hover {{
            border-color: {accent_color};
        }}
        
        /* Anki Browser Window */
        Browser {{
            background-color: {bg_color};
        }}
        
        /* Anki Editor */
        EditorWebView {{
            background-color: {input_bg};
            border: 1px solid {input_border};
        }}
        
        /* Anki Stats - Proper grid alignment */
        StatsDialog {{
            background-color: {bg_color};
        }}
        
        StatsDialog QLabel {{
            padding: {spacing_small} 0;
            min-height: {spacing_large};
            font-size: {font_size_normal};
        }}
        
        StatsDialog QWidget {{
            spacing: {spacing_medium};
        }}
        
        /* Statistics table alignment */
        QTableWidget {{
            gridline-color: {border_color}33;
            padding: 0;
            margin: 0;
        }}
        
        QTableWidget::item {{
            padding: {spacing_small} {spacing_medium};
            min-height: {spacing_xlarge};
            font-size: {font_size_normal};
        }}
        
        QTableWidget QHeaderView::section {{
            padding: {spacing_small} {spacing_medium};
            min-height: {spacing_xlarge};
            font-size: {font_size_normal};
            font-weight: normal;
        }}
        
        /* Anki Preferences */
        Preferences {{
            background-color: {bg_color};
        }}
        
        /* Anki Toolbar specific - ensure consistency */
        QToolBar QToolButton {{
            color: {fg_color};
            background-color: {button_bg};
            min-height: {spacing_xlarge} !important;
            max-height: {spacing_xlarge} !important;
            margin: 2px;
        }}
        
        /* Anki toolbar separators */
        QToolBar QToolButton[objectName="qt_toolbar_ext_button"] {{
            min-width: 16px;
            max-width: 16px;
        }}
        
        /* Anki specific frame elements */
        QFrame {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        
        QFrame[frameShape="HLine"], QFrame[frameShape="VLine"] {{
            background-color: {border_color};
        }}
        
        /* Anki Dialog Buttons Box */
        QDialogButtonBox {{
            background-color: {bg_color};
        }}
        
        QDialogButtonBox QPushButton {{
            min-width: 70px;
        }}
        
        /* Make sure all Anki windows get the theme */
        AnkiWebView {{
            background-color: {bg_color};
        }}
        
        /* Web views and browser elements - Force dark */
        QWebEngineView, QWebView, AnkiWebView {{
            background-color: {bg_color} !important;
        }}
        
        /* Force webview page background */
        QWebEngineView > QWidget {{
            background-color: {bg_color} !important;
        }}
        
        /* Force background on all remaining elements */
        QWidget#centralwidget {{
            background-color: {bg_color};
        }}
        
        /* Third-party addon overrides - AMBOSS and others */
        [class*="amboss"], [class*="AMBOSS"], [id*="amboss"], [id*="AMBOSS"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* AMBOSS specific popup styling */
        QWidget[objectName*="amboss"], QFrame[objectName*="amboss"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            border: 1px solid {border_color} !important;
        }}
        
        /* Any widget with white background - force dark */
        QWidget[styleSheet*="background-color: white"], 
        QWidget[styleSheet*="background-color:#ffffff"],
        QWidget[styleSheet*="background-color: #ffffff"],
        QWidget[styleSheet*="background-color:white"] {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        
        /* Force all text widgets to use theme colors and typography */
        QTextEdit, QTextBrowser, QPlainTextEdit {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            font-size: {font_size_normal} !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            font-weight: normal !important;
            line-height: 1.5 !important;
        }}
        
        /* Ensure all labels have consistent typography */
        QLabel {{
            font-size: {font_size_normal} !important;
            font-weight: normal !important;
        }}
        
        /* Fix any bold text to use opacity instead */
        b, strong, QLabel[font-weight="bold"] {{
            font-weight: normal !important;
            opacity: {opacity_primary};
        }}
        
        /* Small text should use the small size */
        small, QLabel[objectName*="small"] {{
            font-size: {font_size_small} !important;
        }}
        
        /* Catch-all for any remaining unstyled elements */
        * {{
            selection-background-color: {selection_bg};
            selection-color: {list_active_fg};
        }}
        
        /* Force inheritance for all child elements */
        QWidget > * {{
            background-color: inherit;
            color: inherit;
        }}
        """
    
    def set_theme(self, theme_id: str):
        """Set the current theme"""
        if theme_id in self.themes:
            self.config["current_theme"] = theme_id
            mw.addonManager.writeConfig(__name__, self.config)
            self.apply_current_theme()
            return True
        return False
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration"""
        self.config.update(new_config)
        mw.addonManager.writeConfig(__name__, self.config)
        self.apply_current_theme()
        
        # Force immediate refresh
        from aqt.qt import QTimer
        QTimer.singleShot(100, self._force_complete_refresh)
    
    def _force_complete_refresh(self):
        """Force a complete refresh of all UI elements"""
        if mw:
            # Apply to app level ONLY - don't override on window level
            qt_stylesheet = self._generate_qt_stylesheet(self.get_current_theme().get("colors", {}))
            app = QApplication.instance()
            if app:
                app.setStyleSheet(qt_stylesheet)
            # Don't set on mw - let it inherit from app
            
            # Force refresh
            self._refresh_all_windows()
            
            # Reset main window
            if hasattr(mw, 'reset'):
                mw.reset()
    
    def _fix_deck_list_layout(self, widget):
        """Fix deck list gap by modifying Qt layout managers directly"""
        try:
            from aqt.qt import QVBoxLayout, QHBoxLayout, QGridLayout, QLayoutItem
            
            # Recursively find and fix deck list layouts
            def fix_layouts(w):
                if hasattr(w, 'layout') and w.layout():
                    layout = w.layout()
                    
                    # Check if this is a deck browser layout
                    if hasattr(w, 'objectName') and w.objectName():
                        obj_name = w.objectName().lower()
                        if 'deck' in obj_name or 'list' in obj_name or 'browser' in obj_name:
                            # Remove spacing and margins that cause gaps
                            if isinstance(layout, (QVBoxLayout, QHBoxLayout)):
                                layout.setSpacing(0)
                                layout.setContentsMargins(0, 0, 0, 0)
                            elif isinstance(layout, QGridLayout):
                                layout.setSpacing(0)
                                layout.setContentsMargins(0, 0, 0, 0)
                                layout.setVerticalSpacing(0)
                                layout.setHorizontalSpacing(8)  # Keep some horizontal spacing
                    
                    # Also check for table/list widgets specifically
                    for i in range(layout.count()):
                        child_item = layout.itemAt(i)
                        if child_item and child_item.widget():
                            child_widget = child_item.widget()
                            class_name = child_widget.__class__.__name__
                            
                            # Target specific widget types that commonly have gaps
                            if any(keyword in class_name.lower() for keyword in ['list', 'table', 'tree']):
                                if hasattr(child_widget, 'setSpacing'):
                                    child_widget.setSpacing(0)
                                if hasattr(child_widget, 'setContentsMargins'):
                                    child_widget.setContentsMargins(0, 0, 0, 0)
                            
                            # Recursively fix child layouts
                            fix_layouts(child_widget)
                
                # Also check direct children
                for child in w.findChildren(type(w)):
                    if child != w:  # Avoid infinite recursion
                        fix_layouts(child)
            
            fix_layouts(widget)
            
        except Exception as e:
            # Silently continue if layout fixing fails
            pass
    
    def _hook_deck_browser_widgets(self):
        """Hook into deck browser widget creation to fix layouts"""
        try:
            from aqt import mw
            from aqt.qt import QApplication
            
            app = QApplication.instance()
            if not app:
                return
                
            # Find and fix existing deck browser widgets
            for widget in app.topLevelWidgets():
                if widget.isVisible():
                    # Check if this is a deck browser window
                    class_name = widget.__class__.__name__
                    if 'MainWindow' in class_name or 'DeckBrowser' in class_name:
                        self._fix_deck_list_layout(widget)
                        
                    # Also check for the main window deck browser content
                    if hasattr(widget, 'findChild'):
                        deck_widgets = widget.findChildren(type(widget))
                        for deck_widget in deck_widgets:
                            if hasattr(deck_widget, 'objectName') and deck_widget.objectName():
                                if 'deck' in deck_widget.objectName().lower():
                                    self._fix_deck_list_layout(deck_widget)
        except Exception as e:
            # Silently continue if hooking fails
            pass