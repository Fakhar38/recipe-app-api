from rest_framework.routers import DefaultRouter

from . import views

from django.urls import path, include

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientApiViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
