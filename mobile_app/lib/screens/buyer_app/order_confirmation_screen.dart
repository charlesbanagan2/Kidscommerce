import 'package:flutter/material.dart';
import '../../models/order.dart';

class OrderConfirmationScreen extends StatelessWidget {
  final Order order;

  const OrderConfirmationScreen({super.key, required this.order});

  // ── Theme constants (same as CheckoutScreen) ──
  static const Color _primary = Color(0xFF1E4DB7);
  static const Color _primaryLight = Color(0xFFEEF3FF);
  static const Color _surface = Colors.white;
  static const Color _background = Color(0xFFF5F7FA);
  static const Color _textPrimary = Color(0xFF1A1D2E);
  static const Color _textSecondary = Color(0xFF6B7280);
  static const Color _border = Color(0xFFE5E7EB);
  static const Color _green = Color(0xFF16A34A);
  static const Color _greenLight = Color(0xFFF0FDF4);

  @override
  Widget build(BuildContext context) {
    final deliveryFee = order.deliveryFee ?? order.shippingFee;
    final cappedDiscount =
        order.discount > order.subtotal ? order.subtotal : order.discount;
    final subtotalAfterDiscount = order.subtotal - cappedDiscount;
    final total = order.totalAmount > 0
        ? order.totalAmount
        : (subtotalAfterDiscount + deliveryFee);

    return Scaffold(
      backgroundColor: _background,
      appBar: AppBar(
        title: const Text('Order Confirmation'),
        backgroundColor: _primary,
        elevation: 0,
        centerTitle: true,
        automaticallyImplyLeading: false,
        titleTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: Colors.white, size: 18),
          onPressed: () =>
              Navigator.of(context).popUntil((route) => route.isFirst),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 24, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Success Hero ──
            _buildCard(
              child: Column(
                children: [
                  Container(
                    width: 72,
                    height: 72,
                    decoration: const BoxDecoration(
                      color: _greenLight,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check_rounded,
                        color: _green, size: 40),
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Order Confirmed!',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: _textPrimary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Thank you for your purchase.\nYour order has been placed successfully.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      color: _textSecondary,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                    decoration: BoxDecoration(
                      color: _primaryLight,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Order #${order.id}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: _primary,
                      ),
                    ),
                  ),
                  ...[
                    const SizedBox(height: 8),
                    Text(
                      'Placed on ${_formatDate(order.orderDate)}',
                      style:
                          const TextStyle(fontSize: 12, color: _textSecondary),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 14),

            // ── Status Badges ──
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      if (order.trackingNumber != null &&
                          order.trackingNumber!.isNotEmpty)
                        _buildBadge(
                            Icons.qr_code_2_outlined, order.trackingNumber!),
                      _buildBadge(
                        Icons.access_time_rounded,
                        _formatStatus(order.status),
                        bgColor: _primaryLight,
                        textColor: _primary,
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Divider(height: 1, color: _border),
                  const SizedBox(height: 14),
                  _buildInfoRow(
                    Icons.location_on_outlined,
                    'Shipping Address',
                    order.shippingAddress,
                  ),
                  const SizedBox(height: 12),
                  _buildInfoRow(
                    Icons.payment_outlined,
                    'Payment Method',
                    _formatPaymentMethod(order.paymentMethod),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // ── Items Ordered ──
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionLabel('Items Ordered',
                      icon: Icons.inventory_2_outlined),
                  const SizedBox(height: 14),
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: order.items.length,
                    separatorBuilder: (_, __) =>
                        const Divider(height: 20, color: _border),
                    itemBuilder: (context, index) {
                      final item = order.items[index];
                      return Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item.productName,
                                  style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                    color: _textPrimary,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Qty: ${item.quantity}  ×  ₱${item.price.toStringAsFixed(2)}',
                                  style: const TextStyle(
                                      fontSize: 12, color: _textSecondary),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            '₱${(item.price * item.quantity).toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _primary,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.clip,
                          ),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // ── Order Summary ──
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionLabel('Order Summary',
                      icon: Icons.receipt_long_outlined),
                  const SizedBox(height: 14),
                  _buildPriceRow(
                    'Subtotal',
                    '₱${order.subtotal.toStringAsFixed(2)}',
                    strikethrough: cappedDiscount > 0,
                  ),
                  if (cappedDiscount > 0) ...[
                    const SizedBox(height: 10),
                    _buildPriceRow(
                      'Discount',
                      '-₱${cappedDiscount.toStringAsFixed(2)}',
                      valueColor: _green,
                    ),
                  ],
                  const SizedBox(height: 10),
                  _buildPriceRow(
                    'Delivery Fee',
                    '₱${deliveryFee.toStringAsFixed(2)}',
                    icon: Icons.local_shipping_outlined,
                  ),
                  const SizedBox(height: 16),
                  const Divider(height: 1, color: _border),
                  const SizedBox(height: 16),
                  // Total pill
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: _primaryLight,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Total Amount',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: _textPrimary,
                              ),
                            ),
                            Text(
                              'Including all fees',
                              style: TextStyle(
                                  fontSize: 11, color: _textSecondary),
                            ),
                          ],
                        ),
                        Text(
                          '₱${total.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            color: _primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // ── What's Next ──
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionLabel("What's Next?",
                      icon: Icons.info_outline_rounded),
                  const SizedBox(height: 14),
                  _buildNextStep(Icons.mark_email_read_outlined,
                      'Confirmation email sent'),
                  _buildNextStep(Icons.inventory_2_outlined,
                      'Processing: 1–2 business days'),
                  _buildNextStep(Icons.local_shipping_outlined,
                      'Delivery: 3–5 business days'),
                  if (order.paymentMethod.toLowerCase() == 'cod')
                    _buildNextStep(Icons.payments_outlined,
                        'Prepare exact payment on delivery'),
                  _buildNextStep(
                      Icons.support_agent_outlined, 'Call us for updates'),
                  _buildNextStep(
                      Icons.pin_drop_outlined, 'Track your order anytime'),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // ── Action Buttons ──
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => Navigator.of(context)
                        .popUntil((route) => route.isFirst),
                    icon: const Icon(Icons.shopping_bag_outlined, size: 17),
                    label: const Text(
                      'Continue Shopping',
                      style:
                          TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _primary,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => Navigator.of(context)
                        .popUntil((route) => route.isFirst),
                    icon: const Icon(Icons.receipt_long_outlined, size: 17),
                    label: const Text(
                      'My Orders',
                      style:
                          TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _primary,
                      side: const BorderSide(color: _primary, width: 1.5),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ── Reusable Widgets ──

  static Widget _buildCard({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );
  }

  static Widget _buildSectionLabel(String label, {IconData? icon}) {
    return Row(
      children: [
        if (icon != null) ...[
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: _primaryLight,
              borderRadius: BorderRadius.circular(7),
            ),
            child: Icon(icon, size: 15, color: _primary),
          ),
          const SizedBox(width: 8),
        ],
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: _textPrimary,
          ),
        ),
      ],
    );
  }

  static Widget _buildBadge(
    IconData icon,
    String label, {
    Color bgColor = const Color(0xFFEEF3FF),
    Color textColor = const Color(0xFF1E4DB7),
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: textColor),
          const SizedBox(width: 5),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: textColor,
            ),
          ),
        ],
      ),
    );
  }

  static Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 34,
          height: 34,
          decoration: BoxDecoration(
            color: _primaryLight,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(icon, size: 16, color: _primary),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 11,
                  color: _textSecondary,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: _textPrimary,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }

  static Widget _buildPriceRow(
    String label,
    String value, {
    Color? valueColor,
    IconData? icon,
    bool strikethrough = false,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            if (icon != null) ...[
              Icon(icon, size: 14, color: _textSecondary),
              const SizedBox(width: 6),
            ],
            Text(label,
                style: const TextStyle(fontSize: 13, color: _textSecondary)),
          ],
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color:
                strikethrough ? _textSecondary : (valueColor ?? _textPrimary),
            decoration: strikethrough ? TextDecoration.lineThrough : null,
          ),
        ),
      ],
    );
  }

  static Widget _buildNextStep(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: _primaryLight,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, size: 15, color: _primary),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 13,
                color: _textPrimary,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Formatters ──

  String _formatDate(DateTime? date) {
    if (date == null) return 'N/A';
    return '${date.day} ${_getMonthName(date.month)}, ${date.year}';
  }

  String _getMonthName(int month) {
    const months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December'
    ];
    return months[month - 1];
  }

  String _formatStatus(String? status) {
    if (status == null) return 'Pending';
    return status
        .split('_')
        .map((w) => w[0].toUpperCase() + w.substring(1))
        .join(' ');
  }

  String _formatPaymentMethod(String? method) {
    if (method == null) return 'N/A';
    switch (method.toLowerCase()) {
      case 'cod':
        return 'Cash on Delivery';
      case 'gcash':
        return 'GCash';
      case 'card':
        return 'Credit / Debit Card';
      default:
        return method.toUpperCase();
    }
  }
}
