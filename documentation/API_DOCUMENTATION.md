# Mobile API v1 Documentation
## Kids E-commerce System - Flutter Mobile App Integration

### Overview
This REST API provides endpoints for the Flutter mobile app to interact with the existing Flask e-commerce system. The API uses JWT authentication and supports real-time features via Socket.IO.

### Base URL
```
http://YOUR_LOCAL_IP:5000/api/v1
```
Replace `YOUR_LOCAL_IP` with your actual local network IP (e.g., 192.168.1.100)

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### JWT Token Structure
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 86400
}
```

---

## Authentication Endpoints

### POST /auth/login
Login user and return JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "buyer",
    "phone": "+1234567890",
    "profile_image": "http://localhost:5000/static/uploads/profile.jpg"
  },
  "tokens": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 86400
  }
}
```

### POST /auth/register
Register a new user (buyer or rider).

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "role": "buyer"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "buyer",
    "phone": "+1234567890"
  },
  "tokens": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 86400
  }
}
```

### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "tokens": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 86400
  }
}
```

---

## Product Endpoints

### GET /products
Get products with pagination, filtering, and search.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (max: 100)
- `category_id` (int): Filter by category
- `subcategory_id` (int): Filter by subcategory
- `seller_id` (int): Filter by seller
- `search` (string): Search in name and description
- `featured` (bool): Filter featured products
- `sort_by` (string): Sort by (created_at, price, name)
- `sort_order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": 1,
      "name": "Baby Toy",
      "description": "Colorful baby toy",
      "price": 29.99,
      "stock": 50,
      "image": "http://localhost:5000/static/uploads/toy.jpg",
      "gallery": [],
      "video": null,
      "category_id": 2,
      "subcategory_id": 3,
      "seller_id": 5,
      "seller_name": "John Seller",
      "featured": true,
      "rating": 4.5,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 100,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /products/{id}
Get detailed product information.

**Response:**
```json
{
  "success": true,
  "product": {
    "id": 1,
    "name": "Baby Toy",
    "description": "Detailed description...",
    "price": 29.99,
    "stock": 50,
    "image": "http://localhost:5000/static/uploads/toy.jpg",
    "gallery": ["image1.jpg", "image2.jpg"],
    "video": null,
    "category_id": 2,
    "subcategory_id": 3,
    "seller_id": 5,
    "seller": {
      "id": 5,
      "name": "John Seller",
      "store_name": "Kids Store",
      "store_logo": "http://localhost:5000/static/uploads/logo.jpg"
    },
    "featured": true,
    "rating": 4.5,
    "review_count": 25,
    "reviews": [
      {
        "id": 1,
        "rating": 5,
        "title": "Great toy!",
        "content": "My baby loves this toy",
        "user_name": "Happy Parent",
        "created_at": "2024-01-01T12:00:00",
        "verified_purchase": true
      }
    ],
    "created_at": "2024-01-01T12:00:00"
  }
}
```

---

## Order Endpoints

### GET /orders
Get user's orders (authenticated).

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Items per page
- `status` (string): Filter by status

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "id": 1,
      "total_amount": 59.98,
      "status": "pending",
      "payment_method": "cod",
      "payment_status": "pending",
      "delivery_address": "123 Main St, City",
      "items": [
        {
          "id": 1,
          "product_id": 1,
          "product_name": "Baby Toy",
          "product_image": "http://localhost:5000/static/uploads/toy.jpg",
          "quantity": 2,
          "price": 29.99,
          "subtotal": 59.98
        }
      ],
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 2,
    "per_page": 20,
    "total": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

### POST /orders
Create new order (authenticated).

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "delivery_address": "123 Main St, City",
  "payment_method": "cod"
}
```

**Response:**
```json
{
  "success": true,
  "order": {
    "id": 2,
    "total_amount": 59.98,
    "status": "pending",
    "payment_method": "cod",
    "delivery_address": "123 Main St, City",
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### GET /orders/{id}
Get detailed order information (authenticated).

**Response:**
```json
{
  "success": true,
  "order": {
    "id": 1,
    "total_amount": 59.98,
    "status": "pending",
    "payment_method": "cod",
    "payment_status": "pending",
    "delivery_address": "123 Main St, City",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Baby Toy",
        "product_description": "Detailed description...",
        "product_image": "http://localhost:5000/static/uploads/toy.jpg",
        "quantity": 2,
        "price": 29.99,
        "subtotal": 59.98
      }
    ],
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:30:00"
  }
}
```

---

## User Profile Endpoints

### GET /user/profile
Get user profile (authenticated).

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "buyer",
    "profile_image": "http://localhost:5000/static/uploads/profile.jpg",
    "address": "123 Main St, City",
    "status": "active"
  }
}
```

### PUT /user/profile
Update user profile (authenticated).

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "buyer",
    "address": "123 Main St, City"
  }
}
```

---

## Categories Endpoint

### GET /categories
Get all categories with subcategories.

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": 1,
      "name": "Baby Clothes & Accessories",
      "subcategories": [
        {
          "id": 1,
          "name": "Onesies"
        },
        {
          "id": 2,
          "name": "Sleepwear"
        }
      ]
    }
  ]
}
```

---

## Cart Endpoints

### GET /cart
Get user's cart (authenticated).

**Response:**
```json
{
  "success": true,
  "cart_items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Baby Toy",
      "product_image": "http://localhost:5000/static/uploads/toy.jpg",
      "price": 29.99,
      "quantity": 2,
      "stock": 50,
      "subtotal": 59.98
    }
  ],
  "total_amount": 59.98,
  "item_count": 1
}
```

### POST /cart
Add item to cart (authenticated).

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item added to cart"
}
```

### PUT /cart
Update cart item quantity (authenticated).

**Request Body:**
```json
{
  "cart_item_id": 1,
  "quantity": 3
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cart updated"
}
```

### DELETE /cart
Remove item from cart (authenticated).

**Query Parameters:**
- `cart_item_id` (int): Cart item ID to remove

**Response:**
```json
{
  "success": true,
  "message": "Item removed from cart"
}
```

---

## Wishlist Endpoints

### GET /wishlist
Get user's wishlist (authenticated).

**Response:**
```json
{
  "success": true,
  "wishlist_items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Baby Toy",
      "product_image": "http://localhost:5000/static/uploads/toy.jpg",
      "price": 29.99,
      "stock": 50,
      "added_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### POST /wishlist
Add item to wishlist (authenticated).

**Request Body:**
```json
{
  "product_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added to wishlist"
}
```

### DELETE /wishlist
Remove item from wishlist (authenticated).

**Query Parameters:**
- `product_id` (int): Product ID to remove

**Response:**
```json
{
  "success": true,
  "message": "Removed from wishlist"
}
```

---

## Socket.IO Real-time Events

### Connection Setup
```javascript
import 'package:flutter_socket_io/flutter_socket_io.dart';

final socket = SocketIOManager().createSocketIO('http://YOUR_LOCAL_IP:5000', '/');
socket.connect();
```

### Join Tracking Room
**Event:** `join_tracking_room`
**Data:**
```json
{
  "user_id": 1,
  "user_role": "buyer"
}
```

### Rider Location Updates
**Event:** `rider_location_update`
**Data:**
```json
{
  "rider_id": 3,
  "latitude": 14.5995,
  "longitude": 120.9842,
  "order_id": 1,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Order Status Updates
**Event:** `order_status_update`
**Data:**
```json
{
  "user_id": 2,
  "order_id": 1,
  "status": "picked_up",
  "notes": "Package picked up from store",
  "user_role": "rider"
}
```

### Mobile Chat Messages
**Event:** `mobile_chat_message`
**Data:**
```json
{
  "sender_id": 1,
  "receiver_id": 2,
  "message": "Where is my order?",
  "chat_type": "buyer_rider",
  "order_id": 1
}
```

### Get Active Orders
**Event:** `get_active_orders`
**Data:**
```json
{
  "user_id": 1,
  "user_role": "buyer"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

---

## Testing with Postman

### Setup
1. Import the collection (if provided)
2. Set environment variables:
   - `base_url`: `http://YOUR_LOCAL_IP:5000/api/v1`
   - `access_token`: (will be set after login)

### Test Sequence
1. **Register User**: POST `/auth/register`
2. **Login**: POST `/auth/login` (save the access_token)
3. **Get Products**: GET `/products`
4. **Get Categories**: GET `/categories`
5. **Add to Cart**: POST `/cart`
6. **Create Order**: POST `/orders`
7. **Get Orders**: GET `/orders`

---

## Flutter Integration Notes

### HTTP Package Setup
```yaml
dependencies:
  http: ^1.1.0
  flutter_secure_storage: ^8.0.0
```

### JWT Token Storage
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();

// Save token
await storage.write(key: 'access_token', value: token);

// Get token
String? token = await storage.read(key: 'access_token');
```

### API Client Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  final String baseUrl;
  String? accessToken;

  ApiClient(this.baseUrl);

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      accessToken = data['tokens']['access_token'];
      return data;
    } else {
      throw Exception('Login failed');
    }
  }

  Future<Map<String, dynamic>> getProducts() async {
    final response = await http.get(
      Uri.parse('$baseUrl/products'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load products');
    }
  }
}
```

---

## Production Deployment Notes

1. **Environment Variables:**
   - Set `JWT_SECRET_KEY` to a secure random string
   - Update `DATABASE_URI` for production database
   - Configure proper file upload paths

2. **Security:**
   - Enable HTTPS in production
   - Implement rate limiting
   - Add input validation and sanitization
   - Use proper CORS configuration

3. **Performance:**
   - Implement database connection pooling
   - Add Redis for session storage
   - Use CDN for static assets

---

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure proper headers are set
2. **JWT Token Expired**: Use refresh token to get new access token
3. **Database Connection**: Check MySQL service and credentials
4. **Socket.IO Connection**: Verify firewall settings for WebSocket

### Debug Mode
Enable debug logging in development:
```python
app.config['DEBUG'] = True
```

---

This API is ready for Flutter mobile app integration with comprehensive authentication, real-time features, and full e-commerce functionality.
