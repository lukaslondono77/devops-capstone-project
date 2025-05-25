import runpy
import unittest

class TestStatusMain(unittest.TestCase):
    def test_main_guard(self):
        # Executes the module under the "__main__" name,
        # which will hit that `if __name__ == '__main__': pass` line.
        runpy.run_module('service.common.status', run_name='__main__')

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 