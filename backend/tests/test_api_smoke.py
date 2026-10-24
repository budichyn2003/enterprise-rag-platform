import base64
import os
import tempfile
import unittest
import uuid
from pathlib import Path

_TEST_DATABASE = (
    Path(tempfile.gettempdir()) / f"enterprise-rag-tests-{uuid.uuid4().hex}.db"
)
os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///"
    + _TEST_DATABASE.as_posix()
)
os.environ["APP_ENV"] = "development"
os.environ["MOCK_AUTH_ENABLED"] = "true"

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


class ApiSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()
        self.admin_headers = {"X-Mock-Role": "admin"}

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_mock_upload_chat_feedback_and_handoff(self):
        content = b"Pengembalian dana tersedia dalam empat belas hari kalender."
        upload = self.client.post(
            "/api/documents/upload",
            headers=self.admin_headers,
            json={
                "filename": "../../refund-policy.md",
                "content_base64": base64.b64encode(content).decode("ascii"),
                "metadata": {
                    "source_type": "upload",
                    "category": "returns",
                    "language": "id",
                    "product": "general",
                    "region": "global",
                    "sensitivity": "public",
                },
            },
        )
        self.assertEqual(upload.status_code, 200, upload.text)
        self.assertEqual(upload.json()["status"], "indexed")

        chat = self.client.post(
            "/api/chat",
            json={
                "message": "Bagaimana pengembalian dana? Email alice@example.com",
                "language": "id",
            },
        )
        self.assertEqual(chat.status_code, 200, chat.text)
        answer = chat.json()
        self.assertTrue(answer["citations"])
        self.assertTrue(answer["message_id"])

        feedback = self.client.post(
            f"/api/chat/{answer['session_id']}/feedback",
            json={"message_id": answer["message_id"], "rating": 5},
        )
        self.assertEqual(feedback.status_code, 200, feedback.text)
        search = self.client.get(
            "/api/analytics/conversations?q=alice%40example.com",
            headers=self.admin_headers,
        )
        self.assertNotIn(
            answer["session_id"],
            [item["session_id"] for item in search.json()["items"]],
        )

        handoff = self.client.post(
            f"/api/chat/{answer['session_id']}/handoff",
            json={"reason": "customer_requested"},
        )
        self.assertEqual(handoff.status_code, 200, handoff.text)
        self.assertEqual(handoff.json()["status"], "open")

    def test_admin_routes_require_demo_role_and_validate_upload(self):
        self.assertEqual(self.client.get("/api/documents").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/api/documents/upload",
                headers={"X-Mock-Role": "viewer"},
                json={
                    "filename": "safe.md",
                    "content_base64": base64.b64encode(b"safe test").decode("ascii"),
                },
            ).status_code,
            403,
        )
        malformed = self.client.post(
            "/api/documents/upload",
            headers=self.admin_headers,
            json={"filename": "invalid.pdf", "content_base64": "bm90IGEgcGRm"},
        )
        self.assertEqual(malformed.status_code, 422)

    def test_reports_export_csv_and_add_security_headers(self):
        response = self.client.get("/api/analytics/export.csv", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.text.startswith("session_id,status,language"))
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")

    def test_customer_can_resolve_and_delete_session_data(self):
        chat = self.client.post(
            "/api/chat",
            json={"message": "Bagaimana pengiriman?", "language": "id"},
        )
        self.assertEqual(chat.status_code, 200, chat.text)
        session_id = chat.json()["session_id"]
        resolved = self.client.post(f"/api/chat/{session_id}/resolve")
        self.assertEqual(resolved.json()["status"], "resolved")
        removed = self.client.delete(f"/api/chat/{session_id}")
        self.assertEqual(removed.json()["status"], "deleted")
        transcripts = self.client.get(
            "/api/analytics/conversations",
            headers=self.admin_headers,
        )
        self.assertNotIn(session_id, [item["session_id"] for item in transcripts.json()["items"]])

    def test_mock_admin_access_fails_closed_outside_development(self):
        original_environment = settings.APP_ENV
        try:
            settings.APP_ENV = "production"
            response = self.client.get("/api/documents", headers=self.admin_headers)
            self.assertEqual(response.status_code, 503)
        finally:
            settings.APP_ENV = original_environment

    def test_document_version_rollback_delete_and_mock_connector_idempotency(self):
        upload = self.client.post(
            "/api/documents/upload",
            headers=self.admin_headers,
            json={
                "filename": "policy.md",
                "content_base64": base64.b64encode(b"Old refund policy content.").decode("ascii"),
                "metadata": {"source_type": "upload", "category": "returns", "language": "id"},
            },
        )
        self.assertEqual(upload.status_code, 200, upload.text)
        document_id = upload.json()["document_id"]
        updated = self.client.patch(
            f"/api/documents/{document_id}",
            headers=self.admin_headers,
            json={"title": "Updated refund policy"},
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        versions = self.client.get(
            f"/api/documents/{document_id}/versions",
            headers=self.admin_headers,
        )
        self.assertEqual([item["version"] for item in versions.json()], [2, 1])
        rollback = self.client.post(
            f"/api/documents/{document_id}/rollback/1",
            headers=self.admin_headers,
        )
        self.assertEqual(rollback.status_code, 200, rollback.text)
        removed = self.client.delete(
            f"/api/documents/{document_id}",
            headers=self.admin_headers,
        )
        self.assertEqual(removed.json()["status"], "deleted")

        first_sync = self.client.post(
            "/api/documents/sync/confluence",
            headers=self.admin_headers,
        )
        second_sync = self.client.post(
            "/api/documents/sync/confluence",
            headers=self.admin_headers,
        )
        self.assertEqual(first_sync.status_code, 200, first_sync.text)
        self.assertEqual(len(first_sync.json()["documents_created"]), 1)
        self.assertEqual(second_sync.json()["documents_created"], [])

    def test_bot_configuration_restricts_retrieval_categories(self):
        configured = {
            "confidence_threshold": 0.35,
            "max_context_chunks": 4,
            "allowed_topics": ["shipping"],
        }
        saved = self.client.put(
            "/api/admin/config",
            headers=self.admin_headers,
            json=configured,
        )
        self.assertEqual(saved.status_code, 200, saved.text)
        try:
            response = self.client.post(
                "/api/chat",
                json={"message": "Bagaimana pengembalian dana?", "language": "id"},
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertTrue(response.json()["needs_escalation"])
            self.assertEqual(response.json()["citations"], [])
        finally:
            self.client.put(
                "/api/admin/config",
                headers=self.admin_headers,
                json={
                    "confidence_threshold": 0.35,
                    "max_context_chunks": 4,
                    "allowed_topics": ["returns", "shipping", "support", "accounts", "billing"],
                },
            )


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    for path in (_TEST_DATABASE, Path(f"{_TEST_DATABASE}-wal"), Path(f"{_TEST_DATABASE}-shm")):
        path.unlink(missing_ok=True)
