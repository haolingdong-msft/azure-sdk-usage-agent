#!/usr/bin/env python3
"""
Test runner script for SQL client tests with different configurations
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMED OUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Main test runner"""
    # Change to the project directory (parent of tests folder)
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    print("🚀 SQL Client Test Runner")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not Path("src/sql_client.py").exists():
        print("❌ Error: sql_client.py not found. Please run this script from the project root or tests folder.")
        return False
    
    # Install test dependencies if needed
    if "--install-deps" in sys.argv:
        print("\n📦 Installing test dependencies...")
        run_command([
            sys.executable, "-m", "pip", "install", "-r", "tests/test_requirements.txt"
        ], "Installing test dependencies")
    
    all_passed = True
    
    if len(sys.argv) > 1 and sys.argv[1] in ["unit", "integration", "all"]:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    if test_type in ["unit", "all"]:
        # Run unit tests (fast, no network)
        success = run_command([
            sys.executable, "-m", "pytest", 
            "tests/test_connection_pytest.py",
            "-m", "not integration",
            "-v"
        ], "Unit Tests (Fast, No Network)")
        all_passed = all_passed and success
    
    if test_type in ["integration", "all"]:
        # Run integration tests (require auth)
        success = run_command([
            sys.executable, "-m", "pytest", 
            "tests/test_connection_pytest.py",
            "-m", "integration",
            "-v"
        ], "Integration Tests (Require Auth)")
        all_passed = all_passed and success
    
    # Run old test for comparison if requested
    if "--compare" in sys.argv:
        print("\n📊 No legacy test available for comparison (removed)")
        print("The current test file contains all improved functionality.")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
SQL Client Test Runner

Usage:
    python run_tests.py [unit|integration|all] [options]

Test Types:
    unit        - Run only unit tests (fast, no network calls)
    integration - Run only integration tests (require MSI auth)
    all         - Run all tests (default)

Options:
    --install-deps  - Install test dependencies first
    --help, -h      - Show this help message

Examples:
    python run_tests.py unit                    # Fast unit tests only
    python run_tests.py integration             # Integration tests only  
    python run_tests.py all --install-deps      # Install deps and run all tests
""")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)
