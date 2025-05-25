import unittest
from service import app
from service.common import status
from service.common.error_handlers import unauthorized

class TestUnauthorizedHandler(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def _get_handler(self, code):
        spec = self.app.error_handler_spec[None]
        hmap = spec.get(code)
        return next(iter(hmap.values()))

    def test_unauthorized(self):
        fn = self._get_handler(status.HTTP_401_UNAUTHORIZED)
        resp, code = fn(Exception("No creds"))
        self.assertEqual(code, status.HTTP_401_UNAUTHORIZED)
        body = resp.get_json()
        self.assertEqual(body['status'], status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(body['error'], "Unauthorized")
        self.assertEqual(body['message'], "No creds")

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 