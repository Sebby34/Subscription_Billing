from app import create_app
from app.models import db, User, Plan, Subscription, Payment 
from app.utils.util import encode_token
import unittest 
from datetime import date

class TestPayment(unittest.TestCase): 

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
            self.plan_price = self.plan.price

            self.subscription = Subscription(
                user_id = self.normal_user.id,
                plan_id = self.plan.id,
                status = "active"
            )

            db.session.add(self.subscription)
            db.session.commit()
            self.subscription_id = self.subscription.id

            self.payment = Payment(
                subscription_id = self.subscription.id,
                amount = self.plan.price,
                payment_date = date(2026, 4, 5)
            )

            db.session.add(self.payment)
            db.session.commit()
            self.payment_id = self.payment.id

    def tearDown(self): 
        with self.app.app_context(): 
            db.session.remove()
            db.drop_all()

    def test_create_payment_admin(self):
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        payload = {
            "subscription_id": self.subscription_id,
            "amount": self.plan_price,
            "payment_date": "2026-04-05"
        }
        response = self.client.post("/payments/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertEqual(json_data["subscription_id"], self.subscription_id)
        self.assertEqual(json_data["amount"], self.plan_price)
        self.assertTrue(json_data["payment_date"].startswith("2026-04-05"))

    def test_create_payment_user_valid(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        payload = {
            "subscription_id": self.subscription_id,
            "amount": self.plan_price,
            "payment_date": "2026-04-05"
        }
        response = self.client.post("/payments/", json = payload, headers = headers)

        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertEqual(json_data["subscription_id"], self.subscription_id)
        self.assertEqual(json_data["amount"], self.plan_price)
        self.assertTrue(json_data["payment_date"].startswith("2026-04-05"))

    def test_get_all_payments_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.get(f"/payments/", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIsInstance(json_data, list)
        self.assertGreaterEqual(len(json_data), 1)
        self.assertEqual(json_data[0]["amount"], self.plan_price )
    
    def test_get_all_payments_user_unauthorized(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/payments/", headers = headers)
        self.assertEqual(response.status_code, 403)
        json_data = response.get_json()
        self.assertIn("Admin only", json_data["message"])

    def test_get_payment_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.get(f"/payments/{self.payment_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["amount"], self.plan_price)
   
    def test_get_payment_user_valid(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/payments/{self.payment_id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["amount"], self.plan_price)


    