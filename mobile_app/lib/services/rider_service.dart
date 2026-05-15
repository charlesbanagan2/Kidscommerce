import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../config/url_config.dart';

/// Rider Service for handling rider-specific API calls and real-time updates
class RiderService {
  static IO.Socket? _socket;
  static Function(Map<String, dynamic>)? _onNewOrderAvailable;
  static Function(int)? _onOrderTaken;

  /// Initialize Socket.IO connection for real-time updates
  static void initializeSocket(
    String accessToken, {
    Function(Map<String, dynamic>)? onNewOrderAvailable,
    Function(int)? onOrderTaken,
  }) {
    _onNewOrderAvailable = onNewOrderAvailable;
    _onOrderTaken = onOrderTaken;

    _socket = IO.io(UrlConfig.baseUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': true,
      'extraHeaders': {
        'Authorization': 'Bearer $accessToken',
      }
    });

    _socket?.on('connect', (_) {
      debugPrint('✅ Socket.IO connected');
      // Join riders room to receive order notifications
      _socket?.emit('join_riders_room');
    });

    _socket?.on('joined_riders_room', (data) {
      debugPrint('✅ Joined riders room: $data');
    });

    // Listen for new orders available
    _socket?.on('new_order_available', (data) {
      debugPrint('🔔 New order available: $data');
      if (_onNewOrderAvailable != null) {
        _onNewOrderAvailable!(data as Map<String, dynamic>);
      }
    });

    // Listen for orders taken by other riders
    _socket?.on('order_taken', (data) {
      debugPrint('❌ Order taken: $data');
      if (_onOrderTaken != null && data['order_id'] != null) {
        _onOrderTaken!(data['order_id'] as int);
      }
    });

    _socket?.on('disconnect', (_) {
      debugPrint('❌ Socket.IO disconnected');
    });

    _socket?.on('error', (error) {
      debugPrint('❌ Socket.IO error: $error');
    });

    _socket?.connect();
  }

  /// Disconnect Socket.IO
  static void disconnectSocket() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
  }

  /// Get all available orders (ready for pickup)
  static Future<Map<String, dynamic>> getAvailableOrders(
      String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/rider/available-orders'),
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
          'error': 'Failed to fetch available orders: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Accept an order (FCFS - First Come First Served)
  static Future<Map<String, dynamic>> acceptOrder(
      String accessToken, int orderId) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/rider/accept-order'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'order_id': orderId,
        }),
      );

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        return data;
      } else if (response.statusCode == 409) {
        // Order already taken by another rider
        return {
          'success': false,
          'error': data['error'] ?? 'Order already taken by another rider',
          'conflict': true,
        };
      } else {
        return {
          'success': false,
          'error': data['error'] ?? 'Failed to accept order',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get rider's current and past deliveries
  static Future<Map<String, dynamic>> getMyDeliveries(
      String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/rider/my-deliveries'),
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
          'error': 'Failed to fetch deliveries: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Complete a delivery
  static Future<Map<String, dynamic>> completeDelivery(
      String accessToken, int orderId) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/rider/complete-delivery'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'order_id': orderId,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final data = json.decode(response.body);
        return {
          'success': false,
          'error': data['error'] ?? 'Failed to complete delivery',
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
