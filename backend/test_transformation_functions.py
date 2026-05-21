"""
Unit tests for transformation functions in migration_service.py

Tests the transform_store_chat_message() and transform_rider_chat_message()
functions to ensure they correctly convert legacy chat messages to the unified
ChatMessage format.

Requirements: 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 2.5
"""

import pytest
from datetime import datetime
from migration_service import transform_store_chat_message, transform_rider_chat_message


# Mock classes to simulate database models
class MockStoreChatMessage:
    """Mock StoreChatMessage model for testing"""
    def __init__(self, buyer_id, seller_id, sender_role, message, product_id, is_read, created_at):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.sender_role = sender_role
        self.message = message
        self.product_id = product_id
        self.is_read = is_read
        self.created_at = created_at


class MockRiderChatMessage:
    """Mock RiderChatMessage model for testing"""
    def __init__(self, buyer_id, rider_id, sender_role, message, order_id, is_read, created_at):
        self.buyer_id = buyer_id
        self.rider_id = rider_id
        self.sender_role = sender_role
        self.message = message
        self.order_id = order_id
        self.is_read = is_read
        self.created_at = created_at


class TestTransformStoreChatMessage:
    """Test suite for transform_store_chat_message function"""
    
    def test_buyer_sender_mapping(self):
        """Test that buyer sender_role correctly maps to sender_id=buyer_id, receiver_id=seller_id"""
        # Requirement 1.2: WHEN sender_role='buyer', sender_id=buyer_id, receiver_id=seller_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Hello seller',
            product_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['sender_id'] == 10, "Buyer sender_role should map sender_id to buyer_id"
        assert result['receiver_id'] == 20, "Buyer sender_role should map receiver_id to seller_id"
    
    def test_seller_sender_mapping(self):
        """Test that seller sender_role correctly maps to sender_id=seller_id, receiver_id=buyer_id"""
        # Requirement 1.3: WHEN sender_role='seller', sender_id=seller_id, receiver_id=buyer_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='seller',
            message='Hello buyer',
            product_id=5,
            is_read=True,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['sender_id'] == 20, "Seller sender_role should map sender_id to seller_id"
        assert result['receiver_id'] == 10, "Seller sender_role should map receiver_id to buyer_id"
    
    def test_preserve_message_content(self):
        """Test that message text is preserved during transformation"""
        # Requirement 1.4: Preserve message text
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        message_text = "This is a test message with special chars: !@#$%"
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message=message_text,
            product_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['message'] == message_text, "Message text should be preserved"
    
    def test_preserve_created_at(self):
        """Test that created_at timestamp is preserved during transformation"""
        # Requirement 1.4: Preserve created_at timestamp
        timestamp = datetime(2024, 1, 15, 10, 30, 45)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['created_at'] == timestamp, "created_at timestamp should be preserved"
    
    def test_preserve_is_read_status(self):
        """Test that is_read status is preserved during transformation"""
        # Requirement 1.4: Preserve is_read status
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        # Test with is_read=False
        legacy_msg_unread = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=5,
            is_read=False,
            created_at=timestamp
        )
        result_unread = transform_store_chat_message(legacy_msg_unread)
        assert result_unread['is_read'] == False, "is_read=False should be preserved"
        
        # Test with is_read=True
        legacy_msg_read = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=5,
            is_read=True,
            created_at=timestamp
        )
        result_read = transform_store_chat_message(legacy_msg_read)
        assert result_read['is_read'] == True, "is_read=True should be preserved"
    
    def test_preserve_product_id(self):
        """Test that product_id is preserved during transformation"""
        # Requirement 1.4: Preserve product_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=42,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['product_id'] == 42, "product_id should be preserved"
    
    def test_product_id_null(self):
        """Test that product_id=None is preserved"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=None,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['product_id'] is None, "product_id=None should be preserved"
    
    def test_order_id_set_to_null(self):
        """Test that order_id is set to NULL for StoreChatMessage"""
        # Requirement 1.5: Set order_id=NULL
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=10,
            seller_id=20,
            sender_role='buyer',
            message='Test',
            product_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result['order_id'] is None, "order_id should be set to NULL for StoreChatMessage"
    
    def test_complete_transformation_buyer_sender(self):
        """Test complete transformation with buyer as sender"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=100,
            seller_id=200,
            sender_role='buyer',
            message='Do you have this in stock?',
            product_id=15,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result == {
            'sender_id': 100,
            'receiver_id': 200,
            'message': 'Do you have this in stock?',
            'product_id': 15,
            'order_id': None,
            'is_read': False,
            'created_at': timestamp
        }, "Complete transformation should match expected output"
    
    def test_complete_transformation_seller_sender(self):
        """Test complete transformation with seller as sender"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockStoreChatMessage(
            buyer_id=100,
            seller_id=200,
            sender_role='seller',
            message='Yes, we have 5 in stock',
            product_id=15,
            is_read=True,
            created_at=timestamp
        )
        
        result = transform_store_chat_message(legacy_msg)
        
        assert result == {
            'sender_id': 200,
            'receiver_id': 100,
            'message': 'Yes, we have 5 in stock',
            'product_id': 15,
            'order_id': None,
            'is_read': True,
            'created_at': timestamp
        }, "Complete transformation should match expected output"


class TestTransformRiderChatMessage:
    """Test suite for transform_rider_chat_message function"""
    
    def test_buyer_sender_mapping(self):
        """Test that buyer sender_role correctly maps to sender_id=buyer_id, receiver_id=rider_id"""
        # Requirement 2.2: WHEN sender_role='buyer', sender_id=buyer_id, receiver_id=rider_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Where is my order?',
            order_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['sender_id'] == 10, "Buyer sender_role should map sender_id to buyer_id"
        assert result['receiver_id'] == 30, "Buyer sender_role should map receiver_id to rider_id"
    
    def test_rider_sender_mapping(self):
        """Test that rider sender_role correctly maps to sender_id=rider_id, receiver_id=buyer_id"""
        # Requirement 2.3: WHEN sender_role='rider', sender_id=rider_id, receiver_id=buyer_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='rider',
            message='I am on my way',
            order_id=5,
            is_read=True,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['sender_id'] == 30, "Rider sender_role should map sender_id to rider_id"
        assert result['receiver_id'] == 10, "Rider sender_role should map receiver_id to buyer_id"
    
    def test_preserve_message_content(self):
        """Test that message text is preserved during transformation"""
        # Requirement 2.4: Preserve message text
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        message_text = "I will arrive in 10 minutes"
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='rider',
            message=message_text,
            order_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['message'] == message_text, "Message text should be preserved"
    
    def test_preserve_created_at(self):
        """Test that created_at timestamp is preserved during transformation"""
        # Requirement 2.4: Preserve created_at timestamp
        timestamp = datetime(2024, 1, 15, 10, 30, 45)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['created_at'] == timestamp, "created_at timestamp should be preserved"
    
    def test_preserve_is_read_status(self):
        """Test that is_read status is preserved during transformation"""
        # Requirement 2.4: Preserve is_read status
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        # Test with is_read=False
        legacy_msg_unread = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=5,
            is_read=False,
            created_at=timestamp
        )
        result_unread = transform_rider_chat_message(legacy_msg_unread)
        assert result_unread['is_read'] == False, "is_read=False should be preserved"
        
        # Test with is_read=True
        legacy_msg_read = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=5,
            is_read=True,
            created_at=timestamp
        )
        result_read = transform_rider_chat_message(legacy_msg_read)
        assert result_read['is_read'] == True, "is_read=True should be preserved"
    
    def test_preserve_order_id(self):
        """Test that order_id is preserved during transformation"""
        # Requirement 2.4: Preserve order_id
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=99,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['order_id'] == 99, "order_id should be preserved"
    
    def test_order_id_null(self):
        """Test that order_id=None is preserved"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=None,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['order_id'] is None, "order_id=None should be preserved"
    
    def test_product_id_set_to_null(self):
        """Test that product_id is set to NULL for RiderChatMessage"""
        # Requirement 2.5: Set product_id=NULL
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=10,
            rider_id=30,
            sender_role='buyer',
            message='Test',
            order_id=5,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result['product_id'] is None, "product_id should be set to NULL for RiderChatMessage"
    
    def test_complete_transformation_buyer_sender(self):
        """Test complete transformation with buyer as sender"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=100,
            rider_id=300,
            sender_role='buyer',
            message='Where is my delivery?',
            order_id=50,
            is_read=False,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result == {
            'sender_id': 100,
            'receiver_id': 300,
            'message': 'Where is my delivery?',
            'product_id': None,
            'order_id': 50,
            'is_read': False,
            'created_at': timestamp
        }, "Complete transformation should match expected output"
    
    def test_complete_transformation_rider_sender(self):
        """Test complete transformation with rider as sender"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        legacy_msg = MockRiderChatMessage(
            buyer_id=100,
            rider_id=300,
            sender_role='rider',
            message='Arriving in 5 minutes',
            order_id=50,
            is_read=True,
            created_at=timestamp
        )
        
        result = transform_rider_chat_message(legacy_msg)
        
        assert result == {
            'sender_id': 300,
            'receiver_id': 100,
            'message': 'Arriving in 5 minutes',
            'product_id': None,
            'order_id': 50,
            'is_read': True,
            'created_at': timestamp
        }, "Complete transformation should match expected output"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
