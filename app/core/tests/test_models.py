from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTest(TestCase):
    """Contains the test functions for system's models"""
    def sample_user(self):
        email = 'test@teamalif.com'
        password = 'testpass@123'
        return get_user_model().objects.create_user(email=email,
                                                    password=password)

    def test_user_created_with_email(self):
        """Tests if a user is created with the email as identifier"""
        email = "test@teamalif.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """tests if the user's email is all lower caps (normalized)"""
        email = "test@TEAmalif.com"
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEquals(user.email, email.lower())

    def test_user_invalid_email(self):
        """Test creating user with invalid email raises ValueError exception"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """
        Test creating a superuser
        """
        email = "test@teamalif.com"
        user = get_user_model().objects.create_superuser(email, 'test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
            Test the string representation of Tag model
        """
        tag = models.Tag.objects.create(
            user=self.sample_user(),
            name='Vegetable',
        )

        self.assertEqual(str(tag), tag.name)
