# Anki Theme Integration Service
# Automatically synchronize VS Code theme selection with Anki's native theme system

import json
from typing import Dict, Any, Optional, Tuple
from aqt import mw
from aqt.theme import theme_manager as anki_theme_manager
from aqt.qt import QApplication

class AnkiThemeIntegration:
    """
    Service for synchronizing VS Code themes with Anki's native theme system.
    
    This class handles the automatic switching of Anki's built-in theme
    (light/dark mode) when users select VS Code themes in our addon.
    """
    
    def __init__(self):
        self.original_night_mode = None
        self._sync_enabled = True
        
    def is_sync_enabled(self) -> bool:
        """Check if automatic theme sync is enabled"""
        return self._sync_enabled
    
    def set_sync_enabled(self, enabled: bool):
        """Enable or disable automatic theme synchronization"""
        self._sync_enabled = enabled
        print(f"🔄 Anki theme sync {'enabled' if enabled else 'disabled'}")
    
    def get_current_anki_night_mode(self) -> Optional[bool]:
        """
        Get current Anki night mode status.
        Returns True if dark mode, False if light mode, None if unknown.
        """
        try:
            if mw and hasattr(mw, 'pm') and mw.pm:
                return mw.pm.night_mode()
        except Exception as e:
            print(f"⚠️ Could not get Anki night mode status: {e}")
        return None
    
    def classify_vscode_theme(self, theme_data: Dict[str, Any]) -> str:
        """
        Classify VS Code theme as 'light' or 'dark'.
        
        Args:
            theme_data: VS Code theme JSON data
            
        Returns:
            'light' or 'dark'
        """
        # Primary: Use explicit type field
        if 'type' in theme_data:
            theme_type = str(theme_data['type']).lower()
            if theme_type in ['light', 'dark']:
                return theme_type
        
        # Secondary: Analyze background color brightness
        colors = theme_data.get('colors', {})
        bg_color = colors.get('editor.background', '#1e1e1e')
        
        if self._is_light_color(bg_color):
            return 'light'
        else:
            return 'dark'
    
    def _is_light_color(self, hex_color: str) -> bool:
        """
        Determine if a hex color is light or dark based on luminance.
        
        Args:
            hex_color: Color in hex format (e.g., '#ffffff')
            
        Returns:
            True if light color, False if dark
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0  
            b = int(hex_color[4:6], 16) / 255.0
            
            # Calculate relative luminance
            def gamma_correct(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r_lin = gamma_correct(r)
            g_lin = gamma_correct(g)
            b_lin = gamma_correct(b)
            
            luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
            
            # Threshold of 0.5 for light vs dark
            return luminance > 0.5
            
        except Exception as e:
            print(f"⚠️ Error analyzing color {hex_color}: {e}")
            # Default to dark for unknown colors
            return False
    
    def should_sync_to_anki_theme(self, theme_type: str) -> Tuple[bool, str]:
        """
        Determine if we should sync to Anki theme and return reason.
        
        Args:
            theme_type: 'light' or 'dark'
            
        Returns:
            (should_sync: bool, reason: str)
        """
        if not self._sync_enabled:
            return False, "Automatic sync disabled by user"
        
        current_anki_mode = self.get_current_anki_night_mode()
        if current_anki_mode is None:
            return False, "Cannot determine current Anki theme state"
        
        # Check if sync is needed
        needs_dark = theme_type == 'dark'
        current_is_dark = current_anki_mode
        
        if needs_dark == current_is_dark:
            return False, f"Anki already in correct {'dark' if current_is_dark else 'light'} mode"
        
        return True, f"Need to switch Anki from {'dark' if current_is_dark else 'light'} to {theme_type}"
    
    def sync_anki_theme(self, theme_data: Dict[str, Any]) -> bool:
        """
        Synchronize Anki's native theme with VS Code theme.
        
        Args:
            theme_data: VS Code theme JSON data
            
        Returns:
            True if sync was successful, False otherwise
        """
        try:
            # Step 1: Classify the VS Code theme
            theme_type = self.classify_vscode_theme(theme_data)
            theme_name = theme_data.get('name', 'Unknown')
            
            print(f"🎨 Synchronizing Anki theme for '{theme_name}' ({theme_type})")
            
            # Step 2: Check if sync is needed
            should_sync, reason = self.should_sync_to_anki_theme(theme_type)
            print(f"🔍 Sync analysis: {reason}")
            
            if not should_sync:
                return True  # No sync needed, but not an error
            
            # Step 3: Store original state if first time
            if self.original_night_mode is None:
                self.original_night_mode = self.get_current_anki_night_mode()
                print(f"💾 Stored original Anki theme state: {'dark' if self.original_night_mode else 'light'}")
            
            # Step 4: Apply sync using multiple methods
            is_dark = theme_type == 'dark'
            success = self._apply_anki_theme_change(is_dark)
            
            if success:
                print(f"✅ Successfully synced Anki to {theme_type} mode")
                return True
            else:
                print(f"❌ Failed to sync Anki theme")
                return False
                
        except Exception as e:
            print(f"❌ Error in sync_anki_theme: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_anki_theme_change(self, is_dark: bool) -> bool:
        """
        Apply the theme change using multiple methods for maximum compatibility.
        
        Args:
            is_dark: True for dark mode, False for light mode
            
        Returns:
            True if any method succeeded
        """
        methods_tried = []
        success = False
        
        # Method 1: Direct anki_theme_manager API (current approach)
        try:
            if hasattr(anki_theme_manager, 'set_night_mode'):
                anki_theme_manager.set_night_mode(is_dark)
                methods_tried.append("anki_theme_manager.set_night_mode")
                success = True
                print(f"✅ Method 1 success: anki_theme_manager.set_night_mode({is_dark})")
            else:
                methods_tried.append("anki_theme_manager.set_night_mode (not available)")
        except Exception as e:
            print(f"⚠️ Method 1 failed: {e}")
            methods_tried.append(f"anki_theme_manager.set_night_mode (error: {e})")
        
        # Method 2: Profile manager manipulation
        try:
            if mw and hasattr(mw, 'pm') and mw.pm:
                # This is more experimental - profile manager direct access
                if hasattr(mw.pm, 'set_night_mode'):
                    mw.pm.set_night_mode(is_dark)
                    methods_tried.append("mw.pm.set_night_mode")
                    success = True
                    print(f"✅ Method 2 success: mw.pm.set_night_mode({is_dark})")
                else:
                    methods_tried.append("mw.pm.set_night_mode (not available)")
        except Exception as e:
            print(f"⚠️ Method 2 failed: {e}")
            methods_tried.append(f"mw.pm.set_night_mode (error: {e})")
        
        # Method 3: Configuration file manipulation (experimental)
        try:
            # This would require investigation of Anki's config structure
            # Placeholder for future implementation
            methods_tried.append("config manipulation (not implemented)")
        except Exception as e:
            methods_tried.append(f"config manipulation (error: {e})")
        
        # Method 4: Force refresh approach
        if success:
            try:
                # Try to force UI refresh to apply theme changes
                if mw:
                    app = QApplication.instance()
                    if app:
                        app.processEvents()
                    
                    # Force repaint
                    mw.update()
                    mw.repaint()
                    
                print("✅ Forced UI refresh after theme change")
            except Exception as e:
                print(f"⚠️ UI refresh failed: {e}")
        
        print(f"🔍 Methods attempted: {', '.join(methods_tried)}")
        return success
    
    def restore_original_theme(self) -> bool:
        """
        Restore Anki to its original theme state.
        
        Returns:
            True if restoration was successful
        """
        if self.original_night_mode is None:
            print("ℹ️ No original theme state to restore")
            return True
        
        try:
            success = self._apply_anki_theme_change(self.original_night_mode)
            if success:
                print(f"✅ Restored original Anki theme: {'dark' if self.original_night_mode else 'light'}")
                self.original_night_mode = None
            return success
        except Exception as e:
            print(f"❌ Failed to restore original theme: {e}")
            return False
    
    def get_theme_sync_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of theme synchronization capabilities.
        
        Returns:
            Dictionary with sync status information
        """
        status = {
            'sync_enabled': self._sync_enabled,
            'current_anki_night_mode': self.get_current_anki_night_mode(),
            'original_theme_stored': self.original_night_mode is not None,
            'available_apis': {}
        }
        
        # Check API availability
        status['available_apis']['anki_theme_manager'] = hasattr(anki_theme_manager, 'set_night_mode')
        status['available_apis']['profile_manager'] = (
            mw and hasattr(mw, 'pm') and mw.pm and hasattr(mw.pm, 'set_night_mode')
        )
        status['available_apis']['mw_available'] = mw is not None
        
        return status


class ThemeClassificationService:
    """
    Service for classifying and categorizing VS Code themes.
    """
    
    @staticmethod
    def get_theme_type_for_anki(theme_id: str, themes: Dict[str, Any]) -> str:
        """
        Get the Anki-compatible theme type for a VS Code theme.
        
        Args:
            theme_id: VS Code theme identifier
            themes: Dictionary of all available themes
            
        Returns:
            'light' or 'dark'
        """
        theme_data = themes.get(theme_id)
        if not theme_data:
            return 'dark'  # Default fallback
        
        integration = AnkiThemeIntegration()
        return integration.classify_vscode_theme(theme_data)
    
    @staticmethod
    def classify_all_themes(themes: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Classify all themes by light/dark type.
        
        Args:
            themes: Dictionary of all available themes
            
        Returns:
            Dictionary with 'light' and 'dark' keys containing theme lists
        """
        integration = AnkiThemeIntegration()
        classified = {'light': [], 'dark': []}
        
        for theme_id, theme_data in themes.items():
            if not isinstance(theme_data, dict):
                continue
                
            theme_type = integration.classify_vscode_theme(theme_data)
            theme_info = {
                'id': theme_id,
                'name': theme_data.get('name', theme_id),
                'type': theme_type,
                'colors': theme_data.get('colors', {})
            }
            
            classified[theme_type].append(theme_info)
        
        return classified
    
    @staticmethod
    def get_theme_statistics(themes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about theme distribution.
        
        Args:
            themes: Dictionary of all available themes
            
        Returns:
            Statistics dictionary
        """
        classified = ThemeClassificationService.classify_all_themes(themes)
        
        total_themes = len(classified['light']) + len(classified['dark'])
        
        return {
            'total_themes': total_themes,
            'light_themes': len(classified['light']),
            'dark_themes': len(classified['dark']),
            'light_percentage': len(classified['light']) / total_themes * 100 if total_themes > 0 else 0,
            'dark_percentage': len(classified['dark']) / total_themes * 100 if total_themes > 0 else 0,
            'classified_themes': classified
        }


# Global instance for easy access
anki_theme_integration = AnkiThemeIntegration() 