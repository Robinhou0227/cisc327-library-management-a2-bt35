import pytest
from services.library_service import return_book_by_patron

def test_return_book_not_implemented():
    """Test that return book functionality is not yet implemented."""
    success, message = return_book_by_patron("123456", 1)
    assert success == False
    assert message.lower() in ['book not found.', 'invalid patron id. must be exactly 6 digits.']

def test_return_book_invalid_patron_id():
    """Test returning with invalid patron ID."""
    success, message = return_book_by_patron("", 1)
    assert success == False
    assert 'invalid patron id' in message.lower()

def test_return_book_nonexistent_book():
    """Test returning a book that doesn't exist."""
    success, message = return_book_by_patron("123456", 999)
    assert success == False
    assert 'book not found' in message.lower()

def test_return_book_nonexistent_patron():
    """Test returning with non-existent patron."""
    success, message = return_book_by_patron("999999", 1)
    assert success == False
    assert 'book not found' in message.lower()

def test_return_book_invalid_format():
    """Test returning with invalid patron ID format."""
    success, message = return_book_by_patron("abc123", 1)
    assert success == False
    assert 'invalid patron id' in message.lower()
