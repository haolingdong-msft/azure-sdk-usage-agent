#!/usr/bin/env python3
"""
Test logging utility for recording test execution results and errors
"""

import logging
import os
import datetime
from pathlib import Path


class TestLogger:
    """Logger for test execution results and errors"""
    
    def __init__(self, log_dir: str = "tests/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"test_execution_{timestamp}.log"
        
        # Setup logging
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(funcName)s | %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Test logging started - Log file: {self.log_file}")
    
    def log_test_start(self, test_name: str):
        """Log the start of a test"""
        self.logger.info(f"🧪 Starting test: {test_name}")
    
    def log_test_success(self, test_name: str, details: str = ""):
        """Log successful test completion"""
        msg = f"✅ Test passed: {test_name}"
        if details:
            msg += f" - {details}"
        self.logger.info(msg)
    
    def log_test_skip(self, test_name: str, reason: str):
        """Log skipped test"""
        self.logger.warning(f"⏭️ Test skipped: {test_name} - Reason: {reason}")
    
    def log_test_error(self, test_name: str, error: Exception, details: str = ""):
        """Log test error"""
        msg = f"❌ Test error: {test_name} - Error: {str(error)}"
        if details:
            msg += f" - Details: {details}"
        self.logger.error(msg)
    
    def log_connection_attempt(self, server: str, database: str):
        """Log database connection attempt"""
        self.logger.info(f"🔐 Attempting connection to {server}, database: {database}")
    
    def log_connection_success(self, server: str, database: str):
        """Log successful database connection"""
        self.logger.info(f"✅ Connection successful to {server}, database: {database}")
    
    def log_connection_failure(self, server: str, database: str, error: str):
        """Log failed database connection"""
        self.logger.error(f"❌ Connection failed to {server}, database: {database} - Error: {error}")
    
    def log_query_execution(self, query: str):
        """Log SQL query execution"""
        # Truncate long queries for logging
        query_preview = query[:100] + "..." if len(query) > 100 else query
        self.logger.info(f"📊 Executing query: {query_preview}")
    
    def log_query_result(self, row_count: int, execution_time: float = None):
        """Log query results"""
        msg = f"📈 Query returned {row_count} rows"
        if execution_time:
            msg += f" (execution time: {execution_time:.2f}s)"
        self.logger.info(msg)
    
    def log_msi_config(self, client_id: str = None):
        """Log MSI configuration details"""
        if client_id:
            self.logger.info(f"🔑 Using user-assigned MSI with client ID: {client_id}")
        else:
            self.logger.info("🔑 Using system-assigned MSI")
    
    def get_log_file_path(self) -> str:
        """Get the current log file path"""
        return str(self.log_file)


# Global logger instance
_test_logger = None

def get_test_logger() -> TestLogger:
    """Get or create the global test logger instance"""
    global _test_logger
    if _test_logger is None:
        _test_logger = TestLogger()
    return _test_logger
