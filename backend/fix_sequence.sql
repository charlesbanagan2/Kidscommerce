-- Fix the rider_chat_message sequence
SELECT setval('rider_chat_message_id_seq', (SELECT MAX(id) FROM rider_chat_message) + 1, false);
