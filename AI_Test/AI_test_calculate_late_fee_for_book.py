import pytest
from datetime import datetime, timedelta
from library_service import calculate_late_fee_for_book
from database import init_database, clear_database, insert_book, insert_borrow_record

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def borrowed_book_on_time():
    """Create a book borrowed and returned on time."""
    insert_book("On Time Book", "Author", "1234567890123", 1, 1)
    
    # Borrow and return on time
    borrow_date = datetime.now() - timedelta(days=10)
    due_date = borrow_date + timedelta(days=14)
    return_date = due_date - timedelta(days=1)  # 1 day early
    
    insert_borrow_record("123456", 1, borrow_date, due_date)
    # Note: In real scenario, return_date would be set via update_borrow_record_return_date
    # For testing, we'll simulate this scenario
    
    return {"book_id": 1, "patron_id": "123456"}

@pytest.fixture
def overdue_book():
    """Create a book that is currently overdue."""
    insert_book("Overdue Book", "Author", "1111111111111", 1, 0)
    
    # Borrow a book that's overdue
    borrow_date = datetime.now() - timedelta(days=20)  # 20 days ago
    due_date = borrow_date + timedelta(days=14)  # Due 6 days ago
    insert_borrow_record("123456", 1, borrow_date, due_date)
    
    return {"book_id": 1, "patron_id": "123456"}

def test_calculate_late_fee_on_time_book(borrowed_book_on_time):
    """Test late fee calculation for a book returned on time."""
    result = calculate_late_fee_for_book(borrowed_book_on_time["patron_id"], borrowed_book_on_time["book_id"])
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Returned on time'

def test_calculate_late_fee_overdue_book(overdue_book):
    """Test late fee calculation for an overdue book."""
    result = calculate_late_fee_for_book(overdue_book["patron_id"], overdue_book["book_id"])
    
    assert result['fee_amount'] > 0
    assert result['days_overdue'] > 0
    assert "Overdue by" in result['status']
    # Should be $6.00 (6 days overdue at $1.00/day)
    assert result['fee_amount'] == 6.00

def test_calculate_late_fee_book_not_borrowed():
    """Test late fee calculation for a book not borrowed by patron."""
    insert_book("Not Borrowed Book", "Author", "1234567890123", 1, 1)
    
    result = calculate_late_fee_for_book("123456", 1)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "not currently borrowed" in result['status']

def test_calculate_late_fee_nonexistent_book():
    """Test late fee calculation for non-existent book."""
    result = calculate_late_fee_for_book("123456", 999)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "not currently borrowed" in result['status']

def test_calculate_late_fee_nonexistent_patron():
    """Test late fee calculation for non-existent patron."""
    result = calculate_late_fee_for_book("999999", 1)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "not currently borrowed" in result['status']