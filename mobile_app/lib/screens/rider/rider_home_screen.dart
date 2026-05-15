// rider_home_screen.dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'rider_available_orders_screen.dart';
import 'rider_dashboard_screen.dart';
import 'rider_active_delivery_screen.dart';
import 'rider_profile_screen.dart';
import 'rider_chat_conversations_screen.dart';
import '../../services/api_service.dart';

class RiderHomeScreen extends StatefulWidget {
  const RiderHomeScreen({super.key});

  @override
  State<RiderHomeScreen> createState() => _RiderHomeScreenState();
}

class _RiderHomeScreenState extends State<RiderHomeScreen> {
  int _currentIndex = 0;
  int _unreadMessages = 0;
  Timer? _refreshTimer;

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _textSub = Color(0xFF94A3B8);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);

  final List<Widget> _screens = const [
    RiderDashboardScreen(),
    RiderActiveDeliveryScreen(),
    RiderAvailableOrdersScreen(),
    RiderChatConversationsScreen(),
    RiderProfileScreen(),
  ];

  final List<_NavItem> _items = const [
    _NavItem(Icons.dashboard_outlined, Icons.dashboard_rounded, 'Dashboard'),
    _NavItem(Icons.navigation_outlined, Icons.navigation_rounded, 'Delivery'),
    _NavItem(Icons.inventory_2_outlined, Icons.inventory_2_rounded, 'Orders'),
    _NavItem(Icons.chat_bubble_outline, Icons.chat_bubble, 'Messages'),
    _NavItem(Icons.person_outline_rounded, Icons.person_rounded, 'Profile'),
  ];

  @override
  void initState() {
    super.initState();
    _fetchUnreadCounts();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      _fetchUnreadCounts();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchUnreadCounts() async {
    try {
      final msgCount = await ApiService.getUnreadMessagesCount();
      if (mounted) {
        setState(() {
          _unreadMessages = msgCount;
        });
      }
    } catch (e) {
      debugPrint('⚠️ Error fetching unread counts: $e');
    }
  }

  void _onTap(int i) {
    if (i == _currentIndex) return;
    HapticFeedback.selectionClick();
    setState(() => _currentIndex = i);
    if (i == 3) _fetchUnreadCounts(); // Messages tab
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: _surface,
          border: const Border(top: BorderSide(color: _border)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              children: List.generate(_items.length, (i) {
                final item = _items[i];
                final selected = i == _currentIndex;
                final isDelivery = i == 1; // highlight the active delivery tab

                return Expanded(
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => _onTap(i),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 220),
                      curve: Curves.easeOutCubic,
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      decoration: BoxDecoration(
                        color: selected
                            ? (isDelivery ? _green : _primary)
                                .withValues(alpha: 0.1)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        Stack(
                          clipBehavior: Clip.none,
                          children: [
                            AnimatedSwitcher(
                              duration: const Duration(milliseconds: 200),
                              child: Icon(
                                selected ? item.activeIcon : item.icon,
                                key: ValueKey(selected),
                                size: 22,
                                color: selected
                                    ? (isDelivery ? _green : _primary)
                                    : _textSub,
                              ),
                            ),
                            // Pulse dot for delivery tab
                            if (isDelivery && !selected)
                              Positioned(
                                top: -2,
                                right: -2,
                                child: _PulseDot(),
                              ),
                            // Unread badge for messages tab
                            if (i == 3 && _unreadMessages > 0)
                              Positioned(
                                top: -2,
                                right: -2,
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
                        const SizedBox(height: 4),
                        AnimatedDefaultTextStyle(
                          duration: const Duration(milliseconds: 200),
                          style: TextStyle(
                            fontSize: 10.5,
                            fontWeight:
                                selected ? FontWeight.w800 : FontWeight.w500,
                            color: selected
                                ? (isDelivery ? _green : _primary)
                                : _textSub,
                          ),
                          child: Text(item.label),
                        ),
                        const SizedBox(height: 2),
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 220),
                          width: selected ? 18 : 0,
                          height: 3,
                          decoration: BoxDecoration(
                            color: isDelivery ? _green : _primary,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      ]),
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
  }
}

// Small animated pulse dot on the Delivery nav item
class _PulseDot extends StatefulWidget {
  @override
  State<_PulseDot> createState() => _PulseDotState();
}

class _PulseDotState extends State<_PulseDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 900))
      ..repeat(reverse: true);
    _anim = Tween<double>(begin: 0.5, end: 1.0)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => Opacity(
        opacity: _anim.value,
        child: Container(
          width: 7,
          height: 7,
          decoration: const BoxDecoration(
              color: Color(0xFF059669), shape: BoxShape.circle),
        ),
      ),
    );
  }
}

class _NavItem {
  final IconData icon;
  final IconData activeIcon;
  final String label;
  const _NavItem(this.icon, this.activeIcon, this.label);
}
