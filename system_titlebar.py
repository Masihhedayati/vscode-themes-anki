# System Title Bar Theming - Customizes native macOS title bar colors

import colorsys
from aqt.qt import *
from aqt import mw
from typing import Dict, Tuple, Optional
import sys

class SystemTitleBarThemer:
    """Customizes the native macOS system title bar to match VS Code theme colors"""
    
    def __init__(self):
        self.current_theme_colors = {}
        self.original_window_color = None
        self.is_active = False
        
    def apply_theme_to_titlebar(self, theme_colors: Dict[str, str]):
        """Apply theme colors to the native macOS title bar"""
        if not mw or sys.platform != "darwin":
            print("ℹ️ System title bar theming only available on macOS")
            return
            
        try:
            self.current_theme_colors = theme_colors
            
            # Extract theme colors
            bg_color = theme_colors.get("editor.background", "#1e1e1e")
            accent_color = theme_colors.get("button.background", "#007acc")
            
            # Convert to RGB and determine if it's a dark theme
            rgb = self._hex_to_rgb(bg_color)
            is_dark = self._is_dark_color(rgb)
            
            # Generate title bar color that complements the theme
            titlebar_color = self._generate_titlebar_color(bg_color, accent_color, is_dark)
            
            # Apply to main window
            self._apply_titlebar_styling(titlebar_color, is_dark)
            
            print(f"✅ System title bar themed with color: {titlebar_color}")
            self.is_active = True
            
        except Exception as e:
            print(f"❌ Error theming system title bar: {e}")
    
    def _generate_titlebar_color(self, bg_color: str, accent_color: str, is_dark: bool) -> str:
        """Generate an appropriate title bar color based on theme"""
        try:
            bg_rgb = self._hex_to_rgb(bg_color)
            
            # Convert to HSV for manipulation
            bg_hsv = colorsys.rgb_to_hsv(bg_rgb[0]/255, bg_rgb[1]/255, bg_rgb[2]/255)
            
            if is_dark:
                # For dark themes, make title bar slightly lighter
                lightness = min(bg_hsv[2] + 0.08, 0.3)  # Don't go too bright
                saturation = bg_hsv[1] * 0.7  # Reduce saturation slightly
            else:
                # For light themes, make title bar slightly darker
                lightness = max(bg_hsv[2] - 0.05, 0.7)  # Don't go too dark
                saturation = bg_hsv[1] * 0.8
            
            # Convert back to RGB
            themed_rgb = colorsys.hsv_to_rgb(bg_hsv[0], saturation, lightness)
            
            # Convert to hex
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(themed_rgb[0] * 255),
                int(themed_rgb[1] * 255),
                int(themed_rgb[2] * 255)
            )
            
            return hex_color
            
        except Exception as e:
            print(f"Error generating title bar color: {e}")
            return bg_color
    
    def _apply_titlebar_styling(self, color: str, is_dark: bool):
        """Apply the color to the macOS title bar"""
        try:
            # Store original if not already stored
            if not self.original_window_color:
                self.original_window_color = mw.palette().color(QPalette.ColorRole.Window)
            
            # Convert hex to QColor
            qcolor = QColor(color)
            
            # Method 1: Set window background color (affects title bar on macOS)
            palette = mw.palette()
            palette.setColor(QPalette.ColorRole.Window, qcolor)
            mw.setPalette(palette)
            
            # Method 2: Set stylesheet for window background
            window_style = f"""
            QMainWindow {{
                background-color: {color};
            }}
            """
            
            # Apply without affecting existing styles
            current_style = mw.styleSheet()
            if "QMainWindow" in current_style:
                # Replace existing QMainWindow style
                import re
                new_style = re.sub(
                    r'QMainWindow\s*\{[^}]*\}', 
                    window_style.strip(), 
                    current_style
                )
            else:
                new_style = current_style + "\n" + window_style
            
            mw.setStyleSheet(new_style)
            
            # Method 3: Try to set window appearance for macOS
            if hasattr(mw, 'winId'):
                try:
                    # Set appearance based on theme
                    if is_dark:
                        mw.setAttribute(Qt.WidgetAttribute.WA_MacVariableSize, True)
                        # Try to set dark appearance
                        if hasattr(Qt.WidgetAttribute, 'WA_MacNormalSize'):
                            mw.setAttribute(Qt.WidgetAttribute.WA_MacNormalSize, True)
                except:
                    pass
            
            # Force update
            mw.update()
            
        except Exception as e:
            print(f"Error applying title bar styling: {e}")
    
    def reset_titlebar(self):
        """Reset title bar to original appearance"""
        try:
            if not mw or not self.is_active:
                return
                
            # Restore original palette if available
            if self.original_window_color:
                palette = mw.palette()
                palette.setColor(QPalette.ColorRole.Window, self.original_window_color)
                mw.setPalette(palette)
            
            # Remove custom window styling
            current_style = mw.styleSheet()
            if "QMainWindow" in current_style:
                import re
                new_style = re.sub(r'QMainWindow\s*\{[^}]*\}', '', current_style)
                mw.setStyleSheet(new_style)
            
            mw.update()
            self.is_active = False
            print("✅ System title bar reset to original")
            
        except Exception as e:
            print(f"Error resetting title bar: {e}")
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _is_dark_color(self, rgb: Tuple[int, int, int]) -> bool:
        """Determine if a color is dark based on luminance"""
        # Calculate relative luminance
        r, g, b = [x/255.0 for x in rgb]
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 0.5

# Global instance
system_titlebar_themer = SystemTitleBarThemer() 