#!/usr/bin/env python3
"""
Simple Theme Downloader for VS Code Themes
Downloads from direct URLs and NPM packages for guaranteed working themes
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
import time
import sys

class SimpleThemeDownloader:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Direct working URLs for themes
        self.direct_themes = [
            # Catppuccin from NPM distribution
            {
                "name": "catppuccin_latte",
                "url": "https://unpkg.com/@catppuccin/vscode@latest/themes/latte.json"
            },
            {
                "name": "catppuccin_frappe", 
                "url": "https://unpkg.com/@catppuccin/vscode@latest/themes/frappe.json"
            },
            {
                "name": "catppuccin_macchiato",
                "url": "https://unpkg.com/@catppuccin/vscode@latest/themes/macchiato.json"
            },
            {
                "name": "catppuccin_mocha",
                "url": "https://unpkg.com/@catppuccin/vscode@latest/themes/mocha.json"
            },
            
            # VSCode default themes from Microsoft's repo
            {
                "name": "dark_plus",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/dark_plus.json"
            },
            {
                "name": "light_plus",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/light_plus.json"
            },
            {
                "name": "dark_vs",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/dark_vs.json"
            },
            {
                "name": "light_vs",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/light_vs.json"
            },
            {
                "name": "high_contrast",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/hc_black.json"
            },
            {
                "name": "high_contrast_light",
                "url": "https://raw.githubusercontent.com/microsoft/vscode/main/extensions/theme-defaults/themes/hc_light.json"
            },
            
            # Community themes with verified URLs
            {
                "name": "palenight", 
                "url": "https://raw.githubusercontent.com/whizkydee/vscode-material-palenight-theme/master/themes/palenight.json"
            },
            {
                "name": "atom_one_dark",
                "url": "https://raw.githubusercontent.com/akamud/vscode-theme-onedark/master/themes/OneDark.json"
            },
            {
                "name": "atom_one_light",
                "url": "https://raw.githubusercontent.com/akamud/vscode-theme-onelight/master/themes/OneLight.json"
            },
            {
                "name": "noctis",
                "url": "https://raw.githubusercontent.com/liviuschera/noctis/master/themes/noctis.json"
            },
            {
                "name": "noctis_lux",
                "url": "https://raw.githubusercontent.com/liviuschera/noctis/master/themes/noctisLux.json"
            },
            {
                "name": "noctis_minimus",
                "url": "https://raw.githubusercontent.com/liviuschera/noctis/master/themes/noctisMinimus.json"
            },
            {
                "name": "forest_night",
                "url": "https://raw.githubusercontent.com/sainnhe/forest-night-vscode/master/themes/forest-night.json"
            },
            {
                "name": "edge_dark",
                "url": "https://raw.githubusercontent.com/sainnhe/edge-vscode/master/themes/edge-dark.json"
            },
            {
                "name": "edge_light", 
                "url": "https://raw.githubusercontent.com/sainnhe/edge-vscode/master/themes/edge-light.json"
            },
            {
                "name": "panda_syntax",
                "url": "https://raw.githubusercontent.com/tinkertrain/panda-syntax-vscode/master/themes/panda-syntax.json"
            }
        ]
    
    def download_theme(self, theme_info):
        """Download a single theme file"""
        name = theme_info["name"]
        url = theme_info["url"]
        
        try:
            print(f"Downloading: {name}...")
            
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
            
            # Validate and clean JSON
            try:
                theme_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to clean up common issues
                content = self.clean_json(content)
                theme_data = json.loads(content)
            
            # Save theme
            output_path = self.themes_dir / f"{name}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved: {name}.json")
            self.downloaded_count += 1
            return True
            
        except Exception as e:
            print(f"✗ Failed to download {name}: {e}")
            self.failed_count += 1
            return False
    
    def clean_json(self, content):
        """Clean JSON content to fix common issues"""
        import re
        
        # Remove trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Remove single-line comments
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove comments that aren't inside strings
            if '//' in line and not line.strip().startswith('"'):
                comment_pos = line.find('//')
                # Make sure it's not inside a string
                quote_count = line[:comment_pos].count('"') - line[:comment_pos].count('\\"')
                if quote_count % 2 == 0:  # Even number of quotes = not inside string
                    line = line[:comment_pos].rstrip()
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def download_all(self):
        """Download all themes"""
        print(f"Starting simple theme download...")
        print(f"Output directory: {self.themes_dir.absolute()}")
        print("-" * 50)
        
        for theme_info in self.direct_themes:
            self.download_theme(theme_info)
            time.sleep(0.5)  # Be respectful to servers
        
        print("\n" + "=" * 50)
        print(f"Download complete!")
        print(f"Successfully downloaded: {self.downloaded_count} themes")
        print(f"Failed downloads: {self.failed_count} themes")
        print(f"Themes saved to: {self.themes_dir.absolute()}")
    
    def list_existing_themes(self):
        """List themes already in the directory"""
        existing = list(self.themes_dir.glob("*.json"))
        print(f"Existing themes ({len(existing)}):")
        for theme in sorted(existing):
            print(f"  - {theme.name}")
        return existing

def main():
    print("Simple VS Code Theme Downloader")
    print("=" * 50)
    
    downloader = SimpleThemeDownloader()
    
    # Show existing themes
    existing = downloader.list_existing_themes()
    print()
    
    # Download themes
    downloader.download_all()
    
    # Show final count
    print(f"\nFinal theme count: {len(list(downloader.themes_dir.glob('*.json')))}")

if __name__ == "__main__":
    main() 