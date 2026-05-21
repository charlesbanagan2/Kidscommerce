import 'package:flutter/foundation.dart';
import 'dart:async';
import 'dart:io';
import '../models/order.dart' hide CartItem;
import '../services/api_service.dart';

/// BuyerProvider manages buyer-specific data and operations
class BuyerService {
  static const String baseVersion = '/api/v1';
  static const String _cartPath = '$baseVersion/buyer/cart';

  /// Clear orders cache to force fresh fetch
  static void clearOrdersCache() {
    ApiService.clearOrdersCache();
  }

  // ============= Orders APIs =============

  /// Get all orders for current buyer with optional status filter
  static Future<List<Order>> getOrders({String? status}) async {
    try {
      final query = status != null ? {'status': status} : null;
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/orders',
        auth: true,
        query: query,
      );

      if (result['success'] == true && result['orders'] != null) {
        final orders = (result['orders'] as List)
            .map((order) => Order.fromJson(order))
            .toList();
        return orders;
      }
      throw Exception(result['error'] ?? 'Failed to fetch orders');
    } catch (e) {
      throw Exception('Error fetching orders: $e');
    }
  }

  /// Get orders grouped by status (to_pay, to_ship, to_receive, completed, returns, cancelled)
  static Future<Map<String, List<Order>>> getOrdersByStatus() async {
    try {
      debugPrint('📦 BuyerService: Fetching orders by status...');

      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/orders/by-status',
        auth: true,
      );

      debugPrint('📦 API Response type: ${result.runtimeType}');
      debugPrint('📦 API Response keys: ${result is Map ? result.keys.toList() : "not a map"}');

      if (result is! Map<String, dynamic>) {
        debugPrint('⚠️ Invalid response type, returning empty');
        return {};
      }

      if (result['success'] == true) {
        final Map<String, List<Order>> groupedOrders = {};
        result.forEach((key, value) {
          if (key != 'success' && key != 'counts' && value is List) {
            try {
              final orders = value.map((order) => Order.fromJson(order)).toList();
              groupedOrders[key] = orders;
              debugPrint('✅ Parsed $key: ${orders.length} orders');
              if (orders.isNotEmpty) {
                debugPrint('   First order in $key: #${orders.first.id}');
              }
            } catch (e) {
              debugPrint('⚠️ Error parsing orders for status "$key": $e');
            }
          }
        });
        
        debugPrint('✅ Total groups: ${groupedOrders.keys.length}');
        return groupedOrders;
      }

      debugPrint('⚠️ API returned success=false');
      return {};
    } catch (e) {
      debugPrint('⚠️ Orders fetch failed (backend issue): $e');
      return {};
    }
  }

  /// Get specific order details
  static Future<Order> getOrderDetail(int orderId) async {
    try {
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/orders/$orderId',
        auth: true,
      );

      if (result['success'] == true && result['order'] != null) {
        final orderJson = result['order'];

        // Debug: Log raw order data for Order #55
        if (orderId == 55) {
          debugPrint('🔍🔍🔍 RAW ORDER #55 API RESPONSE:');
          debugPrint('Order JSON: ${orderJson.toString()}');
          debugPrint('rider_id: ${orderJson['rider_id']}');
          debugPrint('rider_name: ${orderJson['rider_name']}');
          debugPrint('rider_phone: ${orderJson['rider_phone']}');
          debugPrint(
              'rider_profile_picture: ${orderJson['rider_profile_picture']}');
          debugPrint('status: ${orderJson['status']}');
          debugPrint('🔍🔍🔍 END ORDER #55 RAW RESPONSE');
        }

        return Order.fromJson(orderJson);
      }
      throw Exception(result['error'] ?? 'Failed to fetch order details');
    } catch (e) {
      throw Exception('Error fetching order detail: $e');
    }
  }

  /// Cancel an order
  static Future<bool> cancelOrder(int orderId, {String? reason}) async {
    try {
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/orders/$orderId/cancel',
        auth: true,
        body: {'reason': reason ?? 'No reason provided'},
      );

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error cancelling order: $e');
    }
  }

  /// Confirm order receipt/delivery
  static Future<bool> confirmDelivery(int orderId) async {
    try {
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/orders/$orderId/confirm-delivery',
        auth: true,
      );

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error confirming delivery: $e');
    }
  }

  // ============= Returns APIs =============

  /// Get all return requests for current buyer
  static Future<List<ReturnRequest>> getReturns() async {
    try {
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/returns',
        auth: true,
      );

      if (result['success'] == true && result['returns'] != null) {
        final returns = (result['returns'] as List)
            .map((ret) => ReturnRequest.fromJson(ret))
            .toList();
        return returns;
      }
      throw Exception(result['error'] ?? 'Failed to fetch returns');
    } catch (e) {
      throw Exception('Error fetching returns: $e');
    }
  }

  /// Get specific return request details
  static Future<ReturnRequest> getReturnDetail(int returnId) async {
    try {
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/returns/$returnId',
        auth: true,
      );

      if (result['success'] == true && result['return'] != null) {
        return ReturnRequest.fromJson(result['return']);
      }
      throw Exception(result['error'] ?? 'Failed to fetch return details');
    } catch (e) {
      throw Exception('Error fetching return detail: $e');
    }
  }

  /// Create a new return request
  static Future<ReturnRequest> createReturnRequest({
    required int orderId,
    required String reason,
    required String description,
    List<String>? mediaUrls,
  }) async {
    try {
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/orders/$orderId/return',
        auth: true,
        body: {
          'reason': reason,
          'description': description,
          'media_urls': mediaUrls ?? [],
        },
      );

      if (result['success'] == true && result['return'] != null) {
        return ReturnRequest.fromJson(result['return']);
      }
      throw Exception(result['error'] ?? 'Failed to create return request');
    } catch (e) {
      throw Exception('Error creating return request: $e');
    }
  }

  /// Submit return request
  static Future<bool> submitReturnRequest({
    required int orderId,
    required String reason,
    required String description,
  }) async {
    try {
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/orders/$orderId/return',
        auth: true,
        body: {
          'reason': reason,
          'description': description,
        },
      );

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error submitting return request: $e');
    }
  }

  /// Submit order rating
  static Future<bool> submitOrderRating({
    required int orderId,
    required int rating,
    required String comment,
  }) async {
    try {
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/orders/$orderId/rating',
        auth: true,
        body: {
          'rating': rating,
          'comment': comment,
        },
      );

      // Also submit to product review endpoint (workaround for backend bug)
      if (result['success'] == true) {
        try {
          // Get order details to find product IDs
          final orderResult = await ApiService.request(
            'GET',
            '$baseVersion/buyer/orders/$orderId',
            auth: true,
          );

          if (orderResult['success'] == true && orderResult['order'] != null) {
            final order = orderResult['order'];
            final items = order['items'] as List?;

            if (items != null && items.isNotEmpty) {
              // Submit review for each product in the order
              for (var item in items) {
                final productId = item['product_id'] as int?;
                if (productId != null) {
                  try {
                    await ApiService.submitReview(
                      productId: productId,
                      rating: rating,
                      title: '',
                      content: comment,
                    );
                    debugPrint(
                        '✅ Product review submitted for product $productId');
                  } catch (e) {
                    debugPrint('⚠️ Failed to submit product review: $e');
                  }
                }
              }
            }
          }
        } catch (e) {
          debugPrint('⚠️ Failed to submit product reviews: $e');
        }
      }

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error submitting rating: $e');
    }
  }

  /// Submit order rating with media files
  static Future<bool> submitOrderRatingWithMedia({
    required int orderId,
    required int rating,
    required String comment,
    required List<File> mediaFiles,
  }) async {
    try {
      // If no media files, use regular rating submission
      if (mediaFiles.isEmpty) {
        return submitOrderRating(
          orderId: orderId,
          rating: rating,
          comment: comment,
        );
      }

      // Use multipart request for media upload
      final result = await ApiService.uploadMultipart(
        'POST',
        '$baseVersion/buyer/orders/$orderId/rating',
        files: mediaFiles.asMap().map((index, file) => MapEntry(
              'media_$index',
              file,
            )),
        fields: {
          'rating': rating.toString(),
          'comment': comment,
        },
      );

      // Also submit to product review endpoint (workaround for backend bug)
      if (result['success'] == true) {
        try {
          // Get order details to find product IDs
          final orderResult = await ApiService.request(
            'GET',
            '$baseVersion/buyer/orders/$orderId',
            auth: true,
          );

          if (orderResult['success'] == true && orderResult['order'] != null) {
            final order = orderResult['order'];
            final items = order['items'] as List?;

            if (items != null && items.isNotEmpty) {
              // Submit review for each product in the order
              for (var item in items) {
                final productId = item['product_id'] as int?;
                if (productId != null) {
                  try {
                    await ApiService.uploadMultipart(
                      'POST',
                      '/api/reviews',
                      files: mediaFiles.asMap().map((index, file) => MapEntry(
                            'media_$index',
                            file,
                          )),
                      fields: {
                        'product_id': productId.toString(),
                        'rating': rating.toString(),
                        'title': '',
                        'content': comment,
                      },
                    );
                    debugPrint(
                        '✅ Product review submitted for product $productId');
                  } catch (e) {
                    debugPrint('⚠️ Failed to submit product review: $e');
                  }
                }
              }
            }
          }
        } catch (e) {
          debugPrint('⚠️ Failed to submit product reviews: $e');
        }
      }

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error submitting rating with media: $e');
    }
  }

  // ============= Cart APIs =============

  /// Get all items in the cart
  static Future<List<dynamic>> getCart() async {
    try {
      final result = await ApiService.request(
        'GET',
        _cartPath,
        auth: true,
      );

      // The backend returns a direct list of cart items
      if (result is List) {
        return result;
      }
      // Handle cases where it might be wrapped in a 'cart' key
      if (result is Map && result['cart'] is List) {
        return result['cart'] as List;
      }
      // Handle cases where it might be wrapped in a 'items' key
      if (result is Map && result['items'] is List) {
        return result['items'] as List;
      }

      throw Exception('Failed to parse cart items from response');
    } catch (e) {
      debugPrint('Error fetching cart: $e');
      throw Exception('Error fetching cart: $e');
    }
  }

  /// Add an item to the cart
  static Future<dynamic> addToCart({
    required int productId,
    required int quantity,
    String? size,
    String? color,
  }) async {
    try {
      final result = await ApiService.request(
        'POST',
        _cartPath,
        auth: true,
        body: {
          'product_id': productId,
          'quantity': quantity,
          'size': size,
          'color': color,
        },
      );

      if (result['success'] == true && result['cart_item'] != null) {
        return result['cart_item'];
      }
      throw Exception(result['error'] ?? 'Failed to add item to cart');
    } catch (e) {
      throw Exception('Error adding to cart: $e');
    }
  }

  /// Update cart item quantity
  static Future<dynamic> updateCartItem(int cartItemId, int quantity) async {
    try {
      final result = await ApiService.request(
        'PUT',
        '$_cartPath/$cartItemId',
        auth: true,
        body: {'quantity': quantity},
      );

      if (result['success'] == true && result['cart_item'] != null) {
        return result['cart_item'];
      }

      // Fallback: return a basic cart item structure
      return {
        'id': cartItemId,
        'quantity': quantity,
      };
    } catch (e) {
      throw Exception('Error updating cart item: $e');
    }
  }

  /// Remove an item from the cart
  static Future<bool> removeFromCart(int cartItemId) async {
    try {
      final result = await ApiService.request(
        'DELETE',
        '$_cartPath/$cartItemId',
        auth: true,
      );
      return result['success'] == true;
    } catch (e) {
      throw Exception('Error removing cart item: $e');
    }
  }

  /// Clear all items from the cart
  static Future<bool> clearCart() async {
    try {
      final result = await ApiService.request(
        'POST',
        '$_cartPath/clear',
        auth: true,
      );
      return result['success'] == true;
    } catch (e) {
      throw Exception('Error clearing cart: $e');
    }
  }

  // ============= Checkout APIs =============

  /// Create order from cart
  static Future<Order> checkout({
    required String recipientName,
    required String recipientPhone,
    required String shippingAddress,
    String? paymentMethod = 'cod',
    String? notes,
    List<int>? selectedItemIds,
    Map<int, int>? productQuantities,
    int? couponId,
    double? shippingFee,
    double? deliveryFee,
  }) async {
    try {
      final body = {
        'recipient_name': recipientName,
        'recipient_phone': recipientPhone,
        'shipping_address': shippingAddress,
        'payment_method': paymentMethod,
        'notes': notes,
        'selected_items': selectedItemIds,
        'coupon_id': couponId,
        'shipping_fee': shippingFee ?? 10.0,
        'delivery_fee': deliveryFee ?? 0.0,
      };

      if (productQuantities != null) {
        // Convert Map<int, int> to Map<String, int> for JSON serialization
        body['product_quantities'] = productQuantities.map(
          (key, value) => MapEntry(key.toString(), value),
        );
      }

      debugPrint('🛒 Checkout: $body');

      final result = await ApiService.requestWithRetry(
        'POST',
        '$baseVersion/buyer/checkout',
        auth: true,
        body: body,
        maxRetries: 1,
      );

      debugPrint('📦 Response: ${result.toString().substring(0, 200)}');

      if (result is! Map<String, dynamic>) {
        throw Exception('Invalid response format');
      }

      if (result.containsKey('products') || result.containsKey('pagination')) {
        throw Exception('Server error - wrong data returned');
      }

      if (result['success'] == true && result['order'] != null) {
        return Order.fromJson(result['order']);
      }

      throw Exception(
          result['error'] ?? result['message'] ?? 'Checkout failed');
    } catch (e) {
      debugPrint('❌ Checkout error: $e');
      rethrow;
    }
  }

  /// Apply coupon code
  static Future<Map<String, dynamic>> applyCoupon(String couponCode) async {
    try {
      final result = await ApiService.request(
        'POST',
        '/api/apply-coupon',
        auth: true,
        body: {'coupon_code': couponCode},
      );

      if (result['success'] == true) {
        return result;
      }
      throw Exception(
          result['error'] ?? result['message'] ?? 'Failed to apply coupon');
    } catch (e) {
      throw Exception('Error applying coupon: $e');
    }
  }

  // ============= Messages APIs =============

  /// Get all conversations for buyer
  static Future<List<Conversation>> getConversations() async {
    try {
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/messages/conversations',
        auth: true,
      );

      if (result['success'] == true && result['conversations'] != null) {
        final conversations = (result['conversations'] as List)
            .map((conv) => Conversation.fromJson(conv))
            .toList();
        return conversations;
      }
      return [];
    } catch (e) {
      throw Exception('Error fetching conversations: $e');
    }
  }

  /// Get messages for a specific conversation
  static Future<List<Message>> getMessages(int peerId,
      {bool isSeller = true}) async {
    try {
      final peerType = isSeller ? 'seller' : 'rider';
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/messages/$peerType/$peerId',
        auth: true,
      );

      if (result['success'] == true && result['messages'] != null) {
        final messages = (result['messages'] as List)
            .map((msg) => Message.fromJson(msg))
            .toList();
        return messages;
      }
      return [];
    } catch (e) {
      throw Exception('Error fetching messages: $e');
    }
  }

  /// Send message to seller or rider
  static Future<Message> sendMessage({
    required int recipientId,
    required String content,
    required bool isSeller,
    String? mediaUrl,
  }) async {
    try {
      final peerType = isSeller ? 'seller' : 'rider';
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/messages/send',
        auth: true,
        body: {
          'recipient_id': recipientId,
          'peer_type': peerType,
          'content': content,
          'media_url': mediaUrl,
        },
      );

      if (result['success'] == true && result['message'] != null) {
        return Message.fromJson(result['message']);
      }
      throw Exception(result['error'] ?? 'Failed to send message');
    } catch (e) {
      throw Exception('Error sending message: $e');
    }
  }

  /// Mark messages as read
  static Future<bool> markMessagesAsRead(int peerId,
      {bool isSeller = true}) async {
    try {
      final peerType = isSeller ? 'seller' : 'rider';
      final result = await ApiService.request(
        'POST',
        '$baseVersion/buyer/messages/$peerType/$peerId/read',
        auth: true,
      );

      return result['success'] == true;
    } catch (e) {
      throw Exception('Error marking messages as read: $e');
    }
  }

  // ============= Profile APIs =============

  /// Update buyer profile
  static Future<dynamic> updateProfile({
    String? firstName,
    String? lastName,
    String? phone,
    String? address,
  }) async {
    try {
      final result = await ApiService.request(
        'PUT',
        '$baseVersion/buyer/profile',
        auth: true,
        body: {
          'first_name': firstName,
          'last_name': lastName,
          'phone': phone,
          'address': address,
        },
      );

      if (result['success'] == true) {
        return result['user'];
      }
      throw Exception(result['error'] ?? 'Failed to update profile');
    } catch (e) {
      throw Exception('Error updating profile: $e');
    }
  }

  /// Update profile picture
  static Future<String> updateProfilePicture(String imagePath) async {
    try {
      return await ApiService.uploadProfilePicture(File(imagePath));
    } catch (e) {
      throw Exception('Error updating profile picture: $e');
    }
  }

  /// Get buyer profile details
  static Future<dynamic> getProfile() async {
    try {
      final result = await ApiService.request(
        'GET',
        '$baseVersion/buyer/profile',
        auth: true,
      );

      if (result['success'] == true && result['user'] != null) {
        return result['user'];
      }
      throw Exception(result['error'] ?? 'Failed to fetch profile');
    } catch (e) {
      throw Exception('Error fetching profile: $e');
    }
  }
}
