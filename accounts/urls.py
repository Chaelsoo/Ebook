from django.urls import path
from .views import register_user, login_user, fill_preferences
from rest_framework.authtoken.views import obtain_auth_token
from .views import add_review, edit_review, delete_review, get_book_reviews, get_user_reviews,save_search_query, get_search_history, clear_search_history


urlpatterns = [
    path('register', register_user, name='register'),
    path('login', login_user, name='login'),
    path('api-token-auth', obtain_auth_token, name='api_token_auth'),
    path("fill_preferences/", fill_preferences, name="fill_preferences"),
    path('books/<int:book_id>/reviews/', get_book_reviews, name='book_reviews'),
    path('books/<int:book_id>/review/add/', add_review, name='add_review'),
    path('reviews/<int:review_id>/edit/', edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('reviews/user/', get_user_reviews, name='user_reviews'),
    path('search/save/', save_search_query, name='save_search_query'),
    path('search/history/', get_search_history, name='get_search_history'),
    path('search/clear/', clear_search_history, name='clear_search_history'),
]
