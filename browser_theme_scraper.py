#!/usr/bin/env python3
"""
Browser-based VSCode Themes Scraper
Uses browser automation to extract themes from vscodethemes.com
"""

import json
import re
import time
import requests
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserThemeScraper:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.downloaded_themes = set()
        self.theme_metadata = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def extract_themes_from_page_snapshot(self, snapshot_text):
        """Extract theme information from browser snapshot"""
        themes = []
        
        # Parse the snapshot text to find theme links
        lines = snapshot_text.split('\n')
        current_theme_package = None
        current_publisher = None
        
        for line in lines:
            line = line.strip()
            
            # Look for theme package headers
            if 'heading' in line and 'level=2' in line:
                # Extract theme package name
                match = re.search(r'"([^"]*)".*\[level=2\]', line)
                if match:
                    current_theme_package = match.group(1)
            
            # Look for publisher info
            elif 'heading' in line and 'level=3' in line and 'by ' in line:
                match = re.search(r'"by ([^"]*)"', line)
                if match:
                    current_publisher = match.group(1)
            
            # Look for individual theme links
            elif 'link' in line and '/e/' in line:
                # Extract URL and theme name
                url_match = re.search(r'/url: (/e/[^/]+/[^\s]+)', line)
                name_match = re.search(r'link "([^"]*)"', line)
                
                if url_match and name_match:
                    theme_url = url_match.group(1)
                    theme_name = name_match.group(1)
                    
                    if theme_url not in self.downloaded_themes:
                        themes.append({
                            'url': theme_url,
                            'theme_name': theme_name,
                            'package_name': current_theme_package,
                            'publisher': current_publisher,
                            'full_url': f"https://vscodethemes.com{theme_url}"
                        })
                        self.downloaded_themes.add(theme_url)
        
        return themes
    
    def get_vscode_marketplace_url(self, theme_info):
        """Try to construct VS Code marketplace URL from theme info"""
        try:
            # Extract publisher and extension from URL pattern
            url_parts = theme_info['url'].split('/')
            if len(url_parts) >= 3:
                publisher_extension = url_parts[2]
                theme_variant = url_parts[3] if len(url_parts) > 3 else ""
                
                # Split publisher.extension
                if '.' in publisher_extension:
                    publisher, extension = publisher_extension.split('.', 1)
                    
                    # Construct marketplace download URL
                    marketplace_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension}/latest/vspackage"
                    return marketplace_url
        except Exception as e:
            logger.debug(f"Error constructing marketplace URL: {e}")
        
        return None
    
    def extract_theme_from_vsix(self, vsix_url, theme_info):
        """Download and extract theme JSON from VSIX package"""
        try:
            import zipfile
            import tempfile
            
            logger.info(f"Downloading VSIX: {vsix_url}")
            response = self.session.get(vsix_url, timeout=60)
            response.raise_for_status()
            
            # Save VSIX to temporary file
            with tempfile.NamedTemporaryFile(suffix='.vsix', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_vsix_path = temp_file.name
            
            try:
                # Extract VSIX (it's a ZIP file)
                with zipfile.ZipFile(temp_vsix_path, 'r') as zip_ref:
                    # Look for theme JSON files
                    theme_files = []
                    for file_path in zip_ref.namelist():
                        if file_path.endswith('.json') and ('theme' in file_path.lower() or 'color' in file_path.lower()):
                            theme_files.append(file_path)
                    
                    # Extract and save theme files
                    saved_count = 0
                    for theme_file_path in theme_files:
                        try:
                            theme_content = zip_ref.read(theme_file_path)
                            theme_data = json.loads(theme_content)
                            
                            # Generate filename
                            filename = self.generate_filename_from_vsix(theme_file_path, theme_data, theme_info)
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
                                'source_vsix': vsix_url,
                                'theme_page': theme_info['full_url'],
                                'package_name': theme_info.get('package_name', ''),
                                'publisher': theme_info.get('publisher', ''),
                                'display_name': theme_data.get('displayName', theme_info['theme_name']),
                                'description': theme_data.get('description', ''),
                                'type': theme_data.get('type', 'unknown')
                            }
                            self.theme_metadata.append(metadata)
                            
                            logger.info(f"Extracted theme: {filepath.name}")
                            saved_count += 1
                            
                        except Exception as e:
                            logger.debug(f"Error extracting {theme_file_path}: {e}")
                    
                    return saved_count > 0
                    
            finally:
                # Clean up temp file
                Path(temp_vsix_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Error extracting VSIX {vsix_url}: {e}")
            return False
    
    def generate_filename_from_vsix(self, file_path, theme_data, theme_info):
        """Generate filename from VSIX extraction"""
        # Try different name sources
        name_candidates = [
            theme_data.get('displayName', ''),
            theme_data.get('name', ''),
            Path(file_path).stem,
            theme_info['theme_name']
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
        
        if not name.endswith('.json'):
            name += '.json'
        
        return name
    
    def download_github_theme(self, github_url, theme_info):
        """Download theme directly from GitHub"""
        try:
            # Convert to raw GitHub URL if needed
            if 'github.com' in github_url and '/blob/' in github_url:
                raw_url = github_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
            else:
                raw_url = github_url
            
            logger.info(f"Downloading from GitHub: {raw_url}")
            response = self.session.get(raw_url, timeout=30)
            response.raise_for_status()
            
            theme_data = response.json()
            
            # Generate filename
            filename = self.generate_filename_from_vsix(github_url, theme_data, theme_info)
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
                'source_github': raw_url,
                'theme_page': theme_info['full_url'],
                'package_name': theme_info.get('package_name', ''),
                'publisher': theme_info.get('publisher', ''),
                'display_name': theme_data.get('displayName', theme_info['theme_name']),
                'description': theme_data.get('description', ''),
                'type': theme_data.get('type', 'unknown')
            }
            self.theme_metadata.append(metadata)
            
            logger.info(f"Downloaded GitHub theme: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading GitHub theme {github_url}: {e}")
            return False
    
    def save_metadata(self):
        """Save metadata about all downloaded themes"""
        metadata_file = self.themes_dir / 'themes_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.theme_metadata, f, indent=2)
        logger.info(f"Metadata saved to: {metadata_file}")

# Global scraper instance for use with browser automation
browser_scraper = BrowserThemeScraper()

def process_page_themes(snapshot_text, page_num):
    """Process themes from a page snapshot"""
    logger.info(f"Processing themes from page {page_num}")
    
    themes = browser_scraper.extract_themes_from_page_snapshot(snapshot_text)
    logger.info(f"Found {len(themes)} themes on page {page_num}")
    
    successful_downloads = 0
    
    for i, theme_info in enumerate(themes, 1):
        logger.info(f"Processing theme {i}/{len(themes)}: {theme_info['theme_name']}")
        
        # Try multiple download strategies
        downloaded = False
        
        # Strategy 1: Try VS Code Marketplace
        marketplace_url = browser_scraper.get_vscode_marketplace_url(theme_info)
        if marketplace_url and not downloaded:
            try:
                if browser_scraper.extract_theme_from_vsix(marketplace_url, theme_info):
                    downloaded = True
                    successful_downloads += 1
            except Exception as e:
                logger.debug(f"Marketplace download failed: {e}")
        
        # Strategy 2: Try GitHub
        if not downloaded:
            try:
                if browser_scraper.download_github_theme(theme_info['full_url'], theme_info):
                    downloaded = True
                    successful_downloads += 1
            except Exception as e:
                logger.debug(f"GitHub download failed: {e}")
        
        # Add small delay between downloads
        time.sleep(0.5)
    
    logger.info(f"Page {page_num} completed: {successful_downloads}/{len(themes)} themes downloaded")
    return successful_downloads, len(themes)

def finalize_scraping():
    """Finalize the scraping process"""
    browser_scraper.save_metadata()
    total_themes = len(browser_scraper.theme_metadata)
    logger.info(f"Scraping completed! Total themes downloaded: {total_themes}")
    logger.info(f"Themes saved to: {browser_scraper.themes_dir}")
    return total_themes 