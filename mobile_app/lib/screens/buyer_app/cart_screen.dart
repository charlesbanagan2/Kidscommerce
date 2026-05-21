import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import '../../providers/buyer_provider.dart';
import '../../widgets/skeleton_loader.dart';
import 'buyer_home_screen.dart';
import 'checkout_screen.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  final Set<int> _selectedItemIds = {};
  bool _selectAll = false;
  final Set<int> _updatingItemIds = {}; // Track items being updated

  // ── Theme constants ──
  static const Color _primary = Color(0xFF1E4DB7);
  static const Color _primaryLight = Color(0xFFEEF3FF);
  static const Color _surface = Colors.white;
  static const Color _background = Color(0xFFF5F7FA);
  static const Color _textPrimary = Color(0xFF1A1D2E);
  static const Color _textSecondary = Color(0xFF6B7280);
  static const Color _border = Color(0xFFE5E7EB);

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final provider = context.read<BuyerProvider>();
      await provider.fetchCart();
      await provider.fetchProducts();
    });
  }

  void _toggleSelectAll(bool value, BuyerProvider buyerProvider) {
    debugPrint('📦 Cart: Toggle select all = $value');
    setState(() {
      _selectAll = value;
      if (value) {
        _selectedItemIds.clear();
        _selectedItemIds.addAll(buyerProvider.cartItems.map((item) => item.id));
      } else {
        _selectedItemIds.clear();
      }
    });
    debugPrint('📦 Cart: Selected ${_selectedItemIds.length} items');
  }

  void _toggleItemSelection(int itemId) {
    debugPrint('📦 Cart: Toggle item $itemId');
    setState(() {
      if (_selectedItemIds.contains(itemId)) {
        _selectedItemIds.remove(itemId);
      } else {
        _selectedItemIds.add(itemId);
      }
      _selectAll = _selectedItemIds.length ==
          context.read<BuyerProvider>().cartItems.length;
    });
    debugPrint('📦 Cart: Selected ${_selectedItemIds.length} items');
  }

  double get _selectedTotal {
    final buyerProvider = context.read<BuyerProvider>();
    return buyerProvider.cartItems
        .where((item) => _selectedItemIds.contains(item.id))
        .fold(0.0, (sum, item) => sum + item.subtotal);
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: true,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) {
          Navigator.of(context).popUntil((route) => route.isFirst);
        }
      },
      child: _buildCartScaffold(context),
    );
  }

  Widget _buildCartScaffold(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();

    return Scaffold(
      backgroundColor: _background,
      appBar: AppBar(
        backgroundColor: _primary,
        elevation: 0,
        centerTitle: false,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: Colors.white, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'My Cart',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 17,
              ),
            ),
            Text(
              '${buyerProvider.cartItems.length} item${buyerProvider.cartItems.length == 1 ? '' : 's'}',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: 12,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: buyerProvider.isLoading && buyerProvider.cartItems.isEmpty
                ? const ListSkeletonLoader(
                    itemSkeleton: CartItemSkeleton(),
                    itemCount: 4,
                    padding: EdgeInsets.all(16),
                  )
                : buyerProvider.cartItems.isEmpty
                    ? _buildEmptyCart(context)
                    : _buildCartContent(context, buyerProvider),
          ),
          if (buyerProvider.cartItems.isNotEmpty)
            _buildCheckoutFooter(buyerProvider),
        ],
      ),
    );
  }

  // ── Cart Content ──

  Widget _buildCartContent(BuildContext context, BuyerProvider buyerProvider) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      children: [
        // Select All
        _buildCard(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: [
              Transform.scale(
                scale: 0.9,
                child: Checkbox(
                  value: _selectAll,
                  onChanged: (value) =>
                      _toggleSelectAll(value ?? false, buyerProvider),
                  activeColor: _primary,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(4)),
                  side: const BorderSide(color: _border, width: 1.5),
                ),
              ),
              const Text(
                'Select All Items',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: _textPrimary,
                ),
              ),
              const Spacer(),
              if (_selectedItemIds.isNotEmpty)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _primaryLight,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${_selectedItemIds.length} selected',
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: _primary,
                    ),
                  ),
                ),
            ],
          ),
        ),

        const SizedBox(height: 12),

        // Items
        ...buyerProvider.cartItems
            .map((item) => _buildCartItem(context, item, buyerProvider)),

        const SizedBox(height: 12),

        // Order Summary
        _buildCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: _primaryLight,
                      borderRadius: BorderRadius.circular(7),
                    ),
                    child: const Icon(Icons.receipt_long_outlined,
                        size: 15, color: _primary),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Order Summary',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 14,
                      color: _textPrimary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _buildSummaryRow(
                'Selected Items',
                '${_selectedItemIds.length} item${_selectedItemIds.length == 1 ? '' : 's'}',
              ),
              const SizedBox(height: 8),
              _buildSummaryRow(
                'Subtotal',
                '₱${_selectedTotal.toStringAsFixed(2)}',
              ),
              const SizedBox(height: 14),
              const Divider(height: 1, color: _border),
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Total',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 15,
                      color: _textPrimary,
                    ),
                  ),
                  Text(
                    '₱${_selectedTotal.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 20,
                      color: _primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 8),
      ],
    );
  }

  // ── Cart Item ──

  Widget _buildCartItem(
    BuildContext context,
    dynamic item,
    BuyerProvider buyerProvider,
  ) {
    final isSelected = _selectedItemIds.contains(item.id);
    final isUpdating = _updatingItemIds.contains(item.id);

    final product = buyerProvider.allProducts.cast<dynamic>().firstWhere(
          (p) => p != null && p.id == item.productId,
          orElse: () => null,
        );

    final availableStock = product?.stock ?? 0;
    // Don't show out of stock while updating
    final isOutOfStock = !isUpdating && (product == null || availableStock <= 0);
    final isOverStock = !isUpdating && item.quantity > availableStock;

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Slidable(
        key: ValueKey(item.id),
        endActionPane: ActionPane(
          motion: const DrawerMotion(),
          extentRatio: 0.25,
          children: [
            SlidableAction(
              onPressed: (context) async {
                // Show confirmation dialog
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (dialogContext) => AlertDialog(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    title: const Text(
                      'Remove Item',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 16,
                      ),
                    ),
                    content: Text(
                      'Remove "${item.name}" from cart?',
                      style: const TextStyle(fontSize: 14),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(dialogContext, false),
                        child: const Text(
                          'Cancel',
                          style: TextStyle(color: _textSecondary),
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.pop(dialogContext, true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFDC2626),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        child: const Text('Remove'),
                      ),
                    ],
                  ),
                );

                if (confirmed == true) {
                  final itemName = item.name;
                  await buyerProvider.removeFromCart(item.id);
                  if (context.mounted) {
                    setState(() {
                      _selectedItemIds.remove(item.id);
                    });
                    _showCustomSnackBar(
                      'Removed from Cart',
                      'Item removed successfully',
                    );
                  }
                }
              },
              backgroundColor: const Color(0xFFDC2626),
              foregroundColor: Colors.white,
              icon: Icons.delete_outline_rounded,
              label: 'Delete',
              borderRadius: BorderRadius.circular(16),
            ),
          ],
        ),
        child: _buildCard(
          border: isOutOfStock && !isUpdating
              ? Border.all(color: const Color(0xFFFCA5A5), width: 1.5)
              : isOverStock && !isUpdating
                  ? Border.all(color: const Color(0xFFFBBF24), width: 1.5)
                  : null,
          child: Column(
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Checkbox
                  Transform.scale(
                    scale: 0.85,
                    child: Checkbox(
                      value: isSelected && !isOutOfStock,
                      onChanged: isOutOfStock || isUpdating
                          ? null
                          : (value) => _toggleItemSelection(item.id),
                      activeColor: _primary,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(4)),
                      side: const BorderSide(color: _border, width: 1.5),
                    ),
                  ),

                  // Product Image
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      width: 72,
                      height: 72,
                      color: _background,
                      child: item.imageUrl != null && item.imageUrl!.isNotEmpty
                          ? Image.network(item.imageUrl!, fit: BoxFit.cover)
                          : const Icon(Icons.image_outlined,
                              color: _textSecondary, size: 28),
                    ),
                  ),

                  const SizedBox(width: 12),

                  // Details
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.name,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                            color: _textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '₱${item.price.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 15,
                            color: _primary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        // Stock indicator or loading
                        if (isUpdating)
                          const Row(
                            children: [
                              SizedBox(
                                width: 12,
                                height: 12,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor:
                                      AlwaysStoppedAnimation<Color>(_primary),
                                ),
                              ),
                              SizedBox(width: 6),
                              Text(
                                'Updating...',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: _primary,
                                ),
                              ),
                            ],
                          )
                        else
                          Row(
                            children: [
                              Container(
                                width: 6,
                                height: 6,
                                decoration: BoxDecoration(
                                  color: availableStock > 0
                                      ? const Color(0xFF16A34A)
                                      : const Color(0xFFDC2626),
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 5),
                              Text(
                                availableStock > 0
                                    ? 'Stock: $availableStock'
                                    : 'Out of stock',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: availableStock > 0
                                      ? const Color(0xFF16A34A)
                                      : const Color(0xFFDC2626),
                                ),
                              ),
                            ],
                          ),
                        const SizedBox(height: 10),

                        // Qty Controls (removed delete button)
                        Container(
                          decoration: BoxDecoration(
                            color: _background,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: _border),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              _buildQtyBtn(
                                Icons.remove,
                                item.quantity > 1 && !isUpdating
                                    ? () => _updateQuantity(item.id,
                                        item.quantity - 1, buyerProvider)
                                    : null,
                              ),
                              GestureDetector(
                                onTap: isUpdating
                                    ? null
                                    : () => _showQuantityInput(context, item,
                                        availableStock, buyerProvider),
                                child: Container(
                                  constraints:
                                      const BoxConstraints(minWidth: 32),
                                  alignment: Alignment.center,
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 4),
                                  child: Text(
                                    '${item.quantity}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w700,
                                      fontSize: 13,
                                      color: _textPrimary,
                                    ),
                                  ),
                                ),
                              ),
                              _buildQtyBtn(
                                Icons.add,
                                !isOutOfStock &&
                                        !isUpdating &&
                                        item.quantity < availableStock
                                    ? () => _updateQuantity(item.id,
                                        item.quantity + 1, buyerProvider)
                                    : null,
                                isAdd: true,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              // Warning banner
              if (isOutOfStock && !isUpdating) ...[
                const SizedBox(height: 10),
                _buildWarningBanner(
                  icon: Icons.warning_amber_rounded,
                  message: 'Out of stock — cannot checkout',
                  bgColor: const Color(0xFFFEF2F2),
                  iconColor: const Color(0xFFDC2626),
                  textColor: const Color(0xFFDC2626),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  // ── Empty Cart ──

  Widget _buildEmptyCart(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: _primaryLight,
                borderRadius: BorderRadius.circular(28),
              ),
              child: const Icon(Icons.shopping_bag_outlined,
                  size: 48, color: _primary),
            ),
            const SizedBox(height: 20),
            const Text(
              'Your cart is empty',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: _textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Looks like you haven\'t added\nanything yet.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: _textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 28),
            SizedBox(
              height: 48,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const BuyerHomeScreen()),
                    (route) => false,
                  );
                },
                icon: const Icon(Icons.shopping_bag_outlined, size: 17),
                label: const Text(
                  'Continue Shopping',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Checkout Footer ──

  Widget _buildCheckoutFooter(BuyerProvider buyerProvider) {
    final selectedItems = buyerProvider.cartItems
        .where((item) => _selectedItemIds.contains(item.id))
        .toList();

    final hasOutOfStock = selectedItems.any((item) {
      final product = buyerProvider.allProducts.cast<dynamic>().firstWhere(
            (p) => p != null && p.id == item.productId,
            orElse: () => null,
          );
      return product == null || product.stock <= 0;
    });

    final canCheckout = selectedItems.isNotEmpty && !hasOutOfStock;

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: BoxDecoration(
        color: _surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 16,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Mini summary row
            if (_selectedItemIds.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_selectedItemIds.length} item${_selectedItemIds.length == 1 ? '' : 's'} selected',
                    style: const TextStyle(fontSize: 12, color: _textSecondary),
                  ),
                  Text(
                    '₱${_selectedTotal.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: _primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
            ],

            // Checkout Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: canCheckout
                    ? () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                CheckoutScreen(selectedItems: selectedItems),
                          ),
                        );
                      }
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  disabledBackgroundColor: _border,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.shopping_cart_checkout_rounded,
                      size: 18,
                      color: canCheckout ? Colors.white : _textSecondary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      selectedItems.isEmpty
                          ? 'Select items to checkout'
                          : hasOutOfStock
                              ? 'Remove out-of-stock items'
                              : 'Checkout',
                      style: TextStyle(
                        color: canCheckout ? Colors.white : _textSecondary,
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Helpers ──

  Widget _buildCard({
    required Widget child,
    EdgeInsets? padding,
    Border? border,
  }) {
    return Container(
      width: double.infinity,
      padding: padding ?? const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(16),
        border: border,
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

  Widget _buildQtyBtn(IconData icon, VoidCallback? onTap,
      {bool isAdd = false}) {
    final enabled = onTap != null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 30,
        height: 30,
        decoration: BoxDecoration(
          color: enabled ? (isAdd ? _primary : _surface) : _background,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          size: 14,
          color:
              enabled ? (isAdd ? Colors.white : _textPrimary) : _textSecondary,
        ),
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: const TextStyle(fontSize: 13, color: _textSecondary)),
        Text(value,
            style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 13,
                color: _textPrimary)),
      ],
    );
  }

  Widget _buildWarningBanner({
    required IconData icon,
    required String message,
    required Color bgColor,
    required Color iconColor,
    required Color textColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, size: 15, color: iconColor),
          const SizedBox(width: 7),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                fontSize: 11,
                color: textColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showQuantityInput(
    BuildContext context,
    dynamic item,
    int availableStock,
    BuyerProvider buyerProvider,
  ) {
    final controller = TextEditingController(text: '${item.quantity}');
    String? errorText;

    showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            title: const Text(
              'Enter Quantity',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 16,
              ),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.name,
                  style: const TextStyle(
                    fontSize: 13,
                    color: _textSecondary,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: controller,
                  keyboardType: TextInputType.number,
                  autofocus: true,
                  decoration: InputDecoration(
                    labelText: 'Quantity',
                    hintText: 'Enter quantity',
                    helperText: 'Available stock: $availableStock',
                    helperStyle: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF16A34A),
                    ),
                    errorText: errorText,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: _primary, width: 2),
                    ),
                  ),
                  onChanged: (value) {
                    final qty = int.tryParse(value);
                    setDialogState(() {
                      if (qty == null || qty <= 0) {
                        errorText = 'Please enter a valid quantity';
                      } else if (qty > availableStock) {
                        errorText = 'Only $availableStock available in stock';
                      } else {
                        errorText = null;
                      }
                    });
                  },
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: _textSecondary),
                ),
              ),
              ElevatedButton(
                onPressed: errorText == null
                    ? () {
                        final qty =
                            int.tryParse(controller.text) ?? item.quantity;
                        if (qty > 0 && qty <= availableStock) {
                          Navigator.pop(dialogContext);
                          _updateQuantity(item.id, qty, buyerProvider);
                        }
                      }
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: _border,
                  disabledForegroundColor: _textSecondary,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child: const Text('Update'),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _updateQuantity(
    int itemId,
    int newQuantity,
    BuyerProvider buyerProvider,
  ) async {
    setState(() => _updatingItemIds.add(itemId));

    try {
      await buyerProvider.updateCartItem(itemId, newQuantity);
    } finally {
      if (mounted) {
        setState(() => _updatingItemIds.remove(itemId));
      }
    }
  }

  void _showCustomSnackBar(String title, String message) {
    final overlay = Overlay.of(context);
    final overlayEntry = OverlayEntry(
      builder: (context) => Positioned(
        top: MediaQuery.of(context).padding.top + 16,
        left: 16,
        right: 16,
        child: Material(
          color: Colors.transparent,
          child: TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.0, end: 1.0),
            duration: const Duration(milliseconds: 500),
            curve: Curves.easeOutBack,
            builder: (context, value, child) {
              final clampedValue = value.clamp(0.0, 1.0);
              return Transform.scale(
                scale: clampedValue,
                child: Opacity(
                  opacity: clampedValue,
                  child: child,
                ),
              );
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFEF4444), Color(0xFFDC2626)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFFEF4444).withValues(alpha: 0.4),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.25),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.delete_outline_rounded,
                      color: Colors.white,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.3,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          message,
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.9),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );

    overlay.insert(overlayEntry);

    Future.delayed(const Duration(milliseconds: 3500), () {
      overlayEntry.remove();
    });
  }
}
