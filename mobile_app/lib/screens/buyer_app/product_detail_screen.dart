import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../config/url_config.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/modern_snackbar.dart';
import '../../services/api_service.dart';
import 'checkout_screen.dart';
import 'product_reviews_screen.dart';
import 'store_detail_screen.dart';
import 'product_chat_screen.dart';

class ProductDetailScreen extends StatefulWidget {
  final dynamic product;
  const ProductDetailScreen({required this.product, super.key});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen>
    with SingleTickerProviderStateMixin {
  int _quantity = 1;
  bool _showFullDescription = false;
  int _selectedImageIndex = 0;
  bool _isBottomBarLoading = false;
  bool _isBuyAction = false;
  final Set<int> _addingProductIds = {};
  late ScrollController _scrollController;
  List<Map<String, dynamic>> _reviews = [];
  bool _isLoadingReviews = false;
  double _averageRating = 0.0;
  int _reviewCount = 0;

  // Theme
  static const Color _primaryDark = Color(0xFF1a2f6b);
  static const Color _primary = Color(0xFF1e4db7);
  static const Color _primaryLight = Color(0xFF3B6FE0);
  static const Color _bgColor = Color(0xFFF4F6FC);
  static const Color _textDark = Color(0xFF1A1F36);
  static const Color _textMid = Color(0xFF6B7280);

  bool _isTablet(double width) => width >= 700;
  bool _isSmallPhone(double width) => width < 360;

  double _gridAspectRatio(double width) {
    if (_isTablet(width)) return 0.74;
    if (_isSmallPhone(width)) return 0.57;
    return 0.64;
  }

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    _fetchProductReviews();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        final buyerProvider = context.read<BuyerProvider>();
        buyerProvider.fetchWishlist();
      }
    });
  }

  Future<void> _fetchProductReviews() async {
    setState(() => _isLoadingReviews = true);
    try {
      final result = await ApiService.getProductReviews(widget.product.id);
      if (mounted) {
        setState(() {
          _reviews = (result['reviews'] as List? ?? [])
              .map((e) => (e as Map).cast<String, dynamic>())
              .toList();
          _averageRating = ((result['average_rating'] as num?) ?? 0).toDouble();
          _reviewCount = (result['review_count'] as num?)?.toInt() ?? 0;
          _isLoadingReviews = false;
        });
      }
    } catch (e) {
      debugPrint('Error fetching reviews: $e');
      if (mounted) setState(() => _isLoadingReviews = false);
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _toggleLike() async {
    final buyerProvider = context.read<BuyerProvider>();
    final productId = widget.product.id;
    final authProvider = context.read<AuthProvider>();
    if (!authProvider.isAuthenticated) {
      ModernSnackBar.showError(context, 'Please log in to like products');
      return;
    }
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

  // ─── Open Product Chat ────────────────────────────────────────────────────
  Future<void> _openProductChat() async {
    final authProvider = context.read<AuthProvider>();
    if (!authProvider.isAuthenticated) {
      ModernSnackBar.showError(context, 'Please log in to message the seller');
      return;
    }

    // Check if we have seller info
    if (widget.product.sellerId == null) {
      ModernSnackBar.showError(context, 'Seller information not available');
      return;
    }

    try {
      // Start product chat with seller
      final response = await ApiService.startProductChat(
        productId: widget.product.id,
        message: 'Hi! I\'m interested in ${widget.product.name}',
      );

      if (response['success'] == true && mounted) {
        // Navigate to product chat screen with product context
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductChatScreen(
              productId: widget.product.id,
              productName: widget.product.name,
              productImage: widget.product.imageUrl ?? '',
              productPrice: widget.product.price.toDouble(),
              sellerId: widget.product.sellerId!,
              sellerName: widget.product.storeName ??
                  widget.product.sellerName ??
                  'Seller',
              sellerAvatar: widget.product.storeLogo,
            ),
          ),
        );
      } else {
        if (mounted) {
          ModernSnackBar.showError(
            context,
            response['error'] ?? 'Failed to start chat',
          );
        }
      }
    } catch (e) {
      debugPrint('Error opening product chat: $e');
      if (mounted) {
        ModernSnackBar.showError(
            context, 'Failed to open chat. Please try again.');
      }
    }
  }

  // ─── Add to Cart / Buy Now Sheet ──────────────────────────────────────────
  void _showCartSheet({required bool isBuyNow}) {
    final images = _getImages();
    final mainImage = images.isNotEmpty ? images[0] : '';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setSheet) {
          int qty = _quantity;
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
            ),
            padding: EdgeInsets.only(
              bottom: MediaQuery.of(context).viewInsets.bottom + 24,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Handle
                Container(
                  margin: const EdgeInsets.only(top: 12, bottom: 0),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),

                // Product mini header
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Small product image
                      Container(
                        width: 90,
                        height: 90,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: Colors.grey.shade200, width: 1.5),
                          color: Colors.grey.shade100,
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(14),
                          child: mainImage.isNotEmpty
                              ? Image.network(
                                  mainImage,
                                  fit: BoxFit.cover,
                                  errorBuilder: (_, __, ___) => Icon(
                                    LucideIcons.image,
                                    color: Colors.grey.shade400,
                                  ),
                                )
                              : Icon(LucideIcons.image,
                                  color: Colors.grey.shade400),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Price
                            Text(
                              '₱${widget.product.price.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.w900,
                                color: _primary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            // Product name
                            Text(
                              widget.product.name ?? '',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: _textDark,
                                height: 1.3,
                              ),
                            ),
                            const SizedBox(height: 6),
                            // Stock
                            Row(
                              children: [
                                Icon(LucideIcons.package,
                                    size: 12, color: Colors.grey.shade500),
                                const SizedBox(width: 4),
                                Text(
                                  widget.product.stock > 0
                                      ? '${widget.product.stock} in stock'
                                      : 'Out of stock',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: widget.product.stock > 0
                                        ? const Color(0xFF16A34A)
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: Container(
                          width: 30,
                          height: 30,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(LucideIcons.x,
                              size: 16, color: _textMid),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),
                Divider(height: 1, color: Colors.grey.shade100),
                const SizedBox(height: 20),

                // Quantity selector
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Quantity',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: _textDark,
                        ),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: _bgColor,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Row(
                          children: [
                            _qtyButton(
                              icon: LucideIcons.minus,
                              onTap: qty > 1
                                  ? () => setSheet(() {
                                        qty--;
                                        _quantity = qty;
                                      })
                                  : null,
                            ),
                            SizedBox(
                              width: 40,
                              child: Center(
                                child: Text(
                                  '$qty',
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w800,
                                    color: _textDark,
                                  ),
                                ),
                              ),
                            ),
                            _qtyButton(
                              icon: LucideIcons.plus,
                              onTap: qty < widget.product.stock
                                  ? () => setSheet(() {
                                        qty++;
                                        _quantity = qty;
                                      })
                                  : null,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Action button
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: isBuyNow
                        ? Container(
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [_primaryDark, _primaryLight],
                                begin: Alignment.centerLeft,
                                end: Alignment.centerRight,
                              ),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(16),
                                onTap: () {
                                  Navigator.pop(context);
                                  _handleCartAction(
                                    goToCart: false,
                                    goToCheckout: true,
                                  );
                                },
                                child: const Center(
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(LucideIcons.zap,
                                          color: Colors.white, size: 18),
                                      SizedBox(width: 8),
                                      Text(
                                        'Buy Now',
                                        style: TextStyle(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w800,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          )
                        : ElevatedButton(
                            onPressed: () {
                              Navigator.pop(context);
                              _handleCartAction(
                                goToCart: true,
                                goToCheckout: false,
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.black,
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(LucideIcons.shoppingCart,
                                    size: 18, color: Colors.white),
                                SizedBox(width: 8),
                                Text(
                                  'Add to Cart',
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w800,
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
        },
      ),
    );
  }

  Widget _qtyButton({required IconData icon, VoidCallback? onTap}) {
    final enabled = onTap != null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: enabled ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          boxShadow: enabled
              ? [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.06),
                    blurRadius: 4,
                    offset: const Offset(0, 1),
                  )
                ]
              : null,
        ),
        child: Icon(
          icon,
          size: 16,
          color: enabled ? _primary : Colors.grey.shade400,
        ),
      ),
    );
  }

  List<String> _getImages() {
    final images = <String>[];
    if (widget.product.imageUrl != null &&
        widget.product.imageUrl!.isNotEmpty) {
      images.add(UrlConfig.toAbsoluteImageUrl(widget.product.imageUrl!));
    }
    if (widget.product.images != null && widget.product.images!.isNotEmpty) {
      images.addAll(UrlConfig.toAbsoluteImageUrls(widget.product.images!));
    }
    if (images.isEmpty) {
      images.add(UrlConfig.toAbsoluteImageUrl('placeholder.png'));
    }
    return images;
  }

  @override
  Widget build(BuildContext context) {
    final inStock = widget.product.stock > 0;
    return Scaffold(
      backgroundColor: _bgColor,
      body: Stack(
        children: [
          SingleChildScrollView(
            controller: _scrollController,
            padding: const EdgeInsets.only(bottom: 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildImageGallery(),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildProductInfo(),
                ),
                const SizedBox(height: 10),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildStoreSection(),
                ),
                const SizedBox(height: 10),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildDescriptionSection(),
                ),
                const SizedBox(height: 10),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildRatingsPreview(),
                ),
                const SizedBox(height: 10),
                _buildYouMayAlsoLike(),
                const SizedBox(height: 40),
              ],
            ),
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _buildStickyBottomBar(inStock),
          ),
        ],
      ),
    );
  }

  // ─── Image Gallery ────────────────────────────────────────────────────────
  Widget _buildImageGallery() {
    final images = _getImages();
    return Container(
      color: Colors.white,
      child: Column(
        children: [
          Stack(
            children: [
              // Main image
              AspectRatio(
                aspectRatio: 1.0,
                child: Container(
                  width: double.infinity,
                  color: Colors.grey.shade50,
                  child: Image.network(
                    images[_selectedImageIndex],
                    fit: BoxFit.contain,
                    errorBuilder: (context, error, stackTrace) => Icon(
                      Icons.image,
                      size: 80,
                      color: Colors.grey.shade300,
                    ),
                  ),
                ),
              ),

              // Top gradient overlay
              Positioned(
                top: 0,
                left: 0,
                right: 0,
                height: 120,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.black.withValues(alpha: 0.3),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),

              // Top actions
              Positioned(
                top: MediaQuery.of(context).padding.top + 10,
                left: 16,
                right: 16,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _circleButton(
                        LucideIcons.arrowLeft, () => Navigator.pop(context)),
                    Row(
                      children: [
                        _circleButton(LucideIcons.share2, () {}),
                        const SizedBox(width: 10),
                        _circleButton(
                          LucideIcons.heart,
                          () => _toggleLike(),
                          color: context
                                  .watch<BuyerProvider>()
                                  .isProductLiked(widget.product.id)
                              ? Colors.red
                              : null,
                          fill: context
                              .watch<BuyerProvider>()
                              .isProductLiked(widget.product.id),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Discount badge
              if (widget.product.discountPercent != null &&
                  widget.product.discountPercent! > 0)
                Positioned(
                  bottom: 14,
                  left: 16,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.red.shade600,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.red.withValues(alpha: 0.3),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Text(
                      "-${widget.product.discountPercent}% OFF",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.3,
                      ),
                    ),
                  ),
                ),

              // Image counter badge (top-right of image)
              if (images.length > 1)
                Positioned(
                  bottom: 14,
                  right: 16,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.45),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '${_selectedImageIndex + 1}/${images.length}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
            ],
          ),

          // Thumbnail strip
          if (images.length > 1)
            Container(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
              color: Colors.white,
              child: SizedBox(
                height: 60,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: images.length,
                  itemBuilder: (context, index) => GestureDetector(
                    onTap: () => setState(() => _selectedImageIndex = index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      margin: const EdgeInsets.only(right: 8),
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _selectedImageIndex == index
                              ? _primary
                              : Colors.grey.shade200,
                          width: _selectedImageIndex == index ? 2 : 1.5,
                        ),
                        boxShadow: _selectedImageIndex == index
                            ? [
                                BoxShadow(
                                  color: _primary.withValues(alpha: 0.2),
                                  blurRadius: 6,
                                  offset: const Offset(0, 2),
                                )
                              ]
                            : null,
                        image: DecorationImage(
                          image: NetworkImage(images[index]),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ─── Product Info ─────────────────────────────────────────────────────────
  Widget _buildProductInfo() => Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Price row
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  '₱${widget.product.price.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w900,
                    color: _primary,
                    letterSpacing: -0.5,
                  ),
                ),
                const Spacer(),
                if (widget.product.stock > 0)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF16A34A).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: const BoxDecoration(
                            color: Color(0xFF16A34A),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 5),
                        Text(
                          '${widget.product.stock} in stock',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF16A34A),
                          ),
                        ),
                      ],
                    ),
                  )
                else
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text(
                      'Out of Stock',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: Colors.red,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),

            // Product name
            Text(
              widget.product.name,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: _textDark,
                height: 1.35,
              ),
            ),
            const SizedBox(height: 12),

            // Divider
            Divider(height: 1, color: Colors.grey.shade100),
            const SizedBox(height: 12),

            // Rating row
            Row(
              children: [
                // Stars
                Row(
                  children: List.generate(5, (index) {
                    final filled = index < widget.product.rating.round();
                    return Icon(
                      LucideIcons.star,
                      color: filled ? Colors.amber : Colors.grey.shade300,
                      size: 15,
                      fill: filled ? 0.8 : 0,
                    );
                  }),
                ),
                const SizedBox(width: 8),
                Text(
                  widget.product.rating.toStringAsFixed(1),
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: _textDark,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  '(${widget.product.reviewCount} reviews)',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade500,
                  ),
                ),
              ],
            ),
          ],
        ),
      );

  // ─── Store Section ────────────────────────────────────────────────────────
  Widget _buildStoreSection() => Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            // Store avatar
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  colors: [_primaryDark, _primaryLight],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: _primary.withValues(alpha: 0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ClipOval(
                child: widget.product.storeLogo != null
                    ? Image.network(
                        widget.product.storeLogo!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const Icon(
                          LucideIcons.store,
                          color: Colors.white,
                          size: 22,
                        ),
                      )
                    : const Icon(LucideIcons.store,
                        color: Colors.white, size: 22),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.product.storeName ??
                        widget.product.sellerName ??
                        'Unknown Store',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: _textDark,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: _primary.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text(
                          'Official Store',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            color: _primary,
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      const Icon(LucideIcons.star,
                          size: 11, color: Colors.amber, fill: 0.8),
                      const SizedBox(width: 3),
                      Text(
                        '${widget.product.rating}',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            GestureDetector(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => StoreDetailScreen(
                    sellerId: widget.product.sellerId,
                    storeName: widget.product.storeName ?? 'Store',
                    storeLogo: widget.product.storeLogo,
                    storeBackground: null,
                    storeRating: widget.product.rating,
                    followersCount: 0,
                  ),
                ),
              ),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [_primaryDark, _primaryLight],
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: _primary.withValues(alpha: 0.3),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: const Text(
                  'Visit Shop',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      );

  // ─── Description ──────────────────────────────────────────────────────────
  Widget _buildDescriptionSection() => Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 4,
                  height: 18,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [_primaryDark, _primaryLight],
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                    ),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 10),
                const Text(
                  'Product Description',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: _textDark,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              widget.product.description
                      ?.replaceAll('\\r', '')
                      .replaceAll('\\n', ' ')
                      .trim() ??
                  'No description available',
              maxLines: _showFullDescription ? null : 4,
              overflow: _showFullDescription
                  ? TextOverflow.visible
                  : TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade700,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 10),
            GestureDetector(
              onTap: () =>
                  setState(() => _showFullDescription = !_showFullDescription),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                decoration: BoxDecoration(
                  color: _primary.withValues(alpha: 0.07),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _showFullDescription ? 'Show less' : 'Read more',
                      style: const TextStyle(
                        color: _primary,
                        fontWeight: FontWeight.w700,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      _showFullDescription
                          ? LucideIcons.chevronUp
                          : LucideIcons.chevronDown,
                      size: 14,
                      color: _primary,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      );

  // ─── Ratings Preview ──────────────────────────────────────────────────────
  Widget _buildRatingsPreview() {
    final reviews = _reviews;
    final hasReviews = reviews.isNotEmpty;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Row(
                children: [
                  Container(
                    width: 4,
                    height: 18,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [_primaryDark, _primaryLight],
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                      ),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(width: 10),
                  const Text(
                    'Ratings & Reviews',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: _textDark,
                    ),
                  ),
                ],
              ),
              const Spacer(),
              GestureDetector(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ProductReviewsScreen(
                      productId: widget.product.id,
                      productName: widget.product.name,
                    ),
                  ),
                ),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.07),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Text(
                        hasReviews ? 'See All' : 'View',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: _primary,
                        ),
                      ),
                      const SizedBox(width: 2),
                      const Icon(LucideIcons.chevronRight,
                          size: 14, color: _primary),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Rating summary bar
          if (_reviewCount > 0) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _bgColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  Column(
                    children: [
                      Text(
                        _averageRating.toStringAsFixed(1),
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.w900,
                          color: _textDark,
                          height: 1,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: List.generate(5, (i) {
                          return Icon(
                            LucideIcons.star,
                            size: 13,
                            color: i < _averageRating.floor()
                                ? Colors.amber
                                : Colors.grey.shade300,
                            fill: i < _averageRating.floor() ? 0.8 : 0,
                          );
                        }),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '$_reviewCount reviews',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.grey.shade500,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      children: List.generate(5, (i) {
                        final starNum = 5 - i;
                        final count = reviews
                            .where((r) =>
                                (r['rating'] as num?)?.toInt() == starNum)
                            .length;
                        final ratio =
                            _reviewCount > 0 ? count / _reviewCount : 0.0;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Row(
                            children: [
                              Text(
                                '$starNum',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                              const SizedBox(width: 4),
                              const Icon(LucideIcons.star,
                                  size: 10, color: Colors.amber, fill: 0.8),
                              const SizedBox(width: 6),
                              Expanded(
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: ratio,
                                    minHeight: 6,
                                    backgroundColor: Colors.grey.shade200,
                                    valueColor:
                                        const AlwaysStoppedAnimation<Color>(
                                            Colors.amber),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          if (!hasReviews)
            Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 24),
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: _bgColor,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Icon(LucideIcons.messageSquare,
                          size: 32, color: Colors.grey.shade400),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _isLoadingReviews ? 'Loading reviews…' : 'No reviews yet',
                      style: const TextStyle(
                        color: _textDark,
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Be the first to review this product',
                      style: TextStyle(
                        color: Colors.grey.shade400,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            ...reviews.take(1).map(
                  (review) => _buildReviewCard(
                    name: review['buyer_name'] ??
                        review['user_name'] ??
                        'Anonymous',
                    rating: (review['rating'] as num?)?.toInt() ?? 5,
                    date: review['created_at'] ?? 'Unknown',
                    title: review['title'] ?? '',
                    review: review['content'] ?? '',
                    media: review['media'] ?? const [],
                    helpful: 0,
                    unhelpful: 0,
                    userAvatar: review['buyer_avatar'] ?? review['user_avatar'],
                    categoryRatings: review['category_ratings'] as String?,
                  ),
                ),
        ],
      ),
    );
  }

  Widget _buildReviewCard({
    required String name,
    required int rating,
    required String date,
    required String title,
    required String review,
    required List<dynamic> media,
    required int helpful,
    required int unhelpful,
    String? userAvatar,
    String? categoryRatings,
  }) =>
      Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: _bgColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.shade100),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                userAvatar != null && userAvatar.isNotEmpty
                    ? Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: _primary, width: 1.5),
                        ),
                        child: ClipOval(
                          child: Image.network(
                            UrlConfig.toAbsoluteImageUrl(userAvatar),
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => Container(
                              color: _primary,
                              child: Center(
                                child: Text(
                                  name.isNotEmpty ? name[0].toUpperCase() : 'A',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      )
                    : Container(
                        width: 36,
                        height: 36,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            colors: [_primaryDark, _primaryLight],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            name.isNotEmpty ? name[0].toUpperCase() : 'A',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                        ),
                      ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: _textDark,
                        ),
                      ),
                      Text(
                        date.toString().split('T').first,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
                Row(
                  children: List.generate(5, (index) {
                    return Icon(
                      LucideIcons.star,
                      color:
                          index < rating ? Colors.amber : Colors.grey.shade300,
                      size: 13,
                      fill: index < rating ? 0.8 : 0,
                    );
                  }),
                ),
              ],
            ),
            if (categoryRatings != null && categoryRatings.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  categoryRatings,
                  style: TextStyle(
                    fontSize: 10,
                    color: Colors.grey.shade700,
                  ),
                ),
              ),
            ],
            if (title.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                  color: _textDark,
                ),
              ),
            ],
            if (review.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                review,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  height: 1.5,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
            if (media.isNotEmpty) ...[
              const SizedBox(height: 10),
              SizedBox(
                height: 64,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: media.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 6),
                  itemBuilder: (context, index) {
                    final item = (media[index] as Map).cast<String, dynamic>();
                    final type = (item['type'] ?? '').toString().toLowerCase();
                    final path = (item['path'] ?? '').toString();
                    if (path.isEmpty) return const SizedBox.shrink();
                    final url = path.startsWith('http')
                        ? path
                        : '${UrlConfig.baseUrl}$path';
                    if (type == 'video') {
                      return Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Center(
                          child: Icon(Icons.play_circle_fill,
                              color: Colors.white, size: 28),
                        ),
                      );
                    }
                    return ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: Image.network(
                        url,
                        width: 64,
                        height: 64,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          width: 64,
                          height: 64,
                          color: Colors.grey.shade200,
                          child: Icon(LucideIcons.image,
                              color: Colors.grey.shade400),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      );

  // ─── You May Also Like ────────────────────────────────────────────────────
  Widget _buildYouMayAlsoLike() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Container(
                  width: 4,
                  height: 18,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [_primaryDark, _primaryLight],
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                    ),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 10),
                const Text(
                  'You May Also Like',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: _textDark,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Consumer<BuyerProvider>(
            builder: (context, buyerProvider, _) {
              final screenWidth = MediaQuery.sizeOf(context).width;
              final isTablet = _isTablet(screenWidth);
              final productColumns = isTablet ? 3 : 2;
              final products = buyerProvider.products
                  .where((p) => p.id != widget.product.id)
                  .toList();
              if (products.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    'No other products available',
                    style: TextStyle(color: Colors.grey.shade500),
                  ),
                );
              }
              return GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 16),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: productColumns,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: _gridAspectRatio(screenWidth),
                ),
                itemCount: products.length,
                itemBuilder: (context, index) => _buildModernProductCard(
                    products[index],
                    screenWidth: screenWidth),
              );
            },
          ),
        ],
      );

  Widget _buildModernProductCard(dynamic product,
      {required double screenWidth}) {
    final isTablet = _isTablet(screenWidth);
    final isSmallPhone = _isSmallPhone(screenWidth);
    final imageHeight = isTablet ? 170.0 : (isSmallPhone ? 132.0 : 155.0);
    final nameFont = isTablet ? 13.5 : 12.5;
    final priceFont = isTablet ? 16.0 : 14.0;
    final stockFont = isTablet ? 11.5 : 10.5;
    final buttonPad = isTablet ? 7.0 : 6.0;

    final productId = product.id as int?;
    final isAdding = productId != null && _addingProductIds.contains(productId);

    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProductDetailScreen(product: product),
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 10,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            ClipRRect(
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(16)),
              child: Container(
                height: imageHeight,
                width: double.infinity,
                color: Colors.grey.shade100,
                child: product.imageUrl != null && product.imageUrl!.isNotEmpty
                    ? Image.network(
                        UrlConfig.toAbsoluteImageUrl(product.imageUrl ?? ''),
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Icon(
                          LucideIcons.imageOff,
                          color: Colors.grey.shade400,
                          size: isTablet ? 36 : 30,
                        ),
                      )
                    : Icon(LucideIcons.image,
                        color: Colors.grey.shade400, size: isTablet ? 36 : 30),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      product.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: nameFont,
                        fontWeight: FontWeight.w700,
                        color: _textDark,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '₱${product.displayPrice.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: priceFont,
                        fontWeight: FontWeight.w900,
                        color: _primary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(LucideIcons.package,
                            size: 11, color: Colors.grey.shade500),
                        const SizedBox(width: 3),
                        Expanded(
                          child: Text(
                            product.stock > 0
                                ? 'Stock ${product.stock}'
                                : 'Out of stock',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: stockFont,
                              color: product.stock > 0
                                  ? Colors.grey.shade500
                                  : Colors.red.shade400,
                            ),
                          ),
                        ),
                        GestureDetector(
                          onTap: product.stock > 0
                              ? () async {
                                  if (productId == null || isAdding) return;
                                  setState(
                                      () => _addingProductIds.add(productId));
                                  final buyerProvider =
                                      context.read<BuyerProvider>();
                                  final success = await buyerProvider
                                      .addProductToCart(product);
                                  if (!mounted) return;
                                  if (success) {
                                    await buyerProvider.fetchCart();
                                    if (!mounted) return;
                                    ModernSnackBar.showCartSuccess(
                                        context, product.name);
                                  } else {
                                    ModernSnackBar.showError(
                                      context,
                                      _friendlyCartMessage(
                                          buyerProvider.errorMessage),
                                    );
                                  }
                                  setState(() =>
                                      _addingProductIds.remove(productId));
                                }
                              : null,
                          child: Container(
                            padding: EdgeInsets.all(buttonPad),
                            decoration: BoxDecoration(
                              gradient: product.stock > 0
                                  ? const LinearGradient(
                                      colors: [_primaryDark, _primaryLight],
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                    )
                                  : null,
                              color: product.stock > 0
                                  ? null
                                  : Colors.grey.shade300,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: isAdding
                                ? const SizedBox(
                                    width: 14,
                                    height: 14,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                          Colors.white),
                                    ),
                                  )
                                : const Icon(
                                    LucideIcons.shoppingCart,
                                    size: 14,
                                    color: Colors.white,
                                  ),
                          ),
                        ),
                      ],
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

  // ─── Sticky Bottom Bar ────────────────────────────────────────────────────
  Widget _buildStickyBottomBar(bool inStock) {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.shade100)),
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
        child: Row(
          children: [
            // Chat button
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: _bgColor,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: IconButton(
                icon: Icon(LucideIcons.messageCircle,
                    color: Colors.grey.shade600, size: 20),
                onPressed: () => _openProductChat(),
                padding: EdgeInsets.zero,
              ),
            ),
            const SizedBox(width: 10),

            // Add to Cart
            Expanded(
              child: GestureDetector(
                onTap: inStock && !_isBottomBarLoading
                    ? () => _showCartSheet(isBuyNow: false)
                    : null,
                child: Container(
                  height: 46,
                  decoration: BoxDecoration(
                    color: inStock ? Colors.black : Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: _isBottomBarLoading && !_isBuyAction
                      ? const Center(
                          child: SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                        )
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(LucideIcons.shoppingCart,
                                color: Colors.white, size: 16),
                            SizedBox(width: 6),
                            Text(
                              'Add to Cart',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                ),
              ),
            ),
            const SizedBox(width: 10),

            // Buy Now
            Expanded(
              child: GestureDetector(
                onTap: inStock && !_isBottomBarLoading
                    ? () => _showCartSheet(isBuyNow: true)
                    : null,
                child: Container(
                  height: 46,
                  decoration: BoxDecoration(
                    gradient: inStock
                        ? const LinearGradient(
                            colors: [_primaryDark, _primaryLight],
                            begin: Alignment.centerLeft,
                            end: Alignment.centerRight,
                          )
                        : null,
                    color: inStock ? null : Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: inStock
                        ? [
                            BoxShadow(
                              color: _primary.withValues(alpha: 0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ]
                        : null,
                  ),
                  child: _isBottomBarLoading && _isBuyAction
                      ? const Center(
                          child: SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                        )
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(LucideIcons.zap,
                                color: Colors.white, size: 16),
                            SizedBox(width: 6),
                            Text(
                              'Buy Now',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── Cart / Checkout Action ───────────────────────────────────────────────
  Future<void> _handleCartAction({
    required bool goToCart,
    required bool goToCheckout,
  }) async {
    if (_isBottomBarLoading) return;

    final authProvider = context.read<AuthProvider>();
    if (!authProvider.isAuthenticated) {
      ModernSnackBar.showError(context, 'Please log in to add items to cart');
      return;
    }

    if (goToCheckout) {
      final productItem = {
        'product_id': widget.product.id as int,
        'name': widget.product.name as String,
        'price': (widget.product.price as num).toDouble(),
        'quantity': _quantity,
        'image_url': UrlConfig.toAbsoluteImageUrl(widget.product.imageUrl),
      };
      debugPrint('🛒 Buy Now - Product Item: $productItem');
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => CheckoutScreen(
            selectedItems: [productItem],
            directBuy: true,
          ),
        ),
      );
      return;
    }

    setState(() {
      _isBottomBarLoading = true;
      _isBuyAction = goToCheckout;
    });

    final buyerProvider = context.read<BuyerProvider>();
    final success = await buyerProvider.addProductToCart(
      widget.product,
      quantity: _quantity,
    );

    if (!mounted) return;

    if (success) {
      await buyerProvider.fetchCart();
      if (!mounted) return;
      if (goToCart)
        ModernSnackBar.showCartSuccess(context, widget.product.name);
    } else {
      ModernSnackBar.showError(
        context,
        _friendlyCartMessage(buyerProvider.errorMessage),
      );
    }

    if (mounted) setState(() => _isBottomBarLoading = false);
  }

  String _friendlyCartMessage(String? rawMessage) {
    final message = (rawMessage ?? '').toLowerCase();
    if (message.contains('404'))
      return 'Service unavailable. Please try again later.';
    if (message.contains('network') ||
        message.contains('socket') ||
        message.contains('connection'))
      return 'Check your internet connection.';
    if (message.contains('timeout'))
      return 'Request timeout. Please try again.';
    if (message.contains('login') || message.contains('auth'))
      return 'Please log in again.';
    return 'Could not add to cart. Please try again.';
  }

  Widget _circleButton(
    IconData icon,
    VoidCallback onTap, {
    Color? color,
    bool fill = false,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 38,
        width: 38,
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.12),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(
          icon,
          size: 18,
          color: color ?? _textDark,
          fill: fill ? 0.8 : 0,
        ),
      ),
    );
  }
}
