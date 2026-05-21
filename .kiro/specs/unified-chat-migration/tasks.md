# Implementation Plan: Unified Chat Migration

## Overview

This implementation plan migrates the chat system from a legacy dual-table architecture (StoreChatMessage and RiderChatMessage) to a unified single-table architecture (ChatMessage). The migration preserves all existing data, maintains zero downtime, and consolidates all chat functionality into a maintainable codebase with real-time messaging support.

The implementation follows a phased approach: backup creation, data migration, validation, code cleanup, and monitoring. All tasks build incrementally to ensure the system remains operational throughout the migration process.

## Tasks

- [x] 1. Set up migration infrastructure and backup system
  - [x] 1.1 Create MigrationService class with backup functionality
    - Implement `create_backups()` method to export StoreChatMessage and RiderChatMessage tables to timestamped SQL files
    - Implement `verify_backups()` method to ensure backup files are readable and non-empty
    - Add logging for all backup operations with timestamps
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [x] 1.2 Create RollbackService class for disaster recovery
    - Implement `restore_legacy_tables()` method to restore from backup files
    - Implement `clear_unified_table()` method to truncate ChatMessage table
    - Implement `execute_rollback()` method to orchestrate full rollback workflow
    - Add logging for all rollback operations
    - _Requirements: 11.5, 11.6, 11.7, 11.8_

- [ ] 2. Implement data transformation and migration logic
  - [x] 2.1 Create transformation functions for legacy data
    - Implement `transform_store_chat_message()` to convert StoreChatMessage to ChatMessage format
    - Handle sender_role='buyer' case: sender_id=buyer_id, receiver_id=seller_id
    - Handle sender_role='seller' case: sender_id=seller_id, receiver_id=buyer_id
    - Preserve message, created_at, is_read, product_id; set order_id=NULL
    - Implement `transform_rider_chat_message()` to convert RiderChatMessage to ChatMessage format
    - Handle sender_role='buyer' case: sender_id=buyer_id, receiver_id=rider_id
    - Handle sender_role='rider' case: sender_id=rider_id, receiver_id=buyer_id
    - Preserve message, created_at, is_read, order_id; set product_id=NULL
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 2.5_
  
  - [-] 2.2 Implement batch migration for StoreChatMessage table
    - Implement `migrate_store_chat_messages()` method with batch processing (1000 records per batch)
    - Read records from StoreChatMessage in batches ordered by id
    - Transform each record using `transform_store_chat_message()`
    - Insert transformed records into ChatMessage table
    - Commit each batch independently to prevent transaction timeouts
    - Add 100ms pause between batches to allow other database operations
    - Log success count and error count with record IDs
    - Retry failed batches up to 3 times before logging error
    - _Requirements: 1.1, 1.6, 1.7, 1.8, 12.4, 12.5, 12.6, 12.7_
  
  - [-] 2.3 Implement batch migration for RiderChatMessage table
    - Implement `migrate_rider_chat_messages()` method with batch processing (1000 records per batch)
    - Read records from RiderChatMessage in batches ordered by id
    - Transform each record using `transform_rider_chat_message()`
    - Insert transformed records into ChatMessage table
    - Commit each batch independently to prevent transaction timeouts
    - Add 100ms pause between batches to allow other database operations
    - Log success count and error count with record IDs
    - Retry failed batches up to 3 times before logging error
    - _Requirements: 2.1, 2.6, 2.7, 2.8, 12.4, 12.5, 12.6, 12.7_

- [ ] 3. Implement data integrity validation
  - [x] 3.1 Create DataIntegrityValidator class
    - Implement `count_legacy_records()` to count StoreChatMessage and RiderChatMessage records
    - Implement `count_unified_records()` to count ChatMessage records
    - Implement `validate_record_counts()` to verify unified count equals sum of legacy counts
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [-] 3.2 Implement message content validation
    - Implement `sample_and_verify()` method to randomly sample 100 messages from legacy tables
    - For each sample, find corresponding record in ChatMessage table by matching sender_id, receiver_id, message, and created_at
    - Verify message content matches exactly
    - Verify timestamps are preserved within 1 second accuracy
    - Verify is_read status matches
    - Return list of validation errors with record IDs
    - _Requirements: 3.4, 3.5, 3.6_
  
  - [x] 3.3 Implement validation reporting
    - Implement `generate_report()` method to create comprehensive validation report
    - Include pass/fail status for each validation check
    - Include record counts: legacy total, unified total, match status
    - Include sample validation results with error details
    - Include timestamp accuracy statistics
    - Include is_read status match statistics
    - List all discrepancies with record IDs if validation fails
    - _Requirements: 3.7, 3.8_

- [~] 4. Checkpoint - Verify migration infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Remove legacy chat routes from app.py
  - [-] 5.1 Remove legacy chat endpoints
    - Remove route `/api/chat/conversations` from app.py (line 7728)
    - Remove route `/api/chat/messages/<int:other_user_id>` from app.py (line 7798)
    - Remove route `/api/chat/send` from app.py (line 7833)
    - Remove route `/api/chat/mark-read/<int:other_user_id>` from app.py (line 7926)
    - Remove route `/api/chat/unread-count` from app.py (line 7972)
    - Remove route `/api/chat/search-users` from app.py (line 7994)
    - Remove route `/api/chat/order/<int:order_id>/partner` from app.py (line 8012)
    - Verify no route conflicts remain between app.py and unified_chat_api.py
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

- [ ] 6. Remove legacy chat models from app.py
  - [ ] 6.1 Remove legacy model classes
    - Remove StoreChatMessage class definition from app.py (lines 2893-2906)
    - Remove RiderChatMessage class definition from app.py (lines 2908-2920)
    - Search for all references to StoreChatMessage in app.py and remove or update to use ChatMessage
    - Search for all references to RiderChatMessage in app.py and remove or update to use ChatMessage
    - Verify ChatMessage model exists in unified_chat_api.py
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Verify unified chat API endpoints
  - [~] 7.1 Verify buyer-seller chat functionality
    - Test POST `/api/chat/send` with buyer sending to seller (includes product_id)
    - Test POST `/api/chat/send` with seller sending to buyer (includes product_id)
    - Test GET `/api/chat/messages/<user_id>` returns messages ordered by created_at ascending
    - Test POST `/api/chat/mark-read/<user_id>` marks messages as read
    - Test GET `/api/chat/unread-count` returns correct unread count
    - Test GET `/api/chat/conversations` returns conversation list with last message and timestamp
    - Verify SocketIO emits 'new_message' event when message is sent
    - Verify SocketIO emits 'typing' and 'stop_typing' events
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [~] 7.2 Verify buyer-rider chat functionality
    - Test POST `/api/chat/send` with buyer sending to rider (includes order_id)
    - Test POST `/api/chat/send` with rider sending to buyer (includes order_id)
    - Test GET `/api/chat/messages/<user_id>` returns messages ordered by created_at ascending
    - Test POST `/api/chat/mark-read/<user_id>` marks messages as read
    - Test GET `/api/chat/unread-count` returns correct unread count
    - Test GET `/api/chat/conversations` returns conversation list with last message and timestamp
    - Verify SocketIO emits 'new_message' event when message is sent
    - Verify SocketIO emits 'typing' and 'stop_typing' events
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [ ] 8. Verify SocketIO real-time messaging
  - [~] 8.1 Test SocketIO event handling
    - Test 'join_chat' event joins user to room identified by user_id
    - Test 'new_message' event is emitted to receiver's room with complete message object
    - Test 'typing' event is emitted to receiver's room
    - Test 'stop_typing' event is emitted to receiver's room
    - Test persistent connections are maintained for active users
    - Test automatic reconnection on connection failure
    - Test concurrent messages from multiple users are handled without message loss
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [ ] 9. Verify mobile app compatibility
  - [~] 9.1 Test mobile API endpoints
    - Test mobile app can authenticate using JWT tokens in Authorization header
    - Test GET `/api/v1/chat/conversations` returns conversation lists with user names, profile photos, last message, timestamp
    - Test GET `/api/v1/chat/messages/<user_id>` returns message threads with sender identification and timestamps
    - Test POST `/api/v1/chat/send` sends messages successfully
    - Test POST `/api/v1/chat/mark-read/<user_id>` marks messages as read
    - Test GET `/api/v1/chat/unread-count` returns unread message counts
    - Test mobile app can connect to SocketIO for real-time message delivery
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_
  
  - [~] 9.2 Fix chat list real-time updates (all user roles: buyer, seller, rider)
    - Fix conversation list not updating when new messages arrive via SocketIO
    - Ensure 'new_message' event triggers conversation list refresh to show latest message
    - Update last message text and timestamp in conversation list when new message arrives
    - Move updated conversation to top of list when new message arrives
    - Ensure conversation list sorts by most recent message timestamp (descending order)
    - Fix duplicate message prevention in conversation list updates
    - Test conversation list updates in real-time without requiring manual refresh
    - Verify conversation list shows correct last message after sending or receiving messages
    - Apply fixes to all chat list screens: buyer messages screen, seller inbox, rider messages screen
  
  - [~] 9.3 Fix chat screen scroll and message display (all user roles: buyer, seller, rider)
    - Fix chat screen not scrolling to bottom when opened
    - Ensure _scrollToBottom() is called after messages load in _loadMessages()
    - Fix chat screen not showing newest messages at bottom
    - Ensure messages are sorted by created_at ascending (oldest first, newest last)
    - Fix scroll position jumping when new messages arrive
    - Ensure smooth scroll animation when new message is added
    - Fix optimistic message updates causing duplicate messages
    - Remove temporary messages correctly after real message arrives from server
    - Apply fixes to all chat screens: ChatScreen (buyer), RiderChatScreen (rider), SellerChatScreen (seller)

- [ ] 10. Verify seller inbox integration
  - [~] 10.1 Test seller inbox functionality
    - Test GET `/api/chat/conversations` returns all buyer conversations with product context
    - Test seller inbox displays unread message indicators for each conversation
    - Test POST `/api/chat/send` allows sellers to send messages
    - Test POST `/api/chat/mark-read/<user_id>` marks messages as read when seller views conversation
    - Test seller inbox updates in real-time when new messages arrive via SocketIO
    - Test seller inbox displays buyer profile information (name, photo) in conversation lists
    - Test seller inbox can filter conversations by product or show all conversations
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [~] 11. Checkpoint - Verify all functionality works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement product chat support  
  - [~] 12.1 Verify product context in chat messages
    - Test POST `/api/v1/chat/product/start` creates messages with product_id populated
    - Test chat API retrieves product information (name, image, price) for display in chat context
    - Test conversation lists group messages by product_id
    - Test multiple conversations with same seller about different products work correctly
    - Test conversation lists display product thumbnails
    - Test chat history is preserved when product is deleted (product marked as unavailable)
    - Test sellers can view all product-related chats from seller dashboard
    - Test conversations can be filtered by product_id
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

- [ ] 13. Implement order chat support
  - [~] 13.1 Verify order context in chat messages
    - Test chat messages with order_id populated are created correctly
    - Test chat API retrieves order information (order number, status, delivery address) for display in chat context
    - Test conversation lists group messages by order_id
    - Test buyers can only chat with riders for orders assigned to those riders
    - Test conversation lists display order status
    - Test chat history is preserved when order is completed (order marked as completed)
    - Test riders can view all order-related chats from rider dashboard
    - Test conversations can be filtered by order_id
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_

- [ ] 14. Implement message search and filtering
  - [~] 14.1 Create search and filter functionality
    - Implement message search by text content using case-insensitive matching
    - Implement conversation filtering by user name
    - Implement conversation filtering by product name
    - Implement conversation filtering by order number
    - Return search results ordered by relevance (exact matches first, then partial matches)
    - Highlight search terms in message results
    - Limit search results to messages where current user is sender or receiver
    - Optimize search to return results within 500 milliseconds for databases with up to 100,000 messages
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

- [ ] 15. Implement unread message tracking
  - [~] 15.1 Create unread message tracking functionality
    - Implement unread count query: count messages where receiver_id=current_user_id and is_read=false
    - Group unread counts by sender_id
    - Return total unread count across all conversations
    - Mark all messages in conversation as read when user views conversation
    - Update unread counts in real-time via SocketIO
    - Display unread indicators (badges) in conversation lists
    - Persist unread status across user sessions
    - Optimize unread count calculation to complete within 100 milliseconds
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

- [ ] 16. Implement user profile integration
  - [~] 16.1 Create user profile integration for chat
    - Retrieve user profile information (name, profile_photo_url) for all conversation participants
    - Display profile photos in conversation lists
    - Display profile photos next to each message in message threads
    - Display user names in conversation lists
    - Display user roles (buyer, seller, rider) in conversation lists
    - Display default avatar if user has no profile photo
    - Cache profile information to reduce database queries (5 minute cache)
    - Update profile information when users change their profiles
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8_

- [ ] 17. Implement error handling and logging
  - [~] 17.1 Add comprehensive error handling
    - Return error response with descriptive message if message fails to send
    - Log database query failures with timestamp, user_id, and query details
    - Log SocketIO connection failures and attempt to reconnect
    - Log all API requests with endpoint, user_id, and response status
    - Log all migration operations with record counts and timestamps
    - Log all validation failures with specific discrepancies
    - Store logs in rotating file with maximum size of 100MB
    - Send critical errors to error monitoring service
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8_

- [ ] 18. Implement performance optimizations
  - [~] 18.1 Add database indexes and caching
    - Verify database indexes exist on sender_id, receiver_id, created_at columns
    - Implement pagination for message threads (50 messages per page)
    - Implement pagination for conversation lists (20 conversations per page)
    - Implement caching for user profiles (5 minute cache)
    - Implement caching for product information (5 minute cache)
    - Configure database connection pooling with pool size of 20
    - Optimize conversation list query to return within 200 milliseconds
    - Optimize message thread query to return within 300 milliseconds
    - Optimize message sending to complete within 100 milliseconds
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8_

- [ ] 19. Implement security and authentication
  - [~] 19.1 Add security measures
    - Verify all API requests authenticate using JWT tokens
    - Verify users can only access conversations where they are sender or receiver
    - Reject requests with invalid or expired JWT tokens with HTTP 401 status
    - Sanitize message content to prevent XSS attacks
    - Validate all input parameters (user_id, message length, product_id, order_id)
    - Limit message length to 5000 characters
    - Implement rate limiting: 10 messages per minute per user
    - Log all authentication failures with user_id and IP address
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8_

- [ ] 20. Create migration orchestration script
  - [~] 20.1 Create run_migration.py script
    - Implement `run_full_migration()` function that orchestrates all migration steps
    - Step 1: Create backups using MigrationService.create_backups()
    - Step 2: Verify backups are readable and non-empty
    - Step 3: Run migrate_store_chat_messages()
    - Step 4: Run migrate_rider_chat_messages()
    - Step 5: Run DataIntegrityValidator.generate_report()
    - Step 6: If validation passes, log success and exit
    - Step 7: If validation fails, trigger RollbackService.execute_rollback()
    - Add command-line arguments for dry-run mode and batch size configuration
    - _Requirements: 1.1-1.8, 2.1-2.8, 3.1-3.8, 11.1-11.8, 12.1-12.8_

- [~] 21. Final checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- This implementation plan focuses on code-level tasks that can be executed by a coding agent
- All tasks reference specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- The migration follows a phased approach: backup → migrate → validate → cleanup → monitor
- Zero downtime is maintained by keeping legacy system operational during migration
- Rollback capability ensures system can be restored if migration fails
- All chat functionality (buyer-seller, buyer-rider, real-time messaging) is verified through testing tasks

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.1"] },
    { "id": 3, "tasks": ["3.2", "3.3"] },
    { "id": 4, "tasks": ["5.1", "6.1"] },
    { "id": 5, "tasks": ["7.1", "7.2", "8.1"] },
    { "id": 6, "tasks": ["9.1", "10.1"] },
    { "id": 7, "tasks": ["9.2", "9.3"] },
    { "id": 8, "tasks": ["12.1", "13.1"] },
    { "id": 9, "tasks": ["14.1", "15.1", "16.1"] },
    { "id": 10, "tasks": ["17.1", "18.1", "19.1"] },
    { "id": 11, "tasks": ["20.1"] }
  ]
}
```
