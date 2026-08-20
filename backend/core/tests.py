from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase

User = get_user_model()


class SimpleTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.readonly_user = User.objects.create_user(
            username="readonly_user",
            password="readonly-pass-123",
        )
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            password="admin-pass-123",
        )

    def test_api_hello_returns_ok(self):
        response = self.client.get("/api/v1/hello/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello from Django backend", "status": "ok"})

    def test_readonly_user_can_read_but_not_mutate_feature_flags(self):
        self.client.force_authenticate(user=self.readonly_user)

        read_response = self.client.get("/api/v1/statsigfeatureflag")
        create_response = self.client.post(
            "/api/v1/statsigfeatureflag",
            {
                "product": "demo",
                "environment": "dev",
                "last_checksum": "abc",
            },
            format="json",
        )
        update_response = self.client.put(
            "/api/v1/statsigfeatureflag/1",
            {
                "product": "demo",
                "environment": "dev",
                "last_checksum": "updated",
            },
            format="json",
        )

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

    def test_admin_user_can_create_feature_flags(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/v1/statsigfeatureflag",
            {
                "product": "demo",
                "environment": "dev",
                "last_checksum": "abc",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_admin_can_grant_readonly_user_scoped_write_token(self):
        self.client.force_authenticate(user=self.admin_user)
        grant_response = self.client.post(
            "/api/token/grant/",
            {
                "username": "readonly_user",
                "operations": ["POST"],
                "duration": "24h",
            },
            format="json",
        )

        self.assertEqual(grant_response.status_code, 200)
        self.assertEqual(grant_response.json()["operations"], ["POST"])

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {grant_response.json()['access']}"
        )
        response = self.client.post(
            "/api/v1/statsigfeatureflag",
            {
                "product": "scoped-demo",
                "environment": "dev",
                "last_checksum": "abc",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
