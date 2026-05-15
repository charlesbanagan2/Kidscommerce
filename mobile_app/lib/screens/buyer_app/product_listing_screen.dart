import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../widgets/product_card_widget.dart';
import '../../widgets/skeleton_loader.dart';
import 'cart_screen.dart';
import 'product_detail_screen.dart';

/// Mobile Product Listing Screen with product cards and images
class ProductListingScreen extends StatefulWidget {
  const ProductListingScreen({super.key});

  @override
  State<ProductListingScreen> createState() => _ProductListingScreenState();
}

class _ProductListingScreenState extends State<ProductListingScreen> {
  late TextEditingController _searchController;
  final Set<int> _addingProductIds = {};

  bool _isTablet(double width) => width >= 700;
  bool _isSmallPhone(double width) => width < 360;

  double _gridAspectRatio(double width) {
    if (_isTablet(width)) {
      return 0.74;
    }
    if (_isSmallPhone(width)) {
      return 0.57;
    }
    return 0.64;
  }

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;
    final isTablet = _isTablet(screenWidth);
    final productColumns = isTablet ? 3 : 2;

    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Browse Products'),
        elevation: 0,
        backgroundColor: Colors.purple.shade600,
        centerTitle: true,
      ),
      body: Consumer<BuyerProvider>(
        builder: (context, provider, _) {
          // Fetch products if not already loaded
          if (provider.products.isEmpty && !provider.isLoading) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              provider.fetchProducts();
            });
          }

          return SingleChildScrollView(
            child: Column(
              children: [
                // Search bar
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: TextField(
                    controller: _searchController,
                    onChanged: (query) {
                      provider.searchProducts(query);
                    },
                    decoration: InputDecoration(
                      hintText: 'Search products...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                          vertical: 10, horizontal: 12),
                    ),
                  ),
                ),

                // Loading state
                if (provider.isLoading)
                  GridSkeletonLoader(
                    crossAxisCount: productColumns,
                    childAspectRatio: _gridAspectRatio(screenWidth),
                    itemCount: 6,
                    padding: const EdgeInsets.all(12),
                  )
                // Empty state
                else if (provider.products.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.shopping_bag_outlined,
                            size: 64,
                            color: Colors.grey.shade300,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No products found',
                            style: TextStyle(
                              color: Colors.grey.shade600,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Try adjusting your search',
                            style: TextStyle(
                              color: Colors.grey.shade500,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                // Product grid
                else
                  GridView.builder(
                    padding: const EdgeInsets.all(12),
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: productColumns,
                      childAspectRatio: _gridAspectRatio(screenWidth),
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                    ),
                    itemCount: provider.products.length,
                    itemBuilder: (context, index) {
                      final product = provider.products[index];
                      return ProductCardWidget(
                        product: product,
                        onProductClick: (product) {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  ProductDetailScreen(product: product),
                            ),
                          );
                        },
                        onAddToCart: (product) async {
                          final productId = product.id as int?;
                          if (productId == null ||
                              _addingProductIds.contains(productId)) {
                            return false;
                          }
                          setState(() {
                            _addingProductIds.add(productId);
                          });
                          final buyerProvider = context.read<BuyerProvider>();
                          final success =
                              await buyerProvider.addProductToCart(product);
                          if (!mounted) return false;
                          if (success) {
                            await buyerProvider.fetchCart();
                            if (!mounted) return false;
                            _showCartSnack(
                              '${product.name} added to cart',
                              isError: false,
                            );
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const CartScreen(),
                              ),
                            );
                            setState(() {
                              _addingProductIds.remove(productId);
                            });
                            return true;
                          } else {
                            _showCartSnack(
                              _friendlyCartMessage(buyerProvider.errorMessage),
                              isError: true,
                            );
                            setState(() {
                              _addingProductIds.remove(productId);
                            });
                            return false;
                          }
                        },
                      );
                    },
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _showCartSnack(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }

  String _friendlyCartMessage(String? rawMessage) {
    final message = (rawMessage ?? '').toLowerCase();
    if (message.contains('404')) {
      return 'Service unavailable. Please try again later.';
    }
    if (message.contains('network') ||
        message.contains('socket') ||
        message.contains('connection')) {
      return 'Check your internet connection.';
    }
    if (message.contains('timeout')) {
      return 'Request timeout. Please try again.';
    }
    if (message.contains('login') || message.contains('auth')) {
      return 'Please log in again.';
    }
    return 'Could not add to cart. Please try again.';
  }
}
