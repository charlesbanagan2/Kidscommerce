import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../config/url_config.dart';

/// Chat Service for handling chat API calls and real-time messaging
class ChatService {
  static IO.Socket? _socket;
  static final List<Function(Map<String, dynamic>)> _onNewMessageListeners = [];
  static final List<Function(int)> _onUserTypingListeners = [];
  static final List<Function(int)> _onUserStopTypingListeners = [];
  static final List<Function(Map<String, dynamic>)> _onConversationUpdatedListeners = [];
  static final List<Function(Map<String, dynamic>)> _onUnreadClearedListeners = [];
  static int? _currentUserId;

  /// Initialize Socket.IO connection for real-time chat
  static void initializeSocket(
    String accessToken, {
    int? userId,
    Function(Map<String, dynamic>)? onNewMessage,
    Function(int)? onUserTyping,
    Function(int)? onUserStopTyping,
    Function(Map<String, dynamic>)? onConversationUpdated,
    Function(Map<String, dynamic>)? onUnreadCleared,
  }) {
    if (onNewMessage != null) _onNewMessageListeners.add(onNewMessage);
    if (onUserTyping != null) _onUserTypingListeners.add(onUserTyping);
    if (onUserStopTyping != null)
      _onUserStopTypingListeners.add(onUserStopTyping);
    if (onConversationUpdated != null)
      _onConversationUpdatedListeners.add(onConversationUpdated);
    if (onUnreadCleared != null)
      _onUnreadClearedListeners.add(onUnreadCleared);
    _currentUserId = userId;

    _socket = IO.io(UrlConfig.baseUrl, <String, dynamic>{
      'transports': ['polling'],
      'upgrade': false,
      'autoConnect': true,
      'forceNew': true,
      'extraHeaders': {
        'Authorization': 'Bearer $accessToken',
      }
    });

    _socket?.on('connect', (_) {
      debugPrint('✅ Chat Socket.IO connected');
      if (userId != null) {
        _socket?.emit('join', {'user_id': userId});
      }
      _socket?.emit('join_chat', userId != null ? {'user_id': userId} : null);
    });

    _socket?.on('joined_chat', (data) {
      debugPrint('✅ Joined chat room: $data');
    });

    // Listen for new messages
    _socket?.on('new_message', (data) {
      debugPrint('🔔 New message received: $data');
      try {
        final map = data as Map<String, dynamic>;
        int? peerId;
        if (_currentUserId != null) {
          if (map['sender_id'] == _currentUserId) {
            peerId = map['receiver_id'] as int?;
          } else {
            peerId = map['sender_id'] as int?;
          }
        }
        final enriched = <String, dynamic>{...map};
        if (peerId != null) enriched['peer_id'] = peerId;

        for (final listener in _onNewMessageListeners) {
          try {
            listener(enriched);
          } catch (_) {}
        }
      } catch (e) {
        for (final listener in _onNewMessageListeners) {
          try {
            listener(Map<String, dynamic>.from({'message': data}));
          } catch (_) {}
        }
      }
    });

    // Listen for typing indicators
    _socket?.on('user_typing', (data) {
      debugPrint('⌨️ User typing: $data');
      if (data is Map<String, dynamic> && data['sender_id'] != null) {
        final senderId = data['sender_id'] as int;
        for (final listener in _onUserTypingListeners) {
          try {
            listener(senderId);
          } catch (_) {}
        }
      }
    });

    _socket?.on('user_stop_typing', (data) {
      debugPrint('⌨️ User stopped typing: $data');
      if (data is Map<String, dynamic> && data['sender_id'] != null) {
        final senderId = data['sender_id'] as int;
        for (final listener in _onUserStopTypingListeners) {
          try {
            listener(senderId);
          } catch (_) {}
        }
      }
    });

    // Listen for conversation updates (for list re-sorting)
    _socket?.on('conversation_updated', (data) {
      debugPrint('🔄 Conversation updated: $data');
      try {
        final map = data as Map<String, dynamic>;
        for (final listener in _onConversationUpdatedListeners) {
          try {
            listener(map);
          } catch (_) {}
        }
      } catch (_) {}
    });

    // Listen for unread cleared events
    _socket?.on('unread_cleared', (data) {
      debugPrint('✅ Unread cleared: $data');
      try {
        final map = data as Map<String, dynamic>;
        for (final listener in _onUnreadClearedListeners) {
          try {
            listener(map);
          } catch (_) {}
        }
      } catch (_) {}
    });

    _socket?.on('disconnect', (_) {
      debugPrint('❌ Chat Socket.IO disconnected');
    });

    _socket?.on('error', (error) {
      debugPrint('❌ Chat Socket.IO error: $error');
    });

    _socket?.connect();
  }

  /// Disconnect Socket.IO
  static void disconnectSocket() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
    _onNewMessageListeners.clear();
    _onUserTypingListeners.clear();
    _onUserStopTypingListeners.clear();
    _onConversationUpdatedListeners.clear();
    _onUnreadClearedListeners.clear();
  }

  /// Remove a previously registered new message listener
  static void removeOnNewMessageListener(Function(Map<String, dynamic>) fn) {
    _onNewMessageListeners.remove(fn);
  }

  /// Remove a previously registered typing listener
  static void removeOnUserTypingListener(Function(int) fn) {
    _onUserTypingListeners.remove(fn);
  }

  /// Remove a previously registered stop-typing listener
  static void removeOnUserStopTypingListener(Function(int) fn) {
    _onUserStopTypingListeners.remove(fn);
  }

  /// Remove a previously registered conversation updated listener
  static void removeOnConversationUpdatedListener(Function(Map<String, dynamic>) fn) {
    _onConversationUpdatedListeners.remove(fn);
  }

  /// Remove a previously registered unread cleared listener
  static void removeOnUnreadClearedListener(Function(Map<String, dynamic>) fn) {
    _onUnreadClearedListeners.remove(fn);
  }

  /// Emit typing event
  static void emitTyping(int receiverId) {
    if (_currentUserId == null) return;
    _socket?.emit('typing', {
      'receiver_id': receiverId,
      'sender_id': _currentUserId,
    });
  }

  /// Emit stop typing event
  static void emitStopTyping(int receiverId) {
    if (_currentUserId == null) return;
    _socket?.emit('stop_typing', {
      'receiver_id': receiverId,
      'sender_id': _currentUserId,
    });
  }

  /// Get all conversations
  static Future<Map<String, dynamic>> getConversations(
      String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/conversations'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch conversations: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get messages with a specific user
  static Future<Map<String, dynamic>> getMessages(
      String accessToken, int otherUserId) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/messages/$otherUserId'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch messages: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Send a message
  static Future<Map<String, dynamic>> sendMessage(
    String accessToken,
    int receiverId,
    String message,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/send'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'receiver_id': receiverId,
          'message': message,
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final decoded = json.decode(response.body) as Map<String, dynamic>;

        // Notify local listeners (sender) so conversation list updates immediately.
        try {
          final createdAt =
              decoded['created_at'] ?? DateTime.now().toIso8601String();
          final senderId = decoded['sender_id'] ?? _currentUserId;
          final receiver = decoded['receiver_id'] ?? receiverId;
          final payload = <String, dynamic>{
            'sender_id': senderId,
            'receiver_id': receiver,
            'message': decoded['message'] ?? message,
            'created_at': createdAt,
            // peer_id is the other user in the conversation relative to current user
            'peer_id': (senderId == _currentUserId) ? receiver : senderId,
          };
          for (final listener in _onNewMessageListeners) {
            try {
              listener(payload);
            } catch (_) {}
          }
        } catch (_) {}

        return decoded;
      } else {
        final data = json.decode(response.body);
        return {
          'success': false,
          'error': data['error'] ?? 'Failed to send message',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Mark messages as read
  static Future<Map<String, dynamic>> markMessagesRead(
    String accessToken,
    int otherUserId,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/mark-read/$otherUserId'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to mark messages as read',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get unread message count
  static Future<Map<String, dynamic>> getUnreadCount(String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/unread-count'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch unread count',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Search users to start a conversation
  static Future<Map<String, dynamic>> searchUsers(
    String accessToken, {
    String? query,
    String? role,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (query != null && query.isNotEmpty) {
        queryParams['q'] = query;
      }
      if (role != null && role.isNotEmpty) {
        queryParams['role'] = role;
      }

      final uri = Uri.parse('${UrlConfig.baseUrl}/api/chat/search-users')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to search users',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get chat partner for an order
  static Future<Map<String, dynamic>> getOrderChatPartner(
    String accessToken,
    int orderId,
  ) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/chat/order/$orderId/partner'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'error': 'Failed to get chat partner',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
}
