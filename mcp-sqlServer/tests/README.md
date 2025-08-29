# SQL Client Tests

Fast and reliable tests for the SQL Server MCP client with MSI authentication.

The test suite provides comprehensive coverage with optimized performance:
- **Unit tests**: Fast mocked tests (3 seconds)
- **Integration tests**: Real connection tests with smart skipping
- **Clear feedback**: Immediate identification of auth vs code issues

## Quick Start

```bash
# Install test dependencies
pip install -r tests/test_requirements.txt

# Run fast unit tests (2-3 seconds)
python tests/run_tests.py unit

# Run integration tests (if MSI auth available)
python tests/run_tests.py integration

# Run all tests
python tests/run_tests.py all
```

## Test Files

```
tests/
├── README.md                           # This documentation  
├── run_tests.py                        # Test runner script
├── test_connection_pytest.py           # Main test suite (improved)
├── test_logger.py                      # Test logging utility
├── test_requirements.txt               # Test dependencies
└── logs/                               # Test execution logs

Project root:
├── pytest.ini                          # Pytest configuration
```

## Test Categories

### 🚀 **Unit Tests** (Fast - No Network)
- Client initialization and configuration
- Connection string building
- Mock query execution  
- Error handling scenarios
- **Runtime**: 2-3 seconds
- **Always pass**: No auth required

### 🌐 **Integration Tests** (Require MSI Auth)
- Real database connections
- Query execution against SQL Server
- MSI authentication validation
- **Runtime**: 5-10 seconds with auth, skipped without
- **Conditional**: Require proper MSI setup

## Running Tests

### Using the Test Runner (Recommended)
```bash
# Fast unit tests only
python tests/run_tests.py unit

# Integration tests (requires auth)  
python tests/run_tests.py integration

# All tests with dependency installation
python tests/run_tests.py all --install-deps
```

### Using pytest Directly
```bash
# Unit tests only
pytest tests/test_connection_pytest.py -m "not integration" -v

# Integration tests only
pytest tests/test_connection_pytest.py -m "integration" -v

# All tests
pytest tests/test_connection_pytest.py -v
```

## Performance Improvements

The test suite has been optimized for speed and reliability:

| Test Type | Previous | Current | Improvement |
|-----------|----------|---------|-------------|
| Unit tests | ~30s | ~3s | **10x faster** |
| No auth scenario | ~30s (timeouts) | ~3s (fast skip) | **10x faster** |
| With auth | ~10-30s | ~5-10s | **2-3x faster** |
| Integration skip | ~30s (timeouts) | ~0.1s (immediate) | **300x faster** |

## Expected Results

### Without MSI Authentication (Development)
```
✅ test_client_initialization - PASSED
✅ test_connection_string_building - PASSED  
✅ test_mock_query_execution - PASSED
✅ test_mock_connection_error - PASSED
⏭️ test_connection_test_method_fast - SKIPPED (no auth)
⏭️ test_simple_query_execution_fast - SKIPPED (no auth)

Total: ~3 seconds
```

### With MSI Authentication (Production)
```
✅ All unit tests - PASSED
✅ All integration tests - PASSED

Total: ~10 seconds
```

## Troubleshooting

### Tests Running Slowly?
- Use unit tests only: `python run_tests.py unit`
- Check if old timeouts are being used
- Verify you're using the improved test file

### Import Errors?
```bash
pip install -r tests/test_requirements.txt
```

### Auth Issues?
- Integration tests will skip automatically if MSI not available
- Unit tests don't require auth and should always pass
- Check logs in `tests/logs/` for details

## Configuration

Environment variables:
```bash
# Skip integration tests entirely
export SKIP_INTEGRATION_TESTS=true

# Use specific timeout values
export TEST_TIMEOUT=5
```

Pytest markers:
- `@pytest.mark.unit` - Fast tests, no network
- `@pytest.mark.integration` - Require auth and network
