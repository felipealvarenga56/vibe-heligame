#!/usr/bin/env python3
"""
Test runner for vibe-heligame
Run all tests or specific test modules
"""

import sys
import os
import unittest

def run_all_tests():
    """Run all tests in the tests directory"""
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run specific test
    test_module = f"tests.{test_name}"
    suite = unittest.TestLoader().loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        
        print(f"Running specific test: {test_name}")
        success = run_specific_test(test_name)
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()