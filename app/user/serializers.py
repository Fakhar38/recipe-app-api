from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    # password = serializers.CharField(
    #     style={'input_type': 'password'},
    #     write_only=True,
    #     min_length=5
    # )

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """creates a user object with encrypted password and returns it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Updates the user with encrypted password and returns it"""
        password = self.validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating requests to generate a token
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validates the given credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _("Username or Password is invalid")
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
