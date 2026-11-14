from django.urls import path
from .views import compare
urlpatterns = [path("experiments/compare/", compare, name="compare")]
