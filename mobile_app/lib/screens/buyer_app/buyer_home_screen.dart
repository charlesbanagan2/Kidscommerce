import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../services/api_service.dart';
import '../../widgets/hero_carousel.dart';
import '../../widgets/product_card_widget.dart';
import '../../widgets/modern_snackbar.dart';
import '../../widgets/skeleton_loader.dart';
import 'cart_screen.dart';
import 'chat_conversations_screen.dart';
import 'orders_screen.dart';
import 'product_detail_screen.dart';
import 'profile_screen.dart';
import 'notification_screen.dart';

class BuyerHomeScreen extends StatefulWidget {
  final int initialTab;
  final String? ordersInitialFilter;
  final bool showAddressSetup;

  const BuyerHomeScreen({
    super.key,
    this.initialTab = 0,
    this.ordersInitialFilter,
    this.showAddressSetup = false,
  });

  @override
  State<BuyerHomeScreen> createState() => _BuyerHomeScreenState();
}

class _BuyerHomeScreenState extends State<BuyerHomeScreen> with WidgetsBindingObserver {
  int _selectedIndex = 0;
  int _unreadNotifications = 0;
  int _unreadMessages = 0;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _selectedIndex = widget.initialTab;
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final buyerProvider = context.read<BuyerProvider>();
      debugPrint('🏠 BuyerHomeScreen: Fetching initial data...');
      
      ApiService.clearOrdersCache();
      
      buyerProvider.fetchProducts();
      buyerProvider.fetchWishlist();
      
      try {
        debugPrint('📦 BuyerHomeScreen: Starting orders fetch...');
        await buyerProvider.fetchOrdersByStatus();
        debugPrint('📦 BuyerHomeScreen: Orders fetched - ${buyerProvider.allOrders.length} total');
      } catch (e) {
        debugPrint('❌ BuyerHomeScreen: Error fetching orders - $e');
      }
      
      buyerProvider.fetchCart();
      
      // Fetch notification and message counts
      _fetchUnreadCounts();
      
      // Auto-refresh counts every 30 seconds
      _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
        _fetchUnreadCounts();
      });
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      // Refresh counts when app comes to foreground
      _fetchUnreadCounts();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchUnreadCounts() async {
    try {
      final notifCount = await ApiService.getUnreadNotificationsCount();
      final msgCount = await ApiService.getUnreadMessagesCount();
      if (mounted) {
        setState(() {
          _unreadNotifications = notifCount;
          _unreadMessages = msgCount;
        });
      }
    } catch (e) {
      debugPrint('⚠️ Error fetching unread counts: $e');
    }
  }

  void _onTabChange(int index) {
    debugPrint('🔄 Tab changed: $index');
    setState(() => _selectedIndex = index);
    
    // Refresh notification count when switching to home tab
    if (index == 0) {
      _fetchUnreadCounts();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _DashboardScreen(
            onOpenCart: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const CartScreen(),
                ),
              );
            },
            onOpenMessages: () => _onTabChange(2),
            onOpenNotifications: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const NotificationScreen(),
                ),
              );
              // Refresh counts after returning from notifications
              _fetchUnreadCounts();
            },
          ),
          OrdersScreen(initialFilter: widget.ordersInitialFilter),
          const ChatConversationsScreen(),
          ProfileScreen(showAddressSetup: widget.showAddressSetup),
        ],
      ),
      bottomNavigationBar: _buildModernBottomNav(),
    );
  }

  Widget _buildModernBottomNav() {
    return Consumer<BuyerProvider>(
      builder: (context, buyerProvider, _) {
        return Container(
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.08),
                blurRadius: 12,
                offset: const Offset(0, -4),
              ),
            ],
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildNavItem(0, Icons.home_outlined, Icons.home, 'Home'),
                  _buildNavItem(1, Icons.receipt_long_outlined,
                      Icons.receipt_long, 'Orders'),
                  _buildNavItem(
                      2, Icons.message_outlined, Icons.message, 'Messages'),
                  _buildNavItem(
                      3, Icons.person_outline, Icons.person, 'Profile'),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildNavItem(
    int index,
    IconData iconOutlined,
    IconData iconFilled,
    String label,
  ) {
    final isActive = _selectedIndex == index;
    const primaryColor = Color(0xFF1e4db7);
    final showBadge = index == 2 && _unreadMessages > 0;

    return GestureDetector(
      onTap: () {
        debugPrint('📱 Bottom nav tapped: $label (index: $index)');
        _onTabChange(index);
        if (index == 2) _fetchUnreadCounts();
      },
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              gradient: isActive
                  ? const LinearGradient(
                      colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    )
                  : null,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  isActive ? iconFilled : iconOutlined,
                  size: 20,
                  color: isActive ? Colors.white : Colors.grey.shade600,
                ),
                const SizedBox(height: 3),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
                    color: isActive ? primaryColor : Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          if (showBadge)
            Positioned(
              top: -2,
              right: 4,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: const BoxDecoration(
                  color: Color(0xFFEF4444),
                  shape: BoxShape.circle,
                ),
                constraints: const BoxConstraints(
                  minWidth: 16,
                  minHeight: 16,
                ),
                child: Text(
                  _unreadMessages > 9 ? '9+' : '$_unreadMessages',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 8,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _DashboardScreen extends StatefulWidget {
  final VoidCallback onOpenCart;
  final VoidCallback onOpenMessages;
  final VoidCallback onOpenNotifications;

  const _DashboardScreen({
    required this.onOpenCart,
    required this.onOpenMessages,
    required this.onOpenNotifications,
  });

  @override
  State<_DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<_DashboardScreen> {
  static const int _pageSize = 20;

  // Hero Slide URLs from backend
  late List<String> _heroSlides;

  late final TextEditingController _searchController;
  late final ScrollController _scrollController;

  int _visibleProductCount = _pageSize;
  bool _loadingMore = false;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
    _scrollController = ScrollController()..addListener(_onScroll);

    // Initialize hero slides from backend
    _initializeHeroSlides();
  }

  void _initializeHeroSlides() {
    // Use a single local asset image for hero slide
    _heroSlides = [
      'assets/images/hero_slide_4_new_arrival.png',
      'assets/images/Make_this_Christmas_merry_and_bright_with_toys_theyll_love.png',
      'assets/images/hero_slide_1.png',
    ];
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

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

  void _onScroll() {
    if (!_scrollController.hasClients || _loadingMore) {
      return;
    }
    final position = _scrollController.position;
    if (position.pixels >= position.maxScrollExtent - 280) {
      _loadMoreProducts();
    }
  }

  void _loadMoreProducts() {
    final totalCount = context.read<BuyerProvider>().products.length;
    if (_visibleProductCount >= totalCount) {
      return;
    }

    setState(() => _loadingMore = true);
    Future.microtask(() {
      if (!mounted) {
        return;
      }
      setState(() {
        _visibleProductCount =
            min(_visibleProductCount + _pageSize, totalCount);
        _loadingMore = false;
      });
    });
  }

  void _onSearchChanged(String query) {
    debugPrint('🔍 Search query: "$query"');
    final buyerProvider = context.read<BuyerProvider>();
    buyerProvider.searchProducts(query);
    setState(() => _visibleProductCount = _pageSize);
  }

  void _onSelectCategory(String category) {
    debugPrint('📋 Category selected: "$category"');
    final buyerProvider = context.read<BuyerProvider>();
    buyerProvider.filterByCategory(category);
    setState(() => _visibleProductCount = _pageSize);
  }

  Future<void> _refresh(BuyerProvider provider) async {
    debugPrint('🔄 Pull to refresh triggered');
    await provider.fetchProducts();
    await provider.fetchCart();
    await provider.fetchWishlist();
    if (!mounted) {
      return;
    }
    setState(() => _visibleProductCount = _pageSize);
    debugPrint('✅ Refresh complete');
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;
    final isTablet = _isTablet(screenWidth);
    final isSmallPhone = _isSmallPhone(screenWidth);

    final horizontalPadding = isTablet ? 16.0 : 12.0;
    final bannerHeight = isTablet ? 192.0 : (isSmallPhone ? 140.0 : 156.0);
    final productColumns = isTablet ? 3 : 2;

    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      body: SafeArea(
        child: Consumer<BuyerProvider>(
          builder: (context, provider, _) {
            final products = provider.products;
            final visibleCount = min(_visibleProductCount, products.length);

            return RefreshIndicator(
              color: const Color(0xFF1e4db7),
              onRefresh: () => _refresh(provider),
              child: CustomScrollView(
                controller: _scrollController,
                slivers: [
                  // Gradient Header with Welcome Message
                  SliverToBoxAdapter(
                    child: Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                        ),
                      ),
                      padding: EdgeInsets.fromLTRB(
                          horizontalPadding, 16, horizontalPadding, 0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Top bar with logo and action buttons
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Row(
                                  children: [
                                    SizedBox(
                                      height: 48,
                                      child: Image.asset(
                                        'assets/images/logo_ulit.png',
                                        fit: BoxFit.contain,
                                        errorBuilder: (context, error, stackTrace) {
                                          return Text(
                                            'KK',
                                            style: TextStyle(
                                              color: Colors.white,
                                              fontWeight: FontWeight.bold,
                                              fontSize: isTablet ? 16 : 15,
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                    const SizedBox(width: 14),
                                    Expanded(
                                      child: Text(
                                        'Kids Kingdom',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.w800,
                                          fontSize: isSmallPhone ? 16 : 18,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Row(
                                children: [
                                  GestureDetector(
                                    onTap: widget.onOpenCart,
                                    child: Stack(
                                      clipBehavior: Clip.none,
                                      children: [
                                        Container(
                                          width: 36,
                                          height: 36,
                                          decoration: BoxDecoration(
                                            color: Colors.white
                                                .withValues(alpha: 0.15),
                                            borderRadius:
                                                BorderRadius.circular(12),
                                          ),
                                          child: const Icon(
                                            Icons.shopping_cart_outlined,
                                            color: Colors.white,
                                            size: 18,
                                          ),
                                        ),
                                        if (provider.cartCount > 0)
                                          Positioned(
                                            top: -4,
                                            right: -4,
                                            child: Container(
                                              padding: const EdgeInsets.all(3),
                                              decoration: const BoxDecoration(
                                                color: Color(0xFFEF4444),
                                                shape: BoxShape.circle,
                                              ),
                                              child: Text(
                                                provider.cartCount > 9
                                                    ? '9+'
                                                    : '${provider.cartCount}',
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
                                  const SizedBox(width: 8),
                                  GestureDetector(
                                    onTap: widget.onOpenNotifications,
                                    child: Stack(
                                      clipBehavior: Clip.none,
                                      children: [
                                        Container(
                                          width: 36,
                                          height: 36,
                                          decoration: BoxDecoration(
                                            color: Colors.white
                                                .withValues(alpha: 0.15),
                                            borderRadius:
                                                BorderRadius.circular(12),
                                          ),
                                          child: const Icon(
                                            Icons.notifications_outlined,
                                            color: Colors.white,
                                            size: 18,
                                          ),
                                        ),
                                        Positioned(
                                          top: -4,
                                          right: -4,
                                          child: Container(
                                            padding: const EdgeInsets.all(3),
                                            decoration: const BoxDecoration(
                                              color: Color(0xFFEF4444),
                                              shape: BoxShape.circle,
                                            ),
                                            constraints: const BoxConstraints(
                                              minWidth: 18,
                                              minHeight: 18,
                                            ),
                                            child: Text(
                                              (context.findAncestorStateOfType<_BuyerHomeScreenState>()?._unreadNotifications ?? 0) > 9
                                                  ? '9+'
                                                  : '${context.findAncestorStateOfType<_BuyerHomeScreenState>()?._unreadNotifications ?? 0}',
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 9,
                                                fontWeight: FontWeight.bold,
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),

                          // Search Bar
                          Container(
                            height: 42,
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.95),
                              borderRadius: BorderRadius.circular(20),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.08),
                                  blurRadius: 8,
                                ),
                              ],
                            ),
                            child: TextField(
                              controller: _searchController,
                              onChanged: _onSearchChanged,
                              style: TextStyle(fontSize: isTablet ? 14 : 13),
                              decoration: InputDecoration(
                                hintText: 'Search products, brands...',
                                hintStyle: TextStyle(
                                  fontSize: isTablet ? 13 : 12,
                                  color: Colors.grey.shade400,
                                ),
                                border: InputBorder.none,
                                contentPadding: EdgeInsets.symmetric(
                                  vertical: isTablet ? 12 : 11,
                                ),
                                prefixIcon: Icon(
                                  Icons.search,
                                  size: 17,
                                  color: Colors.grey.shade400,
                                ),
                                suffixIcon: const Icon(
                                  Icons.search,
                                  size: 17,
                                  color: Color(0xFF1e4db7),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),

                          // Category Pills
                          SingleChildScrollView(
                            scrollDirection: Axis.horizontal,
                            child: Row(
                              children: provider.categories.isEmpty
                                  ? [
                                      _buildCategoryPill('All', true, provider),
                                    ]
                                  : [
                                      _buildCategoryPill(
                                          'All',
                                          provider.selectedCategory == 'All',
                                          provider),
                                      ...provider.categories
                                          .where((cat) => cat != 'All')
                                          .take(7)
                                          .map(
                                            (cat) => _buildCategoryPill(
                                                cat,
                                                provider.selectedCategory ==
                                                    cat,
                                                provider),
                                          ),
                                    ],
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                      ),
                    ),
                  ),

                  // Hero Carousel
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: EdgeInsets.fromLTRB(
                          horizontalPadding, 0, horizontalPadding, 12),
                      child: HeroCarousel(
                        imageUrls: _heroSlides,
                        height: bannerHeight,
                        autoScrollDuration: const Duration(seconds: 3),
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                                content: Text('Explore this collection!')),
                          );
                        },
                      ),
                    ),
                  ),

                  // Quick Stats Section
                  SliverToBoxAdapter(
                    child: Padding(
                      padding:
                          EdgeInsets.symmetric(horizontal: horizontalPadding),
                      child: GridView.count(
                        crossAxisCount: 3,
                        mainAxisSpacing: 10,
                        crossAxisSpacing: 10,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        childAspectRatio: 1.1,
                        children: [
                          _buildStatCard('Flash Sale', '12 items',
                              Icons.trending_up, Colors.orange),
                          _buildStatCard('New In', '48 items', Icons.flash_on,
                              Colors.blue),
                          _buildStatCard('Top Rated', '4.8★', Icons.star,
                              Colors.amber),
                        ],
                      ),
                    ),
                  ),

                  SliverToBoxAdapter(
                    child: SizedBox(height: isTablet ? 20 : 16),
                  ),

                  // Daily Discover Title
                  SliverToBoxAdapter(
                    child: Padding(
                      padding:
                          EdgeInsets.symmetric(horizontal: horizontalPadding),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Daily Discover',
                                style: TextStyle(
                                  fontSize: isTablet ? 18 : 16,
                                  fontWeight: FontWeight.bold,
                                  color: const Color(0xFF1F2937),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Curated just for you',
                                style: TextStyle(
                                  fontSize: isSmallPhone ? 10 : 11,
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ],
                          ),
                          GestureDetector(
                            onTap: () {},
                            child: const Row(
                              children: [
                                Text(
                                  'See all',
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF1e4db7),
                                  ),
                                ),
                                SizedBox(width: 4),
                                Icon(
                                  Icons.chevron_right,
                                  color: Color(0xFF1e4db7),
                                  size: 16,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  SliverToBoxAdapter(
                    child: SizedBox(height: isTablet ? 12 : 12),
                  ),

                  // Products Grid
                  if (provider.isLoading && products.isEmpty)
                    SliverPadding(
                      padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
                      sliver: SliverGrid(
                        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: productColumns,
                          mainAxisSpacing: isTablet ? 12 : 10,
                          crossAxisSpacing: isTablet ? 12 : 10,
                          childAspectRatio: _gridAspectRatio(screenWidth),
                        ),
                        delegate: SliverChildBuilderDelegate(
                          (context, index) => const ProductCardSkeleton(),
                          childCount: 6,
                        ),
                      ),
                    )
                  else if (products.isEmpty)
                    const SliverToBoxAdapter(
                      child: Padding(
                        padding: EdgeInsets.symmetric(vertical: 36),
                        child: Center(
                          child: Text(
                            'No products found',
                            style:
                                TextStyle(fontSize: 14, color: Colors.black54),
                          ),
                        ),
                      ),
                    )
                  else
                    SliverToBoxAdapter(
                      child: Padding(
                        padding:
                            EdgeInsets.symmetric(horizontal: horizontalPadding),
                        child: GridView.builder(
                          itemCount: visibleCount,
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: productColumns,
                            mainAxisSpacing: isTablet ? 12 : 10,
                            crossAxisSpacing: isTablet ? 12 : 10,
                            childAspectRatio: _gridAspectRatio(screenWidth),
                          ),
                          itemBuilder: (context, index) {
                            final product = products[index];
                            return ProductCardWidget(
                              product: product,
                              onProductClick: (product) {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) =>
                                        ProductDetailScreen(product: product),
                                  ),
                                );
                              },
                              onAddToCart: (product) async {
                                final buyerProvider =
                                    context.read<BuyerProvider>();
                                final success = await buyerProvider
                                    .addProductToCart(product);
                                if (!context.mounted) {
                                  return false;
                                }
                                if (success) {
                                  await buyerProvider.fetchCart();
                                  if (!context.mounted) {
                                    return false;
                                  }
                                  ModernSnackBar.showCartSuccess(
                                    context,
                                    product.name,
                                    onViewCart: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => const CartScreen(),
                                        ),
                                      );
                                    },
                                  );
                                  return true;
                                } else {
                                  final message = buyerProvider.errorMessage ??
                                      'Could not add to cart. Please try again.';
                                  ModernSnackBar.showError(context, message);
                                  return false;
                                }
                              },
                            );
                          },
                        ),
                      ),
                    ),
                  if (_loadingMore && products.isNotEmpty)
                    const SliverToBoxAdapter(
                      child: Padding(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        child: Center(child: CircularProgressIndicator()),
                      ),
                    ),
                  const SliverToBoxAdapter(child: SizedBox(height: 20)),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildCategoryPill(
      String category, bool isSelected, BuyerProvider provider) {
    return GestureDetector(
      onTap: () => _onSelectCategory(category),
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color:
              isSelected ? Colors.white : Colors.white.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          category,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: isSelected ? const Color(0xFF1e4db7) : Colors.white,
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(
      String label, String value, IconData icon, Color color) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
          ),
        ],
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: color,
              size: 14,
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 9,
                  color: Colors.grey,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
