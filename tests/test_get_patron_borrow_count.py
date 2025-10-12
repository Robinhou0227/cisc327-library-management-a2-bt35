import pytest
from datetime import datetime, timedelta
from database import get_patron_borrow_count, init_database, clear_database, insert_book, insert_borrow_record

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def sample_books():
    """Create sample books for testing."""
    books = []
    for i in range(3):  # Create 3 books for testing
        insert_book(f"Book {i}", f"Author {i}", f"123456789000{i}", 1, 1)
        books.append(i + 1)  # Assuming books get IDs 1-3
    return books

def test_get_patron_borrow_count_no_borrows():
    """Test getting borrow count for patron with no borrowed books."""
    count = get_patron_borrow_count("123456")
    
    assert isinstance(count, int)
    assert count == 0

def test_get_patron_borrow_count_single_borrow(sample_books):
    """Test getting borrow count for patron with one borrowed book."""
    patron_id = "123456"
    book_id = sample_books[0]
    
    # Borrow a book
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    count = get_patron_borrow_count(patron_id)
    
    assert count == 1

def test_get_patron_borrow_count_multiple_borrows(sample_books):
    """Test getting borrow count for patron with multiple borrowed books."""
    patron_id = "123456"
    
    # Borrow multiple books
    for i in range(2):
        book_id = sample_books[i]
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)
        insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    count = get_patron_borrow_count(patron_id)
    
    assert count == 2

def test_get_patron_borrow_count_invalid_patron_format():
    """Test getting borrow count with invalid patron ID format."""
    count = get_patron_borrow_count("abc123")
    
    assert isinstance(count, int)
    assert count == 0

def test_get_patron_borrow_count_nonexistent_patron():
    """Test getting borrow count for non-existent patron."""
    count = get_patron_borrow_count("999999")
    
    assert isinstance(count, int)
    assert count == 0
