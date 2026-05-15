import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../providers/buyer_provider.dart';
import '../../config/url_config.dart';
import '../../services/delivery_fee_service.dart';
import '../../widgets/skeleton_loader.dart';
import 'chat_screen.dart';
import 'buyer_home_screen.dart';
import 'rating_screen.dart';
import 'return_refund_screen.dart';

/// Order Detail Screen
class OrderDetailScreen extends StatefulWidget {
  final int orderId;
  final String? sourceTab; // Add this to know which tab the user came from

  const OrderDetailScreen({
    super.key,
    required this.orderId,
    this.sourceTab,
  });

  @override
  State<OrderDetailScreen> createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BuyerProvider>().selectOrder(widget.orderId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();
    final order = buyerProvider.selectedOrder;

    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      body: Column(
        children: [
          _buildHeader(),
          Expanded(
            child: buyerProvider.isLoading
                ? const OrderDetailSkeleton()
                : order == null
                    ? _buildNotFound()
                    : SingleChildScrollView(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _buildStatusCard(order),
                            const SizedBox(height: 16),
                            _buildOrderItems(order),
                            const SizedBox(height: 16),
                            _buildShippingInfo(order),
                            if (_shouldShowRiderInfo(order)) ...[
                              const SizedBox(height: 16),
                              _buildRiderInfo(order),
                            ],
                            if (_shouldShowDeliveryProof(order)) ...[
                              const SizedBox(height: 16),
                              _buildDeliveryProof(order),
                            ],
                            const SizedBox(height: 16),
                            _buildOrderSummary(order),
                            const SizedBox(height: 16),
                            _buildActionButtons(context, buyerProvider, order),
                          ],
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  bool _shouldShowDeliveryProof(dynamic order) {
    final status = order.status.toString().toLowerCase();
    return (status == 'to_receive' ||
            status == 'out_for_delivery' ||
            status == 'in_transit' ||
            status == 'ready_for_pickup' ||
            status == 'delivered' ||
            status == 'completed') &&
        order.proofPhotoUrl != null &&
        order.proofPhotoUrl!.isNotEmpty;
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
        16,
        MediaQuery.of(context).padding.top + 10,
        16,
        18,
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(LucideIcons.arrowLeft,
                  color: Colors.white, size: 20),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Order #${widget.orderId}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 19,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  'View your order details',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 12,
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

  Widget _buildNotFound() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              shape: BoxShape.circle,
            ),
            child: Icon(LucideIcons.packageX,
                size: 56, color: Colors.grey.shade400),
          ),
          const SizedBox(height: 20),
          const Text(
            'Order not found',
            style: TextStyle(
                fontSize: 17,
                color: Color(0xFF1F2937),
                fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'This order may have been removed\nor doesn\'t exist.',
            style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // ── Status Card ──────────────────────────────────────────────────────────────

  Widget _buildStatusCard(dynamic order) {
    final statusColor = _getStatusColor(order.status);
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(11),
                ),
                child: const Icon(LucideIcons.clipboardList,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Spacer(),
              Flexible(
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                  decoration: BoxDecoration(
                    color: statusColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(_getStatusIconData(order.status),
                          size: 13, color: Colors.white),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          order.statusDisplay,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          _buildStatusTimeline(order),
          const SizedBox(height: 18),
          const Divider(height: 1, color: Color(0xFFEEF0F5)),
          const SizedBox(height: 14),
          _buildInfoRow(
            LucideIcons.calendar,
            'Order placed on ${order.orderDate.toString().split(' ')[0]}',
            Colors.grey.shade600,
          ),
          if (order.expectedDelivery != null) ...[
            const SizedBox(height: 8),
            _buildInfoRow(
              LucideIcons.truck,
              'Expected delivery: ${order.expectedDelivery.toString().split(' ')[0]}',
              Colors.grey.shade600,
            ),
          ],
          if (order.trackingNumber != null) ...[
            const SizedBox(height: 8),
            _buildInfoRow(
              LucideIcons.scanLine,
              'Tracking: ${order.trackingNumber}',
              const Color(0xFF1e4db7),
              fontWeight: FontWeight.w600,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatusTimeline(dynamic order) {
    final steps = [
      ('to_pay', LucideIcons.clock, 'Pending'),
      ('to_ship', LucideIcons.package, 'Processing'),
      ('out_for_delivery', LucideIcons.truck, 'Out for Delivery'),
      ('delivered', LucideIcons.checkCircle2, 'Delivered'),
    ];

    final statusOrder = ['to_pay', 'to_ship', 'out_for_delivery', 'delivered'];

    String normalizedStatus = order.status;
    if (order.status == 'to_receive') normalizedStatus = 'out_for_delivery';
    if (order.status == 'completed') normalizedStatus = 'delivered';

    final currentIndex = statusOrder.indexOf(normalizedStatus);

    if (order.status == 'cancelled') {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.red.withValues(alpha: 0.07),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.red.withValues(alpha: 0.2)),
        ),
        child: const Row(
          children: [
            Icon(LucideIcons.xCircle, color: Colors.red, size: 18),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                'This order has been cancelled.',
                style: TextStyle(
                    color: Colors.red,
                    fontSize: 13,
                    fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      );
    }

    return Row(
      children: steps.asMap().entries.map((entry) {
        final idx = entry.key;
        final step = entry.value;
        final isCompleted = idx < currentIndex;
        final isActive = idx == currentIndex;
        final isLast = idx == steps.length - 1;

        final dotColor = isCompleted
            ? const Color(0xFF10B981)
            : isActive
                ? _getStatusColor(normalizedStatus)
                : Colors.grey.shade200;

        final labelColor = isActive
            ? _getStatusColor(normalizedStatus)
            : isCompleted
                ? const Color(0xFF10B981)
                : Colors.grey.shade400;

        return Expanded(
          child: Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Container(
                      width: 38,
                      height: 38,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: dotColor,
                        boxShadow: isActive
                            ? [
                                BoxShadow(
                                  color: dotColor.withValues(alpha: 0.4),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                )
                              ]
                            : [],
                      ),
                      child: Icon(
                        isCompleted ? LucideIcons.check : step.$2,
                        size: 16,
                        color: isCompleted || isActive
                            ? Colors.white
                            : Colors.grey.shade400,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      step.$3,
                      style: TextStyle(
                        fontSize: 8.5,
                        fontWeight:
                            isActive ? FontWeight.bold : FontWeight.normal,
                        color: labelColor,
                        height: 1.2,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    height: 2.5,
                    margin: const EdgeInsets.only(bottom: 22),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(2),
                      color: idx < currentIndex
                          ? const Color(0xFF10B981)
                          : Colors.grey.shade200,
                    ),
                  ),
                ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInfoRow(IconData icon, String text, Color textColor,
      {FontWeight fontWeight = FontWeight.normal}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: textColor, size: 14),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: TextStyle(
                color: textColor, fontSize: 12, fontWeight: fontWeight),
          ),
        ),
      ],
    );
  }

  // ── Order Items ──────────────────────────────────────────────────────────────

  Widget _buildOrderItems(dynamic order) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(11),
                ),
                child: const Icon(LucideIcons.shoppingBag,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Text(
                'Order Items',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${order.items.length} item${order.items.length > 1 ? 's' : ''}',
                  style: const TextStyle(
                      color: Color(0xFF1e4db7),
                      fontSize: 11,
                      fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: order.items.length,
            separatorBuilder: (_, __) =>
                Divider(height: 20, color: Colors.grey.shade100),
            itemBuilder: (context, index) {
              final item = order.items[index];
              String? productImage;

              if (item is Map) {
                productImage = item['product_image'] ??
                    item['productImage'] ??
                    item['image_url'] ??
                    item['image'];
              } else {
                try {
                  productImage = item.productImage;
                } catch (_) {
                  productImage = null;
                }
              }

              final imageUrl = productImage != null && productImage.isNotEmpty
                  ? UrlConfig.toAbsoluteImageUrl(productImage)
                  : null;

              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      width: 68,
                      height: 68,
                      color: Colors.grey.shade100,
                      child: imageUrl != null
                          ? Image.network(
                              imageUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => Icon(
                                  Icons.image_not_supported,
                                  color: Colors.grey.shade400),
                            )
                          : Icon(Icons.image, color: Colors.grey.shade400),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.productName,
                          style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 13,
                              color: Color(0xFF1F2937)),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 5),
                        Row(
                          children: [
                            _itemTag('x${item.quantity}', Colors.grey.shade600),
                            if (item.size != null &&
                                item.size.toString().isNotEmpty) ...[
                              const SizedBox(width: 6),
                              _itemTag(item.size.toString(),
                                  const Color(0xFF1e4db7)),
                            ],
                            if (item.color != null &&
                                item.color.toString().isNotEmpty) ...[
                              const SizedBox(width: 6),
                              _itemTag(
                                  item.color.toString(), Colors.grey.shade700),
                            ],
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _itemTag(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style:
            TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w500),
      ),
    );
  }

  // ── Shipping Info ────────────────────────────────────────────────────────────

  Widget _buildShippingInfo(dynamic order) {
    return _infoCard(
      icon: LucideIcons.mapPin,
      title: 'Delivery Address',
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFF),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE8EDF5)),
        ),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(LucideIcons.user,
                      size: 14, color: Color(0xFF1e4db7)),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        order.recipientName,
                        style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                            color: Color(0xFF1F2937)),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        order.recipientPhone,
                        style: TextStyle(
                            color: Colors.grey.shade500, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Divider(height: 1, color: Colors.grey.shade200),
            const SizedBox(height: 10),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(LucideIcons.home,
                      size: 14, color: Colors.orange.shade700),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    order.shippingAddress,
                    style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  bool _shouldShowRiderInfo(dynamic order) {
    final status = order.status.toString().toLowerCase();

    // Check if rider is assigned with proper validation
    final hasRiderId = order.riderId != null && order.riderId > 0;
    final riderNameStr = order.riderName?.toString().trim() ?? '';
    final hasRiderName = riderNameStr.isNotEmpty &&
        riderNameStr.toLowerCase() != 'null' &&
        riderNameStr.toLowerCase() != 'n/a';

    final hasRider = hasRiderId && hasRiderName;

    debugPrint(
        '🔍🔍🔍 DETAILED RIDER INFO CHECK FOR ORDER #${widget.orderId}:');
    debugPrint('   Status: "$status"');
    debugPrint(
        '   RiderId: ${order.riderId} (type: ${order.riderId.runtimeType})');
    debugPrint('   HasRiderId: $hasRiderId');
    debugPrint(
        '   RiderName: "${order.riderName}" (type: ${order.riderName.runtimeType})');
    debugPrint('   RiderNameStr: "$riderNameStr"');
    debugPrint('   HasRiderName: $hasRiderName');
    debugPrint('   RiderPhone: "${order.riderPhone}"');
    debugPrint('   RiderProfilePicture: "${order.riderProfilePicture}"');
    debugPrint('   HasRider: $hasRider');

    // Show rider info for these statuses when rider is assigned
    // Covers: processing/ready_for_pickup (rider assigned early), to_ship (picked up),
    // in_transit/out_for_delivery (in delivery), delivered/completed (finished)
    final shouldShow = hasRider &&
        (status == 'processing' ||
            status == 'ready_for_pickup' ||
            status == 'to_ship' ||
            status == 'out_for_delivery' ||
            status == 'in_transit' ||
            status == 'to_receive' ||
            status == 'delivered' ||
            status == 'completed');

    debugPrint('   ✅ ShouldShow: $shouldShow');
    if (!shouldShow) {
      debugPrint('   ❌ Rider card NOT showing because:');
      if (!hasRider) {
        debugPrint('      - No valid rider data (hasRider=$hasRider)');
        if (!hasRiderId)
          debugPrint('      - Missing or invalid riderId: ${order.riderId}');
        if (!hasRiderName)
          debugPrint(
              '      - Missing or invalid riderName: "${order.riderName}"');
      }
      if (hasRider && !shouldShow) {
        debugPrint('      - Status "$status" not in qualifying list');
      }
    }

    return shouldShow;
  }

  // ── Rider Info ───────────────────────────────────────────────────────────────

  Widget _buildRiderInfo(dynamic order) {
    final riderNameStr = order.riderName?.toString().trim() ?? 'Rider';
    final riderPhoneStr = order.riderPhone?.toString().trim() ?? '';
    final hasPhone = riderPhoneStr.isNotEmpty &&
        riderPhoneStr.toLowerCase() != 'null' &&
        riderPhoneStr.toLowerCase() != 'n/a';

    return _infoCard(
      icon: LucideIcons.bike,
      title: 'Assigned Rider',
      trailing: GestureDetector(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ChatScreen(
                otherUserId: order.riderId,
                otherUserName: riderNameStr,
                otherUserRole: 'rider',
                otherUserProfilePicture: order.riderProfilePicture,
              ),
            ),
          );
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: const Color(0xFF1e4db7),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(LucideIcons.messageCircle, color: Colors.white, size: 14),
              SizedBox(width: 6),
              Text(
                'Chat',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFF),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE8EDF5)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(LucideIcons.user,
                      size: 14, color: Color(0xFF1e4db7)),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    riderNameStr,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: Color(0xFF1F2937)),
                  ),
                ),
              ],
            ),
            if (hasPhone) ...[
              const SizedBox(height: 12),
              Divider(height: 1, color: Colors.grey.shade200),
              const SizedBox(height: 12),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: Colors.green.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(LucideIcons.phone,
                        size: 14, color: Colors.green.shade600),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      riderPhoneStr,
                      style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: Colors.green.shade700),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  // ── Delivery Proof ───────────────────────────────────────────────────────────

  Widget _buildDeliveryProof(dynamic order) {
    final photoUrl = UrlConfig.toAbsoluteImageUrl(order.proofPhotoUrl!);

    return _infoCard(
      icon: LucideIcons.camera,
      iconBgColor: Colors.green.withValues(alpha: 0.1),
      iconColor: Colors.green,
      title: 'Delivery Proof',
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.green.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(LucideIcons.checkCircle2, color: Colors.green, size: 11),
            SizedBox(width: 4),
            Text(
              'Verified',
              style: TextStyle(
                  fontSize: 10,
                  color: Colors.green,
                  fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
      child: GestureDetector(
        onTap: () => _showDeliveryProofModal(photoUrl),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: AspectRatio(
            aspectRatio: 16 / 9,
            child: Stack(
              children: [
                Image.network(
                  photoUrl,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  loadingBuilder: (context, child, progress) {
                    if (progress == null) return child;
                    return Container(
                      color: Colors.grey.shade100,
                      child: const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    );
                  },
                  errorBuilder: (context, error, _) => Container(
                    color: Colors.grey.shade100,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(LucideIcons.imageOff,
                            size: 36, color: Colors.grey.shade400),
                        const SizedBox(height: 8),
                        Text('Unable to load photo',
                            style: TextStyle(
                                fontSize: 12, color: Colors.grey.shade500)),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  bottom: 10,
                  right: 10,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(LucideIcons.expand, color: Colors.white, size: 12),
                        SizedBox(width: 4),
                        Text(
                          'Tap to view',
                          style: TextStyle(color: Colors.white, fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showDeliveryProofModal(String imageUrl) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(16),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFF10b981), Color(0xFF059669)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                padding: const EdgeInsets.fromLTRB(18, 14, 14, 14),
                child: Row(
                  children: [
                    const Icon(LucideIcons.camera,
                        color: Colors.white, size: 18),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        'Delivery Proof',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(LucideIcons.x,
                            color: Colors.white, size: 18),
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                color: Colors.white,
                child: Flexible(
                  child: SingleChildScrollView(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.network(
                          imageUrl,
                          fit: BoxFit.contain,
                          loadingBuilder: (context, child, progress) {
                            if (progress == null) return child;
                            return SizedBox(
                              height: 260,
                              child: Center(
                                child: CircularProgressIndicator(
                                  value: progress.expectedTotalBytes != null
                                      ? progress.cumulativeBytesLoaded /
                                          progress.expectedTotalBytes!
                                      : null,
                                  color: Colors.green,
                                ),
                              ),
                            );
                          },
                          errorBuilder: (context, _, __) => Container(
                            height: 260,
                            color: Colors.grey.shade100,
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(LucideIcons.imageOff,
                                    size: 48, color: Colors.grey.shade400),
                                const SizedBox(height: 10),
                                Text(
                                  'Failed to load image',
                                  style: TextStyle(
                                      color: Colors.grey.shade600,
                                      fontSize: 13),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              Container(
                color: Colors.white,
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10b981),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 0,
                    ),
                    child: const Text(
                      'Close',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Order Summary ────────────────────────────────────────────────────────────

  Widget _buildOrderSummary(dynamic order) {
    final rawDeliveryFee = order.deliveryFee ?? order.shippingFee;
    final fallbackDeliveryFee =
        DeliveryFeeService.calculateDeliveryFeeFromAddress(
            order.shippingAddress);
    final deliveryFee = (rawDeliveryFee == null || rawDeliveryFee == 0)
        ? fallbackDeliveryFee
        : rawDeliveryFee;
    final cappedDiscount =
        order.discount > order.subtotal ? order.subtotal : order.discount;
    final subtotalAfterDiscount = order.subtotal - cappedDiscount;
    final total = subtotalAfterDiscount + deliveryFee;

    return _infoCard(
      icon: LucideIcons.receipt,
      title: 'Order Summary',
      child: Column(
        children: [
          _buildSummaryRow('Subtotal', '₱${order.subtotal.toStringAsFixed(2)}',
              strikethrough: cappedDiscount > 0),
          const SizedBox(height: 10),
          _buildSummaryRow(
              'Delivery fee', '₱${deliveryFee.toStringAsFixed(2)}'),
          if (order.discount > 0) ...[
            const SizedBox(height: 10),
            _buildSummaryRow(
              'Discount',
              '-₱${cappedDiscount.toStringAsFixed(2)}',
              valueColor: Colors.green,
            ),
          ],
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Total Amount',
                  style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14),
                ),
                Text(
                  '₱${total.toStringAsFixed(2)}',
                  style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 20),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFF),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE8EDF5)),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(LucideIcons.wallet,
                      size: 14, color: Color(0xFF1e4db7)),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    order.paymentMethod.toString().toUpperCase(),
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: Color(0xFF1F2937)),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: _getStatusColor(_getEffectivePaymentStatus(order))
                        .withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _getEffectivePaymentStatus(order).toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(_getEffectivePaymentStatus(order)),
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _getEffectivePaymentStatus(dynamic order) {
    if (order.paymentMethod.toString().toLowerCase() == 'cod' &&
        (order.status == 'completed' || order.status == 'delivered')) {
      return 'completed';
    }
    return order.paymentStatus;
  }

  Widget _buildSummaryRow(String label, String value,
      {Color? valueColor, bool strikethrough = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
        const SizedBox(width: 16),
        Flexible(
          child: Text(
            value,
            style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: valueColor ??
                    (strikethrough
                        ? Colors.grey.shade500
                        : const Color(0xFF1F2937)),
                decoration: strikethrough ? TextDecoration.lineThrough : null),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  // ── Action Buttons ───────────────────────────────────────────────────────────

  Widget _buildActionButtons(
    BuildContext context,
    BuyerProvider buyerProvider,
    dynamic order,
  ) {
    final status = order.status.toString().toLowerCase();
    final hasRating = order.hasRating == true || order.rating != null;

    // PENDING STATUS: Show Cancel Order only
    if (status == 'pending' || status == 'to_pay') {
      return Column(
        children: [
          _actionButton(
            label: 'Cancel Order',
            icon: LucideIcons.xCircle,
            style: _ButtonStyle.outline,
            color: Colors.red,
            onPressed: () =>
                _showCancelDialog(context, buyerProvider, order.id),
          ),
        ],
      );
    }

    // PROCESSING STATUS: No buttons
    if (status == 'to_ship' ||
        status == 'processing' ||
        status == 'ready_for_pickup') {
      return const SizedBox.shrink();
    }

    // OUT FOR DELIVERY STATUS: No buttons
    if (status == 'out_for_delivery' ||
        status == 'in_transit' ||
        status == 'to_receive') {
      return const SizedBox.shrink();
    }

    // DELIVERED STATUS: Show Order Received and Return & Refund
    if (status == 'delivered') {
      return Column(
        children: [
          _actionButton(
            label: 'Order Received',
            icon: LucideIcons.packageCheck,
            style: _ButtonStyle.filled,
            color: Colors.green,
            onPressed: () async {
              final success = await buyerProvider.confirmDelivery(order.id);
              if (mounted) {
                if (success) {
                  _showConfirmSuccessDialog(context);
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(buyerProvider.errorMessage ??
                          'Failed to confirm delivery'),
                    ),
                  );
                }
              }
            },
          ),
          _actionButton(
            label: 'Return & Refund',
            icon: LucideIcons.rotateCw,
            style: _ButtonStyle.outline,
            color: Colors.orange,
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ReturnRefundScreen(order: order),
                ),
              );
            },
          ),
        ],
      );
    }

    // COMPLETED STATUS: Show Rate Now and Buy Again
    if (status == 'completed') {
      return Column(
        children: [
          if (!hasRating)
            _actionButton(
              label: 'Rate Now',
              icon: LucideIcons.star,
              style: _ButtonStyle.filled,
              color: const Color(0xFFF59E0B),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => RatingScreen(order: order),
                  ),
                );
              },
            ),
          _actionButton(
            label: 'Buy Again',
            icon: LucideIcons.shoppingCart,
            style: _ButtonStyle.outline,
            color: const Color(0xFF1e4db7),
            onPressed: () async {
              // Get first product from order items
              if (order.items.isNotEmpty) {
                final firstItem = order.items[0];
                final productId = firstItem.productId ?? firstItem.id;

                if (productId != null) {
                  // Navigate to product detail screen
                  // Note: You'll need to import your product detail screen
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Opening product #$productId...')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Product not available')),
                  );
                }
              }
            },
          ),
        ],
      );
    }

    return const SizedBox.shrink();
  }

  Widget _actionButton({
    required String label,
    required IconData icon,
    required _ButtonStyle style,
    required Color color,
    required VoidCallback onPressed,
  }) {
    final shape =
        RoundedRectangleBorder(borderRadius: BorderRadius.circular(14));
    const padding = EdgeInsets.symmetric(vertical: 14, horizontal: 20);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: SizedBox(
        width: double.infinity,
        child: style == _ButtonStyle.filled
            ? ElevatedButton.icon(
                onPressed: onPressed,
                icon: Icon(icon, size: 18),
                label: Text(label,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: color,
                  foregroundColor: Colors.white,
                  padding: padding,
                  shape: shape,
                  elevation: 0,
                ),
              )
            : OutlinedButton.icon(
                onPressed: onPressed,
                icon: Icon(icon, size: 18),
                label: Text(label,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 14)),
                style: OutlinedButton.styleFrom(
                  padding: padding,
                  side: BorderSide(color: color, width: 1.5),
                  foregroundColor: color,
                  shape: shape,
                ),
              ),
      ),
    );
  }

  // ── Dialogs ──────────────────────────────────────────────────────────────────

  void _showCancelDialog(
    BuildContext context,
    BuyerProvider buyerProvider,
    int orderId,
  ) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
        child: Padding(
          padding: const EdgeInsets.all(26),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(LucideIcons.xCircle,
                    color: Colors.red, size: 46),
              ),
              const SizedBox(height: 20),
              const Text(
                'Cancel Order?',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                'Are you sure you want to cancel this order?\nThis action cannot be undone.',
                style: TextStyle(
                    fontSize: 13, color: Colors.grey.shade600, height: 1.6),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 26),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(ctx),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        side: BorderSide(color: Colors.grey.shade300),
                        foregroundColor: Colors.grey.shade700,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('Keep Order',
                          style: TextStyle(
                              fontWeight: FontWeight.w600, fontSize: 13)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () async {
                        Navigator.pop(ctx);
                        final success =
                            await buyerProvider.cancelOrder(orderId);
                        if (mounted) {
                          if (success) {
                            _showCancelSuccessDialog(context);
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Row(
                                  children: [
                                    const Icon(LucideIcons.alertCircle,
                                        color: Colors.white, size: 18),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Text(
                                        buyerProvider.errorMessage ??
                                            'Failed to cancel order',
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w500),
                                      ),
                                    ),
                                  ],
                                ),
                                backgroundColor: Colors.red,
                                behavior: SnackBarBehavior.floating,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                margin: const EdgeInsets.all(16),
                              ),
                            );
                          }
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                        elevation: 0,
                      ),
                      child: const Text('Yes, Cancel',
                          style: TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showCancelSuccessDialog(BuildContext context) {
    _showSuccessDialog(
      context: context,
      title: 'Order Cancelled',
      message: 'Your order has been cancelled successfully.',
      onOk: () {
        // Close the dialog
        Navigator.pop(context);
        // Close the order detail screen
        Navigator.pop(context);
        // Navigate to home with cancelled filter
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => const BuyerHomeScreen(
              initialTab: 1,
              ordersInitialFilter: 'cancelled',
            ),
          ),
        );
      },
    );
  }

  void _showConfirmSuccessDialog(BuildContext context) {
    _showSuccessDialog(
      context: context,
      title: 'Order Received!',
      message: 'Your order has been moved to the Delivered tab.',
      onOk: () {
        // Close the dialog
        Navigator.pop(context);
        // Close the order detail screen
        Navigator.pop(context);
        // Navigate to home with delivered filter
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => const BuyerHomeScreen(
              initialTab: 1,
              ordersInitialFilter: 'completed',
            ),
          ),
        );
      },
    );
  }

  void _showSuccessDialog({
    required BuildContext context,
    required String title,
    required String message,
    required VoidCallback onOk,
  }) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
        child: Padding(
          padding: const EdgeInsets.all(26),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(LucideIcons.checkCircle2,
                    color: Colors.green, size: 46),
              ),
              const SizedBox(height: 20),
              Text(
                title,
                style:
                    const TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                message,
                style: TextStyle(
                    fontSize: 13, color: Colors.grey.shade600, height: 1.6),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 26),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    onOk();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 13),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                    elevation: 0,
                  ),
                  child: const Text('OK',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Shared card scaffold ─────────────────────────────────────────────────────

  Widget _infoCard({
    required IconData icon,
    required String title,
    required Widget child,
    Color? iconBgColor,
    Color? iconColor,
    Widget? trailing,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: iconBgColor ??
                      const Color(0xFF1e4db7).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(11),
                ),
                child: Icon(icon,
                    color: iconColor ?? const Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 15),
                ),
              ),
              if (trailing != null) trailing,
            ],
          ),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}

// ── Button style enum ──────────────────────────────────────────────────────────

enum _ButtonStyle { filled, outline }

// ── Top-level helpers ──────────────────────────────────────────────────────────

IconData _getStatusIconData(String status) {
  switch (status.toLowerCase()) {
    case 'pending':
    case 'to_pay':
      return LucideIcons.clock;
    case 'to_ship':
    case 'processing':
    case 'ready_for_pickup':
      return LucideIcons.package;
    case 'in_transit':
    case 'to_receive':
    case 'out_for_delivery':
      return LucideIcons.truck;
    case 'delivered':
      return LucideIcons.checkCircle2;
    case 'completed':
      return LucideIcons.checkCircle2;
    case 'cancelled':
      return LucideIcons.xCircle;
    default:
      return LucideIcons.helpCircle;
  }
}

Color _getStatusColor(String status) {
  switch (status.toLowerCase()) {
    case 'pending':
    case 'to_pay':
      return const Color(0xFFF59E0B);
    case 'to_ship':
    case 'processing':
    case 'ready_for_pickup':
      return const Color(0xFF3B82F6);
    case 'in_transit':
    case 'to_receive':
    case 'out_for_delivery':
      return const Color(0xFF8B5CF6);
    case 'delivered':
      return const Color(0xFF10B981);
    case 'completed':
      return const Color(0xFF059669);
    case 'cancelled':
      return const Color(0xFFEF4444);
    case 'returned':
    case 'refunded':
      return const Color(0xFF991B1B);
    default:
      return const Color(0xFF3B82F6);
  }
}
