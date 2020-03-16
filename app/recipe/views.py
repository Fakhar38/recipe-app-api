from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Tag, Ingredient, Recipe

from .serializers import TagSerializer,\
                         IngredientSerializer,\
                         RecipeSerializer,\
                         RecipeDetailSerializer,\
                         ImageUploadSerializer


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

    def get_serializer_class(self):
        """
        selects RecipeDetailSerializer as serializer_class when getting details
        of the recipe otherwise returns the parent variable
        """
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return ImageUploadSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        assigns the request's user as the user of the recipe when created
        """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """
            Uploads an image to the recipe app
        """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
