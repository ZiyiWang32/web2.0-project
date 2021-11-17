from django.urls import path

from . import views
from django.conf.urls import url
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^login/$',views.login),
    url(r"^signup/$", views.signup)
]