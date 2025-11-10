"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .payment_service import PaymentGateway
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books,
    get_patron_borrow_history
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4: Book Return Processing
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Check if patron has this book borrowed
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_book_ids = [b['book_id'] for b in borrowed_books]
    
    if book_id not in borrowed_book_ids:
        return False, "You haven't borrowed this book."
    
    # Process the return
    return_date = datetime.now()
    
    # Update borrow record with return date
    update_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not update_success:
        return False, "Database error occurred while updating borrow record."
    
    # Update book availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Calculate late fees
    late_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    if late_fee_info['fee_amount'] > 0:
        return True, f'Successfully returned "{book["title"]}". Late fee: ${late_fee_info["fee_amount"]:.2f}'
    else:
        return True, f'Successfully returned "{book["title"]}". No late fees.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5: Late Fee Calculation
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
        
    Returns:
        dict: Contains fee_amount, days_overdue, and status
    """
    # Get the borrow record for this specific book
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Find the specific book in the borrowed books
    target_book = None
    for book in borrowed_books:
        if book['book_id'] == book_id:
            target_book = book
            break
    
    if not target_book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not currently borrowed by this patron'
        }
    
    # Calculate days overdue
    due_date = target_book['due_date']
    return_date = datetime.now()
    
    days_overdue = (return_date - due_date).days
    late_fee_per_day = 1.00  # $1.00 per day
    
    if days_overdue <= 0:
        # Book returned on time or early
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Returned on time'
        }
    else:
        # Book is overdue
        total_fee = days_overdue * late_fee_per_day
        return {
            'fee_amount': round(total_fee, 2),
            'days_overdue': days_overdue,
            'status': f'Overdue by {days_overdue} days'
        }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6: Book Search Functionality
    
    Args:
        search_term: The term to search for
        search_type: Type of search ('title' or 'author')
        
    Returns:
        list: List of matching books
    """
    if not search_term or not search_term.strip():
        return []
    
    search_term = search_term.strip().lower()
    
    # Get all books and filter based on search type
    all_books = get_all_books()
    matching_books = []
    
    for book in all_books:
        if search_type == 'title':
            if search_term in book['title'].lower():
                matching_books.append(book)
        elif search_type == 'author':
            if search_term in book['author'].lower():
                matching_books.append(book)
        else:
            # Search both title and author if invalid search_type
            if (search_term in book['title'].lower() or 
                search_term in book['author'].lower()):
                matching_books.append(book)
    
    return matching_books

def total_late_fees(patron_id: str) -> float:
    """
    Calculate total late fees for a patron.
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        float: Total late fees amount
    """
    borrow_history = get_patron_borrow_history(patron_id)
    total_fees = 0.0
    
    for record in borrow_history:
        if record['is_returned'] and record['return_date']:
            # Calculate late fee for returned book
            days_overdue = (record['return_date'] - record['due_date']).days
            if days_overdue > 0:
                total_fees += days_overdue * 1.00  # $1.00 per day
        elif not record['is_returned'] and record['is_overdue']:
            # Calculate late fee for currently overdue book
            days_overdue = (datetime.now() - record['due_date']).days
            total_fees += days_overdue * 1.00  # $1.00 per day
    
    return round(total_fees, 2)

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: Complete patron status information
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'error': 'Invalid patron ID. Must be exactly 6 digits.'}
    
    # Get current borrowed books
    current_borrowed = get_patron_borrowed_books(patron_id)
    
    # Get borrow count
    borrow_count = get_patron_borrow_count(patron_id)
    
    # Get complete borrow history
    borrow_history = get_patron_borrow_history(patron_id)
    
    # Calculate total late fees
    total_fees = total_late_fees(patron_id)
    
    return {
        'patron_id': patron_id,
        'currently_borrowed_books': current_borrowed,
        'current_borrow_count': borrow_count,
        'borrow_history': borrow_history,
        'total_late_fees': total_fees,
        'status': 'active' if borrow_count < 5 else 'borrowing_limit_reached'
    }

def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[bool, str, Optional[str]]:
    """
    Process payment for late fees using external payment gateway.
    
    NEW FEATURE FOR ASSIGNMENT 3: Demonstrates need for mocking/stubbing
    This function depends on an external payment service that should be mocked in tests.
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book with late fees
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str, transaction_id: Optional[str])
        
    Example for you to mock:
        # In tests, mock the payment gateway:
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", None
    
    # Calculate late fee first
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    # Check if there's a fee to pay
    if not fee_info or 'fee_amount' not in fee_info:
        return False, "Unable to calculate late fees.", None
    
    fee_amount = fee_info.get('fee_amount', 0.0)
    
    if fee_amount <= 0:
        return False, "No late fees to pay for this book.", None
    
    # Get book details for payment description
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", None
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process payment through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN THEIR TESTS!
    try:
        success, transaction_id, message = payment_gateway.process_payment(
            patron_id=patron_id,
            amount=fee_amount,
            description=f"Late fees for '{book['title']}'"
        )
        
        if success:
            return True, f"Payment successful! {message}", transaction_id
        else:
            return False, f"Payment failed: {message}", None
            
    except Exception as e:
        # Handle payment gateway errors
        return False, f"Payment processing error: {str(e)}", None

def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[bool, str]:
    """
    Refund a late fee payment (e.g., if book was returned on time but fees were charged in error).
    
    NEW FEATURE FOR ASSIGNMENT 3: Another function requiring mocking
    
    Args:
        transaction_id: Original transaction ID to refund
        amount: Amount to refund
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."
    
    if amount <= 0:
        return False, "Refund amount must be greater than 0."
    
    if amount > 15.00:  # Maximum late fee per book
        return False, "Refund amount exceeds maximum late fee."
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process refund through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN YOUR TESTS!
    try:
        success, message = payment_gateway.refund_payment(transaction_id, amount)
        
        if success:
            return True, message
        else:
            return False, f"Refund failed: {message}"
            
    except Exception as e:
        return False, f"Refund processing error: {str(e)}"