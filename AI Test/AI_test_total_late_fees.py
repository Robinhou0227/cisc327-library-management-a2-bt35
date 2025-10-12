import pytest
from datetime import datetime, timedelta
from library_service import total_late_fees
from database import init_database, clear_database, insert_book, insert_borrow_record

# Setup database before tests
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize and clear database before each test."""
    init_database()
    clear_database()

@pytest.fixture
def patron_with_late_fees():
    """Create a patron with books that have late fees."""
    # Insert books
    insert_book("Book 1", "Author 1", "1111111111111", 1, 0)
    insert_book("Book 2", "Author 2", "2222222222222", 1, 0)
    
    # Borrow books with different overdue scenarios
    # Book 1: 5 days overdue
    borrow_date1 = datetime.now() - timedelta(days=19)
    due_date1 = borrow_date1 + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date1, due_date1)
    
    # Book 2: 10 days overdue
    borrow_date2 = datetime.now() - timedelta(days=24)
    due_date2 = borrow_date2 + timedelta(days=14)
    insert_borrow_record("123456", 2, borrow_date2, due_date2)
    
    return "123456"

def test_total_late_fees_with_overdue_books(patron_with_late_fees):
    """Test calculating total late fees for patron with overdue books."""
    total = total_late_fees(patron_with_late_fees)
    
    assert isinstance(total, float)
    assert total == 15.0  # 5 days + 10 days = 15 days * $1.00 = $15.00

def test_total_late_fees_no_books():
    """Test calculating total late fees for patron with no books."""
    total = total_late_fees("123456")
    
    assert isinstance(total, float)
    assert total == 0.0

def test_total_late_fees_nonexistent_patron():
    """Test calculating total late fees for non-existent patron."""
    total = total_late_fees("999999")
    
    assert isinstance(total, float)
    assert total == 0.0

def test_total_late_fees_mixed_scenario():
    """Test calculating total late fees with mixed returned and current books."""
    # Insert books
    insert_book("Current Book", "Author", "1111111111111", 1, 0)
    insert_book("Returned Book", "Author", "2222222222222", 1, 1)
    
    # Current overdue book (3 days overdue)
    borrow_date1 = datetime.now() - timedelta(days=17)
    due_date1 = borrow_date1 + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date1, due_date1)
    
    # Returned overdue book (would be 7 days overdue if returned today)
    # This simulates a book that was returned late
    borrow_date2 = datetime.now() - timedelta(days=21)
    due_date2 = borrow_date2 + timedelta(days=14)
    insert_borrow_record("123456", 2, borrow_date2, due_date2)
    
    total = total_late_fees("123456")
    
    # Should only count the currently overdue book (3 days)
    assert isinstance(total, float)
    assert total == 3.0