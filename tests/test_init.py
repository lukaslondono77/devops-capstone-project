import unittest
from unittest.mock import patch
import sys

class TestServiceInit(unittest.TestCase):
    def test_init_db_failure_exits(self):
        # Patch models.init_db to raise an Exception
        with patch('service.models.init_db', side_effect=Exception('DB fail')):
            # Patch sys.exit to raise SystemExit so we can catch it
            with patch.object(sys, 'exit', side_effect=SystemExit(4)) as mock_exit:
                with self.assertRaises(SystemExit) as cm:
                    # Importing service.__init__ will run the code
                    import importlib
                    importlib.reload(__import__('service.__init__'))
                self.assertEqual(cm.exception.code, 4)
                mock_exit.assert_called_once_with(4)

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 