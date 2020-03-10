from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """
    View for the Create User Serializer
    """
    serializer_class = UserSerializer


class CreateAuthTokenView(ObtainAuthToken):
    """
    View for the serializer to create a token
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManagerUserApiView(generics.RetrieveUpdateAPIView):
    """
        View to manage the user profile
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
            returns the object (model) instance of the current authenticated user
        """
        return self.request.user
