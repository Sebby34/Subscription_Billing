from app import create_app
from app.models import db, User, Subscription, Plan 
from app.utils.util import encode_token
import unittest 

class TestSubscription(unittest.TestCase): 

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

            self.subscription = Subscription(
                user_id = self.normal_user.id,
                plan_id = self.plan.id,
                status = "active"
            )

            db.session.add(self.subscription)
            db.session.commit()
            self.subscription_id = self.subscription.id

            self.other_subscription = Subscription( 
                user_id = self.admin_user.id,
                plan_id = self.plan.id,
                status = "active"
            )
            db.session.add(self.other_subscription)
            db.session.commit()
            self.other_subscription_id = self.other_subscription.id

    def tearDown(self): 
        with self.app.app_context(): 
            db.session.remove()
            db.drop_all()

    def test_create_subscription_user(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        payload = {
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "status": "active"
        }
        response = self.client.post("/subscriptions/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertEqual(json_data["user_id"], self.user_id)
        self.assertEqual(json_data["plan_id"], self.plan_id)
        self.assertEqual(json_data["status"], "active")

    def test_create_subscription_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        payload = {
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "status": "active"
        }
        response = self.client.post("/subscriptions/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertEqual(json_data["user_id"], self.user_id)
        self.assertEqual(json_data["plan_id"], self.plan_id)
        self.assertEqual(json_data["status"], "active")

    def test_get_subscription_user_valid(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/subscriptions/{self.subscription_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["user_id"], self.user_id)
    
    def test_get_subscription_user_unauthorized(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/subscriptions/{self.other_subscription_id}", headers = headers)
        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Unauthorized access", json_data["message"])

    def test_get_subscription_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.get(f"/subscriptions/{self.subscription_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["user_id"], self.user_id)
    
    def test_update_subscription_user_valid(self): 
        updated_payload = {
            "status": "Inactive"
        }
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.put(f"/subscriptions/{self.subscription_id}", json = updated_payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "Inactive")
        self.assertEqual(json_data["plan_id"], self.plan_id)

    def test_update_subscription_admin(self): 
        updated_payload = {
            "status": "Inactive"
        }
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.put(f"/subscriptions/{self.subscription_id}", json = updated_payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "Inactive")
        self.assertEqual(json_data["plan_id"], self.plan_id)

    def test_delete_subscription_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.delete(f"/subscriptions/{self.other_subscription_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn(f"successfully deleted subscription {self.other_subscription_id}", response.get_json()["message"])
       
    def test_delete_subscription_user_unauthorized(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.delete(f"/subscriptions/{self.other_subscription_id}", headers = headers)
        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Unauthorized deletion", json_data["message"])