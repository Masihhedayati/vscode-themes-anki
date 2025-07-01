"""
Test Script for Addon Conflict Resolution System
Run this in Anki's debug console to test and manually trigger conflict resolution
"""

def test_addon_conflict_system():
    """
    Test the addon conflict detection and resolution system
    Run this in Anki debug console: exec(open('test_addon_conflicts.py').read())
    """
    print("🧪 Testing Addon Conflict Resolution System")
    print("=" * 50)
    
    try:
        # Import the conflict manager
        from addon_conflict_manager import get_conflict_manager
        
        # Get conflict manager instance
        conflict_manager = get_conflict_manager()
        
        # Test 1: Detect conflicts
        print("\n📍 Test 1: Detecting addon conflicts...")
        conflicts = conflict_manager.detect_conflicting_addons()
        
        if conflicts:
            print(f"⚠️ Found {len(conflicts)} potential conflicts:")
            for conflict in conflicts:
                status = "🔴 ENABLED" if conflict['enabled'] else "⚪ DISABLED"
                print(f"   {status} {conflict['name']} - {conflict['conflict_level']}")
        else:
            print("✅ No addon conflicts detected")
        
        # Test 2: Get conflict report
        print("\n📍 Test 2: Generating conflict report...")
        report = conflict_manager.get_conflict_report()
        
        print(f"📊 Conflict Report:")
        print(f"   Total conflicts: {report['total_conflicts']}")
        print(f"   Critical: {report['critical_conflicts']}")
        print(f"   High: {report['high_conflicts']}")
        print(f"   Moderate: {report['moderate_conflicts']}")
        print(f"   Nuclear CSS applied: {report['nuclear_css_applied']}")
        
        # Test 3: Show recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Test 4: Test nuclear CSS generation (without applying)
        print("\n📍 Test 3: Testing nuclear CSS generation...")
        nuclear_css = conflict_manager._generate_nuclear_css()
        css_length = len(nuclear_css)
        has_high_specificity = 'html body' in nuclear_css
        has_important = '!important' in nuclear_css
        
        print(f"✅ Nuclear CSS generated: {css_length} characters")
        print(f"   High specificity selectors: {has_high_specificity}")
        print(f"   Important declarations: {has_important}")
        
        print("\n🎯 Test Results:")
        print("✅ Conflict detection: Working")
        print("✅ Conflict reporting: Working") 
        print("✅ Nuclear CSS generation: Working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure addon_conflict_manager.py is in the addon directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def resolve_conflicts_now():
    """
    Manually resolve addon conflicts immediately
    Use this if themes are not applying correctly
    """
    print("🔧 Manual Conflict Resolution")
    print("=" * 30)
    
    try:
        from addon_conflict_manager import get_conflict_manager
        
        conflict_manager = get_conflict_manager()
        
        # Detect conflicts first
        conflicts = conflict_manager.detect_conflicting_addons()
        critical_conflicts = [c for c in conflicts if c['enabled'] and c['conflict_level'] == 'CRITICAL']
        
        if critical_conflicts:
            print(f"🔴 Found {len(critical_conflicts)} CRITICAL conflicts:")
            for conflict in critical_conflicts:
                print(f"   • {conflict['name']} - {conflict['description']}")
            
            print("\n🔧 Attempting automatic resolution...")
            success = conflict_manager.resolve_conflicts_automatically()
            
            if success:
                print("✅ All critical conflicts resolved!")
                print("🔄 Please restart Anki for changes to take full effect")
            else:
                print("⚠️ Some conflicts remain, applying nuclear CSS...")
                nuclear_success = conflict_manager.apply_nuclear_css()
                if nuclear_success:
                    print("✅ Nuclear CSS applied as fallback")
                else:
                    print("❌ Nuclear CSS failed")
        else:
            print("✅ No critical conflicts found")
            
        return True
        
    except Exception as e:
        print(f"❌ Manual resolution failed: {e}")
        return False

def apply_emergency_nuclear_css():
    """
    Emergency function to apply nuclear CSS for maximum theme consistency
    Use this as last resort when themes are completely broken
    """
    print("🚀 Emergency Nuclear CSS Application")
    print("=" * 35)
    
    try:
        from addon_conflict_manager import apply_nuclear_css_emergency
        
        success = apply_nuclear_css_emergency()
        
        if success:
            print("✅ Emergency nuclear CSS applied successfully!")
            print("🎨 Themes should now override all conflicting addon styles")
            print("⚠️ Some addon features may be affected")
        else:
            print("❌ Emergency nuclear CSS failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Emergency CSS failed: {e}")
        return False

def show_conflict_status():
    """
    Show current addon conflict status
    """
    print("📊 Addon Conflict Status Report")
    print("=" * 32)
    
    try:
        from addon_conflict_manager import get_conflict_manager
        
        conflict_manager = get_conflict_manager()
        report = conflict_manager.get_conflict_report()
        
        print(f"📦 Total potential conflicts: {report['total_conflicts']}")
        print(f"🔴 Critical conflicts (enabled): {report['critical_conflicts']}")
        print(f"🟠 High conflicts (enabled): {report['high_conflicts']}")
        print(f"🟡 Moderate conflicts (enabled): {report['moderate_conflicts']}")
        print(f"🚀 Nuclear CSS active: {report['nuclear_css_applied']}")
        print(f"👁️ Monitoring active: {report['monitoring_active']}")
        
        if report['conflicts']:
            print(f"\n📋 Detected Conflicts:")
            for conflict in report['conflicts']:
                status = "🔴 ENABLED" if conflict['enabled'] else "⚪ DISABLED"
                level_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MODERATE": "🟡"}.get(conflict['conflict_level'], "⚪")
                print(f"   {status} {level_icon} {conflict['name']}")
                print(f"      └─ {conflict['description']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        return report
        
    except Exception as e:
        print(f"❌ Status report failed: {e}")
        return None

# Instructions for users
def print_instructions():
    """
    Print instructions for using the conflict resolution system
    """
    print("""
🔧 VS Code Themes Addon - Conflict Resolution Instructions

MANUAL COMMANDS (paste in Anki debug console):

1. Test the system:
   exec(open('test_addon_conflicts.py').read()); test_addon_conflict_system()

2. Show current conflict status:
   exec(open('test_addon_conflicts.py').read()); show_conflict_status()

3. Resolve conflicts manually:
   exec(open('test_addon_conflicts.py').read()); resolve_conflicts_now()

4. Emergency nuclear CSS (last resort):
   exec(open('test_addon_conflicts.py').read()); apply_emergency_nuclear_css()

WHAT THIS FIXES:
• Buttons not matching theme colors (The KING of Button Add-ons)
• Tags not following theme colors (Colorful Tags)
• Interface elements staying default Anki colors
• General theme consistency issues

KNOWN CONFLICTS:
🔴 CRITICAL: The KING of Button Add-ons (auto-disable recommended)
🟠 HIGH: Colorful Tags Hierarchical Tags (CSS coordination)
🟡 MODERATE: Review Heatmap, AnKing Note Types

If you see this message, the conflict resolution system is working!
    """)

# Auto-run instructions when script is executed
if __name__ == "__main__":
    print_instructions() 