# VS Code Themes for Anki

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Anki](https://img.shields.io/badge/anki-2.1.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Transform your Anki experience with popular VS Code themes! This addon brings the familiar, eye-friendly color schemes from your favorite code editor directly into Anki, making your study sessions more comfortable and visually appealing.

## ✨ Features

- **12+ Premium VS Code Themes**: One Dark Pro, Dracula, GitHub Dark, Tokyo Night, Ayu Dark, Monokai Pro, and more
- **Mac-Native Title Bar**: Custom title bar with fast restart functionality
- **Perfect Alignment**: Fixed deck browser layout inconsistencies and statistics alignment
- **Smart Layout Management**: Intelligent Qt and CSS integration for seamless theming
- **Real-time Theme Switching**: Switch themes instantly without restarting Anki
- **Comprehensive Coverage**: Themes applied to both UI and card content
- **Custom CSS Support**: Add your own custom styles on top of any theme

## 🎨 Available Themes

| Theme | Description |
|-------|-------------|
| **One Dark Pro** | The iconic VS Code dark theme |
| **Dracula** | A dark theme for those who live in the shadows |
| **GitHub Dark** | GitHub's official dark theme |
| **Tokyo Night** | A clean, dark theme inspired by Tokyo's neon nights |
| **Ayu Dark** | A simple theme with bright colors |
| **Monokai Pro** | The classic Monokai with modern improvements |
| **Solarized Dark** | The legendary Solarized color scheme |

## 🚀 Recent Improvements (v1.1.0)

- ✅ **Fixed Deck List Gap**: Eliminated unwanted spacing in deck browser
- ✅ **Mac-Native Title Bar**: Added custom title bar with native macOS styling
- ✅ **Fast Restart Button**: Quick restart without syncing (⟳ button in title bar)
- ✅ **Perfect Statistics Alignment**: Fixed number alignment in deck browser
- ✅ **Redesigned Button Panel**: Consistent button styling and alignment
- ✅ **Qt Layout Manager Integration**: Direct layout fixes for persistent improvements

## 📦 Installation

### Method 1: Anki Add-ons (Recommended)
1. Open Anki
2. Go to `Tools` → `Add-ons` → `Get Add-ons...`
3. Enter the add-on code: `[CODE_PENDING]`
4. Restart Anki

### Method 2: Manual Installation
1. Download the latest release from [GitHub Releases](https://github.com/Masihhedayati/vscode-themes-anki/releases)
2. Extract the files to your Anki addons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\vscode_themes_anki`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/vscode_themes_anki`
   - **Linux**: `~/.local/share/Anki2/addons21/vscode_themes_anki`
3. Restart Anki

## 🎯 Usage

1. **Theme Selection**: Go to `Tools` → `VS Code Themes` → Choose your preferred theme
2. **Fast Restart**: Click the ⟳ button in the title bar for instant restart
3. **Custom CSS**: Add your own styles in the addon configuration
4. **Toggle Coverage**: Enable/disable theming for UI and/or cards independently

## 🛠️ Configuration

The addon can be configured through:
- **Anki's Add-on Config**: `Tools` → `Add-ons` → `VS Code Themes` → `Config`
- **Theme Manager UI**: Quick access through the Tools menu

```json
{
  "current_theme": "one_dark_pro",
  "apply_to_cards": true,
  "apply_to_ui": true,
  "use_custom_titlebar": true,
  "custom_css": ""
}
```

## 🏗️ Architecture

This addon uses a sophisticated approach to theming:

- **Theme Manager**: Central coordinator for all theming operations
- **Qt Integration**: Direct layout manager manipulation for persistent fixes
- **CSS Injection**: Dynamic stylesheet generation and injection
- **Hook System**: Intercepts Anki's rendering pipeline for seamless integration
- **Platform Detection**: Mac-specific optimizations and native styling

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development

### Project Structure
```
vscode_themes_anki/
├── __init__.py              # Addon entry point
├── theme_manager.py         # Core theming logic
├── custom_titlebar.py       # Mac-native title bar
├── ui.py                   # Theme selection interface
├── theme_converter.py      # Theme processing utilities
├── themes/                 # Theme definitions
├── resources/             # Static assets
└── manifest.json          # Addon metadata
```

### Adding New Themes
1. Create a new `.json` file in the `themes/` directory
2. Follow the existing theme structure
3. Add the theme to the theme list in `theme_manager.py`
4. Test thoroughly across different Anki views

## 🐛 Known Issues

- Some third-party addons may interfere with theming
- Custom CSS may need adjustment after Anki updates
- Theme switching requires a brief moment to fully apply

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- VS Code team for the incredible themes
- Anki community for continuous feedback
- All contributors who helped improve this addon

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Masihhedayati/vscode-themes-anki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Masihhedayati/vscode-themes-anki/discussions)
- **Anki Forums**: [AnkiWeb Support](https://forums.ankiweb.net)

---

**Made with ❤️ for the Anki community**