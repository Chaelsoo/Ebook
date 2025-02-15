from django.urls import path
from .views import get_landing
from .views import (
    create_collection,
    delete_collection,
    add_book_to_collection,
    remove_book_from_collection,
    get_user_collections
)

urlpatterns = [
    path('landing', get_landing, name='landing'),
    path('collection', get_user_collections, name='collection'),
    path('collection/add', create_collection, name='collection_add'),
    path('collection/remove', delete_collection, name='collection_remove'),
    path('collection/add-book', add_book_to_collection, name='collection_add_book'),
    path('collection/remove-book', remove_book_from_collection, name='collection_remove_book'),
]