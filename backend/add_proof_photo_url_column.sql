-- Add proof_photo_url column to order table
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS proof_photo_url TEXT;
