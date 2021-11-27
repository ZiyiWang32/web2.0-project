from django.urls import path

from . import views
from django.conf.urls import url
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^index/$',views.index),
    url(r'^login/$',views.login),
    url(r"^signup/$", views.signup),
    url(r"^logout/$", views.logout),
    url(r"^newpost/$", views.newPost),
    url(r"^insertpost/$", views.insertPost),
    url(r"^readpost/$", views.readPost),
    url(r"^newresponse/$", views.newResponse),
    url(r"^likepost/$", views.likePost),
    url(r"^favoritepost/$", views.favoritePost),
    url(r"^dashboard/$", views.dashboard),
    url(r"^addtag/$", views.addTag),
]