from django.test import TestCase


class SimpleTest(TestCase):
    def test_api_hello_returns_ok(self):
        response = self.client.get("/api/hello/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello from Django backend", "status": "ok"})
