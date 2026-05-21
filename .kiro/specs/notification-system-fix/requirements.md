# Requirements Document: Notification System Bug Fixes and Enhancements

## Introduction

This document specifies the requirements for fixing bugs and implementing a complete Shopee-style notification system for a multi-role e-commerce platform. The system currently has errors and bugs affecting notifications for Seller, Rider, Admin, and Buyer roles. The goal is to ensure all order status updates trigger appropriate notifications to all relevant parties with real-time delivery, database persistence, and comprehensive tracking.

The notification system must support the complete order lifecycle from placement through delivery confirmation, with role-specific notifications, badge counters, notification history, and mobile push notifications.

## Glossary

- **Notification_System**: The complete notification infrastructure including database models, service layer, API endpoints, and real-time delivery mechanisms
- **Buyer**: A user who purchases products from sellers
- **Seller**: A user who lists and sells products
- **Rider**: A delivery personnel who transports orders from sellers to buyers
- **Admin**: A platform administrator who manages the system
- **Order_Status**: The current state of an order in the order lifecycle (pending, processing, ready_for_pickup, accepted_by_rider, in_transit, delivered, completed, cancelled)
- **Notification_Trigger**: An event that causes a notification to be created and sent
- **Push_Notification**: A real-time notification delivered to a mobile device or web browser
- **In_App_Notification**: A notification stored in the database and displayed within the application
- **Badge_Counter**: A visual indicator showing the count of unread notifications
- **Notification_History**: A persistent record of all notifications sent to a user
- **SocketIO**: The real-time communication library used for instant notification delivery
- **Notification_Service**: The backend service responsible for creating and managing notifications
- **Notification_API**: The REST API endpoints for mobile apps to fetch and manage notifications
- **Notification_Model**: The database table storing notification records
- **Unread_Status**: A boolean flag indicating whether a notification has been read by the recipient
- **Action_URL**: A deep link or URL that navigates the user to the relevant screen when clicking a notification
- **Notification_Type**: A category of notification (order, promotion, product, system)
- **Duplicate_Prevention**: Logic to prevent sending the same notification multiple times for the same event
- **Broadcast_Notification**: A notification sent to multiple users simultaneously (e.g., all active riders)
- **Order_Lifecycle**: The complete sequence of status changes from order placement to completion

## Requirements

### Requirement 1: Fix Existing Notification Bugs

**User Story:** As a platform user (Buyer, Seller, Rider, or Admin), I want all notification bugs to be fixed, so that I receive reliable notifications for all relevant events.

#### Acceptance Criteria

1. WHEN the Notification_System is initialized, THE Notification_System SHALL verify all required database columns exist
2. WHEN a notification function is called with missing parameters, THE Notification_System SHALL log the error and continue without crashing
3. WHEN a notification is created, THE Notification_System SHALL validate that the user_id exists before inserting
4. IF a SocketIO connection fails, THEN THE Notification_System SHALL still persist the notification to the database
5. WHEN multiple notifications are triggered simultaneously, THE Notification_System SHALL process them without race conditions
6. THE Notification_System SHALL handle database session rollbacks gracefully on errors
7. WHEN a notification references an order_id, THE Notification_System SHALL verify the order exists
8. THE Notification_System SHALL prevent duplicate notifications for the same event within 5 seconds

### Requirement 2: Complete Order Status Notification Coverage

**User Story:** As a platform user, I want to receive notifications for every order status change, so that I stay informed about my orders.

#### Acceptance Criteria

1. WHEN an order transitions from any status to another status, THE Notification_System SHALL trigger the appropriate notification function
2. WHEN a Buyer places an order (status: pending), THE Notification_System SHALL notify the Seller
3. WHEN a Seller confirms an order (status: to_pay → processing), THE Notification_System SHALL notify the Buyer
4. WHEN a Seller marks an order as processing, THE Notification_System SHALL notify the Buyer
5. WHEN a Seller marks an order as ready_for_pickup, THE Notification_System SHALL notify the Buyer AND broadcast to all active Riders
6. WHEN a Rider accepts an order (status: accepted_by_rider), THE Notification_System SHALL notify the Buyer AND the Seller
7. WHEN a Rider marks an order as in_transit, THE Notification_System SHALL notify the Buyer
8. WHEN a Rider marks an order as delivered, THE Notification_System SHALL notify the Buyer AND the Seller
9. WHEN a Buyer confirms receipt (status: completed), THE Notification_System SHALL notify the Rider with earnings information
10. WHEN an order is cancelled, THE Notification_System SHALL notify all relevant parties (Buyer, Seller, Rider if assigned)

### Requirement 3: Notification Persistence and Retrieval

**User Story:** As a platform user, I want my notifications to be saved in the database, so that I can view them even after refreshing the app or logging out and back in.

#### Acceptance Criteria

1. WHEN a notification is created, THE Notification_System SHALL persist it to the Notification_Model with all required fields
2. THE Notification_Model SHALL store user_id, title, message, type, order_id, action_url, is_read, and created_at
3. WHEN a user requests their notifications, THE Notification_API SHALL return all notifications ordered by created_at descending
4. WHEN a user marks a notification as read, THE Notification_System SHALL update the is_read field to true
5. WHEN a user marks all notifications as read, THE Notification_System SHALL update all unread notifications for that user
6. WHEN a user deletes a notification, THE Notification_System SHALL remove it from the database
7. THE Notification_API SHALL support pagination with configurable limit and offset parameters
8. THE Notification_API SHALL support filtering by notification type (order, promotion, product, system)
9. THE Notification_API SHALL support filtering to show only unread notifications

### Requirement 4: Real-Time Notification Delivery

**User Story:** As a platform user, I want to receive notifications instantly, so that I can respond to time-sensitive events immediately.

#### Acceptance Criteria

1. WHEN a notification is created, THE Notification_System SHALL emit a SocketIO event to the recipient's room
2. THE SocketIO event SHALL include notification id, title, message, type, order_id, action_url, and created_at
3. WHEN a user connects to the application, THE Notification_System SHALL join them to a user-specific SocketIO room
4. THE SocketIO room naming SHALL follow the format "user_{user_id}"
5. WHEN a broadcast notification is sent to Riders, THE Notification_System SHALL emit to all connected Rider clients
6. IF a SocketIO emission fails, THE Notification_System SHALL log the error but not fail the notification creation
7. WHEN a notification is marked as read, THE Notification_System SHALL emit a real-time update to the user's client

### Requirement 5: Badge Counter and Unread Count

**User Story:** As a platform user, I want to see a badge showing my unread notification count, so that I know when I have new notifications without opening the notification panel.

#### Acceptance Criteria

1. THE Notification_API SHALL provide an endpoint to retrieve the unread notification count for a user
2. WHEN a user requests their unread count, THE Notification_System SHALL return the count of notifications where is_read is false
3. WHEN a notification is marked as read, THE Notification_System SHALL decrement the cached unread count
4. WHEN a new notification is created, THE Notification_System SHALL increment the cached unread count
5. THE Notification_System SHALL cache unread counts for 60 seconds to reduce database queries
6. WHEN the cache is invalidated, THE Notification_System SHALL query the database for the current count
7. THE unread count endpoint SHALL respond within 100 milliseconds for cached values

### Requirement 6: Notification Content and Formatting

**User Story:** As a platform user, I want notifications to have clear titles and messages, so that I understand what action is required without opening the full details.

#### Acceptance Criteria

1. WHEN a notification is created, THE Notification_System SHALL include a descriptive title
2. WHEN a notification is created, THE Notification_System SHALL include a message with relevant details (order number, amounts, names)
3. WHEN a notification references an order, THE message SHALL include the order ID in the format "#123"
4. WHEN a notification references a monetary amount, THE message SHALL format it as "₱1,234.56"
5. WHEN a notification references a user, THE message SHALL include their first name
6. WHEN a Rider is assigned, THE notification SHALL include the Rider's name and contact information
7. WHEN a delivery is completed, THE notification to the Rider SHALL include the earnings amount
8. THE notification title SHALL be 100 characters or less
9. THE notification message SHALL be 500 characters or less

### Requirement 7: Action URLs and Deep Linking

**User Story:** As a platform user, I want to tap on a notification and be taken directly to the relevant screen, so that I can quickly view details or take action.

#### Acceptance Criteria

1. WHEN a notification is created, THE Notification_System SHALL include an action_url field
2. WHEN a notification is about an order, THE action_url SHALL navigate to the order detail screen for that user's role
3. FOR Buyer order notifications, THE action_url SHALL be "/buyer/orders/{order_id}"
4. FOR Seller order notifications, THE action_url SHALL be "/seller/orders/{order_id}"
5. FOR Rider order notifications, THE action_url SHALL be "/rider/orders/{order_id}" or "/rider/orders/available"
6. FOR earnings notifications, THE action_url SHALL be "/rider/earnings"
7. FOR promotion notifications, THE action_url SHALL be "/shop"
8. WHEN a user clicks a notification, THE mobile app SHALL navigate to the specified action_url

### Requirement 8: Notification Types and Categories

**User Story:** As a platform user, I want notifications to be categorized by type, so that I can filter and prioritize them.

#### Acceptance Criteria

1. THE Notification_Model SHALL support a type field with values: order, promotion, product, system
2. WHEN a notification is about an order status change, THE type SHALL be "order"
3. WHEN a notification is about a promotion or coupon, THE type SHALL be "promotion"
4. WHEN a notification is about a product approval or stock alert, THE type SHALL be "product"
5. WHEN a notification is about account status or system announcements, THE type SHALL be "system"
6. THE Notification_API SHALL allow filtering notifications by type
7. WHEN a user requests notifications of a specific type, THE Notification_System SHALL return only notifications matching that type

### Requirement 9: Broadcast Notifications to Riders

**User Story:** As a Rider, I want to be notified when any order is ready for pickup, so that I can accept deliveries on a first-come-first-served basis.

#### Acceptance Criteria

1. WHEN an order status changes to ready_for_pickup, THE Notification_System SHALL query all active Riders
2. FOR EACH active Rider, THE Notification_System SHALL create an individual notification record
3. THE Notification_System SHALL emit a SocketIO broadcast event to all connected Rider clients
4. THE notification message SHALL indicate that the order is available for pickup
5. THE action_url SHALL navigate to the available orders screen
6. WHEN a Rider accepts the order, THE Notification_System SHALL not send duplicate notifications for that order
7. THE broadcast notification SHALL include order_id, pickup address, and estimated earnings

### Requirement 10: Notification History and Management

**User Story:** As a platform user, I want to view my notification history and manage old notifications, so that I can keep my notification list organized.

#### Acceptance Criteria

1. THE Notification_API SHALL provide an endpoint to retrieve notification history with pagination
2. THE Notification_API SHALL support a limit parameter (default: 20, maximum: 100)
3. THE Notification_API SHALL support an offset parameter for pagination
4. THE Notification_API SHALL return total_count and has_more fields for pagination
5. THE Notification_API SHALL provide an endpoint to delete a single notification
6. THE Notification_API SHALL provide an endpoint to clear all read notifications
7. WHEN a user deletes a notification, THE Notification_System SHALL verify the notification belongs to that user
8. WHEN a user clears all read notifications, THE Notification_System SHALL delete only notifications where is_read is true

### Requirement 11: Mobile API Authentication

**User Story:** As a mobile app developer, I want secure API endpoints for notifications, so that users can only access their own notifications.

#### Acceptance Criteria

1. THE Notification_API SHALL require JWT authentication for all endpoints
2. WHEN a request is made without a valid JWT token, THE Notification_API SHALL return a 401 Unauthorized response
3. WHEN a request is made with an expired JWT token, THE Notification_API SHALL return a 401 Unauthorized response with message "Token has expired"
4. WHEN a request is made with an invalid JWT token, THE Notification_API SHALL return a 401 Unauthorized response with message "Token is invalid"
5. THE JWT token SHALL contain user_id and role claims
6. THE Notification_API SHALL extract user_id from the JWT token and use it to filter notifications
7. THE Notification_API SHALL not allow users to access notifications belonging to other users

### Requirement 12: Notification Metadata and Rich Content

**User Story:** As a platform user, I want notifications to include relevant images and metadata, so that I can quickly identify the context without opening the full details.

#### Acceptance Criteria

1. THE Notification_Model SHALL support an image_url field for a single thumbnail image
2. THE Notification_Model SHALL support an images field (JSON array) for multiple images
3. THE Notification_Model SHALL support a metadata field (JSON object) for additional structured data
4. WHEN a notification is about an order, THE metadata SHALL include order_id and order_total
5. WHEN a notification is about a Rider assignment, THE metadata SHALL include rider_name and rider_phone
6. WHEN a notification is about earnings, THE metadata SHALL include the earnings amount
7. THE Notification_API SHALL return all metadata fields in the notification response

### Requirement 13: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error logging for the notification system, so that I can diagnose and fix issues quickly.

#### Acceptance Criteria

1. WHEN a notification creation fails, THE Notification_System SHALL log the error with user_id, notification_type, and error message
2. WHEN a SocketIO emission fails, THE Notification_System SHALL log the error but continue processing
3. WHEN a database operation fails, THE Notification_System SHALL rollback the transaction and log the error
4. WHEN an invalid user_id is provided, THE Notification_System SHALL log a warning and skip notification creation
5. WHEN an invalid order_id is provided, THE Notification_System SHALL log a warning and create the notification without order reference
6. THE Notification_System SHALL use structured logging with timestamps and severity levels
7. THE Notification_System SHALL not expose sensitive user data in logs

### Requirement 14: Performance and Caching

**User Story:** As a platform user, I want the notification system to be fast and responsive, so that I don't experience delays when checking notifications.

#### Acceptance Criteria

1. THE Notification_API SHALL use database indexes on user_id, is_read, and created_at columns
2. THE Notification_API SHALL use eager loading for related data (actor user) to prevent N+1 queries
3. THE Notification_API SHALL cache unread counts for 60 seconds using Redis
4. WHEN Redis is unavailable, THE Notification_System SHALL fall back to direct database queries
5. THE Notification_API SHALL limit pagination results to a maximum of 100 notifications per request
6. THE Notification_API SHALL respond to unread count requests within 100 milliseconds
7. THE Notification_API SHALL respond to notification list requests within 500 milliseconds

### Requirement 15: Notification Settings and Preferences

**User Story:** As a platform user, I want to manage my notification preferences, so that I can control which notifications I receive.

#### Acceptance Criteria

1. THE Notification_API SHALL provide an endpoint to retrieve notification settings
2. THE Notification_API SHALL provide an endpoint to update notification settings
3. THE notification settings SHALL include email_notifications (boolean)
4. THE notification settings SHALL include push_notifications (boolean, always true for mobile)
5. THE notification settings SHALL include order_updates (boolean)
6. THE notification settings SHALL include promotions (boolean)
7. THE notification settings SHALL include product_updates (boolean)
8. WHEN a user updates their settings, THE Notification_System SHALL persist the changes to the database

### Requirement 16: Integration with Order Status Changes

**User Story:** As a developer, I want the notification system to automatically trigger when order status changes, so that notifications are sent without manual intervention.

#### Acceptance Criteria

1. WHEN an order status is updated in the database, THE Notification_System SHALL detect the change
2. THE Notification_System SHALL provide a function integrate_with_order_status_change(order, old_status, new_status)
3. THE integration function SHALL map each status to the appropriate notification handler
4. THE integration function SHALL handle errors gracefully without blocking the order status update
5. WHEN a status has no notification handler, THE integration function SHALL log a warning and continue
6. THE integration function SHALL be called from all order status update endpoints
7. THE integration function SHALL support all order statuses: pending, to_pay, processing, ready_for_pickup, accepted_by_rider, in_transit, delivered, completed, cancelled

### Requirement 17: Return and Refund Notifications

**User Story:** As a Buyer or Seller, I want to receive notifications about return and refund requests, so that I can respond promptly.

#### Acceptance Criteria

1. WHEN a Buyer requests a return or refund, THE Notification_System SHALL notify the Seller
2. WHEN a Seller approves a return request, THE Notification_System SHALL notify the Buyer
3. WHEN a Seller rejects a return request, THE Notification_System SHALL notify the Buyer
4. WHEN a refund is processed, THE Notification_System SHALL notify the Buyer with the refund amount
5. THE return notification SHALL include the order_id and return reason
6. THE refund notification SHALL include the refund amount formatted as "₱1,234.56"

### Requirement 18: Product and Promotion Notifications

**User Story:** As a Seller, I want to receive notifications about product approvals and stock alerts, so that I can manage my inventory effectively.

#### Acceptance Criteria

1. WHEN a product is approved by Admin, THE Notification_System SHALL notify the Seller
2. WHEN a product is rejected by Admin, THE Notification_System SHALL notify the Seller with the rejection reason
3. WHEN a product stock falls below 10 units, THE Notification_System SHALL notify the Seller
4. WHEN a product is out of stock, THE Notification_System SHALL notify the Seller
5. WHEN a promotion or coupon is created, THE Notification_System SHALL notify eligible users
6. THE product notification SHALL include the product name and action_url to the product detail page

### Requirement 19: Admin Broadcast Notifications

**User Story:** As an Admin, I want to send broadcast notifications to all users or specific user groups, so that I can communicate important announcements.

#### Acceptance Criteria

1. THE Notification_API SHALL provide an admin-only endpoint to broadcast notifications
2. THE broadcast endpoint SHALL require admin role authentication
3. THE broadcast endpoint SHALL accept title, message, type, and optional target_role parameters
4. WHEN target_role is specified, THE Notification_System SHALL send to users with that role only
5. WHEN target_role is not specified, THE Notification_System SHALL send to all active users
6. THE broadcast endpoint SHALL return the count of notifications sent
7. WHEN a non-admin user attempts to broadcast, THE Notification_API SHALL return a 403 Forbidden response

### Requirement 20: Notification Cleanup and Maintenance

**User Story:** As a system administrator, I want old notifications to be automatically cleaned up, so that the database doesn't grow indefinitely.

#### Acceptance Criteria

1. THE Notification_System SHALL provide a function to delete notifications older than a specified number of days
2. THE cleanup function SHALL accept a days parameter (default: 30)
3. WHEN the cleanup function is called, THE Notification_System SHALL delete all notifications where created_at is older than the cutoff date
4. THE cleanup function SHALL return the count of deleted notifications
5. THE cleanup function SHALL be safe to run on a production database without locking
6. THE cleanup function SHALL preserve unread notifications regardless of age
7. THE cleanup function SHALL be scheduled to run automatically via a cron job or background task

