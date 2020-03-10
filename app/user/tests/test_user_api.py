from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

        # test user is created
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        # test user has the same password as in payload
        self.assertTrue(user.check_password(payload['password']))

        # test password is not returned in response of self.client.post
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        """
        test creating a user already existing
        """
        payload = {
            'email': 'test@teamalif.com',
            'password': 'pass@123'
        }
        # create a user with the above payload
        create_user(**payload)

        # requesting user creation for the existing email(payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        test the password is greater than 5 chars and user is not created
        in that case
        """
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email='testemail@gmail.'
                                                            'com').exists()

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

    def test_retrieve_user_unauthorized(self):
        """
        test retrieving the user when unauthorized
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """
    Test the user api (private)
    """
    def setUp(self) -> None:
        """prerequisites"""
        self.client = APIClient()
        self.user = create_user(
            email='testemail@teamalif.com',
            password='testpass@123',
            name='Test user',
        )
        self.client.force_authenticate(user=self.user)

    def test_profile_retrieval_authorized(self):
        """
        Test retrieving me profile when logged in
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):
        """
            Test that POST request is not allowed to me url (only PUT
            or PATCH)
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
            Test updating your own profile when authenticated
        """
        payload = {
            'email': 'updatedemail@gmail.com',
            'password': 'updatedpass',
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
