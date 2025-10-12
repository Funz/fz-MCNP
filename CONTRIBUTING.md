# Contributing to fz-mcnp

Thank you for your interest in contributing to fz-mcnp! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment (see below)
4. Create a feature branch for your changes
5. Make your changes and test them
6. Submit a pull request

## Development Environment Setup

### Prerequisites

- MCNP6 installation (for testing)
- Python 3.7 or higher
- Git
- fz framework

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fz-mcnp.git
cd fz-mcnp

# Install fz framework
cd ..
git clone https://github.com/Funz/fz.git
cd fz
pip install -e .

# Return to fz-mcnp
cd ../fz-mcnp

# Set MCNP_PATH
export MCNP_PATH="/path/to/your/MCNP6"
```

## Types of Contributions

### Bug Reports

When filing a bug report, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- MCNP version
- Python version
- Operating system
- Relevant error messages or logs

### Feature Requests

When requesting a feature:

- Explain the use case
- Describe the desired behavior
- Provide examples if possible
- Explain why this would benefit other users

### Code Contributions

#### Before You Start

- Check existing issues and pull requests
- Discuss major changes in an issue first
- Follow the coding style of the project
- Write clear commit messages

#### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Keep changes focused and atomic
   - Update documentation as needed
   - Add examples if relevant

3. **Test your changes:**
   ```bash
   # Test with example
   python example_godiva.py
   
   # Validate JSON files
   python -m json.tool .fz/models/MCNP.json
   python -m json.tool .fz/calculators/Localhost_MCNP.json
   
   # Check shell script syntax
   bash -n .fz/calculators/MCNP.sh
   
   # Check Python syntax
   python -m py_compile example_godiva.py
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill in the PR template
   - Submit the PR

## Coding Guidelines

### Shell Scripts

- Use `#!/bin/bash` shebang
- Add comments for complex logic
- Validate input parameters
- Provide clear error messages
- Use `set -e` for critical scripts

Example:
```bash
#!/bin/bash

# Check required environment variable
if [ -z "$MCNP_PATH" ]; then
  echo "Error: MCNP_PATH is not set"
  exit 1
fi
```

### Python Scripts

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings for functions
- Handle exceptions appropriately
- Keep functions focused

Example:
```python
def run_mcnp_study(input_file, parameters):
    """
    Run MCNP parametric study.
    
    Args:
        input_file: Path to MCNP input file
        parameters: Dict of parameter values
        
    Returns:
        DataFrame with results
    """
    # Implementation here
```

### JSON Configuration

- Use 4-space indentation
- Keep structure consistent
- Validate JSON syntax
- Add comments in documentation

Example:
```json
{
    "id": "MCNP",
    "varprefix": "%",
    "delim": "()",
    "output": {
        "mean_keff": "shell command here"
    }
}
```

### Documentation

- Use clear, concise language
- Provide examples
- Keep README up to date
- Document all options and parameters

## Testing

### Manual Testing

Test your changes with:

1. **Basic functionality:**
   ```bash
   python example_godiva.py
   ```

2. **Different parameter values:**
   ```python
   import fz
   results = fz.fzr("godiva.inp", {"r": [8.0, 9.0]}, "MCNP")
   ```

3. **Edge cases:**
   - Empty parameter lists
   - Invalid MCNP paths
   - Missing input files
   - Malformed MCNP input

### Test Coverage

If adding new features, consider:

- Normal operation
- Error conditions
- Edge cases
- Performance implications

## Documentation Updates

When making changes, update:

- README.md (if user-facing)
- QUICKSTART.md (if affecting setup)
- MIGRATION.md (if changing compatibility)
- Code comments (always)
- Example scripts (if relevant)

## Pull Request Process

1. **PR Title:** Clear and descriptive (e.g., "Add support for MCNP5")
2. **PR Description:** Explain what, why, and how
3. **Testing:** Describe testing performed
4. **Breaking Changes:** Clearly mark if any
5. **Documentation:** Confirm docs are updated

### PR Checklist

- [ ] Code follows project style
- [ ] Tests pass (manual testing)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] JSON files validated
- [ ] Shell scripts validated
- [ ] Python scripts validated

## Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

## Code Review

All submissions require review. We'll:

- Review within a week
- Provide constructive feedback
- Request changes if needed
- Merge when approved

Please be patient and responsive to feedback.

## Community

- Be respectful and professional
- Welcome newcomers
- Help others learn
- Share knowledge

## Questions?

- Open an issue for clarification
- Check existing documentation
- Review the fz framework docs

## License

By contributing, you agree that your contributions will be licensed under the BSD 3-Clause License.

## Recognition

Contributors are recognized in:
- Git history
- Release notes (for significant contributions)
- Special thanks section (as appropriate)

Thank you for contributing to fz-mcnp! 🎉
