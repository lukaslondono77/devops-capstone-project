"""
Test Log Handlers
"""
import unittest
import logging
from service import app
from service.common.log_handlers import init_logging

class TestLogHandlers(unittest.TestCase):
    """Test Cases for Log Handlers"""

    def setUp(self):
        """Set up test cases"""
        self.app = app
        self.app.config['TESTING'] = True
        self.logger_name = "test_logger"

    def test_init_logging(self):
        """Test the initialization of logging"""
        # Create a test logger
        test_logger = logging.getLogger(self.logger_name)
        test_logger.setLevel(logging.INFO)
        
        # Add a handler to the test logger
        handler = logging.StreamHandler()
        test_logger.addHandler(handler)
        
        # Initialize logging with the test logger
        init_logging(self.app, self.logger_name)
        
        # Verify the app logger has the same handlers and level
        self.assertEqual(len(self.app.logger.handlers), len(test_logger.handlers))
        self.assertEqual(self.app.logger.level, test_logger.level)
        
        # Verify the formatter was set
        for handler in self.app.logger.handlers:
            self.assertIsInstance(handler.formatter, logging.Formatter)
            self.assertEqual(
                handler.formatter._fmt,
                "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s"
            )
            self.assertEqual(handler.formatter.datefmt, "%Y-%m-%d %H:%M:%S %z")

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 