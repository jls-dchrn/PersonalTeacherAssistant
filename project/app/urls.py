from . import views
from django.urls import path

urlpatterns = [
    # path('user/', views.user_view, name='user'),
    path('user/', views.UserView.as_view(), name='user'),
]