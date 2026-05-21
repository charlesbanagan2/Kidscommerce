import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/api_service.dart';

class RiderNotificationScreen extends StatefulWidget {
  const RiderNotificationScreen({super.key});

  @override
  State<RiderNotificationScreen> createState() =>
      _RiderNotificationScreenState();
}

class _RiderNotificationScreenState extends State<RiderNotificationScreen>
    with TickerProviderStateMixin {
  late AnimationController _animController;
  late TabController _tabController;
  List<_NotifData> _notifications = [];
  bool _isLoading = false;
  int _selectedTab = 0; // 0=All, 1=Unread, 2=Read

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);
  static const Color _violet = Color(0xFF7C3AED);
  static const Color _blue = Color(0xFF2563EB);
  static const Color _amber = Color(0xFFD97706);
  static const Color _red = Color(0xFFDC2626);

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..forward();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) return;
      HapticFeedback.selectionClick();
      setState(() => _selectedTab = _tabController.index);
    });
    _loadNotifications();
  }

  @override
  void dispose() {
    _animController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  void _loadNotifications() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.getNotifications();
      if (response['success'] == true) {
        final List<dynamic> notifications = response['notifications'] ?? [];
        setState(() {
          _notifications = notifications.map((notif) {
            final type = _parseNotificationType(notif['type']);
            return _NotifData(
              id: notif['id']?.toString() ?? '',
              type: type,
              title: notif['title'] ?? 'Notification',
              body: notif['message'] ?? '',
              time: _parseTime(notif['created_at']),
              isRead: notif['is_read'] ?? false,
            );
          }).toList()
            ..sort((a, b) => b.time.compareTo(a.time)); // Sort by time descending (latest first)
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

  _NotifType _parseNotificationType(String? type) {
    if (type == null) return _NotifType.statusChanged;
    final lowerType = type.toLowerCase();
    if (lowerType.contains('new') || lowerType.contains('order')) {
      return _NotifType.newOrder;
    } else if (lowerType.contains('transit')) {
      return _NotifType.inTransit;
    } else if (lowerType.contains('deliver')) {
      return _NotifType.delivered;
    } else if (lowerType.contains('payment') || lowerType.contains('earn')) {
      return _NotifType.paymentReceived;
    } else if (lowerType.contains('bonus')) {
      return _NotifType.bonusEarned;
    } else {
      return _NotifType.statusChanged;
    }
  }

  DateTime _parseTime(String? createdAt) {
    if (createdAt == null) return DateTime.now();
    try {
      return DateTime.parse(createdAt);
    } catch (e) {
      return DateTime.now();
    }
  }

  int get _unreadCount => _notifications.where((n) => !n.isRead).length;
  int get _readCount => _notifications.where((n) => n.isRead).length;

  List<_NotifData> get _filteredNotifications {
    switch (_selectedTab) {
      case 1:
        return _notifications.where((n) => !n.isRead).toList();
      case 2:
        return _notifications.where((n) => n.isRead).toList();
      default:
        return _notifications;
    }
  }

  void _markAsRead(String id) async {
    HapticFeedback.lightImpact();
    final notificationId = int.tryParse(id);
    if (notificationId != null) {
      await ApiService.markNotificationRead(notificationId);
    }
    setState(() {
      final idx = _notifications.indexWhere((n) => n.id == id);
      if (idx != -1) {
        _notifications[idx] = _notifications[idx].copyWith(isRead: true);
      }
    });
  }

  void _markAllAsRead() async {
    HapticFeedback.mediumImpact();
    await ApiService.markAllNotificationsRead();
    setState(() {
      _notifications =
          _notifications.map((n) => n.copyWith(isRead: true)).toList();
    });
  }

  void _deleteNotification(String id) {
    HapticFeedback.heavyImpact();
    setState(() {
      _notifications.removeWhere((n) => n.id == id);
    });
  }

  // ─── Type helpers ─────────────────────────────────────────────────────────────

  IconData _iconFor(_NotifType type) {
    switch (type) {
      case _NotifType.newOrder:
        return Icons.add_shopping_cart_rounded;
      case _NotifType.inTransit:
        return Icons.local_shipping_rounded;
      case _NotifType.delivered:
        return Icons.check_circle_rounded;
      case _NotifType.statusChanged:
        return Icons.update_rounded;
      case _NotifType.paymentReceived:
        return Icons.account_balance_wallet_rounded;
      case _NotifType.bonusEarned:
        return Icons.card_giftcard_rounded;
    }
  }

  Color _colorFor(_NotifType type) {
    switch (type) {
      case _NotifType.newOrder:
        return _primary;
      case _NotifType.inTransit:
        return _amber;
      case _NotifType.delivered:
        return _green;
      case _NotifType.statusChanged:
        return _violet;
      case _NotifType.paymentReceived:
        return _blue;
      case _NotifType.bonusEarned:
        return const Color(0xFFDB2777);
    }
  }

  Color _bgFor(_NotifType type) {
    switch (type) {
      case _NotifType.newOrder:
        return const Color(0xFFFFF7ED);
      case _NotifType.inTransit:
        return const Color(0xFFFFFBEB);
      case _NotifType.delivered:
        return const Color(0xFFECFDF5);
      case _NotifType.statusChanged:
        return const Color(0xFFF5F3FF);
      case _NotifType.paymentReceived:
        return const Color(0xFFEFF6FF);
      case _NotifType.bonusEarned:
        return const Color(0xFFFDF2F8);
    }
  }

  Color _borderFor(_NotifType type) {
    switch (type) {
      case _NotifType.newOrder:
        return const Color(0xFFFFDDB9);
      case _NotifType.inTransit:
        return const Color(0xFFFDE68A);
      case _NotifType.delivered:
        return const Color(0xFFA7F3D0);
      case _NotifType.statusChanged:
        return const Color(0xFFDDD6FE);
      case _NotifType.paymentReceived:
        return const Color(0xFFBFDBFE);
      case _NotifType.bonusEarned:
        return const Color(0xFFFBCFE8);
    }
  }

  String _labelFor(_NotifType type) {
    switch (type) {
      case _NotifType.newOrder:
        return 'NEW ORDER';
      case _NotifType.inTransit:
        return 'IN TRANSIT';
      case _NotifType.delivered:
        return 'DELIVERED';
      case _NotifType.statusChanged:
        return 'STATUS';
      case _NotifType.paymentReceived:
        return 'PAYMENT';
      case _NotifType.bonusEarned:
        return 'BONUS';
    }
  }

  // ─── Time formatting ──────────────────────────────────────────────────────────

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays == 1) return 'Yesterday';
    return '${diff.inDays}d ago';
  }

  // ─── Date group label ─────────────────────────────────────────────────────────

  String _groupLabel(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inHours < 24) return 'Today';
    if (diff.inDays == 1) return 'Yesterday';
    return 'Earlier';
  }

  // ─── Build ────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredNotifications;
    return Scaffold(
      backgroundColor: _bg,
      body: RefreshIndicator(
        color: _primary,
        strokeWidth: 2.5,
        onRefresh: () async => _loadNotifications(),
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            _buildAppBar(),
            SliverToBoxAdapter(child: _buildFilterTabBar()),
            if (_unreadCount > 0 && !_isLoading && _selectedTab == 0)
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
                  child: _buildUnreadBanner(),
                ),
              ),
            if (_isLoading)
              const SliverFillRemaining(
                child: Center(
                  child: CircularProgressIndicator(
                      color: _primary, strokeWidth: 3),
                ),
              )
            else if (filtered.isEmpty)
              SliverFillRemaining(child: _buildEmptyState())
            else
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) => _buildListItem(index, filtered),
                    childCount: filtered.length,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ─── App Bar ──────────────────────────────────────────────────────────────────

  Widget _buildAppBar() {
    return SliverAppBar(
      expandedHeight: 0,
      floating: true,
      snap: true,
      backgroundColor: _surface,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      shadowColor: Colors.black.withValues(alpha: 0.08),
      surfaceTintColor: Colors.transparent,
      toolbarHeight: 64,
      leading: IconButton(
        onPressed: () {
          HapticFeedback.lightImpact();
          Navigator.pop(context);
        },
        icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
        color: const Color(0xFF475569),
      ),
      title: Row(children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(10),
            boxShadow: [
              BoxShadow(
                color: _primary.withValues(alpha: 0.3),
                blurRadius: 6,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Icon(Icons.notifications_rounded,
              color: Colors.white, size: 16),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Flexible(
                child: Text(
                  'Notifications',
                  style: TextStyle(
                    color: Color(0xFF0F172A),
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.4,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (_unreadCount > 0) ...[
                const SizedBox(width: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: _red,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '$_unreadCount',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ]),
            const Text(
              'Order & earnings updates',
              style: TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 10,
                fontWeight: FontWeight.w500,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ]),
        ),
      ]),
      actions: [
        if (_unreadCount > 0)
          GestureDetector(
            onTap: _markAllAsRead,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 11, vertical: 8),
              margin: const EdgeInsets.only(right: 14),
              decoration: BoxDecoration(
                color: _primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _primary.withValues(alpha: 0.2)),
              ),
              child: const Text(
                'Mark all read',
                style: TextStyle(
                  color: _primary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
      ],
    );
  }

  // ─── Filter Tab Bar ───────────────────────────────────────────────────────────

  Widget _buildFilterTabBar() {
    final tabs = [
      _TabInfo(label: 'All', count: _notifications.length, index: 0),
      _TabInfo(label: 'Unread', count: _unreadCount, index: 1),
      _TabInfo(label: 'Read', count: _readCount, index: 2),
    ];

    return Container(
      color: _surface,
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Container(
        height: 44,
        decoration: BoxDecoration(
          color: _bg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _border),
        ),
        child: Row(
          children: tabs.map((tab) {
            final isActive = _selectedTab == tab.index;
            return Expanded(
              child: GestureDetector(
                onTap: () {
                  HapticFeedback.selectionClick();
                  setState(() => _selectedTab = tab.index);
                  _tabController.animateTo(tab.index);
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutCubic,
                  margin: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: isActive ? _surface : Colors.transparent,
                    borderRadius: BorderRadius.circular(11),
                    border: isActive
                        ? Border.all(color: _primary.withValues(alpha: 0.18))
                        : null,
                    boxShadow: isActive
                        ? [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.06),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ]
                        : null,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      AnimatedDefaultTextStyle(
                        duration: const Duration(milliseconds: 200),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight:
                              isActive ? FontWeight.w800 : FontWeight.w500,
                          color: isActive ? _primary : _textSub,
                        ),
                        child: Text(tab.label),
                      ),
                      if (tab.count > 0) ...[
                        const SizedBox(width: 5),
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: isActive
                                ? _primary
                                : _textSub.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${tab.count}',
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.w800,
                              color: isActive ? Colors.white : _textSub,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  // ─── Unread Banner ────────────────────────────────────────────────────────────

  Widget _buildUnreadBanner() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            _primary.withValues(alpha: 0.08),
            _primary.withValues(alpha: 0.04),
          ],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _primary.withValues(alpha: 0.18)),
      ),
      child: Row(children: [
        Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
            color: _primary.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.mark_email_unread_rounded,
              color: _primary, size: 16),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: RichText(
            text: TextSpan(
              style: const TextStyle(
                  fontSize: 12,
                  color: _textSub,
                  fontWeight: FontWeight.w500),
              children: [
                TextSpan(
                  text: '$_unreadCount unread ',
                  style: const TextStyle(
                    color: _primary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const TextSpan(
                    text: 'notification(s) — tap to mark as read.'),
              ],
            ),
          ),
        ),
        GestureDetector(
          onTap: _markAllAsRead,
          child: Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: _primary,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Text(
              'Clear all',
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
      ]),
    );
  }

  // ─── List Item ────────────────────────────────────────────────────────────────

  Widget _buildListItem(int index, List<_NotifData> list) {
    final notif = list[index];
    final color = _colorFor(notif.type);
    final bgColor = _bgFor(notif.type);
    final borderColor = _borderFor(notif.type);
    final icon = _iconFor(notif.type);
    final label = _labelFor(notif.type);

    Widget? groupHeader;
    if (index == 0) {
      groupHeader = _buildGroupHeader(_groupLabel(notif.time));
    } else {
      final prevGroup = _groupLabel(list[index - 1].time);
      final currGroup = _groupLabel(notif.time);
      if (prevGroup != currGroup) {
        groupHeader = _buildGroupHeader(currGroup);
      }
    }

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Duration(milliseconds: 280 + (index % 8) * 55),
      curve: Curves.easeOutCubic,
      builder: (context, v, child) => Opacity(
        opacity: v,
        child:
            Transform.translate(offset: Offset(0, 18 * (1 - v)), child: child),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (groupHeader != null) groupHeader,
          Dismissible(
            key: Key('${notif.id}_$_selectedTab'),
            direction: DismissDirection.endToStart,
            confirmDismiss: (direction) async {
              HapticFeedback.heavyImpact();
              return true;
            },
            background: Container(
              margin: const EdgeInsets.only(bottom: 10),
              decoration: BoxDecoration(
                color: _red.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _red.withValues(alpha: 0.2)),
              ),
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: 22),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: _red.withValues(alpha: 0.12),
                      shape: BoxShape.circle,
                    ),
                    child:
                        const Icon(Icons.delete_rounded, color: _red, size: 20),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Delete',
                    style: TextStyle(
                      color: _red,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
            onDismissed: (_) => _deleteNotification(notif.id),
            child: GestureDetector(
              onTap: () => _markAsRead(notif.id),
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                decoration: BoxDecoration(
                  color: notif.isRead ? _surface : const Color(0xFFFFFBF5),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: notif.isRead
                        ? _border
                        : _primary.withValues(alpha: 0.22),
                    width: notif.isRead ? 1 : 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: notif.isRead
                          ? Colors.black.withValues(alpha: 0.03)
                          : _primary.withValues(alpha: 0.06),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(children: [
                  // ── Colored top accent bar for unread ──
                  if (!notif.isRead)
                    Container(
                      height: 3,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [color, color.withValues(alpha: 0.3)],
                        ),
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(20),
                          topRight: Radius.circular(20),
                        ),
                      ),
                    ),
                  Padding(
                    padding:
                        EdgeInsets.fromLTRB(14, notif.isRead ? 14 : 12, 14, 14),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // ── Icon bubble with unread dot ──
                        Stack(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: bgColor,
                                borderRadius: BorderRadius.circular(14),
                                border:
                                    Border.all(color: borderColor, width: 1.5),
                              ),
                              child: Icon(icon, color: color, size: 20),
                            ),
                            if (!notif.isRead)
                              Positioned(
                                top: 0,
                                right: 0,
                                child: Container(
                                  width: 10,
                                  height: 10,
                                  decoration: BoxDecoration(
                                    color: _primary,
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                        color: _surface, width: 1.5),
                                    boxShadow: [
                                      BoxShadow(
                                        color:
                                            _primary.withValues(alpha: 0.45),
                                        blurRadius: 4,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(width: 12),
                        // ── Content ──
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: bgColor,
                                    borderRadius: BorderRadius.circular(7),
                                    border: Border.all(
                                        color: borderColor, width: 1),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Container(
                                        width: 5,
                                        height: 5,
                                        decoration: BoxDecoration(
                                          color: color,
                                          shape: BoxShape.circle,
                                        ),
                                      ),
                                      const SizedBox(width: 5),
                                      Text(
                                        label,
                                        style: TextStyle(
                                          color: color,
                                          fontSize: 9,
                                          fontWeight: FontWeight.w800,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const Spacer(),
                                Row(children: [
                                  const Icon(Icons.access_time_rounded,
                                      size: 11, color: _textSub),
                                  const SizedBox(width: 3),
                                  Text(
                                    _formatTime(notif.time),
                                    style: const TextStyle(
                                      color: _textSub,
                                      fontSize: 11,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ]),
                              ]),
                              const SizedBox(height: 8),
                              Text(
                                notif.title,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: notif.isRead
                                      ? FontWeight.w600
                                      : FontWeight.w800,
                                  color: _textPrimary,
                                  letterSpacing: -0.2,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                notif.body,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: _textSub,
                                  height: 1.5,
                                  fontWeight: FontWeight.w400,
                                ),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 10),
                              Row(children: [
                                if (!notif.isRead) ...[
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 9, vertical: 5),
                                    decoration: BoxDecoration(
                                      color:
                                          _primary.withValues(alpha: 0.08),
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                          color: _primary
                                              .withValues(alpha: 0.18)),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Container(
                                          width: 6,
                                          height: 6,
                                          decoration: BoxDecoration(
                                            color: _primary,
                                            shape: BoxShape.circle,
                                            boxShadow: [
                                              BoxShadow(
                                                color: _primary.withValues(
                                                    alpha: 0.5),
                                                blurRadius: 4,
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(width: 5),
                                        const Text(
                                          'Unread',
                                          style: TextStyle(
                                            color: _primary,
                                            fontSize: 10,
                                            fontWeight: FontWeight.w700,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ] else ...[
                                  Row(children: [
                                    Icon(Icons.check_circle_rounded,
                                        size: 12,
                                        color: _green.withValues(alpha: 0.7)),
                                    const SizedBox(width: 4),
                                    Text(
                                      'Read',
                                      style: TextStyle(
                                        color:
                                            _textSub.withValues(alpha: 0.6),
                                        fontSize: 10,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ]),
                                ],
                                const Spacer(),
                                Row(children: [
                                  const Icon(Icons.swipe_left_rounded,
                                      size: 12, color: Color(0xFFCBD5E1)),
                                  const SizedBox(width: 4),
                                  Text(
                                    'Swipe to delete',
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: _textSub.withValues(alpha: 0.5),
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ]),
                              ]),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ]),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─── Group Header ─────────────────────────────────────────────────────────────

  Widget _buildGroupHeader(String label) {
    return Padding(
      padding: const EdgeInsets.only(top: 6, bottom: 8, left: 2),
      child: Row(children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: _textSub.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: _textSub,
              letterSpacing: 0.3,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Container(
            height: 1,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [_border, _border.withValues(alpha: 0)],
              ),
            ),
          ),
        ),
      ]),
    );
  }

  // ─── Empty State ──────────────────────────────────────────────────────────────

  Widget _buildEmptyState() {
    final isFilteredEmpty =
        _notifications.isNotEmpty && _filteredNotifications.isEmpty;

    final String title = isFilteredEmpty ? 'Nothing here' : 'All caught up!';
    final String subtitle = isFilteredEmpty
        ? (_selectedTab == 1
            ? 'You have no unread notifications.\nTap "All" to see everything.'
            : 'You have no read notifications yet.\nThey will appear here once viewed.')
        : 'No notifications yet.\nNew order and earnings updates\nwill appear here.';
    final IconData emptyIcon = isFilteredEmpty
        ? (_selectedTab == 1
            ? Icons.drafts_rounded
            : Icons.done_all_rounded)
        : Icons.notifications_off_rounded;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.04),
                    shape: BoxShape.circle,
                  ),
                ),
                Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.06),
                    shape: BoxShape.circle,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    color: _surface,
                    shape: BoxShape.circle,
                    border: Border.all(color: _border, width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.05),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Icon(emptyIcon,
                      size: 40, color: const Color(0xFFCBD5E1)),
                ),
              ],
            ),
            const SizedBox(height: 28),
            Text(
              title,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: _textPrimary,
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: _textSub,
                fontSize: 13,
                height: 1.65,
              ),
            ),
            const SizedBox(height: 28),
            if (!isFilteredEmpty)
              GestureDetector(
                onTap: () {
                  HapticFeedback.lightImpact();
                  _loadNotifications();
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 24, vertical: 13),
                  decoration: BoxDecoration(
                    color: _primary,
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.35),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.refresh_rounded,
                          color: Colors.white, size: 16),
                      SizedBox(width: 8),
                      Text(
                        'Refresh',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              )
            else
              GestureDetector(
                onTap: () {
                  HapticFeedback.selectionClick();
                  setState(() => _selectedTab = 0);
                  _tabController.animateTo(0);
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 24, vertical: 13),
                  decoration: BoxDecoration(
                    color: _bg,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: _border),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.list_rounded, color: _textSub, size: 16),
                      SizedBox(width: 8),
                      Text(
                        'View All',
                        style: TextStyle(
                          color: _textSub,
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                        ),
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
}

// ─── Helper models ────────────────────────────────────────────────────────────

class _TabInfo {
  final String label;
  final int count;
  final int index;
  const _TabInfo(
      {required this.label, required this.count, required this.index});
}

// ─── Data models ──────────────────────────────────────────────────────────────

enum _NotifType {
  newOrder,
  inTransit,
  delivered,
  statusChanged,
  paymentReceived,
  bonusEarned,
}

class _NotifData {
  final String id;
  final _NotifType type;
  final String title;
  final String body;
  final DateTime time;
  final bool isRead;

  const _NotifData({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.time,
    required this.isRead,
  });

  _NotifData copyWith({bool? isRead}) => _NotifData(
        id: id,
        type: type,
        title: title,
        body: body,
        time: time,
        isRead: isRead ?? this.isRead,
      );
}