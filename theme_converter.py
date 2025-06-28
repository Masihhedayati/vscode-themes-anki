# Theme Converter - Convert VS Code themes to Anki-compatible format

import json
from typing import Dict, Any, List
import re

class ThemeConverter:
    """Convert VS Code theme format to Anki-compatible CSS"""
    
    # VS Code workbench colors to Anki UI mapping
    WORKBENCH_MAPPINGS = {
        # Editor colors
        'editor.background': 'background',
        'editor.foreground': 'foreground',
        'editor.lineHighlightBackground': 'lineHighlight',
        'editor.selectionBackground': 'selection',
        'editor.selectionForeground': 'selectionText',
        
        # UI colors
        'sideBar.background': 'sidebarBackground',
        'sideBar.foreground': 'sidebarForeground',
        'activityBar.background': 'activityBarBackground',
        'activityBar.foreground': 'activityBarForeground',
        'statusBar.background': 'statusBarBackground',
        'statusBar.foreground': 'statusBarForeground',
        
        # Input colors
        'input.background': 'inputBackground',
        'input.foreground': 'inputForeground',
        'input.border': 'inputBorder',
        'input.placeholderForeground': 'inputPlaceholder',
        
        # Button colors
        'button.background': 'buttonBackground',
        'button.foreground': 'buttonForeground',
        'button.hoverBackground': 'buttonHoverBackground',
        
        # List/Tree colors
        'list.activeSelectionBackground': 'listActiveSelectionBackground',
        'list.activeSelectionForeground': 'listActiveSelectionForeground',
        'list.inactiveSelectionBackground': 'listInactiveSelectionBackground',
        'list.hoverBackground': 'listHoverBackground',
        
        # Text colors
        'textLink.foreground': 'linkForeground',
        'textLink.activeForeground': 'linkActiveForeground',
        
        # Terminal colors (for syntax highlighting)
        'terminal.ansiBlack': 'ansiBlack',
        'terminal.ansiRed': 'ansiRed',
        'terminal.ansiGreen': 'ansiGreen',
        'terminal.ansiYellow': 'ansiYellow',
        'terminal.ansiBlue': 'ansiBlue',
        'terminal.ansiMagenta': 'ansiMagenta',
        'terminal.ansiCyan': 'ansiCyan',
        'terminal.ansiWhite': 'ansiWhite',
    }
    
    # TextMate scope to CSS class mapping for syntax highlighting
    SCOPE_TO_CSS_CLASS = {
        'comment': ['comment', 'punctuation.definition.comment'],
        'string': ['string', 'string.quoted', 'string.template'],
        'keyword': ['keyword', 'keyword.control', 'keyword.operator'],
        'variable': ['variable', 'variable.other', 'variable.parameter'],
        'function': ['entity.name.function', 'support.function', 'meta.function-call'],
        'number': ['constant.numeric', 'constant.language.numeric'],
        'operator': ['keyword.operator', 'punctuation.operator'],
        'constant': ['constant', 'constant.language', 'support.constant'],
        'class': ['entity.name.class', 'entity.name.type.class', 'support.class'],
        'type': ['entity.name.type', 'support.type', 'storage.type'],
        'tag': ['entity.name.tag', 'meta.tag'],
        'attribute': ['entity.other.attribute-name'],
        'property': ['support.type.property-name', 'variable.other.property'],
        'module': ['entity.name.module', 'support.module'],
        'punctuation': ['punctuation', 'meta.brace'],
    }
    
    @staticmethod
    def convert_vscode_theme(vscode_theme: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a VS Code theme to Anki-compatible format"""
        converted_theme = {
            'name': vscode_theme.get('name', 'Converted Theme'),
            'type': vscode_theme.get('type', 'dark'),
            'colors': {},
            'tokenColors': []
        }
        
        # Convert workbench colors
        if 'colors' in vscode_theme:
            converted_theme['colors'] = ThemeConverter._convert_workbench_colors(
                vscode_theme['colors']
            )
        
        # Convert token colors for syntax highlighting
        if 'tokenColors' in vscode_theme:
            converted_theme['tokenColors'] = ThemeConverter._convert_token_colors(
                vscode_theme['tokenColors']
            )
        
        return converted_theme
    
    @staticmethod
    def _convert_workbench_colors(colors: Dict[str, str]) -> Dict[str, str]:
        """Convert VS Code workbench colors"""
        converted = {}
        
        # Direct copy all colors (for maximum compatibility)
        for key, value in colors.items():
            converted[key] = ThemeConverter._normalize_color(value)
        
        # Add any missing essential colors with defaults
        if 'editor.background' not in converted:
            converted['editor.background'] = '#1e1e1e' if converted.get('type') == 'dark' else '#ffffff'
        
        if 'editor.foreground' not in converted:
            converted['editor.foreground'] = '#d4d4d4' if converted.get('type') == 'dark' else '#000000'
        
        return converted
    
    @staticmethod
    def _convert_token_colors(token_colors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert VS Code token colors for syntax highlighting"""
        converted = []
        
        for token in token_colors:
            if 'scope' not in token or 'settings' not in token:
                continue
            
            converted_token = {
                'name': token.get('name', ''),
                'scope': token['scope'],
                'settings': {}
            }
            
            # Convert settings
            settings = token['settings']
            if 'foreground' in settings:
                converted_token['settings']['foreground'] = ThemeConverter._normalize_color(
                    settings['foreground']
                )
            
            if 'background' in settings:
                converted_token['settings']['background'] = ThemeConverter._normalize_color(
                    settings['background']
                )
            
            if 'fontStyle' in settings:
                converted_token['settings']['fontStyle'] = settings['fontStyle']
            
            converted.append(converted_token)
        
        return converted
    
    @staticmethod
    def _normalize_color(color: str) -> str:
        """Normalize color format to #RRGGBB or #RRGGBBAA"""
        if not color:
            return color
        
        color = color.strip()
        
        # Already in correct format
        if re.match(r'^#[0-9A-Fa-f]{6}$', color) or re.match(r'^#[0-9A-Fa-f]{8}$', color):
            return color.upper()
        
        # Convert 3-digit to 6-digit
        if re.match(r'^#[0-9A-Fa-f]{3}$', color):
            return '#' + ''.join([c*2 for c in color[1:]]).upper()
        
        # Convert 4-digit to 8-digit
        if re.match(r'^#[0-9A-Fa-f]{4}$', color):
            return '#' + ''.join([c*2 for c in color[1:]]).upper()
        
        # Return as-is if format is unknown
        return color
    
    @staticmethod
    def generate_anki_css(theme: Dict[str, Any], target: str = 'cards') -> str:
        """Generate CSS for Anki based on the theme"""
        if target == 'cards':
            return ThemeConverter._generate_card_css(theme)
        elif target == 'ui':
            return ThemeConverter._generate_ui_css(theme)
        else:
            return ""
    
    @staticmethod
    def _generate_card_css(theme: Dict[str, Any]) -> str:
        """Generate CSS for Anki cards"""
        colors = theme.get('colors', {})
        css_parts = []
        
        # Base card styling
        bg_color = colors.get('editor.background', '#1e1e1e')
        fg_color = colors.get('editor.foreground', '#d4d4d4')
        
        css_parts.append(f"""
        /* VS Code Theme - {theme.get('name', 'Custom')} */
        .card {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            line-height: 1.6;
        }}
        
        .card.night_mode {{
            background-color: {bg_color} !important;
            color: {fg_color} !important;
        }}
        """)
        
        # Add more specific styling based on available colors
        if 'editor.selectionBackground' in colors:
            css_parts.append(f"""
            .card ::selection {{
                background-color: {colors['editor.selectionBackground']} !important;
                color: {colors.get('editor.selectionForeground', fg_color)} !important;
            }}
            """)
        
        if 'textLink.foreground' in colors:
            css_parts.append(f"""
            .card a {{
                color: {colors['textLink.foreground']} !important;
            }}
            .card a:hover {{
                color: {colors.get('textLink.activeForeground', colors['textLink.foreground'])} !important;
            }}
            """)
        
        # Code block styling
        code_bg = colors.get('editor.lineHighlightBackground', 
                            colors.get('editor.selectionBackground', '#2d2d2d'))
        css_parts.append(f"""
        .card pre, .card code {{
            background-color: {code_bg} !important;
            color: {fg_color} !important;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        
        .card pre {{
            padding: 1em;
            overflow-x: auto;
        }}
        """)
        
        # Cloze styling
        cloze_color = colors.get('terminal.ansiCyan', 
                                colors.get('terminal.ansiBlue', '#007acc'))
        css_parts.append(f"""
        .cloze {{
            font-weight: bold;
            color: {cloze_color} !important;
        }}
        
        .cloze-inactive {{
            font-weight: normal;
            color: {cloze_color} !important;
            opacity: 0.5;
        }}
        """)
        
        # Add syntax highlighting CSS
        css_parts.append(ThemeConverter._generate_syntax_css(theme))
        
        return '\n'.join(css_parts)
    
    @staticmethod
    def _generate_syntax_css(theme: Dict[str, Any]) -> str:
        """Generate syntax highlighting CSS from token colors"""
        token_colors = theme.get('tokenColors', [])
        if not token_colors:
            return ""
        
        css_rules = ["\n/* Syntax Highlighting */"]
        
        # Process each token color rule
        for token in token_colors:
            if 'scope' not in token or 'settings' not in token:
                continue
            
            scopes = token['scope'] if isinstance(token['scope'], list) else [token['scope']]
            settings = token['settings']
            
            # Build CSS properties
            css_properties = []
            if 'foreground' in settings:
                css_properties.append(f"color: {settings['foreground']} !important")
            
            if 'background' in settings:
                css_properties.append(f"background-color: {settings['background']} !important")
            
            if 'fontStyle' in settings:
                font_style = settings['fontStyle']
                if 'italic' in font_style:
                    css_properties.append("font-style: italic")
                if 'bold' in font_style:
                    css_properties.append("font-weight: bold")
                if 'underline' in font_style:
                    css_properties.append("text-decoration: underline")
            
            if not css_properties:
                continue
            
            # Map scopes to CSS classes
            css_selectors = []
            for scope in scopes:
                for css_class, scope_patterns in ThemeConverter.SCOPE_TO_CSS_CLASS.items():
                    for pattern in scope_patterns:
                        if scope.startswith(pattern):
                            css_selectors.extend([
                                f".card .hljs-{css_class}",
                                f".card .{css_class}",
                                f".card .cm-{css_class}"  # CodeMirror support
                            ])
                            break
            
            if css_selectors:
                selector = ', '.join(list(set(css_selectors)))  # Remove duplicates
                css_rules.append(f"{selector} {{ {'; '.join(css_properties)}; }}")
        
        return '\n'.join(css_rules)
    
    @staticmethod
    def _generate_ui_css(theme: Dict[str, Any]) -> str:
        """Generate CSS for Anki UI (Qt stylesheet)"""
        # This would generate Qt-specific stylesheet
        # For now, returning empty as Qt styling is handled separately
        return ""