# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-02

### Fixed
- **🎯 CRITICAL: Card Content Theming Issue RESOLVED**: Fixed overly aggressive CSS protection that was preventing card backgrounds from being themed
  - **Root Cause**: CSS protection was excluding entire `#qa`, `#middle`, and `.card` containers from theming
  - **Solution**: Refined CSS protection to only preserve actual text content while allowing container theming
  - Card backgrounds now properly use VS Code theme colors (e.g., dark background for dark themes)
  - Medical content and study materials now display on properly themed backgrounds

- **📐 Bottom Bar Spacing Improved**: Increased bottom button bar padding from cramped 8px to spacious 16px vertical, 20px horizontal
  - Better visual breathing room for review buttons (Again, Hard, Good, Easy)
  - Improved button margins (4px 8px) and padding (8px 16px) for better click targets
  - Enhanced overall review experience with less cramped interface

- **⚔️ Addon Conflict Management System**: Comprehensive solution for addon conflicts affecting theme consistency
  - **Automatic Detection**: Identifies conflicting addons by AnkiWeb ID including "The KING of Button Add-ons" (374005964)
  - **Smart Resolution**: User-controlled disabling of conflicting addons with consent dialogs
  - **Nuclear CSS System**: Ultra-high specificity CSS (1,0,0,12+) for override wars
  - **Multi-Method Injection**: CSS applied via webview, Qt stylesheets, DOM manipulation with fallbacks

### Added
- **🔧 Emergency Diagnostic Tools**: Comprehensive diagnostic and fix scripts for theme consistency issues
  - `emergency_diagnostic_and_fix.py` - Complete theme system analysis and repair
  - `addon_conflict_manager.py` - Professional conflict detection and resolution system
  - `theme_diagnostic.py` variants - Multiple diagnostic approaches for different scenarios

- **🎨 Enhanced CSS Architecture**: Improved theme application with better context awareness
  - CSS Variables integration for consistent theming across all interface elements
  - Refined reviewer-specific CSS with proper card content handling
  - Better button styling with hover states and focus indicators
  - Improved scrollbar theming for consistent visual experience

- **🛠️ Developer Controls**: Manual control scripts for testing and debugging
  - `test_addon_conflicts.py` - User-friendly testing interface for conflict detection
  - Theme manager debug functions for real-time CSS inspection
  - Force refresh capabilities for immediate theme reapplication

### Changed
- **📋 CSS Protection Strategy**: Complete overhaul of card content protection approach
  - **Before**: Broad exclusion of entire card containers from theming
  - **After**: Surgical protection of only actual text content, allowing container theming
  - Card medical content, study materials, and flashcard content now properly themed

- **🎯 Context-Aware CSS Injection**: Enhanced reviewer context handling
  - Different CSS strategies for interface vs. card content
  - Proper timing for reviewer-specific CSS application
  - Better compatibility with Anki 2.1.55+ architectural changes

### Technical Improvements
- **🔬 Root Cause Analysis**: Systematic debugging approach identified exact CSS conflicts
  - Anki 2.1.55+ force-applied Qt stylesheets creating override challenges
  - Addon competition for CSS control (particularly with button styling addons)
  - Timing issues with reviewer webview CSS injection

- **💪 Robustness Enhancements**: Multiple fallback systems for maximum reliability
  - Multi-method CSS injection (webview, Qt, DOM) ensures theme application success
  - Real-time conflict monitoring every 30 seconds for persistent issues
  - Comprehensive error handling with detailed logging for troubleshooting

- **⚡ Performance Optimizations**: CSS caching and efficient application strategies
  - Reduced redundant CSS generation through improved caching system
  - Context-specific CSS generation reduces unnecessary processing
  - Emergency fixes available for immediate user relief

### Known Resolved Issues
- ✅ Interface elements not matching selected VS Code theme colors
- ✅ Buttons and UI components showing default Anki styling instead of theme
- ✅ Card content areas remaining unthemed despite interface theming working
- ✅ Bottom button bar appearing cramped with insufficient padding
- ✅ Conflicts with "The KING of Button Add-ons" and similar styling addons
- ✅ Theme consistency issues after Anki 2.1.55+ updates

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