from django.urls import path
from .views import register_user, login_user
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('register', register_user, name='register'),
    path('login', login_user, name='login'),
    path('api-token-auth', obtain_auth_token, name='api_token_auth'),

]