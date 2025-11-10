import pytest
from datetime import datetime, timedelta
from database import get_patron_borrow_history, init_database, clear_database, insert_book, insert_borrow_record, update_borrow_record_return_date

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def patron_with_history():
    """Create a patron with borrow history including returned books."""
    # Insert books
    insert_book("Current Book", "Author 1", "1111111111111", 1, 0)
    insert_book("Returned Book", "Author 2", "2222222222222", 1, 1)
    insert_book("Old Book", "Author 3", "3333333333333", 1, 1)
    
    patron_id = "123456"
    
    # Current book (not returned)
    borrow_date1 = datetime.now() - timedelta(days=5)
    due_date1 = borrow_date1 + timedelta(days=14)
    insert_borrow_record(patron_id, 1, borrow_date1, due_date1)
    
    # Returned book
    borrow_date2 = datetime.now() - timedelta(days=30)
    due_date2 = borrow_date2 + timedelta(days=14)
    return_date2 = datetime.now() - timedelta(days=10)
    insert_borrow_record(patron_id, 2, borrow_date2, due_date2)
    update_borrow_record_return_date(patron_id, 2, return_date2)
    
    # Old returned book
    borrow_date3 = datetime.now() - timedelta(days=60)
    due_date3 = borrow_date3 + timedelta(days=14)
    return_date3 = datetime.now() - timedelta(days=40)
    insert_borrow_record(patron_id, 3, borrow_date3, due_date3)
    update_borrow_record_return_date(patron_id, 3, return_date3)
    
    return patron_id

def test_get_patron_borrow_history_complete_history(patron_with_history):
    """Test getting complete borrow history for a patron."""
    history = get_patron_borrow_history(patron_with_history)
    
    assert isinstance(history, list)
    assert len(history) == 3  # Should include all books (current and returned)
    
    # Check that history is ordered by borrow_date DESC (most recent first)
    borrow_dates = [record['borrow_date'] for record in history]
    assert borrow_dates == sorted(borrow_dates, reverse=True)
    
    # Check data structure
    for record in history:
        assert 'book_id' in record
        assert 'title' in record
        assert 'author' in record
        assert 'borrow_date' in record
        assert 'due_date' in record
        assert 'return_date' in record
        assert 'is_returned' in record
        assert 'is_overdue' in record
        
        assert isinstance(record['borrow_date'], datetime)
        assert isinstance(record['due_date'], datetime)
        assert isinstance(record['is_returned'], bool)
        assert isinstance(record['is_overdue'], bool)

def test_get_patron_borrow_history_no_history():
    """Test getting borrow history for patron with no history."""
    history = get_patron_borrow_history("123456")
    
    assert isinstance(history, list)
    assert len(history) == 0

def test_get_patron_borrow_history_nonexistent_patron():
    """Test getting borrow history for non-existent patron."""
    history = get_patron_borrow_history("999999")
    
    assert isinstance(history, list)
    assert len(history) == 0

def test_get_patron_borrow_history_returned_vs_current(patron_with_history):
    """Test that returned and current books are properly identified."""
    history = get_patron_borrow_history(patron_with_history)
    
    # Find current and returned books
    current_books = [record for record in history if not record['is_returned']]
    returned_books = [record for record in history if record['is_returned']]
    
    assert len(current_books) == 1
    assert len(returned_books) == 2
    
    # Check that return_date is None for current books
    for book in current_books:
        assert book['return_date'] is None
    
    # Check that return_date is set for returned books
    for book in returned_books:
        assert book['return_date'] is not None
        assert isinstance(book['return_date'], datetime)