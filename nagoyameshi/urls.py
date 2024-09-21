from django.urls import path
from . import views

app_name    = "nagoyameshi"
urlpatterns = [
    path('', views.index, name="index"),
]
