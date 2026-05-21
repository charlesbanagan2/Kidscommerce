# Requirements Document: Unified Chat Migration

## Introduction

This document specifies the requirements for migrating the chat system from the legacy dual-table architecture (StoreChatMessage and RiderChatMessage) to the unified single-table architecture (ChatMessage). The migration must preserve all existing chat data, maintain zero downtime, ensure no message loss, and provide a seamless transition for all users (buyers, sellers, and riders) across web and mobile platforms.

The current system has two separate implementations running simultaneously, causing code duplication, maintenance overhead, and route conflicts. The unified system consolidates all chat functionality into a single, maintainable codebase with support for product chat, order chat, and real-time messaging via SocketIO.

## Glossary

- **Legacy_Chat_System**: The old dual-table chat implementation using StoreChatMessage (buyer ↔ seller) and RiderChatMessage (buyer ↔ rider) tables, located in app.py lines 2893-2920 (models) and 7728-7920 (routes)
- **Unified_Chat_System**: The new single-table chat implementation using ChatMessage table, located in unified_chat_api.py with routes `/api/chat/*` and `/api/v1/chat/*`
- **Migration_Service**: The component responsible for transferring data from legacy tables to the unified table
- **Chat_API**: The REST API endpoints for chat operations (send message, get conversations, mark as read, etc.)
- **SocketIO_Service**: The real-time messaging service for live chat updates and typing indicators
- **Seller_Inbox**: The web interface where sellers view and respond to buyer messages
- **Mobile_App**: The mobile application used by buyers, sellers, and riders
- **StoreChatMessage_Table**: Legacy database table storing buyer ↔ seller chat messages
- **RiderChatMessage_Table**: Legacy database table storing buyer ↔ rider chat messages
- **ChatMessage_Table**: Unified database table storing all user-to-user chat messages
- **Data_Integrity_Validator**: Component that verifies data accuracy after migration
- **Rollback_Service**: Component that restores the system to pre-migration state if migration fails

## Requirements

### Requirement 1: Data Migration from StoreChatMessage Table

**User Story:** As a system administrator, I want to migrate all buyer-seller chat messages from the StoreChatMessage table to the ChatMessage table, so that all historical conversations are preserved in the unified system.

#### Acceptance Criteria

1. THE Migration_Service SHALL read all records from the StoreChatMessage_Table
2. WHEN a StoreChatMessage record has sender_role='buyer', THE Migration_Service SHALL create a ChatMessage record with sender_id=buyer_id and receiver_id=seller_id
3. WHEN a StoreChatMessage record has sender_role='seller', THE Migration_Service SHALL create a ChatMessage record with sender_id=seller_id and receiver_id=buyer_id
4. THE Migration_Service SHALL preserve the message text, created_at timestamp, is_read status, and product_id for each migrated message
5. THE Migration_Service SHALL set order_id to NULL for all StoreChatMessage migrations
6. FOR ALL StoreChatMessage records, THE Migration_Service SHALL create exactly one corresponding ChatMessage record (one-to-one mapping)
7. THE Migration_Service SHALL log the count of successfully migrated StoreChatMessage records
8. IF a StoreChatMessage record fails to migrate, THEN THE Migration_Service SHALL log the error with the record ID and continue processing remaining records

### Requirement 2: Data Migration from RiderChatMessage Table

**User Story:** As a system administrator, I want to migrate all buyer-rider chat messages from the RiderChatMessage table to the ChatMessage table, so that all delivery-related conversations are preserved in the unified system.

#### Acceptance Criteria

1. THE Migration_Service SHALL read all records from the RiderChatMessage_Table
2. WHEN a RiderChatMessage record has sender_role='buyer', THE Migration_Service SHALL create a ChatMessage record with sender_id=buyer_id and receiver_id=rider_id
3. WHEN a RiderChatMessage record has sender_role='rider', THE Migration_Service SHALL create a ChatMessage record with sender_id=rider_id and receiver_id=buyer_id
4. THE Migration_Service SHALL preserve the message text, created_at timestamp, is_read status, and order_id for each migrated message
5. THE Migration_Service SHALL set product_id to NULL for all RiderChatMessage migrations
6. FOR ALL RiderChatMessage records, THE Migration_Service SHALL create exactly one corresponding ChatMessage record (one-to-one mapping)
7. THE Migration_Service SHALL log the count of successfully migrated RiderChatMessage records
8. IF a RiderChatMessage record fails to migrate, THEN THE Migration_Service SHALL log the error with the record ID and continue processing remaining records

### Requirement 3: Data Integrity Validation

**User Story:** As a system administrator, I want to verify that all chat messages were migrated correctly, so that I can confirm no data was lost or corrupted during migration.

#### Acceptance Criteria

1. THE Data_Integrity_Validator SHALL count the total records in StoreChatMessage_Table and RiderChatMessage_Table before migration
2. THE Data_Integrity_Validator SHALL count the total records in ChatMessage_Table after migration
3. THE Data_Integrity_Validator SHALL verify that ChatMessage_Table record count equals the sum of StoreChatMessage_Table and RiderChatMessage_Table record counts
4. THE Data_Integrity_Validator SHALL randomly sample 100 messages from legacy tables and verify their content matches the migrated records in ChatMessage_Table
5. THE Data_Integrity_Validator SHALL verify that all timestamps are preserved within 1 second accuracy
6. THE Data_Integrity_Validator SHALL verify that all is_read statuses match between legacy and unified tables
7. THE Data_Integrity_Validator SHALL generate a validation report with pass/fail status and detailed statistics
8. IF validation fails, THEN THE Data_Integrity_Validator SHALL list all discrepancies with record IDs

### Requirement 4: Legacy Chat Route Removal

**User Story:** As a developer, I want to remove the old chat routes from app.py, so that there are no route conflicts and the codebase is cleaner.

#### Acceptance Criteria

1. THE Chat_API SHALL remove the route `/api/chat/conversations` from app.py (line 7728)
2. THE Chat_API SHALL remove the route `/api/chat/messages/<int:other_user_id>` from app.py (line 7798)
3. THE Chat_API SHALL remove the route `/api/chat/send` from app.py (line 7833)
4. THE Chat_API SHALL remove the route `/api/chat/mark-read/<int:other_user_id>` from app.py (line 7926)
5. THE Chat_API SHALL remove the route `/api/chat/unread-count` from app.py (line 7972)
6. THE Chat_API SHALL remove the route `/api/chat/search-users` from app.py (line 7994)
7. THE Chat_API SHALL remove the route `/api/chat/order/<int:order_id>/partner` from app.py (line 8012)
8. THE Chat_API SHALL preserve all routes in unified_chat_api.py with paths `/api/chat/*` and `/api/v1/chat/*`

### Requirement 5: Legacy Chat Model Removal

**User Story:** As a developer, I want to remove the old chat models from app.py, so that the database schema is simplified and there is no confusion about which models to use.

#### Acceptance Criteria

1. THE Chat_API SHALL remove the StoreChatMessage class definition from app.py (lines 2893-2906)
2. THE Chat_API SHALL remove the RiderChatMessage class definition from app.py (lines 2908-2920)
3. THE Chat_API SHALL preserve the ChatMessage model in unified_chat_api.py
4. THE Chat_API SHALL verify that no other code in app.py references StoreChatMessage or RiderChatMessage
5. IF any code references the legacy models, THEN THE Chat_API SHALL update those references to use ChatMessage or remove the code

### Requirement 6: Buyer-Seller Chat Functionality

**User Story:** As a buyer, I want to chat with sellers about products, so that I can ask questions before making a purchase.

#### Acceptance Criteria

1. WHEN a buyer sends a message to a seller, THE Unified_Chat_System SHALL create a ChatMessage record with sender_id=buyer_id, receiver_id=seller_id, and the specified product_id
2. WHEN a seller sends a message to a buyer, THE Unified_Chat_System SHALL create a ChatMessage record with sender_id=seller_id, receiver_id=buyer_id, and the specified product_id
3. THE Unified_Chat_System SHALL retrieve all messages between a buyer and seller ordered by created_at timestamp ascending
4. THE Unified_Chat_System SHALL mark messages as read when the receiver views the conversation
5. THE Unified_Chat_System SHALL calculate unread message count for each conversation
6. THE Unified_Chat_System SHALL emit SocketIO events when new messages are sent in buyer-seller conversations
7. THE Unified_Chat_System SHALL support typing indicators for buyer-seller conversations
8. THE Unified_Chat_System SHALL return conversation lists showing the most recent message and timestamp for each buyer-seller pair

### Requirement 7: Buyer-Rider Chat Functionality

**User Story:** As a buyer, I want to chat with riders about my delivery, so that I can coordinate delivery details and track my order.

#### Acceptance Criteria

1. WHEN a buyer sends a message to a rider, THE Unified_Chat_System SHALL create a ChatMessage record with sender_id=buyer_id, receiver_id=rider_id, and the specified order_id
2. WHEN a rider sends a message to a buyer, THE Unified_Chat_System SHALL create a ChatMessage record with sender_id=rider_id, receiver_id=buyer_id, and the specified order_id
3. THE Unified_Chat_System SHALL retrieve all messages between a buyer and rider ordered by created_at timestamp ascending
4. THE Unified_Chat_System SHALL mark messages as read when the receiver views the conversation
5. THE Unified_Chat_System SHALL calculate unread message count for each conversation
6. THE Unified_Chat_System SHALL emit SocketIO events when new messages are sent in buyer-rider conversations
7. THE Unified_Chat_System SHALL support typing indicators for buyer-rider conversations
8. THE Unified_Chat_System SHALL return conversation lists showing the most recent message and timestamp for each buyer-rider pair

### Requirement 8: Real-Time Messaging via SocketIO

**User Story:** As a user, I want to receive messages instantly without refreshing the page, so that I can have real-time conversations.

#### Acceptance Criteria

1. WHEN a user sends a message, THE SocketIO_Service SHALL emit a 'new_message' event to the receiver's room
2. THE SocketIO_Service SHALL include the complete message object (id, sender_id, receiver_id, message, created_at, is_read) in the event payload
3. WHEN a user connects to the chat, THE SocketIO_Service SHALL join them to a room identified by their user_id
4. WHEN a user starts typing, THE SocketIO_Service SHALL emit a 'typing' event to the receiver's room
5. WHEN a user stops typing, THE SocketIO_Service SHALL emit a 'stop_typing' event to the receiver's room
6. THE SocketIO_Service SHALL maintain persistent connections for all active chat users
7. IF a SocketIO connection fails, THEN THE SocketIO_Service SHALL attempt to reconnect automatically
8. THE SocketIO_Service SHALL handle concurrent messages from multiple users without message loss

### Requirement 9: Mobile App Compatibility

**User Story:** As a mobile app user, I want the chat feature to work seamlessly on my phone, so that I can communicate with sellers and riders on the go.

#### Acceptance Criteria

1. THE Mobile_App SHALL use the `/api/v1/chat/*` endpoints from unified_chat_api.py
2. THE Mobile_App SHALL authenticate using JWT tokens in the Authorization header
3. THE Mobile_App SHALL display conversation lists with user names, profile photos, last message, and timestamp
4. THE Mobile_App SHALL display message threads with sender identification and timestamps
5. THE Mobile_App SHALL send messages using the `/api/v1/chat/send` endpoint
6. THE Mobile_App SHALL mark messages as read using the `/api/v1/chat/mark-read/<user_id>` endpoint
7. THE Mobile_App SHALL display unread message counts using the `/api/v1/chat/unread-count` endpoint
8. THE Mobile_App SHALL connect to SocketIO for real-time message delivery

### Requirement 10: Seller Inbox Integration

**User Story:** As a seller, I want to view and respond to buyer messages in my seller inbox, so that I can manage customer inquiries efficiently.

#### Acceptance Criteria

1. THE Seller_Inbox SHALL retrieve conversations using the `/api/chat/conversations` endpoint from unified_chat_api.py
2. THE Seller_Inbox SHALL display all buyer conversations with product context
3. THE Seller_Inbox SHALL show unread message indicators for each conversation
4. THE Seller_Inbox SHALL allow sellers to send messages using the `/api/chat/send` endpoint
5. THE Seller_Inbox SHALL mark messages as read when the seller views a conversation
6. THE Seller_Inbox SHALL update in real-time when new messages arrive via SocketIO
7. THE Seller_Inbox SHALL display buyer profile information (name, photo) in conversation lists
8. THE Seller_Inbox SHALL filter conversations by product or show all conversations

### Requirement 11: Database Backup and Rollback

**User Story:** As a system administrator, I want to backup the legacy chat tables before migration, so that I can restore the system if the migration fails.

#### Acceptance Criteria

1. THE Migration_Service SHALL create a backup of StoreChatMessage_Table before starting migration
2. THE Migration_Service SHALL create a backup of RiderChatMessage_Table before starting migration
3. THE Migration_Service SHALL store backups with timestamps in the filename (e.g., store_chat_message_backup_20240115_143022.sql)
4. THE Migration_Service SHALL verify that backup files are readable and non-empty
5. IF migration validation fails, THEN THE Rollback_Service SHALL restore StoreChatMessage_Table and RiderChatMessage_Table from backups
6. THE Rollback_Service SHALL clear the ChatMessage_Table if rollback is triggered
7. THE Rollback_Service SHALL restore the legacy chat routes in app.py if rollback is triggered
8. THE Rollback_Service SHALL log all rollback operations with timestamps and reasons

### Requirement 12: Zero Downtime Migration

**User Story:** As a user, I want to continue using the chat feature during migration, so that my conversations are not interrupted.

#### Acceptance Criteria

1. WHILE migration is in progress, THE Unified_Chat_System SHALL accept new messages and store them in ChatMessage_Table
2. WHILE migration is in progress, THE Legacy_Chat_System SHALL remain accessible for reading historical messages
3. THE Migration_Service SHALL run during low-traffic hours to minimize performance impact
4. THE Migration_Service SHALL process records in batches of 1000 to avoid database locks
5. THE Migration_Service SHALL commit each batch independently to prevent transaction timeouts
6. IF a batch fails, THEN THE Migration_Service SHALL retry the batch up to 3 times before logging an error
7. THE Migration_Service SHALL pause for 100 milliseconds between batches to allow other database operations
8. THE Migration_Service SHALL complete within 2 hours for databases with up to 100,000 messages

### Requirement 13: Product Chat Support

**User Story:** As a buyer, I want to chat with sellers about specific products, so that I can ask questions about product details, availability, and pricing.

#### Acceptance Criteria

1. WHEN a buyer initiates a chat from a product page, THE Unified_Chat_System SHALL create messages with the product_id field populated
2. THE Unified_Chat_System SHALL retrieve product information (name, image, price) for display in chat context
3. THE Unified_Chat_System SHALL group messages by product_id in conversation lists
4. THE Unified_Chat_System SHALL allow multiple conversations with the same seller about different products
5. THE Unified_Chat_System SHALL display product thumbnails in conversation lists
6. WHEN a product is deleted, THE Unified_Chat_System SHALL preserve chat history but mark the product as unavailable
7. THE Unified_Chat_System SHALL allow sellers to view all product-related chats from their seller dashboard
8. THE Unified_Chat_System SHALL filter conversations by product_id when requested

### Requirement 14: Order Chat Support

**User Story:** As a buyer, I want to chat with riders about my order delivery, so that I can provide delivery instructions and track my package.

#### Acceptance Criteria

1. WHEN a buyer initiates a chat with a rider, THE Unified_Chat_System SHALL create messages with the order_id field populated
2. THE Unified_Chat_System SHALL retrieve order information (order number, status, delivery address) for display in chat context
3. THE Unified_Chat_System SHALL group messages by order_id in conversation lists
4. THE Unified_Chat_System SHALL allow buyers to chat with riders only for orders assigned to those riders
5. THE Unified_Chat_System SHALL display order status in conversation lists
6. WHEN an order is completed, THE Unified_Chat_System SHALL preserve chat history but mark the order as completed
7. THE Unified_Chat_System SHALL allow riders to view all order-related chats from their rider dashboard
8. THE Unified_Chat_System SHALL filter conversations by order_id when requested

### Requirement 15: Message Search and Filtering

**User Story:** As a user, I want to search for specific messages or conversations, so that I can quickly find important information.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL search messages by text content using case-insensitive matching
2. THE Unified_Chat_System SHALL filter conversations by user name
3. THE Unified_Chat_System SHALL filter conversations by product name
4. THE Unified_Chat_System SHALL filter conversations by order number
5. THE Unified_Chat_System SHALL return search results ordered by relevance (exact matches first, then partial matches)
6. THE Unified_Chat_System SHALL highlight search terms in message results
7. THE Unified_Chat_System SHALL limit search results to messages where the current user is sender or receiver
8. THE Unified_Chat_System SHALL return search results within 500 milliseconds for databases with up to 100,000 messages

### Requirement 16: Unread Message Tracking

**User Story:** As a user, I want to see how many unread messages I have, so that I know when someone has sent me a new message.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL count unread messages where receiver_id equals current user_id and is_read equals false
2. THE Unified_Chat_System SHALL group unread counts by sender_id
3. THE Unified_Chat_System SHALL return total unread count across all conversations
4. WHEN a user views a conversation, THE Unified_Chat_System SHALL mark all messages in that conversation as read
5. THE Unified_Chat_System SHALL update unread counts in real-time via SocketIO
6. THE Unified_Chat_System SHALL display unread indicators (badges) in conversation lists
7. THE Unified_Chat_System SHALL persist unread status across user sessions
8. THE Unified_Chat_System SHALL calculate unread counts within 100 milliseconds

### Requirement 17: User Profile Integration

**User Story:** As a user, I want to see profile photos and names in my chat conversations, so that I can easily identify who I'm talking to.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL retrieve user profile information (name, profile_photo_url) for all conversation participants
2. THE Unified_Chat_System SHALL display profile photos in conversation lists
3. THE Unified_Chat_System SHALL display profile photos next to each message in message threads
4. THE Unified_Chat_System SHALL display user names in conversation lists
5. THE Unified_Chat_System SHALL display user roles (buyer, seller, rider) in conversation lists
6. IF a user has no profile photo, THEN THE Unified_Chat_System SHALL display a default avatar
7. THE Unified_Chat_System SHALL cache profile information to reduce database queries
8. THE Unified_Chat_System SHALL update profile information when users change their profiles

### Requirement 18: Error Handling and Logging

**User Story:** As a developer, I want comprehensive error handling and logging, so that I can diagnose and fix issues quickly.

#### Acceptance Criteria

1. IF a message fails to send, THEN THE Unified_Chat_System SHALL return an error response with a descriptive message
2. IF a database query fails, THEN THE Unified_Chat_System SHALL log the error with timestamp, user_id, and query details
3. IF a SocketIO connection fails, THEN THE SocketIO_Service SHALL log the error and attempt to reconnect
4. THE Unified_Chat_System SHALL log all API requests with endpoint, user_id, and response status
5. THE Unified_Chat_System SHALL log all migration operations with record counts and timestamps
6. THE Unified_Chat_System SHALL log all validation failures with specific discrepancies
7. THE Unified_Chat_System SHALL store logs in a rotating file with maximum size of 100MB
8. THE Unified_Chat_System SHALL send critical errors to an error monitoring service

### Requirement 19: Performance Optimization

**User Story:** As a user, I want the chat system to load quickly and respond instantly, so that I can have smooth conversations.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL return conversation lists within 200 milliseconds
2. THE Unified_Chat_System SHALL return message threads within 300 milliseconds
3. THE Unified_Chat_System SHALL send messages within 100 milliseconds
4. THE Unified_Chat_System SHALL use database indexes on sender_id, receiver_id, and created_at columns
5. THE Unified_Chat_System SHALL paginate message threads with 50 messages per page
6. THE Unified_Chat_System SHALL paginate conversation lists with 20 conversations per page
7. THE Unified_Chat_System SHALL cache frequently accessed data (user profiles, product info) for 5 minutes
8. THE Unified_Chat_System SHALL use connection pooling for database connections with a pool size of 20

### Requirement 20: Security and Authentication

**User Story:** As a user, I want my chat messages to be private and secure, so that only authorized users can read my conversations.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL authenticate all API requests using JWT tokens
2. THE Unified_Chat_System SHALL verify that users can only access conversations where they are sender or receiver
3. THE Unified_Chat_System SHALL reject requests with invalid or expired JWT tokens with HTTP 401 status
4. THE Unified_Chat_System SHALL sanitize message content to prevent XSS attacks
5. THE Unified_Chat_System SHALL validate all input parameters (user_id, message length, product_id, order_id)
6. THE Unified_Chat_System SHALL limit message length to 5000 characters
7. THE Unified_Chat_System SHALL rate limit message sending to 10 messages per minute per user
8. THE Unified_Chat_System SHALL log all authentication failures with user_id and IP address

### Requirement 21: Migration Testing

**User Story:** As a QA engineer, I want comprehensive tests for the migration process, so that I can verify the system works correctly after migration.

#### Acceptance Criteria

1. THE Migration_Service SHALL include a test suite that verifies data migration accuracy
2. THE Migration_Service SHALL include a test suite that verifies API endpoint functionality
3. THE Migration_Service SHALL include a test suite that verifies SocketIO real-time messaging
4. THE Migration_Service SHALL include a test suite that verifies mobile app compatibility
5. THE Migration_Service SHALL include a test suite that verifies seller inbox integration
6. THE Migration_Service SHALL include a test suite that verifies rollback functionality
7. THE Migration_Service SHALL include a test suite that verifies performance under load (1000 concurrent users)
8. THE Migration_Service SHALL generate a test report with pass/fail status for all test cases

### Requirement 22: Documentation and Training

**User Story:** As a developer, I want comprehensive documentation for the unified chat system, so that I can maintain and extend it in the future.

#### Acceptance Criteria

1. THE Unified_Chat_System SHALL include API documentation with endpoint descriptions, parameters, and response formats
2. THE Unified_Chat_System SHALL include database schema documentation with table structures and relationships
3. THE Unified_Chat_System SHALL include SocketIO event documentation with event names and payload formats
4. THE Unified_Chat_System SHALL include migration guide with step-by-step instructions
5. THE Unified_Chat_System SHALL include troubleshooting guide with common issues and solutions
6. THE Unified_Chat_System SHALL include code comments explaining complex logic
7. THE Unified_Chat_System SHALL include architecture diagrams showing system components and data flow
8. THE Unified_Chat_System SHALL include deployment guide with environment variables and configuration

## Notes

### Migration Strategy

The migration will follow a phased approach:

1. **Phase 1: Preparation** - Backup legacy tables, verify unified system is ready
2. **Phase 2: Data Migration** - Migrate StoreChatMessage and RiderChatMessage to ChatMessage
3. **Phase 3: Validation** - Verify data integrity and run test suite
4. **Phase 4: Code Cleanup** - Remove legacy routes and models from app.py
5. **Phase 5: Monitoring** - Monitor system for 48 hours, ready to rollback if needed

### Rollback Criteria

The system will be rolled back if:
- Data validation fails (record counts don't match)
- More than 5% of messages fail to migrate
- Critical functionality breaks (message sending, real-time updates)
- Performance degrades by more than 50%

### Success Metrics

The migration is considered successful when:
- 100% of messages are migrated with data integrity verified
- All API endpoints return correct responses
- Real-time messaging works for all user types
- Mobile app and seller inbox function correctly
- No critical errors in logs for 48 hours post-migration
