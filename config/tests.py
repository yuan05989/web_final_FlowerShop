from django.test import TestCase


class DocsRouteTest(TestCase):
    def test_swagger_available(self):
        response = self.client.get("/swagger/")
        self.assertEqual(response.status_code, 200)

    def test_schema_available(self):
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)
