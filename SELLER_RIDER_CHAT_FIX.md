# Seller to Rider Chat Fix

## Problem
The seller-to-rider chat is using the old `RiderChatMessage` table instead of the unified `chat_message` table. This causes:
1. Messages sent by seller don't appear in rider's inbox
2. Rider can't see seller's messages
3. Chat conversations are not synced

## Solution
Update the `seller_chat_rider` route in `app.py` to use the unified chat system.

## Files to Update
1. `backend/app.py` - Update `seller_chat_rider` route (around line 12263)

## Implementation
Replace the `seller_chat_rider` function with the corrected version that uses the unified chat_message table.
