import 'package:flutter/foundation.dart';

/// Order model matching Flask backend structure
class Order {
  final int id;
  final int buyerId;
  final int? sellerId;
  final int? riderId;
  final String status;
  final String paymentStatus;
  final String paymentMethod;
  final double subtotal;
  final double shippingFee;
  final double discount;
  final double totalAmount;
  final double? deliveryFee; // Added: pre-calculated delivery fee from backend
  final DateTime orderDate;
  final DateTime? expectedDelivery;
  final DateTime? deliveredAt;
  final String? trackingNumber;
  final List<OrderItem> items;
  final String shippingAddress;
  final String recipientName;
  final String recipientPhone;
  final String? notes;
  final String? sellerName;
  final String? sellerAddress;
  final String? buyerName;
  final String? buyerPhone;
  final String? buyerEmail;
  final String? itemsSummary;
  final String? riderName;
  final String? riderPhone;
  final String? riderProfilePicture;
  final String? proofPhotoUrl;
  final bool? hasRating;
  final int? rating;

  Order({
    required this.id,
    required this.buyerId,
    this.sellerId,
    this.riderId,
    required this.status,
    required this.paymentStatus,
    required this.paymentMethod,
    required this.subtotal,
    required this.shippingFee,
    required this.discount,
    required this.totalAmount,
    this.deliveryFee, // Added: optional delivery fee
    required this.orderDate,
    this.expectedDelivery,
    this.deliveredAt,
    this.trackingNumber,
    required this.items,
    required this.shippingAddress,
    required this.recipientName,
    required this.recipientPhone,
    this.notes,
    this.sellerName,
    this.sellerAddress,
    this.buyerName,
    this.buyerPhone,
    this.buyerEmail,
    this.itemsSummary,
    this.riderName,
    this.riderPhone,
    this.riderProfilePicture,
    this.proofPhotoUrl,
    this.hasRating,
    this.rating,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    // Extract rider information with multiple fallbacks
    final riderData = json['rider'] as Map<String, dynamic>?;
    final riderId = json['rider_id'] ?? riderData?['id'];

    String? riderName;
    if (json['rider_name'] != null &&
        json['rider_name'].toString().trim().isNotEmpty) {
      riderName = json['rider_name'];
    } else if (riderData != null) {
      final firstName = riderData['first_name']?.toString().trim() ?? '';
      final lastName = riderData['last_name']?.toString().trim() ?? '';
      final name = riderData['name']?.toString().trim() ?? '';

      if (firstName.isNotEmpty || lastName.isNotEmpty) {
        riderName = '$firstName $lastName'.trim();
      } else if (name.isNotEmpty) {
        riderName = name;
      }
    }

    String? riderPhone;
    if (json['rider_phone'] != null &&
        json['rider_phone'].toString().trim().isNotEmpty) {
      riderPhone = json['rider_phone'];
    } else if (riderData?['phone'] != null &&
        riderData!['phone'].toString().trim().isNotEmpty) {
      riderPhone = riderData['phone'];
    }

    String? riderProfilePic;
    if (json['rider_profile_picture'] != null) {
      riderProfilePic = json['rider_profile_picture'];
    } else if (riderData?['profile_picture'] != null) {
      riderProfilePic = riderData!['profile_picture'];
    }

    debugPrint(
        '🔍 Order.fromJson - rider_id: $riderId, rider_name: $riderName, rider_phone: $riderPhone, rider_profile_picture: $riderProfilePic');

    return Order(
      id: json['id'] ?? 0,
      buyerId: json['buyer_id'] ?? 0,
      sellerId: json['seller_id'],
      riderId: riderId,
      status: json['status'] ?? 'pending',
      paymentStatus: json['payment_status'] ?? 'pending',
      paymentMethod: json['payment_method'] ?? 'cod',
      subtotal: (json['subtotal'] ?? 0).toDouble(),
      shippingFee: (json['shipping_fee'] ?? 0).toDouble(),
      discount: (json['discount'] ?? 0).toDouble(),
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      deliveryFee: json['delivery_fee'] != null
          ? (json['delivery_fee'] as num).toDouble()
          : null,
      orderDate: json['order_date'] != null
          ? DateTime.parse(json['order_date'])
          : DateTime.now(),
      expectedDelivery: json['expected_delivery'] != null
          ? DateTime.parse(json['expected_delivery'])
          : null,
      deliveredAt: json['delivered_at'] != null
          ? DateTime.parse(json['delivered_at'])
          : null,
      trackingNumber: json['tracking_number'],
      items: (json['items'] as List<dynamic>?)
              ?.map((item) => OrderItem.fromJson(item))
              .toList() ??
          [],
      shippingAddress: json['shipping_address'] ?? '',
      recipientName: json['recipient_name'] ?? '',
      recipientPhone: json['recipient_phone'] ?? '',
      notes: json['notes'],
      sellerName: json['seller_name'] ?? json['seller']?['first_name'],
      sellerAddress: json['seller_address'] ?? json['seller']?['address'],
      buyerName: json['buyer_name'] ??
          json['buyer']?['first_name'] ??
          json['customer']?['first_name'],
      buyerPhone: json['buyer_phone'] ?? json['customer']?['phone'],
      buyerEmail: json['buyer_email'] ?? json['customer']?['email'],
      itemsSummary: json['items_summary'],
      riderName: riderName,
      riderPhone: riderPhone,
      riderProfilePicture: riderProfilePic,
      proofPhotoUrl: json['proof_photo_url'],
      hasRating: json['has_rating'] ?? json['rated'] ?? false,
      rating: json['rating'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'buyer_id': buyerId,
      'seller_id': sellerId,
      'rider_id': riderId,
      'status': status,
      'payment_status': paymentStatus,
      'payment_method': paymentMethod,
      'subtotal': subtotal,
      'shipping_fee': shippingFee,
      'discount': discount,
      'total_amount': totalAmount,
      'order_date': orderDate.toIso8601String(),
      'expected_delivery': expectedDelivery?.toIso8601String(),
      'delivered_at': deliveredAt?.toIso8601String(),
      'tracking_number': trackingNumber,
      'items': items.map((item) => item.toJson()).toList(),
      'shipping_address': shippingAddress,
      'recipient_name': recipientName,
      'recipient_phone': recipientPhone,
      'notes': notes,
      'seller_name': sellerName,
      'seller_address': sellerAddress,
      'buyer_name': buyerName,
      'buyer_phone': buyerPhone,
      'buyer_email': buyerEmail,
      'items_summary': itemsSummary,
      'rider_name': riderName,
      'rider_phone': riderPhone,
      'rider_profile_picture': riderProfilePicture,
      'proof_photo_url': proofPhotoUrl,
      'has_rating': hasRating,
      'rating': rating,
    };
  }

  String get statusDisplay {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'to_pay':
        return 'To Pay';
      case 'to_ship':
        return 'To Ship';
      case 'in_transit':
        return 'In Transit';
      case 'to_receive':
        return 'To Receive';
      case 'delivered':
        return 'Delivered';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'returned':
        return 'Returned';
      default:
        return status;
    }
  }
}

class OrderItem {
  final int id;
  final int productId;
  final String productName;
  final String? productImage;
  final int quantity;
  final double price;
  final double totalPrice;
  final String? size;
  final String? color;

  OrderItem({
    required this.id,
    required this.productId,
    required this.productName,
    this.productImage,
    required this.quantity,
    required this.price,
    required this.totalPrice,
    this.size,
    this.color,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      productName: json['product_name'] ?? '',
      productImage: json['product_image'],
      quantity: json['quantity'] ?? 1,
      price: (json['price'] ?? 0).toDouble(),
      totalPrice: (json['total_price'] ?? 0).toDouble(),
      size: json['size'],
      color: json['color'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'product_name': productName,
      'product_image': productImage,
      'quantity': quantity,
      'price': price,
      'total_price': totalPrice,
      'size': size,
      'color': color,
    };
  }
}

class ReturnRequest {
  final int id;
  final int orderId;
  final String reason;
  final String status;
  final List<String> mediaUrls;
  final String description;
  final DateTime requestDate;
  final DateTime? approvedDate;
  final String? refundAmount;
  final String? adminNotes;

  ReturnRequest({
    required this.id,
    required this.orderId,
    required this.reason,
    required this.status,
    required this.mediaUrls,
    required this.description,
    required this.requestDate,
    this.approvedDate,
    this.refundAmount,
    this.adminNotes,
  });

  factory ReturnRequest.fromJson(Map<String, dynamic> json) {
    return ReturnRequest(
      id: json['id'] ?? 0,
      orderId: json['order_id'] ?? 0,
      reason: json['reason'] ?? '',
      status: json['status'] ?? 'pending',
      mediaUrls: List<String>.from(json['media_urls'] ?? []),
      description: json['description'] ?? '',
      requestDate: json['request_date'] != null
          ? DateTime.parse(json['request_date'])
          : DateTime.now(),
      approvedDate: json['approved_date'] != null
          ? DateTime.parse(json['approved_date'])
          : null,
      refundAmount: json['refund_amount'],
      adminNotes: json['admin_notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'reason': reason,
      'status': status,
      'media_urls': mediaUrls,
      'description': description,
      'request_date': requestDate.toIso8601String(),
      'approved_date': approvedDate?.toIso8601String(),
      'refund_amount': refundAmount,
      'admin_notes': adminNotes,
    };
  }
}

class Message {
  final int id;
  final int senderId;
  final int recipientId;
  final String content;
  final DateTime timestamp;
  final bool isRead;
  final String? mediaUrl;
  final String senderName;
  final String? senderAvatar;

  Message({
    required this.id,
    required this.senderId,
    required this.recipientId,
    required this.content,
    required this.timestamp,
    required this.isRead,
    this.mediaUrl,
    required this.senderName,
    this.senderAvatar,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? 0,
      senderId: json['sender_id'] ?? 0,
      recipientId: json['recipient_id'] ?? 0,
      content: json['content'] ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      isRead: json['is_read'] ?? false,
      mediaUrl: json['media_url'],
      senderName: json['sender_name'] ?? '',
      senderAvatar: json['sender_avatar'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'recipient_id': recipientId,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'is_read': isRead,
      'media_url': mediaUrl,
      'sender_name': senderName,
      'sender_avatar': senderAvatar,
    };
  }
}

class Conversation {
  final int id;
  final int peerId;
  final String peerName;
  final String? peerAvatar;
  final String lastMessage;
  final DateTime lastMessageTime;
  final int unreadCount;
  final bool isPeerSeller;

  Conversation({
    required this.id,
    required this.peerId,
    required this.peerName,
    this.peerAvatar,
    required this.lastMessage,
    required this.lastMessageTime,
    required this.unreadCount,
    required this.isPeerSeller,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] ?? 0,
      peerId: json['peer_id'] ?? 0,
      peerName: json['peer_name'] ?? '',
      peerAvatar: json['peer_avatar'],
      lastMessage: json['last_message'] ?? '',
      lastMessageTime: json['last_message_time'] != null
          ? DateTime.parse(json['last_message_time'])
          : DateTime.now(),
      unreadCount: json['unread_count'] ?? 0,
      isPeerSeller: json['is_peer_seller'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'peer_id': peerId,
      'peer_name': peerName,
      'peer_avatar': peerAvatar,
      'last_message': lastMessage,
      'last_message_time': lastMessageTime.toIso8601String(),
      'unread_count': unreadCount,
      'is_peer_seller': isPeerSeller,
    };
  }
}

class CartItem {
  final int id;
  final int productId;
  final String productName;
  final String? productImage;
  final int quantity;
  final double price;
  final String? size;
  final String? color;
  final int? sellerId;
  final String? sellerName;

  CartItem({
    required this.id,
    required this.productId,
    required this.productName,
    this.productImage,
    required this.quantity,
    required this.price,
    this.size,
    this.color,
    this.sellerId,
    this.sellerName,
  });

  double get totalPrice => price * quantity;

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      productName: json['product_name'] ?? '',
      productImage: json['product_image'],
      quantity: json['quantity'] ?? 1,
      price: (json['price'] ?? 0).toDouble(),
      size: json['size'],
      color: json['color'],
      sellerId: json['seller_id'],
      sellerName: json['seller_name'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'product_name': productName,
      'product_image': productImage,
      'quantity': quantity,
      'price': price,
      'size': size,
      'color': color,
      'seller_id': sellerId,
      'seller_name': sellerName,
    };
  }
}
