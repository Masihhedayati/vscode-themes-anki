#!/usr/bin/env python3
"""
Comprehensive VSCode Theme Downloader
Downloads themes from VS Code marketplace using minimal dependencies
"""

import json
import re
import urllib.request
import urllib.parse
import urllib.error
import zipfile
import tempfile
import os
from pathlib import Path
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VSCodeThemeDownloader:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.downloaded_themes = set()
        self.theme_metadata = []
        
    def get_marketplace_extension_url(self, publisher, extension_name):
        """Get the VS Code marketplace download URL for an extension"""
        return f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension_name}/latest/vspackage"
    
    def download_and_extract_vsix(self, vsix_url, extension_info):
        """Download VSIX and extract theme files"""
        try:
            logger.info(f"Downloading: {extension_info['name']} by {extension_info['publisher']}")
            
            # Download VSIX
            req = urllib.request.Request(vsix_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=60) as response:
                vsix_data = response.read()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.vsix', delete=False) as temp_file:
                temp_file.write(vsix_data)
                temp_vsix_path = temp_file.name
            
            try:
                # Extract VSIX (it's a ZIP)
                with zipfile.ZipFile(temp_vsix_path, 'r') as zip_ref:
                    extracted_count = 0
                    
                    # Look for theme files
                    for file_path in zip_ref.namelist():
                        if (file_path.endswith('.json') and 
                            ('theme' in file_path.lower() or 
                             'color' in file_path.lower() or
                             file_path.endswith('-color-theme.json'))):
                            
                            try:
                                # Read theme content
                                theme_content = zip_ref.read(file_path)
                                theme_data = json.loads(theme_content.decode('utf-8'))
                                
                                # Generate filename
                                filename = self.generate_filename(file_path, theme_data, extension_info)
                                filepath = self.themes_dir / filename
                                
                                # Avoid duplicates
                                counter = 1
                                original_filepath = filepath
                                while filepath.exists():
                                    name_part = original_filepath.stem
                                    extension = original_filepath.suffix
                                    filepath = self.themes_dir / f"{name_part}_{counter}{extension}"
                                    counter += 1
                                
                                # Save theme
                                with open(filepath, 'w', encoding='utf-8') as f:
                                    json.dump(theme_data, f, indent=2)
                                
                                # Track metadata
                                metadata = {
                                    'filename': filepath.name,
                                    'source_extension': f"{extension_info['publisher']}.{extension_info['name']}",
                                    'extension_name': extension_info['name'],
                                    'publisher': extension_info['publisher'],
                                    'display_name': theme_data.get('displayName', theme_data.get('name', filepath.stem)),
                                    'description': theme_data.get('description', ''),
                                    'type': theme_data.get('type', 'unknown'),
                                    'original_path': file_path
                                }
                                self.theme_metadata.append(metadata)
                                
                                logger.info(f"✓ Extracted: {filepath.name}")
                                extracted_count += 1
                                
                            except Exception as e:
                                logger.debug(f"Error processing {file_path}: {e}")
                    
                    if extracted_count > 0:
                        logger.info(f"Successfully extracted {extracted_count} themes from {extension_info['name']}")
                        return True
                    else:
                        logger.warning(f"No themes found in {extension_info['name']}")
                        return False
                        
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_vsix_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error downloading {extension_info['name']}: {e}")
            return False
    
    def generate_filename(self, file_path, theme_data, extension_info):
        """Generate a clean filename"""
        # Try different name sources
        name_candidates = [
            theme_data.get('displayName', ''),
            theme_data.get('name', ''),
            Path(file_path).stem,
            extension_info['name']
        ]
        
        name = None
        for candidate in name_candidates:
            if candidate and candidate.strip():
                name = candidate.strip()
                break
        
        if not name:
            name = "unknown_theme"
        
        # Clean filename
        name = re.sub(r'[^\w\-_\.]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        # Add publisher prefix if not already there
        if not name.startswith(extension_info['publisher']):
            name = f"{extension_info['publisher']}_{name}"
        
        if not name.endswith('.json'):
            name += '.json'
        
        return name
    
    def download_popular_themes(self):
        """Download popular VS Code themes"""
        
        # Popular theme extensions from vscodethemes.com
        popular_extensions = [
            {'publisher': 'ms-vscode', 'name': 'cpptools-themes'},
            {'publisher': 'GitHub', 'name': 'github-vscode-theme'},
            {'publisher': 'ms-vscode', 'name': 'PowerShell'},
            {'publisher': 'Equinusocio', 'name': 'vsc-material-theme'},
            {'publisher': 'teabyii', 'name': 'ayu'},
            {'publisher': 'monokai', 'name': 'theme-monokai-pro-vscode'},
            {'publisher': 'johnpapa', 'name': 'winteriscoming'},
            {'publisher': 'sdras', 'name': 'night-owl'},
            {'publisher': 'enkia', 'name': 'tokyo-night'},
            {'publisher': 'akamud', 'name': 'vscode-theme-onelight'},
            {'publisher': 'liviuschera', 'name': 'noctis'},
            {'publisher': 'BeardedBear', 'name': 'beardedtheme'},
            {'publisher': 'jdinhlife', 'name': 'gruvbox'},
            {'publisher': 'fisheva', 'name': 'eva-theme'},
            {'publisher': 'Catppuccin', 'name': 'catppuccin-vsc'},
            {'publisher': 'Shopify', 'name': 'ruby-extensions-pack'},
            {'publisher': 'daylerees', 'name': 'rainglow'},
            {'publisher': 'unthrottled', 'name': 'doki-theme'},
            {'publisher': 'felipe-mendes', 'name': 'slack-theme'},
            {'publisher': 'miguelsolorio', 'name': 'min-theme'},
            {'publisher': 'thenikso', 'name': 'github-plus-theme'},
            {'publisher': 'uloco', 'name': 'theme-bluloco-light'},
            {'publisher': 'davidbwaters', 'name': 'macos-modern-theme'},
            {'publisher': 'Hyzeta', 'name': 'vscode-theme-github-light'},
            {'publisher': 'sainnhe', 'name': 'gruvbox-material'},
            {'publisher': 'dunstontc', 'name': 'dark-plus-syntax'},
            {'publisher': 'lkytal', 'name': 'FlatUI'},
            {'publisher': 'Youssef', 'name': 'viow'},
            {'publisher': 'mvllow', 'name': 'rose-pine'},
            {'publisher': 'crazyurus', 'name': 'miniprogram-vscode-extension'},
            {'publisher': 'elanzalaco', 'name': 'grey-light-plus-pro'},
            {'publisher': 'Heron', 'name': 'firefox-devtools-theme'},
            {'publisher': 'ryanolsonx', 'name': 'solarized'},
            {'publisher': 'webfreak', 'name': 'cute-theme'},
            {'publisher': 'obrejla', 'name': 'netbeans-light-theme'},
            {'publisher': 'karyfoundation', 'name': 'theme-karyfoundation-themes'},
            {'publisher': 'zhuangtongfa', 'name': 'Material-theme'},
            {'publisher': 'PKief', 'name': 'material-icon-theme'},
            {'publisher': 'Dracula', 'name': 'theme-dracula'},
            {'publisher': 'wesbos', 'name': 'theme-cobalt2'},
            {'publisher': 'ahmadawais', 'name': 'shades-of-purple'},
            {'publisher': 'RobbOwen', 'name': 'synthwave-vscode'},
            {'publisher': 'whizkydee', 'name': 'material-palenight-theme'},
            {'publisher': 'Equinusocio', 'name': 'vsc-community-material-theme'},
            {'publisher': 'jolaleye', 'name': 'horizon-theme-vscode'},
            {'publisher': 'antfu', 'name': 'theme-vitesse'},
            {'publisher': 'bradlc', 'name': 'vscode-tailwindcss'},
            {'publisher': 'arcticicestudio', 'name': 'nord-visual-studio-code'},
            {'publisher': 'bung87', 'name': 'vscode-gemini'},
            {'publisher': 'tal7aouy', 'name': 'theme'},
            {'publisher': 'hoovercj', 'name': 'vscode-power-mode'},
        ]
        
        successful = 0
        total = len(popular_extensions)
        
        for i, ext_info in enumerate(popular_extensions, 1):
            logger.info(f"Processing {i}/{total}: {ext_info['publisher']}.{ext_info['name']}")
            
            marketplace_url = self.get_marketplace_extension_url(ext_info['publisher'], ext_info['name'])
            
            if self.download_and_extract_vsix(marketplace_url, ext_info):
                successful += 1
            
            # Small delay to be respectful
            import time
            time.sleep(0.5)
        
        self.save_metadata()
        
        logger.info(f"✅ Download completed!")
        logger.info(f"Successfully processed: {successful}/{total} extensions")
        logger.info(f"Total themes downloaded: {len(self.theme_metadata)}")
        logger.info(f"Themes saved to: {self.themes_dir}")
        
        return successful, len(self.theme_metadata)
    
    def save_metadata(self):
        """Save metadata about downloaded themes"""
        metadata_file = self.themes_dir / 'themes_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.theme_metadata, f, indent=2)
        logger.info(f"📝 Metadata saved to: {metadata_file}")

def main():
    downloader = VSCodeThemeDownloader()
    downloader.download_popular_themes()

if __name__ == "__main__":
    main() 