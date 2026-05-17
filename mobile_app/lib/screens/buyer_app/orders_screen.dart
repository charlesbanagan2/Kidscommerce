import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import '../../widgets/loading_time_indicator.dart';
import '../../widgets/skeleton_loader.dart';
import 'order_detail.dart';
import 'buyer_home_screen.dart';

/// Orders Screen
class OrdersScreen extends StatefulWidget {
  final String? initialFilter;

  const OrdersScreen({super.key, this.initialFilter});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  late String _selectedFilter;

  @override
  void initState() {
    super.initState();
    _selectedFilter = widget.initialFilter ?? 'all';
  }

  Future<void> _loadOrders() async {
    final buyerProvider = context.read<BuyerProvider>();
    final authProvider = context.read<AuthProvider>();

    if (!authProvider.isAuthenticated) {
      debugPrint('⚠️ Not authenticated, skipping order fetch');
      return;
    }

    ApiService.clearOrdersCache();

    try {
      debugPrint('🔍 Orders screen - fetching orders...');
      await buyerProvider.fetchOrdersByStatus();
      if (mounted) {
        debugPrint('✅ Orders loaded: ${buyerProvider.allOrders.length} total');
        LoadingTimeSnackbar.show(context, 'Fetch Orders');
      }
    } catch (e) {
      debugPrint('❌ Error loading orders: $e');
    }
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();

    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      body: Column(
        children: [
          _buildHeader(),
          _buildFilterTabs(),
          Expanded(
            child:
                buyerProvider.isLoading && buyerProvider.ordersByStatus.isEmpty
                    ? const ListSkeletonLoader(
                        itemSkeleton: OrderCardSkeleton(),
                        itemCount: 6,
                        padding: EdgeInsets.all(16),
                      )
                    : _buildOrdersBody(buyerProvider),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
        ),
      ),
      padding: EdgeInsets.fromLTRB(
        12,
        MediaQuery.of(context).padding.top + 8,
        12,
        16,
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(LucideIcons.arrowLeft, color: Colors.white),
            onPressed: () {
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(
                  builder: (context) => const BuyerHomeScreen(),
                ),
                (route) => false,
              );
            },
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
            iconSize: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'My Orders',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  'Track and manage your orders',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 11,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterTabs() {
    final filters = [
      ('all', 'All'),
      ('to_pay', 'Pending'),
      ('to_ship', 'Processing'),
      ('to_receive', 'To Receive'),
      ('completed', 'Completed'),
      ('returns', 'Returns'),
      ('cancelled', 'Cancelled'),
    ];

    return Container(
      color: Colors.white,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: filters.map((filter) {
            final isSelected = _selectedFilter == filter.$1;
            return GestureDetector(
              onTap: () {
                debugPrint('📋 Orders filter: ${filter.$1}');
                setState(() => _selectedFilter = filter.$1);
              },
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(
                      color: isSelected
                          ? const Color(0xFF1e4db7)
                          : Colors.transparent,
                      width: 2,
                    ),
                  ),
                ),
                child: Text(
                  filter.$2,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isSelected
                        ? const Color(0xFF1e4db7)
                        : Colors.grey.shade600,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildOrdersBody(BuyerProvider buyerProvider) {
    if (_selectedFilter == 'returns') {
      return _buildReturnsList(buyerProvider);
    } else if (_selectedFilter == 'all') {
      return _buildAllOrdersList(buyerProvider);
    } else {
      return _buildOrderList(buyerProvider, _selectedFilter);
    }
  }

  Widget _buildAllOrdersList(BuyerProvider buyerProvider) {
    // Use allOrders from provider which is now populated
    final allOrders = List.from(buyerProvider.allOrders);

    // Sort by order date descending (latest first)
    allOrders.sort((a, b) => b.orderDate.compareTo(a.orderDate));

    debugPrint('📊 Building all orders list: ${allOrders.length} orders');

    if (allOrders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(LucideIcons.inbox, size: 80, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text(
              'No orders yet',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text(
              'Start shopping to see your orders here',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadOrders,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: allOrders.length,
        itemBuilder: (context, index) {
          final order = allOrders[index];
          return _buildOrderCard(context, order, buyerProvider, order.status);
        },
      ),
    );
  }

  Widget _buildOrderList(BuyerProvider buyerProvider, String status) {
    final orders = List.from(buyerProvider.ordersByStatus[status] ?? []);

    // Sort by order date descending (latest first)
    orders.sort((a, b) => b.orderDate.compareTo(a.orderDate));

    debugPrint('📊 Building $status orders list: ${orders.length} orders');

    if (orders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox, size: 80, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              _emptyTitle(status),
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text(
              _emptySubtitle(status),
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadOrders,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
              child: _buildInfoBanner(status, orders),
            ),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.all(12),
              itemCount: orders.length,
              itemBuilder: (context, index) {
                final order = orders[index];
                return _buildOrderCard(context, order, buyerProvider, status);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOrderCard(
    BuildContext context,
    dynamic order,
    BuyerProvider buyerProvider,
    String contextTab,
  ) {
    final items = order.items as List<dynamic>;
    // Get first item for display
    final firstItem = items.isNotEmpty ? items.first : null;

    final String? productImage = firstItem?.productImage ??
        (firstItem is Map
            ? firstItem['image_url'] ?? firstItem['image']
            : null);
    final imageUrl = productImage != null && productImage.isNotEmpty
        ? UrlConfig.toAbsoluteImageUrl(productImage)
        : null;

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => OrderDetailScreen(
              orderId: order.id,
              sourceTab: contextTab, // Pass the tab context
            ),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
            ),
          ],
        ),
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // Product Image
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Container(
                width: 64,
                height: 64,
                color: Colors.grey.shade200,
                child: imageUrl != null
                    ? Image.network(
                        imageUrl,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => Icon(
                            Icons.image_not_supported,
                            color: Colors.grey.shade400),
                      )
                    : Icon(Icons.image, color: Colors.grey.shade400),
              ),
            ),
            const SizedBox(width: 12),

            // Order Details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Name
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          firstItem?.productName ?? 'Order ${order.id}',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        LucideIcons.chevronRight,
                        size: 14,
                        color: Colors.grey.shade400,
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),

                  // Order ID and Date
                  Text(
                    'Order #${order.id} · ${order.orderDate.toString().split(' ')[0]}',
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.grey.shade500,
                    ),
                  ),
                  const SizedBox(height: 6),

                  // Status and Price Row
                  Row(
                    children: [
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getStatusColor(order.status)
                                .withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              _getStatusIcon(order.status),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  _compactStatusLabel(
                                    order.status,
                                    contextTab,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: _getStatusColor(order.status),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '₱${order.totalAmount.toStringAsFixed(2)}',
                        maxLines: 1,
                        overflow: TextOverflow.clip,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1e4db7),
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

  Widget _getStatusIcon(String status) {
    IconData icon;
    Color color;

    switch (status.toLowerCase()) {
      case 'pending':
      case 'to_pay':
        icon = LucideIcons.clock;
        color = Colors.orange;
        break;
      case 'to_ship':
      case 'processing':
        icon = LucideIcons.package;
        color = Colors.blue;
        break;
      case 'in_transit':
      case 'to_receive':
        icon = LucideIcons.truck;
        color = Colors.purple;
        break;
      case 'delivered':
      case 'completed':
        icon = LucideIcons.checkCircle2;
        color = Colors.green;
        break;
      case 'cancelled':
        icon = LucideIcons.xCircle;
        color = Colors.red;
        break;
      case 'returned':
      case 'refunded':
      case 'return_approved':
      case 'refund_approved':
        icon = LucideIcons.undo2;
        color = Colors.purple;
        break;
      default:
        if (status.contains('return') || status.contains('refund')) {
          icon = LucideIcons.undo2;
          color = Colors.purple;
        } else {
          icon = LucideIcons.helpCircle;
          color = Colors.grey;
        }
    }

    return Icon(icon, size: 12, color: color);
  }

  Widget _buildInfoBanner(String status, List<dynamic> orders) {
    if (orders.isEmpty) {
      return const SizedBox.shrink();
    }

    if (status == 'to_pay' || status == 'to_ship') {
      final bool isCod =
          orders.any((o) => (o.paymentMethod as String).toLowerCase() == 'cod');
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFDBEAFE),
          borderRadius: BorderRadius.circular(8),
          border: const Border(
              left: BorderSide(color: Color(0xFF3B82F6), width: 4)),
        ),
        child: Row(
          children: [
            const Icon(Icons.info, color: Color(0xFF3B82F6), size: 18),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                isCod
                    ? 'Cash on Delivery. No payment action needed. Waiting for seller to process your order.'
                    : 'Order placed successfully. Waiting for seller to process your order.',
                style: const TextStyle(
                    color: Color(0xFF1E40AF),
                    fontSize: 12,
                    fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      );
    }

    if (status == 'to_receive') {
      final bool delivered =
          orders.any((o) => (o.status as String) == 'delivered');
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFDCFCE7),
          borderRadius: BorderRadius.circular(8),
          border: const Border(
              left: BorderSide(color: Color(0xFF22C55E), width: 4)),
        ),
        child: Row(
          children: [
            Icon(delivered ? Icons.check_circle : Icons.local_shipping,
                color: const Color(0xFF22C55E), size: 18),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                delivered
                    ? 'Your order has been delivered. Confirm receipt to complete.'
                    : 'Your order is on the way. Track it for real-time updates.',
                style: const TextStyle(
                    color: Color(0xFF166534),
                    fontSize: 12,
                    fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  /// Shorter labels for order list cards to avoid horizontal overflow.
  String _compactStatusLabel(String status, String contextTab) {
    final normalized = status.toLowerCase();
    if (normalized == 'return_requested') {
      return 'Return Requested';
    }
    if (contextTab == 'returns') {
      if (normalized.contains('refund')) return 'Refunded';
      if (normalized.contains('return')) return 'Returned';
    }
    switch (normalized) {
      case 'return_requested':
        return 'Return Requested';
      case 'refund_approved':
      case 'refund_processing':
      case 'refunded':
        return 'Refunded';
      case 'return_approved':
      case 'returned':
        return 'Returned';
      case 'out_for_delivery':
        return 'Out for Delivery';
      case 'ready_for_pickup':
        return 'Ready for Pickup';
      default:
        return _statusLabel(status, contextTab);
    }
  }

  String _statusLabel(String status, String contextTab) {
    if (status.toLowerCase() == 'return_requested') {
      return 'Return & Refund Requested';
    }
    if (contextTab == 'returns') {
      if (status.toLowerCase().contains('refund')) {
        return 'Refunded';
      } else if (status.toLowerCase().contains('return')) {
        return 'Returned';
      }
    }
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Pending';
      case 'to_pay':
        return 'To Pay';
      case 'to_ship':
      case 'processing':
      case 'ready_for_pickup':
        return 'Processing';
      case 'in_transit':
      case 'out_for_delivery':
        return 'Out for Delivery';
      case 'to_receive':
        return 'To Receive';
      case 'delivered':
        return 'Delivered';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'refunded':
      case 'refund_approved':
      case 'refund_processing':
        return 'Refunded';
      case 'returned':
      case 'return_approved':
        return 'Returned';
      case 'return_requested':
        return 'Return & Refund Requested';
      case 'rejected':
        return 'Rejected';
      default:
        if (status.toLowerCase().contains('refund')) {
          return 'Refunded';
        }
        if (status.toLowerCase().contains('return')) {
          return 'Returned';
        }
        return OrderStatusLabel(status).label;
    }
  }

  String _emptyTitle(String status) {
    switch (status) {
      case 'to_pay':
        return 'No Orders to Pay';
      case 'to_ship':
        return 'No Orders Being Prepared';
      case 'to_receive':
        return 'No Orders in Transit';
      case 'completed':
        return 'No Completed Orders';
      case 'cancelled':
        return 'No Cancelled Orders';
      default:
        return 'No Orders';
    }
  }

  String _emptySubtitle(String status) {
    switch (status) {
      case 'to_pay':
        return "You don't have any pending orders right now.";
      case 'to_ship':
        return 'Your orders will appear here once sellers start preparing them.';
      case 'to_receive':
        return "You don't have any orders out for delivery yet.";
      case 'completed':
        return 'Your completed orders will appear here once delivery is confirmed.';
      case 'cancelled':
        return 'Cancelled orders will appear here for your reference.';
      default:
        return "There's nothing here yet.";
    }
  }

  Widget _buildReturnsList(BuyerProvider buyerProvider) {
    // Get orders with return requests (approved or refunded status)
    final returnOrders = buyerProvider.allOrders.where((order) {
      final status = order.status.toString().toLowerCase();
      return status.contains('return') ||
          status.contains('refund') ||
          status == 'returned' ||
          status == 'refunded';
    }).toList();

    // Sort by order date descending (latest first)
    returnOrders.sort((a, b) => b.orderDate.compareTo(a.orderDate));

    if (returnOrders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(LucideIcons.undo2, size: 80, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text(
              'No returns or refunds',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text(
              'Return and refund requests will appear here',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadOrders,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: returnOrders.length,
        itemBuilder: (context, index) {
          final order = returnOrders[index];
          return _buildOrderCard(context, order, buyerProvider, 'returns');
        },
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
      case 'to_pay':
        return Colors.orange;
      case 'to_ship':
      case 'processing':
      case 'ready_for_pickup':
        return Colors.blue;
      case 'in_transit':
      case 'to_receive':
      case 'out_for_delivery':
        return Colors.purple;
      case 'delivered':
        return Colors.green;
      case 'completed':
        return const Color(0xFF059669);
      case 'cancelled':
        return Colors.red;
      case 'returned':
      case 'refunded':
      case 'return_approved':
      case 'refund_approved':
        return const Color(0xFF991B1B);
      case 'rejected':
        return Colors.red;
      default:
        if (status.contains('return') || status.contains('refund')) {
          return const Color(0xFF991B1B);
        }
        return Colors.blue;
    }
  }
}

class OrderStatusLabel {
  final String raw;
  OrderStatusLabel(this.raw);

  String get label {
    switch (raw.toLowerCase()) {
      case 'pending':
        return 'Pending';
      case 'to_pay':
        return 'To Pay';
      case 'to_ship':
        return 'To Ship';
      case 'in_transit':
        return 'In Transit';
      case 'to_receive':
        return 'To Receive';
      case 'delivered':
        return 'Delivered';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'returned':
        return 'Returned';
      case 'refunded':
      case 'refund_approved':
      case 'refund_processing':
        return 'Refunded';
      case 'return_approved':
      case 'return_requested':
        return raw.toLowerCase() == 'return_requested'
            ? 'Return & Refund Requested'
            : 'Return Approved';
      case 'rejected':
        return 'Rejected';
      default:
        if (raw.toLowerCase().contains('refund')) {
          return 'Refunded';
        }
        if (raw.toLowerCase().contains('return')) {
          return 'Returned';
        }
        return raw.replaceAll('_', ' ');
    }
  }
}
