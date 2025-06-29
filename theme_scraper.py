#!/usr/bin/env python3
"""
VSCode Themes Scraper
Scrapes themes from vscodethemes.com and downloads them to the themes directory
"""

import os
import re
import json
import time
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VSCodeThemeScraper:
    def __init__(self, base_url="https://vscodethemes.com", themes_dir="themes"):
        self.base_url = base_url
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Track downloaded themes to avoid duplicates
        self.downloaded_themes = set()
        self.theme_metadata = []
        
    def get_page_themes(self, page_num):
        """Extract all theme URLs from a specific page"""
        url = f"{self.base_url}/?page={page_num}"
        logger.info(f"Scraping page {page_num}: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            content = response.text
            
            # Extract individual theme URLs using regex
            # Pattern looks for theme URLs like /e/publisher.extension/theme-name
            theme_pattern = r'/e/([^/]+\.[^/]+)/([^"\'>\s]+)'
            matches = re.findall(theme_pattern, content)
            
            themes = []
            for publisher_extension, theme_name in matches:
                theme_url = f"/e/{publisher_extension}/{theme_name}"
                if theme_url not in self.downloaded_themes:
                    themes.append({
                        'url': theme_url,
                        'publisher_extension': publisher_extension,
                        'theme_name': theme_name,
                        'full_url': urljoin(self.base_url, theme_url)
                    })
                    self.downloaded_themes.add(theme_url)
            
            logger.info(f"Found {len(themes)} unique themes on page {page_num}")
            return themes
            
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return []
    
    def get_theme_json_url(self, theme_info):
        """Get the actual JSON download URL for a theme"""
        try:
            theme_page_url = theme_info['full_url']
            logger.info(f"Getting JSON URL for: {theme_info['theme_name']}")
            
            response = self.session.get(theme_page_url)
            response.raise_for_status()
            content = response.text
            
            # Look for JSON download links
            json_patterns = [
                r'"(https://[^"]*\.json[^"]*)"',
                r"'(https://[^']*\.json[^']*)'",
                r'href="([^"]*\.json[^"]*)"',
                r"href='([^']*\.json[^']*)'",
                r'(https://raw\.githubusercontent\.com/[^"\'>\s]+\.json)',
                r'(https://[^"\'>\s]*themes?[^"\'>\s]*\.json)',
            ]
            
            json_urls = []
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                json_urls.extend(matches)
            
            # Also look for GitHub repository links to extract themes
            github_patterns = [
                r'(https://github\.com/[^"\'>\s]+)',
                r'"(https://[^"]*github[^"]*)"'
            ]
            
            github_urls = []
            for pattern in github_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                github_urls.extend(matches)
            
            # Try to get themes from GitHub repos
            for github_url in github_urls[:3]:  # Limit to first 3 to avoid too many requests
                try:
                    repo_themes = self.extract_themes_from_github(github_url)
                    json_urls.extend(repo_themes)
                except Exception as e:
                    logger.debug(f"Error extracting from GitHub {github_url}: {e}")
            
            # Remove duplicates and invalid URLs
            valid_json_urls = []
            seen = set()
            for url in json_urls:
                if url and url not in seen and url.endswith('.json'):
                    valid_json_urls.append(url)
                    seen.add(url)
            
            logger.info(f"Found {len(valid_json_urls)} JSON URLs for {theme_info['theme_name']}")
            return valid_json_urls
            
        except Exception as e:
            logger.error(f"Error getting JSON URL for {theme_info['theme_name']}: {e}")
            return []
    
    def extract_themes_from_github(self, github_url):
        """Extract theme JSON files from a GitHub repository"""
        try:
            # Convert GitHub URL to raw content URL
            if 'github.com' in github_url and '/blob/' not in github_url:
                # Try to find themes directory
                api_url = github_url.replace('github.com', 'api.github.com/repos') + '/contents'
                response = self.session.get(api_url)
                if response.status_code == 200:
                    contents = response.json()
                    theme_files = []
                    
                    for item in contents:
                        if item['type'] == 'dir' and 'theme' in item['name'].lower():
                            # Get themes from themes directory
                            themes_api_url = item['url']
                            themes_response = self.session.get(themes_api_url)
                            if themes_response.status_code == 200:
                                theme_contents = themes_response.json()
                                for theme_file in theme_contents:
                                    if theme_file['name'].endswith('.json'):
                                        theme_files.append(theme_file['download_url'])
                        elif item['name'].endswith('.json') and 'theme' in item['name'].lower():
                            theme_files.append(item['download_url'])
                    
                    return theme_files
        except Exception as e:
            logger.debug(f"Error extracting from GitHub {github_url}: {e}")
        
        return []
    
    def download_theme_json(self, json_url, theme_info):
        """Download and save a theme JSON file"""
        try:
            logger.info(f"Downloading: {json_url}")
            response = self.session.get(json_url, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON to validate
            theme_data = response.json()
            
            # Generate filename
            filename = self.generate_filename(json_url, theme_info, theme_data)
            filepath = self.themes_dir / filename
            
            # Avoid overwriting existing files
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                name_part = original_filepath.stem
                extension = original_filepath.suffix
                filepath = self.themes_dir / f"{name_part}_{counter}{extension}"
                counter += 1
            
            # Save the theme
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            # Track metadata
            metadata = {
                'filename': filepath.name,
                'source_url': json_url,
                'theme_page': theme_info['full_url'],
                'publisher_extension': theme_info['publisher_extension'],
                'theme_name': theme_info['theme_name'],
                'display_name': theme_data.get('displayName', theme_info['theme_name']),
                'description': theme_data.get('description', ''),
                'type': theme_data.get('type', 'unknown')
            }
            self.theme_metadata.append(metadata)
            
            logger.info(f"Successfully saved: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading {json_url}: {e}")
            return False
    
    def generate_filename(self, json_url, theme_info, theme_data):
        """Generate a clean filename for the theme"""
        # Try different sources for the name
        name_candidates = [
            theme_data.get('displayName', ''),
            theme_data.get('name', ''),
            theme_info['theme_name'],
            Path(urlparse(json_url).path).stem
        ]
        
        # Find the first non-empty name
        name = None
        for candidate in name_candidates:
            if candidate and candidate.strip():
                name = candidate.strip()
                break
        
        if not name:
            name = "unknown_theme"
        
        # Clean the filename
        name = re.sub(r'[^\w\-_\.]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        # Ensure .json extension
        if not name.endswith('.json'):
            name += '.json'
        
        return name
    
    def scrape_all_themes(self, max_pages=7):
        """Main method to scrape all themes from all pages"""
        logger.info(f"Starting to scrape {max_pages} pages from {self.base_url}")
        
        all_themes = []
        
        # Scrape all pages
        for page_num in range(1, max_pages + 1):
            page_themes = self.get_page_themes(page_num)
            all_themes.extend(page_themes)
            time.sleep(1)  # Be respectful to the server
        
        logger.info(f"Found {len(all_themes)} total unique themes")
        
        # Download each theme
        successful_downloads = 0
        total_attempts = 0
        
        for i, theme_info in enumerate(all_themes, 1):
            logger.info(f"Processing theme {i}/{len(all_themes)}: {theme_info['theme_name']}")
            
            json_urls = self.get_theme_json_url(theme_info)
            
            for json_url in json_urls:
                total_attempts += 1
                if self.download_theme_json(json_url, theme_info):
                    successful_downloads += 1
                
                time.sleep(0.5)  # Small delay between downloads
            
            # Larger delay between themes
            if i % 10 == 0:
                logger.info(f"Processed {i} themes, taking a longer break...")
                time.sleep(3)
            else:
                time.sleep(1)
        
        # Save metadata
        self.save_metadata()
        
        logger.info(f"Scraping completed!")
        logger.info(f"Successfully downloaded: {successful_downloads}/{total_attempts} theme files")
        logger.info(f"Total unique themes processed: {len(all_themes)}")
        logger.info(f"Files saved to: {self.themes_dir}")
        
        return successful_downloads, total_attempts
    
    def save_metadata(self):
        """Save metadata about all downloaded themes"""
        metadata_file = self.themes_dir / 'themes_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.theme_metadata, f, indent=2)
        logger.info(f"Metadata saved to: {metadata_file}")

def main():
    scraper = VSCodeThemeScraper()
    scraper.scrape_all_themes(max_pages=7)

if __name__ == "__main__":
    main() 