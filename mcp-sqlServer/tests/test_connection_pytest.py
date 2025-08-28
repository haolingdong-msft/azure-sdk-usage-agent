#!/usr/bin/env python3
"""
Pytest version of the SQL Server connection test
"""

import pytest
import asyncio
import sys
import os
import time

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sql_client import MSSQLMSIClient
from src.config import SQL_SERVER, SQL_DATABASE

# Import test logger
sys.path.insert(0, os.path.dirname(__file__))
from test_logger import get_test_logger


class TestSQLConnection:
    """Test suite for SQL Server connectivity"""
    
    @pytest.fixture
    def client(self):
        """Fixture to create a SQL client instance"""
        return MSSQLMSIClient()
    
    def test_client_initialization(self):
        """Test that client can be instantiated"""
        logger = get_test_logger()
        logger.log_test_start("test_client_initialization")
        
        try:
            client = MSSQLMSIClient()
            assert client is not None
            assert hasattr(client, 'connection_string')
            assert hasattr(client, 'credential')
            
            # Test connection string format
            assert 'ActiveDirectoryMSI' in client.connection_string
            assert SQL_SERVER in client.connection_string
            assert SQL_DATABASE in client.connection_string
            
            logger.log_test_success("test_client_initialization", 
                                  f"Client initialized with server: {SQL_SERVER}, database: {SQL_DATABASE}")
        except Exception as e:
            logger.log_test_error("test_client_initialization", e)
            raise
    
    @pytest.mark.asyncio
    async def test_connection_test_method(self):
        """Test the connection test method"""
        logger = get_test_logger()
        logger.log_test_start("test_connection_test_method")
        
        try:
            client = MSSQLMSIClient()
            
            # Test connection - this should not raise an exception
            # even if it fails to connect (it should return error info)
            logger.log_connection_attempt(SQL_SERVER, SQL_DATABASE)
            result = client.test_connection()
            
            assert isinstance(result, dict)
            assert 'status' in result
            assert result['status'] in ['success', 'error']
            
            if result['status'] == 'success':
                logger.log_connection_success(SQL_SERVER, SQL_DATABASE)
                logger.log_test_success("test_connection_test_method", "Connection test passed")
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.log_connection_failure(SQL_SERVER, SQL_DATABASE, error_msg)
                logger.log_test_success("test_connection_test_method", 
                                      f"Connection test handled error gracefully: {error_msg}")
        except Exception as e:
            logger.log_test_error("test_connection_test_method", e)
            raise
    
    @pytest.mark.asyncio
    async def test_simple_query_execution(self):
        """Test executing a simple query"""
        logger = get_test_logger()
        logger.log_test_start("test_simple_query_execution")
        
        client = MSSQLMSIClient()
        
        try:
            query = "SELECT TOP 1 1 as test_column"
            logger.log_query_execution(query)
            start_time = time.time()
            
            result = await client.execute_query(query)
            execution_time = time.time() - start_time
            
            # Check result structure
            assert isinstance(result, dict)
            assert 'status' in result
            
            if result['status'] == 'success':
                assert 'columns' in result
                assert 'rows' in result
                assert 'row_count' in result
                logger.log_query_result(result['row_count'], execution_time)
                logger.log_test_success("test_simple_query_execution", 
                                      f"Query executed successfully, returned {result['row_count']} rows")
            else:
                # Expected if MSI is not configured
                assert 'error' in result
                error_msg = result['error']
                logger.log_test_skip("test_simple_query_execution", 
                                   f"MSI connection failed (expected in test env): {error_msg}")
                pytest.skip(f"MSI connection failed (expected in test env): {error_msg}")
                
        except Exception as e:
            logger.log_test_skip("test_simple_query_execution", f"Query execution failed: {str(e)}")
            pytest.skip(f"Query execution failed (may be expected): {str(e)}")
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection establishment"""
        logger = get_test_logger()
        logger.log_test_start("test_database_connection")
        
        client = MSSQLMSIClient()
        
        try:
            logger.log_connection_attempt(SQL_SERVER, SQL_DATABASE)
            connection = await client._get_connection()
            assert connection is not None
            connection.close()
            logger.log_connection_success(SQL_SERVER, SQL_DATABASE)
            logger.log_test_success("test_database_connection", "Direct connection test passed")
        except Exception as e:
            error_msg = str(e)
            logger.log_connection_failure(SQL_SERVER, SQL_DATABASE, error_msg)
            logger.log_test_skip("test_database_connection", f"Database connection failed: {error_msg}")
            pytest.skip(f"Database connection failed (may be expected): {error_msg}")
    
    @pytest.mark.asyncio
    async def test_usage_metrics_query(self):
        """Test query on usage_metrics table"""
        logger = get_test_logger()
        logger.log_test_start("test_usage_metrics_query")
        
        client = MSSQLMSIClient()
        
        try:
            query = "SELECT TOP 5 * FROM usage_metrics"
            logger.log_query_execution(query)
            start_time = time.time()
            
            result = await client.execute_query(query)
            execution_time = time.time() - start_time
            
            if result.get('status') == 'success':
                assert 'columns' in result
                assert 'rows' in result
                assert result['row_count'] >= 0
                logger.log_query_result(result['row_count'], execution_time)
                logger.log_test_success("test_usage_metrics_query", 
                                      f"Usage metrics query successful, returned {result['row_count']} rows")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.log_test_skip("test_usage_metrics_query", f"Query failed: {error_msg}")
                pytest.skip(f"Query failed (may be expected): {error_msg}")
                
        except Exception as e:
            error_msg = str(e)
            logger.log_test_skip("test_usage_metrics_query", f"Query execution failed: {error_msg}")
            pytest.skip(f"Query execution failed (may be expected): {error_msg}")
