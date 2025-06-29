#!/usr/bin/env python3
"""
Theme Validator for VS Code Themes
Validates themes for compatibility with Anki add-on and checks structure
"""

import json
import os
from pathlib import Path
import sys

class ThemeValidator:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self.valid_themes = []
        self.invalid_themes = []
        
        # Required fields for VS Code themes
        self.required_fields = [
            "name",
            "colors",
            "tokenColors"
        ]
        
        # Essential color properties for Anki add-on
        self.essential_colors = [
            "editor.background",
            "editor.foreground",
            "editor.selectionBackground",
            "editor.lineHighlightBackground",
            "editorCursor.foreground"
        ]
        
        # Common optional but recommended colors
        self.recommended_colors = [
            "sideBar.background",
            "sideBar.foreground", 
            "activityBar.background",
            "activityBar.foreground",
            "statusBar.background",
            "statusBar.foreground",
            "tab.activeBackground",
            "tab.activeForeground"
        ]
    
    def validate_json_structure(self, theme_path):
        """Validate basic JSON structure and required fields"""
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Check required top-level fields
            missing_fields = []
            for field in self.required_fields:
                if field not in theme_data:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Missing required fields: {missing_fields}"
            
            # Validate name field
            if not isinstance(theme_data.get("name"), str) or not theme_data["name"].strip():
                return False, "Theme name must be a non-empty string"
            
            # Validate colors section
            if not isinstance(theme_data.get("colors"), dict):
                return False, "Colors section must be an object"
            
            # Validate tokenColors section
            if not isinstance(theme_data.get("tokenColors"), list):
                return False, "TokenColors section must be an array"
            
            return True, theme_data
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def validate_color_properties(self, theme_data):
        """Validate essential color properties"""
        colors = theme_data.get("colors", {})
        issues = []
        
        # Check for essential colors
        missing_essential = []
        for color in self.essential_colors:
            if color not in colors:
                missing_essential.append(color)
        
        if missing_essential:
            issues.append(f"Missing essential colors: {missing_essential}")
        
        # Check for recommended colors
        missing_recommended = []
        for color in self.recommended_colors:
            if color not in colors:
                missing_recommended.append(color)
        
        if missing_recommended:
            issues.append(f"Missing recommended colors: {missing_recommended}")
        
        # Validate color format (should be hex colors)
        invalid_colors = []
        for key, value in colors.items():
            if isinstance(value, str):
                # Check if it's a valid hex color
                if not (value.startswith('#') and len(value) in [7, 9] and 
                       all(c in '0123456789ABCDEFabcdef' for c in value[1:])):
                    invalid_colors.append(f"{key}: {value}")
        
        if invalid_colors:
            issues.append(f"Invalid color formats: {invalid_colors[:5]}")  # Limit to first 5
        
        return issues
    
    def validate_token_colors(self, theme_data):
        """Validate token colors structure"""
        token_colors = theme_data.get("tokenColors", [])
        issues = []
        
        if not token_colors:
            issues.append("No token colors defined")
            return issues
        
        for i, token in enumerate(token_colors):
            if not isinstance(token, dict):
                issues.append(f"Token color {i} is not an object")
                continue
            
            # Check for required fields in token color
            if "scope" not in token:
                issues.append(f"Token color {i} missing 'scope' field")
            
            if "settings" not in token:
                issues.append(f"Token color {i} missing 'settings' field")
            
            # Validate scope format
            scope = token.get("scope")
            if scope is not None and not (isinstance(scope, list) or isinstance(scope, str)):
                issues.append(f"Token color {i} scope must be string or array")
            
            # Validate settings
            settings = token.get("settings")
            if settings is not None and not isinstance(settings, dict):
                issues.append(f"Token color {i} settings must be an object")
        
        return issues
    
    def fix_common_issues(self, theme_path, theme_data):
        """Attempt to fix common theme issues"""
        fixed = False
        
        # Add missing type field if not present
        if "type" not in theme_data:
            # Guess type based on background color
            bg_color = theme_data.get("colors", {}).get("editor.background", "#000000")
            if bg_color.startswith('#'):
                # Simple brightness check
                hex_color = bg_color[1:7]
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    brightness = (r * 299 + g * 587 + b * 114) / 1000
                    theme_data["type"] = "light" if brightness > 127 else "dark"
                    fixed = True
                except:
                    theme_data["type"] = "dark"  # Default to dark
                    fixed = True
        
        # Ensure all essential colors exist with reasonable defaults
        colors = theme_data.setdefault("colors", {})
        if theme_data.get("type") == "light":
            defaults = {
                "editor.background": "#FFFFFF",
                "editor.foreground": "#000000",
                "editor.selectionBackground": "#ADD6FF",
                "editor.lineHighlightBackground": "#F0F0F0",
                "editorCursor.foreground": "#000000"
            }
        else:
            defaults = {
                "editor.background": "#1E1E1E",
                "editor.foreground": "#D4D4D4",
                "editor.selectionBackground": "#264F78",
                "editor.lineHighlightBackground": "#2A2D2E",
                "editorCursor.foreground": "#AEAFAD"
            }
        
        for key, default_value in defaults.items():
            if key not in colors:
                colors[key] = default_value
                fixed = True
        
        # Save fixed theme if changes were made
        if fixed:
            backup_path = theme_path.with_suffix('.json.backup')
            theme_path.rename(backup_path)
            
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Fixed and saved (backup: {backup_path.name})"
        
        return False, "No fixes needed"
    
    def validate_theme(self, theme_path):
        """Validate a single theme file"""
        theme_name = theme_path.name
        
        # Validate JSON structure
        is_valid, result = self.validate_json_structure(theme_path)
        if not is_valid:
            return {
                "name": theme_name,
                "valid": False,
                "errors": [result],
                "warnings": [],
                "fixed": False
            }
        
        theme_data = result
        errors = []
        warnings = []
        
        # Validate color properties
        color_issues = self.validate_color_properties(theme_data)
        for issue in color_issues:
            if "Missing essential" in issue:
                errors.append(issue)
            else:
                warnings.append(issue)
        
        # Validate token colors
        token_issues = self.validate_token_colors(theme_data)
        warnings.extend(token_issues)
        
        # Attempt to fix if there are errors
        fixed = False
        if errors:
            fix_result, fix_message = self.fix_common_issues(theme_path, theme_data)
            if fix_result:
                fixed = True
                warnings.append(f"Auto-fixed: {fix_message}")
                # Re-validate after fixing
                errors = []
                color_issues = self.validate_color_properties(theme_data)
                for issue in color_issues:
                    if "Missing essential" in issue:
                        errors.append(issue)
        
        return {
            "name": theme_name,
            "theme_display_name": theme_data.get("name", theme_name),
            "type": theme_data.get("type", "unknown"),
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "fixed": fixed,
            "colors_count": len(theme_data.get("colors", {})),
            "token_colors_count": len(theme_data.get("tokenColors", []))
        }
    
    def validate_all_themes(self):
        """Validate all themes in the directory"""
        theme_files = list(self.themes_dir.glob("*.json"))
        
        # Exclude non-theme files
        theme_files = [f for f in theme_files if not f.name.startswith('themes_metadata')]
        
        results = []
        
        print(f"Validating {len(theme_files)} theme files...")
        print("-" * 60)
        
        for theme_file in sorted(theme_files):
            result = self.validate_theme(theme_file)
            results.append(result)
            
            # Print immediate feedback
            status = "✅ VALID" if result["valid"] else "❌ INVALID"
            fixes = " (FIXED)" if result["fixed"] else ""
            print(f"{status}{fixes} {result['name']} - {result['theme_display_name']}")
            
            for error in result["errors"]:
                print(f"  ❌ {error}")
            
            for warning in result["warnings"][:3]:  # Limit warnings display
                print(f"  ⚠️  {warning}")
        
        return results
    
    def generate_report(self, results):
        """Generate a comprehensive validation report"""
        valid_themes = [r for r in results if r["valid"]]
        invalid_themes = [r for r in results if not r["valid"]]
        fixed_themes = [r for r in results if r["fixed"]]
        
        print("\n" + "=" * 60)
        print("THEME VALIDATION REPORT")
        print("=" * 60)
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total themes: {len(results)}")
        print(f"  Valid themes: {len(valid_themes)}")
        print(f"  Invalid themes: {len(invalid_themes)}")
        print(f"  Auto-fixed themes: {len(fixed_themes)}")
        print(f"  Success rate: {len(valid_themes)/len(results)*100:.1f}%")
        
        if valid_themes:
            print(f"\n✅ VALID THEMES ({len(valid_themes)}):")
            dark_themes = [t for t in valid_themes if t.get("type") == "dark"]
            light_themes = [t for t in valid_themes if t.get("type") == "light"]
            
            print(f"  Dark themes ({len(dark_themes)}):")
            for theme in sorted(dark_themes, key=lambda x: x["theme_display_name"]):
                print(f"    • {theme['theme_display_name']}")
            
            print(f"  Light themes ({len(light_themes)}):")
            for theme in sorted(light_themes, key=lambda x: x["theme_display_name"]):
                print(f"    • {theme['theme_display_name']}")
        
        if invalid_themes:
            print(f"\n❌ INVALID THEMES ({len(invalid_themes)}):")
            for theme in invalid_themes:
                print(f"  • {theme['name']} - {'; '.join(theme['errors'])}")
        
        if fixed_themes:
            print(f"\n🔧 AUTO-FIXED THEMES ({len(fixed_themes)}):")
            for theme in fixed_themes:
                print(f"  • {theme['theme_display_name']}")
        
        print(f"\n🎨 THEME COMPATIBILITY:")
        print(f"  All valid themes are ready for use in your Anki add-on!")
        print(f"  Themes with rich color schemes: {len([t for t in valid_themes if t['colors_count'] > 50])}")
        print(f"  Themes with comprehensive syntax highlighting: {len([t for t in valid_themes if t['token_colors_count'] > 20])}")

def main():
    print("VS Code Theme Validator for Anki Add-on")
    print("=" * 50)
    
    validator = ThemeValidator()
    
    if not validator.themes_dir.exists():
        print(f"❌ Themes directory not found: {validator.themes_dir}")
        return
    
    # Validate all themes
    results = validator.validate_all_themes()
    
    # Generate report
    validator.generate_report(results)
    
    # Save detailed results
    report_file = validator.themes_dir / "validation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main() 