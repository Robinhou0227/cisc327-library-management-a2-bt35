"""
Test file for Assignment 3 - Mocking and Stubbing
5 test cases for pay_late_fees and 5 for refund_late_fee_payment
"""

import pytest
from unittest.mock import Mock, patch
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


class TestPayLateFees:
    def test_pay_late_fees_success(self, mocker):
        """Test 1 where we check Successful payment processing"""
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                    return_value={'fee_amount': 15.0, 'days_overdue': 15, 'status': 'Overdue'})
        mocker.patch('services.library_service.get_book_by_id', 
                    return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_12345", "Payment is successful")
        success, message, transaction_id = pay_late_fees(
            patron_id="123456", 
            book_id=1, 
            payment_gateway=mock_gateway
        )
        assert success == True
        assert transaction_id == "txn_12345"
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=15.0,
            description="Late fees for 'Test Book'"
        )

    def test_pay_late_fees_payment_declined(self, mocker):
        """Test 2 for a payment declined by gateway"""
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                    return_value={'fee_amount': 10.0, 'days_overdue': 10, 'status': 'Overdue'})
        mocker.patch('services.library_service.get_book_by_id', 
                    return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (False, None, "Payment declined, you have insufficient funds")
        success, message, transaction_id = pay_late_fees(
            patron_id="123456", 
            book_id=1, 
            payment_gateway=mock_gateway
        )
        assert success == False
        assert transaction_id is None
        assert "declined" in message.lower()
        mock_gateway.process_payment.assert_called_once()

    def test_pay_late_fees_invalid_patron_id(self, mocker):
        """Test 3 with an invalid patron ID, mock should not be called"""
        mocker.patch('services.library_service.calculate_late_fee_for_book')
        mocker.patch('services.library_service.get_book_by_id')
        mock_gateway = Mock(spec=PaymentGateway)
        success, message, transaction_id = pay_late_fees(
            patron_id="123",
            book_id=1, 
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "invalid patron id" in message.lower()
        mock_gateway.process_payment.assert_not_called()

    def test_pay_late_fees_zero_late_fees(self, mocker):
        """Test 4 with zero late fees, mock should not be called"""
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                    return_value={'fee_amount': 0.0, 'days_overdue': 0, 'status': 'Returned on time'})
        mocker.patch('services.library_service.get_book_by_id', 
                    return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
        mock_gateway = Mock(spec=PaymentGateway)
        success, message, transaction_id = pay_late_fees(
            patron_id="123456", 
            book_id=1, 
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "no late fees" in message.lower()
        mock_gateway.process_payment.assert_not_called()

    def test_pay_late_fees_network_error(self, mocker):
        """Test 5 with network error exception handling"""
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                    return_value={'fee_amount': 12.5, 'days_overdue': 12, 'status': 'Overdue'})
        mocker.patch('services.library_service.get_book_by_id', 
                    return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = Exception("The network timed out")
        success, message, transaction_id = pay_late_fees(
            patron_id="123456", 
            book_id=1, 
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "error" in message.lower()
        assert transaction_id is None
        mock_gateway.process_payment.assert_called_once()


class TestRefundLateFeePayment:
    def test_refund_late_fee_payment_success(self, mocker):
        """Test 1 for successful refund processing"""
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "The refund processed successfully")
        success, message = refund_late_fee_payment(
            transaction_id="txn_12345",
            amount=10.0,
            payment_gateway=mock_gateway
        )
        assert success == True
        assert "success" in message.lower()
        mock_gateway.refund_payment.assert_called_once_with("txn_12345", 10.0)

    def test_refund_late_fee_payment_invalid_transaction_id(self, mocker):
        """Test 2 check with an invalid transaction ID, mock should not be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        invalid_ids = ["", "invalid", "12345", "pay_12345"]
        
        for transaction_id in invalid_ids:
            success, message = refund_late_fee_payment(
                transaction_id=transaction_id,
                amount=10.0,
                payment_gateway=mock_gateway
            )
            assert success == False
            assert "invalid transaction id" in message.lower()
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_late_fee_payment_negative_amount(self, mocker):
        """Test 3 with a negative amount, mock should not be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        success, message = refund_late_fee_payment(
            transaction_id="txn_12345",
            amount=-5.0,
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "greater than 0" in message.lower()
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_late_fee_payment_zero_amount(self, mocker):
        """Test 4 with a zero amount, mock should not be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        success, message = refund_late_fee_payment(
            transaction_id="txn_12345",
            amount=0.0, 
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "greater than 0" in message.lower()
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_late_fee_payment_exceeds_maximum(self, mocker):
        """Test 5 with an amount not going over $15, mock should not be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        success, message = refund_late_fee_payment(
            transaction_id="txn_12345",
            amount=20.0,
            payment_gateway=mock_gateway
        )
        assert success == False
        assert "exceeds maximum" in message.lower()
        mock_gateway.refund_payment.assert_not_called()