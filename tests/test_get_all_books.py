import pytest
from database import get_all_books, init_database, clear_database, insert_book

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

def test_get_all_books_empty_database():
    """Test getting all books from empty database."""
    books = get_all_books()
    
    assert isinstance(books, list)
    assert len(books) == 0

def test_get_all_books_single_book():
    """Test getting all books with one book in database."""
    insert_book("Test Book", "Test Author", "1234567890123", 3, 3)
    
    books = get_all_books()
    
    assert isinstance(books, list)
    assert len(books) == 1
    assert books[0]['title'] == "Test Book"
    assert books[0]['author'] == "Test Author"
    assert books[0]['isbn'] == "1234567890123"
    assert books[0]['total_copies'] == 3
    assert books[0]['available_copies'] == 3

def test_get_all_books_multiple_books():
    """Test getting all books with multiple books in database."""
    # Insert multiple books
    insert_book("Book 1", "Author 1", "1111111111111", 2, 2)
    insert_book("Book 2", "Author 2", "2222222222222", 1, 1)
    insert_book("Book 3", "Author 3", "3333333333333", 4, 3)
    
    books = get_all_books()
    
    assert isinstance(books, list)
    assert len(books) == 3
    
    # Verify books are ordered by title (as per the SQL query)
    titles = [book['title'] for book in books]
    assert titles == sorted(titles)

def test_get_all_books_data_structure():
    """Test that returned books have the correct data structure."""
    insert_book("Test Book", "Test Author", "1234567890123", 3, 2)
    
    books = get_all_books()
    book = books[0]
    
    # Verify all required fields are present
    required_fields = ['id', 'title', 'author', 'isbn', 'total_copies', 'available_copies']
    for field in required_fields:
        assert field in book
    
    # Verify field types
    assert isinstance(book['id'], int)
    assert isinstance(book['title'], str)
    assert isinstance(book['author'], str)
    assert isinstance(book['isbn'], str)
    assert isinstance(book['total_copies'], int)
    assert isinstance(book['available_copies'], int)

def test_get_all_books_ordering():
    """Test that books are returned in alphabetical order by title."""
    # Insert books in non-alphabetical order
    insert_book("Zebra Book", "Author", "1111111111111", 1, 1)
    insert_book("Apple Book", "Author", "2222222222222", 1, 1)
    insert_book("Banana Book", "Author", "3333333333333", 1, 1)
    
    books = get_all_books()
    
    assert len(books) == 3
    titles = [book['title'] for book in books]
    assert titles == ["Apple Book", "Banana Book", "Zebra Book"]
