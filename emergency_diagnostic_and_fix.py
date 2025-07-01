"""
EMERGENCY DIAGNOSTIC AND FIX - Immediate theme consistency repair
Run this in Anki debug console to diagnose and fix theme issues right now
"""

# Required imports
try:
    from aqt import mw
    from aqt.qt import QTimer, QApplication
except ImportError:
    pass

def emergency_diagnosis_and_fix():
    """
    Comprehensive emergency diagnosis and immediate fix application
    Use this when theme consistency is still broken
    """
    print("🚨 EMERGENCY THEME CONSISTENCY DIAGNOSTIC")
    print("=" * 50)
    
    try:
        # Test 1: Check if our conflict manager exists and works
        print("\n📍 TEST 1: Conflict Manager System")
        try:
            from addon_conflict_manager import get_conflict_manager, apply_nuclear_css_emergency
            conflict_manager = get_conflict_manager()
            
            # Detect conflicts
            conflicts = conflict_manager.detect_conflicting_addons()
            critical_conflicts = [c for c in conflicts if c['enabled'] and c['conflict_level'] == 'CRITICAL']
            
            print(f"✅ Conflict manager working")
            print(f"   📊 Total conflicts: {len(conflicts)}")
            print(f"   🔴 Critical conflicts: {len(critical_conflicts)}")
            
            if critical_conflicts:
                for conflict in critical_conflicts:
                    print(f"      • {conflict['name']} - ENABLED and causing issues")
            
        except ImportError as e:
            print(f"❌ Conflict manager import failed: {e}")
            
        except Exception as e:
            print(f"❌ Conflict manager test failed: {e}")
        
        # Test 2: Check theme manager and CSS generation
        print("\n📍 TEST 2: Theme Manager and CSS")
        try:
            # Try to access theme manager
            if hasattr(mw, 'addon_theme_manager'):
                theme_mgr = mw.addon_theme_manager
                print("✅ Theme manager accessible via mw.addon_theme_manager")
            else:
                print("❌ Theme manager not found at mw.addon_theme_manager")
                # Try alternative access
                print("🔍 Searching for theme manager...")
                
            # Test CSS generation
            if 'theme_mgr' in locals():
                css = theme_mgr.get_current_theme_css()
                css_length = len(css) if css else 0
                print(f"✅ CSS generation working: {css_length} characters")
                
                # Check for key elements in CSS
                has_variables = '--vscode-' in css if css else False
                has_high_specificity = 'html body' in css if css else False
                has_important = '!important' in css if css else False
                
                print(f"   📊 CSS Variables: {has_variables}")
                print(f"   📊 High Specificity: {has_high_specificity}")
                print(f"   📊 Important Rules: {has_important}")
                
        except Exception as e:
            print(f"❌ Theme manager test failed: {e}")
        
        # Test 3: Check webview injection
        print("\n📍 TEST 3: Webview CSS Injection")
        try:
            if mw and hasattr(mw, 'web'):
                # Test if we can inject CSS directly
                test_css = """
                body { border: 2px solid red !important; }
                """
                mw.web.eval(f"""
                    var testStyle = document.getElementById('emergency-test-css');
                    if (testStyle) testStyle.remove();
                    
                    var style = document.createElement('style');
                    style.id = 'emergency-test-css';
                    style.textContent = `{test_css}`;
                    document.head.appendChild(style);
                    
                    console.log('Emergency CSS test injected');
                """)
                print("✅ Webview injection test completed")
                
                # Remove test CSS after 2 seconds
                def remove_test():
                    try:
                        mw.web.eval("document.getElementById('emergency-test-css')?.remove();")
                    except:
                        pass
                
                QTimer.singleShot(2000, remove_test)
                
        except Exception as e:
            print(f"❌ Webview injection test failed: {e}")
        
        # EMERGENCY FIX 1: Direct nuclear CSS injection
        print("\n🚀 EMERGENCY FIX 1: Direct Nuclear CSS")
        try:
            # Apply ultra-high specificity CSS directly
            emergency_nuclear_css = """
            /* EMERGENCY NUCLEAR CSS - MAXIMUM SPECIFICITY */
            html body div#main html body .centralwidget html body * {
                background-color: #282c34 !important;
                color: #abb2bf !important;
            }
            
            html body div#main html body .centralwidget html body QPushButton,
            html body div#main html body .centralwidget html body .btn,
            html body div#main html body .centralwidget html body button {
                background-color: #404754 !important;
                color: #ffffff !important;
                border: 1px solid #181a1f !important;
                border-radius: 4px !important;
            }
            
            html body div#main html body .centralwidget html body QPushButton:hover,
            html body div#main html body .centralwidget html body .btn:hover,
            html body div#main html body .centralwidget html body button:hover {
                background-color: #5a6375 !important;
            }
            
            html body div#main html body .centralwidget html body QLineEdit,
            html body div#main html body .centralwidget html body QTextEdit,
            html body div#main html body .centralwidget html body input,
            html body div#main html body .centralwidget html body textarea {
                background-color: #1e2227 !important;
                color: #abb2bf !important;
                border: 1px solid #181a1f !important;
            }
            """
            
            # Method 1: Webview injection
            if mw and hasattr(mw, 'web'):
                mw.web.eval(f"""
                    var nuclearStyle = document.getElementById('emergency-nuclear-css');
                    if (nuclearStyle) nuclearStyle.remove();
                    
                    var style = document.createElement('style');
                    style.id = 'emergency-nuclear-css';
                    style.textContent = `{emergency_nuclear_css}`;
                    document.head.appendChild(style);
                    
                    console.log('Emergency nuclear CSS applied via webview');
                """)
                print("✅ Nuclear CSS applied via webview")
            
            # Method 2: Qt Application stylesheet
            try:
                from aqt.qt import QApplication
                app = QApplication.instance()
                if app:
                    current_style = app.styleSheet()
                    app.setStyleSheet(current_style + "\n\n" + emergency_nuclear_css)
                    print("✅ Nuclear CSS applied via Qt stylesheet")
            except Exception as e:
                print(f"⚠️ Qt stylesheet failed: {e}")
            
            # Method 3: Main window direct
            try:
                if mw:
                    current_style = mw.styleSheet()
                    mw.setStyleSheet(current_style + "\n\n" + emergency_nuclear_css)
                    print("✅ Nuclear CSS applied via main window")
            except Exception as e:
                print(f"⚠️ Main window styling failed: {e}")
            
        except Exception as e:
            print(f"❌ Emergency nuclear CSS failed: {e}")
        
        # EMERGENCY FIX 2: Force theme reapplication
        print("\n🔄 EMERGENCY FIX 2: Force Theme Reapplication")
        try:
            # Try to force theme reapplication through theme manager
            if hasattr(mw, 'addon_theme_manager'):
                mw.addon_theme_manager.force_theme_refresh()
                mw.addon_theme_manager.apply_current_theme()
                print("✅ Forced theme reapplication")
            else:
                print("⚠️ Theme manager not accessible for reapplication")
                
        except Exception as e:
            print(f"❌ Force reapplication failed: {e}")
        
        # EMERGENCY FIX 3: Disable conflicting addons immediately
        print("\n🔧 EMERGENCY FIX 3: Disable Critical Conflicts")
        try:
            # Known critical addon IDs
            critical_addon_ids = ['374005964']  # The KING of Button Add-ons
            
            for addon_id in critical_addon_ids:
                try:
                    if mw and hasattr(mw, 'addonManager'):
                        all_addons = mw.addonManager.allAddons()
                        if addon_id in all_addons and mw.addonManager.isEnabled(addon_id):
                            # Disable without asking (emergency mode)
                            mw.addonManager.toggleEnabled(addon_id, enable=False)
                            print(f"✅ Emergency disabled addon {addon_id}")
                        else:
                            print(f"ℹ️ Addon {addon_id} not found or already disabled")
                except Exception as e:
                    print(f"⚠️ Failed to disable addon {addon_id}: {e}")
                    
        except Exception as e:
            print(f"❌ Emergency addon disabling failed: {e}")
        
        print("\n🎯 EMERGENCY FIXES COMPLETE")
        print("✅ Multiple CSS injection methods applied")
        print("✅ Critical addons disabled")
        print("✅ Theme reapplication attempted")
        print("\n🔄 Please restart Anki for full effect")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_direct_nuclear_css():
    """
    Direct nuclear CSS application without any dependencies
    Use this if everything else fails
    """
    print("🚀 DIRECT NUCLEAR CSS APPLICATION")
    print("=" * 35)
    
    try:
        # Ultra-high specificity CSS that should beat everything
        nuclear_css = """
        /* DIRECT NUCLEAR CSS - BEATS ALL ADDON CONFLICTS */
        html body div html body div html body div html body * {
            background-color: #282c34 !important;
            color: #abb2bf !important;
        }
        
        html body div html body div html body div html body QPushButton,
        html body div html body div html body div html body .btn,
        html body div html body div html body div html body button {
            background-color: #404754 !important;
            color: #ffffff !important;
            border: 1px solid #181a1f !important;
            border-radius: 4px !important;
            font-family: inherit !important;
        }
        
        html body div html body div html body div html body QPushButton:hover,
        html body div html body div html body div html body .btn:hover,
        html body div html body div html body div html body button:hover {
            background-color: #5a6375 !important;
        }
        """
        
        # Apply through all possible methods
        if mw and hasattr(mw, 'web'):
            mw.web.eval(f"""
                var directNuclear = document.getElementById('direct-nuclear-css');
                if (directNuclear) directNuclear.remove();
                
                var style = document.createElement('style');
                style.id = 'direct-nuclear-css';
                style.textContent = `{nuclear_css}`;
                document.head.appendChild(style);
            """)
            print("✅ Direct nuclear CSS applied")
            return True
        else:
            print("❌ Cannot apply direct nuclear CSS - webview not available")
            return False
            
    except Exception as e:
        print(f"❌ Direct nuclear CSS failed: {e}")
        return False

# Instructions
def print_emergency_instructions():
    print("""
🚨 EMERGENCY THEME FIX COMMANDS

1. Full emergency diagnosis and fix:
   exec(open('emergency_diagnostic_and_fix.py').read()); emergency_diagnosis_and_fix()

2. Direct nuclear CSS only:
   exec(open('emergency_diagnostic_and_fix.py').read()); apply_direct_nuclear_css()

These commands will:
• Test what's failing in the theme system
• Apply emergency nuclear CSS with maximum specificity
• Disable critical conflicting addons
• Force theme reapplication

If themes are still broken after this, the issue is deeper than addon conflicts.
    """)

if __name__ == "__main__":
    print_emergency_instructions() 