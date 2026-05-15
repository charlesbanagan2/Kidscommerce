import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/url_config.dart';
import '../models/user.dart';

class ApiService {
  static const String buildMarker = 'build-2026-04-18-01';
  // Backend API base URL - dynamic based on platform
  // Initialize with UrlConfig default value to prevent LateInitializationError
  static String baseUrl = UrlConfig.baseUrl;

  static void initializeBaseUrl() {
    try {
      if (kIsWeb) {
        baseUrl = 'http://localhost:5000';
      } else {
        baseUrl = UrlConfig.baseUrl;
      }
    } catch (e) {
      baseUrl = UrlConfig.baseUrl;
    }
  }

  static void logBuildMarker() {
    if (debugMode) {
      debugPrint('API build marker: $buildMarker');
      debugPrint('API baseUrl: $baseUrl');
    }
  }

  static const Duration _timeout = Duration(seconds: 30);
  static final http.Client _client = http.Client();
  static bool debugMode = true;

  static String? _accessToken;
  static String? _refreshToken;
  static Future<void>? _tokenLoadFuture;
  
  // Simple cache for orders to reduce API calls (public for BuyerService)
  static Map<String, dynamic>? ordersCache;
  static DateTime? ordersCacheTime;
  static const Duration cacheValidity = Duration(seconds: 30);

  static void setTokens(String accessToken, String refreshToken) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
  }

  static String? get accessToken => _accessToken;

  static bool hasAccessToken() {
    return _accessToken != null && _accessToken!.isNotEmpty;
  }

  static void clearTokens() {
    _accessToken = null;
    _refreshToken = null;
  }

  /// Get the current access token (for internal use)
  static Future<String?> _getToken() async {
    if (_accessToken != null) {
      return _accessToken;
    }
    await _ensureTokensLoaded();
    return _accessToken;
  }
  
  /// Clear orders cache
  static void clearOrdersCache() {
    ordersCache = null;
    ordersCacheTime = null;
  }

  static Future<void> _ensureTokensLoaded() async {
    if (_accessToken != null) return;
    if (_tokenLoadFuture != null) {
      await _tokenLoadFuture;
      return;
    }

    _tokenLoadFuture = () async {
      try {
        final prefs = await SharedPreferences.getInstance();
        final accessToken = prefs.getString('access_token');
        final refreshToken = prefs.getString('refresh_token');
        if (accessToken != null && refreshToken != null) {
          setTokens(accessToken, refreshToken);
        }
      } catch (e) {
        if (debugMode) {
          debugPrint('⚠️ Token restore failed: $e');
        }
      }
    }();

    try {
      await _tokenLoadFuture;
    } finally {
      _tokenLoadFuture = null;
    }
  }

  static Future<void> bootstrapFromStorage() async {
    await _ensureTokensLoaded();
  }

  static Future<void> logout() async {
    clearTokens();
  }

  static Map<String, String> _headers({bool auth = true}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (auth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
      if (debugMode) {
        final tokenPreview = _accessToken!.length > 20
            ? '${_accessToken!.substring(0, 20)}...'
            : _accessToken!;
        debugPrint('🔑 Using access token: $tokenPreview');
      }
    } else if (auth) {
      if (debugMode) {
        debugPrint('⚠️ Auth requested but no access token available');
      }
    }
    return headers;
  }

  static Future<dynamic> request(
    String method,
    String path, {
    bool auth = true,
    Map<String, dynamic>? body,
    Map<String, dynamic>? query,
  }) async {
    if (auth && _accessToken == null) {
      await _ensureTokensLoaded();
    }

    Uri uri = Uri.parse('$baseUrl$path');
    if (query != null && query.isNotEmpty) {
      final filtered = <String, String>{};
      query.forEach((key, value) {
        if (value != null) {
          filtered[key] = value.toString();
        }
      });
      uri = uri.replace(queryParameters: filtered);
    }

    if (debugMode) {
      debugPrint('ðŸ“¤ API $method $uri');
      if (body != null) {
        debugPrint('   Body: $body');
      }
    }

    http.Response response;
    try {
      switch (method.toUpperCase()) {
        case 'GET':
          response =
              await _client.get(uri, headers: _headers(auth: auth)).timeout(
            _timeout,
            onTimeout: () {
              throw TimeoutException(
                'Request timeout after ${_timeout.inSeconds}s: $method $path',
                _timeout,
              );
            },
          );
          break;
        case 'POST':
          response = await _client
              .post(
            uri,
            headers: _headers(auth: auth),
            body: jsonEncode(body ?? {}),
          )
              .timeout(
            _timeout,
            onTimeout: () {
              throw TimeoutException(
                'Request timeout after ${_timeout.inSeconds}s: $method $path',
                _timeout,
              );
            },
          );
          break;
        case 'PUT':
          response = await _client
              .put(
            uri,
            headers: _headers(auth: auth),
            body: jsonEncode(body ?? {}),
          )
              .timeout(
            _timeout,
            onTimeout: () {
              throw TimeoutException(
                'Request timeout after ${_timeout.inSeconds}s: $method $path',
                _timeout,
              );
            },
          );
          break;
        case 'DELETE':
          response = await _client
              .delete(
            uri,
            headers: _headers(auth: auth),
            body: jsonEncode(body ?? {}),
          )
              .timeout(
            _timeout,
            onTimeout: () {
              throw TimeoutException(
                'Request timeout after ${_timeout.inSeconds}s: $method $path',
                _timeout,
              );
            },
          );
          break;
        default:
          throw ApiException(message: 'Unsupported method: $method');
      }

      if (debugMode) {
        debugPrint(
          'ðŸ“¥ API Response (${response.statusCode}): ${response.body.substring(0, 200.clamp(0, response.body.length))}',
        );
      }
    } on TimeoutException catch (e) {
      debugPrint('âŒ Timeout Error: $e');
      throw ApiException(
        message: 'Request timeout. Server not responding.',
        originalException: e as Exception,
      );
    } catch (e) {
      // Handle network errors and other exceptions
      final errorMsg = e.toString();
      if (errorMsg.contains('Socket') ||
          errorMsg.contains('Connection') ||
          errorMsg.contains('Network')) {
        debugPrint('âŒ Network Error: $e');
        throw ApiException(
          message: 'Network error: Check internet connection.',
          originalException: e as Exception,
        );
      }
      debugPrint('âŒ Request Error: $e');
      rethrow;
    }

    return _handleResponse(response);
  }

  static dynamic _handleResponse(http.Response response) {
    dynamic payload;
    try {
      payload = jsonDecode(response.body);
    } catch (e) {
      throw ApiException(
        message: 'Invalid response from server',
        statusCode: response.statusCode,
        originalException: e as Exception?,
      );
    }

    if (response.statusCode >= 400) {
      String message = 'Request failed';
      if (payload is Map) {
        message = payload['error']?.toString() ??
            payload['message']?.toString() ??
            message;
      }
      throw ApiException(
        message: message,
        statusCode: response.statusCode,
      );
    }

    if (payload is Map) {
      return payload.cast<String, dynamic>();
    }
    return payload;
  }

  static Future<dynamic> requestWithRetry(
    String method,
    String path, {
    bool auth = true,
    Map<String, dynamic>? body,
    Map<String, dynamic>? query,
    int maxRetries = 1,
  }) async {
    for (int attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        final result =
            await request(method, path, auth: auth, body: body, query: query);

        // Validate response for checkout endpoint
        if (path.contains('/checkout') && result is Map) {
          if (result.containsKey('products') ||
              result.containsKey('pagination')) {
            if (debugMode) {
              debugPrint('⚠️ Wrong response for checkout, retrying...');
            }
            if (attempt < maxRetries) {
              await Future.delayed(const Duration(milliseconds: 300));
              continue;
            }
            throw ApiException(message: 'Invalid response from server');
          }
        }

        return result;
      } on ApiException catch (e) {
        // Handle 401 - refresh token and retry once
        if (e.statusCode == 401 && _refreshToken != null && attempt == 0) {
          if (debugMode) {
            debugPrint('🔄 401 error, refreshing token...');
          }
          try {
            await refreshToken();
            if (debugMode) {
              debugPrint('✅ Token refreshed, retrying...');
            }
            await Future.delayed(const Duration(milliseconds: 200));
            continue;
          } catch (refreshError) {
            if (debugMode) {
              debugPrint('❌ Token refresh failed: $refreshError');
            }
            rethrow;
          }
        }

        // If last attempt, throw error
        if (attempt >= maxRetries) {
          rethrow;
        }

        // Retry with delay
        if (debugMode) {
          debugPrint('⚠️ Retry ${attempt + 1}/$maxRetries');
        }
        await Future.delayed(Duration(milliseconds: 500 * (attempt + 1)));
      }
    }

    throw ApiException(message: 'Request failed after retries');
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    final result = await request(
      'POST',
      '/api/login',
      auth: false,
      body: {'email': email, 'password': password},
    );
    // Handle nested tokens format from /api/login
    final tokensData = result['tokens'] as Map<String, dynamic>?;
    String? accessToken;
    String? refreshToken;

    if (tokensData != null) {
      accessToken = tokensData['access_token']?.toString();
      refreshToken = tokensData['refresh_token']?.toString();
    } else {
      // Fallback for old format (if migrate helpers ever revert)
      accessToken = result['access_token']?.toString();
      refreshToken = result['refresh_token']?.toString();
    }

    if (accessToken != null && refreshToken != null) {
      setTokens(accessToken, refreshToken);
    }
    return result;
  }

  static Future<Map<String, dynamic>> register(
    Map<String, dynamic> regRequest,
  ) async {
    final result = await request(
      'POST',
      '/api/register',
      auth: false,
      body: regRequest,
    );
    return result;
  }

  static Future<Map<String, dynamic>> refreshToken() async {
    if (_refreshToken == null) {
      throw ApiException(message: 'No refresh token available');
    }
    final result = await request(
      'POST',
      '/api/refresh',
      auth: false,
      body: {'refresh_token': _refreshToken},
    );
    final accessToken = result['access_token']?.toString();
    final refreshToken = result['refresh_token']?.toString();
    if (accessToken != null && refreshToken != null) {
      setTokens(accessToken, refreshToken);
    }
    return result;
  }

  static Future<List<dynamic>> getProducts({
    String? search,
    int page = 1,
    int perPage = 20,
    bool inStockOnly = false,
    bool bustCache = false,
  }) async {
    final queryParams = {
      'search': search,
      'page': page,
      'per_page': perPage,
      'in_stock': inStockOnly ? 'true' : null,
    };
    
    // Add timestamp to bust cache when needed
    if (bustCache) {
      queryParams['_t'] = DateTime.now().millisecondsSinceEpoch.toString();
    }
    
    final result = await request(
      'GET',
      '/api/v1/products',
      auth: false,
      query: queryParams,
    );
    if (result is List) {
      return result;
    }
    if (result is Map<String, dynamic> && result['products'] is List) {
      return result['products'] as List<dynamic>;
    }
    return <dynamic>[];
  }

  static Future<dynamic> getCart() {
    return request('GET', '/api/v1/cart');
  }

  static Future<dynamic> addToCart(
    int productId, {
    int quantity = 1,
  }) {
    return request(
      'POST',
      '/api/v1/cart',
      body: {'product_id': productId, 'quantity': quantity},
    );
  }

  static Future<dynamic> updateCartItem(
    int cartItemId, {
    required int quantity,
  }) {
    return request(
      'PUT',
      '/api/v1/cart/$cartItemId',
      body: {'quantity': quantity},
    );
  }

  static Future<dynamic> removeFromCart(int cartItemId) {
    return request(
      'DELETE',
      '/api/v1/cart/$cartItemId',
    );
  }

  static Future<dynamic> createOrder({
    required String deliveryAddress,
    String paymentMethod = 'cod',
    bool useCart = true,
    List<Map<String, dynamic>>? items,
  }) {
    return request(
      'POST',
      '/api/v1/orders',
      body: {
        'shipping_address': deliveryAddress,
        'payment_method': paymentMethod.toUpperCase(),
        if (!useCart && items != null) 'items': items,
      },
    );
  }

  static Future<List<dynamic>> getUserOrders() async {
    final result = await request('GET', '/api/v1/orders');
    if (result is List) {
      return result;
    }
    if (result is Map<String, dynamic> && result['orders'] is List) {
      return result['orders'] as List<dynamic>;
    }
    return <dynamic>[];
  }

  static Future<Map<String, dynamic>> getRiderEarnings() async {
    try {
      final result = await request('GET', '/api/v1/rider/earnings');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'today': 0, 'week': 0, 'month': 0, 'total': 0};
    } catch (e) {
      debugPrint('⚠️ Earnings endpoint not available: $e');
      return <String, dynamic>{'today': 0, 'week': 0, 'month': 0, 'total': 0};
    }
  }

  static Future<Map<String, dynamic>> getProductReviews(int productId) async {
    final result = await request(
      'GET',
      '/api/products/$productId/reviews',
      auth: false,
    );
    return result is Map<String, dynamic>
        ? result
        : <String, dynamic>{'success': false, 'reviews': <dynamic>[]};
  }

  static Future<Map<String, dynamic>> submitReview({
    required int productId,
    required int rating,
    String? title,
    String? content,
    List<String>? imageUrls,
    List<String>? videoUrls,
  }) async {
    final result = await request(
      'POST',
      '/api/reviews',
      body: {
        'product_id': productId,
        'rating': rating,
        'title': title,
        'content': content,
        'image_urls': imageUrls ?? <String>[],
        'video_urls': videoUrls ?? <String>[],
      },
    );
    return result is Map<String, dynamic>
        ? result
        : <String, dynamic>{'success': false};
  }

  static Future<List<Map<String, dynamic>>> getRiderOrders() async {
    final result = await request('GET', '/api/v1/rider/my-deliveries');
    final rows = (result['orders'] as List?) ?? <dynamic>[];
    return rows
        .map((e) => (e as Map).cast<String, dynamic>())
        .toList(growable: false);
  }

  static Future<List<Map<String, dynamic>>> getRiderAvailableOrders() async {
    final result = await request('GET', '/api/v1/rider/available-orders');
    final rows = (result['orders'] as List?) ?? <dynamic>[];
    return rows
        .map((e) => (e as Map).cast<String, dynamic>())
        .toList(growable: false);
  }

  static Future<Map<String, dynamic>> acceptRiderOrder(int orderId) async {
    final result = await request(
      'POST',
      '/api/v1/rider/accept-order',
      body: {'order_id': orderId},
    );
    return result is Map<String, dynamic>
        ? result
        : <String, dynamic>{'success': false};
  }

  static Future<Map<String, dynamic>> markOrderAsDelivered(int orderId) async {
    try {
      debugPrint('📦 Marking order $orderId as delivered');
      final result = await request(
        'POST',
        '/api/v1/rider/complete-delivery',
        body: {'order_id': orderId},
      );
      debugPrint('✅ Mark delivered response: $result');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error marking as delivered: $e');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> declineRiderOrder(int orderId) async {
    final result = await request(
      'POST',
      '/api/v1/rider/decline-order',
      body: {'order_id': orderId},
    );
    return result is Map<String, dynamic>
        ? result
        : <String, dynamic>{'success': false};
  }

  static Future<dynamic> updateOrderStatus({
    required int orderId,
    required String status,
    int? riderId,
  }) {
    return request(
      'PUT',
      '/api/orders/status',
      body: {
        'order_id': orderId,
        'status': status,
        if (riderId != null) 'rider_id': riderId,
      },
    );
  }

  static Future<bool> isConnected() async {
    try {
      final payload = await request('GET', '/api/health', auth: false);
      return payload['success'] == true;
    } catch (_) {
      return false;
    }
  }

  static Future<User> getUserProfile() async {
    final result = await request('GET', '/api/user/profile');
    return User.fromJson(result['user'] ?? result);
  }

  static Future<User> updateUserProfile(Map<String, dynamic> updates) async {
    final result = await request('PUT', '/api/user/profile', body: updates);
    return User.fromJson(result['user'] ?? result);
  }

  static Future<String> uploadDeliveryProof({
    required int orderId,
    required File file,
  }) async {
    try {
      debugPrint('📷 Uploading proof for order $orderId');
      debugPrint('📷 File path: ${file.path}');
      
      // Try multiple possible endpoints
      final possibleEndpoints = [
        '/api/v1/rider/orders/$orderId/upload-proof',
        '/api/orders/$orderId/upload-proof',
        '/api/v1/orders/$orderId/upload-proof',
        '/api/rider/orders/$orderId/upload-proof',
      ];
      
      for (final endpoint in possibleEndpoints) {
        try {
          final uri = Uri.parse('$baseUrl$endpoint');
          debugPrint('📷 Trying upload URI: $uri');
          
          final request = http.MultipartRequest('POST', uri);
          request.headers['Authorization'] = 'Bearer $_accessToken';
          request.files.add(await http.MultipartFile.fromPath('proof_photo', file.path));
          
          debugPrint('📷 Sending request...');
          final response = await request.send().timeout(
            const Duration(seconds: 15),
            onTimeout: () => throw TimeoutException('Upload timeout'),
          );
          final responseBody = await response.stream.bytesToString();
          debugPrint('📷 Response status: ${response.statusCode}');
          
          if (response.statusCode == 404) {
            debugPrint('⚠️ Endpoint not found, trying next...');
            continue;
          }
          
          debugPrint('📷 Response body: $responseBody');
          
          try {
            final result = jsonDecode(responseBody);
            
            if (response.statusCode >= 400) {
              throw ApiException(
                message: result['error'] ?? 'Upload failed',
                statusCode: response.statusCode,
              );
            }
            
            final photoUrl = result['proof_photo_url'] ?? result['photo_url'] ?? '/uploads/proof_$orderId.jpg';
            debugPrint('✅ Photo uploaded successfully: $photoUrl');
            return photoUrl;
          } catch (e) {
            if (e is ApiException) rethrow;
            // If JSON decode fails but status is 200, consider it success
            if (response.statusCode == 200) {
              debugPrint('✅ Upload successful (non-JSON response)');
              return '/uploads/proof_$orderId.jpg';
            }
            throw ApiException(message: 'Invalid response format');
          }
        } catch (e) {
          if (e is TimeoutException) {
            debugPrint('⏱️ Upload timeout, trying next endpoint...');
            continue;
          }
          if (e is ApiException && e.statusCode != 404) {
            rethrow;
          }
          debugPrint('⚠️ Error with endpoint: $e');
          continue;
        }
      }
      
      // All endpoints failed - throw clear error
      throw ApiException(
        message: 'Backend upload endpoint not implemented. Please contact support.',
        statusCode: 501,
      );
    } catch (e) {
      debugPrint('❌ Upload error: $e');
      rethrow;
    }
  }

  static Future<List<dynamic>> getOrderChatMessages({required int orderId}) async {
    final result = await request('GET', '/api/v1/orders/$orderId/messages');
    if (result is List) {
      return result;
    }
    if (result is Map<String, dynamic> && result['messages'] is List) {
      return result['messages'] as List<dynamic>;
    }
    return <dynamic>[];
  }

  static Future<Map<String, dynamic>> sendChatMessage({
    required int orderId,
    required String message,
    required String senderRole,
  }) async {
    final result = await request(
      'POST',
      '/api/v1/orders/$orderId/messages',
      body: {
        'message': message,
        'sender_role': senderRole,
      },
    );
    return result is Map<String, dynamic>
        ? result
        : <String, dynamic>{'success': false};
  }

  // ============= NOTIFICATION METHODS =============

  static Future<Map<String, dynamic>> getNotifications({Map<String, dynamic>? query}) async {
    try {
      final result = await request('GET', '/api/v1/notifications', query: query);
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false, 'notifications': <dynamic>[]};
    } catch (e) {
      debugPrint('❌ Error fetching notifications: $e');
      return <String, dynamic>{'success': false, 'notifications': <dynamic>[]};
    }
  }

  static Future<int> getUnreadNotificationsCount() async {
    try {
      final result = await request('GET', '/api/v1/notifications/unread-count');
      return (result['unread_count'] as num?)?.toInt() ?? 0;
    } catch (e) {
      debugPrint('⚠️ Error getting unread count: $e');
      return 0;
    }
  }

  static Future<bool> markNotificationRead(int notificationId) async {
    try {
      final result = await request(
        'PUT',
        '/api/v1/notifications/$notificationId/read',
      );
      return result['success'] == true;
    } catch (e) {
      debugPrint('❌ Error marking notification as read: $e');
      return false;
    }
  }

  static Future<bool> markAllNotificationsRead() async {
    try {
      final result = await request(
        'PUT',
        '/api/v1/notifications/mark-all-read',
      );
      return result['success'] == true;
    } catch (e) {
      debugPrint('❌ Error marking all as read: $e');
      return false;
    }
  }

  static Future<bool> deleteNotification(int notificationId) async {
    try {
      final result = await request(
        'DELETE',
        '/api/v1/notifications/$notificationId',
      );
      return result['success'] == true;
    } catch (e) {
      debugPrint('❌ Error deleting notification: $e');
      return false;
    }
  }

  static Future<Map<String, dynamic>> clearAllReadNotifications() async {
    try {
      final result = await request('DELETE', '/api/v1/notifications/clear-all');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error clearing read notifications: $e');
      return <String, dynamic>{'success': false};
    }
  }

  static Future<Map<String, dynamic>> getNotificationSettings() async {
    try {
      final result = await request('GET', '/api/v1/notifications/settings');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error getting notification settings: $e');
      return <String, dynamic>{'success': false};
    }
  }

  static Future<bool> updateNotificationSettings(Map<String, dynamic> settings) async {
    try {
      final result = await request('PUT', '/api/v1/notifications/settings', body: settings);
      return result['success'] == true;
    } catch (e) {
      debugPrint('❌ Error updating notification settings: $e');
      return false;
    }
  }

  // ============= CHAT METHODS =============

  static Future<List<dynamic>> getChatConversations() async {
    try {
      final result = await request('GET', '/api/v1/chat/conversations');
      if (result is Map<String, dynamic> && result['conversations'] is List) {
        return result['conversations'] as List<dynamic>;
      }
      return <dynamic>[];
    } catch (e) {
      debugPrint('❌ Error fetching conversations: $e');
      return <dynamic>[];
    }
  }

  static Future<List<dynamic>> getChatMessages({
    required int peerId,
    bool isSeller = true,
  }) async {
    try {
      final result = await request(
        'GET',
        '/api/v1/chat/messages/$peerId',
        query: {'is_seller': isSeller.toString()},
      );
      if (result is Map<String, dynamic> && result['messages'] is List) {
        return result['messages'] as List<dynamic>;
      }
      return <dynamic>[];
    } catch (e) {
      debugPrint('❌ Error fetching messages: $e');
      return <dynamic>[];
    }
  }

  static Future<bool> sendChatMessageNew({
    required int recipientId,
    required String content,
    bool isSeller = true,
  }) async {
    try {
      final result = await request(
        'POST',
        '/api/v1/chat/send',
        body: {
          'recipient_id': recipientId,
          'content': content,
          'is_seller': isSeller,
        },
      );
      return result['success'] == true;
    } catch (e) {
      debugPrint('❌ Error sending message: $e');
      return false;
    }
  }

  static Future<int> getUnreadMessagesCount() async {
    try {
      final result = await request('GET', '/api/v1/chat/unread-count');
      return (result['unread_count'] as num?)?.toInt() ?? 0;
    } catch (e) {
      debugPrint('⚠️ Error getting unread messages count: $e');
      return 0;
    }
  }

  // ============= PRODUCT CHAT METHODS =============

  static Future<Map<String, dynamic>> startProductChat({
    required int productId,
    String? message,
  }) async {
    try {
      final result = await request(
        'POST',
        '/api/v1/chat/product/start',
        body: {
          'product_id': productId,
          if (message != null) 'message': message,
        },
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error starting product chat: $e');
      return <String, dynamic>{
        'success': false,
        'error': 'Failed to start chat. Please try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> getProductChatMessages(int productId) async {
    try {
      final result = await request(
        'GET',
        '/api/v1/chat/product/$productId/messages',
      );
      if (result is Map<String, dynamic> && result['messages'] is List) {
        return result;
      }
      return <String, dynamic>{'success': true, 'messages': <dynamic>[]};
    } catch (e) {
      debugPrint('❌ Error fetching product chat messages: $e');
      return <String, dynamic>{'success': false, 'messages': <dynamic>[]};
    }
  }

  static Future<Map<String, dynamic>> sendProductMessage({
    required int productId,
    required String message,
  }) async {
    try {
      final result = await request(
        'POST',
        '/api/v1/chat/product/send',
        body: {
          'product_id': productId,
          'message': message,
        },
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error sending product message: $e');
      return <String, dynamic>{
        'success': false,
        'error': 'Failed to send message. Please try again.',
      };
    }
  }

  // ============= Wishlist Methods =============

  static Future<List<dynamic>> getWishlist() async {
    try {
      final result = await request('GET', '/api/v1/wishlist');
      if (result is List) {
        return result;
      }
      if (result is Map<String, dynamic> && result['wishlist'] is List) {
        return result['wishlist'] as List<dynamic>;
      }
      return <dynamic>[];
    } catch (e) {
      debugPrint('❌ Error fetching wishlist: $e');
      return <dynamic>[];
    }
  }

  static Future<Map<String, dynamic>> addToWishlist(int productId) async {
    try {
      final result = await request(
        'POST',
        '/api/v1/wishlist',
        body: {'product_id': productId},
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error adding to wishlist: $e');
      return <String, dynamic>{
        'success': false,
        'message': 'Failed to add to wishlist. Please try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> removeFromWishlist(int productId) async {
    try {
      final result = await request(
        'DELETE',
        '/api/v1/wishlist/$productId',
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('❌ Error removing from wishlist: $e');
      return <String, dynamic>{
        'success': false,
        'message': 'Failed to remove from wishlist. Please try again.',
      };
    }
  }

  static Future<bool> isInWishlist(int productId) async {
    try {
      final wishlist = await getWishlist();
      return wishlist.any((item) => 
        (item['product_id'] as int?) == productId ||
        (item['id'] as int?) == productId
      );
    } catch (e) {
      debugPrint('⚠️ Error checking wishlist: $e');
      return false;
    }
  }

  /// Upload multipart data with files
  static Future<Map<String, dynamic>> uploadMultipart(
    String method,
    String path, {
    Map<String, File>? files,
    Map<String, String>? fields,
    bool auth = true,
  }) async {
    if (auth && _accessToken == null) {
      await _ensureTokensLoaded();
    }

    final uri = Uri.parse('$baseUrl$path');
    
    if (debugMode) {
      debugPrint('📤 Multipart $method $uri');
      if (fields != null) {
        debugPrint('   Fields: $fields');
      }
      if (files != null) {
        debugPrint('   Files: ${files.keys.join(', ')}');
      }
    }

    try {
      final request = http.MultipartRequest(method.toUpperCase(), uri);
      
      // Add headers
      if (auth && _accessToken != null) {
        request.headers['Authorization'] = 'Bearer $_accessToken';
      }
      request.headers['Accept'] = 'application/json';
      
      // Add fields
      if (fields != null) {
        request.fields.addAll(fields);
      }
      
      // Add files
      if (files != null) {
        for (final entry in files.entries) {
          request.files.add(
            await http.MultipartFile.fromPath(entry.key, entry.value.path),
          );
        }
      }
      
      final response = await request.send().timeout(
        _timeout,
        onTimeout: () {
          throw TimeoutException(
            'Upload timeout after ${_timeout.inSeconds}s: $method $path',
            _timeout,
          );
        },
      );
      
      final responseBody = await response.stream.bytesToString();
      
      if (debugMode) {
        debugPrint(
          '🔥 Multipart Response (${response.statusCode}): ${responseBody.substring(0, 200.clamp(0, responseBody.length))}',
        );
      }
      
      dynamic payload;
      try {
        payload = jsonDecode(responseBody);
      } catch (e) {
        throw ApiException(
          message: 'Invalid response from server',
          statusCode: response.statusCode,
          originalException: e as Exception?,
        );
      }
      
      if (response.statusCode >= 400) {
        String message = 'Upload failed';
        if (payload is Map) {
          message = payload['error']?.toString() ??
              payload['message']?.toString() ??
              message;
        }
        throw ApiException(
          message: message,
          statusCode: response.statusCode,
        );
      }
      
      if (payload is Map) {
        return payload.cast<String, dynamic>();
      }
      return {'success': true, 'data': payload};
    } on TimeoutException catch (e) {
      debugPrint('⌛ Upload Timeout Error: $e');
      throw ApiException(
        message: 'Upload timeout. Please try again.',
        originalException: e as Exception,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      
      final errorMsg = e.toString();
      if (errorMsg.contains('Socket') ||
          errorMsg.contains('Connection') ||
          errorMsg.contains('Network')) {
        debugPrint('⌛ Upload Network Error: $e');
        throw ApiException(
          message: 'Network error during upload. Check internet connection.',
          originalException: e as Exception,
        );
      }
      debugPrint('⌛ Upload Error: $e');
      rethrow;
    }
  }
  // -----------------------------------------------------------
  // RETURN & REFUND API
  // -----------------------------------------------------------

  /// Upload return evidence (image/video)
  static Future<String?> uploadReturnEvidence(File file) async {
    try {
      final uri = Uri.parse('${UrlConfig.baseUrl}/api/return-evidence/upload');
      final request = http.MultipartRequest('POST', uri);
      
      // Add auth token
      final token = await _getToken();
      if (token != null) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      
      // Add file
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          file.path,
          filename: file.path.split('/').last,
        ),
      );
      
      // Send request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          return data['url'];
        }
      }
      
      debugPrint('Upload failed: ${response.body}');
      return null;
    } catch (e) {
      debugPrint('Error uploading return evidence: $e');
      return null;
    }
  }

  static Future<Map<String, dynamic>> createReturnRequest(
    int orderId,
    Map<String, dynamic> requestData,
  ) async {
    try {
      final result = await request(
        'POST',
        '/api/buyer/orders/$orderId/return-request',
        body: requestData,
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('Error creating return request: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> getBuyerReturnRequests() async {
    try {
      final result = await request('GET', '/api/buyer/return-requests');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('Error fetching return requests: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> getSellerReturnRequests() async {
    try {
      final result = await request('GET', '/api/seller/return-requests');
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('Error fetching seller return requests: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> approveReturnRequest(int returnId) async {
    try {
      final result = await request(
        'POST',
        '/api/seller/return-requests/$returnId/approve',
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('Error approving return: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> rejectReturnRequest(
    int returnId,
    String reason,
  ) async {
    try {
      final result = await request(
        'POST',
        '/api/seller/return-requests/$returnId/reject',
        body: {'reason': reason},
      );
      return result is Map<String, dynamic>
          ? result
          : <String, dynamic>{'success': false};
    } catch (e) {
      debugPrint('Error rejecting return: $e');
      return {'success': false, 'error': e.toString()};
    }
  }
}

/// Custom exception class for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final Exception? originalException;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalException,
  });

  @override
  String toString() {
    if (statusCode != null) {
      return 'ApiException: [$statusCode] $message';
    }
    return 'ApiException: $message';
  }
}

