import 'dart:async';
import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../models/order.dart';
import '../../widgets/skeleton_loader.dart';
import 'rider_chat_screen.dart';
import 'rider_notifications_screen.dart';

class RiderDashboardScreen extends StatefulWidget {
  const RiderDashboardScreen({super.key});

  @override
  State<RiderDashboardScreen> createState() => _RiderDashboardScreenState();
}

class _RiderDashboardScreenState extends State<RiderDashboardScreen>
    with SingleTickerProviderStateMixin {
  List<Order> _orders = [];
  bool _isLoading = true;
  String? _error;
  double _totalEarnings = 0;
  double _earningsToday = 0;
  double _earningsWeek = 0;
  double _earningsMonth = 0;
  String _userName = 'Rider';
  int _unreadNotificationCount = 0;
  late AnimationController _animController;

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
    _fetchDashboardData();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _fetchDashboardData() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final myOrders = await ApiService.getRiderOrders();
      final earningsPayload = await ApiService.getRiderEarnings();
      final notifResponse = await ApiService.getNotifications();

      _totalEarnings = (earningsPayload['total'] as num?)?.toDouble() ?? 0.0;
      _earningsToday = (earningsPayload['today'] as num?)?.toDouble() ?? 0.0;
      _earningsWeek = (earningsPayload['week'] as num?)?.toDouble() ?? 0.0;
      _earningsMonth = (earningsPayload['month'] as num?)?.toDouble() ?? 0.0;

      final orders = myOrders.map((json) => Order.fromJson(json)).toList();

      if (notifResponse['success'] == true) {
        final notifications = notifResponse['notifications'] as List? ?? [];
        _unreadNotificationCount =
            notifications.where((n) => n['is_read'] == false).length;
      }

      if (mounted)
        setState(() {
          _orders = orders;
          _isLoading = false;
        });
    } catch (e) {
      if (mounted)
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
    }
  }

  List<Order> get _activeOrders => _orders
      .where((o) => o.status == 'in_transit' || o.status == 'to_ship')
      .toList();

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: _bg,
        body: Column(
          children: [
            // App bar skeleton
            Container(
              color: _surface,
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 12,
                bottom: 12,
                left: 16,
                right: 14,
              ),
              child: Row(
                children: [
                  SkeletonLoader(
                    width: 36,
                    height: 36,
                    borderRadius: BorderRadius.circular(11),
                  ),
                  const SizedBox(width: 11),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SkeletonLoader(
                          height: 17,
                          width: 120,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        const SizedBox(height: 4),
                        SkeletonLoader(
                          height: 11,
                          width: 140,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    ),
                  ),
                  SkeletonLoader(
                    width: 34,
                    height: 34,
                    borderRadius: BorderRadius.circular(11),
                  ),
                  const SizedBox(width: 6),
                  SkeletonLoader(
                    width: 34,
                    height: 34,
                    borderRadius: BorderRadius.circular(11),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const SizedBox(height: 12),
                    // Hero card skeleton
                    SkeletonLoader(
                      height: 120,
                      borderRadius: BorderRadius.circular(22),
                    ),
                    const SizedBox(height: 20),
                    // Earnings section skeleton
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            SkeletonLoader(
                              width: 28,
                              height: 28,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            const SizedBox(width: 9),
                            SkeletonLoader(
                              height: 15,
                              width: 140,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        // Total earnings card
                        SkeletonLoader(
                          height: 140,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        const SizedBox(height: 12),
                        // Mini cards row
                        Row(
                          children: [
                            Expanded(
                              child: SkeletonLoader(
                                height: 100,
                                borderRadius: BorderRadius.circular(18),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: SkeletonLoader(
                                height: 100,
                                borderRadius: BorderRadius.circular(18),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: SkeletonLoader(
                                height: 100,
                                borderRadius: BorderRadius.circular(18),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Active orders section skeleton
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            SkeletonLoader(
                              width: 28,
                              height: 28,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            const SizedBox(width: 9),
                            SkeletonLoader(
                              height: 15,
                              width: 120,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Order cards
                        SkeletonLoader(
                          height: 180,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        const SizedBox(height: 12),
                        SkeletonLoader(
                          height: 180,
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (_error != null) {
      return Scaffold(
        backgroundColor: _bg,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child:
                Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.red.shade100)),
                child: Icon(Icons.wifi_off_rounded,
                    size: 44, color: Colors.red.shade400),
              ),
              const SizedBox(height: 20),
              const Text('Connection error',
                  style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: _textPrimary,
                      letterSpacing: -0.3)),
              const SizedBox(height: 8),
              Text(_error!,
                  textAlign: TextAlign.center,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      color: _textSub, fontSize: 13, height: 1.5)),
              const SizedBox(height: 28),
              SizedBox(
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: _fetchDashboardData,
                  icon: const Icon(Icons.refresh_rounded, size: 17),
                  label: const Text('Try Again',
                      style:
                          TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                  style: ElevatedButton.styleFrom(
                      backgroundColor: _primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 28, vertical: 14),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14)),
                      elevation: 0),
                ),
              ),
            ]),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: _bg,
      body: RefreshIndicator(
        color: _primary,
        strokeWidth: 2.5,
        onRefresh: _fetchDashboardData,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            _buildSliverAppBar(),
            SliverToBoxAdapter(
              child: _buildHeroSection(),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  const SizedBox(height: 20),
                  _buildEarningsSection(),
                  const SizedBox(height: 24),
                  _buildActiveOrdersSection(),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliverAppBar() {
    return SliverAppBar(
      expandedHeight: 0,
      floating: true,
      snap: true,
      backgroundColor: _surface,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      shadowColor: Colors.black.withValues(alpha: 0.08),
      surfaceTintColor: Colors.transparent,
      toolbarHeight: 60,
      title: Row(children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(11),
            boxShadow: [
              BoxShadow(
                  color: _primary.withValues(alpha: 0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 3))
            ],
          ),
          child: const Icon(Icons.two_wheeler_rounded,
              color: Colors.white, size: 18),
        ),
        const SizedBox(width: 11),
        const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Dashboard',
              style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4)),
          Text('Track your deliveries',
              style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.w500)),
        ]),
      ]),
      actions: [
        GestureDetector(
          onTap: _fetchDashboardData,
          child: Container(
            padding: const EdgeInsets.all(8),
            margin: const EdgeInsets.only(right: 6),
            decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(11),
                border: Border.all(color: _border)),
            child: const Icon(Icons.refresh_rounded,
                size: 18, color: Color(0xFF475569)),
          ),
        ),
        Container(
          margin: const EdgeInsets.only(right: 14),
          child: GestureDetector(
            onTap: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const RiderNotificationScreen(),
                ),
              );
              _fetchDashboardData();
            },
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                      color: _bg,
                      borderRadius: BorderRadius.circular(11),
                      border: Border.all(color: _border)),
                  child: const Icon(Icons.notifications_rounded,
                      size: 18, color: Color(0xFF475569)),
                ),
                if (_unreadNotificationCount > 0)
                  Positioned(
                    top: -4,
                    right: -4,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: _red,
                        shape: BoxShape.circle,
                        border: Border.all(color: _surface, width: 1.5),
                        boxShadow: [
                          BoxShadow(
                            color: _red.withValues(alpha: 0.4),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Center(
                        child: Text(
                          _unreadNotificationCount > 99
                              ? '99+'
                              : '$_unreadNotificationCount',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// Redesigned hero — compact horizontal card with gradient, no huge avatar block
  Widget _buildHeroSection() {
    final initial = _userName.isNotEmpty ? _userName[0].toUpperCase() : 'R';

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
            colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
              color: _primary.withValues(alpha: 0.38),
              blurRadius: 24,
              offset: const Offset(0, 10))
        ],
      ),
      child: Stack(clipBehavior: Clip.none, children: [
        // Decorative circles
        Positioned(
            top: -18,
            right: -18,
            child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.07),
                    shape: BoxShape.circle))),
        Positioned(
            bottom: -24,
            right: 50,
            child: Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.05),
                    shape: BoxShape.circle))),

        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top row: avatar + name + status badge
                Row(children: [
                  // Compact avatar
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.22),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.4),
                            width: 1.5)),
                    child: Center(
                        child: Text(initial,
                            style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w800,
                                fontSize: 20))),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                      child: Text(_userName,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 17,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -0.4),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis)),
                  // Online pill
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.18),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.3))),
                    child: Row(mainAxisSize: MainAxisSize.min, children: [
                      Container(
                          width: 7,
                          height: 7,
                          decoration: const BoxDecoration(
                              color: Color(0xFF34D399),
                              shape: BoxShape.circle)),
                      const SizedBox(width: 5),
                      const Text('Online',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700)),
                    ]),
                  ),
                ]),
              ]),
        ),
      ]),
    );
  }

  Widget _buildEarningsSection() {
    final stats = [
      _StatData(
          'Total Earnings',
          '₱${_totalEarnings.toStringAsFixed(2)}',
          Icons.account_balance_wallet_rounded,
          _blue,
          const Color(0xFFEFF6FF),
          const Color(0xFFDBEAFE)),
      _StatData(
          'Today',
          '₱${_earningsToday.toStringAsFixed(2)}',
          Icons.wb_sunny_rounded,
          _green,
          const Color(0xFFECFDF5),
          const Color(0xFFD1FAE5)),
      _StatData(
          'This Week',
          '₱${_earningsWeek.toStringAsFixed(2)}',
          Icons.date_range_rounded,
          _violet,
          const Color(0xFFF5F3FF),
          const Color(0xFFEDE9FE)),
      _StatData(
          'This Month',
          '₱${_earningsMonth.toStringAsFixed(2)}',
          Icons.bar_chart_rounded,
          _primary,
          const Color(0xFFFFF7ED),
          const Color(0xFFFFEDD5)),
    ];

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _sectionHeader('Earnings Overview', Icons.insights_rounded),
      const SizedBox(height: 14),

      // Total earnings — full-width feature card
      TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: 1),
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOutCubic,
        builder: (context, v, child) => Opacity(
            opacity: v,
            child: Transform.translate(
                offset: Offset(0, 16 * (1 - v)), child: child)),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
              gradient: const LinearGradient(
                  colors: [_blue, const Color(0xFF1D4ED8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                    color: _blue.withValues(alpha: 0.25),
                    blurRadius: 20,
                    offset: const Offset(0, 8))
              ]),
          child: Row(children: [
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Row(children: [
                    Icon(Icons.account_balance_wallet_rounded,
                        color: Colors.white.withValues(alpha: 0.8), size: 14),
                    const SizedBox(width: 6),
                    Text('TOTAL EARNINGS',
                        style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.8),
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5)),
                  ]),
                  const SizedBox(height: 8),
                  Text('₱${_totalEarnings.toStringAsFixed(2)}',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 30,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.8)),
                  const SizedBox(height: 4),
                  Text('All-time accumulated earnings',
                      style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.65),
                          fontSize: 11,
                          fontWeight: FontWeight.w500)),
                ])),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16)),
              child: const Icon(Icons.trending_up_rounded,
                  color: Colors.white, size: 28),
            ),
          ]),
        ),
      ),

      const SizedBox(height: 12),

      // 3-column grid for Today / Week / Month
      Row(children: [
        for (int i = 1; i < stats.length; i++) ...[
          Expanded(
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: 1),
              duration: Duration(milliseconds: 420 + i * 80),
              curve: Curves.easeOutCubic,
              builder: (context, v, child) => Opacity(
                  opacity: v,
                  child: Transform.translate(
                      offset: Offset(0, 16 * (1 - v)), child: child)),
              child: _earningsMiniCard(stats[i]),
            ),
          ),
          if (i < stats.length - 1) const SizedBox(width: 10),
        ]
      ]),
    ]);
  }

  Widget _earningsMiniCard(_StatData s) {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 16),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: s.borderColor, width: 1.5),
          boxShadow: [
            BoxShadow(
                color: s.color.withValues(alpha: 0.07),
                blurRadius: 16,
                offset: const Offset(0, 6))
          ]),
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
                padding: const EdgeInsets.all(7),
                decoration: BoxDecoration(
                    color: s.bgColor, borderRadius: BorderRadius.circular(10)),
                child: Icon(s.icon, color: s.color, size: 15)),
            const SizedBox(height: 8),
            Text(s.label,
                style: TextStyle(
                    fontSize: 10,
                    color: s.color.withValues(alpha: 0.85),
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.2),
                maxLines: 1,
                overflow: TextOverflow.ellipsis),
            const SizedBox(height: 3),
            FittedBox(
              fit: BoxFit.scaleDown,
              alignment: Alignment.centerLeft,
              child: Text(s.value,
                  style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: _textPrimary,
                      letterSpacing: -0.4)),
            ),
          ]),
    );
  }

  Widget _buildActiveOrdersSection() {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Expanded(
            child:
                _sectionHeader('My Deliveries', Icons.local_shipping_rounded)),
        if (_activeOrders.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
            decoration: BoxDecoration(
                color: _primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _primary.withValues(alpha: 0.2))),
            child: Text('${_activeOrders.length} active',
                style: const TextStyle(
                    color: _primary,
                    fontSize: 11,
                    fontWeight: FontWeight.w700)),
          ),
      ]),
      const SizedBox(height: 12),
      if (_activeOrders.isEmpty)
        _buildEmptyState()
      else
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _activeOrders.length,
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemBuilder: (context, i) {
            return TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: 1),
              duration: Duration(milliseconds: 300 + i * 70),
              curve: Curves.easeOutCubic,
              builder: (context, v, child) => Opacity(
                  opacity: v,
                  child: Transform.translate(
                      offset: Offset(0, 24 * (1 - v)), child: child)),
              child: _buildOrderCard(_activeOrders[i]),
            );
          },
        ),
    ]);
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 44, horizontal: 24),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border)),
      child: Column(children: [
        Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
                color: _bg, borderRadius: BorderRadius.circular(18)),
            child: const Icon(Icons.inbox_rounded,
                size: 36, color: Color(0xFFCBD5E1))),
        const SizedBox(height: 16),
        const Text('No active deliveries',
            style: TextStyle(
                color: _textPrimary,
                fontSize: 15,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.2)),
        const SizedBox(height: 6),
        const Text('Accept orders from the Orders tab\nto start delivering.',
            textAlign: TextAlign.center,
            style: TextStyle(color: _textSub, fontSize: 13, height: 1.5)),
      ]),
    );
  }

  Widget _buildOrderCard(Order order) {
    final isInTransit = order.status == 'in_transit';
    final statusColor = isInTransit ? _amber : _violet;
    final statusLabel = order.status.replaceAll('_', ' ').toUpperCase();
    final statusBg =
        isInTransit ? const Color(0xFFFFFBEB) : const Color(0xFFF5F3FF);

    return Container(
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 18,
                offset: const Offset(0, 6))
          ]),
      child: Column(children: [
        // Card body
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              // Icon
              Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                      color: _primary.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(13)),
                  child: const Icon(Icons.receipt_long_rounded,
                      color: _primary, size: 17)),
              const SizedBox(width: 12),
              // Order info
              Expanded(
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                    Text('Order #${order.id}',
                        style: const TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 15,
                            color: _textPrimary,
                            letterSpacing: -0.3)),
                    const SizedBox(height: 3),
                    Text(order.buyerName ?? 'Unknown buyer',
                        style: const TextStyle(
                            fontSize: 12,
                            color: _textSub,
                            fontWeight: FontWeight.w500)),
                  ])),
              const SizedBox(width: 8),
              // Status chip
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                decoration: BoxDecoration(
                    color: statusBg,
                    borderRadius: BorderRadius.circular(8),
                    border:
                        Border.all(color: statusColor.withValues(alpha: 0.25))),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                          color: statusColor,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                                color: statusColor.withValues(alpha: 0.4),
                                blurRadius: 4)
                          ])),
                  const SizedBox(width: 5),
                  Text(statusLabel,
                      style: TextStyle(
                          color: statusColor,
                          fontSize: 9,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.3)),
                ]),
              ),
            ]),
            const SizedBox(height: 12),
            // Address
            Container(
              padding: const EdgeInsets.all(11),
              decoration: BoxDecoration(
                  color: _bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _border)),
              child: Row(children: [
                Container(
                    padding: const EdgeInsets.all(5),
                    decoration: BoxDecoration(
                        color: _green.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(7)),
                    child: const Icon(Icons.location_on_rounded,
                        color: _green, size: 13)),
                const SizedBox(width: 9),
                Expanded(
                    child: Text(order.shippingAddress,
                        style: const TextStyle(
                            fontSize: 12,
                            color: _textPrimary,
                            fontWeight: FontWeight.w500,
                            height: 1.35),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis)),
              ]),
            ),
          ]),
        ),

        // Footer
        Container(
          padding: const EdgeInsets.fromLTRB(16, 11, 16, 13),
          decoration: const BoxDecoration(
              color: const Color(0xFFF8F9FC),
              borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(20),
                  bottomRight: Radius.circular(20)),
              border: Border(top: BorderSide(color: _border))),
          child: Row(children: [
            // Amount
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('ORDER TOTAL',
                  style: TextStyle(
                      fontSize: 9,
                      color: _textSub,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.4)),
              const SizedBox(height: 2),
              Text('₱${order.totalAmount.toStringAsFixed(2)}',
                  style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      color: _textPrimary,
                      fontSize: 17,
                      letterSpacing: -0.5)),
            ]),
            const Spacer(),
            // Chat button
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => RiderChatScreen(
                      otherUserId: order.buyerId,
                      otherUserName: order.buyerName ?? 'Customer',
                      otherUserRole: 'buyer',
                      otherUserProfilePicture: null,
                    ),
                  ),
                );
              },
              child: Container(
                height: 40,
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                    gradient: const LinearGradient(
                        colors: [_blue, Color(0xFF1D4ED8)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                          color: _blue.withValues(alpha: 0.25),
                          blurRadius: 8,
                          offset: const Offset(0, 3))
                    ]),
                child: const Row(children: [
                  Icon(Icons.chat_bubble_rounded,
                      size: 14, color: Colors.white),
                  SizedBox(width: 6),
                  Text('Chat',
                      style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: Colors.white)),
                ]),
              ),
            ),
          ]),
        ),
      ]),
    );
  }

  Widget _sectionHeader(String title, IconData icon) {
    return Row(children: [
      Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
            color: _primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8)),
        child: Icon(icon, size: 14, color: _primary),
      ),
      const SizedBox(width: 9),
      Text(title,
          style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w800,
              color: _textPrimary,
              letterSpacing: -0.3)),
    ]);
  }
}

class _StatData {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final Color borderColor;
  const _StatData(this.label, this.value, this.icon, this.color, this.bgColor,
      this.borderColor);
}
