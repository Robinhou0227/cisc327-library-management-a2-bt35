import pytest
from datetime import datetime, timedelta
from database import get_patron_borrowed_books, init_database, clear_database, insert_book, insert_borrow_record

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

def test_get_patron_borrowed_books_no_borrows():
    """Test getting borrowed books for patron with no borrowed books."""
    books = get_patron_borrowed_books("123456")
    
    assert isinstance(books, list)
    assert len(books) == 0

def test_get_patron_borrowed_books_single_borrow(sample_books):
    """Test getting borrowed books for patron with one borrowed book."""
    patron_id = "123456"
    book_id = sample_books[0]
    
    # Borrow a book
    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    books = get_patron_borrowed_books(patron_id)
    
    assert isinstance(books, list)
    assert len(books) == 1
    
    book = books[0]
    assert book['book_id'] == book_id
    assert book['title'] == "Book 0"
    assert book['author'] == "Author 0"
    assert isinstance(book['borrow_date'], datetime)
    assert isinstance(book['due_date'], datetime)
    assert isinstance(book['is_overdue'], bool)

def test_get_patron_borrowed_books_multiple_borrows(sample_books):
    """Test getting borrowed books for patron with multiple borrowed books."""
    patron_id = "123456"
    
    # Borrow multiple books
    for i in range(2):
        book_id = sample_books[i]
        borrow_date = datetime.now() - timedelta(days=5)
        due_date = borrow_date + timedelta(days=14)
        insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    books = get_patron_borrowed_books(patron_id)
    
    assert isinstance(books, list)
    assert len(books) == 2
    
    # Verify all books are present
    book_ids = [book['book_id'] for book in books]
    for i in range(2):
        assert sample_books[i] in book_ids

def test_get_patron_borrowed_books_overdue_detection(sample_books):
    """Test that overdue status is correctly detected."""
    patron_id = "123456"
    book_id = sample_books[0]
    
    # Borrow a book that's overdue
    borrow_date = datetime.now() - timedelta(days=20)  # 20 days ago
    due_date = borrow_date + timedelta(days=14)  # Due 6 days ago
    insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    books = get_patron_borrowed_books(patron_id)
    
    assert len(books) == 1
    assert books[0]['is_overdue'] == True

def test_get_patron_borrowed_books_nonexistent_patron():
    """Test getting borrowed books for non-existent patron."""
    books = get_patron_borrowed_books("999999")
    
    assert isinstance(books, list)
    assert len(books) == 0
