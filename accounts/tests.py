from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(TestCase):

    def setUp(self):
        self.registration_url = reverse('accounts:register')
        self.user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'testuser@exampletest.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }

    def test_register_page_status_code(self):
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)

    def test_register_form_display(self):
        response = self.client.get(self.registration_url)
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="confirm_password"')

    def test_successful_registration(self):
        response = self.client.post(self.registration_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='testuser@exampletest.com').exists())

    def test_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['confirm_password'] = 'differentpassword'
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")

    #
    def test_registration_existing_email(self):
        User.objects.create_user(
            username='testuser@exampletest.com',
            password='password123'
        )
        response = self.client.post(self.registration_url, self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email already exists.")

    def test_registration_missing_fields(self):
        response = self.client.post(self.registration_url, {
            # 'first_name': '',
            'last_name': 'user',
            'email': 'testuser@exampletest.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")


class UserLoginTests(TestCase):

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='testuser@exampletest.com',
            password='password123'
        )

    def test_login_page_status_code(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_form_display(self):
        response = self.client.get(self.login_url)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser@exampletest.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser@exampletest.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password.")

    def test_login_missing_fields(self):
        response = self.client.post(self.login_url, {
            # 'username': '',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
