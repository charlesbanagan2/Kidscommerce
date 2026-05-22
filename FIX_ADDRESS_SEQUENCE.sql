-- Fix address table sequence issue
-- This happens when the auto-increment sequence gets out of sync with actual data

-- Step 1: Find the maximum ID currently in the address table
SELECT MAX(id) FROM address;

-- Step 2: Reset the sequence to the correct value
-- Replace the sequence name if different (check with \d address in psql)
SELECT setval('address_id_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);

-- Step 3: Verify the fix
SELECT currval('address_id_seq') as current_sequence_value;
SELECT MAX(id) as max_id_in_table FROM address;

-- The current_sequence_value should be >= max_id_in_table

-- Alternative: If the sequence name is different, try these:
-- SELECT setval('address_pkey_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);
-- SELECT setval(pg_get_serial_sequence('address', 'id'), (SELECT COALESCE(MAX(id), 1) FROM address), true);
