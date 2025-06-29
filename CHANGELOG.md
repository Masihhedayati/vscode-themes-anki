# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-01-01

### Added
- **29 Professional Themes**: Comprehensive theme collection including Catppuccin, Atom One, Edge, Night Owl, Tokyo Night, and more
- **Reviewer-Safe CSS System**: Context-aware CSS injection that themes interface without affecting card content
- **Advanced Debugging Tools**: Built-in "Debug Reviewer" button and comprehensive logging system
- **Robust Error Handling**: Graceful fallbacks and detailed error reporting throughout the addon
- **Theme Validation System**: Automatic theme validation with fallback creation for reliability

### Fixed
- **Critical AttributeError**: Fixed 'ThemeDialog' object has no attribute 'theme_manger' typo
- **Hook System Crashes**: Resolved non-existent hook references causing startup failures
- **CSS Injection Failures**: Fixed syntax errors and string literal issues in CSS generation
- **Theme Persistence**: Corrected configuration save/load mechanism for reliable theme persistence
- **Performance Issues**: Eliminated redundant timers and heavy refresh operations
- **Memory Leaks**: Added proper CSS caching and reduced unnecessary object creation

### Changed
- **Smart Context Detection**: CSS injection now intelligently handles different Anki contexts (deck browser, reviewer, editor)
- **Enhanced Theme Manager**: Complete rewrite with better error handling, caching, and validation
- **Improved UI Responsiveness**: Faster theme switching and reduced application lag
- **Better CSS Specificity**: Higher-priority selectors ensure theme overrides work consistently

### Technical Improvements
- **Lenient Theme Loading**: Themes with missing fields now load successfully with sensible defaults
- **CSS Caching System**: Significant performance improvement through intelligent CSS caching
- **Maximum Compatibility**: Support for various VS Code theme formats and structures
- **Comprehensive Logging**: Detailed debug output for troubleshooting and development
- **Modular Architecture**: Cleaner separation of concerns between UI, theming, and configuration

### Developer Experience
- **Debug Interface**: New debugging tools accessible through the theme dialog
- **Better Error Messages**: Clear, actionable error messages for troubleshooting
- **Extensive Logging**: Detailed console output for development and debugging
- **Code Quality**: Improved error handling, validation, and robustness throughout

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