from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminTests(TestCase):

    def setUp(self) -> None:
        """Sets Up the pre-requisites for tests"""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@teamalif.com',
            password='test123',
            name='Test User'
        )
        self.admin = get_user_model().objects.create_superuser(
            'admin@teamalif.com',
            'test@123'
        )
        self.client.force_login(self.admin)

    def test_users_listed(self):
        """Tests if admin page lists users of the system"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)  # res = response

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """Tests if user change page is available"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)

    def test_create_user_page(self):
        """Test if the create user page exists"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)
