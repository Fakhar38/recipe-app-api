from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Tag

from .serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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
