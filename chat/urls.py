from django.urls import path
from .views import send_message,protected_view

urlpatterns = [
    path('sendMessage', send_message, name='sendMessage'),
    path('protect', protected_view, name='protectedView'),
]
