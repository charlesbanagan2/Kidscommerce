# MOBILE APP UPDATES FOR STOCK RESERVATION

## 1. Update Product Model (lib/models/product.dart)

```dart
class Product {
  final int id;
  final String name;
  final String description;
  final double price;
  final int stock;
  final int reservedStock;
  final String? imageFilename;
  final int categoryId;
  final int sellerId;
  final String status;
  final bool featured;
  final DateTime createdAt;

  // Computed property for available stock
  int get availableStock => stock - reservedStock;
  bool get isInStock => availableStock > 0;
  String get stockStatus => isInStock ? 'In Stock ($availableStock available)' : 'Out of Stock';

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.stock,
    this.reservedStock = 0,
    this.imageFilename,
    required this.categoryId,
    required this.sellerId,
    this.status = 'active',
    this.featured = false,
    required this.createdAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      price: (json['price'] as num).toDouble(),
      stock: json['stock'] as int? ?? 0,
      reservedStock: json['reserved_stock'] as int? ?? 0,
      imageFilename: json['image_filename'] as String?,
      categoryId: json['category_id'] as int,
      sellerId: json['seller_id'] as int,
      status: json['status'] as String? ?? 'active',
      featured: json['featured'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'stock': stock,
      'reserved_stock': reservedStock,
      'image_filename': imageFilename,
      'category_id': categoryId,
      'seller_id': sellerId,
      'status': status,
      'featured': featured,
      'created_at': createdAt.toIso8601String(),
    };
  }

  // Create a copy with updated fields
  Product copyWith({
    int? stock,
    int? reservedStock,
    double? price,
  }) {
    return Product(
      id: id,
      name: name,
      description: description,
      price: price ?? this.price,
      stock: stock ?? this.stock,
      reservedStock: reservedStock ?? this.reservedStock,
      imageFilename: imageFilename,
      categoryId: categoryId,
      sellerId: sellerId,
      status: status,
      featured: featured,
      createdAt: createdAt,
    );
  }
}
```

## 2. Create Socket Service (lib/services/socket_service.dart)

```dart
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:flutter/foundation.dart';

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  IO.Socket? _socket;
  final Map<String, List<Function>> _listeners = {};

  // Initialize socket connection
  void connect(String serverUrl) {
    if (_socket != null && _socket!.connected) {
      debugPrint('Socket already connected');
      return;
    }

    _socket = IO.io(serverUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': true,
    });

    _socket!.onConnect((_) {
      debugPrint('Socket connected');
    });

    _socket!.onDisconnect((_) {
      debugPrint('Socket disconnected');
    });

    _socket!.onError((error) {
      debugPrint('Socket error: $error');
    });

    // Listen for stock updates
    _socket!.on('product_stock_update', (data) {
      debugPrint('Stock update received: $data');
      _notifyListeners('product_stock_update', data);
    });

    // Listen for price updates
    _socket!.on('product_price_update', (data) {
      debugPrint('Price update received: $data');
      _notifyListeners('product_price_update', data);
    });
  }

  // Add listener for specific event
  void on(String event, Function callback) {
    if (!_listeners.containsKey(event)) {
      _listeners[event] = [];
    }
    _listeners[event]!.add(callback);
  }

  // Remove listener
  void off(String event, Function callback) {
    if (_listeners.containsKey(event)) {
      _listeners[event]!.remove(callback);
    }
  }

  // Notify all listeners for an event
  void _notifyListeners(String event, dynamic data) {
    if (_listeners.containsKey(event)) {
      for (var callback in _listeners[event]!) {
        callback(data);
      }
    }
  }

  // Disconnect socket
  void disconnect() {
    _socket?.disconnect();
    _socket = null;
    _listeners.clear();
  }

  // Check if connected
  bool get isConnected => _socket?.connected ?? false;
}
```

## 3. Update Product Provider (lib/providers/product_provider.dart)

```dart
import 'package:flutter/foundation.dart';
import '../models/product.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';

class ProductProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final SocketService _socketService = SocketService();
  
  List<Product> _products = [];
  bool _isLoading = false;
  String? _error;

  List<Product> get products => _products;
  bool get isLoading => _isLoading;
  String? get error => _error;

  ProductProvider() {
    _initializeSocketListeners();
  }

  void _initializeSocketListeners() {
    // Listen for stock updates
    _socketService.on('product_stock_update', (data) {
      final productId = data['product_id'] as int;
      final newStock = data['stock'] as int;
      final reservedStock = data['reserved_stock'] as int;
      
      updateProductStock(productId, newStock, reservedStock);
    });

    // Listen for price updates
    _socketService.on('product_price_update', (data) {
      final productId = data['product_id'] as int;
      final newPrice = (data['price'] as num).toDouble();
      
      updateProductPrice(productId, newPrice);
    });
  }

  // Fetch products from API
  Future<void> fetchProducts() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _products = await _apiService.getProducts();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  // Update product stock (called by socket listener)
  void updateProductStock(int productId, int newStock, int reservedStock) {
    final index = _products.indexWhere((p) => p.id == productId);
    if (index != -1) {
      _products[index] = _products[index].copyWith(
        stock: newStock,
        reservedStock: reservedStock,
      );
      notifyListeners();
      debugPrint('Updated stock for product $productId: $newStock (reserved: $reservedStock)');
    }
  }

  // Update product price (called by socket listener)
  void updateProductPrice(int productId, double newPrice) {
    final index = _products.indexWhere((p) => p.id == productId);
    if (index != -1) {
      _products[index] = _products[index].copyWith(price: newPrice);
      notifyListeners();
      debugPrint('Updated price for product $productId: $newPrice');
    }
  }

  // Get product by ID
  Product? getProductById(int id) {
    try {
      return _products.firstWhere((p) => p.id == id);
    } catch (e) {
      return null;
    }
  }

  @override
  void dispose() {
    _socketService.disconnect();
    super.dispose();
  }
}
```

## 4. Update Product Card Widget (lib/widgets/product_card.dart)

```dart
import 'package:flutter/material.dart';
import '../models/product.dart';

class ProductCard extends StatelessWidget {
  final Product product;
  final VoidCallback? onTap;

  const ProductCard({
    Key? key,
    required this.product,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product Image
            Stack(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                  child: AspectRatio(
                    aspectRatio: 4 / 3,
                    child: product.imageFilename != null
                        ? Image.network(
                            'YOUR_API_URL/static/uploads/${product.imageFilename}',
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: Colors.grey[200],
                                child: const Icon(Icons.image, size: 50, color: Colors.grey),
                              );
                            },
                          )
                        : Container(
                            color: Colors.grey[200],
                            child: const Icon(Icons.image, size: 50, color: Colors.grey),
                          ),
                  ),
                ),
                // Out of Stock Overlay
                if (!product.isInStock)
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.8),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: Colors.white.withOpacity(0.1)),
                      ),
                      child: const Text(
                        'OUT OF STOCK',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            // Product Details
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Name
                  Text(
                    product.name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  // Price
                  Text(
                    '₱${product.price.toStringAsFixed(2)}',
                    style: const TextStyle(
                      color: Color(0xFFFF6A00),
                      fontWeight: FontWeight.w700,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 8),
                  // Stock Status
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: product.isInStock
                              ? Colors.green.withOpacity(0.1)
                              : Colors.red.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: product.isInStock ? Colors.green : Colors.red,
                          ),
                        ),
                        child: Text(
                          product.isInStock
                              ? 'In Stock (${product.availableStock})'
                              : 'Out of Stock',
                          style: TextStyle(
                            color: product.isInStock ? Colors.green : Colors.red,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 5. Initialize Socket in Main App (lib/main.dart)

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/product_provider.dart';
import 'services/socket_service.dart';

void main() {
  // Initialize socket service
  final socketService = SocketService();
  socketService.connect('http://YOUR_SERVER_URL:5000');

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ProductProvider()),
        // Add other providers here
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Kids & Baby Store',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomePage(),
    );
  }
}
```

## 6. Add Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.0.5
  http: ^1.1.0
  socket_io_client: ^2.0.3+1
```

## Testing Checklist

- [ ] Product list shows available stock (total - reserved)
- [ ] Out of stock products show badge
- [ ] Real-time updates when stock changes
- [ ] Real-time updates when price changes
- [ ] Cart validates against available stock
- [ ] Order placement reserves stock immediately
- [ ] Mobile and web show same values
