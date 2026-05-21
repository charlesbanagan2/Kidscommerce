import 'package:flutter/material.dart';

import '../../services/api_service.dart';
import '../../widgets/skeleton_loader.dart';

// ─── Theme Constants ────────────────────────────────────────────────────────
class _AppColors {
  static const primary = Color(0xFF1e4db7);
  static const primaryDark = Color(0xFF1a2f6b);
  static const background = Color(0xFFF4F7FF);
  static const surface = Colors.white;
  static const textPrimary = Color(0xFF0F172A);
  static const textSecondary = Color(0xFF64748B);
  static const textMuted = Color(0xFF94A3B8);
  static const unreadBg = Color(0xFFEEF3FF);
  static const unreadBorder = Color(0xFFBFCFFF);
  static const divider = Color(0xFFE8EDF5);
  static const danger = Color(0xFFEF4444);
  static const orderGreen = Color(0xFF10B981);
  static const promoAmber = Color(0xFFF59E0B);
  static const productBlue = Color(0xFF3B82F6);
  static const systemPurple = Color(0xFF8B5CF6);
  static const paymentTeal = Color(0xFF14B8A6);
}

// ─── Data Models ────────────────────────────────────────────────────────────
enum NotificationType { order, promotion, product, system, payment }

enum NotificationFilter { all, unread, orders, promos, products, system }

class NotificationItem {
  final String id;
  final String title;
  final String message;
  final String time;
  final NotificationType type;
  final bool isRead;
  final int? orderId;
  final String? link;
  final String? imageUrl;
  final DateTime? createdAt;

  NotificationItem({
    required this.id,
    required this.title,
    required this.message,
    required this.time,
    required this.type,
    this.isRead = false,
    this.orderId,
    this.link,
    this.imageUrl,
    this.createdAt,
  });

  NotificationItem copyWith({bool? isRead}) {
    return NotificationItem(
      id: id,
      title: title,
      message: message,
      time: time,
      type: type,
      isRead: isRead ?? this.isRead,
      orderId: orderId,
      link: link,
      imageUrl: imageUrl,
      createdAt: createdAt,
    );
  }
}

// ─── Screen ─────────────────────────────────────────────────────────────────
class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  NotificationFilter _activeFilter = NotificationFilter.all;

  List<NotificationItem> _notifications = [];
  bool _isLoading = true;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();
  int _totalCount = 0;
  bool _hasMore = true;
  int _offset = 0;
  static const int _limit = 20;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    );
    _fadeController.forward();
    _loadNotifications();
  }

  Future<void> _loadNotifications({bool refresh = true}) async {
    if (refresh) {
      setState(() {
        _isLoading = true;
        _offset = 0;
        _hasMore = true;
      });
    }

    try {
      final queryParams = <String, String>{
        'limit': '$_limit',
        'offset': '$_offset',
      };
      if (_activeFilter == NotificationFilter.unread) {
        queryParams['unread_only'] = 'true';
      } else if (_activeFilter == NotificationFilter.orders) {
        queryParams['type'] = 'order';
      } else if (_activeFilter == NotificationFilter.promos) {
        queryParams['type'] = 'promotion';
      } else if (_activeFilter == NotificationFilter.products) {
        queryParams['type'] = 'product';
      } else if (_activeFilter == NotificationFilter.system) {
        queryParams['type'] = 'system';
      }

      final response = await ApiService.getNotifications(query: queryParams);
      if (response['success'] == true) {
        final List<dynamic> notifications = response['notifications'] ?? [];
        final total = (response['total_count'] as num?)?.toInt() ?? 0;
        final hasMore = (response['has_more'] as bool?) ?? false;

        setState(() {
          final mapped = notifications.map((notif) {
            final type = _parseNotificationType(notif['type']);
            return NotificationItem(
              id: notif['id']?.toString() ?? '',
              title: notif['title'] ?? 'Notification',
              message: notif['message'] ?? '',
              time: _formatTime(notif['created_at']),
              type: type,
              isRead: notif['is_read'] ?? false,
              orderId: (notif['order_id'] as num?)?.toInt(),
              link: notif['link'] ?? notif['action_url'],
              imageUrl: notif['image_url'],
              createdAt: _parseDateTime(notif['created_at']),
            );
          }).toList()
            ..sort((a, b) {
              // Sort by createdAt descending (latest first)
              if (a.createdAt == null && b.createdAt == null) return 0;
              if (a.createdAt == null) return 1;
              if (b.createdAt == null) return -1;
              return b.createdAt!.compareTo(a.createdAt!);
            });

          if (refresh) {
            _notifications = mapped;
          } else {
            _notifications.addAll(mapped);
          }
          _totalCount = total;
          _hasMore = hasMore;
          _offset = _notifications.length;
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      debugPrint('Error loading notifications: $e');
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadMore() async {
    if (!_hasMore || _isLoading) return;
    await _loadNotifications(refresh: false);
  }

  DateTime? _parseDateTime(String? createdAt) {
    if (createdAt == null) return null;
    try {
      return DateTime.parse(createdAt);
    } catch (e) {
      return null;
    }
  }

  NotificationType _parseNotificationType(String? type) {
    if (type == null) return NotificationType.order;
    switch (type.toLowerCase()) {
      case 'promotion':
      case 'promo':
        return NotificationType.promotion;
      case 'product':
        return NotificationType.product;
      case 'system':
        return NotificationType.system;
      case 'payment':
        return NotificationType.payment;
      default:
        return NotificationType.order;
    }
  }

  String _formatTime(String? createdAt) {
    if (createdAt == null) return 'Just now';
    try {
      final dateTime = DateTime.parse(createdAt);
      final now = DateTime.now();
      final diff = now.difference(dateTime);
      if (diff.inMinutes < 1) return 'Just now';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      if (diff.inDays == 1) return 'Yesterday';
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return '${dateTime.month}/${dateTime.day}/${dateTime.year}';
    } catch (e) {
      return 'Just now';
    }
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  int get _unreadCount => _notifications.where((n) => !n.isRead).length;

  List<NotificationItem> get _filteredNotifications {
    var list = _notifications;
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      list = list.where((n) =>
        n.title.toLowerCase().contains(query) ||
        n.message.toLowerCase().contains(query) ||
        (n.orderId?.toString() ?? '').contains(query)
      ).toList();
    }
    switch (_activeFilter) {
      case NotificationFilter.all:
        return list;
      case NotificationFilter.unread:
        return list.where((n) => !n.isRead).toList();
      case NotificationFilter.orders:
        return list.where((n) => n.type == NotificationType.order).toList();
      case NotificationFilter.promos:
        return list.where((n) => n.type == NotificationType.promotion).toList();
      case NotificationFilter.products:
        return list.where((n) => n.type == NotificationType.product).toList();
      case NotificationFilter.system:
        return list.where((n) =>
          n.type == NotificationType.system || n.type == NotificationType.payment
        ).toList();
    }
  }

  int _filterCount(NotificationFilter filter) {
    switch (filter) {
      case NotificationFilter.all:
        return _notifications.length;
      case NotificationFilter.unread:
        return _notifications.where((n) => !n.isRead).length;
      case NotificationFilter.orders:
        return _notifications.where((n) => n.type == NotificationType.order).length;
      case NotificationFilter.promos:
        return _notifications.where((n) => n.type == NotificationType.promotion).length;
      case NotificationFilter.products:
        return _notifications.where((n) => n.type == NotificationType.product).length;
      case NotificationFilter.system:
        return _notifications.where((n) =>
          n.type == NotificationType.system || n.type == NotificationType.payment
        ).length;
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredNotifications;

    return Scaffold(
      backgroundColor: _AppColors.background,
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: RefreshIndicator(
          onRefresh: () => _loadNotifications(refresh: true),
          color: _AppColors.primary,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              _buildAppBar(),
              SliverToBoxAdapter(child: _buildSummaryCard()),
              if (_isLoading)
                const SliverFillRemaining(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Column(
                      children: [
                        NotificationSkeleton(),
                        NotificationSkeleton(),
                        NotificationSkeleton(),
                        NotificationSkeleton(),
                        NotificationSkeleton(),
                      ],
                    ),
                  ),
                )
              else ...[
                SliverToBoxAdapter(child: _buildFilterTabBar()),
                if (filtered.isNotEmpty) ...[
                  _buildGroupedNotifications(filtered),
                ] else
                  SliverToBoxAdapter(
                    child: _buildEmptyFilterState(),
                  ),
                if (_hasMore)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      child: Center(
                        child: GestureDetector(
                          onTap: _loadMore,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                            decoration: BoxDecoration(
                              color: _AppColors.primary.withValues(alpha: 0.08),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: _AppColors.primary.withValues(alpha: 0.2)),
                            ),
                            child: Text(
                              'Load More ($_totalCount total)',
                              style: const TextStyle(
                                color: _AppColors.primary,
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      pinned: true,
      floating: false,
      elevation: 0,
      backgroundColor: _AppColors.primary,
      leading: GestureDetector(
        onTap: () => Navigator.pop(context),
        child: Container(
          margin: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(
            Icons.chevron_left,
            color: Colors.white,
            size: 20,
          ),
        ),
      ),
      title: const Text(
        'Notifications',
        style: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          letterSpacing: -0.5,
        ),
      ),
      actions: [
        GestureDetector(
          onTap: _showSettingsSheet,
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.settings,
              color: Colors.white,
              size: 18,
            ),
          ),
        ),
        if (_unreadCount > 0)
          GestureDetector(
            onTap: _markAllAsRead,
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Colors.white.withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: const Text(
                'Mark all read',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.3,
                ),
              ),
            ),
          ),
      ],
    );
  }

  // ── Grouped Notifications ──────────────────────────────────────────────
  Widget _buildGroupedNotifications(List<NotificationItem> items) {
    final groups = <String, List<NotificationItem>>{};
    final now = DateTime.now();

    for (final item in items) {
      final created = item.createdAt;
      String group;
      if (created == null) {
        group = 'Recent';
      } else {
        final diff = now.difference(created);
        if (diff.inDays == 0) {
          group = 'Today';
        } else if (diff.inDays == 1) {
          group = 'Yesterday';
        } else if (diff.inDays < 7) {
          group = 'This Week';
        } else {
          group = 'Earlier';
        }
      }
      groups.putIfAbsent(group, () => []).add(item);
    }

    // Sort items within each group by createdAt descending (latest first)
    for (final groupItems in groups.values) {
      groupItems.sort((a, b) {
        if (a.createdAt == null && b.createdAt == null) return 0;
        if (a.createdAt == null) return 1;
        if (b.createdAt == null) return -1;
        return b.createdAt!.compareTo(a.createdAt!);
      });
    }

    final order = ['Today', 'Yesterday', 'This Week', 'Earlier', 'Recent'];
    final slivers = <Widget>[];

    for (final groupName in order) {
      final groupItems = groups[groupName];
      if (groupItems == null || groupItems.isEmpty) continue;
      slivers.add(_buildSectionHeader('$groupName (${groupItems.length})'));
      slivers.add(_buildNotificationList(groupItems));
    }

    return SliverMainAxisGroup(slivers: slivers);
  }

  // ── Sliver AppBar ──────────────────────────────────────────────────────────
  Widget _buildSummaryCard() {
    final orderCount = _notifications
        .where((n) => n.type == NotificationType.order && !n.isRead)
        .length;
    final promoCount = _notifications
        .where((n) => n.type == NotificationType.promotion && !n.isRead)
        .length;
    final productCount = _notifications
        .where((n) => n.type == NotificationType.product && !n.isRead)
        .length;
    final systemCount = _notifications
        .where((n) => (n.type == NotificationType.system || n.type == NotificationType.payment) && !n.isRead)
        .length;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_AppColors.primaryDark, _AppColors.primary],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: _AppColors.primary.withValues(alpha: 0.35),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          _buildSummaryBadge(
            icon: Icons.inventory_2_outlined,
            label: 'Orders',
            count: orderCount,
            color: _AppColors.orderGreen,
          ),
          _buildVerticalDivider(),
          _buildSummaryBadge(
            icon: Icons.local_offer,
            label: 'Promos',
            count: promoCount,
            color: _AppColors.promoAmber,
          ),
          _buildVerticalDivider(),
          _buildSummaryBadge(
            icon: Icons.shopping_bag_outlined,
            label: 'Products',
            count: productCount,
            color: _AppColors.productBlue,
          ),
          _buildVerticalDivider(),
          _buildSummaryBadge(
            icon: Icons.notifications_outlined,
            label: 'System',
            count: systemCount,
            color: _AppColors.systemPurple,
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryBadge({
    required IconData icon,
    required String label,
    required int count,
    required Color color,
  }) {
    return Expanded(
      child: Column(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              if (count > 0)
                Positioned(
                  top: -5,
                  right: -5,
                  child: Container(
                    width: 18,
                    height: 18,
                    decoration: const BoxDecoration(
                      color: _AppColors.danger,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '$count',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.8),
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVerticalDivider() {
    return Container(
      width: 1,
      height: 40,
      color: Colors.white.withValues(alpha: 0.15),
    );
  }

  // ── Filter Tab Bar ─────────────────────────────────────────────────────────
  Widget _buildFilterTabBar() {
    final filters = [
      _FilterTab(
        filter: NotificationFilter.all,
        label: 'All',
        icon: Icons.grid_view,
      ),
      _FilterTab(
        filter: NotificationFilter.unread,
        label: 'Unread',
        icon: Icons.notifications_active,
      ),
      _FilterTab(
        filter: NotificationFilter.orders,
        label: 'Orders',
        icon: Icons.inventory_2_outlined,
      ),
      _FilterTab(
        filter: NotificationFilter.promos,
        label: 'Promos',
        icon: Icons.local_offer,
      ),
      _FilterTab(
        filter: NotificationFilter.products,
        label: 'Products',
        icon: Icons.shopping_bag_outlined,
      ),
      _FilterTab(
        filter: NotificationFilter.system,
        label: 'System',
        icon: Icons.notifications_outlined,
      ),
    ];

    return Container(
      margin: const EdgeInsets.only(top: 16),
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: filters.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final tab = filters[index];
          final isActive = _activeFilter == tab.filter;
          final count = _filterCount(tab.filter);

          return GestureDetector(
            onTap: () {
              setState(() => _activeFilter = tab.filter);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 0),
              decoration: BoxDecoration(
                color: isActive ? _AppColors.primary : _AppColors.surface,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(
                  color: isActive ? _AppColors.primary : _AppColors.divider,
                  width: 1.2,
                ),
                boxShadow: isActive
                    ? [
                        BoxShadow(
                          color: _AppColors.primary.withValues(alpha: 0.30),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ]
                    : [],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    tab.icon,
                    size: 14,
                    color: isActive ? Colors.white : _AppColors.textSecondary,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    tab.label,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                      color: isActive ? Colors.white : _AppColors.textSecondary,
                      letterSpacing: 0.2,
                    ),
                  ),
                  if (count > 0) ...[
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color: isActive
                            ? Colors.white.withValues(alpha: 0.25)
                            : _AppColors.danger,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        count > 99 ? '99+' : '$count',
                        style: const TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Section Header ─────────────────────────────────────────────────────────
  Widget _buildSectionHeader(String title) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 4),
        child: Row(
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: _AppColors.textSecondary,
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Container(height: 1, color: _AppColors.divider),
            ),
          ],
        ),
      ),
    );
  }

  // ── Notification List ──────────────────────────────────────────────────────
  Widget _buildNotificationList(List<NotificationItem> items) {
    return SliverPadding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      sliver: SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) {
            final notification = items[index];
            return _NotificationTile(
              key: ValueKey(notification.id),
              notification: notification,
              onTap: () => _onNotificationTap(notification),
              onDismiss: () => _dismissNotification(notification.id),
            );
          },
          childCount: items.length,
        ),
      ),
    );
  }

  // ── Empty Filter State ─────────────────────────────────────────────────────
  Widget _buildEmptyFilterState() {
    final isUnread = _activeFilter == NotificationFilter.unread;

    return Container(
      margin: const EdgeInsets.only(top: 60),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: _AppColors.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Icon(
              isUnread ? Icons.check : Icons.inbox,
              size: 36,
              color: _AppColors.primary,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            isUnread ? 'All caught up!' : 'Nothing here',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: _AppColors.textPrimary,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            isUnread
                ? 'No unread notifications right now.'
                : 'No notifications in this category.',
            style: const TextStyle(
              fontSize: 13,
              color: _AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  // ── Actions ────────────────────────────────────────────────────────────────
  void _onNotificationTap(NotificationItem notification) async {
    if (!notification.isRead) {
      final notificationId = int.tryParse(notification.id);
      if (notificationId != null) {
        await ApiService.markNotificationRead(notificationId);
      }
    }
    setState(() {
      final idx = _notifications.indexWhere((n) => n.id == notification.id);
      if (idx != -1) {
        _notifications[idx] = notification.copyWith(isRead: true);
      }
    });

    // Deep link navigation
    if (notification.link != null && notification.link!.isNotEmpty) {
      _navigateToLink(notification.link!, notification.orderId);
    } else if (notification.orderId != null) {
      _navigateToOrder(notification.orderId!);
    }
  }

  void _navigateToLink(String link, int? orderId) {
    // Navigate based on link pattern
    if (link.contains('/buyer/orders/') || link.contains('/buyer/order/')) {
      final orderIdStr = link.split('/').last;
      final oid = int.tryParse(orderIdStr) ?? orderId;
      if (oid != null) _navigateToOrder(oid);
    } else if (link.contains('/seller/products/')) {
      Navigator.pushNamed(context, '/seller/products');
    } else if (link.contains('/rider/')) {
      Navigator.pushNamed(context, '/rider/orders');
    } else if (link.contains('/buyer/wallet')) {
      Navigator.pushNamed(context, '/buyer/wallet');
    } else if (link.contains('/seller/returns/')) {
      final returnIdStr = link.split('/').last;
      Navigator.pushNamed(context, '/seller/returns', arguments: {'return_id': returnIdStr});
    } else if (link.contains('/shop')) {
      Navigator.pushNamed(context, '/shop');
    } else if (link.contains('/login')) {
      Navigator.pushNamed(context, '/login');
    } else if (link.contains('/rider/earnings')) {
      Navigator.pushNamed(context, '/rider/earnings');
    } else if (link.contains('/rider/orders/available')) {
      Navigator.pushNamed(context, '/rider/orders');
    }
  }

  void _navigateToOrder(int orderId) {
    Navigator.pushNamed(context, '/buyer/order-details', arguments: {'order_id': orderId});
  }

  void _dismissNotification(String id) async {
    final notificationId = int.tryParse(id);
    if (notificationId != null) {
      await ApiService.deleteNotification(notificationId);
    }
    setState(() => _notifications.removeWhere((n) => n.id == id));
  }

  void _markAllAsRead() async {
    await ApiService.markAllNotificationsRead();
    setState(() {
      _notifications = _notifications.map((n) => n.copyWith(isRead: true)).toList();
    });
  }

  void _showSettingsSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: _AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => _NotificationSettingsSheet(
        onClearRead: _clearReadNotifications,
      ),
    );
  }

  void _clearReadNotifications() async {
    final result = await ApiService.clearAllReadNotifications();
    if (result['success'] == true) {
      final deleted = (result['deleted_count'] as num?)?.toInt() ?? 0;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Cleared $deleted read notifications'),
            backgroundColor: _AppColors.orderGreen,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
      }
      _loadNotifications(refresh: true);
    }
  }
}

// ─── Filter Tab Model ────────────────────────────────────────────────────────
class _FilterTab {
  final NotificationFilter filter;
  final String label;
  final IconData icon;

  _FilterTab({
    required this.filter,
    required this.label,
    required this.icon,
  });
}

// ─── Notification Tile ───────────────────────────────────────────────────────
class _NotificationTile extends StatelessWidget {
  final NotificationItem notification;
  final VoidCallback onTap;
  final VoidCallback onDismiss;

  const _NotificationTile({
    super.key,
    required this.notification,
    required this.onTap,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    final color = _typeColor;

    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      background: Container(
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(
          color: _AppColors.danger,
          borderRadius: BorderRadius.circular(16),
        ),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.delete_outline, color: Colors.white, size: 20),
            SizedBox(height: 4),
            Text(
              'Delete',
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
      onDismissed: (_) => onDismiss(),
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          margin: const EdgeInsets.only(bottom: 10),
          decoration: BoxDecoration(
            color:
                notification.isRead ? _AppColors.surface : _AppColors.unreadBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: notification.isRead
                  ? _AppColors.divider
                  : _AppColors.unreadBorder,
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: notification.isRead
                    ? Colors.black.withValues(alpha: 0.03)
                    : _AppColors.primary.withValues(alpha: 0.07),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Icon
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(_typeIcon, color: color, size: 22),
                ),
                const SizedBox(width: 14),
                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              notification.title,
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: notification.isRead
                                    ? FontWeight.w600
                                    : FontWeight.w800,
                                color: _AppColors.textPrimary,
                                letterSpacing: -0.2,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            notification.time,
                            style: const TextStyle(
                              fontSize: 11,
                              color: _AppColors.textMuted,
                              fontWeight: FontWeight.w400,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 5),
                      Text(
                        notification.message,
                        style: const TextStyle(
                          fontSize: 13,
                          color: _AppColors.textSecondary,
                          height: 1.4,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _typeLabel,
                              style: TextStyle(
                                fontSize: 10,
                                color: color,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.4,
                              ),
                            ),
                          ),
                          if (notification.orderId != null) ...[
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                              decoration: BoxDecoration(
                                color: _AppColors.primary.withValues(alpha: 0.08),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.tag, size: 10, color: _AppColors.primary.withValues(alpha: 0.6)),
                                  const SizedBox(width: 2),
                                  Text(
                                    '${notification.orderId}',
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: _AppColors.primary.withValues(alpha: 0.8),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          const Spacer(),
                          if (!notification.isRead)
                            Row(
                              children: [
                                Container(
                                  width: 7,
                                  height: 7,
                                  decoration: const BoxDecoration(
                                    color: _AppColors.primary,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 5),
                                const Text(
                                  'New',
                                  style: TextStyle(
                                    fontSize: 11,
                                    color: _AppColors.primary,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ],
                            )
                          else
                            const Text(
                              'Read',
                              style: TextStyle(
                                fontSize: 11,
                                color: _AppColors.textMuted,
                                fontWeight: FontWeight.w500,
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
        ),
      ),
    );
  }

  Color get _typeColor {
    switch (notification.type) {
      case NotificationType.order:
        return _AppColors.orderGreen;
      case NotificationType.promotion:
        return _AppColors.promoAmber;
      case NotificationType.product:
        return _AppColors.productBlue;
      case NotificationType.system:
        return _AppColors.systemPurple;
      case NotificationType.payment:
        return _AppColors.paymentTeal;
    }
  }

  IconData get _typeIcon {
    switch (notification.type) {
      case NotificationType.order:
        return Icons.inventory_2_outlined;
      case NotificationType.promotion:
        return Icons.local_offer;
      case NotificationType.product:
        return Icons.shopping_bag_outlined;
      case NotificationType.system:
        return Icons.shield;
      case NotificationType.payment:
        return Icons.credit_card;
    }
  }

  String get _typeLabel {
    switch (notification.type) {
      case NotificationType.order:
        return 'ORDER';
      case NotificationType.promotion:
        return 'PROMO';
      case NotificationType.product:
        return 'PRODUCT';
      case NotificationType.system:
        return 'SYSTEM';
      case NotificationType.payment:
        return 'PAYMENT';
    }
  }
}

// ─── Notification Settings Sheet ────────────────────────────────────────────
class _NotificationSettingsSheet extends StatefulWidget {
  final VoidCallback onClearRead;

  const _NotificationSettingsSheet({required this.onClearRead});

  @override
  State<_NotificationSettingsSheet> createState() => _NotificationSettingsSheetState();
}

class _NotificationSettingsSheetState extends State<_NotificationSettingsSheet> {
  bool _orderUpdates = true;
  bool _promotions = true;
  bool _productUpdates = true;
  bool _systemAlerts = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final result = await ApiService.getNotificationSettings();
    if (result['success'] == true && result['settings'] != null) {
      final settings = result['settings'] as Map<String, dynamic>;
      setState(() {
        _orderUpdates = settings['order_updates'] ?? true;
        _promotions = settings['promotions'] ?? true;
        _productUpdates = settings['product_updates'] ?? true;
        _systemAlerts = settings['system_alerts'] ?? true;
      });
    }
  }

  Future<void> _saveSettings() async {
    setState(() => _isLoading = true);
    await ApiService.updateNotificationSettings({
      'order_updates': _orderUpdates,
      'promotions': _promotions,
      'product_updates': _productUpdates,
      'system_alerts': _systemAlerts,
    });
    setState(() => _isLoading = false);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Settings saved'),
          backgroundColor: _AppColors.orderGreen,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: _AppColors.divider,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Notification Settings',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _AppColors.textPrimary),
            ),
            const SizedBox(height: 20),
            _buildToggle('Order Updates', 'Get notified about order status changes', _orderUpdates, (v) => setState(() => _orderUpdates = v)),
            _buildToggle('Promotions', 'Receive deals and promotional offers', _promotions, (v) => setState(() => _promotions = v)),
            _buildToggle('Product Updates', 'Stock alerts and product approvals', _productUpdates, (v) => setState(() => _productUpdates = v)),
            _buildToggle('System & Payments', 'System announcements and payment alerts', _systemAlerts, (v) => setState(() => _systemAlerts = v)),
            const SizedBox(height: 16),
            const Divider(color: _AppColors.divider),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: () {
                widget.onClearRead();
                Navigator.pop(context);
              },
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: _AppColors.danger.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: _AppColors.danger.withValues(alpha: 0.2)),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.delete_outline, color: _AppColors.danger, size: 18),
                    SizedBox(width: 8),
                    Text('Clear All Read Notifications', style: TextStyle(color: _AppColors.danger, fontWeight: FontWeight.w600, fontSize: 14)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: _isLoading ? null : _saveSettings,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [_AppColors.primaryDark, _AppColors.primary]),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Center(
                  child: _isLoading
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Save Settings', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 15)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToggle(String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: _AppColors.textPrimary)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: _AppColors.textSecondary)),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeThumbColor: _AppColors.primary,
          ),
        ],
      ),
    );
  }
}

