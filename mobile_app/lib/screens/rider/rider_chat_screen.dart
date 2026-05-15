import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../../providers/auth_provider.dart';
import '../../services/chat_service.dart';
import '../../config/url_config.dart';

class RiderChatScreen extends StatefulWidget {
  final int otherUserId;
  final String otherUserName;
  final String otherUserRole;
  final String? otherUserProfilePicture;

  const RiderChatScreen({
    super.key,
    required this.otherUserId,
    required this.otherUserName,
    required this.otherUserRole,
    this.otherUserProfilePicture,
  });

  @override
  State<RiderChatScreen> createState() => _RiderChatScreenState();
}

class _RiderChatScreenState extends State<RiderChatScreen>
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

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _green = Color(0xFF059669);
  static const Color _bubbleMe = Color(0xFFFA6B02);

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
        return 'Rider';
      case 'buyer':
        return 'Buyer';
      default:
        return widget.otherUserRole;
    }
  }

  Color get _roleColor {
    switch (widget.otherUserRole.toLowerCase()) {
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

  @override
  void initState() {
    super.initState();
    _typingAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
    _typingAnim =
        CurvedAnimation(parent: _typingAnimController, curve: Curves.easeInOut);
    _messageController.addListener(() {
      setState(() => _hasText = _messageController.text.trim().isNotEmpty);
    });
    _focusNode.addListener(() => setState(() {}));
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
          if (messageData['sender_id'] == widget.otherUserId) _loadMessages();
        },
        onUserTyping: (senderId) {
          if (senderId == widget.otherUserId)
            setState(() => _isOtherUserTyping = true);
        },
        onUserStopTyping: (senderId) {
          if (senderId == widget.otherUserId)
            setState(() => _isOtherUserTyping = false);
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
    final result =
        await ChatService.sendMessage(accessToken, widget.otherUserId, message);
    if (mounted) {
      setState(() => _isSending = false);
      if (result['success'] == true) {
        _loadMessages();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Row(children: [
            const Icon(Icons.error_outline, color: Colors.white, size: 18),
            const SizedBox(width: 8),
            Text(result['error'] ?? 'Failed to send message'),
          ]),
          backgroundColor: const Color(0xFFDC2626),
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ));
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
      backgroundColor: _bg,
      body: Column(children: [
        _buildAppBar(),
        Expanded(child: _buildMessagesList()),
        if (_isOtherUserTyping) _buildTypingIndicator(),
        _buildMessageInput(),
      ]),
    );
  }

  Widget _buildAppBar() {
    return Container(
      color: _surface,
      padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top),
      child: Column(children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(6, 8, 10, 10),
          child: Row(children: [
            GestureDetector(
              onTap: () {
                HapticFeedback.lightImpact();
                Navigator.pop(context);
              },
              child: Container(
                margin: const EdgeInsets.only(left: 8),
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: _bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _border),
                ),
                child: const Icon(Icons.arrow_back_ios_new_rounded,
                    size: 16, color: Color(0xFF475569)),
              ),
            ),
            const SizedBox(width: 10),
            Stack(children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: _border, width: 2),
                ),
                child: ClipOval(
                  child: widget.otherUserProfilePicture != null &&
                          widget.otherUserProfilePicture!.isNotEmpty
                      ? Image.network(
                          UrlConfig.toAbsoluteImageUrl(
                              widget.otherUserProfilePicture!),
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _buildAvatarFallback(),
                        )
                      : _buildAvatarFallback(),
                ),
              ),
              Positioned(
                bottom: 1,
                right: 1,
                child: Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: _green,
                    shape: BoxShape.circle,
                    border: Border.all(color: _surface, width: 2),
                  ),
                ),
              ),
            ]),
            const SizedBox(width: 11),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(widget.otherUserName,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                        letterSpacing: -0.3,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 2),
                  Row(children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: _roleColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                            color: _roleColor.withValues(alpha: 0.2)),
                      ),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        Icon(_roleIcon, size: 9, color: _roleColor),
                        const SizedBox(width: 3),
                        Text(_roleLabel,
                            style: TextStyle(
                              fontSize: 9,
                              color: _roleColor,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.3,
                            )),
                      ]),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                          color: _green, shape: BoxShape.circle),
                    ),
                    const SizedBox(width: 4),
                    const Text('Online',
                        style: TextStyle(
                          fontSize: 10,
                          color: _green,
                          fontWeight: FontWeight.w600,
                        )),
                  ]),
                ],
              ),
            ),
            GestureDetector(
              onTap: () {},
              child: Container(
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: _bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _border),
                ),
                child: const Icon(Icons.call_rounded,
                    size: 18, color: Color(0xFF475569)),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: () {},
              child: Container(
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: _bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _border),
                ),
                child: const Icon(Icons.more_vert_rounded,
                    size: 18, color: Color(0xFF475569)),
              ),
            ),
          ]),
        ),
        Container(height: 1, color: _border),
      ]),
    );
  }

  Widget _buildAvatarFallback() {
    return Container(
      color: _roleColor.withValues(alpha: 0.12),
      child: Center(
        child: Text(
          widget.otherUserName.isNotEmpty
              ? widget.otherUserName[0].toUpperCase()
              : '?',
          style: TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w800,
            color: _roleColor,
          ),
        ),
      ),
    );
  }

  Widget _buildMessagesList() {
    if (_isLoading) {
      return const Center(
          child: CircularProgressIndicator(color: _primary, strokeWidth: 3));
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            Stack(alignment: Alignment.center, children: [
              Container(
                  width: 110,
                  height: 110,
                  decoration: BoxDecoration(
                    color: const Color(0xFFDC2626).withValues(alpha: 0.04),
                    shape: BoxShape.circle,
                  )),
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
                    )
                  ],
                ),
                child: const Icon(Icons.wifi_off_rounded,
                    size: 38, color: Color(0xFFCBD5E1)),
              ),
            ]),
            const SizedBox(height: 24),
            const Text('Failed to load messages',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.3)),
            const SizedBox(height: 10),
            Text(_error!,
                textAlign: TextAlign.center,
                style: const TextStyle(
                    color: Color(0xFF64748B), fontSize: 13, height: 1.6)),
            const SizedBox(height: 24),
            GestureDetector(
              onTap: () {
                HapticFeedback.lightImpact();
                _loadMessages();
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
                    )
                  ],
                ),
                child: const Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.refresh_rounded, color: Colors.white, size: 16),
                  SizedBox(width: 8),
                  Text('Try Again',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 13)),
                ]),
              ),
            ),
          ]),
        ),
      );
    }

    if (_messages.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(40),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            Stack(alignment: Alignment.center, children: [
              Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.04),
                    shape: BoxShape.circle,
                  )),
              Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.07),
                    shape: BoxShape.circle,
                  )),
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
                    )
                  ],
                ),
                child: const Icon(Icons.chat_bubble_outline_rounded,
                    size: 40, color: Color(0xFFCBD5E1)),
              ),
            ]),
            const SizedBox(height: 28),
            const Text('No messages yet',
                style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.4)),
            const SizedBox(height: 10),
            Text('Say hi to ${widget.otherUserName}! 👋',
                style: const TextStyle(
                    color: Color(0xFF64748B), fontSize: 13, height: 1.65),
                textAlign: TextAlign.center),
          ]),
        ),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.fromLTRB(14, 16, 14, 8),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        final isMe = message['sender_id'] == _currentUserId;
        final showDate = index == 0 ||
            _isDifferentDay(
                _messages[index - 1]['created_at'], message['created_at']);
        return Column(children: [
          if (showDate) _buildDateSeparator(message['created_at']),
          _buildMessageBubble(message, isMe, index),
        ]);
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
      child: Row(children: [
        Expanded(
            child: Container(
                height: 1,
                decoration: BoxDecoration(
                    gradient: LinearGradient(
                  colors: [_border.withValues(alpha: 0), _border],
                )))),
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 12),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
          decoration: BoxDecoration(
            color: _textSub.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(label,
              style: const TextStyle(
                fontSize: 11,
                color: Color(0xFF64748B),
                fontWeight: FontWeight.w700,
                letterSpacing: 0.2,
              )),
        ),
        Expanded(
            child: Container(
                height: 1,
                decoration: BoxDecoration(
                    gradient: LinearGradient(
                  colors: [_border, _border.withValues(alpha: 0)],
                )))),
      ]),
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

  Widget _buildMessageBubble(
      Map<String, dynamic> message, bool isMe, int index) {
    final messageText = message['message'] ?? '';
    final createdAt = message['created_at'];
    final sender = message['sender'];
    final profilePic = sender?['profile_picture'];
    final isLastInGroup = index == _messages.length - 1 ||
        _messages[index + 1]['sender_id'] != message['sender_id'];

    return Padding(
      padding: EdgeInsets.only(
        bottom: isLastInGroup ? 10 : 3,
        left: isMe ? 52 : 0,
        right: isMe ? 0 : 52,
      ),
      child: Row(
        mainAxisAlignment:
            isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isMe) ...[
            SizedBox(
              width: 30,
              child: isLastInGroup
                  ? Container(
                      width: 30,
                      height: 30,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: _border, width: 1.5),
                      ),
                      child: ClipOval(
                        child: profilePic != null && profilePic.isNotEmpty
                            ? Image.network(
                                UrlConfig.toAbsoluteImageUrl(profilePic),
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) =>
                                    _buildMiniAvatarFallback(),
                              )
                            : _buildMiniAvatarFallback(),
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 7),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: isMe ? _bubbleMe : _surface,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft: Radius.circular(isMe ? 18 : 5),
                      bottomRight: Radius.circular(isMe ? 5 : 18),
                    ),
                    border: isMe ? null : Border.all(color: _border, width: 1),
                    boxShadow: [
                      BoxShadow(
                        color: isMe
                            ? _primary.withValues(alpha: 0.22)
                            : Colors.black.withValues(alpha: 0.04),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      )
                    ],
                  ),
                  child: Text(messageText,
                      style: TextStyle(
                        fontSize: 14,
                        color: isMe ? Colors.white : _textPrimary,
                        height: 1.45,
                        fontWeight: FontWeight.w400,
                      )),
                ),
                if (isLastInGroup) ...[
                  const SizedBox(height: 4),
                  Row(mainAxisSize: MainAxisSize.min, children: [
                    Icon(Icons.access_time_rounded,
                        size: 10, color: _textSub.withValues(alpha: 0.7)),
                    const SizedBox(width: 3),
                    Text(_formatMessageTime(createdAt),
                        style: TextStyle(
                          fontSize: 10,
                          color: _textSub.withValues(alpha: 0.7),
                          fontWeight: FontWeight.w500,
                        )),
                    if (isMe) ...[
                      const SizedBox(width: 4),
                      const Icon(Icons.done_all_rounded,
                          size: 13, color: _primary),
                    ],
                  ]),
                ],
              ],
            ),
          ),
          if (isMe) const SizedBox(width: 2),
        ],
      ),
    );
  }

  Widget _buildMiniAvatarFallback() {
    return Container(
      color: _roleColor.withValues(alpha: 0.12),
      child: Center(
        child: Text(
          widget.otherUserName.isNotEmpty
              ? widget.otherUserName[0].toUpperCase()
              : '?',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            color: _roleColor,
          ),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(left: 14, bottom: 6, right: 60),
      child: Row(children: [
        Container(
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(color: _border, width: 1.5),
          ),
          child: ClipOval(
            child: widget.otherUserProfilePicture != null &&
                    widget.otherUserProfilePicture!.isNotEmpty
                ? Image.network(
                    UrlConfig.toAbsoluteImageUrl(
                        widget.otherUserProfilePicture!),
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _buildMiniAvatarFallback(),
                  )
                : _buildMiniAvatarFallback(),
          ),
        ),
        const SizedBox(width: 7),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
          decoration: BoxDecoration(
            color: _surface,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(18),
              topRight: Radius.circular(18),
              bottomRight: Radius.circular(18),
              bottomLeft: Radius.circular(5),
            ),
            border: Border.all(color: _border),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 8,
                offset: const Offset(0, 3),
              )
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: List.generate(3, (i) {
              return AnimatedBuilder(
                animation: _typingAnim,
                builder: (context, _) {
                  final delay = i * 0.18;
                  final v = (_typingAnim.value - delay).clamp(0.0, 1.0);
                  return Container(
                    margin: const EdgeInsets.symmetric(horizontal: 2.5),
                    width: 7,
                    height: 7 + (v * 4),
                    decoration: BoxDecoration(
                      color: _primary.withValues(alpha: 0.35 + v * 0.65),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  );
                },
              );
            }),
          ),
        ),
      ]),
    );
  }

  Widget _buildMessageInput() {
    final hasFocus = _focusNode.hasFocus;
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 10,
        bottom: MediaQuery.of(context).padding.bottom + 10,
      ),
      decoration: const BoxDecoration(
        color: _surface,
        border: Border(top: BorderSide(color: _border)),
        boxShadow: [
          BoxShadow(
            color: Color.fromRGBO(0, 0, 0, 0.04),
            blurRadius: 12,
            offset: Offset(0, -3),
          )
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          GestureDetector(
            onTap: () {},
            child: Container(
              width: 42,
              height: 42,
              margin: const EdgeInsets.only(right: 8, bottom: 1),
              decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(13),
                border: Border.all(color: _border),
              ),
              child: const Icon(Icons.add_rounded,
                  color: Color(0xFF475569), size: 20),
            ),
          ),
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: hasFocus ? _primary.withValues(alpha: 0.4) : _border,
                  width: hasFocus ? 1.5 : 1,
                ),
              ),
              child: TextField(
                controller: _messageController,
                focusNode: _focusNode,
                onChanged: (_) => _onTyping(),
                decoration: const InputDecoration(
                  hintText: 'Type a message…',
                  hintStyle: TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                  ),
                  border: InputBorder.none,
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                ),
                maxLines: null,
                textCapitalization: TextCapitalization.sentences,
                style: const TextStyle(
                  fontSize: 14,
                  color: Color(0xFF0F172A),
                  fontWeight: FontWeight.w400,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOutCubic,
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: _hasText
                  ? const LinearGradient(
                      colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    )
                  : null,
              color: _hasText ? null : _bg,
              borderRadius: BorderRadius.circular(13),
              border: _hasText ? null : Border.all(color: _border),
              boxShadow: _hasText
                  ? [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.38),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      )
                    ]
                  : [],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(13),
                onTap: _hasText && !_isSending ? _sendMessage : null,
                child: Center(
                  child: _isSending
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2.5))
                      : Icon(Icons.send_rounded,
                          color:
                              _hasText ? Colors.white : const Color(0xFF94A3B8),
                          size: 18),
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
      final h = dt.hour > 12
          ? dt.hour - 12
          : dt.hour == 0
              ? 12
              : dt.hour;
      final m = dt.minute.toString().padLeft(2, '0');
      final p = dt.hour >= 12 ? 'PM' : 'AM';
      return '$h:$m $p';
    } catch (_) {
      return '';
    }
  }
}
