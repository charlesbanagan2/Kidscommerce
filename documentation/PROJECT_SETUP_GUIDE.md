# Kids Commerce - Project Structure & Setup Guide

## Project Organization

The project has been reorganized into two main directories:

```
kids/
|-- backend/          # Flask backend application
|-- mobile_app/       # Flutter mobile application
```

## Backend Setup (Flask)

### Directory Structure
```
backend/
|-- app.py             # Main Flask application
|-- .env               # Environment variables
|-- .env.example       # Environment variables template
|-- requirements.txt   # Python dependencies
|-- run.py            # Alternative server startup
|-- start_server.py   # Enhanced startup script
|-- static/           # Static files (CSS, JS, images)
|-- templates/        # HTML templates
|-- instance/         # Database instance
|-- migrations/       # Database migrations
|-- __pycache__/      # Python cache files
```

### Running the Backend

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server:**
   ```bash
   python -m flask run --host=0.0.0.0 --port=5000
   ```
   
   Or use the enhanced startup script:
   ```bash
   python start_server.py
   ```

4. **Access the API:**
   - Web Interface: `http://127.0.0.1:5000`
   - Mobile API: `http://192.168.100.46:5000/api/v1`
   - Socket.IO: `ws://192.168.100.46:5000/socket.io/`

### API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh

#### Products
- `GET /api/v1/products` - Get products list
- `GET /api/v1/products/{id}` - Get product details

#### Orders
- `GET /api/v1/orders` - Get user orders
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/orders/{id}` - Get order details

#### User
- `GET /api/v1/user/profile` - Get user profile
- `PUT /api/v1/user/profile` - Update user profile

#### Categories
- `GET /api/v1/categories` - Get categories with subcategories

#### Cart
- `GET /api/v1/cart` - Get user cart
- `POST /api/v1/cart` - Add item to cart
- `PUT /api/v1/cart` - Update cart item
- `DELETE /api/v1/cart` - Remove item from cart

#### Wishlist
- `GET /api/v1/wishlist` - Get user wishlist
- `POST /api/v1/wishlist` - Add item to wishlist
- `DELETE /api/v1/wishlist` - Remove item from wishlist

## Mobile App Setup (Flutter)

### Prerequisites

1. **Install Flutter SDK:**
   - Download from: https://flutter.dev/docs/get-started/install
   - Follow installation guide for your operating system

2. **Verify Flutter installation:**
   ```bash
   flutter doctor
   ```

3. **Set up development environment:**
   - Install Android Studio or VS Code with Flutter extensions
   - Set up Android emulator or physical device

### Directory Structure
```
mobile_app/
|-- lib/
|   |-- main.dart                    # App entry point
|   |-- models/
|   |   |-- user.dart                # User models
|   |-- providers/
|   |   |-- auth_provider.dart       # Authentication state management
|   |-- services/
|   |   |-- api_service.dart         # HTTP client for API calls
|   |-- screens/
|   |   |-- auth/
|   |   |   |-- login_screen.dart      # Login screen
|   |   |   |-- register_screen.dart   # Registration screen
|   |   |-- buyer/
|   |   |   |-- buyer_home_screen.dart # Buyer dashboard
|   |   |-- rider/
|   |   |   |-- rider_dashboard_screen.dart # Rider dashboard
|-- pubspec.yaml      # Flutter dependencies
|-- README.md         # Flutter-specific documentation
```

### Running the Mobile App

1. **Navigate to mobile_app directory:**
   ```bash
   cd mobile_app
   ```

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the app:**
   ```bash
   flutter run
   ```

4. **Choose target device:**
   - Select Android emulator
   - Or connect physical device and select it

### Flutter App Features

#### Authentication System
- **Unified Login/Registration**: Single system for Buyers and Riders
- **Role Selection**: Choose between Buyer and Rider during registration
- **JWT Token Management**: Secure token storage and automatic refresh
- **Form Validation**: Email format, password length, required fields

#### Role-Based Navigation
- **Buyer**: Navigates to BuyerHomeScreen
  - Home (product browsing)
  - Categories
  - Shopping Cart
  - Orders
  - Profile
- **Rider**: Navigates to RiderDashboardScreen
  - Dashboard (stats, online status)
  - Orders (delivery assignments)
  - Earnings
  - Profile

#### API Integration
- **Base URL**: `http://192.168.100.46:5000/api/v1`
- **Error Handling**: Network errors, API errors, user-friendly messages
- **State Management**: Provider pattern for authentication state
- **Token Persistence**: SharedPreferences for secure storage

## Development Workflow

### Backend Development
1. Make changes to Flask code in `backend/`
2. Restart Flask server to see changes
3. Test API endpoints with Postman or curl

### Mobile App Development
1. Make changes to Flutter code in `mobile_app/`
2. Use `flutter hot reload` for instant updates
3. Test on emulator or physical device

### Testing Integration
1. Ensure Flask backend is running
2. Start Flutter app
3. Test registration and login flows
4. Verify role-based navigation

## Configuration

### Backend Configuration
Edit `backend/.env` file:
```env
DATABASE_URI=mysql://username:password@localhost/kids_db
JWT_SECRET_KEY=your-secret-key-here
FLASK_SECRET_KEY=your-flask-secret-key
```

### Mobile App Configuration
Edit `mobile_app/lib/services/api_service.dart`:
```dart
static const String _baseUrl = 'http://YOUR_LOCAL_IP:5000/api/v1';
```

Replace `YOUR_LOCAL_IP` with your actual local IP address.

## Troubleshooting

### Backend Issues
- **Database Connection**: Check MySQL service and credentials
- **Port Conflicts**: Ensure port 5000 is available
- **Dependencies**: Run `pip install -r requirements.txt`

### Mobile App Issues
- **Flutter Installation**: Run `flutter doctor` to check setup
- **Dependencies**: Run `flutter pub get` to install packages
- **Network Connection**: Ensure backend is running and accessible
- **API Errors**: Check backend logs for error messages

### Common Solutions
1. **Backend not accessible**: Check firewall settings
2. **API connection failed**: Verify IP address and port
3. **Token errors**: Clear app data and re-login
4. **Build errors**: Run `flutter clean` then `flutter pub get`

## Next Steps

1. **Start Backend**: Run Flask server in `backend/` directory
2. **Setup Flutter**: Install Flutter SDK and dependencies
3. **Run Mobile App**: Start Flutter app in `mobile_app/` directory
4. **Test Integration**: Verify authentication and role-based navigation
5. **Develop Features**: Add more functionality to both backend and mobile app

## Production Deployment

### Backend
- Use production WSGI server (Gunicorn, uWSGI)
- Set up proper database configuration
- Configure HTTPS/SSL certificates
- Set up environment variables properly

### Mobile App
- Update API base URL to production server
- Build release APK/AAB for Android
- Submit to app stores (Google Play, Apple App Store)
- Implement proper error handling and logging

This reorganized structure provides clear separation between backend and mobile app, making development and deployment much more manageable.
