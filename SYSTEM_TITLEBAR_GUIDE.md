# System Title Bar Theming Guide

## Overview

The **System Title Bar Theming** feature automatically colors the native macOS title bar to match your selected VS Code theme colors. This creates a seamless, cohesive appearance where the title bar harmonizes with your chosen theme.

## Features

### 🎨 **Intelligent Color Adaptation**
- Automatically extracts colors from your VS Code theme
- Generates complementary title bar colors based on theme background
- Maintains proper contrast and readability
- Supports both dark and light themes

### 🖥️ **Native macOS Integration**
- Works with the real macOS title bar (not a replacement)
- Preserves all native functionality (traffic lights, dragging, etc.)
- Compatible with macOS appearance settings
- Seamless integration with Qt and Anki

### ⚡ **Real-time Updates**
- Title bar updates instantly when switching themes
- No restart required for color changes
- Smooth transitions between theme colors

## How It Works

### Color Generation Algorithm

1. **Theme Analysis**: Extracts primary colors from the VS Code theme:
   - `editor.background` - Main background color
   - `button.background` - Accent color for influence

2. **Color Processing**: 
   - Converts hex colors to HSV color space for manipulation
   - Determines if theme is dark or light based on luminance
   - Generates appropriate title bar color variation

3. **Dark Theme Processing**:
   - Makes title bar slightly lighter than background
   - Reduces saturation for subtle effect
   - Caps brightness to maintain dark appearance

4. **Light Theme Processing**:
   - Makes title bar slightly darker than background
   - Maintains good contrast
   - Preserves light theme aesthetics

### Technical Implementation

The system uses multiple methods to ensure compatibility:

1. **Qt Palette**: Updates window palette colors
2. **Stylesheet**: Applies background color via CSS
3. **macOS Attributes**: Sets native appearance flags when possible

## Usage

### Enable/Disable
1. Open **Tools → VS Code Themes**
2. Check/uncheck **"🎨 Theme macOS title bar colors (matches theme)"**
3. Changes apply immediately when switching themes

### Configuration
Located in `config.json`:
```json
{
    "system_titlebar_theming": true
}
```

## Platform Support

- **macOS**: Full support with native title bar theming
- **Windows/Linux**: Feature disabled (system-specific)

## Theme Examples

### Dark Themes
- **One Dark Pro**: Deep blue-gray title bar
- **Dracula**: Subtle purple-tinted title bar  
- **Monokai**: Warm dark gray title bar

### Light Themes
- **Light VS**: Clean light gray title bar
- **GitHub Light**: Soft white-gray title bar
- **Solarized Light**: Warm beige title bar

## Technical Notes

### Color Calculation
```python
# For dark themes
lightness = min(background_lightness + 0.08, 0.3)
saturation = background_saturation * 0.7

# For light themes  
lightness = max(background_lightness - 0.05, 0.7)
saturation = background_saturation * 0.8
```

### Reset Functionality
The system automatically stores the original title bar appearance and can restore it when:
- Feature is disabled
- Addon is unloaded
- Theme is reset

## Troubleshooting

### Title Bar Not Changing
1. Ensure you're on macOS
2. Check that the setting is enabled in VS Code Themes dialog
3. Try switching to a different theme to trigger update
4. Restart Anki if issues persist

### Colors Look Wrong
- Some themes may have unusual color values
- The algorithm automatically adjusts for edge cases
- Light/dark detection handles most scenarios automatically

### Conflicts with Other Addons
- Disable other addons that modify window appearance
- Check for conflicting Qt stylesheets
- Report issues with specific addon combinations

## Future Enhancements

- More sophisticated color harmony algorithms
- User-customizable color adjustment parameters
- Integration with macOS system appearance
- Support for gradient title bar effects

## Related Features

- **Theme Manager**: Core theming system
- **CSS Injection**: Web content theming
- **Qt Styling**: UI element theming

This feature provides a seamless way to extend your VS Code theme beyond just the content area to create a truly unified visual experience in Anki. 