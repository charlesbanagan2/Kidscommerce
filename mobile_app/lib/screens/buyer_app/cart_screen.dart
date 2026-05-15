import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
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

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BuyerProvider>().fetchCart();
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
      backgroundColor: const Color(0xFFF0F4FB),
      body: Column(
        children: [
          // Header with gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
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
                  icon: const Icon(Icons.arrow_back, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
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
                        'My Cart',
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
                        '${buyerProvider.cartItems.length} items in your cart',
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
          ),

          // Main Content
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

          // Bottom Checkout Button
          if (buyerProvider.cartItems.isNotEmpty)
            _buildCheckoutFooter(buyerProvider),
        ],
      ),
    );
  }

  Widget _buildCartContent(BuildContext context, BuyerProvider buyerProvider) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Select All Widget
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
          decoration: BoxDecoration(
              color: Colors.white, borderRadius: BorderRadius.circular(15)),
          child: CheckboxListTile(
            value: _selectAll,
            onChanged: (value) =>
                _toggleSelectAll(value ?? false, buyerProvider),
            title: const Text("Select All Items",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            controlAffinity: ListTileControlAffinity.leading,
            activeColor: const Color(0xFF1e4db7),
            checkboxShape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(5)),
          ),
        ),

        // List of Items
        ...buyerProvider.cartItems
            .map((item) => _buildCartItem(context, item, buyerProvider))
            .toList(),

        const SizedBox(height: 16),

        // Order Summary Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: Colors.white, borderRadius: BorderRadius.circular(20)),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Order Summary",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 12),
              _buildSummaryRow(
                  "Selected Items", _selectedItemIds.length.toString()),
              _buildSummaryRow(
                  "Subtotal", "₱${_selectedTotal.toStringAsFixed(2)}"),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("Total",
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  Text(
                    "₱${_selectedTotal.toStringAsFixed(2)}",
                    style: const TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 18,
                        color: Color(0xFF1e4db7)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyCart(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.shopping_bag_outlined,
              size: 80, color: Colors.grey.shade300),
          const SizedBox(height: 16),
          const Text("Your cart is empty",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(
                    builder: (context) => const BuyerHomeScreen()),
                (route) => false,
              );
            },
            style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1e4db7),
                padding:
                    const EdgeInsets.symmetric(horizontal: 30, vertical: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10))),
            child: const Text("Continue Shopping",
                style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Widget _buildCartItem(
    BuildContext context,
    dynamic item,
    BuyerProvider buyerProvider,
  ) {
    final isSelected = _selectedItemIds.contains(item.id);

    // Get current product stock
    final product = buyerProvider.allProducts.cast<dynamic>().firstWhere(
          (p) => p != null && p.id == item.productId, // ✅ Explicit null check
          orElse: () => null,
        );

    final availableStock = product?.stock ?? 0;
    final isOverStock = item.quantity > availableStock;
    final isOutOfStock = availableStock <= 0;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: isOverStock || isOutOfStock
            ? Border.all(color: Colors.red.shade300, width: 1.5)
            : null,
      ),
      child: Column(
        children: [
          Row(
            children: [
              Transform.scale(
                scale: 0.9,
                child: Checkbox(
                  value: isSelected && !isOutOfStock,
                  onChanged: isOutOfStock
                      ? null
                      : (value) => _toggleItemSelection(item.id),
                  activeColor: const Color(0xFF1e4db7),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(4)),
                ),
              ),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  width: 70,
                  height: 70,
                  color: Colors.grey.shade100,
                  child: item.imageUrl != null && item.imageUrl!.isNotEmpty
                      ? Image.network(item.imageUrl!, fit: BoxFit.cover)
                      : const Icon(Icons.image_outlined, color: Colors.grey),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 14)),
                    const SizedBox(height: 4),
                    Text("₱${item.price.toStringAsFixed(2)}",
                        style: const TextStyle(
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF1e4db7))),
                    const SizedBox(height: 4),
                    Text(
                      'Stock: $availableStock',
                      style: TextStyle(
                        fontSize: 11,
                        color: availableStock > 0
                            ? Colors.green.shade700
                            : Colors.red.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Quantity Controls
                        Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                              color: const Color(0xFFF0F4FB),
                              borderRadius: BorderRadius.circular(10)),
                          child: Row(
                            children: [
                              _buildQtyBtn(
                                  Icons.remove,
                                  Colors.white,
                                  Colors.black,
                                  item.quantity > 1
                                      ? () => buyerProvider.updateCartItem(
                                          item.id, item.quantity - 1)
                                      : null),
                              Padding(
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 10),
                                child: Text("${item.quantity}",
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold)),
                              ),
                              _buildQtyBtn(
                                  Icons.add,
                                  const Color(0xFF1e4db7),
                                  Colors.white,
                                  item.quantity < availableStock
                                      ? () => buyerProvider.updateCartItem(
                                          item.id, item.quantity + 1)
                                      : null),
                            ],
                          ),
                        ),
                        // Trash/Delete Button
                        GestureDetector(
                          onTap: () => buyerProvider.removeFromCart(item.id),
                          child: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                                color: Colors.red.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(10)),
                            child: const Icon(Icons.delete_outline,
                                size: 16, color: Colors.redAccent),
                          ),
                        ),
                      ],
                    )
                  ],
                ),
              )
            ],
          ),
          // Stock warning
          if (isOutOfStock)
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.warning_amber_rounded,
                      size: 16, color: Colors.red.shade700),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Out of stock - Cannot checkout',
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.red.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else if (isOverStock)
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline,
                      size: 16, color: Colors.orange.shade700),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Quantity exceeds stock - Auto-adjusted to $availableStock',
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.orange.shade700,
                        fontWeight: FontWeight.w600,
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

  Widget _buildQtyBtn(IconData icon, Color bg, Color fg, VoidCallback? onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 24,
        height: 24,
        decoration: BoxDecoration(
            color: onTap == null ? Colors.grey.shade300 : bg,
            borderRadius: BorderRadius.circular(6)),
        child: Icon(icon, size: 12, color: fg),
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          Text(value,
              style:
                  const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildCheckoutFooter(BuyerProvider buyerProvider) {
    final selectedItems = buyerProvider.cartItems
        .where((item) => _selectedItemIds.contains(item.id))
        .toList();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Color(0xFFEEEEEE))),
      ),
      child: Container(
        width: double.infinity,
        height: 55,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)]),
          borderRadius: BorderRadius.circular(15),
          boxShadow: [
            BoxShadow(
                color: const Color(0xFF1e4db7).withValues(alpha: 0.3),
                blurRadius: 10,
                offset: const Offset(0, 5))
          ],
        ),
        child: ElevatedButton(
          onPressed: selectedItems.isEmpty
              ? null
              : () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) =>
                          CheckoutScreen(selectedItems: selectedItems),
                    ),
                  );
                },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.transparent,
            shadowColor: Colors.transparent,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
          ),
          child: const Text(
            "Checkout",
            style: TextStyle(
                color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
          ),
        ),
      ),
    );
  }
}
