from django.db import models
from django.contrib.auth.models import User
import random


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")  # Collection belongs to a user
    name = models.CharField(max_length=255)
    books = models.ManyToManyField('Book', related_name='collections')

    class Meta:
        unique_together = ('user', 'name')  # Ensures a user can't have duplicate collection names

    def __str__(self):
        return f"{self.user.username}'s Collection: {self.name}"

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2,default=random.randint(1, 100))
    categories = categories = models.JSONField(default=list) # List of categories
    description = models.TextField(blank=True)
    published_date = models.DateField(default="2021-01-01")
    cover = models.URLField(default="http://books.google.com/books/content?id=I2jbBlMHlAMC&printsec=frontcover&img=1&zoom=1&source=gbs_api")
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    num_reviews = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title


class UserBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="user_books")
    progress = models.FloatField(default=0)  # Percentage read (0 to 100)
    screen_time = models.PositiveIntegerField(default=0)  # Time in seconds
    last_updated = models.DateTimeField(auto_now=True)  # Track last progress update

    class Meta:
        unique_together = ('user', 'book')  # Ensures a user-book pair is unique

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.progress}%)"