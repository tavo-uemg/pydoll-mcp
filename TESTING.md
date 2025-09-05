# PyDoll MCP Testing Framework

Comprehensive testing framework for the PyDoll MCP browser automation server.

## Overview

This testing framework provides complete coverage for:
- MCP protocol compliance and JSON-RPC communication
- Browser session management and lifecycle
- Tab operations and navigation
- Element finding, interaction, and property operations
- Error handling and edge cases
- Security and performance validation

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m browser      # Browser automation tests

# Run with coverage
pytest --cov=. --cov-report=html

# Run in parallel
pytest -n auto
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_mcp_protocol.py     # MCP protocol compliance tests
├── test_browser_session.py  # Browser session management tests
├── test_tab_operations.py   # Tab and navigation tests
├── test_element_operations.py # Element interaction tests
├── integration/             # Integration test suite
│   ├── test_end_to_end.py   # Complete workflow tests
│   └── test_real_browser.py # Real browser automation tests
└── fixtures/                # Test data and fixtures
    ├── sample_pages/        # HTML test pages
    └── mock_data.py         # Mock response data
```

## Test Categories

### Unit Tests (`-m unit`)
- Individual function and method testing
- Mock-based testing without external dependencies
- Fast execution, suitable for TDD workflows

### Integration Tests (`-m integration`)
- Full system testing with real MCP server process
- Browser automation with actual Chrome/Chromium
- Network requests and file operations

### Browser Tests (`-m browser`)
- Tests requiring actual browser instances
- Element interaction and page manipulation
- Screenshot and PDF generation

## Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Default CLI options with coverage and reporting
- Async test configuration
- Timeout settings and logging

### Coverage Configuration (`.coveragerc`)
- Source code coverage tracking
- Exclusion patterns for test files
- HTML and XML report generation
- Minimum coverage thresholds

## Fixtures

### Core Fixtures (`conftest.py`)

```python
@pytest.fixture
async def mcp_client():
    """MCP test client for JSON-RPC communication."""
    
@pytest.fixture
def mock_pydoll():
    """Mock PyDoll browser for unit testing."""
    
@pytest.fixture
def browser_session_data():
    """Test data for browser session creation."""
    
@pytest.fixture
def element_selectors():
    """Common element selectors for testing."""
```

### Test Data Fixtures
- Sample HTML content for element testing
- Browser configuration data
- Mock JSON-RPC requests and responses

## Testing Patterns

### MCP Protocol Testing
```python
@pytest.mark.asyncio
async def test_tool_call(mcp_client):
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "tool_name",
            "arguments": {"param": "value"}
        }
    }
    response = await mcp_client.send_request(request)
    assert response["jsonrpc"] == "2.0"
    assert "result" in response or "error" in response
```

### Browser Automation Testing
```python
@pytest.mark.browser
async def test_browser_workflow(mcp_client):
    # Create session
    await create_browser_session()
    # Navigate and interact
    await navigate_and_test()
    # Cleanup
    await cleanup_session()
```

### Error Handling Testing
```python
async def test_invalid_parameters():
    # Test with missing required parameters
    # Test with invalid parameter types
    # Test with malformed JSON-RPC requests
```

## CI/CD Integration

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

**Multi-Python Version Testing:**
- Python 3.10, 3.11, 3.12
- Matrix-based parallel execution
- Dependency caching for faster builds

**Test Stages:**
1. **Lint and Type Check**: Ruff, MyPy validation
2. **Unit Tests**: Fast test suite with mocking
3. **Integration Tests**: Full system testing
4. **Security Scan**: Bandit and Safety checks

**Reporting:**
- JUnit XML test results
- Coverage reports with Codecov integration
- HTML coverage reports as artifacts

### Local Development

```bash
# Setup development environment
pip install -e ".[dev]"
pre-commit install

# Run full test suite
pytest --cov=. --cov-report=html

# Run security checks
bandit -r .
safety check

# Format code
black .
ruff --fix .
```

## Best Practices

### Test Design
- **Isolation**: Each test should be independent
- **Deterministic**: Tests should produce consistent results
- **Fast**: Unit tests should run quickly
- **Comprehensive**: Cover happy paths, edge cases, and error conditions

### Mocking Strategy
```python
# Mock external dependencies
@patch('subprocess.Popen')
@patch('asyncio.create_subprocess_exec')
async def test_with_mocks(mock_subprocess, mock_popen):
    # Test logic without external dependencies
```

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_functionality():
    # Use asyncio-compatible fixtures
    # Proper async context management
    # Timeout handling for long-running operations
```

## Performance Testing

### Load Testing
```python
@pytest.mark.performance
async def test_concurrent_requests():
    # Test server under concurrent load
    # Measure response times
    # Validate resource cleanup
```

### Memory Testing
```python
def test_memory_usage():
    # Monitor memory consumption
    # Check for memory leaks
    # Validate cleanup operations
```

## Troubleshooting

### Common Issues

**Chrome/Chromium Not Found:**
```bash
sudo apt-get install chromium-browser chromium-chromedriver
```

**Display Issues (Headless):**
```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
```

**Permission Errors:**
```bash
chmod +x pydoll-mcp
```

### Debug Mode
```bash
# Run tests with verbose output and no capture
pytest -vvv -s --tb=long

# Run single test with debugging
pytest tests/test_specific.py::TestClass::test_method -vvv -s
```

## Continuous Integration

### Required Environment Variables
- `DISPLAY`: For headless browser testing
- `CODECOV_TOKEN`: For coverage reporting (optional)

### Artifact Collection
- Test results in JUnit XML format
- Coverage reports in HTML and XML
- Security scan results
- Performance benchmarks

## Contributing

### Adding New Tests
1. Follow existing test patterns and naming conventions
2. Include appropriate markers (`@pytest.mark.unit`, etc.)
3. Add fixtures for reusable test data
4. Update documentation for new test categories

### Test Requirements
- All new features must include tests
- Maintain minimum 70% code coverage
- Pass all existing tests
- Include both positive and negative test cases

This testing framework ensures robust, reliable operation of the PyDoll MCP server across different environments and use cases.