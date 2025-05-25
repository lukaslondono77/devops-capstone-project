import importlib
import sys
import unittest
from unittest.mock import patch

class TestServiceInitSuccess(unittest.TestCase):
    def test_init_db_success(self):
        # Patch init_db so it doesn't raise
        with patch('service.models.init_db', return_value=None):
            called = []
            # Patch sys.exit so it just records calls
            with patch.object(sys, 'exit', side_effect=lambda code: called.append(code)):
                # Reload the package (which runs the top-level init logic)
                import service
                importlib.reload(service)
            # sys.exit should never have been invoked
            self.assertEqual(called, [])

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 