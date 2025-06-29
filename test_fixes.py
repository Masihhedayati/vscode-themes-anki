#!/usr/bin/env python3
"""
Test script to verify VS Code Themes Anki fixes
Run this after restarting Anki to check if the issues are resolved
"""

def test_fixes():
    """Test if the three main issues have been fixed"""
    from aqt import mw
    from aqt.qt import QApplication, QToolBar
    
    print("=== VS Code Themes Fix Verification ===\n")
    
    # Test 1: Check if toolbar has dark background
    print("1. Checking toolbar theming...")
    app = QApplication.instance()
    if app and app.styleSheet():
        if "#282c34" in app.styleSheet() or "background-color:" in app.styleSheet():
            print("✓ Application-level stylesheet is applied")
        else:
            print("✗ Application stylesheet may not be properly set")
    
    # Check if toolbars exist and have styles
    if mw:
        toolbars = mw.findChildren(QToolBar)
        if toolbars:
            print(f"✓ Found {len(toolbars)} toolbar(s)")
            for i, toolbar in enumerate(toolbars):
                if toolbar.styleSheet() or (app and app.styleSheet()):
                    print(f"  - Toolbar {i+1}: Styled")
                else:
                    print(f"  - Toolbar {i+1}: No style applied")
        else:
            print("✗ No toolbars found")
    
    # Test 2: Check webview CSS injection
    print("\n2. Checking deck browser CSS...")
    if hasattr(mw, 'web') and mw.web:
        # Check if CSS is injected
        result = mw.web.page().runJavaScript("""
            var hasThemeCSS = document.getElementById('vscode-theme-css') !== null;
            var bodyBg = window.getComputedStyle(document.body).backgroundColor;
            JSON.stringify({hasCSS: hasThemeCSS, bgColor: bodyBg});
        """, lambda x: print(f"✓ Webview check: {x}"))
    
    # Test 3: Check timing mechanisms
    print("\n3. Checking timing mechanisms...")
    from . import theme_manager
    if hasattr(theme_manager.ThemeManager, '_force_toolbar_refresh'):
        print("✓ Toolbar refresh method exists")
    if hasattr(theme_manager.ThemeManager, '_delayed_webview_refresh'):
        print("✓ Delayed webview refresh method exists")
    
    print("\n=== Manual Verification Steps ===")
    print("1. Deck Browser Gap: Look at the deck list - there should be NO gap between header and first deck")
    print("2. Toolbar Theme: The top navigation bar should match your VS Code theme colors")
    print("3. Theme Persistence: Switch themes and check if they apply immediately and persist")
    print("\nIf any issues persist, check the Anki console for errors.")

if __name__ == "__main__":
    test_fixes()