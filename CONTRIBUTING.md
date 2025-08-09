# Contributing to JWhisper

Thank you for your interest in contributing to JWhisper! This document provides guidelines and information for contributors.

## 🤝 Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve documentation and guides
- **Testing**: Help test new features and releases
- **User Support**: Help other users in discussions

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps that reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: 
   - OS version (Windows 10/11)
   - Python version
   - JWhisper version
6. **Logs**: Include relevant log entries from `src/jwhisper.log`

## 💡 Feature Requests

For feature requests:

1. **Search first**: Check if the feature has already been requested
2. **Use case**: Explain why this feature would be useful
3. **Details**: Provide specific details about the desired functionality
4. **Mockups**: Include mockups or examples if applicable

## 🛠️ Development Setup

### Prerequisites

- Windows 10/11
- Python 3.8+
- Git
- A code editor (VS Code recommended)

### Setup Steps

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/JWhisper.git
   cd JWhisper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If dev requirements exist
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Code Style

### Python Code Style

- **PEP 8**: Follow Python PEP 8 style guide
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Document functions and classes
- **Comments**: Add comments for complex logic

### Example:
```python
def transcribe_audio(audio_data: np.ndarray, language: Optional[str] = None) -> str:
    """
    Transcribe audio data using Whisper model.
    
    Args:
        audio_data: Raw audio data as numpy array
        language: Optional language code ('en', 'ru', etc.)
        
    Returns:
        Transcribed text string
    """
    # Implementation here
    pass
```

### Batch Files

- Use clear, descriptive variable names
- Add comments explaining complex operations
- Follow consistent formatting

## 🧪 Testing

### Manual Testing

1. **Install your changes** using `scripts\install.bat`
2. **Test core functionality**:
   - Start/stop service
   - Voice recording and transcription
   - System tray integration
   - Auto-startup functionality
3. **Test edge cases**:
   - Long recordings
   - Background noise
   - Different languages
   - System restart scenarios

### Test Scenarios

- [ ] Service starts successfully
- [ ] F9 hotkey works correctly
- [ ] Audio recording functions properly
- [ ] Text is transcribed accurately
- [ ] Text is pasted correctly
- [ ] System tray icon appears and works
- [ ] Service manager functions work
- [ ] Auto-startup works after reboot
- [ ] Service stops cleanly
- [ ] Logs are generated correctly

## 📋 Pull Request Process

### Before Submitting

1. **Test thoroughly** on your local system
2. **Update documentation** if needed
3. **Add/update comments** in code
4. **Check for breaking changes**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (specify):

## Testing
- [ ] Tested manually
- [ ] All scenarios work as expected
- [ ] No breaking changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated if needed
- [ ] Comments added for complex code
```

### Review Process

1. **Automated checks**: Ensure all checks pass
2. **Code review**: Maintainers will review your code
3. **Testing**: Changes will be tested
4. **Feedback**: Address any requested changes
5. **Merge**: Once approved, changes will be merged

## 📚 Documentation

### Types of Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: Document functions and classes
- **README**: Keep user-facing documentation updated
- **Technical Docs**: Add to `docs/` folder for technical details

### Documentation Style

- **Clear and Concise**: Use simple, clear language
- **Examples**: Include code examples where helpful
- **Screenshots**: Add screenshots for UI changes
- **Step-by-step**: Break complex processes into steps

## 🏷️ Version Management

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes (backward compatible)

### Release Notes

- Update `CHANGELOG.md` for significant changes
- Include release notes in GitHub releases
- Document breaking changes clearly

## 🆘 Getting Help

### Community Support

- **GitHub Discussions**: Ask questions and discuss ideas
- **Issues**: Report bugs or request help
- **Discord**: Join our community chat (if available)

### Maintainer Contact

- **GitHub**: @yourusername
- **Email**: maintainer@example.com

## 📄 License

By contributing to JWhisper, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are recognized in:

- **README**: Contributors section
- **CHANGELOG**: Release notes
- **GitHub**: Contributor graphs and history

---

**Thank you for contributing to JWhisper! 🎉**