# Contributing to errortools

Thank you for your interest in contributing to **errortools**! We welcome contributions from the community, including bug reports, feature requests, documentation improvements, and code submissions.

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/more-abc/errortools.git
   cd errortools
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## Submitting Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, well-documented code
- Add or update tests for your changes
- Ensure your code follows the project style guide
- Keep commits atomic and with clear messages

### 3. Run All Quality Checks

Before pushing, ensure everything passes:

```bash
# Format code
black .

# Run linter
flake8 .

# Type check
mypy .

# Run tests with coverage
pytest
```

### 4. Commit and Push

```bash
git add change_file
git commit -m "Descriptive commit message"
git push origin type/your-branch-name
```

### 5. Open a Pull Request

- Use the provided PR template
- Link related issues with `Closes #` or `Relates to #`
- Describe your changes clearly
- Ensure the PR title is descriptive and concise

## Pull Request Guidelines

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines (Black, Flake8)
- [ ] All tests pass locally (`pytest`)
- [ ] Type checks pass (`mypy`)
- [ ] Added or updated tests for new functionality
- [ ] Documentation is updated if needed
- [ ] No new warnings or errors
- [ ] No breaking changes (discuss with maintainers if necessary)
- [ ] Commit messages are clear and descriptive

## Code Review Process

1. Automated checks (CI/CD) will run on your PR
2. Maintainers will review your code
3. Address any requested changes
4. Once approved, your PR will be merged

## Reporting Issues

### Bug Reports
Please use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Python version and OS
- Steps to reproduce
- Expected vs. actual behavior
- Error messages and tracebacks

### Feature Requests
Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and describe:
- The problem you're solving
- Your proposed solution
- Alternative approaches you've considered

### Documentation Issues
Use the [documentation template](.github/ISSUE_TEMPLATE/docs.md) to report unclear or missing documentation.

### Performance Issues
Use the [performance template](.github/ISSUE_TEMPLATE/performance.md) to report performance bottlenecks.

## Project Structure

```
errortools/
├── _errortools/          # Main package (implementation)
│   ├── classes/          # Custom exception classes
│   ├── decorator/        # Decorator utilities
│   ├── descriptor/       # Descriptor utilities
│   ├── logging/          # Logging implementation
│   ├── methods/          # Method utilities
│   ├── wrappers/         # Wrapper utilities
│   ├── future.py         # Performance utilities
│   ├── ignore.py         # Exception suppression
│   ├── raises.py         # Exception raising
│   ├── typing.py         # Type aliases
│   └── ...
├── errortools/           # Public API (exports)
├── tests/                # Test suite
├── .github/              # GitHub templates and workflows
├── setup.py              # Package configuration
├── pytest.ini            # Pytest configuration
├── requirements-dev.txt  # Development dependencies
└── ...
```

## Module Overview

- **ignore.py**: Context managers for suppressing exceptions (`ignore()`, `fast_ignore()`, `timeout()`, `retry()`)
- **raises.py**: Functions for raising exceptions (`raises()`, `raises_all()`, `reraise()`)
- **future.py**: High-performance utilities (`super_fast_ignore()`, `ExceptionCollector`)
- **classes/**: Custom exception bases and error codes
- **logging/**: Structured logging functionality
- **decorator/**: Decorators for error handling and caching
- **typing.py**: Type aliases for common patterns
- **...**

## Configuration Files

- **.black**: Black formatter configuration
- **.flake8**: Flake8 linter settings
- **mypy.ini**: MyPy type checker configuration
- **.editorconfig**: Editor configuration for consistency
- **...**

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful to all contributors and community members.

## Questions?

Feel free to:
- Open an discussion for questions
- Create a issue or discussion for feature ideas
- Reach out to maintainers for guidance

Thank you for contributing! 🎉
