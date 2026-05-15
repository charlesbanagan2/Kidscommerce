import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../services/delivery_fee_service.dart';
import '../../models/order.dart';
import '../../widgets/skeleton_loader.dart';

class RiderAvailableOrdersScreen extends StatefulWidget {
  const RiderAvailableOrdersScreen({super.key});

  @override
  State<RiderAvailableOrdersScreen> createState() =>
      _RiderAvailableOrdersScreenState();
}

class _RiderAvailableOrdersScreenState
    extends State<RiderAvailableOrdersScreen> {
  List<Order> _availableOrders = [];
  bool _isLoading = true;
  String? _error;
  final Set<int> _acceptingIds = {};

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);
  static const Color _amber = Color(0xFFD97706);
  static const Color _greenBg = Color(0xFFECFDF5);
  static const Color _amberBg = Color(0xFFFFFBEB);

  @override
  void initState() {
    super.initState();
    _fetchAvailableOrders();
  }

  Future<void> _fetchAvailableOrders() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      debugPrint('🔍 Fetching available orders...');
      final data = await ApiService.getRiderAvailableOrders();
      debugPrint('✅ Received ${data.length} available orders');

      final orders = data.map((json) => Order.fromJson(json)).toList();
      
      // Sort by order ID descending (latest orders first)
      orders.sort((a, b) => b.id.compareTo(a.id));

      if (mounted) {
        setState(() {
          _availableOrders = orders;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('❌ Error fetching available orders: $e');
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _acceptOrder(int orderId) async {
    if (!mounted) return;
    setState(() => _acceptingIds.add(orderId));
    try {
      await ApiService.acceptRiderOrder(orderId);
      if (!mounted) return;
      _showSnack('Order accepted! Check My Deliveries.', _green);
      _fetchAvailableOrders();
    } catch (e) {
      if (mounted) _showSnack('Error: $e', Colors.red.shade600);
    } finally {
      if (mounted) setState(() => _acceptingIds.remove(orderId));
    }
  }

  void _showSnack(String msg, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              color == _green
                  ? Icons.check_circle_rounded
                  : Icons.error_rounded,
              color: Colors.white,
              size: 18,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(msg,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600, fontSize: 13)),
            ),
          ],
        ),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: RefreshIndicator(
        color: _primary,
        strokeWidth: 2.5,
        onRefresh: _fetchAvailableOrders,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            _buildAppBar(),
            if (_isLoading)
              SliverFillRemaining(child: _buildSkeletonLoader())
            else if (_error != null)
              SliverFillRemaining(child: _buildErrorState())
            else if (_availableOrders.isEmpty)
              SliverFillRemaining(child: _buildEmptyState())
            else ...[
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: Row(
                    children: [
                      Text(
                        '${_availableOrders.length} order${_availableOrders.length == 1 ? '' : 's'} near you',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: _textSub,
                        ),
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: _greenBg,
                          borderRadius: BorderRadius.circular(20),
                          border:
                              Border.all(color: _green.withValues(alpha: 0.2)),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: _green,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                      color: _green.withValues(alpha: 0.4),
                                      blurRadius: 4)
                                ],
                              ),
                            ),
                            const SizedBox(width: 5),
                            const Text(
                              'Live',
                              style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700,
                                  color: _green),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, i) => Padding(
                      padding: const EdgeInsets.only(bottom: 14),
                      child: TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0, end: 1),
                        duration: Duration(milliseconds: 300 + i * 70),
                        curve: Curves.easeOutCubic,
                        builder: (context, v, child) => Opacity(
                          opacity: v,
                          child: Transform.translate(
                            offset: Offset(0, 24 * (1 - v)),
                            child: child,
                          ),
                        ),
                        child: _buildOrderCard(_availableOrders[i]),
                      ),
                    ),
                    childCount: _availableOrders.length,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      floating: true,
      snap: true,
      backgroundColor: _surface,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      shadowColor: Colors.black.withValues(alpha: 0.08),
      surfaceTintColor: Colors.transparent,
      toolbarHeight: 64,
      title: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: _primary.withValues(alpha: 0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: const Icon(Icons.storefront_rounded,
                color: Colors.white, size: 19),
          ),
          const SizedBox(width: 12),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Available Orders',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4,
                ),
              ),
              Text(
                'Tap to accept a delivery',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 14),
          child: GestureDetector(
            onTap: _fetchAvailableOrders,
            child: Container(
              padding: const EdgeInsets.all(9),
              decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _border),
              ),
              child: const Icon(Icons.refresh_rounded,
                  size: 19, color: Color(0xFF475569)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderCard(Order order) {
    final isAccepting = _acceptingIds.contains(order.id);

    // Use delivery fee from backend if available, otherwise calculate from address
    final deliveryFee = order.deliveryFee ??
        DeliveryFeeService.calculateDeliveryFeeFromAddress(
            order.shippingAddress);

    // Debug: Log address parsing (only if we had to calculate it)
    if (order.deliveryFee == null) {
      debugPrint('📍 Order #${order.id}: Address: "${order.shippingAddress}"');
      final debugInfo =
          DeliveryFeeService.debugAddressParsing(order.shippingAddress);
      debugPrint(
          '   Extracted: ${debugInfo['extractedProvince']} → Fee: ₱${debugInfo['calculatedFee']}');
    } else {
      debugPrint(
          '✅ Order #${order.id}: Using backend delivery fee ₱${order.deliveryFee}');
    }

    return Container(
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.02),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _primary.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: const Icon(Icons.receipt_long_rounded,
                          color: _primary, size: 18),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Order #${order.id}',
                            style: const TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 15,
                              color: _textPrimary,
                              letterSpacing: -0.3,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            order.buyerName ?? 'Unknown buyer',
                            style: const TextStyle(
                                fontSize: 12,
                                color: _textSub,
                                fontWeight: FontWeight.w500),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Rider Earnings Badge
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: _greenBg,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: _green.withValues(alpha: 0.3),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.payments_rounded,
                                  size: 11, color: _green),
                              SizedBox(width: 4),
                              Text(
                                'Delivery Fee',
                                style: TextStyle(
                                    fontSize: 9,
                                    color: _green,
                                    fontWeight: FontWeight.w600,
                                    letterSpacing: 0.3),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '₱${deliveryFee.toStringAsFixed(0)}',
                            style: const TextStyle(
                                fontSize: 16,
                                color: _green,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.5),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 14),
                const Divider(height: 1, color: Color(0xFFF1F3F8)),
                const SizedBox(height: 14),

                // Address chain
                if (order.sellerAddress != null &&
                    order.sellerAddress!.isNotEmpty) ...[
                  _buildAddressRow(
                    icon: Icons.store_rounded,
                    label: 'PICKUP',
                    address: order.sellerAddress!,
                    color: _amber,
                    bgColor: _amberBg,
                  ),
                  Padding(
                    padding: const EdgeInsets.only(left: 13, top: 2, bottom: 2),
                    child: Row(
                      children: List.generate(
                        4,
                        (i) => Padding(
                          padding: const EdgeInsets.only(bottom: 3),
                          child: Container(
                            width: 1.5,
                            height: 4,
                            color: i % 2 == 0
                                ? _textSub.withValues(alpha: 0.3)
                                : Colors.transparent,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],

                _buildAddressRow(
                  icon: Icons.location_on_rounded,
                  label: 'DROP-OFF',
                  address: order.shippingAddress,
                  color: _green,
                  bgColor: _greenBg,
                ),

                // Notes chip
                if (order.notes != null && order.notes!.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(11),
                    decoration: BoxDecoration(
                      color: _amberBg,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: _amber.withValues(alpha: 0.25)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.sticky_note_2_rounded,
                            size: 14, color: _amber),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            order.notes!,
                            style: TextStyle(
                              fontSize: 12,
                              color: _amber.withValues(alpha: 0.85),
                              fontWeight: FontWeight.w500,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Footer CTA
          Container(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
            decoration: const BoxDecoration(
              color: Color(0xFFF8F9FC),
              borderRadius: BorderRadius.only(
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
              border: Border(top: BorderSide(color: _border)),
            ),
            child: SizedBox(
              width: double.infinity,
              height: 46,
              child: ElevatedButton(
                onPressed: isAccepting ? null : () => _acceptOrder(order.id),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: _primary.withValues(alpha: 0.5),
                  elevation: 0,
                  shadowColor: Colors.transparent,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(13)),
                ),
                child: isAccepting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.2,
                        ),
                      )
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_task_rounded, size: 17),
                          SizedBox(width: 8),
                          Text(
                            'Accept This Order',
                            style: TextStyle(
                              fontWeight: FontWeight.w700,
                              fontSize: 14,
                              letterSpacing: 0.1,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddressRow({
    required IconData icon,
    required String label,
    required String address,
    required Color color,
    required Color bgColor,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(icon, size: 14, color: color),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 9,
                  color: color,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                address,
                style: const TextStyle(
                  fontSize: 12.5,
                  color: _textPrimary,
                  fontWeight: FontWeight.w500,
                  height: 1.35,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSkeletonLoader() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView.builder(
        itemCount: 3,
        itemBuilder: (context, index) => Container(
          margin: const EdgeInsets.only(bottom: 14),
          decoration: BoxDecoration(
            color: _surface,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: _border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top section
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header row
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SkeletonLoader(
                          width: 40,
                          height: 40,
                          borderRadius: BorderRadius.circular(13),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SkeletonLoader(
                                height: 15,
                                width: 100,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              const SizedBox(height: 6),
                              SkeletonLoader(
                                height: 12,
                                width: 80,
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        SkeletonLoader(
                          width: 70,
                          height: 50,
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Divider(height: 1, color: Color(0xFFF1F3F8)),
                    const SizedBox(height: 14),
                    // Address rows
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SkeletonLoader(
                          width: 28,
                          height: 28,
                          borderRadius: BorderRadius.circular(9),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SkeletonLoader(
                                height: 9,
                                width: 60,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              const SizedBox(height: 6),
                              SkeletonLoader(
                                height: 12,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              const SizedBox(height: 4),
                              SkeletonLoader(
                                height: 12,
                                width: 200,
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Footer
              Container(
                padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
                decoration: const BoxDecoration(
                  color: Color(0xFFF8F9FC),
                  borderRadius: BorderRadius.only(
                    bottomLeft: Radius.circular(20),
                    bottomRight: Radius.circular(20),
                  ),
                  border: Border(top: BorderSide(color: _border)),
                ),
                child: SkeletonLoader(
                  height: 46,
                  borderRadius: BorderRadius.circular(13),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: _surface,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: _border),
            ),
            child: const CircularProgressIndicator(
                color: _primary, strokeWidth: 3),
          ),
          const SizedBox(height: 16),
          const Text('Finding orders near you...',
              style: TextStyle(
                  color: _textSub, fontSize: 13, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                color: _surface,
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _border),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Icon(Icons.storefront_rounded,
                  size: 44, color: Color(0xFFCBD5E1)),
            ),
            const SizedBox(height: 24),
            const Text(
              'No orders available',
              style: TextStyle(
                color: _textPrimary,
                fontSize: 17,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.3,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Pull down to refresh and\ncheck for new orders nearby.',
              textAlign: TextAlign.center,
              style: TextStyle(color: _textSub, fontSize: 13, height: 1.6),
            ),
            const SizedBox(height: 28),
            SizedBox(
              height: 46,
              child: OutlinedButton.icon(
                onPressed: _fetchAvailableOrders,
                icon: const Icon(Icons.refresh_rounded, size: 17),
                label: const Text('Refresh',
                    style: TextStyle(fontWeight: FontWeight.w700)),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _primary,
                  side: const BorderSide(color: _primary, width: 1.5),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(13)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.red.shade100),
              ),
              child: Icon(Icons.wifi_off_rounded,
                  size: 44, color: Colors.red.shade400),
            ),
            const SizedBox(height: 24),
            const Text('Connection error',
                style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: _textPrimary,
                    letterSpacing: -0.3)),
            const SizedBox(height: 8),
            Text(
              _error!,
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style:
                  const TextStyle(color: _textSub, fontSize: 13, height: 1.5),
            ),
            const SizedBox(height: 28),
            SizedBox(
              height: 46,
              child: ElevatedButton.icon(
                onPressed: _fetchAvailableOrders,
                icon: const Icon(Icons.refresh_rounded, size: 17),
                label: const Text('Try Again',
                    style: TextStyle(fontWeight: FontWeight.w700)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(13)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
