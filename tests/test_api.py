import os
import tempfile
import unittest
from unittest.mock import patch


database_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
database_file.close()
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_file.name}"

from app import Task, app, db


class TaskApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()

    def create_task(self, **overrides):
        payload = {
            "name": "Prepare report",
            "due_date": "2026-09-10",
            "priority": "HIGH",
            "tag": "WORK",
        }
        payload.update(overrides)
        return self.client.post("/api/tasks", json=payload)

    def test_create_get_update_filter_complete_and_delete_task(self):
        created = self.create_task()
        self.assertEqual(created.status_code, 201)
        task = created.get_json()["task"]
        self.assertEqual(task["tag"], "WORK")

        fetched = self.client.get(f"/api/tasks/{task['id']}")
        self.assertEqual(fetched.status_code, 200)

        updated = self.client.patch(
            f"/api/tasks/{task['id']}", json={"tag": "PERSONAL", "priority": "LOW"}
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["tag"], "PERSONAL")

        self.assertEqual(self.client.get("/api/tasks?tag=WORK").get_json(), [])
        personal = self.client.get("/api/tasks?tag=PERSONAL").get_json()
        self.assertEqual(len(personal), 1)

        completed = self.client.post(f"/api/tasks/{task['id']}/complete")
        self.assertTrue(completed.get_json()["completed"])
        self.assertEqual(self.client.get("/api/tasks").get_json(), [])
        self.assertEqual(len(self.client.get("/api/tasks?completed=true").get_json()), 1)

        deleted = self.client.delete(f"/api/tasks/{task['id']}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get(f"/api/tasks/{task['id']}").status_code, 404)

    def test_rejects_invalid_task_data_and_filters(self):
        response = self.create_task(tag="OTHER")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Invalid task data")

        response = self.create_task(due_date="10/09/2026")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Invalid task data")

        response = self.client.get("/api/tasks?completed=perhaps")
        self.assertEqual(response.status_code, 400)

    def test_complete_all_can_be_filtered_by_tag(self):
        self.create_task(name="Work", tag="WORK")
        self.create_task(name="Home", tag="PERSONAL")

        response = self.client.post("/api/tasks/complete-all?tag=WORK")
        self.assertEqual(response.get_json()["completed_count"], 1)
        remaining = self.client.get("/api/tasks").get_json()
        self.assertEqual([task["name"] for task in remaining], ["Home"])

    @patch("app.print_task_card")
    def test_print_endpoint(self, print_task_card):
        task_id = self.create_task().get_json()["task"]["id"]
        response = self.client.post(f"/api/tasks/{task_id}/print")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["printed"])
        print_task_card.assert_called_once()


if __name__ == "__main__":
    unittest.main()
