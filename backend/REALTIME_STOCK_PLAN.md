# Real-Time Stock Update Implementation Plan

## Overview
Implement real-time stock deduction when orders are placed, with automatic updates to both mobile app and website.

## Current Flow Issues
1. Stock is reserved but not deducted immediately
2. No real-time updates to UI when stock changes
3. Mobile app doesn't reflect stock changes until manual refresh

## Solution Architecture

### Backend Changes
1. **Immediate Stock Deduction on Checkout**
   - Deduct from `product.stock` when order status = 'pending'
   - Update `product.reserved_stock` tracking
   - Broadcast stock change via SocketIO

2. **SocketIO Real-Time Events**
   - Emit 'stock_update' event when stock changes
   - Include product_id, new_stock, available_stock

3. **API Endpoint for Stock Check**
   - GET /api/v1/products/{id}/stock
   - Returns current available stock

### Mobile App Changes
1. **WebSocket Connection**
   - Connect to SocketIO server
   - Listen for 'stock_update' events
   - Update local product cache

2. **Automatic UI Updates**
   - Update product listing when stock changes
   - Update product detail screen
   - Show "Out of Stock" when stock = 0

### Website Changes
1. **JavaScript SocketIO Client**
   - Connect on page load
   - Listen for stock updates
   - Update product cards dynamically

## Implementation Steps
1. Fix backend stock deduction logic
2. Add SocketIO stock broadcast
3. Add mobile WebSocket listener
4. Add website JavaScript listener
5. Test real-time updates

## Example Flow
1. Buyer A views product: 170 stock available
2. Buyer B checks out 10 items
3. Backend deducts: 170 - 10 = 160
4. Backend broadcasts: stock_update(product_id=X, stock=160)
5. Buyer A's screen updates: Now shows 160 stock
6. Database updated: product.stock = 160
