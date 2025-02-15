from django.contrib.auth import authenticate, login
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from chat.models import Chat  
from books.models import Collection
from .models import UserProfile, Review, Book,SearchHistory
from django.shortcuts import get_object_or_404
from .serializers import ReviewSerializer,SearchHistorySerializer



@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Create associated models for the new user
        chat = Chat.objects.create(user=user)
        fav = Collection.objects.create(user=user, name="Favourites")
        profile = UserProfile.objects.create(user=user)  # Initialize UserProfile

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data  # Assuming LoginSerializer returns the user
        login(request, user)  # Logs the user in
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fill_preferences(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    # Get categories from request body
    categories = request.data.get('categories', [])
    age = request.data.get('age', 20)

    if not isinstance(categories, list):
        return Response({"error": "Categories should be a list of strings."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's preferences with new categories
    user_profile.preferences = categories
    user_profile.age = age
    user_profile.save()

    return Response({"message": "Preferences updated successfully", "preferences": user_profile.preferences}, status=status.HTTP_200_OK)













#REVIEWS 
# Add a review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    # Prevent duplicate reviews
    if Review.objects.filter(user=request.user, book=book).exists():
        return Response({"error": "You have already reviewed this book."}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    serializer = ReviewSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save(user=request.user, book=book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Edit a review
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response({"error": "Review not found or not owned by you"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a review
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response({"error": "Review not found or not owned by you"}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return Response({"message": "Review deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Get all reviews for a book
@api_view(['GET'])
def get_book_reviews(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    reviews = Review.objects.filter(book=book)
    serializer = ReviewSerializer(reviews, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# Get all reviews by a user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reviews(request):
    reviews = Review.objects.filter(user=request.user)
    serializer = ReviewSerializer(reviews, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

















#AI
def get_user_data(user):
    profile = user.profile
    favorite_books = [{"title": book.title, "genre": book.genre} for book in profile.favorite_books.all()]
    reading_history = [{"title": book.title, "genre": book.genre} for book in profile.reading_history.all()]
    search_history = [{"query": s.query, "timestamp": s.timestamp} for s in user.search_history.all()]
    reviews = [{"title": r.book.title, "rating": r.rating, "comment": r.comment} for r in user.reviews.all()]
    screen_time = [st.to_dict() for st in user.screen_time.all()]

    return {
        "user_id": user.id,
        "age": profile.age,  # Add age field in UserProfile
        "preferred_genres": profile.preferred_genres.split(",") if profile.preferred_genres else [],
        "favorite_books": favorite_books,
        "reading_history": reading_history,
        "search_history": search_history,
        "reviews": reviews,
        "screen_time": screen_time
        # "search_history": search_history,
    }

# Store a search query
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_search_query(request):
    query = request.data.get("query", "").strip()

    if not query:
        return Response({"error": "Search query cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

    search_entry = SearchHistory.objects.create(user=request.user, query=query)
    return Response({"message": "Search saved", "query": query}, status=status.HTTP_201_CREATED)

# Get user search history
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')  # Latest first
    serializer = SearchHistorySerializer(searches, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Clear search history
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_search_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return Response({"message": "Search history cleared"}, status=status.HTTP_204_NO_CONTENT)
