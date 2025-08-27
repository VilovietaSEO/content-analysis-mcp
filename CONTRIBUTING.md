# Contributing to Content Analysis MCP

Thank you for your interest in contributing! This project aims to provide accessible, professional-grade content analysis tools for the SEO community.

## How to Contribute

### Reporting Issues
- Use the GitHub issue tracker
- Include your OS, Python version, and complete error messages
- Describe what you expected vs what happened

### Feature Requests
- Check existing issues first
- Clearly describe the use case and benefit
- Consider if it aligns with the project's goal of simplicity

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes**
4. **Test thoroughly** with different content types
5. **Update documentation** if needed
6. **Submit a pull request**

### Code Standards

- **Python 3.10+** compatibility
- **Clear, readable code** with comments
- **Error handling** for edge cases
- **Consistent formatting** (we use Black)
- **Type hints** where helpful

### Testing

Before submitting:
```bash
# Test with different content types
python analyze_content_quality.py test_collection

# Test error handling
python analyze_content_quality.py nonexistent_collection

# Test command line options
python analyze_content_quality.py --help
```

### Areas for Contribution

- **Additional analysis dimensions** (readability, sentiment, etc.)
- **Output formats** (CSV, HTML reports, etc.)
- **Performance improvements** for large collections
- **Better error messages** and user guidance
- **Documentation improvements**
- **Example content and use cases**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/content-analysis-mcp.git
cd content-analysis-mcp

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests (if you add them)
python -m pytest tests/
```

## Questions?

Feel free to open an issue for questions or discussion. We appreciate all contributions, from typo fixes to major features!