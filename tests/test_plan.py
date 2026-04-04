from app import create_app
from app.models import db, User, Subscription, Plan 
from app.utils.util import encode_token
import unittest 

class TestPlan(unittest.TestCase): 

    def setUp(self): 
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

        with self.app.app_context(): 
            db.drop_all()
            db.create_all()

            self.admin_user = User(
                name = "test_admin",
                email = "admin@gmail.com",
                password = "1234",
                role = "Admin"
            )

            self.normal_user = User(
                name = "test_user",
                email = "user@gmail.com",
                password = "1234",
                role = "user"
            )

            db.session.add(self.admin_user)
            db.session.add(self.normal_user)
            db.session.commit()

            self.admin_id = self.admin_user.id 
            self.user_id = self.normal_user.id

            self.admin_token = encode_token(self.admin_user.id)
            self.user_token = encode_token(self.normal_user.id)

            self.plan = Plan(
                name = "Verizon",
                price = 75,
                billing_cycle = "monthly"
            )

            db.session.add(self.plan)
            db.session.commit()
            self.plan_id = self.plan.id

    def tearDown(self): 
        with self.app.app_context(): 
            db.session.remove()
            db.drop_all()

    def test_create_plan_admin(self):
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        payload = {
            "name": "insurance",
            "price": 400,
            "billing_cycle": "monthly"
        }
        response = self.client.post("/plans/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertEqual(json_data["name"], "insurance")
        self.assertEqual(json_data["price"], 400)
        self.assertEqual(json_data["billing_cycle"], "monthly")

    def test_create_plan_user_unauthorized(self):
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        payload = {
            "name": "insurance",
            "price": 400,
            "billing_cycle": "monthly"
        }
        response = self.client.post("/plans/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Admin only", json_data["message"])

    def test_get_plan_user_valid(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/plans/{self.plan_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["price"], 75)
    
    def test_update_plan_admin(self): 
        updated_payload = {
            "billing_cycle": "weekly"
        }
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.put(f"/plans/{self.plan_id}", json = updated_payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["billing_cycle"], "weekly")
        self.assertEqual(json_data["name"], "Verizon")
    
    def test_update_plan_user_unauthorized(self): 
        updated_payload = {
            "billing_cycle": "weekly"
        }
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.put(f"/plans/{self.plan_id}", json = updated_payload, headers=headers)

        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Admin only", json_data["message"])

    def test_delete_plan_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.delete(f"/plans/{self.plan_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn(f"successfully deleted plan {self.plan_id}", json_data["message"])

    def test_delete_plan_user_unauthorized(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.delete(f"/plans/{self.plan_id}", headers = headers)
        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Admin only", json_data["message"])