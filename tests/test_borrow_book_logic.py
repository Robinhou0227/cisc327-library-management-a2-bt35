import pytest
from datetime import datetime, timedelta
from library_service import borrow_book_by_patron
from database import get_book_by_id, get_patron_borrow_count, init_database, clear_database, insert_book, insert_borrow_record

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def sample_book():
    """Create a sample book for testing."""
    insert_book("Test Book", "Test Author", "1234567890123", 3, 3)
    return get_book_by_id(1)  # Assuming it gets ID 1

def test_borrow_book_valid_input(sample_book):
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", sample_book['id'])
    
    assert success == True
    assert "successfully borrowed" in message.lower()
    assert "due date" in message.lower()
    
    # Verify book availability decreased
    updated_book = get_book_by_id(sample_book['id'])
    assert updated_book['available_copies'] == sample_book['available_copies'] - 1
    
    # Verify patron borrow count increased
    borrow_count = get_patron_borrow_count("123456")
    assert borrow_count == 1

def test_borrow_book_invalid_patron_id():
    """Test borrowing with invalid patron ID (too short)."""
    success, message = borrow_book_by_patron("12345", 1)
    
    assert success == False
    assert "invalid patron id" in message.lower()
    assert "6 digits" in message.lower()

def test_borrow_book_nonexistent_book():
    """Test borrowing a book that doesn't exist."""
    success, message = borrow_book_by_patron("123456", 999)
    
    assert success == False
    assert "book not found" in message.lower()

def test_borrow_book_unavailable():
    """Test borrowing a book with no available copies."""
    # Create a book with 0 available copies
    insert_book("Unavailable Book", "Test Author", "1111111111111", 2, 0)
    book = get_book_by_id(2)  # Assuming it gets ID 2
    
    success, message = borrow_book_by_patron("123456", book['id'])
    
    assert success == False
    assert "not available" in message.lower()

def test_borrow_book_patron_limit_exceeded(sample_book):
    """Test borrowing when patron has reached the 5-book limit."""
    # Borrow 5 books first
    for i in range(5):
        insert_book(f"Book {i}", "Author", f"123456789000{i}", 1, 1)
        insert_borrow_record("123456", i + 2, datetime.now(), datetime.now() + timedelta(days=14))
    
    # Try to borrow another book
    success, message = borrow_book_by_patron("123456", sample_book['id'])
    
    assert success == False
    assert "maximum borrowing limit" in message.lower()
    assert "5 books" in message.lower()