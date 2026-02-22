# Contributing to Govee Razer LED Controller

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🧪 Add tests
- 🌍 Add translations

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/bochelork/govee_razer_led.git
cd govee_razer_led
```

### 2. Set Up Development Environment

```bash
# Install Home Assistant in development mode
pip install homeassistant

# Link the custom component for testing
ln -s $(pwd)/custom_components/govee_razer_led ~/.homeassistant/custom_components/
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Example Code Style

```python
"""Module for handling Govee protocol."""

def calculate_checksum(data: bytes) -> int:
    """
    Calculate XOR checksum for packet data.
    
    Args:
        data: Byte array to calculate checksum for
        
    Returns:
        XOR checksum as integer
    """
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum
```

### Testing

Before submitting:

1. **Test manually** with your Govee device
2. **Check logs** for errors/warnings
3. **Test edge cases** (e.g., invalid IPs, disconnection)
4. **Test with different configurations**

### Logging

Use appropriate log levels:

```python
import logging

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("Detailed info for debugging")
_LOGGER.info("General information")
_LOGGER.warning("Warning about potential issue")
_LOGGER.error("Error occurred: %s", error)
```

## Pull Request Process

### 1. Update Documentation

- Update README.md if adding features
- Add entries to CHANGELOG.md
- Update INSTALL.md if changing setup
- Update examples/ if relevant

### 2. Commit Messages

Use clear, descriptive commit messages:

```
Add support for 20-LED strips

- Update LED count validation
- Add configuration example
- Update documentation

Fixes #123
```

### 3. Submit Pull Request

1. Push your branch to GitHub
2. Create a Pull Request
3. Fill out the PR template
4. Link related issues
5. Wait for review

### 4. Code Review

- Address reviewer comments
- Update code as needed
- Keep discussion respectful and constructive

## Reporting Bugs

### Before Reporting

1. Check if the issue already exists
2. Test with latest version
3. Verify it's not a configuration issue
4. Check the logs for errors

### Bug Report Template

**Title**: Brief description of the issue

**Description**:
Clear description of what went wrong

**Steps to Reproduce**:
1. First step
2. Second step
3. ...

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happened

**Environment**:
- Home Assistant version: X.X.X
- Integration version: X.X.X
- Govee device model: HXXXX
- Number of LEDs: XX

**Logs**:
```
Paste relevant logs here
```

**Configuration**:
```yaml
# Your configuration (remove sensitive info)
```

## Suggesting Features

### Feature Request Template

**Title**: Brief feature description

**Problem**:
What problem does this solve?

**Proposed Solution**:
How should it work?

**Alternatives**:
Other ways to solve this?

**Additional Context**:
Any other relevant info

## Development Tips

### Testing Without a Device

You can test basic functionality without a physical device:

1. Use a network packet logger (Wireshark)
2. Create mock UDP receiver for testing
3. Use virtual environments

### Understanding the Protocol

Read `PROTOCOL.md` for detailed protocol documentation.

### Common Development Tasks

**Adding a new effect:**

1. Add effect name to `const.py`
2. Implement in `GoveeColorManager.generate_effect_colors()`
3. Add to `EFFECTS` list
4. Update documentation
5. Add example usage

**Changing LED data format:**

1. Update `govee_protocol.py`
2. Test with various LED counts
3. Update protocol documentation
4. Test with actual device

**Adding configuration option:**

1. Add to `const.py`
2. Add to `config_flow.py` schema
3. Update `light.py` to use it
4. Update `strings.json`
5. Update README.md

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing private information

## Questions?

- Open a [GitHub Discussion](https://github.com/bochelork/govee_razer_led/discussions)
- Check existing [Issues](https://github.com/bochelork/govee_razer_led/issues)
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Git commit history

Thank you for contributing! 🎉
