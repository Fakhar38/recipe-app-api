from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer

from core.models import Recipe


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """
        Created a sample recipe objects for the given user
    """
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00,
    }

    # to update or add in defaults with given value (params)
    defaults.update(params)

    Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """
    Test for the publicly available api
    """
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """
            Test that request fails when unauthorized
        """
        res = self.client.post(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
        Tests for authorized users
    """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testemail@teamalif.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_recipe_successful(self):
        """
        Tests retrieving the recipe when user is authorized
        """
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_retrieved_for_current_auth_user_only(self):
        """
            Test that recipe objects are retrieved for current authorized user
            only
        """
        user2 = get_user_model().objects.create_user(
            email='other@email.com',
            password='otherpass',
        )
        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
