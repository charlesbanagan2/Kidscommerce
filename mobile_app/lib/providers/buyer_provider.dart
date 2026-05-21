import 'package:flutter/foundation.dart';
import 'dart:async';
import 'dart:io';
import '../config/url_config.dart';
import '../models/order.dart' as order_model;
import '../models/product.dart';
import '../services/buyer_service.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart' as cart_provider_module;

class Buyer {
  final String name;
  final String phoneNumber;
  final String address;

  Buyer({required this.name, required this.phoneNumber, required this.address});
}

/// BuyerProvider manages buyer-specific data and operations
/// Handles orders, returns, cart, messages, and profile management
class BuyerProvider with ChangeNotifier {
  // Products
  List<Product> _products = [];
  List<Product> _filteredProducts = [];
  Product? _selectedProduct;
  String _selectedCategory = 'All';
  List<String> _categories = ['All'];

  // Real-time update tracking
  DateTime? _lastProductSync;
  Timer? _autoRefreshTimer;
  final Duration _refreshInterval = const Duration(seconds: 30);
  bool _autoRefreshEnabled = false;

  // Orders
  List<order_model.Order> _allOrders = [];
  Map<String, List<order_model.Order>> _ordersByStatus = {};
  order_model.Order? _selectedOrder;

  // Returns
  List<order_model.ReturnRequest> _returns = [];
  order_model.ReturnRequest? _selectedReturn;

  // Cart
  List<cart_provider_module.CartItem> _cartItems = [];

  // Messages
  List<order_model.Conversation> _conversations = [];
  List<order_model.Message> _currentMessages = [];
  order_model.Conversation? _selectedConversation;

  // Profile
  Map<String, dynamic>? _profile;

  // Auth/session
  int? _userId;

  // Coupons
  List<dynamic> _availableCoupons = [];
  double _discount = 0.0;
  Map<String, dynamic>? _appliedCoupon;

  // Wishlist/Liked Products
  List<Product> _wishlistProducts = [];
  Set<int> _wishlistProductIds = {};

  // Loading & Error states
  bool _isLoading = false;
  String? _errorMessage;
  bool _isFetching = false;

  // Product Getters
  List<Product> get products =>
      _filteredProducts.isEmpty ? _products : _filteredProducts;
  List<Product> get allProducts => _products;
  Product? get selectedProduct => _selectedProduct;
  String get selectedCategory => _selectedCategory;
  List<String> get categories => _categories;

  // Getters
  List<order_model.Order> get allOrders => _allOrders;
  Map<String, List<order_model.Order>> get ordersByStatus => _ordersByStatus;
  order_model.Order? get selectedOrder => _selectedOrder;

  List<order_model.ReturnRequest> get returns => _returns;
  order_model.ReturnRequest? get selectedReturn => _selectedReturn;

  List<cart_provider_module.CartItem> get cartItems => _cartItems;
  double get cartTotal =>
      _cartItems.fold(0, (sum, item) => sum + item.subtotal);
  int get cartCount => _cartItems.length;

  List<order_model.Conversation> get conversations => _conversations;
  List<order_model.Message> get currentMessages => _currentMessages;
  order_model.Conversation? get selectedConversation => _selectedConversation;

  Map<String, dynamic>? get profile => _profile;
  Buyer? get buyer => _profile != null
      ? Buyer(
          name: '${_profile!['first_name'] ?? ''} ${_profile!['last_name'] ?? ''}'.trim(),
          phoneNumber: _profile!['phone'] ?? 'No Phone',
          address: _profile!['address'] ?? 'No Address',
        )
      : null;

  List<dynamic> get availableCoupons => _availableCoupons;
  double get discount => _discount;
  Map<String, dynamic>? get appliedCoupon => _appliedCoupon;

  // Wishlist getters
  List<Product> get wishlistProducts => _wishlistProducts;
  Set<int> get wishlistProductIds => _wishlistProductIds;
  bool isProductLiked(int productId) => _wishlistProductIds.contains(productId);

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isFetching => _isFetching;
  int? get userId => _userId;

  // Real-time update getters
  bool get autoRefreshEnabled => _autoRefreshEnabled;
  DateTime? get lastProductSync => _lastProductSync;
  Duration get refreshInterval => _refreshInterval;

  // ============= Products Methods =============

  /// Fetch all products from API with category mapping
  Future<void> fetchProducts({String? category, String? search, bool bustCache = false}) async {
    _setLoading(true);
    _clearError();

    try {
      // First, fetch categories to create a mapping
      Map<int, String> categoryMap = {};
      try {
        final categoriesResponse = await ApiService.request(
          'GET',
          '/api/v1/categories',
          auth: false,
        );

        if (categoriesResponse['categories'] != null) {
          for (var cat in categoriesResponse['categories'] as List) {
            categoryMap[cat['id'] as int] = cat['name'] as String;
          }
        }
      } catch (e) {
        debugPrint('âš ï¸ Could not fetch categories: $e');
      }

      // Fetch products with cache busting if requested
      final productsList = await ApiService.getProducts(
        search: search,
        inStockOnly: false,
        bustCache: bustCache,
      );

      // Convert API response to Product objects
      _products = productsList.map((productJson) {
        // Prepare image URL using centralized helper
        String imageUrl = productJson['image'] ?? '';
        imageUrl = UrlConfig.toAbsoluteImageUrl(imageUrl);
        productJson['image_url'] = imageUrl;

        // Prepare gallery URLs using centralized helper
        if (productJson['gallery'] != null) {
          List<String> galleryUrls = [];
          for (var galleryItem in productJson['gallery']) {
            String galleryUrl = galleryItem is String ? galleryItem : '';
            if (galleryUrl.isNotEmpty) {
              galleryUrl = UrlConfig.toAbsoluteImageUrl(galleryUrl);
              galleryUrls.add(galleryUrl);
            }
          }
          productJson['gallery'] = galleryUrls;
        }

        // Handle store_background URL
        if (productJson['store_background'] != null &&
            productJson['store_background'].isNotEmpty) {
          productJson['store_background_url'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_background']);
        }

        // Handle store_logo URL
        if (productJson['store_logo'] != null &&
            productJson['store_logo'].isNotEmpty) {
          productJson['store_logo'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_logo']);
        }

        // Get category name from mapping
        String categoryName = categoryMap[productJson['category_id']] ??
            productJson['category'] ??
            'Other';
        productJson['category'] = categoryName;

        // Use Product.fromJson for consistent parsing
        return Product.fromJson(productJson);
      }).toList();

      // Extract unique categories from fetched products
      _categories = ['All'] + _products.map((p) => p.category).toSet().toList();

      // Apply filters if provided
      _applyFilters(category: category, search: search);

      debugPrint('âœ… Fetched ${_products.length} products from API');
      debugPrint('ðŸ“‚ Categories: $_categories');
    } catch (e) {
      _setError('Failed to fetch products: $e');
      debugPrint('âŒ Error fetching products: $e');
    } finally {
      _setLoading(false);
      notifyListeners();
    }
  }

  /// Filter products by category
  void filterByCategory(String category) {
    _selectedCategory = category;
    _applyFilters(category: category);
    notifyListeners();
  }

  /// Search products by name
  void searchProducts(String query) {
    _applyFilters(search: query);
    notifyListeners();
  }

  /// Apply filters to products
  void _applyFilters({String? category, String? search}) {
    _filteredProducts = _products.where((product) {
      // Category filter
      if (category != null && category != 'All') {
        if (product.category != category) return false;
      }

      // Search filter
      if (search != null && search.isNotEmpty) {
        final searchLower = search.toLowerCase();
        final matchesName = product.name.toLowerCase().contains(searchLower);
        final matchesDesc =
            product.description?.toLowerCase().contains(searchLower) ?? false;
        if (!matchesName && !matchesDesc) return false;
      }

      return true;
    }).toList();
  }

  /// Select a product for detail view
  void selectProduct(Product product) {
    _selectedProduct = product;
    notifyListeners();
  }

  /// Clear selected product
  void clearSelectedProduct() {
    _selectedProduct = null;
    notifyListeners();
  }

  // ============= Real-time Product Updates =============

  /// Start auto-refresh of products (checks for updates periodically)
  void startAutoRefresh() {
    if (_autoRefreshEnabled) return; // Already running

    _autoRefreshEnabled = true;
    // Safeguard: Don't use future dates (device time might be wrong)
    final now = DateTime.now();
    final serverTime = DateTime(2025, 1, 1); // Minimum valid date
    _lastProductSync = now.isAfter(serverTime) ? now : null;

    _autoRefreshTimer = Timer.periodic(_refreshInterval, (_) {
      debugPrint('🔄 Auto-refreshing products...');
      syncProducts();
    });

    debugPrint('✅ Auto-refresh started (every ${_refreshInterval.inSeconds}s)');
  }

  /// Stop auto-refresh of products
  void stopAutoRefresh() {
    _autoRefreshTimer?.cancel();
    _autoRefreshTimer = null;
    _autoRefreshEnabled = false;
    debugPrint('🛑 Auto-refresh stopped');
  }

  /// Manually trigger a product sync (check for updates from server)
  Future<void> syncProducts({String? category, String? search}) async {
    if (_isFetching) return; // Prevent multiple simultaneous syncs

    _isFetching = true;

    try {
      List<dynamic> productsList = [];

      // Try efficient sync endpoint first (only fetch updated products)
      // Only use sync endpoint if user is authenticated
      if (_lastProductSync != null && ApiService.hasAccessToken()) {
        try {
          debugPrint(
              '🔄 Checking for product updates since $_lastProductSync...');

          final syncResponse = await ApiService.requestWithRetry(
            'GET',
            '/api/v1/products/sync?last_sync=${_lastProductSync!.toIso8601String()}&per_page=100',
            auth: true,
          );

          if (syncResponse['products'] != null) {
            productsList = syncResponse['products'] as List;
            debugPrint(
                '✨ Found ${productsList.length} updated/new products since last sync');

            // If we have updates, merge with existing products
            if (productsList.isNotEmpty) {
              // Process the sync updates
              await _processSyncUpdates(productsList);
              _lastProductSync = DateTime.now();
              _clearError();
              _isFetching = false;
              notifyListeners();
              return;
            }
          }
        } catch (e) {
          debugPrint(
              '⚠️ Sync endpoint unavailable: $e, falling back to full fetch');
          // Fall through to full fetch
        }
      }

      // Fallback: Fetch all products (full sync)
      debugPrint('📥 Performing full product sync...');
      productsList = await ApiService.getProducts(
        search: search,
        inStockOnly: false,
      );

      // Build category mapping
      Map<int, String> categoryMap = {};
      try {
        final categoriesResponse = await ApiService.request(
          'GET',
          '/api/v1/categories',
          auth: false,
        );

        if (categoriesResponse['categories'] != null) {
          for (var cat in categoriesResponse['categories'] as List) {
            categoryMap[cat['id'] as int] = cat['name'] as String;
          }
        }
      } catch (e) {
        debugPrint('⚠️ Could not fetch categories during sync: $e');
      }

      // Convert to Product objects
      final newProducts = productsList.map((productJson) {
        // Prepare image URL using centralized helper
        String imageUrl = productJson['image'] ?? '';
        imageUrl = UrlConfig.toAbsoluteImageUrl(imageUrl);
        productJson['image_url'] = imageUrl;

        // Prepare gallery URLs using centralized helper
        if (productJson['gallery'] != null) {
          List<String> galleryUrls = [];
          for (var galleryItem in productJson['gallery']) {
            String galleryUrl = galleryItem is String ? galleryItem : '';
            if (galleryUrl.isNotEmpty) {
              galleryUrl = UrlConfig.toAbsoluteImageUrl(galleryUrl);
              galleryUrls.add(galleryUrl);
            }
          }
          productJson['gallery'] = galleryUrls;
        }

        // Handle store_background URL
        if (productJson['store_background'] != null &&
            productJson['store_background'].isNotEmpty) {
          productJson['store_background_url'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_background']);
        }

        // Handle store_logo URL
        if (productJson['store_logo'] != null &&
            productJson['store_logo'].isNotEmpty) {
          productJson['store_logo'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_logo']);
        }

        // Get category name
        String categoryName = categoryMap[productJson['category_id']] ??
            productJson['category'] ??
            'Other';
        productJson['category'] = categoryName;

        return Product.fromJson(productJson);
      }).toList();

      // Detect changes and update
      _handleProductUpdate(newProducts);

      _lastProductSync = DateTime.now();
      _clearError();

      debugPrint('✅ Full sync complete - ${newProducts.length} products');
    } catch (e) {
      debugPrint('❌ Product sync error: $e');
      _setError('Failed to sync products: $e');
    } finally {
      _isFetching = false;
      notifyListeners();
    }
  }

  /// Process sync updates - merges with existing products
  Future<void> _processSyncUpdates(List<dynamic> syncedProductsList) async {
    try {
      // Build category mapping
      Map<int, String> categoryMap = {};
      try {
        final categoriesResponse = await ApiService.request(
          'GET',
          '/api/v1/categories',
          auth: false,
        );

        if (categoriesResponse['categories'] != null) {
          for (var cat in categoriesResponse['categories'] as List) {
            categoryMap[cat['id'] as int] = cat['name'] as String;
          }
        }
      } catch (e) {
        debugPrint('⚠️ Could not fetch categories: $e');
      }

      // Convert synced items to Product objects
      final syncedProducts = syncedProductsList.map((productJson) {
        // Prepare image URL using centralized helper
        String imageUrl = productJson['image'] ?? '';
        imageUrl = UrlConfig.toAbsoluteImageUrl(imageUrl);
        productJson['image_url'] = imageUrl;

        // Prepare gallery URLs using centralized helper
        if (productJson['gallery'] != null) {
          List<String> galleryUrls = [];
          for (var galleryItem in productJson['gallery']) {
            String galleryUrl = galleryItem is String ? galleryItem : '';
            if (galleryUrl.isNotEmpty) {
              galleryUrl = UrlConfig.toAbsoluteImageUrl(galleryUrl);
              galleryUrls.add(galleryUrl);
            }
          }
          productJson['gallery'] = galleryUrls;
        }

        // Handle store_background URL
        if (productJson['store_background'] != null &&
            productJson['store_background'].isNotEmpty) {
          productJson['store_background_url'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_background']);
        }

        // Handle store_logo URL
        if (productJson['store_logo'] != null &&
            productJson['store_logo'].isNotEmpty) {
          productJson['store_logo'] =
              UrlConfig.toAbsoluteImageUrl(productJson['store_logo']);
        }

        // Get category name
        String categoryName = categoryMap[productJson['category_id']] ??
            productJson['category'] ??
            'Other';
        productJson['category'] = categoryName;

        return Product.fromJson(productJson);
      }).toList();

      // Merge with existing products
      for (var syncedProduct in syncedProducts) {
        final existingIndex =
            _products.indexWhere((p) => p.id == syncedProduct.id);

        if (existingIndex >= 0) {
          // Update existing product
          _products[existingIndex] = syncedProduct;
          debugPrint('🔄 Updated product: ${syncedProduct.name}');
        } else {
          // Add new product
          _products.add(syncedProduct);
          debugPrint('✨ Added new product: ${syncedProduct.name}');
        }

        // Update selected product if it was synced
        if (_selectedProduct?.id == syncedProduct.id) {
          _selectedProduct = syncedProduct;
        }
      }

      // Update categories
      _categories = ['All'] + _products.map((p) => p.category).toSet().toList();

      // Re-apply current filters
      _applyFilters(
        category: _selectedCategory != 'All' ? _selectedCategory : null,
      );
    } catch (e) {
      debugPrint('❌ Error processing sync updates: $e');
    }
  }

  /// Handle product updates - compare with existing and update
  void _handleProductUpdate(List<Product> newProducts) {
    bool hasChanges = false;

    // Check for new, modified, or removed products
    if (newProducts.length != _products.length) {
      hasChanges = true;
      debugPrint(
          '📊 Product count changed: ${_products.length} → ${newProducts.length}');
    }

    // Track IDs of new products
    for (var newProduct in newProducts) {
      final existingProduct = _products.firstWhere(
        (p) => p.id == newProduct.id,
        orElse: () => Product(
          id: -1,
          name: '',
          price: 0,
          category: '',
          stock: 0,
          sellerId: 0,
        ),
      );

      if (existingProduct.id == -1) {
        // New product
        hasChanges = true;
        debugPrint('✨ New product detected: ${newProduct.name}');
      } else if (existingProduct != newProduct) {
        // Product was modified
        hasChanges = true;
        debugPrint('🔄 Product updated: ${newProduct.name}');
      }
    }

    // Update products list and re-apply filters
    if (hasChanges) {
      _products = newProducts;
      _categories = ['All'] + _products.map((p) => p.category).toSet().toList();

      // If a product detail is open, update it too
      if (_selectedProduct != null) {
        final updatedSelected = _products.firstWhere(
          (p) => p.id == _selectedProduct!.id,
          orElse: () => _selectedProduct!,
        );
        _selectedProduct = updatedSelected;
      }

      // Re-apply current filters
      _applyFilters(
        category: _selectedCategory != 'All' ? _selectedCategory : null,
      );
    }
  }

  // ============= Orders Methods =============

  /// Fetch all buyer orders
  Future<void> fetchOrders({String? status}) async {
    _setLoading(true);
    _clearError();

    try {
      final orders = await BuyerService.getOrders(status: status);
      
      // Sort orders by created_at DESC (latest first)
      _allOrders = List<order_model.Order>.from(orders);
      _allOrders.sort((a, b) => b.orderDate.compareTo(a.orderDate));
    } catch (e) {
      _setError('Failed to fetch orders: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Fetch orders grouped by status
  Future<void> fetchOrdersByStatus() async {
    _setLoading(true);
    _clearError();

    try {
      await ApiService.bootstrapFromStorage();
      
      debugPrint('📦 BuyerProvider: Fetching orders by status...');
      final grouped = await BuyerService.getOrdersByStatus();
      
      debugPrint('📊 Received grouped orders: ${grouped.keys.toList()}');
      grouped.forEach((status, orders) {
        debugPrint('   $status: ${orders.length} orders');
      });
      
      _ordersByStatus = grouped.map((status, orders) {
        final sortedOrders = List<order_model.Order>.from(orders);
        sortedOrders.sort((a, b) => b.orderDate.compareTo(a.orderDate));
        return MapEntry(status, sortedOrders);
      });
      
      _allOrders = [];
      _ordersByStatus.values.forEach((orders) {
        _allOrders.addAll(orders);
      });
      _allOrders.sort((a, b) => b.orderDate.compareTo(a.orderDate));
      
      debugPrint('✅ Total orders loaded: ${_allOrders.length}');
      debugPrint('📊 Orders by status after processing:');
      _ordersByStatus.forEach((status, orders) {
        debugPrint('   $status: ${orders.length} orders');
        if (orders.isNotEmpty) {
          debugPrint('      First order: #${orders.first.id}');
        }
      });
      
      notifyListeners();
    } catch (e) {
      debugPrint('❌ Orders fetch error: $e');
      _setError('Failed to fetch orders: $e');
      _ordersByStatus = {};
      _allOrders = [];
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  /// Select order for detail view
  Future<void> selectOrder(int orderId) async {
    _setLoading(true);
    _clearError();

    try {
      _selectedOrder = await BuyerService.getOrderDetail(orderId);
    } catch (e) {
      _setError('Failed to load order: $e');
      _selectedOrder = null;
    } finally {
      _setLoading(false);
    }
  }

  /// Cancel an order
  Future<bool> cancelOrder(int orderId, {String? reason}) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await BuyerService.cancelOrder(orderId, reason: reason);
      if (success) {
        // Update order in list
        await fetchOrders();
      }
      return success;
    } catch (e) {
      _setError('Failed to cancel order: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Confirm delivery of order
  Future<bool> confirmDelivery(int orderId) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await BuyerService.confirmDelivery(orderId);
      if (success) {
        await fetchOrders();
      }
      return success;
    } catch (e) {
      _setError('Failed to confirm delivery: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // ============= Returns Methods =============

  /// Fetch all return requests
  Future<void> fetchReturns() async {
    _setLoading(true);
    _clearError();

    try {
      final returns = await BuyerService.getReturns();
      _returns = returns;
    } catch (e) {
      _setError('Failed to fetch returns: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Select return for detail view
  Future<void> selectReturn(int returnId) async {
    _setLoading(true);
    _clearError();

    try {
      _selectedReturn = await BuyerService.getReturnDetail(returnId);
    } catch (e) {
      _setError('Failed to load return: $e');
      _selectedReturn = null;
    } finally {
      _setLoading(false);
    }
  }

  /// Create a return request
  Future<bool> createReturn({
    required int orderId,
    required String reason,
    required String description,
    List<String>? mediaUrls,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final returnRequest = await BuyerService.createReturnRequest(
        orderId: orderId,
        reason: reason,
        description: description,
        mediaUrls: mediaUrls,
      );
      _returns.add(returnRequest);
      return true;
    } catch (e) {
      _setError('Failed to create return: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Submit return request
  Future<bool> submitReturnRequest(
    int orderId,
    String reason,
    String description,
  ) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await BuyerService.submitReturnRequest(
        orderId: orderId,
        reason: reason,
        description: description,
      );
      if (success) {
        await fetchReturns();
      }
      return success;
    } catch (e) {
      _setError('Failed to submit return request: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Submit order rating
  Future<bool> submitOrderRating(
    int orderId,
    int rating,
    String comment,
  ) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await BuyerService.submitOrderRating(
        orderId: orderId,
        rating: rating,
        comment: comment,
      );
      return success;
    } catch (e) {
      _setError('Failed to submit rating: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Submit order rating with media files
  Future<bool> submitOrderRatingWithMedia(
    int orderId,
    int rating,
    String comment,
    List<File> mediaFiles,
  ) async {
    _setLoading(true);
    _clearError();

    try {
      final success = await BuyerService.submitOrderRatingWithMedia(
        orderId: orderId,
        rating: rating,
        comment: comment,
        mediaFiles: mediaFiles,
      );
      return success;
    } catch (e) {
      _setError('Failed to submit rating: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  cart_provider_module.CartItem _normalizeCartItem(dynamic item) {
    if (item is cart_provider_module.CartItem) {
      return item;
    }
    if (item is order_model.CartItem) {
      return cart_provider_module.CartItem(
        id: item.id,
        productId: item.productId,
        name: item.productName,
        price: item.price,
        quantity: item.quantity,
        imageUrl: UrlConfig.toAbsoluteImageUrl(item.productImage),
      );
    }
    if (item is Map<String, dynamic>) {
      return cart_provider_module.CartItem.fromJson(item);
    }
    throw Exception('Unsupported cart item type');
  }

  List<cart_provider_module.CartItem> _normalizeCartItems(List items) {
    return items.map(_normalizeCartItem).toList();
  }

  // ============= Cart Methods =============

  /// Fetch cart items and validate against current stock
  Future<void> fetchCart() async {
    _isFetching = true;
    _clearError();

    try {
      final items = await BuyerService.getCart();
      _cartItems = _normalizeCartItems(items);
      
      // Validate cart items against current stock
      await _validateCartStock();
    } catch (e) {
      _setError('Failed to fetch cart: $e');
    } finally {
      _isFetching = false;
      notifyListeners();
    }
  }

  /// Validate cart items against current product stock
  Future<void> _validateCartStock() async {
    bool hasChanges = false;
    final itemsToUpdate = <int, int>{};

    for (var cartItem in _cartItems) {
      final product = _products.firstWhere(
        (p) => p.id == cartItem.productId,
        orElse: () => Product(
          id: cartItem.productId,
          name: '',
          price: 0,
          category: '',
          stock: 0,
          sellerId: 0,
        ),
      );

      // If cart quantity exceeds available stock, auto-adjust
      if (cartItem.quantity > product.stock) {
        if (product.stock > 0) {
          debugPrint('⚠️ Auto-adjusting ${cartItem.name}: ${cartItem.quantity} → ${product.stock}');
          itemsToUpdate[cartItem.id] = product.stock;
          hasChanges = true;
        } else {
          debugPrint('⚠️ ${cartItem.name} is out of stock');
          // Item is out of stock, will be handled by UI
        }
      }
    }

    // Update cart items that exceed stock
    for (var entry in itemsToUpdate.entries) {
      try {
        await updateCartItem(entry.key, entry.value);
      } catch (e) {
        debugPrint('❌ Failed to auto-adjust cart item ${entry.key}: $e');
      }
    }

    if (hasChanges) {
      debugPrint('✅ Cart quantities auto-adjusted to match available stock');
    }
  }

  /// Add item to cart with real-time stock validation
  Future<bool> addToCart(
    int productId,
    int quantity, {
    String? size,
    String? color,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      // Get current product stock
      final product = _products.firstWhere(
        (p) => p.id == productId,
        orElse: () => Product(
          id: productId,
          name: '',
          price: 0,
          category: '',
          stock: 0,
          sellerId: 0,
        ),
      );

      // Check existing quantity in cart
      final existingCartItem = _cartItems.firstWhere(
        (item) => item.productId == productId,
        orElse: () => cart_provider_module.CartItem(
          id: -1,
          productId: productId,
          name: '',
          price: 0,
          quantity: 0,
        ),
      );

      final currentCartQty = existingCartItem.id != -1 ? existingCartItem.quantity : 0;
      final requestedTotal = currentCartQty + quantity;

      // Validate against available stock
      if (product.stock <= 0) {
        _setError('This product is out of stock');
        return false;
      }

      if (requestedTotal > product.stock) {
        final availableToAdd = product.stock - currentCartQty;
        if (availableToAdd <= 0) {
          _setError('Maximum stock (${product.stock}) already in cart');
          return false;
        }
        _setError('Only $availableToAdd more available (${product.stock} in stock, ${currentCartQty} in cart)');
        return false;
      }

      final rawItem = await BuyerService.addToCart(
        productId: productId,
        quantity: quantity,
        size: size,
        color: color,
      );
      final item = _normalizeCartItem(rawItem);

      // Check if item already exists in cart to avoid duplicates
      final existingIndex =
          _cartItems.indexWhere((cartItem) => cartItem.id == item.id);
      if (existingIndex == -1) {
        _cartItems.add(item);
      } else {
        // Update quantity if item already exists
        _cartItems[existingIndex].quantity = item.quantity;
      }

      notifyListeners();
      return true;
    } catch (e) {
      _setError(_friendlyCartError(e));
      return false;
    } finally {
      _setLoading(false);
      notifyListeners();
    }
  }

  String _friendlyCartError(Object error) {
    if (error is ApiException) {
      final status = error.statusCode;
      if (status == 404) {
        return 'Product not found or unavailable. Please refresh and try again.';
      }
      if (status == 401 || status == 403) {
        return 'Please log in again.';
      }
      final message = error.message.toLowerCase();
      if (message.contains('network')) {
        return 'Check your internet connection.';
      }
      if (message.contains('timeout')) {
        return 'Request timeout. Please try again.';
      }
      if (message.contains('stock')) {
        return error.message;
      }
    }

    final fallback = error.toString().toLowerCase();
    if (fallback.contains('network') ||
        fallback.contains('socket') ||
        fallback.contains('connection')) {
      return 'Check your internet connection.';
    }
    if (fallback.contains('timeout')) {
      return 'Request timeout. Please try again.';
    }
    if (fallback.contains('not found') || fallback.contains('404')) {
      return 'Product not found. Please refresh and try again.';
    }
    return 'Could not add to cart. Please try again.';
  }

  /// Add product object to cart (convenience method) with stock validation
  Future<bool> addProductToCart(dynamic product, {int quantity = 1}) async {
    // Sync product data first to get latest stock
    await syncProducts();
    
    return addToCart(
      product.id,
      quantity,
    );
  }

  /// Update cart item quantity with real-time stock validation
  Future<bool> updateCartItem(int itemId, int quantity) async {
    _clearError();

    try {
      // Find the cart item
      final cartItem = _cartItems.firstWhere(
        (item) => item.id == itemId,
        orElse: () => cart_provider_module.CartItem(
          id: -1,
          productId: -1,
          name: '',
          price: 0,
          quantity: 0,
        ),
      );

      if (cartItem.id == -1) {
        _setError('Cart item not found');
        return false;
      }

      // Get current product stock
      final product = _products.firstWhere(
        (p) => p.id == cartItem.productId,
        orElse: () => Product(
          id: cartItem.productId,
          name: '',
          price: 0,
          category: '',
          stock: 0,
          sellerId: 0,
        ),
      );

      // Validate against available stock
      if (quantity > product.stock) {
        _setError('Only ${product.stock} available in stock');
        // Auto-adjust to maximum available
        quantity = product.stock;
        if (quantity <= 0) {
          _setError('Product is out of stock');
          return false;
        }
      }

      final rawUpdated = await BuyerService.updateCartItem(itemId, quantity);
      final updated = _normalizeCartItem(rawUpdated);
      final index = _cartItems.indexWhere((item) => item.id == itemId);
      if (index != -1) {
        _cartItems[index] = updated;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError('Failed to update cart: $e');
      return false;
    }
  }

  /// Remove item from cart
  Future<bool> removeFromCart(int itemId) async {
    try {
      final success = await BuyerService.removeFromCart(itemId);
      if (success) {
        _cartItems.removeWhere((item) => item.id == itemId);
      }
      return success;
    } catch (e) {
      _setError('Failed to remove from cart: $e');
      return false;
    }
  }

  /// Clear entire cart
  Future<bool> clearCart() async {
    try {
      final success = await BuyerService.clearCart();
      if (success) {
        _cartItems.clear();
      }
      return success;
    } catch (e) {
      _setError('Failed to clear cart: $e');
      return false;
    }
  }

  // ============= Wishlist Methods =============

  /// Fetch wishlist products
  Future<void> fetchWishlist() async {
    _clearError();

    try {
      final wishlistData = await ApiService.getWishlist();
      
      // Extract product IDs and build full product objects
      _wishlistProductIds = <int>{};
      _wishlistProducts = [];
      
      for (final item in wishlistData) {
        final productId = item['product_id'] as int?;
        if (productId != null) {
          _wishlistProductIds.add(productId);
          
          // Build product from wishlist data directly
          final product = Product(
            id: productId,
            name: item['product_name'] ?? item['name'] ?? 'Unknown Product',
            price: (item['price'] as num?)?.toDouble() ?? 0.0,
            category: item['category'] ?? '',
            stock: item['stock'] as int? ?? 0,
            sellerId: item['seller_id'] as int? ?? 0,
            imageUrl: item['product_image'] as String? ?? item['image_url'] as String?,
            description: item['description'] as String?,
            rating: (item['rating'] as num?)?.toDouble() ?? 0.0,
            reviewCount: item['review_count'] as int? ?? 0,
            salePrice: item['sale_price'] != null ? (item['sale_price'] as num).toDouble() : null,
          );
          _wishlistProducts.add(product);
        }
      }
      
      debugPrint('✅ Wishlist loaded: ${_wishlistProducts.length} products, IDs: $_wishlistProductIds');
      notifyListeners();
    } catch (e) {
      debugPrint('❌ Failed to fetch wishlist: $e');
      _setError('Failed to fetch wishlist: $e');
    }
  }

  /// Add product to wishlist
  Future<bool> addToWishlist(int productId) async {
    _clearError();

    try {
      // Check if product is already in wishlist locally to avoid API error
      if (_wishlistProductIds.contains(productId)) {
        debugPrint('ℹ️ Product already in wishlist: $productId');
        return true;
      }

      final result = await ApiService.addToWishlist(productId);
      
      if (result['success'] == true || result.containsKey('id')) {
        // Immediately update local state
        _wishlistProductIds.add(productId);
        
        // Find and add the full product to wishlist products
        final product = _products.firstWhere(
          (p) => p.id == productId,
          orElse: () => Product(
            id: productId,
            name: 'Unknown Product',
            price: 0.0,
            category: '',
            stock: 0,
            sellerId: 0,
          ),
        );
        
        if (!_wishlistProducts.any((p) => p.id == productId)) {
          _wishlistProducts.add(product);
        }
        
        debugPrint('✅ Added to wishlist: $productId, Total: ${_wishlistProducts.length}');
        notifyListeners();
        
        // Refresh from backend to ensure sync
        await fetchWishlist();
        return true;
      } else {
        _setError(result['message'] ?? 'Failed to add to wishlist');
        return false;
      }
    } catch (e) {
      debugPrint('❌ Failed to add to wishlist: $e');
      _setError('Failed to add to wishlist: $e');
      return false;
    }
  }

  /// Remove product from wishlist
  Future<bool> removeFromWishlist(int productId) async {
    _clearError();

    try {
      final result = await ApiService.removeFromWishlist(productId);
      
      if (result['success'] == true) {
        // Immediately update local state
        _wishlistProductIds.remove(productId);
        _wishlistProducts.removeWhere((p) => p.id == productId);
        debugPrint('✅ Removed from wishlist: $productId, Remaining: ${_wishlistProducts.length}');
        notifyListeners();
        
        // Refresh from backend to ensure sync
        await fetchWishlist();
        return true;
      } else {
        _setError(result['message'] ?? 'Failed to remove from wishlist');
        return false;
      }
    } catch (e) {
      debugPrint('❌ Failed to remove from wishlist: $e');
      _setError('Failed to remove from wishlist: $e');
      return false;
    }
  }

  /// Toggle product in wishlist (add if not present, remove if present)
  Future<bool> toggleWishlist(int productId) async {
    if (isProductLiked(productId)) {
      return await removeFromWishlist(productId);
    } else {
      return await addToWishlist(productId);
    }
  }

  // ============= Checkout Methods =============

  /// Checkout and create order
  Future<order_model.Order?> checkout({
    required String recipientName,
    required String recipientPhone,
    required String shippingAddress,
    String? paymentMethod = 'cod',
    String? notes,
    List<int>? selectedItemIds,
    Map<int, int>? productQuantities,
    int? couponId,
    double? shippingFee,
    double? deliveryFee,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final order = await BuyerService.checkout(
        recipientName: recipientName,
        recipientPhone: recipientPhone,
        shippingAddress: shippingAddress,
        paymentMethod: paymentMethod,
        notes: notes,
        selectedItemIds: selectedItemIds,
        productQuantities: productQuantities,
        couponId: couponId,
        shippingFee: shippingFee,
        deliveryFee: deliveryFee,
      );

      _allOrders.add(order);
      
      // Only remove selected items from cart, not all items
      if (selectedItemIds != null && selectedItemIds.isNotEmpty) {
        // Remove only the checked out items
        _cartItems.removeWhere((item) => selectedItemIds.contains(item.id));
        notifyListeners();
      } else {
        // If no specific items selected, clear entire cart (original behavior)
        await clearCart();
      }
      
      return order;
    } catch (e) {
      _setError('Checkout failed: $e');
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// Apply coupon code
  Future<bool> applyCoupon(String couponCode) async {
    _setLoading(true);
    _clearError();
    try {
      final response = await ApiService.request(
        'POST',
        '/api/apply-coupon',
        auth: true,
        body: {'coupon_code': couponCode},
      );

      if (response.containsKey('discount_amount')) {
        _discount = (response['discount_amount'] as num).toDouble();
        // Store coupon data from response
        if (response.containsKey('coupon')) {
          _appliedCoupon = response['coupon'] as Map<String, dynamic>;
        }
        _clearError();
        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Invalid coupon code');
        return false;
      }
    } catch (e) {
      _setError('Failed to apply coupon: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchAvailableCoupons() async {
    _setLoading(true);
    _clearError();
    try {
      final response = await ApiService.request(
        'GET',
        '/api/available-coupons',
        auth: true,
      );
      if (response.containsKey('coupons')) {
        _availableCoupons = response['coupons'];
      }
    } catch (e) {
      _setError('Failed to fetch coupons: $e');
    } finally {
      _setLoading(false);
    }
  }

  // ============= Messages Methods =============

  /// Fetch all conversations
  Future<void> fetchConversations() async {
    _setLoading(true);
    _clearError();

    try {
      final convos = await BuyerService.getConversations();
      _conversations = convos;
    } catch (e) {
      _setError('Failed to fetch conversations: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Select conversation and fetch messages
  Future<void> selectConversation(int peerId, {bool isSeller = true}) async {
    _setLoading(true);
    _clearError();

    try {
      final messages =
          await BuyerService.getMessages(peerId, isSeller: isSeller);
      _currentMessages = messages;
      _selectedConversation = _conversations.firstWhere(
        (conv) => conv.peerId == peerId && conv.isPeerSeller == isSeller,
        orElse: () => order_model.Conversation(
          id: 0,
          peerId: peerId,
          peerName: 'Unknown',
          lastMessage: '',
          lastMessageTime: DateTime.now(),
          unreadCount: 0,
          isPeerSeller: isSeller,
        ),
      );
    } catch (e) {
      _setError('Failed to load conversation: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Send message
  Future<bool> sendMessage({
    required int recipientId,
    required String content,
    required bool isSeller,
    String? mediaUrl,
  }) async {
    try {
      final message = await BuyerService.sendMessage(
        recipientId: recipientId,
        content: content,
        isSeller: isSeller,
        mediaUrl: mediaUrl,
      );
      _currentMessages.add(message);
      return true;
    } catch (e) {
      _setError('Failed to send message: $e');
      return false;
    }
  }

  /// Mark messages as read
  Future<bool> markMessagesAsRead(int peerId, {bool isSeller = true}) async {
    try {
      return await BuyerService.markMessagesAsRead(peerId, isSeller: isSeller);
    } catch (e) {
      _setError('Failed to mark messages as read: $e');
      return false;
    }
  }

  // ============= Profile Methods =============

  /// Fetch buyer profile
  Future<void> fetchProfile() async {
    _setLoading(true);
    _clearError();

    try {
      final profile = await BuyerService.getProfile();
      _profile = profile;
      
      // Also fetch wishlist when profile is loaded (don't await to avoid blocking)
      fetchWishlist();
    } catch (e) {
      _setError('Failed to fetch profile: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Update profile
  Future<bool> updateProfile({
    String? firstName,
    String? lastName,
    String? phone,
    String? address,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final updated = await BuyerService.updateProfile(
        firstName: firstName,
        lastName: lastName,
        phone: phone,
        address: address,
      );
      _profile = updated;
      return true;
    } catch (e) {
      _setError('Failed to update profile: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Update profile picture
  Future<bool> updateProfilePicture(String imagePath) async {
    _setLoading(true);
    _clearError();

    try {
      final imageUrl = await BuyerService.updateProfilePicture(imagePath);
      if (_profile != null) {
        _profile!['profile_picture'] = imageUrl;
      }
      return true;
    } catch (e) {
      _setError('Failed to update profile picture: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // ============= Helper Methods =============

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _clearError() {
    _errorMessage = null;
  }

  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }

  void clearError() {
    _clearError();
    notifyListeners();
  }

  void clearSelectedOrder() {
    _selectedOrder = null;
    notifyListeners();
  }

  void clearSelectedReturn() {
    _selectedReturn = null;
    notifyListeners();
  }

  void clearConversation() {
    _selectedConversation = null;
    _currentMessages.clear();
    notifyListeners();
  }

  /// Cleanup resources - should be called when provider is disposed or on logout
  void cleanup() {
    stopAutoRefresh(); // Stop any running auto-refresh timer
    
    // Clear all data
    _products = [];
    _filteredProducts = [];
    _selectedProduct = null;
    _selectedCategory = 'All';
    _categories = ['All'];
    _lastProductSync = null;
    _allOrders = [];
    _ordersByStatus = {};
    _selectedOrder = null;
    _returns = [];
    _selectedReturn = null;
    _cartItems = [];
    _wishlistProducts = [];
    _wishlistProductIds = {};
    _conversations = [];
    _currentMessages = [];
    _selectedConversation = null;
    _profile = null;
    _userId = null;
    _availableCoupons = [];
    _discount = 0.0;
    _appliedCoupon = null;
    _isLoading = false;
    _errorMessage = null;
    _isFetching = false;
    
    debugPrint('🧹 BuyerProvider cleanup completed');
  }
}
