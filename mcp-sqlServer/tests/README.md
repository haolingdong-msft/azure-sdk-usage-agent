# Test Documentation

This directory contains automated tests for the SQL Server MCP (Model Context Protocol) server with MSI authentication.

## Overview

The test suite validates SQL Server connectivity using Azure Managed Service Identity (MSI) authentication and provides comprehensive logging for debugging and monitoring.

## Test Structure

```
tests/
├── README.md                    # This documentation
├── test_connection_pytest.py    # Main test suite
├── test_logger.py              # Test logging utility
└── logs/                       # Test execution logs
    └── test_execution_*.log    # Timestamped log files
```

## What is Tested

### 1. `test_client_initialization`
- **Purpose**: Validates SQL client can be instantiated correctly
- **Tests**:
  - Client object creation
  - Required attributes exist (`connection_string`, `credential`)
  - Connection string format validation
  - MSI authentication configuration
- **Expected Result**: ✅ PASS (always succeeds in any environment)

### 2. `test_connection_test_method`
- **Purpose**: Tests the synchronous connection test method
- **Tests**:
  - Connection test method execution
  - Error handling and graceful failure
  - Return value structure validation
- **Expected Result**: ✅ PASS (handles errors gracefully)

### 3. `test_simple_query_execution` (async)
- **Purpose**: Tests basic SQL query execution
- **Tests**:
  - Simple SELECT query execution
  - Result structure validation
  - Error handling for connection failures
- **Expected Result**: ⏭️ SKIP (in test environments without MSI setup)

### 4. `test_database_connection` (async)
- **Purpose**: Tests direct database connection establishment
- **Tests**:
  - Low-level connection creation
  - Connection cleanup
  - Connection failure handling
- **Expected Result**: ⏭️ SKIP (in test environments without MSI setup)

### 5. `test_usage_metrics_query` (async)
- **Purpose**: Tests querying the actual usage_metrics table
- **Tests**:
  - Table-specific query execution
  - Real data retrieval validation
  - Production-like scenario testing
- **Expected Result**: ⏭️ SKIP (in test environments without MSI setup)

## How to Run Tests

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required packages** (included in requirements.txt):
   - `pytest>=8.0.0` - Test framework
   - `pytest-asyncio>=0.21.0` - Async test support
   - `azure-identity` - Azure authentication
   - `pyodbc` - SQL Server connectivity

### Running Tests

#### Run All Tests
```bash
# From project root
python -m pytest tests/test_connection_pytest.py -v

# With detailed output
python -m pytest tests/test_connection_pytest.py -v -s
```

#### Run Specific Tests
```bash
# Test client initialization only
python -m pytest tests/test_connection_pytest.py::TestSQLConnection::test_client_initialization -v

# Test connection method only
python -m pytest tests/test_connection_pytest.py::TestSQLConnection::test_connection_test_method -v

# Run async tests only
python -m pytest tests/test_connection_pytest.py -k "asyncio" -v
```

#### Run with Time Limit (recommended for CI/CD)
```bash
# Timeout after 5 minutes to prevent hanging
timeout 300s python -m pytest tests/test_connection_pytest.py -v
```

### Test Environment Expectations

#### In Development/Test Environment (No MSI setup):
- ✅ **2 tests PASS**: `test_client_initialization`, `test_connection_test_method`
- ⏭️ **3 tests SKIP**: All async connection tests (expected behavior)
- ⏱️ **Execution time**: ~30 seconds total

#### In Production Environment (With MSI setup):
- ✅ **5 tests PASS**: All tests should pass
- ⏱️ **Execution time**: ~10-30 seconds total

## Test Logging

### Log File Location
```
tests/logs/test_execution_YYYYMMDD_HHMMSS.log
```

### Log File Features
- **Timestamped entries** with precise timing
- **Emoji indicators** for quick visual scanning
- **Structured format** with log levels and function names
- **Both console and file output** for immediate feedback and permanent records

### Reading Test Logs

#### Log Entry Format
```
YYYY-MM-DD HH:MM:SS,mmm | LEVEL | function_name | message
```

#### Common Log Patterns

**Test Lifecycle**:
```
🧪 Starting test: test_name
✅ Test passed: test_name - details
⏭️ Test skipped: test_name - Reason: reason
❌ Test error: test_name - Error: error_message
```

**Connection Events**:
```
🔐 Attempting connection to server, database: database_name
✅ Connection successful to server, database: database_name
❌ Connection failed to server, database: database_name - Error: error_details
```

**Query Execution**:
```
📊 Executing query: SELECT ...
📈 Query returned N rows (execution time: X.XXs)
```

**MSI Configuration**:
```
🔑 Using system-assigned managed identity
🔑 Using user-assigned managed identity: client_id
```

### Checking Test Results

#### 1. Check Console Output
```bash
# Look for test summary
================ X passed, Y skipped in Z.ZZs ================
```

#### 2. Check Latest Log File
```bash
# View latest log
ls -la tests/logs/test_execution_*.log | tail -1

# Read latest log
cat tests/logs/test_execution_$(ls tests/logs/ | grep test_execution | tail -1)

# Monitor real-time (if test is running)
tail -f tests/logs/test_execution_$(ls tests/logs/ | grep test_execution | tail -1)
```

#### 3. Search for Specific Issues
```bash
# Find connection errors
grep "❌ Connection failed" tests/logs/test_execution_*.log

# Find test failures
grep "❌ Test error" tests/logs/test_execution_*.log

# Find all skipped tests
grep "⏭️ Test skipped" tests/logs/test_execution_*.log
```

## Troubleshooting

### Common Issues

#### 1. **Tests Hang/Take Too Long**
- **Symptom**: Tests run for more than 5 minutes
- **Cause**: MSI authentication timeout in test environment
- **Solution**: Use timeout command or expect 3 tests to skip
- **Fix**: `timeout 300s python -m pytest ...`

#### 2. **Import Errors**
```
ModuleNotFoundError: No module named 'pytest'
```
- **Solution**: Install requirements: `pip install -r requirements.txt`

#### 3. **Connection Timeout Errors**
```
Login timeout expired (0) (SQLDriverConnect)
```
- **Expected**: This is normal in test environments without MSI setup
- **Result**: Tests should skip gracefully, not fail

#### 4. **Event Loop Errors**
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```
- **Cause**: Incorrect `@pytest.mark.asyncio` usage
- **Check**: Ensure sync methods don't have async decorators

### Performance Optimization

#### Connection Timeout Settings
The SQL client uses reduced timeouts for faster test execution:
```python
Connection Timeout=3;  # 3 seconds instead of default 30
Login Timeout=3;       # 3 seconds for MSI authentication
```

This reduces individual test timeout from ~2.5 minutes to ~6 seconds in failure scenarios.

## CI/CD Integration

### Recommended CI Pipeline
```yaml
# Example GitHub Actions
- name: Run SQL Tests
  run: |
    timeout 300s python -m pytest tests/test_connection_pytest.py -v --tb=short
  continue-on-error: true  # Allow MSI connection failures in CI

- name: Check Test Logs
  run: |
    echo "Latest test log:"
    ls -la tests/logs/
    tail -20 tests/logs/test_execution_*.log | tail -20
```

### Success Criteria for CI
- ✅ **Client initialization**: Must pass
- ✅ **Connection test method**: Must pass  
- ⏭️ **Connection tests**: Can skip (expected in CI environments)
- ❌ **No hard failures**: Tests should not crash or hang

## Development Workflow

1. **Before code changes**: Run tests to establish baseline
2. **After code changes**: Run tests to verify functionality
3. **Check logs**: Review logs for any new errors or warnings
4. **Performance check**: Ensure tests complete within reasonable time
5. **MSI validation**: In production environment, verify all tests pass

## Log Retention

- **Development**: Keep recent logs for debugging
- **Production**: Archive logs for audit and troubleshooting
- **CI/CD**: Upload logs as build artifacts

```bash
# Clean old logs (keep last 10)
ls -t tests/logs/test_execution_*.log | tail -n +11 | xargs rm -f
```
