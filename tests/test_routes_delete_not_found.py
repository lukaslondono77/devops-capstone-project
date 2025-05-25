import unittest
from service import app
from service.common import status

class TestRoutesDeleteNotFound(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_delete_not_found(self):
        resp = self.client.delete(
            "/accounts/9999",
            json={}, 
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        body = resp.get_json()
        self.assertIn("could not be found", body['message'])

if __name__ == '__main__':  # pragma: no cover
    unittest.main() 