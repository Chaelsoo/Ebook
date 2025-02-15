from rest_framework import serializers
from .models import Book, UserBook, Collection

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class UserBookSerializer(serializers.ModelSerializer):
    book = BookSerializer()  # Include book details in the response

    class Meta:
        model = UserBook
        fields = ['book', 'progress']


class CollectionSerializer(serializers.ModelSerializer):
    books = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), many=True, required=False
    )

    class Meta:
        model = Collection
        fields = ['id', 'user', 'name', 'books']
        read_only_fields = ['id', 'user']

