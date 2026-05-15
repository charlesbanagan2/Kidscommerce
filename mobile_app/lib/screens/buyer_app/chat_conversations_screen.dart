import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import '../../widgets/skeleton_loader.dart';
import 'chat_screen.dart';

class ChatConversationsScreen extends StatefulWidget {
  const ChatConversationsScreen({super.key});

  @override
  State<ChatConversationsScreen> createState() =>
      _ChatConversationsScreenState();
}

class _ChatConversationsScreenState extends State<ChatConversationsScreen>
    with SingleTickerProviderStateMixin {
  List<dynamic> _conversations = [];
  List<dynamic> _filtered = [];
  bool _isLoading = true;
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  // ── Colors (match ProfileScreen) ─────────────────────────────────────────────
  static const Color _primaryDark = Color(0xFF1a2f6b);
  static const Color _primary = Color(0xFF1e4db7);
  static const Color _primaryLight = Color(0xFF3B6FE0);
  static const Color _bgColor = Color(0xFFF4F6FC);
  static const Color _textDark = Color(0xFF1A1F36);
  static const Color _onlineDot = Color(0xFF22C55E);
  static const Color _textSub = Color(0xFF6B7280);

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
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

  // ── Role helpers ──────────────────────────────────────────────────────────
  Color _roleColor(String role) {
    switch (role.toLowerCase()) {
      case 'seller':
        return _primary;
      case 'rider':
        return const Color(0xFF3B82F6);
      case 'buyer':
        return const Color(0xFF10B981);
      default:
        return const Color(0xFF6B7280);
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
        return 'Delivery Rider';
      case 'buyer':
        return 'Buyer';
      default:
        return role;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgColor,
      body: Column(
        children: [
          _buildHeader(),
          if (_isSearching) _buildSearchBar(),
          Expanded(
            child: _isLoading
                ? const ListSkeletonLoader(
                    itemSkeleton: ChatConversationSkeleton(),
                    itemCount: 8,
                    padding: EdgeInsets.fromLTRB(16, 8, 16, 32),
                  )
                : _conversations.isEmpty
                    ? _buildEmptyState()
                    : _filtered.isEmpty
                        ? _buildNoResultsState()
                        : RefreshIndicator(
                            color: _primary,
                            onRefresh: _loadConversations,
                            child: FadeTransition(
                              opacity: _fadeAnimation,
                              child: ListView.builder(
                                padding:
                                    const EdgeInsets.fromLTRB(16, 8, 16, 32),
                                itemCount: _filtered.length,
                                itemBuilder: (context, index) {
                                  return _buildConversationTile(
                                      _filtered[index], index);
                                },
                              ),
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [_primaryDark, _primaryLight],
        ),
      ),
      padding: EdgeInsets.fromLTRB(
        16,
        MediaQuery.of(context).padding.top + 12,
        16,
        14,
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Decorative icon
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.chat_bubble_rounded,
                  color: Colors.white,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Messages',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.5,
                      ),
                    ),
                    Text(
                      _totalUnread > 0
                          ? '$_totalUnread unread message${_totalUnread > 1 ? 's' : ''}'
                          : 'All messages read',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.75),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              // Search toggle
              _buildHeaderAction(
                icon: _isSearching ? Icons.close_rounded : Icons.search_rounded,
                onTap: () {
                  setState(() {
                    _isSearching = !_isSearching;
                    if (!_isSearching) {
                      _searchController.clear();
                      _filtered = _conversations;
                    }
                  });
                },
              ),
              const SizedBox(width: 8),
              // Refresh
              _buildHeaderAction(
                icon: Icons.refresh_rounded,
                onTap: _loadConversations,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderAction({
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: Colors.white, size: 20),
      ),
    );
  }

  // ── Search Bar ────────────────────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Container(
      color: _primary,
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Container(
        height: 42,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(21),
        ),
        child: TextField(
          controller: _searchController,
          autofocus: true,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            hintText: 'Search conversations...',
            hintStyle: TextStyle(
              color: Colors.white.withValues(alpha: 0.65),
              fontSize: 14,
            ),
            prefixIcon: Icon(
              Icons.search_rounded,
              color: Colors.white.withValues(alpha: 0.8),
              size: 20,
            ),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(vertical: 11),
          ),
        ),
      ),
    );
  }

  // ── Conversation Tile ─────────────────────────────────────────────────────
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

    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ChatScreen(
              otherUserId: peerId,
              otherUserName: peerName,
              otherUserRole: peerRole,
              otherUserProfilePicture: peerProfilePic,
            ),
          ),
        ).then((_) => _loadConversations());
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(
          color: isUnread ? Colors.white : Colors.white.withValues(alpha: 0.85),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color:
                isUnread ? _primary.withValues(alpha: 0.2) : Colors.transparent,
            width: 1.2,
          ),
          boxShadow: [
            BoxShadow(
              color: isUnread
                  ? _primary.withValues(alpha: 0.08)
                  : Colors.black.withValues(alpha: 0.04),
              blurRadius: isUnread ? 12 : 8,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              // ── Avatar ──────────────────────────────────────────────────
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
                            : Colors.grey.withValues(alpha: 0.15),
                        width: 2,
                      ),
                    ),
                    child: peerProfilePic != null && peerProfilePic.isNotEmpty
                        ? ClipOval(
                            child: Image.network(
                              UrlConfig.toAbsoluteImageUrl(peerProfilePic),
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) =>
                                  _buildAvatarFallback(peerName, roleColor),
                            ),
                          )
                        : ClipOval(
                            child: _buildAvatarFallback(peerName, roleColor),
                          ),
                  ),
                  // Online indicator
                  Positioned(
                    bottom: 1,
                    right: 1,
                    child: Container(
                      width: 13,
                      height: 13,
                      decoration: BoxDecoration(
                        color: _onlineDot,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(width: 12),

              // ── Content ──────────────────────────────────────────────────
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name + time
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            peerName,
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight:
                                  isUnread ? FontWeight.w800 : FontWeight.w600,
                              color: _textDark,
                              letterSpacing: -0.2,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (timestamp != null) ...[
                          const SizedBox(width: 8),
                          Text(
                            _formatTime(timestamp),
                            style: TextStyle(
                              fontSize: 11,
                              color: isUnread ? _primary : _textSub,
                              fontWeight:
                                  isUnread ? FontWeight.w700 : FontWeight.w400,
                            ),
                          ),
                        ],
                      ],
                    ),

                    const SizedBox(height: 4),

                    // Role chip + last message
                    Row(
                      children: [
                        if (peerRole.isNotEmpty) ...[
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: roleColor.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  _roleIcon(peerRole),
                                  size: 9,
                                  color: roleColor,
                                ),
                                const SizedBox(width: 3),
                                Text(
                                  _roleLabel(peerRole),
                                  style: TextStyle(
                                    fontSize: 9,
                                    color: roleColor,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.2,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 6),
                        ],
                        Expanded(
                          child: Text(
                            lastMessage,
                            style: TextStyle(
                              fontSize: 13,
                              color: isUnread ? _textDark : _textSub,
                              fontWeight:
                                  isUnread ? FontWeight.w600 : FontWeight.w400,
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

              const SizedBox(width: 8),

              // ── Unread badge ─────────────────────────────────────────────
              if (isUnread)
                Container(
                  constraints: const BoxConstraints(minWidth: 22),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [_primary, _primaryLight],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.4),
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
                const Icon(
                  Icons.chevron_right_rounded,
                  color: _textSub,
                  size: 20,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatarFallback(String name, Color color) {
    return Container(
      color: color.withValues(alpha: 0.15),
      child: Center(
        child: Text(
          name.isNotEmpty ? name[0].toUpperCase() : '?',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ),
    );
  }

  // ── Empty State ───────────────────────────────────────────────────────────
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: _primary.withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.chat_bubble_outline_rounded,
                size: 42,
                color: _primary,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'No conversations yet',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: _textDark,
                letterSpacing: -0.3,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Start chatting with a seller,\nrider, or buyer!',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: _textSub,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 28),
            ElevatedButton.icon(
              onPressed: _loadConversations,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: const Text('Refresh'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _primary,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 28, vertical: 13),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
                elevation: 0,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── No Search Results ─────────────────────────────────────────────────────
  Widget _buildNoResultsState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: _textSub.withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.search_off_rounded,
                size: 38,
                color: _textSub,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'No results found',
              style: TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w700,
                color: _textDark,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Try searching a different name\nor message.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: _textSub.withValues(alpha: 0.8),
                height: 1.5,
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
}
