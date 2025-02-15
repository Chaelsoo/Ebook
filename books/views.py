from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Book, UserBook, Collection  
from .serializers import BookSerializer, UserBookSerializer, CollectionSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_landing(request):
    
    # Fetch books in user's library with progress < 100
    user_books = UserBook.objects.filter(user=request.user, progress__lt=100)
    user_books_serializer = UserBookSerializer(user_books, many=True)

    # Fetch all books with optional category filtering
    category = request.query_params.get('category', None)
    books = Book.objects.all()
    
    if category:
        books = books.filter(categories__icontains=category)  # Adjust this based on category storage

    all_books_serializer = BookSerializer(books, many=True)

    return Response({
        "user_library": user_books_serializer.data,
        "all_books": all_books_serializer.data
    }, status=status.HTTP_200_OK)  


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favourite_books(request):
    try:
        favourites_collection = Collection.objects.get(user=request.user, name="Favourites")
        favourite_books = favourites_collection.books.all()

        user_owned_books = set(UserBook.objects.filter(user=request.user).values_list('book_id', flat=True))

        serialized_books = BookSerializer(favourite_books, many=True).data
        for book in serialized_books:
            book["owned"] = book["id"] in user_owned_books

        return Response(serialized_books, status=status.HTTP_200_OK)

    except Collection.DoesNotExist:
        return Response({"error": "Favourites collection not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_books_in_progress(request):
    
    in_progress_books = UserBook.objects.filter(user=request.user)
    serialized_books = UserBookSerializer(in_progress_books, many=True)

    return Response(serialized_books.data, status=status.HTTP_200_OK)






#COLLECTIONS 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_collections(request):
    """Fetch all collections for the authenticated user."""
    collections = Collection.objects.filter(user=request.user)
    serializer = CollectionSerializer(collections, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_collection(request):
    """Create a new book collection for the user."""
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Collection name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    collection = Collection.objects.create(user=request.user, name=name)
    return Response(CollectionSerializer(collection).data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_collection(request):
    """Delete a collection by ID."""
    collection_id = request.data.get('collection_id')
    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        collection.delete()
        return Response({'message': 'Collection deleted successfully'}, status=status.HTTP_200_OK)
    except Collection.DoesNotExist:
        return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_book_to_collection(request):
    """Add a book to a collection."""
    collection_id = request.data.get('collection_id')
    book_id = request.data.get('book_id')

    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        book = Book.objects.get(id=book_id)
        collection.books.add(book)
        return Response({'message': 'Book added to collection'}, status=status.HTTP_200_OK)
    except Collection.DoesNotExist:
        return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_book_from_collection(request):
    """Remove a book from a collection."""
    collection_id = request.data.get('collection_id')
    book_id = request.data.get('book_id')

    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        book = Book.objects.get(id=book_id)
        collection.books.remove(book)
        return Response({'message': 'Book removed from collection'}, status=status.HTTP_200_OK)
    except Collection.DoesNotExist:
        return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)