from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Tag, Ingredient, Recipe

from .serializers import TagSerializer,\
                         IngredientSerializer,\
                         RecipeSerializer


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """
    Base ViewSet for Tags and Ingredients as they contain much common funcs
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Returns objects for current user only
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Allocates the current user as user when creating objects
        """
        return serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """
        ViewSet for the tags
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientApiViewSet(BaseRecipeAttrViewSet):
    """
    ViewSet for Ingredients
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """
        ViewSet for the Recipe api
    """
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
