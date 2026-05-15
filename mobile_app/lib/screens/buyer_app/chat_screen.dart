import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../../providers/auth_provider.dart';
import '../../services/chat_service.dart';
import '../../config/url_config.dart';

class ChatScreen extends StatefulWidget {
  final int otherUserId;
  final String otherUserName;
  final String otherUserRole;
  final String? otherUserProfilePicture;

  const ChatScreen({
    super.key,
    required this.otherUserId,
    required this.otherUserName,
    required this.otherUserRole,
    this.otherUserProfilePicture,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();

  List<dynamic> _messages = [];
  bool _isLoading = true;
  bool _isSending = false;
  String? _error;
  int? _currentUserId;
  Timer? _typingTimer;
  bool _isOtherUserTyping = false;
  bool _hasText = false;

  late AnimationController _typingAnimController;
  late Animation<double> _typingAnim;

  // ── Colors (match ProfileScreen) ────────────────────────────────────────
  static const Color _primary = Color(0xFF1e4db7);
  static const Color _primaryLight = Color(0xFF3B6FE0);
  static const Color _bgColor = Color(0xFFF4F6FC);
  static const Color _bubbleMe = Color(0xFF1e4db7);
  static const Color _bubbleOther = Colors.white;
  static const Color _textDark = Color(0xFF1A1F36);
  static const Color _textSub = Color(0xFF6B7280);
  static const Color _inputBg = Color(0xFFF4F6FC);
  static const Color _onlineDot = Color(0xFF22C55E);

  IconData get _roleIcon {
    switch (widget.otherUserRole.toLowerCase()) {
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

  String get _roleLabel {
    switch (widget.otherUserRole.toLowerCase()) {
      case 'seller':
        return 'Seller';
      case 'rider':
        return 'Delivery Rider';
      case 'buyer':
        return 'Buyer';
      default:
        return widget.otherUserRole;
    }
  }

  @override
  void initState() {
    super.initState();

    _typingAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);

    _typingAnim = CurvedAnimation(
      parent: _typingAnimController,
      curve: Curves.easeInOut,
    );

    _messageController.addListener(() {
      setState(() => _hasText = _messageController.text.trim().isNotEmpty);
    });

    _loadMessages();
    _initializeRealTimeChat();
  }

  void _initializeRealTimeChat() {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final accessToken = authProvider.accessToken;
    _currentUserId = authProvider.user?.id;

    if (accessToken != null) {
      ChatService.initializeSocket(
        accessToken,
        userId: _currentUserId,
        onNewMessage: (messageData) {
          if (messageData['sender_id'] == widget.otherUserId) {
            _loadMessages();
          }
        },
        onUserTyping: (senderId) {
          if (senderId == widget.otherUserId) {
            setState(() => _isOtherUserTyping = true);
          }
        },
        onUserStopTyping: (senderId) {
          if (senderId == widget.otherUserId) {
            setState(() => _isOtherUserTyping = false);
          }
        },
      );
    }
  }

  Future<void> _loadMessages() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final accessToken = authProvider.accessToken;

    if (accessToken == null) {
      setState(() {
        _error = 'Not authenticated';
        _isLoading = false;
      });
      return;
    }

    final result =
        await ChatService.getMessages(accessToken, widget.otherUserId);

    if (mounted) {
      setState(() {
        _isLoading = false;
        if (result['success'] == true) {
          _messages = result['messages'] ?? [];
          _scrollToBottom();
        } else {
          _error = result['error'] ?? 'Failed to load messages';
        }
      });
    }
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty || _isSending) return;

    HapticFeedback.lightImpact();

    setState(() => _isSending = true);

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final accessToken = authProvider.accessToken;

    if (accessToken == null) {
      setState(() => _isSending = false);
      return;
    }

    _messageController.clear();
    ChatService.emitStopTyping(widget.otherUserId);

    final result = await ChatService.sendMessage(
      accessToken,
      widget.otherUserId,
      message,
    );

    if (mounted) {
      setState(() => _isSending = false);

      if (result['success'] == true) {
        _loadMessages();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.white, size: 18),
                const SizedBox(width: 8),
                Text(result['error'] ?? 'Failed to send message'),
              ],
            ),
            backgroundColor: Colors.red.shade600,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        );
      }
    }
  }

  void _onTyping() {
    ChatService.emitTyping(widget.otherUserId);
    _typingTimer?.cancel();
    _typingTimer = Timer(const Duration(seconds: 2), () {
      ChatService.emitStopTyping(widget.otherUserId);
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    _typingTimer?.cancel();
    _typingAnimController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgColor,
      appBar: _buildAppBar(),
      body: Column(
        children: [
          Expanded(child: _buildMessagesList()),
          _buildTypingIndicator(),
          _buildMessageInput(),
        ],
      ),
    );
  }

  // ── AppBar ────────────────────────────────────────────────────────────────
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      elevation: 0,
      backgroundColor: _primary,
      foregroundColor: Colors.white,
      systemOverlayStyle: SystemUiOverlayStyle.light,
      titleSpacing: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
        onPressed: () => Navigator.pop(context),
      ),
      title: Row(
        children: [
          Stack(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.4),
                    width: 2,
                  ),
                ),
                child: ClipOval(
                  child: widget.otherUserProfilePicture != null &&
                          widget.otherUserProfilePicture!.isNotEmpty
                      ? Image.network(
                          UrlConfig.toAbsoluteImageUrl(
                              widget.otherUserProfilePicture!),
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) =>
                              _buildAvatarFallback(radius: 20),
                        )
                      : _buildAvatarFallback(radius: 20),
                ),
              ),
              // Online indicator
              Positioned(
                bottom: 1,
                right: 1,
                child: Container(
                  width: 11,
                  height: 11,
                  decoration: BoxDecoration(
                    color: _onlineDot,
                    shape: BoxShape.circle,
                    border: Border.all(color: _primary, width: 2),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  widget.otherUserName,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Row(
                  children: [
                    Icon(_roleIcon, size: 11, color: Colors.white70),
                    const SizedBox(width: 3),
                    Text(
                      _roleLabel,
                      style: const TextStyle(
                        fontSize: 11,
                        color: Colors.white70,
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
      actions: [
        IconButton(
          icon: const Icon(Icons.call_rounded, size: 22),
          onPressed: () {},
        ),
        IconButton(
          icon: const Icon(Icons.more_vert_rounded, size: 22),
          onPressed: () {},
        ),
      ],
    );
  }

  Widget _buildAvatarFallback({required double radius}) {
    return Container(
      width: radius * 2,
      height: radius * 2,
      color: _primaryLight.withValues(alpha: 0.3),
      child: Center(
        child: Text(
          widget.otherUserName.isNotEmpty
              ? widget.otherUserName[0].toUpperCase()
              : '?',
          style: TextStyle(
            fontSize: radius * 0.85,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  // ── Messages List ─────────────────────────────────────────────────────────
  Widget _buildMessagesList() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(
          color: _primary,
          strokeWidth: 2.5,
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.wifi_off_rounded,
                    size: 36, color: Colors.red),
              ),
              const SizedBox(height: 16),
              const Text(
                'Failed to load messages',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                  color: _textDark,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: _textSub, fontSize: 13),
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _loadMessages,
                icon: const Icon(Icons.refresh_rounded, size: 18),
                label: const Text('Try Again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primary,
                  foregroundColor: Colors.white,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
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

    if (_messages.isEmpty) {
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
                  color: _primary.withValues(alpha: 0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 38,
                  color: _primary,
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'No messages yet',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: _textDark,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Say hi to ${widget.otherUserName}! 👋',
                style: const TextStyle(fontSize: 13, color: _textSub),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    // Group messages by date
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.fromLTRB(12, 16, 12, 8),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        final isMe = message['sender_id'] == _currentUserId;

        // Show date separator
        final showDate = index == 0 ||
            _isDifferentDay(
              _messages[index - 1]['created_at'],
              message['created_at'],
            );

        return Column(
          children: [
            if (showDate) _buildDateSeparator(message['created_at']),
            _buildMessageBubble(message, isMe, index),
          ],
        );
      },
    );
  }

  bool _isDifferentDay(String? a, String? b) {
    if (a == null || b == null) return false;
    try {
      final da = DateTime.parse(a);
      final db = DateTime.parse(b);
      return da.year != db.year || da.month != db.month || da.day != db.day;
    } catch (_) {
      return false;
    }
  }

  Widget _buildDateSeparator(String? isoTime) {
    String label = '';
    if (isoTime != null) {
      try {
        final dt = DateTime.parse(isoTime).toLocal();
        final now = DateTime.now();
        if (dt.year == now.year && dt.month == now.month && dt.day == now.day) {
          label = 'Today';
        } else if (dt.year == now.year &&
            dt.month == now.month &&
            dt.day == now.day - 1) {
          label = 'Yesterday';
        } else {
          label = '${_monthName(dt.month)} ${dt.day}, ${dt.year}';
        }
      } catch (_) {}
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 16),
      child: Row(
        children: [
          Expanded(child: Divider(color: Colors.grey.withValues(alpha: 0.25))),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Text(
                label,
                style: const TextStyle(
                  fontSize: 11,
                  color: _textSub,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          Expanded(child: Divider(color: Colors.grey.withValues(alpha: 0.25))),
        ],
      ),
    );
  }

  String _monthName(int month) {
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'
    ];
    return months[month - 1];
  }

  // ── Message Bubble ────────────────────────────────────────────────────────
  Widget _buildMessageBubble(
      Map<String, dynamic> message, bool isMe, int index) {
    final messageText = message['message'] ?? '';
    final createdAt = message['created_at'];
    final sender = message['sender'];
    final profilePicture = sender?['profile_picture'];

    // Check if next message is from same sender (for avatar spacing)
    final isLastInGroup = index == _messages.length - 1 ||
        _messages[index + 1]['sender_id'] != message['sender_id'];

    return Padding(
      padding: EdgeInsets.only(
        bottom: isLastInGroup ? 8 : 2,
        left: isMe ? 48 : 0,
        right: isMe ? 0 : 48,
      ),
      child: Row(
        mainAxisAlignment:
            isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Other user avatar (only on last in group)
          if (!isMe) ...[
            SizedBox(
              width: 32,
              child: isLastInGroup
                  ? CircleAvatar(
                      radius: 14,
                      backgroundColor: _primary.withValues(alpha: 0.1),
                      backgroundImage:
                          profilePicture != null && profilePicture.isNotEmpty
                              ? NetworkImage(
                                  UrlConfig.toAbsoluteImageUrl(profilePicture))
                              : null,
                      child: profilePicture == null || profilePicture.isEmpty
                          ? Text(
                              widget.otherUserName.isNotEmpty
                                  ? widget.otherUserName[0].toUpperCase()
                                  : '?',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: _primary,
                              ),
                            )
                          : null,
                    )
                  : null,
            ),
            const SizedBox(width: 6),
          ],

          // Bubble
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: isMe ? _bubbleMe : _bubbleOther,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft: Radius.circular(isMe ? 18 : 4),
                      bottomRight: Radius.circular(isMe ? 4 : 18),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isMe
                            ? _primary.withValues(alpha: 0.25)
                            : Colors.black.withValues(alpha: 0.06),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Text(
                    messageText,
                    style: TextStyle(
                      fontSize: 14,
                      color: isMe ? Colors.white : _textDark,
                      height: 1.4,
                    ),
                  ),
                ),
                if (isLastInGroup) ...[
                  const SizedBox(height: 4),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _formatMessageTime(createdAt),
                        style: const TextStyle(
                          fontSize: 10,
                          color: _textSub,
                        ),
                      ),
                      if (isMe) ...[
                        const SizedBox(width: 4),
                        const Icon(
                          Icons.done_all_rounded,
                          size: 14,
                          color: _primary,
                        ),
                      ],
                    ],
                  ),
                ],
              ],
            ),
          ),

          if (isMe) const SizedBox(width: 4),
        ],
      ),
    );
  }

  // ── Typing Indicator ──────────────────────────────────────────────────────
  Widget _buildTypingIndicator() {
    if (!_isOtherUserTyping) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 4),
      child: Row(
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: _primary.withValues(alpha: 0.1),
            backgroundImage: widget.otherUserProfilePicture != null &&
                    widget.otherUserProfilePicture!.isNotEmpty
                ? NetworkImage(UrlConfig.toAbsoluteImageUrl(
                    widget.otherUserProfilePicture!))
                : null,
            child: widget.otherUserProfilePicture == null ||
                    widget.otherUserProfilePicture!.isEmpty
                ? Text(
                    widget.otherUserName.isNotEmpty
                        ? widget.otherUserName[0].toUpperCase()
                        : '?',
                    style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: _primary),
                  )
                : null,
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.06),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return AnimatedBuilder(
                  animation: _typingAnim,
                  builder: (context, _) {
                    final delay = i * 0.15;
                    final animValue =
                        (_typingAnim.value - delay).clamp(0.0, 1.0);
                    return Container(
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      width: 7,
                      height: 7 + (animValue * 4),
                      decoration: BoxDecoration(
                        color:
                            _primary.withValues(alpha: 0.4 + animValue * 0.6),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    );
                  },
                );
              }),
            ),
          ),
        ],
      ),
    );
  }

  // ── Message Input ─────────────────────────────────────────────────────────
  Widget _buildMessageInput() {
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 10,
        bottom: MediaQuery.of(context).padding.bottom + 10,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 12,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Attachment button
          Container(
            width: 40,
            height: 40,
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: _primary.withValues(alpha: 0.08),
              shape: BoxShape.circle,
            ),
            child: IconButton(
              padding: EdgeInsets.zero,
              icon: const Icon(Icons.add_rounded, color: _primary, size: 22),
              onPressed: () {},
            ),
          ),

          // Text field
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: _inputBg,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: _focusNode.hasFocus
                      ? _primary.withValues(alpha: 0.4)
                      : Colors.transparent,
                  width: 1.5,
                ),
              ),
              child: TextField(
                controller: _messageController,
                focusNode: _focusNode,
                onChanged: (_) => _onTyping(),
                decoration: const InputDecoration(
                  hintText: 'Type a message...',
                  hintStyle: TextStyle(
                    color: _textSub,
                    fontSize: 14,
                  ),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                ),
                maxLines: null,
                textCapitalization: TextCapitalization.sentences,
                cursorColor: _primary,
                style: const TextStyle(
                  fontSize: 14,
                  color: _textDark,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),

          const SizedBox(width: 8),

          // Send button
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: _hasText
                  ? const LinearGradient(
                      colors: [_primary, _primaryLight],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    )
                  : null,
              color: _hasText ? null : _inputBg,
              shape: BoxShape.circle,
              boxShadow: _hasText
                  ? [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.4),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ]
                  : [],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(22),
                onTap: _hasText && !_isSending ? _sendMessage : null,
                child: Center(
                  child: _isSending
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : Icon(
                          Icons.send_rounded,
                          color: _hasText ? Colors.white : _textSub,
                          size: 20,
                        ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatMessageTime(String? isoTime) {
    if (isoTime == null) return '';
    try {
      final dt = DateTime.parse(isoTime).toLocal();
      final hour = dt.hour > 12
          ? dt.hour - 12
          : dt.hour == 0
              ? 12
              : dt.hour;
      final min = dt.minute.toString().padLeft(2, '0');
      final period = dt.hour >= 12 ? 'PM' : 'AM';
      return '$hour:$min $period';
    } catch (_) {
      return '';
    }
  }
}
