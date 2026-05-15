import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/modern_snackbar.dart';
import '../../config/url_config.dart';
import 'product_detail_screen.dart';

class LikedProductsScreen extends StatefulWidget {
  const LikedProductsScreen({super.key});

  @override
  State<LikedProductsScreen> createState() => _LikedProductsScreenState();
}

class _LikedProductsScreenState extends State<LikedProductsScreen> {
  bool _isLoading = false;

  static const _primaryBlue = Color(0xFF1e4db7);
  static const _darkBlue = Color(0xFF1a2f6b);
  static const _bgColor = Color(0xFFF0F4FB);

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchLikedProducts();
    });
  }

  Future<void> _fetchLikedProducts() async {
    setState(() => _isLoading = true);
    try {
      final buyerProvider = context.read<BuyerProvider>();
      await buyerProvider.fetchWishlist();
      debugPrint('✅ Liked products fetched: ${buyerProvider.wishlistProducts.length}');
    } catch (e) {
      debugPrint('Error fetching liked products: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleLike(int productId) async {
    final authProvider = context.read<AuthProvider>();
    if (!authProvider.isAuthenticated) {
      ModernSnackBar.showError(context, 'Please log in to like products');
      return;
    }

    final buyerProvider = context.read<BuyerProvider>();
    final success = await buyerProvider.toggleWishlist(productId);

    if (mounted) {
      if (success) {
        final isLiked = buyerProvider.isProductLiked(productId);
        ModernSnackBar.show(
          context,
          message: isLiked
              ? 'Added to liked products'
              : 'Removed from liked products',
        );
      } else {
        ModernSnackBar.showError(
          context,
          buyerProvider.errorMessage ?? 'Failed to update liked products',
        );
      }
    }
  }

  void _navigateToProductDetail(dynamic product) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProductDetailScreen(product: product),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgColor,
      body: Column(
        children: [
          // Header with gradient - consistent with cart/orders
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [_darkBlue, _primaryBlue],
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
                        'Liked Products',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Consumer<BuyerProvider>(
                        builder: (context, buyerProvider, child) {
                          return Text(
                            '${buyerProvider.wishlistProducts.length} saved item${buyerProvider.wishlistProducts.length == 1 ? '' : 's'}',
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.7),
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
                if (_isLoading)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                else
                  IconButton(
                    icon:
                        const Icon(LucideIcons.refreshCw, color: Colors.white),
                    onPressed: _fetchLikedProducts,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    iconSize: 18,
                  ),
              ],
            ),
          ),
          Expanded(
            child: Consumer<BuyerProvider>(
              builder: (context, buyerProvider, child) {
                final likedProducts = buyerProvider.wishlistProducts;
                return _isLoading && likedProducts.isEmpty
                    ? const Center(
                        child: CircularProgressIndicator(
                          valueColor:
                              AlwaysStoppedAnimation<Color>(_primaryBlue),
                        ),
                      )
                    : likedProducts.isEmpty
                        ? _buildEmptyState()
                        : RefreshIndicator(
                            onRefresh: _fetchLikedProducts,
                            color: _primaryBlue,
                            child: GridView.builder(
                              padding:
                                  const EdgeInsets.fromLTRB(16, 20, 16, 32),
                              gridDelegate:
                                  const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                                childAspectRatio: 0.64,
                              ),
                              itemCount: likedProducts.length,
                              itemBuilder: (context, index) {
                                final product = likedProducts[index];
                                return _buildProductCard(
                                    product, buyerProvider);
                              },
                            ),
                          );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                shape: BoxShape.circle,
              ),
              child: Icon(
                LucideIcons.heart,
                size: 44,
                color: Colors.red.shade300,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'No liked products yet',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Start adding products you love\nto see them here',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade500,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 28),
            ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(LucideIcons.shoppingBag, size: 16),
              label: const Text('Browse Products'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _primaryBlue,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                elevation: 0,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductCard(dynamic product, BuyerProvider buyerProvider) {
    final isLiked = buyerProvider.isProductLiked(product.id);
    final inStock = product.stock > 0;

    return GestureDetector(
      onTap: () => _navigateToProductDetail(product),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 3,
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(18),
                      topRight: Radius.circular(18),
                    ),
                    child:
                        product.imageUrl != null && product.imageUrl!.isNotEmpty
                            ? Image.network(
                                UrlConfig.toAbsoluteImageUrl(product.imageUrl!),
                                fit: BoxFit.cover,
                                width: double.infinity,
                                height: double.infinity,
                                errorBuilder: (context, error, stackTrace) =>
                                    Container(
                                  color: Colors.grey.shade100,
                                  child: Center(
                                    child: Icon(LucideIcons.imageOff,
                                        color: Colors.grey.shade400, size: 32),
                                  ),
                                ),
                              )
                            : Container(
                                color: Colors.grey.shade100,
                                child: Center(
                                  child: Icon(LucideIcons.image,
                                      color: Colors.grey.shade400, size: 32),
                                ),
                              ),
                  ),
                  if (!inStock)
                    ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(18),
                        topRight: Radius.circular(18),
                      ),
                      child: Container(
                        color: Colors.black.withValues(alpha: 0.03),
                        child: const Center(
                          child: Text(
                            'Out of Stock',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: GestureDetector(
                      onTap: () => _toggleLike(product.id),
                      child: Container(
                        width: 34,
                        height: 34,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.1),
                              blurRadius: 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Center(
                          child: Icon(
                            isLiked
                                ? Icons.favorite_rounded
                                : Icons.favorite_border_rounded,
                            size: 17,
                            color: isLiked ? Colors.red : Colors.grey.shade400,
                          ),
                        ),
                      ),
                    ),
                  ),
                  if (product.discountPercent != null &&
                      product.discountPercent! > 0)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 7, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '-${product.discountPercent}%',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                        height: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '\₱${product.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        color: _primaryBlue,
                      ),
                    ),
                    const Spacer(),
                    Row(
                      children: [
                        Container(
                          width: 7,
                          height: 7,
                          decoration: BoxDecoration(
                            color: inStock
                                ? Colors.green.shade400
                                : Colors.red.shade400,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: Text(
                            inStock ? 'Stock ${product.stock}' : 'Out of stock',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w500,
                              color: inStock
                                  ? Colors.green.shade600
                                  : Colors.red.shade400,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            GestureDetector(
              onTap: () => _navigateToProductDetail(product),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [_darkBlue, _primaryBlue],
                  ),
                  borderRadius: BorderRadius.only(
                    bottomLeft: Radius.circular(18),
                    bottomRight: Radius.circular(18),
                  ),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'View Product',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(LucideIcons.arrowRight, color: Colors.white, size: 13),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
