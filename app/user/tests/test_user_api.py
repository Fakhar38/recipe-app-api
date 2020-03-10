from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """
    creates a user in the user model
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """
    Test the user api (public)
    """
    def setUp(self) -> None:
        """
        doing the prerequisites for the tests
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test user create with valid payload
        """
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpass@123',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)     # test user is created

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))       # test user has the same password as in payload

        self.assertNotIn('password', res.data)  # test password is not returned in response of self.client.post

    def test_user_already_exists(self):
        """
        test creating a user already existing
        """
        payload = {
            'email': 'test@teamalif.com',
            'password': 'pass@123'
        }
        create_user(**payload)      # created a user with the above payload

        res = self.client.post(CREATE_USER_URL, payload)    # requesting user creation for the existing email(payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        test the password is greater than 5 chars and user is not created in that case
        """
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email='testemail@gmail.com').exists()

        self.assertFalse(user_exists)

    def test_create_token(self):
        """
        Test token is generated for a user
        """
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpass@123',
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_password(self):
        """
        Test that token is not generated for invalid password
        """
        create_user(email='testemail@gmail.com', password='testpass@123')
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'wrongpass'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        test that token is not generated for non-existing user
        """
        payload = {
            'email': 'test@gmail.com',
            "password": 'testpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_empty_field(self):
        """
        Test generating a token when any of the fields is empty
        """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)