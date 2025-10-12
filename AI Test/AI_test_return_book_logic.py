import pytest
from datetime import datetime, timedelta
from library_service import return_book_by_patron
from database import init_database, clear_database, insert_book, insert_borrow_record, get_book_by_id, get_patron_borrow_count

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def borrowed_book():
    """Create a book that has been borrowed by a patron."""
    # Insert book
    insert_book("Test Book", "Test Author", "1234567890123", 2, 1)
    
    # Borrow the book
    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    
    return {"book_id": 1, "patron_id": "123456"}

def test_return_book_valid_input(borrowed_book):
    """Test returning a book with valid input."""
    success, message = return_book_by_patron(borrowed_book["patron_id"], borrowed_book["book_id"])
    
    assert success == True
    assert "successfully returned" in message.lower()
    assert "Test Book" in message
    
    # Verify book availability increased
    book = get_book_by_id(borrowed_book["book_id"])
    assert book['available_copies'] == 2  # Back to original amount
    
    # Verify patron borrow count decreased
    borrow_count = get_patron_borrow_count(borrowed_book["patron_id"])
    assert borrow_count == 0

def test_return_book_invalid_patron_id():
    """Test returning with invalid patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    assert "invalid patron id" in message.lower()
    assert "6 digits" in message.lower()

def test_return_book_nonexistent_book():
    """Test returning a book that doesn't exist."""
    success, message = return_book_by_patron("123456", 999)
    
    assert success == False
    assert "book not found" in message.lower()

def test_return_book_not_borrowed():
    """Test returning a book that the patron hasn't borrowed."""
    # Create a book but don't borrow it
    insert_book("Test Book", "Test Author", "1234567890123", 1, 1)
    
    success, message = return_book_by_patron("123456", 1)
    
    assert success == False
    assert "haven't borrowed this book" in message.lower()

def test_return_book_invalid_patron_format():
    """Test returning with invalid patron ID format."""
    success, message = return_book_by_patron("abc123", 1)
    
    assert success == False
    assert "invalid patron id" in message.lower()