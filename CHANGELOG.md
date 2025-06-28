# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-19

### Added
- Mac-native custom title bar with system-style buttons
- Fast restart button (⟳) in title bar - restarts Anki without syncing
- Qt layout manager integration for persistent layout fixes
- Comprehensive deck browser alignment improvements

### Fixed
- **Deck List Gap**: Eliminated unwanted spacing between deck title and first deck
- **Statistics Alignment**: Perfect number alignment in deck browser statistics
- **Button Panel**: Consistent button styling and alignment
- **Layout Persistence**: Fixes now persist across Anki restarts

### Changed
- Enhanced CSS injection system for better compatibility
- Improved theme application logic
- Better error handling and debugging

### Technical Improvements
- Direct Qt layout manipulation
- Aggressive CSS targeting for deck browser
- Platform-specific optimizations for macOS
- Enhanced hook system integration

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Support for 7+ VS Code themes (One Dark Pro, Dracula, GitHub Dark, etc.)
- Theme switching interface
- Custom CSS support
- Theme import functionality
- Card and UI theming options 