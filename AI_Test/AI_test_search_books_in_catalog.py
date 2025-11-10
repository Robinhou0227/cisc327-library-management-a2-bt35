import pytest
from library_service import search_books_in_catalog
from database import init_database, clear_database, insert_book

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def sample_books():
    """Create sample books for testing."""
    books = [
        ("The Great Gatsby", "F. Scott Fitzgerald", "1111111111111", 2),
        ("To Kill a Mockingbird", "Harper Lee", "2222222222222", 1),
        ("1984", "George Orwell", "3333333333333", 3),
        ("Gatsby's Return", "F. Scott Fitzgerald", "4444444444444", 1)
    ]
    
    for title, author, isbn, copies in books:
        insert_book(title, author, isbn, copies, copies)
    
    return books

def test_search_books_by_title(sample_books):
    """Test searching books by title."""
    results = search_books_in_catalog("gatsby", "title")
    
    assert isinstance(results, list)
    assert len(results) == 2  # Should find both Gatsby books
    titles = [book['title'] for book in results]
    assert "The Great Gatsby" in titles
    assert "Gatsby's Return" in titles

def test_search_books_by_author(sample_books):
    """Test searching books by author."""
    results = search_books_in_catalog("fitzgerald", "author")
    
    assert isinstance(results, list)
    assert len(results) == 2  # Should find both Fitzgerald books
    authors = [book['author'] for book in results]
    assert all("F. Scott Fitzgerald" in author for author in authors)

def test_search_books_case_insensitive(sample_books):
    """Test that search is case insensitive."""
    results = search_books_in_catalog("MOCKINGBIRD", "title")
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]['title'] == "To Kill a Mockingbird"

def test_search_books_no_matches(sample_books):
    """Test searching for books that don't exist."""
    results = search_books_in_catalog("nonexistent", "title")
    
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_empty_search_term():
    """Test search with empty search term."""
    results = search_books_in_catalog("", "title")
    
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_whitespace_search_term():
    """Test search with whitespace-only search term."""
    results = search_books_in_catalog("   ", "title")
    
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_invalid_search_type(sample_books):
    """Test search with invalid search type (should search both title and author)."""
    results = search_books_in_catalog("fitzgerald", "invalid_type")
    
    assert isinstance(results, list)
    assert len(results) == 2  # Should find Fitzgerald books in both title and author

def test_search_books_partial_match(sample_books):
    """Test searching with partial matches."""
    results = search_books_in_catalog("kill", "title")
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]['title'] == "To Kill a Mockingbird"