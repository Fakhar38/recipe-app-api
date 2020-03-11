from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """
        Tests for the publicly available Ingredient api
    """
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authorization_required(self):
        """
            Test that authorization is required to access the api
        """
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """
        Tests the ingredient Api for authorized users
    """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testemail@teamalif.com',
            password='testpass123',
        )

        self.client.force_authenticate(self.user)

    def test_get_ingredient_authorized(self):
        """
            Test to get the ingredients for authenticated user
        """
        Ingredient.objects.create(user=self.user, name='Carrot')
        Ingredient.objects.create(user=self.user, name='Ginger')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_ingredient_current_user_only(self):
        """
            Tests if retrieved ingredients are for current user only
        """
        user2 = get_user_model().objects.create_user(
            email='other@teamalif.com',
            password='testpass123',
        )
        Ingredient.objects.create(user=user2, name='Cucumber')

        # Now we create ingredient for current user
        ingredient = Ingredient.objects.create(user=self.user, name='Carrot')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredients_successful(self):
        """
        Test creating an ingredient
        """
        payload = {'name': 'Cucumber'}
        res = self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(user=self.user).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """
        Test creating an invalid ingredient
        """
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(user=self.user,
                                           name=payload['name']).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)
