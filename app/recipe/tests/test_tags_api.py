from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer
from core.models import Tag


TAG_URL = reverse('recipe:tag-list')


class PublicTagApiTest(TestCase):
    """
        Test the publicly available tags API
    """
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_tags_unauthorized(self):
        """
            Test if tags are retrieved for unauthorized users
        """
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """
        Test the tags api for authorized users
    """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testemail@teamalif.com',
            password='testpass@123',
        )

        self.client.force_authenticate(self.user)

    def test_tag_api_for_authorized_user(self):
        """
            Test retrieving tags for an authorized user
        :return: Tag object
        """
        Tag.objects.create(user=self.user, name='Vegetable')
        Tag.objects.create(user=self.user, name='Chicken')

        res = self.client.get(TAG_URL)

        tag = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tag, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_retrieved_for_auhtorized_user_only(self):
        """
            Test if tags returned are for the current authorized user only
        :return: Tag object
        """
        user2 = get_user_model().objects.create_user(
            email='other@teamalif.com',
            password='testpass233',
        )
        Tag.objects.create(user=user2, name='Vegetable')
        tag = Tag.objects.create(user=self.user, name='Chicken')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """
        Test creating a tag successfully
        :return: Tag object created for the current authenticated user
        """
        payload = {'name': 'new_tag'}

        res = self.client.post(TAG_URL, payload)
        exists = Tag.objects.filter(user=self.user).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """
        Test creating the tag with invalid payload
        :return: 400 Bad request
        """
        payload = {'name': ''}

        res = self.client.post(TAG_URL, payload)
        exists = Tag.objects.filter(user=self.user).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)
