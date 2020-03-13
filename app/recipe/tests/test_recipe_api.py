from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

from core.models import Recipe, Tag, Ingredient


RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """
    Creates and return url of detail of the recipe
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Vegetable'):
    """
    Create and return a Tag objects
    """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Carrot'):
    """
    Create and return an Ingredient objects
    """
    return Ingredient.objects.create(user=user, name=name)


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

    return Recipe.objects.create(user=user, **defaults)


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


# noinspection DuplicatedCode
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

    def test_view_recipe_detail(self):
        """
        Test viewing the detail of a recipe objects
        """
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = recipe_detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_simple_recipe(self):
        """
        Test for creating the recipe without tags and ingredients
        """
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': 7.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        Test creating the recipe with tags
        """
        tag1 = sample_tag(self.user)
        tag2 = sample_tag(self.user)
        payload = {
            'title': 'Test Recipe',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 50,
            'price': 40,
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
        Test for creating the recipe with ingredients
        """
        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user)
        payload = {
            'title': 'Sample Recipe',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 50,
            'price': 50,
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_recipe_update(self):
        """
            Test updating the recipe with patch request
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(self.user))

        new_tag = sample_tag(user=self.user, name='Curry')

        # payload to update the recipe
        payload = {
            'title': 'Chicken tikka',
            'tags': [new_tag.id]
        }
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_recipe_total_update(self):
        """
            Test updating the recipe with put request
        """
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))

        payload = {
            'title': 'Chicken Tikka',
            'time_minutes': 40,
            'price': 100,
        }
        url = recipe_detail_url(recipe.id)

        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
