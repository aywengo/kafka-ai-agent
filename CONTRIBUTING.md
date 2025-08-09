# Contributing to Kafka AI Agent

Thank you for your interest in contributing to Kafka AI Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Create a new issue with a clear title and description
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Open a discussion in the Issues section
2. Describe the feature and its use case
3. Explain why it would be valuable

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/kafka-ai-agent.git
   cd kafka-ai-agent
   git remote add upstream https://github.com/aywengo/kafka-ai-agent.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Check code style
   black .
   flake8 .
   mypy .
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions or changes
   - `refactor:` Code refactoring
   - `style:` Code style changes
   - `chore:` Maintenance tasks

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (optional)

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Run with coverage**
   ```bash
   pytest tests/ --cov=kafka_ai_agent --cov-report=html
   ```

## Coding Standards

### Python Style Guide

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable names

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings
- Update README.md for significant changes
- Add examples for new features

### Testing

- Write unit tests for all new code
- Maintain test coverage above 80%
- Use pytest for testing
- Mock external dependencies

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a release PR
4. After merge, tag the release
5. Build and publish to PyPI

## Getting Help

- Join our discussions on GitHub
- Check the documentation
- Ask questions in issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.