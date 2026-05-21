import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../widgets/skeleton_loader.dart';
import '../../services/delivery_fee_service.dart';
import 'order_confirmation_screen.dart';

/// Checkout Screen
class CheckoutScreen extends StatefulWidget {
  final List<dynamic>? selectedItems;
  final bool directBuy;
  const CheckoutScreen({super.key, this.selectedItems, this.directBuy = false});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _addressController;
  late TextEditingController _notesController;
  late TextEditingController _couponController;
  String _paymentMethod = 'cod';
  double _deliveryFee = 0.0;
  String _selectedCouponId = '';
  List<dynamic> _addresses = [];
  dynamic _selectedAddress;
  List<dynamic> _availableCoupons = [];
  bool _isLoadingCoupons = false;
  bool _showCoupons = false;
  bool _isApplyingCoupon = false; // Track coupon application state

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
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    final name = authProvider.user?.firstName != null &&
            authProvider.user?.lastName != null
        ? '${authProvider.user!.firstName} ${authProvider.user!.lastName}'
            .trim()
        : '';
    final phone = authProvider.user?.phone ?? '';
    final address = authProvider.user?.address ?? '';

    _nameController = TextEditingController(text: name);
    _phoneController = TextEditingController(text: phone);
    _addressController = TextEditingController(text: address)
      ..addListener(() {
        if (mounted) _calculateDeliveryFee();
      });
    _notesController = TextEditingController();
    _couponController = TextEditingController();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        _fetchAddresses();
        _fetchAvailableCoupons();
        _calculateDeliveryFee();
      }
    });
  }

  void _calculateDeliveryFee() {
    if (!mounted) return;
    final address = _addressController.text;
    if (address.isNotEmpty) {
      final province = DeliveryFeeService.extractProvinceFromAddress(address);
      setState(() {
        _deliveryFee =
            DeliveryFeeService.calculateDeliveryFeeFromAddress(address);
      });
      debugPrint('=== Delivery Fee Calculation ===');
      debugPrint('Address: $address');
      debugPrint('Detected Province: $province');
      debugPrint('Delivery Fee: ₱$_deliveryFee');
    } else {
      setState(() {
        _deliveryFee = 0.0;
      });
    }
  }

  Future<void> _fetchAddresses() async {
    try {
      final response =
          await ApiService.request('GET', '/api/v1/buyer/addresses');
      if (response['success'] == true && mounted) {
        setState(() {
          _addresses = response['addresses'] ?? [];
          final defaultAddr = _addresses.firstWhere(
            (addr) => addr['is_default'] == true,
            orElse: () => _addresses.isNotEmpty ? _addresses.first : null,
          );
          if (defaultAddr != null) {
            _selectedAddress = defaultAddr;
            _addressController.text = _selectedAddress['full_address'] ?? '';
          }
        });
        if (mounted) _calculateDeliveryFee();
      }
    } catch (e) {
      debugPrint('Error fetching addresses: $e');
    }
  }

  Future<void> _showAddressPicker() async {
    if (!mounted) return;
    if (_addresses.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No saved addresses found.')),
      );
      return;
    }

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: const BoxDecoration(
            color: _surface,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                margin: const EdgeInsets.only(top: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: _border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
                child: Row(
                  children: [
                    const Text(
                      'Select Address',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: _textPrimary,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close,
                          size: 20, color: _textSecondary),
                      style: IconButton.styleFrom(
                        backgroundColor: _background,
                        minimumSize: const Size(36, 36),
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1, color: _border),
              ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.5,
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: _addresses.length,
                  separatorBuilder: (_, __) => const Divider(
                      height: 1, indent: 20, endIndent: 20, color: _border),
                  itemBuilder: (context, index) {
                    final addr = _addresses[index];
                    final isSelected = _selectedAddress != null &&
                        addr['id']?.toString() ==
                            _selectedAddress['id']?.toString();
                    final isDefault = addr['is_default'] == true;
                    return InkWell(
                      onTap: () {
                        setState(() {
                          _selectedAddress = addr;
                          _addressController.text = addr['full_address'] ?? '';
                        });
                        _calculateDeliveryFee();
                        Navigator.pop(context);
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 14),
                        child: Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: isSelected ? _primary : _primaryLight,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Icon(
                                Icons.location_on,
                                size: 20,
                                color: isSelected ? Colors.white : _primary,
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        addr['label']?.toString() ?? 'Address',
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w600,
                                          color: isSelected
                                              ? _primary
                                              : _textPrimary,
                                        ),
                                      ),
                                      if (isDefault) ...[
                                        const SizedBox(width: 6),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: _primaryLight,
                                            borderRadius:
                                                BorderRadius.circular(6),
                                          ),
                                          child: const Text(
                                            'Default',
                                            style: TextStyle(
                                              fontSize: 9,
                                              fontWeight: FontWeight.w600,
                                              color: _primary,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    addr['full_address']?.toString() ?? '',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: _textSecondary,
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                            if (isSelected)
                              Container(
                                width: 22,
                                height: 22,
                                decoration: const BoxDecoration(
                                  color: _primary,
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.check,
                                    color: Colors.white, size: 14),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  Future<void> _fetchAvailableCoupons() async {
    setState(() => _isLoadingCoupons = true);
    try {
      final response =
          await ApiService.request('GET', '/api/available-coupons');
      if (response['success'] == true) {
        setState(() {
          _availableCoupons = response['coupons'] ?? [];
        });
      }
    } catch (e) {
      debugPrint('Error fetching coupons: $e');
    } finally {
      setState(() => _isLoadingCoupons = false);
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _notesController.dispose();
    _couponController.dispose();
    super.dispose();
  }

  Future<bool> _applyCoupon(BuyerProvider buyerProvider) async {
    final couponCode = _couponController.text.trim();
    if (couponCode.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a coupon code')),
      );
      return false;
    }

    setState(() => _isApplyingCoupon = true);

    final success = await buyerProvider.applyCoupon(couponCode);
    
    if (mounted) {
      setState(() => _isApplyingCoupon = false);
      
      if (success) {
        setState(() {
          final appliedCoupon = buyerProvider.appliedCoupon;
          if (appliedCoupon != null) {
            _selectedCouponId = appliedCoupon['id'].toString();
          }
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Coupon applied successfully!')),
        );
      } else {
        setState(() => _selectedCouponId = '');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content:
                  Text(buyerProvider.errorMessage ?? 'Failed to apply coupon')),
        );
      }
    }
    return success;
  }

  Future<void> _placeOrder(BuyerProvider buyerProvider) async {
    final authProvider = context.read<AuthProvider>();
    if (!authProvider.isAuthenticated) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please log in to place an order')),
      );
      return;
    }

    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your name')),
      );
      return;
    }
    if (_addressController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a delivery address')),
      );
      return;
    }

    debugPrint('=== Checkout Debug ===');
    debugPrint('Name: "${_nameController.text}"');
    debugPrint('Phone: "${_phoneController.text}"');
    debugPrint('Address: "${_addressController.text}"');
    debugPrint('Payment Method: $_paymentMethod');

    List<int>? selectedItemIds;
    Map<int, int>? productQuantities;

    if (widget.selectedItems != null) {
      if (widget.directBuy) {
        selectedItemIds = widget.selectedItems!.map<int>((item) {
          if (item is Map)
            return item['product_id'] as int;
          else
            return item.productId;
        }).toList();
        productQuantities = {
          for (var item in widget.selectedItems!)
            if (item is Map)
              item['product_id'] as int: item['quantity'] as int
            else
              item.productId: item.quantity
        };
      } else {
        selectedItemIds = widget.selectedItems!.map<int>((item) {
          if (item is Map)
            return item['id'] as int;
          else
            return item.id;
        }).toList();
      }
    }

    final order = await buyerProvider.checkout(
      recipientName: _nameController.text,
      recipientPhone: _phoneController.text,
      shippingAddress: _addressController.text,
      paymentMethod: _paymentMethod,
      notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      couponId:
          _selectedCouponId.isNotEmpty ? int.tryParse(_selectedCouponId) : null,
      shippingFee: _deliveryFee,
      deliveryFee: _deliveryFee,
      selectedItemIds: selectedItemIds,
      productQuantities: productQuantities,
    );

    if (mounted) {
      if (order != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Order placed successfully')),
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => OrderConfirmationScreen(order: order),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content:
                  Text(buyerProvider.errorMessage ?? 'Failed to place order')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();
    final isInitialLoading = buyerProvider.isLoading && _addresses.isEmpty;

    return Scaffold(
      backgroundColor: _background,
      appBar: AppBar(
        title: const Text('Checkout'),
        backgroundColor: _primary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: Colors.white, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: isInitialLoading
          ? const ListSkeletonLoader(
              itemSkeleton: OrderCardSkeleton(),
              itemCount: 4,
              padding: EdgeInsets.all(16),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (buyerProvider.errorMessage != null)
                    _buildErrorBanner(buyerProvider.errorMessage!),
                  
                  _buildSectionLabel('Delivery Address'),
                  const SizedBox(height: 8),
                  _buildCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: _primaryLight,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'Default',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  color: _primary,
                                ),
                              ),
                            ),
                            const Spacer(),
                            GestureDetector(
                              onTap: _showAddressPicker,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: _primaryLight,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.edit_outlined,
                                        size: 13, color: _primary),
                                    SizedBox(width: 4),
                                    Text(
                                      'Change',
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w600,
                                        color: _primary,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: _primaryLight,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.location_on,
                                  size: 18, color: _primary),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                _addressController.text.isEmpty
                                    ? 'No address selected'
                                    : _addressController.text,
                                style: TextStyle(
                                  fontSize: 13,
                                  height: 1.5,
                                  color: _addressController.text.isEmpty
                                      ? _textSecondary
                                      : _textPrimary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        if (_deliveryFee > 0) ...[
                          const SizedBox(height: 10),
                          const Divider(height: 1, color: _border),
                          const SizedBox(height: 10),
                          Row(
                            children: [
                              const Icon(Icons.local_shipping_outlined,
                                  size: 14, color: _textSecondary),
                              const SizedBox(width: 6),
                              const Text(
                                'Delivery fee for this area: ',
                                style: TextStyle(
                                    fontSize: 12, color: _textSecondary),
                              ),
                              Text(
                                '₱${_deliveryFee.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  color: _primary,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  _buildSectionLabel('Order Notes'),
                  const SizedBox(height: 8),
                  _buildCard(
                    padding: EdgeInsets.zero,
                    child: TextFormField(
                      controller: _notesController,
                      style: const TextStyle(fontSize: 14, color: _textPrimary),
                      decoration: const InputDecoration(
                        hintText: 'e.g., Leave at door, call upon arrival',
                        hintStyle:
                            TextStyle(fontSize: 13, color: _textSecondary),
                        prefixIcon: Icon(Icons.sticky_note_2_outlined,
                            size: 18, color: _textSecondary),
                        border: InputBorder.none,
                        contentPadding:
                            EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      ),
                      maxLines: 2,
                    ),
                  ),
                  const SizedBox(height: 20),
                  _buildSectionLabel('Payment Method'),
                  const SizedBox(height: 8),
                  _buildCard(
                    child: Column(
                      children: [
                        _buildPaymentMethodOption(
                          'cod',
                          'Cash on Delivery',
                          Icons.payments_outlined,
                          'Pay when you receive',
                        ),
                        const SizedBox(height: 10),
                        _buildPaymentMethodOption(
                          'gcash',
                          'GCash',
                          Icons.account_balance_wallet_outlined,
                          'Pay via GCash wallet',
                        ),
                        const SizedBox(height: 10),
                        _buildPaymentMethodOption(
                          'card',
                          'Credit / Debit Card',
                          Icons.credit_card_outlined,
                          'Pay with card',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  _buildOrderSummaryCard(buyerProvider),
                  const SizedBox(height: 28),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: buyerProvider.isLoading
                          ? null
                          : () => _placeOrder(buyerProvider),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _primary,
                        disabledBackgroundColor:
                            _primary.withValues(alpha: 0.5),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: buyerProvider.isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              'Place Order',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                                letterSpacing: 0.3,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Center(
                    child: TextButton.icon(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back_ios_new,
                          size: 13, color: _textSecondary),
                      label: const Text(
                        'Back to Cart',
                        style: TextStyle(
                            fontSize: 13,
                            color: _textSecondary,
                            fontWeight: FontWeight.w500),
                      ),
                    ),
                  ),
                  SizedBox(
                      height: MediaQuery.of(context).viewInsets.bottom + 16),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionLabel(String label) {
    return Text(
      label,
      style: const TextStyle(
        fontSize: 13,
        fontWeight: FontWeight.w700,
        color: _textSecondary,
        letterSpacing: 0.5,
      ),
    );
  }

  Widget _buildCard({required Widget child, EdgeInsets? padding}) {
    return Container(
      width: double.infinity,
      padding: padding ?? const EdgeInsets.all(16),
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

  Widget _buildErrorBanner(String message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(color: Color(0xFFDC2626), fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrderSummaryCard(BuyerProvider buyerProvider) {
    final itemsToShow = widget.selectedItems ?? buyerProvider.cartItems;

    double subtotal;
    if (widget.selectedItems != null) {
      subtotal = widget.selectedItems!.fold<double>(0, (sum, item) {
        if (item is Map) {
          return sum +
              (item['price'] as num).toDouble() * (item['quantity'] as int);
        } else {
          return sum + item.price * item.quantity;
        }
      });
    } else {
      subtotal = buyerProvider.cartTotal;
    }

    final discount = buyerProvider.discount;
    final cappedDiscount = discount > subtotal ? subtotal : discount;
    final total = (subtotal - cappedDiscount) + _deliveryFee;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionLabel('Order Summary'),
        const SizedBox(height: 8),
        _buildCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: itemsToShow.length,
                separatorBuilder: (_, __) =>
                    const Divider(height: 20, color: _border),
                itemBuilder: (context, index) {
                  final item = itemsToShow[index];
                  final String imageUrl;
                  final String name;
                  final int quantity;
                  final double price;

                  if (item is Map) {
                    imageUrl = item['image_url'] ??
                        item['product_image'] ??
                        item['image'] ??
                        '';
                    name = item['name'] ?? item['product_name'] ?? '';
                    quantity = item['quantity'] ?? 1;
                    price = (item['price'] as num).toDouble();
                  } else {
                    imageUrl = item.imageUrl ?? '';
                    name = item.name;
                    quantity = item.quantity;
                    price = item.price;
                  }

                  return Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.network(
                          imageUrl,
                          width: 64,
                          height: 64,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            width: 64,
                            height: 64,
                            color: _background,
                            child: const Icon(Icons.image_not_supported,
                                size: 26, color: _textSecondary),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              name,
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
                              'Qty: $quantity  ×  ₱${price.toStringAsFixed(2)}',
                              style: const TextStyle(
                                  fontSize: 12, color: _textSecondary),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '₱${(price * quantity).toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: _textPrimary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.clip,
                      ),
                    ],
                  );
                },
              ),

              const SizedBox(height: 20),
              const Divider(height: 1, color: _border),
              const SizedBox(height: 16),

              // Coupon
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 44,
                      decoration: BoxDecoration(
                        color: _background,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: _border),
                      ),
                      child: TextFormField(
                        controller: _couponController,
                        enabled: !_isApplyingCoupon,
                        style:
                            const TextStyle(fontSize: 13, color: _textPrimary),
                        decoration: const InputDecoration(
                          hintText: 'Promo code',
                          hintStyle:
                              TextStyle(fontSize: 13, color: _textSecondary),
                          prefixIcon: Icon(Icons.local_offer_outlined,
                              size: 16, color: _textSecondary),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                              horizontal: 12, vertical: 10),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  SizedBox(
                    height: 44,
                    child: ElevatedButton(
                      onPressed: _isApplyingCoupon
                          ? null
                          : () => _applyCoupon(buyerProvider),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _primary,
                        disabledBackgroundColor: _primary.withValues(alpha: 0.6),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                        padding: const EdgeInsets.symmetric(horizontal: 18),
                      ),
                      child: _isApplyingCoupon
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              'Apply',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Colors.white,
                              ),
                            ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),
              GestureDetector(
                onTap: () => setState(() => _showCoupons = !_showCoupons),
                child: Row(
                  children: [
                    Icon(
                      _showCoupons
                          ? Icons.keyboard_arrow_up
                          : Icons.keyboard_arrow_down,
                      size: 16,
                      color: _primary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      _showCoupons ? 'Hide coupons' : 'View available coupons',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: _primary,
                      ),
                    ),
                  ],
                ),
              ),

              if (_showCoupons) ...[
                const SizedBox(height: 12),
                if (_isLoadingCoupons)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      child: SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2)),
                    ),
                  )
                else if (_availableCoupons.isNotEmpty)
                  Container(
                    decoration: BoxDecoration(
                      color: _background,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: _border),
                    ),
                    child: ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _availableCoupons.length,
                      separatorBuilder: (_, __) =>
                          const Divider(height: 1, color: _border),
                      itemBuilder: (context, index) {
                        final coupon = _availableCoupons[index];
                        final discountType = coupon['discount_type'];
                        final discountValue = coupon['discount_value'];
                        String discountText;
                        if (discountType == 'percentage') {
                          discountText = '$discountValue% off';
                        } else if (discountType == 'fixed') {
                          discountText = '₱$discountValue off';
                        } else if (discountType == 'free_shipping') {
                          discountText = 'Free shipping';
                        } else {
                          discountText = '$discountValue off';
                        }

                        return InkWell(
                          onTap: () {
                            _couponController.text = coupon['code'];
                            setState(() => _showCoupons = false);
                          },
                          borderRadius: BorderRadius.circular(12),
                          child: Padding(
                            padding: const EdgeInsets.all(14),
                            child: Row(
                              children: [
                                Container(
                                  width: 36,
                                  height: 36,
                                  decoration: BoxDecoration(
                                    color: _primaryLight,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Icon(Icons.local_offer,
                                      size: 16, color: _primary),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        coupon['code'] ?? '',
                                        style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: _textPrimary,
                                        ),
                                      ),
                                      if (coupon['description'] != null &&
                                          coupon['description'].isNotEmpty)
                                        Text(
                                          coupon['description'],
                                          style: const TextStyle(
                                              fontSize: 11,
                                              color: _textSecondary),
                                        ),
                                      if (coupon['min_order_amount'] != null &&
                                          coupon['min_order_amount'] > 0)
                                        Text(
                                          'Min. ₱${coupon['min_order_amount']}',
                                          style: const TextStyle(
                                              fontSize: 10,
                                              color: _textSecondary),
                                        ),
                                    ],
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: _primaryLight,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    discountText,
                                    style: const TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w700,
                                      color: _primary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  )
                else
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 12),
                    child: Center(
                      child: Text(
                        'No coupons available',
                        style: TextStyle(fontSize: 12, color: _textSecondary),
                      ),
                    ),
                  ),
              ],

              const SizedBox(height: 20),
              const Divider(height: 1, color: _border),
              const SizedBox(height: 16),

              _buildPriceRow('Subtotal', '₱${subtotal.toStringAsFixed(2)}'),
              if (cappedDiscount > 0) ...[
                const SizedBox(height: 10),
                _buildPriceRow(
                  'Discount',
                  '-₱${cappedDiscount.toStringAsFixed(2)}',
                  valueColor: const Color(0xFF16A34A),
                ),
              ],
              const SizedBox(height: 10),
              _buildPriceRow(
                'Delivery Fee',
                '₱${_deliveryFee.toStringAsFixed(2)}',
                icon: Icons.local_shipping_outlined,
              ),

              const SizedBox(height: 16),
              const Divider(height: 1, color: _border),
              const SizedBox(height: 16),

              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                decoration: BoxDecoration(
                  color: _primaryLight,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Total',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: _textPrimary,
                      ),
                    ),
                    Text(
                      '₱${total.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: _primary,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 12),

              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFBBF7D0)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.schedule, size: 15, color: Color(0xFF16A34A)),
                    SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        'Estimated delivery: 3–5 business days',
                        style: TextStyle(
                          fontSize: 11,
                          color: Color(0xFF15803D),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPriceRow(String label, String value,
      {Color? valueColor, IconData? icon}) {
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
            color: valueColor ?? _textPrimary,
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentMethodOption(
    String value,
    String title,
    IconData icon,
    String subtitle,
  ) {
    final isSelected = _paymentMethod == value;
    return GestureDetector(
      onTap: () => setState(() => _paymentMethod = value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? _primaryLight : _background,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? _primary : _border,
            width: isSelected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: isSelected ? _primary : _surface,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isSelected ? _primary : _border,
                ),
              ),
              child: Icon(
                icon,
                color: isSelected ? Colors.white : _textSecondary,
                size: 20,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isSelected ? _primary : _textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 11, color: _textSecondary),
                  ),
                ],
              ),
            ),
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              child: isSelected
                  ? const Icon(Icons.check_circle_rounded,
                      color: _primary, size: 22, key: ValueKey('checked'))
                  : const Icon(Icons.radio_button_unchecked,
                      color: _border, size: 22, key: ValueKey('unchecked')),
            ),
          ],
        ),
      ),
    );
  }
}
