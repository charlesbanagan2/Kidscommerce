import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import '../../models/order.dart';
import 'rider_edit_profile_screen.dart';

class RiderProfileScreen extends StatefulWidget {
  const RiderProfileScreen({super.key});

  @override
  State<RiderProfileScreen> createState() => _RiderProfileScreenState();
}

class _RiderProfileScreenState extends State<RiderProfileScreen> {
  List<Order> _orders = [];
  bool _loadingOrders = true;

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);
  static const Color _violet = Color(0xFF7C3AED);
  static const Color _blue = Color(0xFF2563EB);
  static const Color _red = Color(0xFFDC2626);

  @override
  void initState() {
    super.initState();
    _loadProfile();
    _loadOrders();
  }

  Future<void> _loadProfile() async {
    // Refresh user profile from backend to get latest profile image
    final authProvider = context.read<AuthProvider>();
    await authProvider.refreshUser();
  }

  Future<void> _loadOrders() async {
    try {
      final data = await ApiService.getRiderOrders();
      if (mounted) {
        setState(() {
          _orders = data.map((j) => Order.fromJson(j)).toList();
          _loadingOrders = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loadingOrders = false);
    }
  }

  int get _totalOrders => _orders.length;
  int get _activeOrders => _orders
      .where((o) => o.status == 'in_transit' || o.status == 'to_ship')
      .length;
  int get _deliveredOrders =>
      _orders.where((o) => o.status == 'delivered').length;

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;

    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            _buildSliverAppBar(context),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  _buildProfileCard(user, context),
                  const SizedBox(height: 20),
                  _buildStatsRow(),
                  const SizedBox(height: 20),
                  _buildSection('Account', [
                    _buildMenuItem(
                        icon: Icons.person_rounded,
                        title: 'Personal Information',
                        onTap: () async {
                          final updated = await Navigator.push<bool>(
                              context,
                              MaterialPageRoute(
                                  builder: (_) =>
                                      const RiderEditProfileScreen()));
                          if (updated == true && mounted) {
                            await Provider.of<AuthProvider>(context,
                                    listen: false)
                                .refreshUser();
                            setState(() {});
                          }
                        }),
                    _buildMenuItem(
                        icon: Icons.local_shipping_rounded,
                        title: 'Delivery History',
                        onTap: () {}),
                    _buildMenuItem(
                        icon: Icons.account_balance_wallet_rounded,
                        title: 'Earnings & Payouts',
                        onTap: () {}),
                  ]),
                  const SizedBox(height: 20),
                  _buildSection('Settings', [
                    _buildMenuItem(
                        icon: Icons.notifications_rounded,
                        title: 'Notifications',
                        onTap: () {}),
                    _buildMenuItem(
                        icon: Icons.help_rounded,
                        title: 'Help & Support',
                        onTap: () {}),
                    _buildMenuItem(
                        icon: Icons.info_rounded, title: 'About', onTap: () {}),
                  ]),
                  const SizedBox(height: 20),
                  _buildLogoutButton(authProvider, context),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliverAppBar(BuildContext context) {
    return SliverAppBar(
      floating: true,
      snap: true,
      backgroundColor: _surface,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      shadowColor: Colors.black.withValues(alpha: 0.08),
      surfaceTintColor: Colors.transparent,
      toolbarHeight: 64,
      title: Row(children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                  color: _primary.withValues(alpha: 0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 3))
            ],
          ),
          child:
              const Icon(Icons.person_rounded, color: Colors.white, size: 19),
        ),
        const SizedBox(width: 12),
        const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('My Profile',
              style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4)),
          Text('Manage your account',
              style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.w500)),
        ]),
      ]),
    );
  }

  Widget _buildProfileCard(dynamic user, BuildContext context) {
    final profileImage = user?.profileImage;
    final initial = user?.fullName?.isNotEmpty == true
        ? user!.fullName!.substring(0, 1).toUpperCase()
        : 'R';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 20,
                offset: const Offset(0, 8))
          ]),
      child: Row(children: [
        Container(
          width: 66,
          height: 66,
          decoration: BoxDecoration(
              gradient: profileImage == null || profileImage.isEmpty
                  ? const LinearGradient(
                      colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight)
                  : null,
              borderRadius: BorderRadius.circular(20)),
          child: profileImage != null && profileImage.isNotEmpty
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Image.network(
                    UrlConfig.toAbsoluteImageUrl(profileImage),
                    width: 66,
                    height: 66,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Center(
                      child: Text(initial,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.w800)),
                    ),
                  ),
                )
              : Center(
                  child: Text(initial,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.w800))),
        ),
        const SizedBox(width: 16),
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(user?.fullName ?? 'Rider',
              style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: _textPrimary,
                  letterSpacing: -0.3)),
          const SizedBox(height: 3),
          Text(user?.email ?? '',
              style: const TextStyle(
                  fontSize: 12, color: _textSub, fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
                color: _green.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _green.withValues(alpha: 0.2))),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Container(
                  width: 6,
                  height: 6,
                  decoration: const BoxDecoration(
                      color: _green, shape: BoxShape.circle)),
              const SizedBox(width: 6),
              const Text('Active Rider',
                  style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _green)),
            ]),
          ),
        ])),
        GestureDetector(
          onTap: () async {
            final updated = await Navigator.push<bool>(
                context,
                MaterialPageRoute(
                    builder: (_) => const RiderEditProfileScreen()));
            if (updated == true && mounted) {
              await Provider.of<AuthProvider>(context, listen: false)
                  .refreshUser();
              setState(() {});
            }
          },
          child: Container(
            padding: const EdgeInsets.all(9),
            decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _border)),
            child: const Icon(Icons.edit_rounded, size: 17, color: _textSub),
          ),
        ),
      ]),
    );
  }

  // ── Delivery Stats Row ──────────────────────
  Widget _buildStatsRow() {
    if (_loadingOrders) {
      return Container(
        height: 90,
        decoration: BoxDecoration(
            color: _surface,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: _border)),
        child: const Center(
            child:
                CircularProgressIndicator(color: _primary, strokeWidth: 2.5)),
      );
    }

    final stats = [
      _StatsItem('Total', _totalOrders.toString(), Icons.receipt_long_rounded,
          _blue, const Color(0xFFEFF6FF), const Color(0xFFDBEAFE)),
      _StatsItem(
          'Active',
          _activeOrders.toString(),
          Icons.local_shipping_rounded,
          _violet,
          const Color(0xFFF5F3FF),
          const Color(0xFFEDE9FE)),
      _StatsItem(
          'Delivered',
          _deliveredOrders.toString(),
          Icons.check_circle_rounded,
          _green,
          const Color(0xFFECFDF5),
          const Color(0xFFD1FAE5)),
    ];

    return Row(
      children: stats.map((s) {
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: s == stats.last ? 0 : 10),
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
            decoration: BoxDecoration(
                color: _surface,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: s.borderColor, width: 1.5),
                boxShadow: [
                  BoxShadow(
                      color: s.color.withValues(alpha: 0.07),
                      blurRadius: 14,
                      offset: const Offset(0, 5))
                ]),
            child: Column(children: [
              Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                      color: s.bgColor,
                      borderRadius: BorderRadius.circular(11)),
                  child: Icon(s.icon, color: s.color, size: 17)),
              const SizedBox(height: 8),
              Text(s.value,
                  style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: _textPrimary,
                      letterSpacing: -0.5)),
              const SizedBox(height: 2),
              Text(s.label,
                  style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: s.color.withValues(alpha: 0.8),
                      letterSpacing: 0.3)),
            ]),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 12),
        child: Text(title,
            style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: _textSub,
                letterSpacing: 0.3)),
      ),
      Container(
          decoration: BoxDecoration(
              color: _surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _border)),
          child: Column(children: children)),
    ]);
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(children: [
          Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                  color: _bg, borderRadius: BorderRadius.circular(10)),
              child: Icon(icon, size: 18, color: _primary)),
          const SizedBox(width: 12),
          Expanded(
              child: Text(title,
                  style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: _textPrimary))),
          const Icon(Icons.chevron_right_rounded, size: 20, color: _textSub),
        ]),
      ),
    );
  }

  Future<void> _showLogoutDialog(
      BuildContext context, AuthProvider authProvider) async {
    return showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        contentPadding: const EdgeInsets.all(24),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _red.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.logout_rounded, color: _red, size: 32),
            ),
            const SizedBox(height: 16),
            const Text('Sign Out?',
                style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: _textPrimary)),
            const SizedBox(height: 8),
            const Text('Are you sure you want to sign out?',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: _textSub)),
            const SizedBox(height: 20),
            Row(children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(ctx),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    side: const BorderSide(color: _border),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Cancel',
                      style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: _textPrimary)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () async {
                    Navigator.pop(ctx);
                    await authProvider.logout();
                    if (context.mounted) {
                      Navigator.pushNamedAndRemoveUntil(
                          context, '/home', (r) => false);
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    backgroundColor: _red,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Sign Out',
                      style:
                          TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                ),
              ),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildLogoutButton(AuthProvider authProvider, BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton.icon(
        onPressed: () => _showLogoutDialog(context, authProvider),
        icon: const Icon(Icons.logout_rounded, size: 18),
        label: const Text('Log Out',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
        style: ElevatedButton.styleFrom(
            backgroundColor: _red,
            foregroundColor: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16))),
      ),
    );
  }
}

class _StatsItem {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final Color borderColor;
  const _StatsItem(this.label, this.value, this.icon, this.color, this.bgColor,
      this.borderColor);
}
