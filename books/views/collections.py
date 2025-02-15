from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Collection, Book
from ..serializers import CollectionSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_collection(request):
    """Create a new collection for the authenticated user."""
    name = request.data.get("name")
    
    if not name:
        return Response({"error": "Collection name is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if Collection.objects.filter(user=request.user, name=name).exists():
        return Response({"error": "Collection with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

    collection = Collection.objects.create(user=request.user, name=name)
    return Response(CollectionSerializer(collection).data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_collection(request, collection_id):
    """Delete a collection (except the default 'Favourites')."""
    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        if collection.name == "Favourites":
            return Response({"error": "Cannot delete the default 'Favourites' collection."}, status=status.HTTP_400_BAD_REQUEST)

        collection.delete()
        return Response({"message": "Collection deleted successfully."}, status=status.HTTP_200_OK)

    except Collection.DoesNotExist:
        return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_book_to_collection(request, collection_id):
    """Add a book to a user's collection."""
    book_id = request.data.get("book_id")

    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        book = Book.objects.get(id=book_id)

        collection.books.add(book)
        return Response({"message": f"Book '{book.title}' added to '{collection.name}' collection."}, status=status.HTTP_200_OK)

    except Collection.DoesNotExist:
        return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
    except Book.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_book_from_collection(request, collection_id):
    """Remove a book from a user's collection."""
    book_id = request.data.get("book_id")

    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        book = Book.objects.get(id=book_id)

        if book not in collection.books.all():
            return Response({"error": "Book is not in this collection."}, status=status.HTTP_400_BAD_REQUEST)

        collection.books.remove(book)
        return Response({"message": f"Book '{book.title}' removed from '{collection.name}' collection."}, status=status.HTTP_200_OK)

    except Collection.DoesNotExist:
        return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
    except Book.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
