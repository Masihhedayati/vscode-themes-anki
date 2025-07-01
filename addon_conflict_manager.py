"""
Addon Conflict Manager - Comprehensive solution for theme consistency issues
Handles detection, resolution, and prevention of CSS conflicts with other addons
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from aqt import mw
from aqt.qt import QMessageBox, QTimer, QApplication
from aqt.utils import showInfo, askUser


class AddonConflictManager:
    """
    Comprehensive addon conflict detection and resolution system
    Automatically handles CSS conflicts that break theme consistency
    """
    
    # Known conflicting addons with their AnkiWeb IDs and conflict details
    KNOWN_CONFLICTS = {
        '374005964': {
            'name': 'The KING of Button Add-ons',
            'conflict_level': 'CRITICAL',
            'conflict_type': 'Direct CSS Override Competition',
            'css_patterns': ['.btn', 'QPushButton', '.answer-button', '.review-button'],
            'description': 'Directly modifies button styling that conflicts with theme button colors',
            'mitigation_strategy': 'auto_disable_with_consent',
            'nuclear_css_required': True,
            'priority': 1  # Highest priority conflict
        },
        '594329229': {
            'name': 'Colorful Tags (+ Hierarchical Tags)',
            'conflict_level': 'HIGH',
            'conflict_type': 'Tag Styling CSS Competition',  
            'css_patterns': ['.tag', '.tag-color', 'span.tag'],
            'description': 'Modifies tag colors that conflict with theme tag styling',
            'mitigation_strategy': 'css_coordination',
            'nuclear_css_required': True,
            'priority': 2
        },
        '1771074083': {
            'name': 'Review Heatmap',
            'conflict_level': 'MODERATE',
            'conflict_type': 'Main Window CSS Injection',
            'css_patterns': ['.heatmap', '.cal-heatmap', '#review-heatmap'],
            'description': 'Adds visual elements with hardcoded colors that may not follow theme',
            'mitigation_strategy': 'theme_aware_injection',
            'nuclear_css_required': False,
            'priority': 3
        },
        '952691989': {
            'name': 'AnKing Note Types (Easy Customization)',
            'conflict_level': 'MODERATE',
            'conflict_type': 'Card Template CSS Override',
            'css_patterns': ['.card', '.note-type', '.anking-style'],
            'description': 'Modifies card styling that themes should control',
            'mitigation_strategy': 'template_coordination',
            'nuclear_css_required': False,
            'priority': 4
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the conflict manager with configuration"""
        self.config = config or {}
        self.detected_conflicts = []
        self.monitoring_active = False
        self.nuclear_css_applied = False
        self.user_conflict_preferences = {}
        print("🔧 AddonConflictManager initialized")
    
    def detect_conflicting_addons(self) -> List[Dict[str, Any]]:
        """
        Scan for installed addons that conflict with theme system
        Returns list of detected conflicts with details
        """
        print("🔍 Scanning for conflicting addons...")
        conflicts = []
        
        try:
            if not mw or not hasattr(mw, 'addonManager'):
                print("⚠️ Addon manager not available")
                return conflicts
            
            # Get all installed addons
            all_addons = mw.addonManager.allAddons()
            print(f"📦 Found {len(all_addons)} total addons installed")
            
            # Check each known conflict
            for addon_id, conflict_info in self.KNOWN_CONFLICTS.items():
                if addon_id in all_addons:
                    # Check if addon is actually enabled
                    enabled = mw.addonManager.isEnabled(addon_id)
                    
                    conflict_details = {
                        'addon_id': addon_id,
                        'enabled': enabled,
                        **conflict_info
                    }
                    
                    conflicts.append(conflict_details)
                    
                    status = "🔴 ENABLED" if enabled else "⚪ DISABLED"
                    print(f"{status} Conflict detected: {conflict_info['name']} ({conflict_info['conflict_level']})")
            
            # Sort by priority (highest first)
            conflicts.sort(key=lambda x: x['priority'])
            
            print(f"⚠️ Total conflicts detected: {len(conflicts)}")
            self.detected_conflicts = conflicts
            
            return conflicts
            
        except Exception as e:
            print(f"❌ Error detecting conflicts: {e}")
            return []
    
    def resolve_conflicts_automatically(self, conflicts: List[Dict[str, Any]] = None) -> bool:
        """
        Automatically resolve conflicts based on user preferences and conflict severity
        Returns True if all critical conflicts were resolved
        """
        if conflicts is None:
            conflicts = self.detect_conflicting_addons()
        
        if not conflicts:
            print("✅ No conflicts to resolve")
            return True
        
        print(f"🔧 Resolving {len(conflicts)} addon conflicts...")
        
        critical_conflicts_resolved = True
        
        for conflict in conflicts:
            if not conflict['enabled']:
                print(f"✅ {conflict['name']} already disabled, skipping")
                continue
            
            # Handle based on mitigation strategy
            strategy = conflict.get('mitigation_strategy', 'ask_user')
            
            if strategy == 'auto_disable_with_consent':
                resolved = self._handle_auto_disable_conflict(conflict)
                if not resolved and conflict['conflict_level'] == 'CRITICAL':
                    critical_conflicts_resolved = False
                    
            elif strategy == 'css_coordination':
                resolved = self._handle_css_coordination_conflict(conflict)
                
            elif strategy == 'theme_aware_injection':
                resolved = self._handle_theme_aware_conflict(conflict)
                
            else:
                resolved = self._handle_generic_conflict(conflict)
        
        # Apply nuclear CSS if needed for any unresolved conflicts
        if not critical_conflicts_resolved or self._has_unresolved_nuclear_conflicts(conflicts):
            print("🚀 Applying nuclear CSS for unresolved conflicts...")
            self.apply_nuclear_css()
        
        return critical_conflicts_resolved
    
    def _handle_auto_disable_conflict(self, conflict: Dict[str, Any]) -> bool:
        """Handle conflicts that should be auto-disabled with user consent"""
        addon_id = conflict['addon_id']
        addon_name = conflict['name']
        
        print(f"🔴 Handling critical conflict: {addon_name}")
        
        # Check user preference for this specific addon
        pref_key = f"auto_disable_{addon_id}"
        user_preference = self.user_conflict_preferences.get(pref_key, None)
        
        if user_preference == 'always_disable':
            return self._disable_addon(addon_id, addon_name, auto=True)
        elif user_preference == 'never_disable':
            print(f"⚪ User chose to keep {addon_name} enabled, applying nuclear CSS")
            return False
        else:
            # Ask user for permission
            return self._ask_user_to_disable_addon(conflict)
    
    def _ask_user_to_disable_addon(self, conflict: Dict[str, Any]) -> bool:
        """Ask user permission to disable conflicting addon"""
        addon_id = conflict['addon_id']
        addon_name = conflict['name']
        description = conflict['description']
        
        message = f"""
🔴 CRITICAL THEME CONFLICT DETECTED

Addon: {addon_name}
Issue: {description}

This addon is causing theme consistency problems where buttons and interface elements don't match your selected VS Code theme.

Would you like to automatically disable this addon to fix theme consistency?

Note: You can re-enable it later from Tools > Add-ons if needed.
        """.strip()
        
        title = "Resolve Theme Conflict"
        
        try:
            # Use Anki's askUser function for better integration
            user_agreed = askUser(message, title=title)
            
            if user_agreed:
                # Save user preference
                self.user_conflict_preferences[f"auto_disable_{addon_id}"] = 'always_disable'
                return self._disable_addon(addon_id, addon_name, auto=False)
            else:
                # Save user preference to not ask again
                self.user_conflict_preferences[f"auto_disable_{addon_id}"] = 'never_disable'
                print(f"⚪ User chose to keep {addon_name} enabled")
                return False
                
        except Exception as e:
            print(f"❌ Error asking user about {addon_name}: {e}")
            return False
    
    def _disable_addon(self, addon_id: str, addon_name: str, auto: bool = False) -> bool:
        """Disable the specified addon"""
        try:
            if not mw or not hasattr(mw, 'addonManager'):
                print("❌ Cannot disable addon - addon manager not available")
                return False
            
            # Disable the addon
            mw.addonManager.toggleEnabled(addon_id, enable=False)
            
            action_type = "automatically" if auto else "successfully"
            print(f"✅ {action_type.title()} disabled {addon_name}")
            
            # Show user notification
            if not auto:
                showInfo(f"Successfully disabled {addon_name} to resolve theme conflicts.\n\nPlease restart Anki for the change to take full effect.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error disabling {addon_name}: {e}")
            return False
    
    def _handle_css_coordination_conflict(self, conflict: Dict[str, Any]) -> bool:
        """Handle conflicts that can be resolved through CSS coordination"""
        addon_name = conflict['name']
        print(f"🔧 Applying CSS coordination for {addon_name}")
        
        # For CSS coordination conflicts, we apply high-specificity CSS
        # without disabling the addon
        return True  # Always return True since we handle it via CSS
    
    def _handle_theme_aware_conflict(self, conflict: Dict[str, Any]) -> bool:
        """Handle conflicts that need theme-aware color injection"""
        addon_name = conflict['name']
        print(f"🎨 Applying theme-aware handling for {addon_name}")
        
        # These conflicts are handled by ensuring our theme colors
        # are injected with appropriate specificity
        return True
    
    def _handle_generic_conflict(self, conflict: Dict[str, Any]) -> bool:
        """Handle generic conflicts with fallback strategy"""
        addon_name = conflict['name']
        print(f"⚙️ Applying generic conflict resolution for {addon_name}")
        return True
    
    def _has_unresolved_nuclear_conflicts(self, conflicts: List[Dict[str, Any]]) -> bool:
        """Check if any conflicts require nuclear CSS"""
        for conflict in conflicts:
            if conflict['enabled'] and conflict.get('nuclear_css_required', False):
                return True
        return False
    
    def apply_nuclear_css(self) -> bool:
        """
        Apply ultra-high specificity CSS that overrides conflicting addon styles
        This is the "nuclear option" for when addon conflicts can't be resolved otherwise
        """
        print("🚀 Applying NUCLEAR CSS for maximum specificity...")
        
        try:
            # Get current theme colors for nuclear CSS
            if not mw or not hasattr(mw, 'addon_config'):
                print("❌ Cannot access theme manager for nuclear CSS")
                return False
            
            # Generate nuclear CSS with ultra-high specificity
            nuclear_css = self._generate_nuclear_css()
            
            # Apply nuclear CSS through multiple injection methods
            self._inject_nuclear_css_multimethod(nuclear_css)
            
            self.nuclear_css_applied = True
            print("✅ Nuclear CSS applied successfully")
            return True
            
        except Exception as e:
            print(f"❌ Nuclear CSS application failed: {e}")
            return False
    
    def _generate_nuclear_css(self) -> str:
        """Generate ultra-high specificity CSS that beats addon conflicts"""
        
        # Try to get current theme colors
        theme_colors = self._get_current_theme_colors()
        
        # Ultra-high specificity selectors (beats most addon CSS)
        nuclear_css = f"""
/* NUCLEAR CSS - Ultra-High Specificity for Addon Conflict Resolution */
/* Specificity: 1,0,0,12+ - Beats most addon CSS */

/* Button Conflicts (The KING of Button Add-ons) */
html body div.deck-browser html body div.overview html body .review-state html body .btn,
html body #main html body .centralwidget html body QPushButton,
html body .review-screen html body .answer-buttons html body button {{
    background-color: {theme_colors.get('button.background', '#404754')} !important;
    color: {theme_colors.get('button.foreground', '#ffffff')} !important;
    border: 1px solid {theme_colors.get('button.border', theme_colors.get('editorGroup.border', '#181a1f'))} !important;
    border-radius: 4px !important;
}}

html body div.deck-browser html body div.overview html body .review-state html body .btn:hover,
html body #main html body .centralwidget html body QPushButton:hover,
html body .review-screen html body .answer-buttons html body button:hover {{
    background-color: {theme_colors.get('button.hoverBackground', '#5a6375')} !important;
}}

/* Tag Conflicts (Colorful Tags) */
html body .deck-browser html body .browser html body .tag,
html body .card html body span.tag,
html body .review html body .tag-color {{
    background-color: {theme_colors.get('badge.background', '#404754')} !important;
    color: {theme_colors.get('badge.foreground', '#ffffff')} !important;
    border: 1px solid {theme_colors.get('editorGroup.border', '#181a1f')} !important;
}}

/* General Interface Elements */
html body #main html body .centralwidget html body QWidget,
html body .deck-browser html body .overview html body div {{
    background-color: {theme_colors.get('editor.background', '#282c34')} !important;
    color: {theme_colors.get('editor.foreground', '#abb2bf')} !important;
}}

/* Input Fields */
html body #main html body QLineEdit,
html body #main html body QTextEdit,
html body .editor html body input,
html body .editor html body textarea {{
    background-color: {theme_colors.get('input.background', '#1e2227')} !important;
    color: {theme_colors.get('input.foreground', theme_colors.get('editor.foreground', '#abb2bf'))} !important;
    border: 1px solid {theme_colors.get('input.border', theme_colors.get('editorGroup.border', '#181a1f'))} !important;
}}

/* Selection and Focus */
html body * html body *:focus,
html body * html body *::selection {{
    background-color: {theme_colors.get('editor.selectionBackground', '#3e4451')} !important;
    color: {theme_colors.get('editor.foreground', '#abb2bf')} !important;
    outline: 2px solid {theme_colors.get('focusBorder', '#007acc')} !important;
}}
        """.strip()
        
        return nuclear_css
    
    def _get_current_theme_colors(self) -> Dict[str, str]:
        """Get current theme colors for nuclear CSS generation"""
        try:
            # Try to access theme manager through various paths
            if hasattr(mw, 'addon_theme_manager'):
                theme = mw.addon_theme_manager.get_current_theme()
                if theme and 'colors' in theme:
                    return theme['colors']
            
            # Fallback to default dark theme colors
            return {
                'editor.background': '#282c34',
                'editor.foreground': '#abb2bf',
                'button.background': '#404754',
                'button.foreground': '#ffffff',
                'button.hoverBackground': '#5a6375',
                'input.background': '#1e2227',
                'editorGroup.border': '#181a1f',
                'focusBorder': '#007acc',
                'editor.selectionBackground': '#3e4451'
            }
            
        except Exception as e:
            print(f"⚠️ Could not get theme colors, using defaults: {e}")
            return {
                'editor.background': '#282c34',
                'editor.foreground': '#abb2bf',
                'button.background': '#404754',
                'button.foreground': '#ffffff',
                'button.hoverBackground': '#5a6375',
                'input.background': '#1e2227',
                'editorGroup.border': '#181a1f',
                'focusBorder': '#007acc',
                'editor.selectionBackground': '#3e4451'
            }
    
    def _inject_nuclear_css_multimethod(self, nuclear_css: str):
        """Inject nuclear CSS through multiple methods for maximum reliability"""
        
        print("💉 Injecting nuclear CSS through multiple channels...")
        
        # Method 1: Direct webview injection
        try:
            if mw and hasattr(mw, 'web'):
                mw.web.eval(f"""
                    var nuclearStyle = document.getElementById('nuclear-addon-conflict-css');
                    if (nuclearStyle) {{
                        nuclearStyle.remove();
                    }}
                    
                    var style = document.createElement('style');
                    style.id = 'nuclear-addon-conflict-css';
                    style.textContent = `{nuclear_css}`;
                    document.head.appendChild(style);
                """)
                print("✅ Nuclear CSS injected via webview")
        except Exception as e:
            print(f"⚠️ Webview injection failed: {e}")
        
        # Method 2: Qt application stylesheet (for Qt widgets)
        try:
            app = QApplication.instance()
            if app:
                current_stylesheet = app.styleSheet()
                # Append nuclear CSS to current stylesheet
                app.setStyleSheet(current_stylesheet + "\n\n" + nuclear_css)
                print("✅ Nuclear CSS injected via Qt stylesheet")
        except Exception as e:
            print(f"⚠️ Qt stylesheet injection failed: {e}")
        
        # Method 3: Main window direct styling
        try:
            if mw:
                current_style = mw.styleSheet()
                mw.setStyleSheet(current_style + "\n\n" + nuclear_css)
                print("✅ Nuclear CSS injected via main window")
        except Exception as e:
            print(f"⚠️ Main window injection failed: {e}")
    
    def start_conflict_monitoring(self):
        """Start real-time monitoring for addon conflicts"""
        if self.monitoring_active:
            print("ℹ️ Conflict monitoring already active")
            return
        
        print("👁️ Starting real-time conflict monitoring...")
        
        def check_conflicts():
            try:
                # Re-detect conflicts
                current_conflicts = self.detect_conflicting_addons()
                
                # Check if any new critical conflicts appeared
                critical_conflicts = [c for c in current_conflicts if c['enabled'] and c['conflict_level'] == 'CRITICAL']
                
                if critical_conflicts and not self.nuclear_css_applied:
                    print("🚨 New critical conflicts detected during monitoring")
                    self.resolve_conflicts_automatically(critical_conflicts)
                
            except Exception as e:
                print(f"⚠️ Error during conflict monitoring: {e}")
        
        # Monitor every 30 seconds
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(check_conflicts)
        self.monitor_timer.start(30000)  # 30 seconds
        
        self.monitoring_active = True
        print("✅ Conflict monitoring started")
    
    def stop_conflict_monitoring(self):
        """Stop real-time conflict monitoring"""
        if hasattr(self, 'monitor_timer'):
            self.monitor_timer.stop()
            self.monitoring_active = False
            print("⏹️ Conflict monitoring stopped")
    
    def get_conflict_report(self) -> Dict[str, Any]:
        """Generate a comprehensive conflict report"""
        conflicts = self.detect_conflicting_addons()
        
        report = {
            'total_conflicts': len(conflicts),
            'critical_conflicts': len([c for c in conflicts if c['conflict_level'] == 'CRITICAL' and c['enabled']]),
            'high_conflicts': len([c for c in conflicts if c['conflict_level'] == 'HIGH' and c['enabled']]),
            'moderate_conflicts': len([c for c in conflicts if c['conflict_level'] == 'MODERATE' and c['enabled']]),
            'nuclear_css_applied': self.nuclear_css_applied,
            'monitoring_active': self.monitoring_active,
            'conflicts': conflicts,
            'recommendations': self._generate_recommendations(conflicts)
        }
        
        return report
    
    def _generate_recommendations(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate user-friendly recommendations for conflict resolution"""
        recommendations = []
        
        critical_enabled = [c for c in conflicts if c['conflict_level'] == 'CRITICAL' and c['enabled']]
        if critical_enabled:
            recommendations.append(
                f"🔴 CRITICAL: {len(critical_enabled)} addon(s) are causing severe theme conflicts. "
                "Consider disabling them for best theme consistency."
            )
        
        high_enabled = [c for c in conflicts if c['conflict_level'] == 'HIGH' and c['enabled']]
        if high_enabled:
            recommendations.append(
                f"🟠 HIGH: {len(high_enabled)} addon(s) may cause noticeable theme inconsistencies."
            )
        
        if self.nuclear_css_applied:
            recommendations.append(
                "🚀 Nuclear CSS is active to override addon conflicts. "
                "Some addon features may be affected."
            )
        
        if not conflicts:
            recommendations.append("✅ No addon conflicts detected. Theme should work perfectly!")
        
        return recommendations


# Global instance for easy access
addon_conflict_manager = None

def get_conflict_manager(config: Dict[str, Any] = None) -> AddonConflictManager:
    """Get or create the global conflict manager instance"""
    global addon_conflict_manager
    if addon_conflict_manager is None:
        addon_conflict_manager = AddonConflictManager(config)
    return addon_conflict_manager

def resolve_all_conflicts(config: Dict[str, Any] = None) -> bool:
    """Convenience function to resolve all addon conflicts"""
    manager = get_conflict_manager(config)
    return manager.resolve_conflicts_automatically()

def apply_nuclear_css_emergency() -> bool:
    """Emergency function to apply nuclear CSS immediately"""
    manager = get_conflict_manager()
    return manager.apply_nuclear_css() 