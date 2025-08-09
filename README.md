# JWhisper - Voice-to-Text Application

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

A powerful, lightweight voice-to-text application for Windows with system tray integration and hotkey support.

## ✨ Features

- **🎤 Push-to-Talk**: Press and hold F9 to record voice
- **🧠 AI-Powered**: Uses OpenAI's Whisper model for accurate transcription
- **📋 Instant Paste**: Automatically types transcribed text where your cursor is
- **🔧 System Tray**: Runs quietly in the background with tray icon
- **⚡ Fast**: Optimized for real-time voice recognition
- **🌐 Multi-language**: Auto-detects language or configure specific languages
- **🔄 Auto-startup**: Optional Windows startup integration
- **📊 Logging**: Comprehensive logging and status monitoring

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8 or later
- Microphone access

### Installation

1. **Download or clone this repository**
   ```bash
   git clone https://github.com/yourusername/JWhisper.git
   cd JWhisper
   ```

2. **Run the installer**
   ```bash
   scripts\install.bat
   ```

3. **Launch the service manager**
   ```bash
   scripts\manager.bat
   ```

4. **Install and start the service** (Option 1 in the manager)

### Usage

1. **Look for the microphone icon** in your system tray
2. **Press and hold F9** while speaking
3. **Release F9** when done - text will be automatically typed where your cursor is
4. **Right-click the tray icon** for options and settings

## 📁 Project Structure

```
JWhisper/
├── src/
│   └── jwhisper.py          # Main application
├── scripts/
│   ├── install.bat          # Installation script
│   ├── manager.bat          # Service management interface
│   └── start_hidden.vbs     # Silent launcher
├── docs/
│   ├── CONFIGURATION.md     # Configuration guide
│   └── TROUBLESHOOTING.md   # Troubleshooting guide
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
├── CONTRIBUTING.md         # Contribution guidelines
└── CHANGELOG.md           # Version history
```

## ⚙️ Configuration

The application can be configured by modifying the settings in `src/jwhisper.py`:

- **PUSH_TO_TALK_KEY**: Change the hotkey (default: F9)
- **WHISPER_MODEL_NAME**: Model size ("tiny", "base", "small", "medium", "large-v3")
- **LANGUAGE**: Set specific language or None for auto-detection
- **AUDIO_THRESHOLD**: Sensitivity for voice detection

## 🛠️ Service Management

Use the service manager (`scripts\manager.bat`) to:

1. **Install Service** - Set up and start JWhisper with Windows startup
2. **Remove Service** - Stop and remove from startup
3. **Check Status** - View running status and logs
4. **View Logs** - Open log file in notepad
5. **Restart Service** - Restart the application
6. **Install Dependencies** - Install/update Python packages

## 🐛 Troubleshooting

### Common Issues

**Service won't start:**
- Ensure Python 3.8+ is installed
- Run `scripts\install.bat` to install dependencies
- Check antivirus isn't blocking the application

**No transcription:**
- Check microphone permissions
- Verify microphone is working in other applications
- Try adjusting AUDIO_THRESHOLD in settings

**Text not pasting:**
- Ensure the target application has focus
- Try clicking where you want text to appear before recording

For detailed troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for optimized inference
- All contributors and users of this project

## 📞 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/JWhisper/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/JWhisper/discussions)

---

**Made with ❤️ for seamless voice-to-text transcription**