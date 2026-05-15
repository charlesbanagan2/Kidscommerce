import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../config/url_config.dart';

/// Complete Rider Service for Mobile App Only
/// All rider functionality accessible via API
class RiderMobileService {
  static IO.Socket? _socket;
  static Function(Map<String, dynamic>)? _onNewOrderAvailable;
  static Function(int)? _onOrderClaimed;
  
  /// Initialize Socket.IO for real-time order notifications
  static void initializeSocket(String accessToken, {
    Function(Map<String, dynamic>)? onNewOrderAvailable,
    Function(int)? onOrderClaimed,
  }) {
    _onNewOrderAvailable = onNewOrderAvailable;
    _onOrderClaimed = onOrderClaimed;
    
    _socket = IO.io(UrlConfig.baseUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': true,
      'extraHeaders': {
        'Authorization': 'Bearer $accessToken',
      }
    });
    
    _socket?.on('connect', (_) {
      debugPrint('✅ Rider Socket.IO connected');
      _socket?.emit('join_riders_room');
    });
    
    _socket?.on('joined_riders_room', (data) {
      debugPrint('✅ Joined riders room: $data');
    });
    
    // Listen for new orders
    _socket?.on('new_order_available', (data) {
      debugPrint('🔔 New order available: $data');
      if (_onNewOrderAvailable != null) {
        _onNewOrderAvailable!(data as Map<String, dynamic>);
      }
    });
    
    // Listen for orders claimed by other riders
    _socket?.on('order_claimed', (data) {
      debugPrint('❌ Order claimed: $data');
      if (_onOrderClaimed != null && data['order_id'] != null) {
        _onOrderClaimed!(data['order_id'] as int);
      }
    });
    
    _socket?.on('disconnect', (_) {
      debugPrint('❌ Rider Socket.IO disconnected');
    });
    
    _socket?.on('error', (error) {
      debugPrint('❌ Rider Socket.IO error: $error');
    });
    
    _socket?.connect();
  }
  
  /// Disconnect Socket.IO
  static void disconnectSocket() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
  }
  
  /// Register new rider
  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String phone,
    required String address,
    required String vehicleType,
    required String vehicleModel,
    required String plateNumber,
    File? validIdFront,
    File? validIdBack,
    File? driversLicense,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/register'),
      );
      
      // Add form fields
      request.fields['email'] = email;
      request.fields['password'] = password;
      request.fields['first_name'] = firstName;
      request.fields['last_name'] = lastName;
      request.fields['phone'] = phone;
      request.fields['address'] = address;
      request.fields['vehicle_type'] = vehicleType;
      request.fields['vehicle_model'] = vehicleModel;
      request.fields['plate_number'] = plateNumber;
      
      // Add files
      if (validIdFront != null) {
        request.files.add(await http.MultipartFile.fromPath(
          'valid_id_front',
          validIdFront.path,
        ));
      }
      
      if (validIdBack != null) {
        request.files.add(await http.MultipartFile.fromPath(
          'valid_id_back',
          validIdBack.path,
        ));
      }
      
      if (driversLicense != null) {
        request.files.add(await http.MultipartFile.fromPath(
          'drivers_license',
          driversLicense.path,
        ));
      }
      
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 201 || response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        final data = json.decode(responseBody);
        return {
          'success': false,
          'error': data['error'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  /// Get available orders (FCFS)
  static Future<Map<String, dynamic>> getAvailableOrders(String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/available-orders'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 403) {
        return {
          'success': false,
          'error': 'Your account is not approved yet',
        };
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch orders: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  /// Accept order (FCFS with conflict handling)
  static Future<Map<String, dynamic>> acceptOrder(
    String accessToken,
    int orderId,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/accept-order'),
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
        // Order already taken (FCFS conflict)
        return {
          'success': false,
          'error': data['error'] ?? 'Order already taken by another rider',
          'conflict': true,
        };
      } else if (response.statusCode == 403) {
        return {
          'success': false,
          'error': 'Your account is not approved',
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
  
  /// Get my deliveries
  static Future<Map<String, dynamic>> getMyDeliveries(
    String accessToken, {
    String? status,
  }) async {
    try {
      var uri = Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/my-deliveries');
      
      if (status != null) {
        uri = uri.replace(queryParameters: {'status': status});
      }
      
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
  
  /// Complete delivery
  static Future<Map<String, dynamic>> completeDelivery(
    String accessToken,
    int orderId,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/complete-delivery'),
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
  
  /// Get earnings statistics
  static Future<Map<String, dynamic>> getEarnings(String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/earnings'),
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
          'error': 'Failed to fetch earnings',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  /// Get rider profile
  static Future<Map<String, dynamic>> getProfile(String accessToken) async {
    try {
      final response = await http.get(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/profile'),
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
          'error': 'Failed to fetch profile',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  /// Update rider profile
  static Future<Map<String, dynamic>> updateProfile(
    String accessToken,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await http.put(
        Uri.parse('${UrlConfig.baseUrl}/api/v1/rider/profile'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: json.encode(updates),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final data = json.decode(response.body);
        return {
          'success': false,
          'error': data['error'] ?? 'Failed to update profile',
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
