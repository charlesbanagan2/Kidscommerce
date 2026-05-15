import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import '../../widgets/skeleton_loader.dart';
import 'rider_chat_screen.dart';

class RiderChatConversationsScreen extends StatefulWidget {
  const RiderChatConversationsScreen({super.key});

  @override
  State<RiderChatConversationsScreen> createState() =>
      _RiderChatConversationsScreenState();
}

class _RiderChatConversationsScreenState
    extends State<RiderChatConversationsScreen>
    with SingleTickerProviderStateMixin {
  List<dynamic> _conversations = [];
  List<dynamic> _filtered = [];
  bool _isLoading = true;
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 380),
    );
    _fadeAnimation =
        CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _loadConversations();
    _searchController.addListener(() {
      _filterConversations(_searchController.text);
    });
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadConversations() async {
    setState(() => _isLoading = true);
    try {
      final conversations = await ApiService.getChatConversations();
      if (mounted) {
        setState(() {
          _conversations = conversations;
          _filtered = conversations;
          _isLoading = false;
        });
        _fadeController.forward(from: 0);
      }
    } catch (e) {
      debugPrint('Error loading conversations: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _filterConversations(String query) {
    setState(() {
      if (query.isEmpty) {
        _filtered = _conversations;
      } else {
        _filtered = _conversations.where((c) {
          final name = (c['peer_name'] as String? ?? '').toLowerCase();
          final msg = (c['last_message'] as String? ?? '').toLowerCase();
          return name.contains(query.toLowerCase()) ||
              msg.contains(query.toLowerCase());
        }).toList();
      }
    });
  }

  int get _totalUnread => _conversations.fold(
      0, (sum, c) => sum + ((c['unread_count'] as int?) ?? 0));

  Color _roleColor(String role) {
    switch (role.toLowerCase()) {
      case 'seller':
        return _primary;
      case 'rider':
        return const Color(0xFFFF9A3C);
      case 'buyer':
        return _green;
      default:
        return _textSub;
    }
  }

  IconData _roleIcon(String role) {
    switch (role.toLowerCase()) {
      case 'seller':
        return Icons.storefront_rounded;
      case 'rider':
        return Icons.delivery_dining_rounded;
      case 'buyer':
        return Icons.person_rounded;
      default:
        return Icons.person_outline_rounded;
    }
  }

  String _roleLabel(String role) {
    switch (role.toLowerCase()) {
      case 'seller':
        return 'Seller';
      case 'rider':
        return 'Rider';
      case 'buyer':
        return 'Buyer';
      default:
        return role;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: Column(
        children: [
          _buildAppBar(),
          if (_isSearching) _buildSearchBar(),
          Expanded(
            child: _isLoading
                ? _buildSkeletonLoader()
                : _conversations.isEmpty
                    ? _buildEmptyState()
                    : _filtered.isEmpty
                        ? _buildNoResultsState()
                        : RefreshIndicator(
                            color: _primary,
                            strokeWidth: 2.5,
                            onRefresh: _loadConversations,
                            child: FadeTransition(
                              opacity: _fadeAnimation,
                              child: ListView.builder(
                                padding:
                                    const EdgeInsets.fromLTRB(16, 8, 16, 40),
                                itemCount: _filtered.length,
                                itemBuilder: (context, index) =>
                                    _buildConversationTile(
                                        _filtered[index], index),
                              ),
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      color: _surface,
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top,
        bottom: 0,
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 14, 12),
            child: Row(
              children: [
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.chat_bubble_rounded,
                      color: Colors.white, size: 18),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text(
                            'Messages',
                            style: TextStyle(
                              color: Color(0xFF0F172A),
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -0.4,
                            ),
                          ),
                          if (_totalUnread > 0) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 7, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFDC2626),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                '$_totalUnread',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      Text(
                        _totalUnread > 0
                            ? '$_totalUnread unread message${_totalUnread > 1 ? 's' : ''}'
                            : 'All messages read',
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    HapticFeedback.lightImpact();
                    setState(() {
                      _isSearching = !_isSearching;
                      if (!_isSearching) {
                        _searchController.clear();
                        _filtered = _conversations;
                      }
                    });
                  },
                  child: Container(
                    padding: const EdgeInsets.all(9),
                    decoration: BoxDecoration(
                      color:
                          _isSearching ? _primary.withValues(alpha: 0.1) : _bg,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _isSearching
                            ? _primary.withValues(alpha: 0.25)
                            : _border,
                      ),
                    ),
                    child: Icon(
                      _isSearching ? Icons.close_rounded : Icons.search_rounded,
                      size: 18,
                      color: _isSearching ? _primary : const Color(0xFF475569),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: () {
                    HapticFeedback.lightImpact();
                    _loadConversations();
                  },
                  child: Container(
                    padding: const EdgeInsets.all(9),
                    decoration: BoxDecoration(
                      color: _bg,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: _border),
                    ),
                    child: const Icon(Icons.refresh_rounded,
                        size: 18, color: Color(0xFF475569)),
                  ),
                ),
              ],
            ),
          ),
          Container(height: 1, color: _border),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      color: _surface,
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 12),
      child: Container(
        height: 44,
        decoration: BoxDecoration(
          color: _bg,
          borderRadius: BorderRadius.circular(13),
          border: Border.all(color: _border),
        ),
        child: TextField(
          controller: _searchController,
          autofocus: true,
          style: const TextStyle(
              color: Color(0xFF0F172A),
              fontSize: 14,
              fontWeight: FontWeight.w500),
          decoration: InputDecoration(
            hintText: 'Search conversations…',
            hintStyle: const TextStyle(
              color: Color(0xFF94A3B8),
              fontSize: 14,
              fontWeight: FontWeight.w400,
            ),
            prefixIcon: const Icon(Icons.search_rounded,
                color: Color(0xFF94A3B8), size: 19),
            suffixIcon: _searchController.text.isNotEmpty
                ? GestureDetector(
                    onTap: () {
                      _searchController.clear();
                      HapticFeedback.lightImpact();
                    },
                    child: const Icon(Icons.cancel_rounded,
                        color: Color(0xFFCBD5E1), size: 18),
                  )
                : null,
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(vertical: 12),
          ),
        ),
      ),
    );
  }

  Widget _buildConversationTile(dynamic conversation, int index) {
    final peerId = conversation['peer_id'] as int;
    final peerName = conversation['peer_name'] as String? ?? 'Unknown';
    final peerRole = conversation['peer_role'] as String? ?? '';
    final peerProfilePic = conversation['peer_profile_picture'] as String?;
    final lastMessage = conversation['last_message'] as String? ?? '';
    final unreadCount = conversation['unread_count'] as int? ?? 0;
    final timestamp = conversation['last_message_time'] as String?;
    final isUnread = unreadCount > 0;
    final roleColor = _roleColor(peerRole);

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Duration(milliseconds: 280 + (index % 8) * 50),
      curve: Curves.easeOutCubic,
      builder: (context, v, child) => Opacity(
        opacity: v,
        child:
            Transform.translate(offset: Offset(0, 16 * (1 - v)), child: child),
      ),
      child: GestureDetector(
        onTap: () {
          HapticFeedback.lightImpact();
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => RiderChatScreen(
                otherUserId: peerId,
                otherUserName: peerName,
                otherUserRole: peerRole,
                otherUserProfilePicture: peerProfilePic,
              ),
            ),
          ).then((_) => _loadConversations());
        },
        child: Container(
          margin: const EdgeInsets.only(bottom: 10),
          decoration: BoxDecoration(
            color: isUnread ? const Color(0xFFFFFBF5) : _surface,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isUnread ? _primary.withValues(alpha: 0.22) : _border,
              width: isUnread ? 1.5 : 1,
            ),
            boxShadow: [
              BoxShadow(
                color: isUnread
                    ? _primary.withValues(alpha: 0.06)
                    : Colors.black.withValues(alpha: 0.03),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            children: [
              if (isUnread)
                Container(
                  height: 3,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [_primary, _primary.withValues(alpha: 0.3)],
                    ),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(20),
                      topRight: Radius.circular(20),
                    ),
                  ),
                ),
              Padding(
                padding: EdgeInsets.fromLTRB(14, isUnread ? 12 : 14, 14, 14),
                child: Row(
                  children: [
                    // Avatar
                    Stack(
                      children: [
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: isUnread
                                  ? _primary.withValues(alpha: 0.3)
                                  : _border,
                              width: 2,
                            ),
                          ),
                          child: ClipOval(
                            child: peerProfilePic != null &&
                                    peerProfilePic.isNotEmpty
                                ? Image.network(
                                    UrlConfig.toAbsoluteImageUrl(peerProfilePic),
                                    fit: BoxFit.cover,
                                    errorBuilder: (_, __, ___) =>
                                        _buildAvatarFallback(
                                            peerName, roleColor),
                                  )
                                : _buildAvatarFallback(peerName, roleColor),
                          ),
                        ),
                        Positioned(
                          bottom: 1,
                          right: 1,
                          child: Container(
                            width: 13,
                            height: 13,
                            decoration: BoxDecoration(
                              color: _green,
                              shape: BoxShape.circle,
                              border: Border.all(color: _surface, width: 2),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 13),
                    // Content
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  peerName,
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: isUnread
                                        ? FontWeight.w800
                                        : FontWeight.w600,
                                    color: _textPrimary,
                                    letterSpacing: -0.2,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              if (timestamp != null) ...[
                                const SizedBox(width: 8),
                                Row(children: [
                                  Icon(Icons.access_time_rounded,
                                      size: 10,
                                      color: isUnread ? _primary : _textSub),
                                  const SizedBox(width: 3),
                                  Text(
                                    _formatTime(timestamp),
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: isUnread ? _primary : _textSub,
                                      fontWeight: isUnread
                                          ? FontWeight.w700
                                          : FontWeight.w400,
                                    ),
                                  ),
                                ]),
                              ],
                            ],
                          ),
                          const SizedBox(height: 5),
                          Row(
                            children: [
                              if (peerRole.isNotEmpty) ...[
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 7, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: roleColor.withValues(alpha: 0.1),
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                        color:
                                            roleColor.withValues(alpha: 0.2)),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(_roleIcon(peerRole),
                                          size: 9, color: roleColor),
                                      const SizedBox(width: 3),
                                      Text(
                                        _roleLabel(peerRole),
                                        style: TextStyle(
                                          fontSize: 9,
                                          color: roleColor,
                                          fontWeight: FontWeight.w700,
                                          letterSpacing: 0.3,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 7),
                              ],
                              Expanded(
                                child: Text(
                                  lastMessage,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isUnread ? _textPrimary : _textSub,
                                    fontWeight: isUnread
                                        ? FontWeight.w600
                                        : FontWeight.w400,
                                    height: 1.3,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    // Badge or chevron
                    if (isUnread)
                      Container(
                        constraints: const BoxConstraints(minWidth: 24),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 7, vertical: 4),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: _primary.withValues(alpha: 0.38),
                              blurRadius: 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Text(
                          unreadCount > 99 ? '99+' : '$unreadCount',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      )
                    else
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: _bg,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: _border),
                        ),
                        child: const Icon(Icons.chevron_right_rounded,
                            size: 16, color: Color(0xFF94A3B8)),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatarFallback(String name, Color color) {
    return Container(
      color: color.withValues(alpha: 0.12),
      child: Center(
        child: Text(
          name.isNotEmpty ? name[0].toUpperCase() : '?',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: color,
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
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
                    color: _primary.withValues(alpha: 0.07),
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
                  child: const Icon(Icons.chat_bubble_outline_rounded,
                      size: 40, color: Color(0xFFCBD5E1)),
                ),
              ],
            ),
            const SizedBox(height: 28),
            const Text(
              'No conversations yet',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Start chatting with a seller,\nrider, or buyer!',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Color(0xFF64748B),
                fontSize: 13,
                height: 1.65,
              ),
            ),
            const SizedBox(height: 28),
            GestureDetector(
              onTap: () {
                HapticFeedback.lightImpact();
                _loadConversations();
              },
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 13),
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
                    Icon(Icons.refresh_rounded, color: Colors.white, size: 16),
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
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoResultsState() {
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
                  width: 110,
                  height: 110,
                  decoration: BoxDecoration(
                    color: _textSub.withValues(alpha: 0.04),
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
                        color: Colors.black.withValues(alpha: 0.04),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.search_off_rounded,
                      size: 38, color: Color(0xFFCBD5E1)),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'No results found',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
                letterSpacing: -0.3,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Try a different name\nor message.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: _textSub.withValues(alpha: 0.8),
                height: 1.65,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(String timestamp) {
    try {
      final dt = DateTime.parse(timestamp).toLocal();
      final now = DateTime.now();
      final diff = now.difference(dt);
      if (diff.inMinutes < 1) return 'Now';
      if (diff.inHours < 1) return '${diff.inMinutes}m';
      if (diff.inDays < 1) {
        final h = dt.hour > 12
            ? dt.hour - 12
            : dt.hour == 0
                ? 12
                : dt.hour;
        final m = dt.minute.toString().padLeft(2, '0');
        final p = dt.hour >= 12 ? 'PM' : 'AM';
        return '$h:$m $p';
      }
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return '${dt.day}/${dt.month}';
    } catch (_) {
      return '';
    }
  }

  Widget _buildSkeletonLoader() {
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 40),
      itemCount: 8,
      itemBuilder: (context, index) => Container(
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              // Avatar skeleton
              SkeletonLoader(
                width: 52,
                height: 52,
                borderRadius: BorderRadius.circular(26),
              ),
              const SizedBox(width: 13),
              // Content skeleton
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        SkeletonLoader(
                          height: 14,
                          width: 120,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        const Spacer(),
                        SkeletonLoader(
                          height: 11,
                          width: 40,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        SkeletonLoader(
                          height: 12,
                          width: 50,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        const SizedBox(width: 7),
                        Expanded(
                          child: SkeletonLoader(
                            height: 12,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              // Badge skeleton
              SkeletonLoader(
                width: 24,
                height: 24,
                borderRadius: BorderRadius.circular(12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
