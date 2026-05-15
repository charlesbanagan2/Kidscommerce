import 'package:flutter/foundation.dart';

/// Order model
class Order {
  final int id;
  final String status;
  final double total;
  final String paymentMethod;
  final String paymentStatus;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<dynamic> items;

  Order({
    required this.id,
    required this.status,
    required this.total,
    required this.paymentMethod,
    required this.paymentStatus,
    required this.createdAt,
    this.updatedAt,
    this.items = const [],
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] ?? 0,
      status: json['status'] ?? 'pending',
      total: (json['total_amount'] ?? 0.0).toDouble(),
      paymentMethod: json['payment_method'] ?? '',
      paymentStatus: json['payment_status'] ?? 'pending',
      createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
      items: json['items'] ?? [],
    );
  }

  bool get isPending => status == 'pending';
  bool get isProcessing => status == 'processing';
  bool get isShipped => status == 'shipped';
  bool get isCompleted => status == 'completed';
  bool get isCancelled => status == 'cancelled';

  String get statusDisplay {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Pending';
      case 'processing':
        return 'Processing';
      case 'shipped':
        return 'Shipped';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }
}

/// OrderProvider manages user orders
class OrderProvider with ChangeNotifier {
  final List<Order> _orders = [];
  Order? _selectedOrder;
  bool _isLoading = false;
  String? _errorMessage;

  List<Order> get orders => _orders;
  Order? get selectedOrder => _selectedOrder;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// Add order to list
  void addOrder(Order order) {
    _orders.insert(0, order); // Add to beginning
    notifyListeners();
  }

  /// Update order status
  void updateOrderStatus(int orderId, String newStatus) {
    final orderIndex = _orders.indexWhere((o) => o.id == orderId);
    if (orderIndex >= 0) {
      _orders[orderIndex] = Order(
        id: _orders[orderIndex].id,
        status: newStatus,
        total: _orders[orderIndex].total,
        paymentMethod: _orders[orderIndex].paymentMethod,
        paymentStatus: _orders[orderIndex].paymentStatus,
        createdAt: _orders[orderIndex].createdAt,
        updatedAt: DateTime.now(),
        items: _orders[orderIndex].items,
      );

      if (_selectedOrder?.id == orderId) {
        _selectedOrder = _orders[orderIndex];
      }

      notifyListeners();
    }
  }

  /// Set selected order
  void selectOrder(Order order) {
    _selectedOrder = order;
    notifyListeners();
  }

  /// Get orders by status
  List<Order> getOrdersByStatus(String status) {
    return _orders.where((o) => o.status == status).toList();
  }

  /// Clear all orders
  void clearOrders() {
    _orders.clear();
    _selectedOrder = null;
    notifyListeners();
  }

  /// Set loading state
  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// Set error message
  void setError(String? error) {
    _errorMessage = error;
    notifyListeners();
  }
}
