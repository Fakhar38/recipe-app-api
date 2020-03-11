from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Tag, Ingredient

from .serializers import TagSerializer, IngredientSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """
        ViewSet for the tags
    """
    serializer_class = TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        """
            Filters the queryset to the current authorized user only
        :return: Tag objects for current user
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Override the create function to assign current user to the tag
        :param serializer:
        :return: Tag object created for current user
        """
        return serializer.save(user=self.request.user)


class IngredientApiViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin):
    """
    ViewSet for Ingredients
    """
    serializer_class = IngredientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """
            Filters the ingredients for current user only
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')
