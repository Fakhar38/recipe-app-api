import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def get_recipe_image_file_path(instance, filename):
    """
        Generates a path to the actual file after uuid operation
    """
    extension = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{extension}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):
    """
    A user manager that provides helper functions to created users
    """

    def create_user(self, email, password, **extra_fields):
        """
        Function to create a user
        """
        if not email:
            raise ValueError("Please provide an valid email address")
        email = self.normalize_email(email)   # makes the email all lower caps
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        creates a superuser for the system
        """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model that supports email authentication instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """
        Model to store tags for the recipes
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """
            string representation of tags
        """
        return self.name


class Ingredient(models.Model):
    """
        Model to store recipe ingredients
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """
            string representation of ingredients
        """
        return self.name


class Recipe(models.Model):
    """
        Recipe models
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    # price = models.FloatField(max_digits=5, decimal_places=2)
    price = models.FloatField(max_length=5)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=get_recipe_image_file_path)

    def __str__(self):
        return self.title
