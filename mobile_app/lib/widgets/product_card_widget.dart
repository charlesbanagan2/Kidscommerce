import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../config/url_config.dart';

/// Reusable Product Card Widget
/// Displays product image, name, rating, price, stock status, and add-to-cart button
class ProductCardWidget extends StatefulWidget {
  final dynamic product;
  final void Function(dynamic product)? onProductClick;
  final Future<bool> Function(dynamic product)? onAddToCart;
  final bool isLoading;

  const ProductCardWidget({
    super.key,
    required this.product,
    this.onProductClick,
    this.onAddToCart,
    this.isLoading = false,
  });

  @override
  State<ProductCardWidget> createState() => _ProductCardWidgetState();
}

class _ProductCardWidgetState extends State<ProductCardWidget>
    with SingleTickerProviderStateMixin {
  bool _added = false;
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _handleAddToCart() async {
    if (widget.product.stock == 0) return;

    if (widget.onAddToCart != null) {
      final success = await widget.onAddToCart!(widget.product);
      if (success && mounted) {
        setState(() => _added = true);
        await Future.delayed(const Duration(milliseconds: 1500));
        if (mounted) {
          setState(() => _added = false);
        }
      }
    } else {
      // Default behavior if no callback provided
      setState(() => _added = true);
      await Future.delayed(const Duration(milliseconds: 1500));
      if (mounted) {
        setState(() => _added = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isOutOfStock = widget.product.stock == 0;
    final hasDiscount = widget.product.isOnSale ?? false;

    return GestureDetector(
      onTap: widget.onProductClick != null && !isOutOfStock
          ? () => widget.onProductClick!(widget.product)
          : null,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: Colors.grey.shade200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image Section
            Expanded(
              child: Stack(
                children: [
                  // Product Image
                  Container(
                    width: double.infinity,
                    color: Colors.grey.shade50,
                    child: _buildProductImage(),
                  ),

                  // Discount Badge
                  if (hasDiscount)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red.shade500,
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.1),
                              blurRadius: 4,
                            ),
                          ],
                        ),
                        child: Text(
                          '-${((widget.product.price - widget.product.displayPrice) / widget.product.price * 100).toStringAsFixed(0)}%',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),

                  // Out of Stock Overlay
                  if (isOutOfStock)
                    Positioned.fill(
                      child: Container(
                        color: Colors.black.withValues(alpha: 0.4),
                        child: Center(
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              'Out of Stock',
                              style: TextStyle(
                                color: Colors.grey.shade700,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // Info Section
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Name
                  Text(
                    widget.product.name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF1F2937),
                      height: 1.3,
                    ),
                  ),
                  const SizedBox(height: 6),

                  // Rating and Stock
                  Row(
                    children: [
                      const Icon(
                        LucideIcons.star,
                        size: 10,
                        color: Color(0xFFFCD34D),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        widget.product.rating > 0 ? widget.product.rating.toStringAsFixed(1) : '0.0',
                        style: const TextStyle(
                          fontSize: 10,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '· ${isOutOfStock ? 'Sold out' : '${widget.product.stock} left'}',
                        style: const TextStyle(
                          fontSize: 10,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Price and Button
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      // Prices
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (hasDiscount)
                              Text(
                                '₱${widget.product.price.toStringAsFixed(2)}',
                                style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.grey.shade500,
                                  decoration: TextDecoration.lineThrough,
                                  height: 1.2,
                                ),
                              ),
                            Text(
                              '₱${widget.product.displayPrice.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF1e4db7),
                              ),
                            ),
                          ],
                        ),
                      ),

                      // Add to Cart Button
                      ScaleTransition(
                        scale: Tween<double>(begin: 1, end: 1.05)
                            .animate(_animationController),
                        child: GestureDetector(
                          onTap: widget.isLoading || isOutOfStock
                              ? null
                              : _handleAddToCart,
                          child: Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: _added
                                  ? Colors.green.shade500
                                  : isOutOfStock
                                      ? Colors.grey.shade300
                                      : const Color(0xFF1e4db7),
                              borderRadius: BorderRadius.circular(10),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.08),
                                  blurRadius: 4,
                                ),
                              ],
                            ),
                            child: widget.isLoading
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 1.5,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white,
                                      ),
                                    ),
                                  )
                                : Icon(
                                    _added
                                        ? LucideIcons.check
                                        : LucideIcons.shoppingCart,
                                    color: Colors.white,
                                    size: 14,
                                  ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductImage() {
    final imageUrl = widget.product.imageUrl;
    if (imageUrl != null && imageUrl.isNotEmpty) {
      final absoluteUrl = UrlConfig.toAbsoluteImageUrl(imageUrl);
      return Image.network(
        absoluteUrl,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          return Center(
            child: Icon(
              LucideIcons.package,
              size: 32,
              color: Colors.grey.shade300,
            ),
          );
        },
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 1.5,
                value: loadingProgress.expectedTotalBytes != null
                    ? loadingProgress.cumulativeBytesLoaded /
                        loadingProgress.expectedTotalBytes!
                    : null,
              ),
            ),
          );
        },
      );
    }

    return Center(
      child: Icon(
        LucideIcons.package,
        size: 32,
        color: Colors.grey.shade300,
      ),
    );
  }
}
