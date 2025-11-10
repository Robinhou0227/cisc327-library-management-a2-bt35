import pytest
from datetime import datetime, timedelta
from library_service import get_patron_status_report
from database import init_database, clear_database, insert_book, insert_borrow_record

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def patron_with_books():
    """Create a patron with borrowed books."""
    # Insert books
    insert_book("Book 1", "Author 1", "1111111111111", 2, 1)
    insert_book("Book 2", "Author 2", "2222222222222", 1, 0)
    insert_book("Book 3", "Author 3", "3333333333333", 3, 2)
    
    # Borrow books
    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    
    # Borrow another book that's overdue
    overdue_borrow_date = datetime.now() - timedelta(days=20)
    overdue_due_date = overdue_borrow_date + timedelta(days=14)
    insert_borrow_record("123456", 2, overdue_borrow_date, overdue_due_date)
    
    return "123456"

def test_get_patron_status_report_valid_patron(patron_with_books):
    """Test getting status report for a valid patron."""
    result = get_patron_status_report(patron_with_books)
    
    assert isinstance(result, dict)
    assert result['patron_id'] == patron_with_books
    assert result['current_borrow_count'] == 2
    assert len(result['currently_borrowed_books']) == 2
    assert len(result['borrow_history']) == 2
    assert result['total_late_fees'] > 0  # Should have late fees from overdue book
    assert result['status'] == 'active'

def test_get_patron_status_report_no_books():
    """Test getting status report for patron with no books."""
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    assert result['patron_id'] == "123456"
    assert result['current_borrow_count'] == 0
    assert len(result['currently_borrowed_books']) == 0
    assert len(result['borrow_history']) == 0
    assert result['total_late_fees'] == 0.0
    assert result['status'] == 'active'

def test_get_patron_status_report_invalid_patron_id():
    """Test getting status report with invalid patron ID."""
    result = get_patron_status_report("12345")
    
    assert isinstance(result, dict)
    assert 'error' in result
    assert "invalid patron id" in result['error'].lower()
    assert "6 digits" in result['error'].lower()

def test_get_patron_status_report_invalid_format():
    """Test getting status report with invalid patron ID format."""
    result = get_patron_status_report("abc123")
    
    assert isinstance(result, dict)
    assert 'error' in result
    assert "invalid patron id" in result['error'].lower()

def test_get_patron_status_report_nonexistent_patron():
    """Test getting status report for non-existent patron."""
    result = get_patron_status_report("999999")
    
    assert isinstance(result, dict)
    assert result['patron_id'] == "999999"
    assert result['current_borrow_count'] == 0
    assert len(result['currently_borrowed_books']) == 0
    assert len(result['borrow_history']) == 0
    assert result['total_late_fees'] == 0.0
    assert result['status'] == 'active'

def test_get_patron_status_report_borrowing_limit_reached():
    """Test getting status report for patron at borrowing limit."""
    # Borrow 5 books to reach limit
    for i in range(5):
        insert_book(f"Book {i}", f"Author {i}", f"123456789000{i}", 1, 0)
        borrow_date = datetime.now() - timedelta(days=5)
        due_date = borrow_date + timedelta(days=14)
        insert_borrow_record("123456", i + 1, borrow_date, due_date)
    
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    assert result['current_borrow_count'] == 5
    assert len(result['currently_borrowed_books']) == 5
    assert result['status'] == 'borrowing_limit_reached'