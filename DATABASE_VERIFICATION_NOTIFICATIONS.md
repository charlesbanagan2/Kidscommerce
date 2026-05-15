# Database Verification for Notification System

## Required Columns in `notification` Table

The notification table must have these columns for the API to work correctly:

```sql
-- Core columns (REQUIRED)
id              INTEGER PRIMARY KEY
user_id         INTEGER NOT NULL (Foreign Key to user.id)
message         VARCHAR(255) NOT NULL
is_read         BOOLEAN DEFAULT FALSE
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Enhanced columns (OPTIONAL but recommended)
title           VARCHAR(255)
image_url       VARCHAR(255)
link            VARCHAR(255)
type            VARCHAR(40)
actor_user_id   INTEGER (Foreign Key to user.id)
order_id        INTEGER
images          JSON
```

## Quick Verification SQL

Run these queries to verify your database schema:

### 1. Check if notification table exists
```sql
-- PostgreSQL/Supabase
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'notification';

-- SQLite
SELECT name FROM sqlite_master WHERE type='table' AND name='notification';
```

### 2. Check all columns
```sql
-- PostgreSQL/Supabase
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'notification'
ORDER BY ordinal_position;

-- SQLite
PRAGMA table_info(notification);
```

### 3. Check indexes (for performance)
```sql
-- PostgreSQL/Supabase
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'notification';

-- SQLite
SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='notification';
```

## Expected Output

### Column List (PostgreSQL/Supabase)
```
column_name     | data_type          | is_nullable
----------------|--------------------|-----------
id              | integer            | NO
user_id         | integer            | NO
message         | character varying  | NO
title           | character varying  | YES
image_url       | character varying  | YES
link            | character varying  | YES
type            | character varying  | YES
actor_user_id   | integer            | YES
order_id        | integer            | YES
images          | json               | YES
is_read         | boolean            | YES
created_at      | timestamp          | YES
```

## Create Missing Columns

If any columns are missing, run these ALTER TABLE statements:

```sql
-- Add title column
ALTER TABLE notification ADD COLUMN title VARCHAR(255);

-- Add image_url column
ALTER TABLE notification ADD COLUMN image_url VARCHAR(255);

-- Add link column
ALTER TABLE notification ADD COLUMN link VARCHAR(255);

-- Add type column
ALTER TABLE notification ADD COLUMN type VARCHAR(40);

-- Add actor_user_id column
ALTER TABLE notification ADD COLUMN actor_user_id INTEGER;

-- Add order_id column
ALTER TABLE notification ADD COLUMN order_id INTEGER;

-- Add images column (JSON)
ALTER TABLE notification ADD COLUMN images JSON;

-- Add foreign key constraints (optional but recommended)
ALTER TABLE notification 
ADD CONSTRAINT fk_notification_user 
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

ALTER TABLE notification 
ADD CONSTRAINT fk_notification_actor 
FOREIGN KEY (actor_user_id) REFERENCES "user"(id) ON DELETE SET NULL;
```

## Create Indexes for Performance

These indexes will significantly improve query performance:

```sql
-- Index on user_id (most important)
CREATE INDEX IF NOT EXISTS idx_notification_user_id 
ON notification(user_id);

-- Index on is_read for filtering unread notifications
CREATE INDEX IF NOT EXISTS idx_notification_is_read 
ON notification(is_read);

-- Index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_notification_created_at 
ON notification(created_at DESC);

-- Composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_notification_user_unread 
ON notification(user_id, is_read, created_at DESC);

-- Index on type for filtering by notification type
CREATE INDEX IF NOT EXISTS idx_notification_type 
ON notification(type);
```

## Test Data

Insert some test notifications to verify everything works:

```sql
-- Test notification for user_id = 1
INSERT INTO notification (user_id, title, message, type, is_read, created_at)
VALUES 
(1, 'Test Order Notification', 'Your order #123 has been placed', 'order', false, NOW()),
(1, 'Test Promotion', 'Special discount available!', 'promotion', false, NOW()),
(1, 'Test Product Update', 'New product added to your wishlist', 'product', true, NOW() - INTERVAL '1 day');

-- Verify test data
SELECT id, user_id, title, message, type, is_read, created_at
FROM notification
WHERE user_id = 1
ORDER BY created_at DESC;
```

## Verification Checklist

Run through this checklist to ensure everything is set up correctly:

- [ ] notification table exists
- [ ] All required columns exist (id, user_id, message, is_read, created_at)
- [ ] All optional columns exist (title, image_url, link, type, actor_user_id, order_id, images)
- [ ] Indexes are created for performance
- [ ] Foreign key constraints are set up
- [ ] Test data can be inserted successfully
- [ ] Test data can be queried successfully

## Common Issues

### Issue: Column doesn't exist
**Error**: `column "title" does not exist`
**Fix**: Run the ALTER TABLE statement to add the missing column

### Issue: Type mismatch
**Error**: `column "images" is of type text but expression is of type json`
**Fix**: 
```sql
-- PostgreSQL
ALTER TABLE notification ALTER COLUMN images TYPE JSON USING images::json;

-- SQLite (recreate table)
-- Backup data first, then recreate table with correct types
```

### Issue: Foreign key constraint fails
**Error**: `foreign key constraint fails`
**Fix**: Make sure the referenced user exists in the user table

## Performance Verification

After setting up indexes, verify they're being used:

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM notification
WHERE user_id = 1 AND is_read = false
ORDER BY created_at DESC
LIMIT 20;

-- Look for "Index Scan" in the output
-- If you see "Seq Scan", indexes aren't being used
```

## Cleanup (if needed)

To start fresh (⚠️ WARNING: This deletes all notifications):

```sql
-- Delete all notifications
DELETE FROM notification;

-- Reset auto-increment (PostgreSQL)
ALTER SEQUENCE notification_id_seq RESTART WITH 1;

-- Reset auto-increment (SQLite)
DELETE FROM sqlite_sequence WHERE name='notification';
```

---

**Next Steps**: 
1. Run verification queries
2. Add missing columns if needed
3. Create indexes for performance
4. Test with sample data
5. Restart backend server
6. Test mobile app

**Status**: ✅ Database schema verification guide complete
