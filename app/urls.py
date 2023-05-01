from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("simdocs", views.simdocs, name="simdocs"),
    path(
        "simdocs_most_frequent_terms",
        views.simdocs_most_frequent_terms,
        name="simdocs_most_frequent_terms",
    ),
]
