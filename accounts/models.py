from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.IntegerField(blank=True, null=True)
    favorite_books = models.ManyToManyField(Book, related_name="favorited_by", blank=True)
    reading_history = models.ManyToManyField(Book, related_name="read_by", blank=True)
    preferred_genres = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating} stars)"


# class Wishlist(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
#     books = models.ManyToManyField(Book, related_name='wishlisted_by')

#     def __str__(self):
#         return f"Wishlist of {self.user.username}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    query = models.CharField(max_length=255)  # The search query
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"{self.user.username} - {self.query}"
