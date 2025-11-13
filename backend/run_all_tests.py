"""
Run all unit tests for Phase 1
Uses Python's built-in unittest (no external dependencies needed)
"""
import sys
import unittest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
from tests import test_models_unittest, test_content_processor_unittest

def run_tests():
    """Run all unit tests and report results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromModule(test_models_unittest))
    suite.addTests(loader.loadTestsFromModule(test_content_processor_unittest))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    # Return exit code
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED! Ready to continue with Phase 2.\n")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Please fix before continuing.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

