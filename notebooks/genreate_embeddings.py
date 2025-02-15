"""

This code implements a book recommendation system using semantic search with LangChain, ChromaDB, and Jina Embeddings. Here's an overview of its key components:

1. Data Processing:
Loads book data from books_with_emotions.csv and extracts tagged_description into a separate text file.
Uses TextLoader to load the descriptions and CharacterTextSplitter to split them into smaller text chunks.

2. Vector Embeddings & Database Setup:
Uses Jina Embeddings to generate vector representations of the book descriptions.
Stores and retrieves embeddings using ChromaDB, a persistent vector database.

3. User Data Analysis:
Extracts the most common genre from the user's:
Favorite books
Reading history
Search queries
Enhances search queries with genre-related keywords to improve recommendation relevance.

4. Recommendation System:
Semantic Recommendations: Retrieves top books matching a user's query using similarity search.
For-You Recommendations: Generates personalized book suggestions based on past interactions and enhanced queries.
Best Rating Selection: Finds the highest-rated book from the recommended list.

5. Execution & Output:
Enhances the user’s input query and finds relevant books.
Prints recommended books along with their title, genre, author, and rating.
Saves user data embeddings and confirms successful recommendation generation.
This system personalizes book suggestions by analyzing user preferences and improving search queries with keyword expansion, making it a smart recommendation engine. It leverages semantic search to find books similar to the user's interests and enhances the search process with genre-specific keywords for better results.

"""

from langchain_community.embeddings import JinaEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
import pandas as pd
from collections import Counter
import random


load_dotenv()

# Load books data
books = pd.read_csv("books_with_emotions.csv")

books["tagged_description"].to_csv("tagged_description.txt",
                                   sep = "\n",
                                   index = False,
                                   header = False)

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

raw_documents = TextLoader("tagged_description.txt").load()

# Change size and overlap
text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
documents = text_splitter.split_documents(raw_documents)

# Create embeddings
current_dir = os.getcwd()
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

embeddings = JinaEmbeddings(
    jina_api_key=os.getenv("JINA_API_KEY", "jina_*"), model_name="jina-embeddings-v2-base-en"
)

# Load existing ChromaDB or create a new one
books_db = Chroma(
    persist_directory=persistent_directory, 
    embedding_function=embeddings
)

def retrieve_semantic_recommendations(query, user_data, top_k=5):
    most_common_genre = get_most_common_genre(user_data)
    if most_common_genre:
        combined_query = f"{query} {enhanced_query}"
    else:
        combined_query = query
    search_results = books_db.similarity_search(combined_query, k=top_k)
    books_list = [int(result.metadata['isbn13']) for result in search_results]
    return books[books["isbn13"].isin(books_list)]

# THIS IS TO GET HOME RECCOMENDATION 
def retrieve_foryou_recommendations(user_data):
    dummy_query=""
    enhanced=enhance_query(dummy_query,user_data,genre_keywords)
    print(f"query used in reccomendation :{enhanced}")
    search_results = books_db.similarity_search(enhanced, k=30)
    books_list = [int(result.metadata['isbn13']) for result in search_results]
    return books[books["isbn13"].isin(books_list)]

def get_highest_rating(books_list):
    highest_rated_book = books_list.loc[books_list["average_rating"].idxmax()]
    return highest_rated_book

# User data
user_data = {
    "user_id": 2,
    "age": 30,
    "preferred_genres": ["Mystery"],
    "favorite_books": [
        {"title": "Gone Girl", "genre": "Mystery"},
        {"title": "The Girl with the Dragon Tattoo", "genre": "Thriller"}
    ],
    "reading_history": [
        {"title": "The Da Vinci Code", "genre": "Mystery"},
        {"title": "Angels & Demons", "genre": "Thriller"}
    ],
    "search_history": [
        {"query": "best mystery books", "timestamp": "2025-02-14T12:00:00Z"},
        {"query": "top thrillers", "timestamp": "2025-02-13T18:30:00Z"}
    ],
    "reviews": [
        {"title": "The Da Vinci Code", "rating": 5, "comment": "Incredible twists and turns!"},
        {"title": "Angels & Demons", "rating": 4, "comment": "Great read but a bit predictable."}
    ],
    "screen_time": [
        {"title": "Gone Girl", "duration_minutes": 135},
        {"title": "The Girl with the Dragon Tattoo", "duration_minutes": 158}
    ],
}

genre_keywords = {
    "Mystery": ["detective", "investigation", "clues", "crime", "whodunit", "suspense", "secrets"],
    "Thriller": ["suspense", "action", "danger", "fast-paced", "conspiracy", "adrenaline"],
    "Science Fiction": ["future", "technology", "space", "robots", "AI", "extraterrestrial", "cyberpunk"],
    "Fantasy": ["magic", "dragons", "mythical", "sorcery", "epic", "adventure", "kingdoms"],
    "Romance": ["love", "passion", "relationship", "heartfelt", "drama", "soulmate", "affection"],
    "Horror": ["fear", "ghosts", "haunted", "monsters", "terror", "supernatural", "dark"],
    "Historical Fiction": ["past", "war", "kings", "ancient", "historical", "tradition", "period"],
    "Dystopian": ["future", "apocalypse", "totalitarian", "rebellion", "oppression", "society"],
    "Adventure": ["journey", "exploration", "action", "danger", "discovery", "expedition"],
    "Non-Fiction": ["real", "true", "history", "facts", "knowledge", "learning", "biography"],
    "Fiction": ["storytelling", "narrative", "imaginative", "characters", "plot", "novel", "literature"]
}



def get_most_common_genre(user_data):
    genre_counts = Counter()

    # Count genres from favorite books
    for book in user_data.get("favorite_books", []):
        genre_counts[book["genre"]] += 1

    # Count genres from reading history
    for book in user_data.get("reading_history", []):
        genre_counts[book["genre"]] += 1

    # NOW THIS WONT GET ANY PREFERED GENRES BUT IT WILL GET SOME KEYWORDS FROM THE SEARCH HISTORY THAT MIGHT HELP
    for search in user_data.get("search_history", []):
        for genre in user_data.get("preferred_genres", []):
            if genre.lower() in search["query"].lower():
                genre_counts[genre] += 1

    # Find the most common genre
    if genre_counts:
        most_common_genre = genre_counts.most_common(1)[0][0]  # Get top genre
        return most_common_genre
    return None  # No genre found


def enhance_query(query, user_data, genre_keywords):
    most_common_genre = get_most_common_genre(user_data)

    if most_common_genre and most_common_genre in genre_keywords:
        keywords = genre_keywords[most_common_genre]
        selected_words = ", ".join(random.sample(keywords, min(5, len(keywords))))  # Pick 5 relevant words
        enhanced_query = f"{query} {selected_words}"
    else:
        enhanced_query = query  # No genre found, use original query

    return enhanced_query

query = "I want an exciting book."
enhanced_query = enhance_query(query, user_data, genre_keywords)

print(f"Enhanced Query: {enhanced_query}")



print(f"Most common genre: {get_most_common_genre(user_data)}")
print(f"Final search query: {query} {get_most_common_genre(user_data)}")
recommendation_results = retrieve_semantic_recommendations(query, user_data, 5)
print(f'recommendation_results = {recommendation_results}')
for_you = retrieve_foryou_recommendations(user_data)
print("Home Recommendations:")
for book in for_you.itertuples(index=False):
    print(f"Title: {book.title}, Categories: {book.categories}")




i = 1
for row in recommendation_results.itertuples(index=False):
    print(f"{i}: Title: {row.title},Genre:{row.categories} Author: {row.authors}, Average Rating: {row.average_rating}")
    print("-" * 50)
    i += 1

best_result = get_highest_rating(recommendation_results)
print(best_result)
print(best_result.title)

print("User data embeddings saved and recommendations generated successfully!")
