from django.urls import path
from . import views

app_name = "pat"
urlpatterns = [
    # path('', views.main, name='main'),
    path("pp/", views.portfolio, name="portfolio"),
    path("pp/details/<int:id>", views.details, name="details"),
]
