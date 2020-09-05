from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<int:id>", views.listingpage, name="listingpage"),
    path("comments", views.comment, name="comment"),
    path("bids", views.bid, name="bid"),
    path("addtowatch", views.addtowatch, name="addtowatch"),
    path("removewatch", views.removewatch, name="removewatch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close", views.close, name="close"),
    path("win", views.win, name="win"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category")
]
