# tests/test_error_handlers.py

import unittest
from service import app
from service.common import status
from service.models import DataValidationError
from service.common.error_handlers import request_validation_error

class TestErrorHandlers(unittest.TestCase):
    """Test Cases for all Error Handlers"""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def _get_handler(self, key):
        """
        Retrieve the handler function for either
        an exception class or an HTTP status code.
        """
        spec = self.app.error_handler_spec[None]
        hmap = spec.get(key) or spec.get(type(key))
        # Flask stores a dict of {None: handler_fn}
        return next(iter(hmap.values()))

    def test_request_validation_error(self):
        """DataValidationError → 400"""
        err = DataValidationError("Invalid data")
        rv, code = request_validation_error(err)
        self.assertEqual(code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(rv.json['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(rv.json['error'], "Bad Request")
        self.assertEqual(rv.json['message'], "Invalid data")

    def test_bad_request(self):
        """400 Bad Request handler"""
        err = Exception("Bad request message")
        fn = self._get_handler(status.HTTP_400_BAD_REQUEST)
        rv, code = fn(err)
        self.assertEqual(code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(rv.json['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(rv.json['error'], "Bad Request")
        self.assertEqual(rv.json['message'], "Bad request message")

    def test_not_found(self):
        """404 Not Found handler"""
        err = Exception("Resource not found")
        fn = self._get_handler(status.HTTP_404_NOT_FOUND)
        rv, code = fn(err)
        self.assertEqual(code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(rv.json['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(rv.json['error'], "Not Found")
        self.assertEqual(rv.json['message'], "Resource not found")

    def test_method_not_supported(self):
        """405 Method Not Allowed handler"""
        err = Exception("Method not allowed")
        fn = self._get_handler(status.HTTP_405_METHOD_NOT_ALLOWED)
        rv, code = fn(err)
        self.assertEqual(code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(rv.json['status'], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(rv.json['error'], "Method not Allowed")
        self.assertEqual(rv.json['message'], "Method not allowed")

    def test_mediatype_not_supported(self):
        """415 Unsupported Media Type handler"""
        err = Exception("Unsupported media type")
        fn = self._get_handler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        rv, code = fn(err)
        self.assertEqual(code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(rv.json['status'], status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(rv.json['error'], "Unsupported media type")
        self.assertEqual(rv.json['message'], "Unsupported media type")

    def test_internal_server_error(self):
        """500 Internal Server Error handler"""
        err = Exception("Test error message")
        fn = self._get_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        rv, code = fn(err)
        self.assertEqual(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(rv.json['status'], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(rv.json['error'], "Internal Server Error")
        self.assertEqual(rv.json['message'], "Test error message")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
