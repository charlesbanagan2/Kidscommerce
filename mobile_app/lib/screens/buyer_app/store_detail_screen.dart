import 'package:flutter/material.dart';

import 'package:provider/provider.dart';
import '../../models/product.dart';
import '../../providers/buyer_provider.dart';
import '../../config/url_config.dart';
import 'cart_screen.dart';
import 'product_detail_screen.dart';

class StoreDetailScreen extends StatefulWidget {
  final int sellerId;
  final String storeName;
  final String? storeLogo;
  final String? storeBackground;
  final double? storeRating;
  final int? followersCount;

  const StoreDetailScreen({
    required this.sellerId,
    required this.storeName,
    this.storeLogo,
    this.storeBackground,
    this.storeRating,
    this.followersCount,
    super.key,
  });

  @override
  State<StoreDetailScreen> createState() => _StoreDetailScreenState();
}

class _StoreDetailScreenState extends State<StoreDetailScreen>
    with SingleTickerProviderStateMixin {
  late TextEditingController _searchController;
  bool _isFollowing = false;
  final Set<int> _addingProductIds = {};
  late ScrollController _scrollController;
  bool _isHeaderCollapsed = false;

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
    _searchController = TextEditingController();
    _scrollController = ScrollController();
    _scrollController.addListener(() {
      final collapsed = _scrollController.offset > 160;
      if (collapsed != _isHeaderCollapsed) {
        setState(() => _isHeaderCollapsed = collapsed);
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;
    final isTablet = _isTablet(screenWidth);
    final productColumns = isTablet ? 3 : 2;

    return Scaffold(
      backgroundColor: _bgColor,
      body: Consumer<BuyerProvider>(
        builder: (context, provider, _) {
          final storeProducts = provider.allProducts
              .where((p) => p.sellerId == widget.sellerId)
              .toList();

          final filtered = storeProducts
              .where((p) =>
                  _searchController.text.isEmpty ||
                  p.name
                      .toLowerCase()
                      .contains(_searchController.text.toLowerCase()))
              .toList();

          return CustomScrollView(
            controller: _scrollController,
            slivers: [
              // ── Collapsible App Bar ──────────────────────────────────
              SliverAppBar(
                expandedHeight: 260,
                pinned: true,
                stretch: true,
                backgroundColor: _primaryDark,
                leading: Padding(
                  padding: const EdgeInsets.all(8),
                  child: GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.2),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.arrow_back,
                          color: Colors.white, size: 20),
                    ),
                  ),
                ),
                actions: [
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: GestureDetector(
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (_) => const CartScreen()),
                      ),
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          shape: BoxShape.circle,
                        ),
                        padding: const EdgeInsets.all(8),
                        child: const Icon(Icons.shopping_cart_outlined,
                            color: Colors.white, size: 20),
                      ),
                    ),
                  ),
                ],
                title: AnimatedOpacity(
                  opacity: _isHeaderCollapsed ? 1.0 : 0.0,
                  duration: const Duration(milliseconds: 200),
                  child: Row(
                    children: [
                      Container(
                        width: 30,
                        height: 30,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border:
                              Border.all(color: Colors.white, width: 1.5),
                          color: Colors.white.withValues(alpha: 0.15),
                        ),
                        child: ClipOval(
                          child: widget.storeLogo != null
                              ? Image.network(
                                  UrlConfig.toAbsoluteImageUrl(
                                      widget.storeLogo!),
                                  fit: BoxFit.cover,
                                  errorBuilder: (_, __, ___) => const Icon(
                                      Icons.store,
                                      color: Colors.white,
                                      size: 16),
                                )
                              : const Icon(Icons.store,
                                  color: Colors.white, size: 16),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        widget.storeName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
                flexibleSpace: FlexibleSpaceBar(
                  stretchModes: const [StretchMode.zoomBackground],
                  background: _buildHeroBackground(storeProducts.length),
                ),
              ),

              // ── Store Info Card ──────────────────────────────────────
              SliverToBoxAdapter(
                child: _buildStoreInfoCard(),
              ),

              // ── Stats Row ────────────────────────────────────────────
              SliverToBoxAdapter(
                child: _buildStatsRow(storeProducts.length),
              ),

              // ── Search Bar ───────────────────────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
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
                    child: TextField(
                      controller: _searchController,
                      onChanged: (_) => setState(() {}),
                      style: const TextStyle(
                          fontSize: 14, color: _textDark),
                      decoration: InputDecoration(
                        hintText: 'Search in ${widget.storeName}…',
                        hintStyle: TextStyle(
                            color: Colors.grey.shade400, fontSize: 13),
                        prefixIcon: const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 14),
                          child: Icon(Icons.search,
                              color: _primary, size: 18),
                        ),
                        prefixIconConstraints: const BoxConstraints(
                            minWidth: 48, minHeight: 48),
                        suffixIcon: _searchController.text.isNotEmpty
                            ? GestureDetector(
                                onTap: () {
                                  _searchController.clear();
                                  setState(() {});
                                },
                                child: const Padding(
                                  padding: EdgeInsets.symmetric(
                                      horizontal: 14),
                                  child: Icon(Icons.close,
                                      color: _textMid, size: 16),
                                ),
                              )
                            : null,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 14, horizontal: 16),
                      ),
                    ),
                  ),
                ),
              ),

              // ── Section title ────────────────────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
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
                      Text(
                        _searchController.text.isNotEmpty
                            ? '${filtered.length} result${filtered.length == 1 ? '' : 's'} found'
                            : 'All Products',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                          color: _textDark,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // ── Products Grid ────────────────────────────────────────
              if (filtered.isEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 48),
                    child: Center(
                      child: Column(
                        children: [
                          Container(
                            width: 72,
                            height: 72,
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Icon(Icons.shopping_bag_outlined,
                                size: 36, color: Colors.grey.shade400),
                          ),
                          const SizedBox(height: 14),
                          Text(
                            _searchController.text.isNotEmpty
                                ? 'No products match your search'
                                : 'No products in this store',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _textDark,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Check back later for new arrivals',
                            style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade400),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16),
                  sliver: SliverGrid(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        if (index >= filtered.length) return null;
                        return _buildProductCard(filtered[index],
                            screenWidth: screenWidth);
                      },
                      childCount: filtered.length,
                    ),
                    gridDelegate:
                        SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: productColumns,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: _gridAspectRatio(screenWidth),
                    ),
                  ),
                ),

              const SliverToBoxAdapter(child: SizedBox(height: 40)),
            ],
          );
        },
      ),
    );
  }

  // ── Hero Background ──────────────────────────────────────────────────────
  Widget _buildHeroBackground(int productCount) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Background image or gradient
        widget.storeBackground != null
            ? Image.network(
                UrlConfig.toAbsoluteImageUrl(widget.storeBackground!),
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => _gradientBg(),
              )
            : _gradientBg(),

        // Dark overlay
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black.withValues(alpha: 0.25),
                Colors.black.withValues(alpha: 0.6),
              ],
            ),
          ),
        ),

        // Store logo + name centered at bottom
        Positioned(
          bottom: 24,
          left: 20,
          right: 20,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // Logo
              Container(
                width: 76,
                height: 76,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white,
                  border: Border.all(color: Colors.white, width: 3),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.2),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ClipOval(
                  child: widget.storeLogo != null
                      ? Image.network(
                          UrlConfig.toAbsoluteImageUrl(
                              widget.storeLogo!),
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            color: _primaryDark,
                            child: const Icon(Icons.store,
                                color: Colors.white, size: 36),
                          ),
                        )
                      : Container(
                          decoration: const BoxDecoration(
                            gradient: LinearGradient(
                              colors: [_primaryDark, _primaryLight],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                          ),
                          child: const Icon(Icons.store,
                              color: Colors.white, size: 36),
                        ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      widget.storeName,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -0.3,
                        shadows: [
                          Shadow(
                              color: Colors.black45,
                              blurRadius: 4,
                              offset: Offset(0, 1))
                        ],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.star,
                            color: Colors.amber, size: 13, fill: 0.8),
                        const SizedBox(width: 4),
                        Text(
                          '${(widget.storeRating ?? 0).toStringAsFixed(1)}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                                color: Colors.white.withValues(alpha: 0.4)),
                          ),
                          child: const Text(
                            'Official Store',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
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
      ],
    );
  }

  Widget _gradientBg() => Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [_primaryDark, _primary, _primaryLight],
          ),
        ),
      );

  // ── Store Info Card ──────────────────────────────────────────────────────
  Widget _buildStoreInfoCard() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () => setState(() => _isFollowing = !_isFollowing),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 250),
                height: 44,
                decoration: BoxDecoration(
                  gradient: _isFollowing
                      ? const LinearGradient(
                          colors: [_primaryDark, _primaryLight],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        )
                      : null,
                  color: _isFollowing ? null : Colors.transparent,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color:
                        _isFollowing ? Colors.transparent : Colors.grey.shade300,
                    width: 1.5,
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      _isFollowing
                          ? Icons.favorite_border
                          : Icons.favorite,
                      size: 15,
                      color:
                          _isFollowing ? Colors.white : _textMid,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _isFollowing ? 'Following' : 'Follow',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: _isFollowing ? Colors.white : _textDark,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Container(
              height: 44,
              decoration: BoxDecoration(
                color: _bgColor,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.chat_bubble_outline,
                      size: 15, color: _primary),
                  SizedBox(width: 6),
                  Text(
                    'Contact',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: _primary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Stats Row ────────────────────────────────────────────────────────────
  Widget _buildStatsRow(int productCount) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          _statItem(
            icon: Icons.star,
            iconColor: Colors.amber,
            value:
                '${(widget.storeRating ?? 0).toStringAsFixed(1)}',
            label: 'Rating',
          ),
          _statDivider(),
          _statItem(
            icon: Icons.people,
            iconColor: _primary,
            value: '${widget.followersCount ?? 0}',
            label: 'Followers',
          ),
          _statDivider(),
          _statItem(
            icon: Icons.inventory_2_outlined,
            iconColor: const Color(0xFF16A34A),
            value: '$productCount',
            label: 'Products',
          ),
        ],
      ),
    );
  }

  Widget _statItem({
    required IconData icon,
    required Color iconColor,
    required String value,
    required String label,
  }) =>
      Expanded(
        child: Column(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: iconColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, size: 17, color: iconColor),
            ),
            const SizedBox(height: 6),
            Text(
              value,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w900,
                color: _textDark,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w500,
                color: _textMid,
              ),
            ),
          ],
        ),
      );

  Widget _statDivider() => Container(
        width: 1,
        height: 40,
        color: Colors.grey.shade100,
      );

  // ── Product Card ─────────────────────────────────────────────────────────
  Widget _buildProductCard(Product product, {required double screenWidth}) {
    final isTablet = _isTablet(screenWidth);
    final isSmallPhone = _isSmallPhone(screenWidth);
    final imageHeight = isTablet ? 170.0 : (isSmallPhone ? 132.0 : 155.0);
    final nameFont = isTablet ? 13.5 : 12.5;
    final priceFont = isTablet ? 16.0 : 14.0;
    final stockFont = isTablet ? 11.5 : 10.5;
    final buttonPad = isTablet ? 7.0 : 6.0;

    final productId = product.id;
    final isAdding = _addingProductIds.contains(productId);

    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ProductDetailScreen(product: product),
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
              child: Stack(
                children: [
                  Container(
                    height: imageHeight,
                    width: double.infinity,
                    color: Colors.grey.shade100,
                    child: product.imageUrl != null &&
                            product.imageUrl!.isNotEmpty
                        ? Image.network(
                            UrlConfig.toAbsoluteImageUrl(
                                product.imageUrl ?? ''),
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => Icon(
                              Icons.hide_image,
                              color: Colors.grey.shade400,
                              size: isTablet ? 36 : 30,
                            ),
                          )
                        : Icon(Icons.image,
                            color: Colors.grey.shade400,
                            size: isTablet ? 36 : 30),
                  ),
                  // Out of stock overlay
                  if (product.stock <= 0)
                    Positioned.fill(
                      child: Container(
                        color: Colors.black.withValues(alpha: 0.35),
                        child: const Center(
                          child: Text(
                            'Out of Stock',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w800,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // Info
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
                        Icon(Icons.inventory_2_outlined,
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
                        // Cart button
                        GestureDetector(
                          onTap: product.stock > 0
                              ? () async {
                                  if (isAdding) return;
                                  setState(() =>
                                      _addingProductIds.add(productId));
                                  final buyerProvider =
                                      context.read<BuyerProvider>();
                                  final success =
                                      await buyerProvider.addProductToCart(
                                          product);
                                  if (!mounted) return;
                                  if (success) {
                                    await buyerProvider.fetchCart();
                                    if (!mounted) return;
                                    _showSnackBar(
                                        '${product.name} added to cart',
                                        isSuccess: true);
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                          builder: (_) =>
                                              const CartScreen()),
                                    );
                                  } else {
                                    _showSnackBar(
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
                                      valueColor:
                                          AlwaysStoppedAnimation<Color>(
                                              Colors.white),
                                    ),
                                  )
                                : const Icon(
                                    Icons.shopping_cart_outlined,
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

  void _showSnackBar(String message, {bool isSuccess = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isSuccess ? Icons.check_circle : Icons.error,
              color: Colors.white,
              size: 16,
            ),
            const SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor:
            isSuccess ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  String _friendlyCartMessage(String? rawMessage) {
    final message = (rawMessage ?? '').toLowerCase();
    if (message.contains('404'))
      return 'Service unavailable. Please try again later.';
    if (message.contains('network') ||
        message.contains('socket') ||
        message.contains('connection'))
      return 'Check your internet connection.';
    if (message.contains('timeout')) return 'Request timeout. Please try again.';
    if (message.contains('login') || message.contains('auth'))
      return 'Please log in again.';
    return 'Could not add to cart. Please try again.';
  }
}

