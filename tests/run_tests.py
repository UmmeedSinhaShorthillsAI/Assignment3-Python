#!/usr/bin/env python3
import unittest

# Import all test modules
from tests.test_file_loader import TestFileLoader
from tests.test_data_extractor import TestDataExtractor
from tests.test_storage import TestFileStorage, TestSQLStorage

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFileLoader))
    test_suite.addTest(unittest.makeSuite(TestDataExtractor))
    test_suite.addTest(unittest.makeSuite(TestFileStorage))
    test_suite.addTest(unittest.makeSuite(TestSQLStorage))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)