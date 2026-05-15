import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../config/url_config.dart';

/// Chat Service for handling chat API calls and real-time messaging
class ChatService {
  static IO.Socket? _socket;
  static Function(Map<String, dynamic>)? _onNewMessage;
  static Function(int)? _onUserTyping;
  static Function(int)? _onUserStopTyping;
  static int? _currentUserId;

  /// Initialize Socket.IO connection for real-time chat
  static void initializeSocket(
    String accessToken, {
    int? userId,
    Function(Map<String, dynamic>)? onNewMessage,
    Function(int)? onUserTyping,
    Function(int)? onUserStopTyping,
  }) {
    _onNewMessage = onNewMessage;
    _onUserTyping = onUserTyping;
    _onUserStopTyping = onUserStopTyping;
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
      if (_onNewMessage != null) {
        _onNewMessage!(data as Map<String, dynamic>);
      }
    });

    // Listen for typing indicators
    _socket?.on('user_typing', (data) {
      debugPrint('⌨️ User typing: $data');
      if (_onUserTyping != null && data['sender_id'] != null) {
        _onUserTyping!(data['sender_id'] as int);
      }
    });

    _socket?.on('user_stop_typing', (data) {
      debugPrint('⌨️ User stopped typing: $data');
      if (_onUserStopTyping != null && data['sender_id'] != null) {
        _onUserStopTyping!(data['sender_id'] as int);
      }
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
        return json.decode(response.body);
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
