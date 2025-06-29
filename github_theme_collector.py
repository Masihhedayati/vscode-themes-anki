#!/usr/bin/env python3
"""
GitHub Theme Collector for VS Code Themes (Updated with correct paths)
Downloads themes from verified GitHub repositories containing VS Code theme JSON files
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path
import time
import sys

class GitHubThemeCollector:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Updated theme sources with correct repository paths
        self.theme_sources = [
            {
                "name": "Catppuccin",
                "repo": "catppuccin/vscode",
                "path": "packages/catppuccin-vsc/themes",
                "files": [
                    "latte.json",
                    "frappe.json", 
                    "macchiato.json",
                    "mocha.json"
                ]
            },
            {
                "name": "Dracula Community",
                "repo": "kevinvn1709/vscode-dracula-color-theme",
                "path": "themes",
                "files": [
                    "dracula-color-theme.json"
                ]
            },
            {
                "name": "Dracula Redefined",
                "repo": "lakshits11/dracula-redefined",
                "path": "themes",
                "files": [
                    "Dracula-Redefined-color-theme.json"
                ]
            },
            {
                "name": "Winter is Coming",
                "repo": "johnpapa/vscode-winteriscoming",
                "path": "themes",
                "files": [
                    "WinterIsComing-dark-blue-color-theme.json",
                    "WinterIsComing-dark-black-color-theme.json",
                    "WinterIsComing-light-color-theme.json"
                ]
            },
            {
                "name": "Night Owl",
                "repo": "sdras/night-owl-vscode-theme",
                "path": "themes",
                "files": [
                    "Night%20Owl-color-theme.json",
                    "Night%20Owl%20Light-color-theme.json",
                    "Night%20Owl%20(No%20Italics)-color-theme.json"
                ]
            },
            {
                "name": "Material Theme Community",
                "repo": "whizkydee/vscode-material-palenight-theme",
                "path": "themes",
                "files": [
                    "Material-Palenight-color-theme.json"
                ]
            },
            {
                "name": "Tokyo Night",
                "repo": "enkia/tokyo-night-vscode-theme",
                "path": "themes",
                "files": [
                    "tokyo-night-color-theme.json",
                    "tokyo-night-storm-color-theme.json",
                    "tokyo-night-light-color-theme.json"
                ]
            },
            {
                "name": "Ayu",
                "repo": "ayu-theme/vscode-ayu",
                "path": "themes",
                "files": [
                    "ayu-dark.json",
                    "ayu-light.json",
                    "ayu-mirage.json"
                ]
            },
            {
                "name": "Gruvbox",
                "repo": "morhetz/gruvbox",
                "path": "contrib/vscode",
                "files": [
                    "gruvbox-dark-hard.json",
                    "gruvbox-dark-medium.json",
                    "gruvbox-dark-soft.json",
                    "gruvbox-light-hard.json",
                    "gruvbox-light-medium.json",
                    "gruvbox-light-soft.json"
                ]
            },
            {
                "name": "One Dark Pro",
                "repo": "Binaryify/OneDark-Pro",
                "path": "themes",
                "files": [
                    "OneDark-Pro.json",
                    "OneDark-Pro-darker.json",
                    "OneDark-Pro-flat.json"
                ]
            },
            {
                "name": "Synthwave 84",
                "repo": "robb0wen/synthwave-vscode",
                "path": "themes",
                "files": ["synthwave-color-theme.json"]
            },
            {
                "name": "Shades of Purple",
                "repo": "ahmadawais/shades-of-purple-vscode",
                "path": "themes",
                "files": ["shades-of-purple-color-theme.json"]
            },
            {
                "name": "Cobalt2",
                "repo": "wesbos/cobalt2-vscode",
                "path": "theme",
                "files": ["cobalt2.json"]
            },
            {
                "name": "Nord",
                "repo": "arcticicestudio/nord-visual-studio-code",
                "path": "themes",
                "files": ["nord-color-theme.json"]
            },
            {
                "name": "Monokai Pro",
                "repo": "monokai/monokai-pro-vscode",
                "path": "themes",
                "files": [
                    "monokai-pro-color-theme.json",
                    "monokai-pro-machine-color-theme.json",
                    "monokai-pro-octagon-color-theme.json",
                    "monokai-pro-ristretto-color-theme.json",
                    "monokai-pro-spectrum-color-theme.json"
                ]
            }
        ]
    
    def download_theme(self, repo, file_path, local_name):
        """Download a single theme file from GitHub"""
        url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
        
        try:
            print(f"Downloading: {local_name}...")
            
            # Try main branch first, then master if 404
            try:
                with urllib.request.urlopen(url) as response:
                    content = response.read().decode('utf-8')
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    # Try master branch
                    url = f"https://raw.githubusercontent.com/{repo}/master/{file_path}"
                    with urllib.request.urlopen(url) as response:
                        content = response.read().decode('utf-8')
                else:
                    raise
            
            # Validate JSON and handle common issues
            try:
                theme_data = json.loads(content)
            except json.JSONDecodeError as je:
                # Try to fix common JSON issues
                if "Illegal trailing comma" in str(je):
                    # Remove trailing commas and retry
                    import re
                    content = re.sub(r',(\s*[}\]])', r'\1', content)
                    theme_data = json.loads(content)
                else:
                    # Remove comments if present
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        # Remove single-line comments
                        if '//' in line and not line.strip().startswith('"'):
                            line = line.split('//')[0]
                        cleaned_lines.append(line)
                    content = '\n'.join(cleaned_lines)
                    theme_data = json.loads(content)
            
            # Save to themes directory
            output_path = self.themes_dir / local_name
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved: {local_name}")
            self.downloaded_count += 1
            return True
            
        except Exception as e:
            print(f"✗ Failed to download {local_name}: {e}")
            self.failed_count += 1
            return False
    
    def collect_themes(self):
        """Download all themes from GitHub repositories"""
        print(f"Starting GitHub theme collection...")
        print(f"Output directory: {self.themes_dir.absolute()}")
        print("-" * 50)
        
        for source in self.theme_sources:
            print(f"\nProcessing: {source['name']}")
            
            for theme_file in source['files']:
                file_path = f"{source['path']}/{theme_file}"
                # Create clean filename
                clean_name = theme_file.replace(' ', '_').replace('(', '').replace(')', '').replace('-color-theme', '').replace('%20', '_').replace('%28', '').replace('%29', '')
                local_name = f"{source['name'].lower().replace(' ', '_')}_{clean_name}"
                
                self.download_theme(source['repo'], file_path, local_name)
                
                # Small delay to be respectful to GitHub
                time.sleep(0.5)
            
            time.sleep(1)  # Longer delay between repositories
        
        print("\n" + "=" * 50)
        print(f"Collection complete!")
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
    print("VS Code Theme Collector - GitHub Edition (Updated)")
    print("=" * 50)
    
    collector = GitHubThemeCollector()
    
    # Show existing themes
    existing = collector.list_existing_themes()
    print()
    
    # Collect new themes
    collector.collect_themes()
    
    # Show final count
    print(f"\nFinal theme count: {len(list(collector.themes_dir.glob('*.json')))}")

if __name__ == "__main__":
    main() 