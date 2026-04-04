from app import create_app
from app.models import db, User 
from app.utils.util import encode_token
import unittest 

class TestUser(unittest.TestCase): 

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

            self.admin_token = encode_token(self.admin_user.id)
            self.user_token = encode_token(self.normal_user.id)

    def tearDown(self): 
        with self.app.app_context(): 
            db.session.remove()
            db.drop_all()
    
    def test_create_admin(self): 
        payload = {
            "name": "John Doe",
            "email": "jd@gmail.com",
            "password": "1234",
            "role": "Admin"
        }
        response = self.client.post("/users/", json = payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "John Doe")

    def test_create_normal_user(self): 
        payload = {
            "name": "Jane Doe",
            "email": "janed@gmail.com",
            "password": "1234",
            "role": "User"
        }
        response = self.client.post("/users/", json = payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Jane Doe")
    
    def test_invalid_creation_admin(self): 
        payload = {
            "name": "John Doe",
            "password": "1234",
            "role": "Admin"
        }
        response = self.client.post("/users/", json = payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.get_json())
        self.assertEqual(response.get_json()["email"], ["Missing data for required field."])

    def test_invalid_creation_normal_user(self): 
        payload = {
            "name": "Jane Doe",
            "password": "1234",
            "role": "User"
        }
        response = self.client.post("/users/", json = payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.get_json())
        self.assertEqual(response.get_json()["email"], ["Missing data for required field."])
    
    def test_login_admin(self): 
        credentials = {
            "email": "admin@gmail.com",
            "password": "1234"
        }
        response = self.client.post("/users/login", json = credentials)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("token", json_data)
        
        self.token = json_data["token"]
    
    def test_login_normal_user(self): 
        credentials = {
            "email": "user@gmail.com",
            "password": "1234"
        }
        response = self.client.post("/users/login", json = credentials)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("token", json_data)
        
        self.token = json_data["token"]
    
    def test_invalid_login(self): 
        credentials = {
            "email": "wrong@gmail.com",
            "password": "wrongpass"
        }
        response = self.client.post("/users/login", json = credentials)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid email or password!")

    def test_login_wrong_password(self): 
        credentials = {
            "email": "admin@gmail.com",
            "password": "wrong_password"
        }
        response = self.client.post("/users/login", json = credentials)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid email or password!")

    def test_login_empty_email_password(self): 
        credentials = {
            "email": "",
            "password": "1234"
        }
        response = self.client.post("/users/login", json = credentials)
        self.assertEqual(response.status_code, 404)

        credentials = {
            "email": "admin@gmail.com",
            "password": ""
        }
        response = self.client.post("/users/login", json = credentials)
        self.assertEqual(response.status_code, 404)

        credentials = {
            "email": "",
            "password": ""
        }
        response = self.client.post("/users/login", json = credentials)
        self.assertEqual(response.status_code, 404)

    def test_get_all_users_admin(self): 
        headers = {
            "Authorization": f'Bearer {self.admin_token}'
        }
        response = self.client.get("/users/", headers = headers)
        self.assertEqual(response.status_code, 200)

        users = response.get_json()
        self.assertTrue(len(users)>=1)
        self.assertEqual(users[0]["name"], "test_admin")

    def test_get_all_users_normal_user(self): 
        headers = {
            "Authorization": f'Bearer {self.user_token}'
        }
        response = self.client.get("/users/", headers = headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "Unauthorized access")
    
    def test_get_specific_user_admin(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.get(f"/users/{self.normal_user.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "user@gmail.com")

    def test_get_specific_user_normal_valid(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.get(f"/users/{self.normal_user.id}", headers = headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "user@gmail.com")

    def test_get_specific_user_normal_unauthorized(self): 
        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }      
        response = self.client.get(f"/users/{self.admin_user.id}", headers = headers) 
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "Unauthorized access")

    def test_get_nonexistent_user(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.get("/users/99999", headers = headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid user id")

    def test_update_user_admin(self): 
        self.test_login_admin()

        updated_payload = {
            "name": "Updated Name"
        }
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.put(f"/users/{self.normal_user.id}", json = updated_payload, headers=headers)

        json_data = response.get_json()
        self.assertEqual(json_data["name"], "Updated Name")
        self.assertEqual(json_data["email"], "user@gmail.com")

    def test_update_user_normal_valid(self):
        self.test_login_normal_user()

        updated_payload = {
            "name": "Updated Name"
        }
        headers = {
        "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.put(f"/users/{self.normal_user.id}", json = updated_payload, headers=headers)

        json_data = response.get_json()
        self.assertEqual(json_data["name"], "Updated Name")
        self.assertEqual(json_data["email"], "user@gmail.com")

    def test_update_user_normal_unauthorized(self): 
        self.test_login_normal_user()

        updated_payload = {
            "name": "Updated Name"
        }
        headers = {
        "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.put(f"/users/{self.admin_user.id}", json = updated_payload, headers=headers)

        json_data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "Unauthorized update")

    def test_update_nonexistent_user(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        payload = {
            "name": "Nobody"
        }
        response = self.client.put("/users/99999", json = payload, headers = headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid user id")

    def test_delete_user_admin(self): 
        self.test_login_admin()

        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.delete(f"/users/{self.normal_user.id}", headers = headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"successfully deleted user {self.normal_user.id}", response.get_json()["message"])

    def test_delete_user_normal_valid(self): 
        self.test_login_normal_user()

        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.delete(f"/users/{self.normal_user.id}", headers = headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"successfully deleted user {self.normal_user.id}", response.get_json()["message"])

    def test_delete_user_normal_unauthorized(self): 
        self.test_login_normal_user()

        headers = {
            "Authorization": f"Bearer {self.user_token}"
        }
        response = self.client.delete(f"/users/{self.admin_user.id}", headers = headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "Unauthorized deletion")

    def test_delete_nonexistent_user(self): 
        headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }
        response = self.client.delete("/users/99999", headers = headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid user id")
