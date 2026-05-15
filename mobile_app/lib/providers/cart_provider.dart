import 'package:flutter/foundation.dart';
import '../services/buyer_service.dart';
import '../services/delivery_fee_service.dart';
import '../config/url_config.dart';

/// Cart model for a single item
class CartItem {
  final int id;
  final int productId;
  final String name;
  final double price;
  final String? imageUrl;
  int quantity;

  CartItem({
    required this.id,
    required this.productId,
    required this.name,
    required this.price,
    this.imageUrl,
    this.quantity = 1,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    final product = json['product'];
    final rawImage =
        json['image_url'] ?? json['product_image'] ?? json['image'];
    final productImage = rawImage ??
        (product is Map
            ? (product['image_url'] ??
                product['product_image'] ??
                product['image'])
            : null);
    final name = json['product_name'] ??
        json['name'] ??
        (product is Map ? product['name'] : null) ??
        '';
    final priceValue =
        json['price'] ?? (product is Map ? product['price'] : null) ?? 0;

    return CartItem(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      name: name.toString(),
      price: (priceValue as num).toDouble(),
      quantity: (json['quantity'] ?? 1) as int,
      imageUrl: UrlConfig.toAbsoluteImageUrl(productImage?.toString()),
    );
  }

  double get subtotal => price * quantity;

  Map<String, dynamic> toJson() => {
        'product_id': productId,
        'quantity': quantity,
      };
}

/// CartProvider manages shopping cart state
class CartProvider with ChangeNotifier {
  List<CartItem> _items = [];
  bool _isLoading = false;
  String? _error;

  List<CartItem> get items => _items;
  int get itemCount => _items.length;
  bool get isLoading => _isLoading;
  String? get error => _error;

  double get total {
    return _items.fold(0, (sum, item) => sum + item.subtotal);
  }

  double get subtotal => total;
  double get tax => total * 0.12; // 12% tax
  
  /// Calculate delivery fee based on buyer's province and item count
  double getDeliveryFee(String? province) {
    if (province == null || _items.isEmpty) return 0.0;
    return DeliveryFeeService.calculateTotalDeliveryFee(province, _items.length);
  }
  
  double getGrandTotal(String? province) => total + tax + getDeliveryFee(province);

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String? error) {
    _error = error;
    notifyListeners();
  }

  /// Load cart from backend
  Future<void> loadCart() async {
    _setLoading(true);
    _setError(null);
    try {
      final List<dynamic> items = await BuyerService.getCart();
      _items = items
          .map<CartItem>((item) => item is CartItem
              ? item
              : CartItem.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  /// Add item to cart
  Future<void> addItem(int productId, int quantity) async {
    _setLoading(true);
    _setError(null);
    try {
      final dynamic rawItem = await BuyerService.addToCart(
        productId: productId,
        quantity: quantity,
      );
      final CartItem newItem = rawItem is CartItem
          ? rawItem
          : CartItem.fromJson(rawItem as Map<String, dynamic>);
      final existingIndex =
          _items.indexWhere((i) => i.productId == newItem.productId);

      if (existingIndex >= 0) {
        _items[existingIndex] = newItem;
      } else {
        _items.add(newItem);
      }
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  /// Update item quantity
  Future<void> updateQuantity(int cartItemId, int quantity) async {
    final itemIndex = _items.indexWhere((i) => i.id == cartItemId);
    if (itemIndex >= 0) {
      _setLoading(true);
      _setError(null);
      try {
        if (quantity <= 0) {
          await BuyerService.removeFromCart(cartItemId);
          _items.removeAt(itemIndex);
        } else {
          await BuyerService.updateCartItem(cartItemId, quantity);
          _items[itemIndex].quantity = quantity;
        }
      } catch (e) {
        _setError(e.toString());
      } finally {
        _setLoading(false);
      }
    }
  }

  /// Remove item from cart
  Future<void> removeItem(int cartItemId) async {
    final itemIndex = _items.indexWhere((i) => i.id == cartItemId);
    if (itemIndex >= 0) {
      _setLoading(true);
      _setError(null);
      try {
        await BuyerService.removeFromCart(cartItemId);
        _items.removeAt(itemIndex);
      } catch (e) {
        _setError(e.toString());
      } finally {
        _setLoading(false);
      }
    }
  }

  /// Clear all items from cart
  Future<void> clear() async {
    _setLoading(true);
    _setError(null);
    try {
      await BuyerService.clearCart();
      _items.clear();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  /// Clear cart locally (for logout)
  void clearCart() {
    _items.clear();
    _error = null;
    _isLoading = false;
    notifyListeners();
  }

  /// Convert cart to order format
  List<Map<String, dynamic>> toOrderItems() {
    return _items.map((item) => item.toJson()).toList();
  }
}
