from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="blogHome"),
    path("blogpost/<int:blogid>", views.blogpost, name="blogPost"),
    path("search/", views.search, name="Search"),
]
