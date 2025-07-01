#!/usr/bin/env python3
"""
THEME CONSISTENCY DIAGNOSTIC TOOL

Run from Anki Debug Console:
exec(open("/Users/stevmq/Library/Application Support/Anki2/addons21/vscode_themes_anki/theme_diagnostic.py").read())
"""

def comprehensive_theme_diagnostic():
    """Comprehensive diagnostic of theme consistency issues"""
    print("🔍 THEME CONSISTENCY DIAGNOSTIC")
    print("=" * 50)
    
    try:
        # Phase 1: Get theme manager state
        print("\n📊 PHASE 1: Theme Manager Analysis")
        print("-" * 30)
        
        import __init__ as addon_module
        theme_mgr = getattr(addon_module, 'theme_mgr', None)
        
        if not theme_mgr:
            print("❌ CRITICAL: Theme manager not found")
            return False
            
        print(f"✅ Theme manager found")
        print(f"📚 Themes loaded: {len(theme_mgr.themes)}")
        print(f"🎨 Current theme: {theme_mgr.config.get('current_theme', 'None')}")
        
        # Phase 2: CSS Generation Analysis  
        print("\n🎨 PHASE 2: CSS Generation Analysis")
        print("-" * 30)
        
        try:
            current_css = theme_mgr.get_current_theme_css()
            print(f"📏 CSS length: {len(current_css)} characters")
            
            # Check for unified system indicators
            indicators = {
                "CSS Variables": "--vscode-bg-primary" in current_css,
                "Variable Usage": "var(--vscode-bg-primary)" in current_css,
                "High Specificity": "html body" in current_css,
                "Important Rules": "!important" in current_css,
                "Context Targeting": "body.deckbrowser" in current_css
            }
            
            print("🔍 CSS System Analysis:")
            for indicator, present in indicators.items():
                status = "✅" if present else "❌"
                print(f"  {status} {indicator}")
                
            # Identify missing elements
            missing = [key for key, present in indicators.items() if not present]
            if missing:
                print(f"\n⚠️ Missing CSS features: {', '.join(missing)}")
            else:
                print("\n✅ All CSS features present")
                
        except Exception as e:
            print(f"❌ CSS generation failed: {e}")
            
        # Phase 3: Context Filtering Analysis
        print("\n🔗 PHASE 3: Context Detection Analysis")
        print("-" * 30)
        
        # Simulate context detection
        test_contexts = [
            "deckbrowser", "overview", "reviewer", "browser",
            "card_layout", "clayout", "editor", "main"
        ]
        
        print("Testing context filtering:")
        for context in test_contexts:
            # Simulate the filtering logic from __init__.py
            context_str = str(context).lower()
            unsafe_contexts = ["card_layout", "clayout", "editor", "card_", "note_"]
            is_blocked = any(unsafe in context_str for unsafe in unsafe_contexts)
            
            status = "🚫 BLOCKED" if is_blocked else "✅ ALLOWED"
            print(f"  {status} {context}")
            
        # Phase 4: CSS Specificity Test
        print("\n⚖️ PHASE 4: CSS Specificity Analysis")
        print("-" * 30)
        
        # Get current theme colors for testing
        current_theme = theme_mgr.get_current_theme()
        if current_theme:
            colors = current_theme.get("colors", {})
            bg_color = colors.get('editor.background', '#282c34')
            fg_color = colors.get('editor.foreground', '#abb2bf')
            
            print(f"🎨 Theme colors:")
            print(f"  Background: {bg_color}")
            print(f"  Foreground: {fg_color}")
            
            # Analyze CSS selectors used
            selector_analysis = {
                "Basic selectors": "body {" in current_css,
                "High specificity": "html body" in current_css,
                "Context specific": ".deckbrowser" in current_css,
                "Table targeting": "table" in current_css,
                "Important rules": "!important" in current_css
            }
            
            print("🎯 Selector Analysis:")
            for selector, present in selector_analysis.items():
                status = "✅" if present else "❌"
                print(f"  {status} {selector}")
        
        # Phase 5: Recommendations
        print("\n💡 PHASE 5: Recommendations")
        print("-" * 30)
        
        recommendations = []
        
        if not indicators.get("CSS Variables", False):
            recommendations.append("Apply runtime hotfix to enable CSS variables")
            
        if not indicators.get("High Specificity", False):
            recommendations.append("Increase CSS specificity with 'html body' selectors")
            
        if not indicators.get("Important Rules", False):
            recommendations.append("Add !important rules to override Anki defaults")
            
        if not recommendations:
            recommendations.append("CSS system appears complete - check browser caching")
            
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
            
        print(f"\n🎯 Priority: {recommendations[0] if recommendations else 'All systems operational'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def quick_css_specificity_test():
    """Test CSS specificity requirements"""
    print("\n🧪 CSS SPECIFICITY TEST")
    print("-" * 25)
    
    # Test different specificity levels
    specificity_levels = [
        ("Low", "body { background: red; }"),
        ("Medium", "body.deckbrowser { background: blue; }"),
        ("High", "html body.deckbrowser { background: green; }"),
        ("Ultra", "html body.deckbrowser div table { background: yellow; }")
    ]
    
    print("Recommended specificity levels:")
    for level, example in specificity_levels:
        print(f"  {level}: {example}")
    
    print("\n💡 For maximum override power, use Ultra level with !important")

# Execute diagnostic
if __name__ == "__main__":
    comprehensive_theme_diagnostic()
    quick_css_specificity_test()
    
print("\n" + "="*50)
print("🚀 Ready to apply enhanced hotfix based on diagnostic results") 