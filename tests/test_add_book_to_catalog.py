import pytest
from library_service import add_book_to_catalog
from database import get_book_by_isbn, init_database, clear_database

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()
    
    # Verify book was actually added to database
    book = get_book_by_isbn("1234567890123")
    assert book is not None
    assert book['title'] == "Test Book"
    assert book['author'] == "Test Author"
    assert book['total_copies'] == 5
    assert book['available_copies'] == 5

def test_add_book_invalid_isbn():
    """Test adding a book with invalid ISBN (too short)."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_negative_copies():
    """Test adding a book with negative copy count."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -2)
    
    assert success == False
    assert "must be a positive integer" in message.lower()

def test_add_book_missing_title():
    """Test adding a book with missing title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title is required" in message.lower()

def test_add_book_duplicate_isbn():
    """Test adding a book with duplicate ISBN."""
    # First add a book
    add_book_to_catalog("First Book", "First Author", "1111111111111", 3)
    
    # Try to add another book with same ISBN
    success, message = add_book_to_catalog("Second Book", "Second Author", "1111111111111", 2)
    
    assert success == False
    assert "already exists" in message.lower()
