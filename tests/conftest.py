import pytest
import sqlite3
from pytest_mock import MockFixture
from datetime import datetime, timedelta
from database import (
    insert_book,
    insert_borrow_record
)

@pytest.fixture
def sample_book():
    """Create a sample book for testing."""
    book_id = 1
    insert_book(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        total_copies=2,
        available_copies=2
    )
    return {
        'id': book_id,
        'title': "Test Book",
        'author': "Test Author",
        'isbn': "1234567890123",
        'total_copies': 2,
        'available_copies': 2
    }

@pytest.fixture
def sample_books():
    """Create multiple sample books for testing."""
    books = []
    for i in range(1, 4):
        book_id = i
        insert_book(
            title=f"Test Book {i}",
            author=f"Test Author {i}",
            isbn=f"123456789012{i}",
            total_copies=2,
            available_copies=2
        )
        books.append(book_id)
    return books

@pytest.fixture
def sample_borrow_record(sample_book):
    """Create a sample borrow record for testing."""
    patron_id = "123456"
    book_id = sample_book['id']
    borrow_date = datetime.now() - timedelta(days=7)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    return {
        'patron_id': patron_id,
        'book_id': book_id,
        'borrow_date': borrow_date,
        'due_date': due_date
    }

