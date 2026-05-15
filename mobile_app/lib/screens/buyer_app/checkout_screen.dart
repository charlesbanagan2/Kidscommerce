import '../../models/order.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../widgets/skeleton_loader.dart';
import '../../services/delivery_fee_service.dart';

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

  @override
  void initState() {
    super.initState();
    final buyerProvider = Provider.of<BuyerProvider>(context, listen: false);
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    debugPrint('=== Checkout Init Debug ===');
    debugPrint('Buyer: ${buyerProvider.buyer}');
    debugPrint('Auth User: ${authProvider.user}');
    debugPrint('Buyer Name: ${buyerProvider.buyer?.name}');
    debugPrint('Buyer Phone: ${buyerProvider.buyer?.phoneNumber}');
    debugPrint('Buyer Address: ${buyerProvider.buyer?.address}');

    // Initialize controllers with authProvider data (most reliable source)
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
        // Recalculate delivery fee when address changes
        _calculateDeliveryFee();
      });
    _notesController = TextEditingController();
    _couponController = TextEditingController();

    // Fetch buyer profile to get updated data
    if (authProvider.isAuthenticated) {
      buyerProvider.fetchProfile().then((_) {
        debugPrint('=== Profile Fetch Debug ===');
        debugPrint('Auth User phone: ${authProvider.user?.phone}');
        // Get raw profile data without fallback values
        final profile = buyerProvider.profile;
        debugPrint('Raw profile: $profile');
        if (profile != null && mounted) {
          setState(() {
            // Use raw profile data, not Buyer model fallbacks
            final profileName =
                '${profile['first_name'] ?? ''} ${profile['last_name'] ?? ''}'
                    .trim();
            final profilePhone = profile['phone'] as String?;
            final profileAddress = profile['address'] as String?;

            debugPrint('Profile phone from API: $profilePhone');

            if (_nameController.text.isEmpty && profileName.isNotEmpty) {
              _nameController.text = profileName;
            }
            if ((_phoneController.text.isEmpty ||
                    _phoneController.text == 'No Phone') &&
                profilePhone != null &&
                profilePhone.isNotEmpty) {
              _phoneController.text = profilePhone;
            }
            if ((_addressController.text.isEmpty ||
                    _addressController.text == 'No Address') &&
                profileAddress != null &&
                profileAddress.isNotEmpty) {
              _addressController.text = profileAddress;
            }
            debugPrint('=== Controllers After Profile Update ===');
            debugPrint('Name: ${_nameController.text}');
            debugPrint('Phone: ${_phoneController.text}');
            debugPrint('Address: ${_addressController.text}');
            // Recalculate delivery fee with updated address
            _calculateDeliveryFee();
          });
        }
      }).catchError((error) {
        debugPrint('=== Profile Fetch Error ===');
        debugPrint('Error: $error');
      });
    }

    _fetchAddresses();
    _fetchAvailableCoupons();
    _calculateDeliveryFee();
  }

  void _calculateDeliveryFee() {
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
      if (response['success'] == true) {
        setState(() {
          _addresses = response['addresses'] ?? [];
          if (_addresses.isNotEmpty) {
            _selectedAddress = _addresses.first;
            _addressController.text = _selectedAddress['full_address'] ?? '';
          }
        });
        // Recalculate delivery fee with fetched address
        _calculateDeliveryFee();
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

    final selected = await showDialog<dynamic>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Select Delivery Address'),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _addresses.length,
              itemBuilder: (context, index) {
                final addr = _addresses[index];
                final isSelected = _selectedAddress != null &&
                    addr['id']?.toString() ==
                        _selectedAddress['id']?.toString();
                return ListTile(
                  title: Text(addr['label']?.toString() ?? 'Address'),
                  subtitle: Text(addr['full_address']?.toString() ?? ''),
                  trailing: isSelected
                      ? const Icon(Icons.check, color: Colors.green)
                      : null,
                  onTap: () => Navigator.pop(context, addr),
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );

    if (!mounted) return;
    if (selected != null) {
      setState(() {
        _selectedAddress = selected;
        _addressController.text = _selectedAddress['full_address'] ?? '';
      });
      _calculateDeliveryFee();
    }
  }

  Future<void> _fetchAvailableCoupons() async {
    setState(() {
      _isLoadingCoupons = true;
    });
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
      setState(() {
        _isLoadingCoupons = false;
      });
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

    final success = await buyerProvider.applyCoupon(couponCode);
    if (mounted) {
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
        setState(() {
          _selectedCouponId = '';
        });
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

    debugPrint('=== Checkout Debug ===');
    debugPrint('Name: "${_nameController.text}"');
    debugPrint('Phone: "${_phoneController.text}"');
    debugPrint('Address: "${_addressController.text}"');
    debugPrint('Payment Method: $_paymentMethod');

    // Extract selected items for checkout
    List<int>? selectedItemIds;
    Map<int, int>? productQuantities;

    if (widget.selectedItems != null) {
      if (widget.directBuy) {
        // Direct buy: pass product IDs with quantities
        selectedItemIds = widget.selectedItems!.map<int>((item) {
          if (item is Map) {
            return item['product_id'] as int;
          } else {
            return item.productId;
          }
        }).toList();
        productQuantities = {
          for (var item in widget.selectedItems!)
            if (item is Map)
              item['product_id'] as int: item['quantity'] as int
            else
              item.productId: item.quantity
        };
      } else {
        // Cart checkout: pass cart item IDs
        selectedItemIds = widget.selectedItems!.map<int>((item) {
          if (item is Map) {
            return item['id'] as int;
          } else {
            return item.id;
          }
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

    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      appBar: AppBar(
        title: const Text('Checkout'),
        backgroundColor: const Color(0xFF1a2f6b),
        elevation: 0,
        centerTitle: true,
        titleTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: buyerProvider.isLoading
          ? const ListSkeletonLoader(
              itemSkeleton: OrderCardSkeleton(),
              itemCount: 4,
              padding: EdgeInsets.all(16),
            )
          : SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (buyerProvider.errorMessage != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade100,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          buyerProvider.errorMessage!,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    // Contact Information (from database)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Contact Information',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              const Icon(Icons.person,
                                  size: 18, color: Colors.grey),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _nameController.text,
                                  style: const TextStyle(fontSize: 14),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              const Icon(Icons.phone,
                                  size: 18, color: Colors.grey),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _phoneController.text,
                                  style: const TextStyle(fontSize: 14),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Delivery Address (website-style)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Row(
                                  children: [
                                    const Text(
                                      'Delivery Address',
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(width: 6),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 6,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF3B82F6),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: const Text(
                                        'Default',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 10,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              TextButton(
                                onPressed: _showAddressPicker,
                                style: TextButton.styleFrom(
                                  padding:
                                      const EdgeInsets.symmetric(horizontal: 8),
                                  minimumSize: const Size(0, 32),
                                  tapTargetSize:
                                      MaterialTapTargetSize.shrinkWrap,
                                ),
                                child: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.edit, size: 14),
                                    SizedBox(width: 4),
                                    Text('Change',
                                        style: TextStyle(fontSize: 12)),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _addressController.text,
                              style: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Order Notes
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: TextFormField(
                        controller: _notesController,
                        decoration: const InputDecoration(
                          labelText: 'Order Notes (Optional)',
                          hintText: 'e.g., Leave at door, call upon arrival',
                          prefixIcon: Icon(Icons.note_outlined, size: 20),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                        ),
                        maxLines: 2,
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Payment Method Section
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Payment Method',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _buildPaymentMethodOption(
                            'cod',
                            'Cash on Delivery',
                            Icons.money,
                            'Pay when you receive',
                          ),
                          const SizedBox(height: 8),
                          _buildPaymentMethodOption(
                            'gcash',
                            'GCash',
                            Icons.account_balance_wallet,
                            'Pay via GCash wallet',
                          ),
                          const SizedBox(height: 8),
                          _buildPaymentMethodOption(
                            'card',
                            'Credit/Debit Card',
                            Icons.credit_card,
                            'Pay with card',
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),
                    // Order Summary Card (like website)
                    _buildOrderSummaryCard(buyerProvider),
                    const SizedBox(height: 24),
                    // Checkout Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: buyerProvider.isLoading
                            ? null
                            : () => _placeOrder(buyerProvider),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1e4db7),
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: buyerProvider.isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white),
                                ),
                              )
                            : const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    'Place Order',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Center(
                      child: TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.arrow_back,
                                size: 16, color: Colors.grey.shade600),
                            const SizedBox(width: 4),
                            Text(
                              'Back to Cart',
                              style: TextStyle(color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(
                        height: MediaQuery.of(context).viewInsets.bottom + 16),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOrderSummaryCard(BuyerProvider buyerProvider) {
    // Use selected items if provided, otherwise use all cart items
    final itemsToShow = widget.selectedItems ?? buyerProvider.cartItems;

    // Calculate subtotal
    double subtotal;
    if (widget.selectedItems != null) {
      subtotal = widget.selectedItems!.fold<double>(
        0,
        (sum, item) {
          if (item is Map) {
            return sum +
                (item['price'] as num).toDouble() * (item['quantity'] as int);
          } else {
            return sum + item.price * item.quantity;
          }
        },
      );
    } else {
      subtotal = buyerProvider.cartTotal;
    }

    final discount = buyerProvider.discount;
    final cappedDiscount = discount > subtotal ? subtotal : discount;
    final total = (subtotal - cappedDiscount) + _deliveryFee;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            const Text(
              'Order Summary',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // Order Items
            const Text(
              'Order Items',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: itemsToShow.length,
              itemBuilder: (context, index) {
                final item = itemsToShow[index];

                final String imageUrl;
                final String name;
                final int quantity;
                final double price;

                if (item is Map) {
                  // Handle multiple possible image field names
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

                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      // Product Image
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          imageUrl,
                          width: 70,
                          height: 70,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) =>
                              Container(
                            width: 70,
                            height: 70,
                            color: Colors.grey.shade200,
                            child:
                                const Icon(Icons.image_not_supported, size: 30),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      // Product Details
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              name,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Qty: $quantity',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      // Price
                      Text(
                        '₱${(price * quantity).toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 16),

            // Subtotal
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Subtotal'),
                Flexible(
                  child: Text(
                    '₱${subtotal.toStringAsFixed(2)}',
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Discount Code Section
            const Text(
              'Discount Code',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _couponController,
                    decoration: InputDecoration(
                      hintText: 'Enter promo code',
                      prefixIcon: const Icon(Icons.local_offer, size: 20),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _applyCoupon(buyerProvider),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1e4db7),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                  ),
                  child: const Text('Apply'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // View Coupons Button
            TextButton.icon(
              onPressed: () {
                setState(() {
                  _showCoupons = !_showCoupons;
                });
              },
              icon: const Icon(Icons.local_offer, size: 16),
              label: Text(_showCoupons ? 'Hide Coupons' : 'View Coupons'),
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFF1e4db7),
              ),
            ),
            if (_showCoupons)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  if (_isLoadingCoupons)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: Center(
                          child: SizedBox(
                              width: 20,
                              height: 20,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2))),
                    )
                  else if (_availableCoupons.isNotEmpty)
                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Available Coupons',
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.grey,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1e4db7),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    '${_availableCoupons.length}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const Divider(height: 1),
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: _availableCoupons.length,
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
                                  setState(() {
                                    _showCoupons = false;
                                  });
                                },
                                child: Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: const BoxDecoration(
                                    border: Border(
                                      bottom: BorderSide(
                                          color: Colors.grey, width: 0.5),
                                    ),
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            coupon['code'] ?? '',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.w600,
                                              fontSize: 13,
                                            ),
                                          ),
                                          Text(
                                            discountText,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Color(0xFF1e4db7),
                                              fontWeight: FontWeight.w500,
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        coupon['description'] ?? '',
                                        style: TextStyle(
                                          fontSize: 11,
                                          color: Colors.grey.shade600,
                                        ),
                                      ),
                                      if (coupon['min_order_amount'] != null &&
                                          coupon['min_order_amount'] > 0)
                                        Padding(
                                          padding:
                                              const EdgeInsets.only(top: 4),
                                          child: Text(
                                            'Min. order: ₱${coupon['min_order_amount']}',
                                            style: TextStyle(
                                              fontSize: 10,
                                              color: Colors.grey.shade500,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    )
                  else
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Center(
                        child: Text(
                          'No coupons available',
                          style: TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ),
                    ),
                ],
              ),
            const SizedBox(height: 8),

            // Discount Display
            if (cappedDiscount > 0)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Flexible(
                    child: Text(
                      'Discount',
                      style: TextStyle(color: Color(0xFF1e4db7)),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Flexible(
                    child: Text(
                      '-₱${cappedDiscount.toStringAsFixed(2)}',
                      style: const TextStyle(color: Color(0xFF1e4db7)),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            if (cappedDiscount > 0) const SizedBox(height: 8),

            // Delivery Fee
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Flexible(
                  child: Row(
                    children: [
                      Icon(Icons.local_shipping, size: 16),
                      SizedBox(width: 4),
                      Flexible(
                        child: Text(
                          'Delivery Fee',
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                Flexible(
                  child: Text(
                    '₱${_deliveryFee.toStringAsFixed(2)}',
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),

            // Total
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Flexible(
                    child: Text(
                      'Total Amount',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Flexible(
                    child: Text(
                      '₱${total.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1e4db7),
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Estimated Delivery
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: const Row(
                children: [
                  Icon(Icons.local_shipping, color: Colors.blue, size: 20),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Estimated delivery: 3-5 business days',
                      style: TextStyle(fontSize: 12, color: Colors.blue),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPaymentMethodOption(
    String value,
    String title,
    IconData icon,
    String subtitle,
  ) {
    final isSelected = _paymentMethod == value;
    return InkWell(
      onTap: () {
        setState(() {
          _paymentMethod = value;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF1e4db7).withValues(alpha: 0.05)
              : Colors.grey.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color(0xFF1e4db7) : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color:
                    isSelected ? const Color(0xFF1e4db7) : Colors.grey.shade300,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                color: isSelected ? Colors.white : Colors.grey.shade700,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color:
                          isSelected ? const Color(0xFF1e4db7) : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              const Icon(
                Icons.check_circle,
                color: Color(0xFF1e4db7),
                size: 24,
              ),
          ],
        ),
      ),
    );
  }
}

class OrderConfirmationScreen extends StatelessWidget {
  final Order order;

  const OrderConfirmationScreen({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    final deliveryFee = order.deliveryFee ?? order.shippingFee;
    final cappedDiscount =
        order.discount > order.subtotal ? order.subtotal : order.discount;
    final subtotalAfterDiscount = order.subtotal - cappedDiscount;
    final total = subtotalAfterDiscount + deliveryFee;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Order Confirmation'),
        automaticallyImplyLeading: false,
        backgroundColor: const Color(0xFF1a2f6b),
        elevation: 0,
        centerTitle: true,
        titleTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Success Header
              const Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.check_circle,
                      color: Color(0xFF1e4db7),
                      size: 100,
                    ),
                    SizedBox(height: 20),
                    Text(
                      'Order Confirmed!',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1e4db7),
                      ),
                    ),
                    SizedBox(height: 10),
                    Text(
                      'Thank you for your purchase. Your order has been placed successfully.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              // Order ID Badge
              Center(
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Order #${order.id}',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Order Details Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Tracking Number & Status
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          if (order.trackingNumber != null)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade100,
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.qr_code,
                                      size: 14, color: Color(0xFF1e4db7)),
                                  const SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      order.trackingNumber!,
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w600,
                                        fontSize: 11,
                                        color: Color(0xFF1e4db7),
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.blue.shade100,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.access_time,
                                    size: 14, color: Colors.blue.shade700),
                                const SizedBox(width: 4),
                                Flexible(
                                  child: Text(
                                    order.status,
                                    style: TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 11,
                                      color: Colors.blue.shade700,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Shipping Address
                      _buildInfoSection(
                        Icons.location_on,
                        'Shipping Address',
                        order.shippingAddress,
                      ),
                      const SizedBox(height: 12),
                      // Payment Method
                      _buildInfoSection(
                        Icons.payment,
                        'Payment Method',
                        order.paymentMethod,
                      ),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 16),
                      // Items
                      const Text(
                        'Items Ordered',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1e4db7),
                        ),
                      ),
                      const SizedBox(height: 12),
                      ...order.items.map((item) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade50,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          item.productName,
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w600,
                                            fontSize: 14,
                                          ),
                                        ),
                                        Text(
                                          'Qty: ${item.quantity} × ₱${item.price.toStringAsFixed(2)}',
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey.shade600,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Text(
                                    '₱${(item.price * item.quantity).toStringAsFixed(2)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                      color: Color(0xFF1e4db7),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          )),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 16),
                      // Order Summary
                      const Text(
                        'Order Summary',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1e4db7),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Subtotal'),
                          Text('₱${order.subtotal.toStringAsFixed(2)}'),
                        ],
                      ),
                      const SizedBox(height: 8),
                      if (order.discount > 0)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('Discount',
                                style: TextStyle(color: Colors.green)),
                            Text('-₱${order.discount.toStringAsFixed(2)}',
                                style: const TextStyle(color: Colors.green)),
                          ],
                        ),
                      if (order.discount > 0) const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Delivery Fee'),
                          Text('₱${deliveryFee.toStringAsFixed(2)}'),
                        ],
                      ),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 16),
                      // Total
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [
                              Color(0xFFEFF6FF),
                              Color(0xFFDBEAFE),
                            ],
                          ),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blue.shade200),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Flexible(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Total Amount',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    'Including all fees',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Flexible(
                              child: Text(
                                '₱${total.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1e4db7),
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // Next Steps
              Card(
                elevation: 0,
                color: const Color(0xFFEFF6FF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: BorderSide(color: Colors.blue.shade200),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'What\'s Next?',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildNextStep(Icons.email, 'Email confirmation sent'),
                      _buildNextStep(
                          Icons.settings, 'Processing: 1-2 business days'),
                      _buildNextStep(
                          Icons.local_shipping, 'Delivery: 3-5 business days'),
                      if (order.paymentMethod.toLowerCase() == 'cod')
                        _buildNextStep(
                            Icons.attach_money, 'Prepare exact payment'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.popUntil(context, (route) => route.isFirst);
                      },
                      icon: const Icon(Icons.shopping_bag, size: 18),
                      label: const Text('Continue',
                          style: TextStyle(fontSize: 13)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1e4db7),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(25),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.popUntil(context, (route) => route.isFirst);
                        // Navigate to orders screen
                      },
                      icon: const Icon(Icons.list, size: 18),
                      label: const Text('My Orders',
                          style: TextStyle(fontSize: 13)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF1e4db7),
                        side: const BorderSide(color: Color(0xFF1e4db7)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(25),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoSection(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: const Color(0xFF1e4db7)),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildNextStep(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: const Color(0xFF1e4db7)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }
}
