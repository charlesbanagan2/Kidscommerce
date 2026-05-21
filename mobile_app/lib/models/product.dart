/// Product model matching Flask backend structure
class Product {
  final int id;
  final String name;
  final String? description;
  final double price;
  final double? salePrice;
  final String? imageUrl;
  final List<String>? images;
  final List<String>? videos;
  final String category;
  final String? subcategory;
  final int stock;
  final double rating;
  final int reviewCount;
  final List<Map<String, dynamic>>? reviews;
  final bool isActive;
  final int sellerId;
  final String? sellerName;
  final String? storeName;
  final String? storeLogo;
  final DateTime? createdAt;

  Product({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    this.salePrice,
    this.imageUrl,
    this.images,
    this.videos,
    required this.category,
    this.subcategory,
    required this.stock,
    this.rating = 0.0,
    this.reviewCount = 0,
    this.reviews,
    this.isActive = true,
    required this.sellerId,
    this.sellerName,
    this.storeName,
    this.storeLogo,
    this.createdAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    // Handle nested seller object
    String? extractedSellerName;
    String? extractedStoreName;
    String? extractedStoreLogo;

    if (json['seller'] is Map) {
      final seller = json['seller'] as Map<String, dynamic>;
      extractedSellerName = seller['name'] as String?;
      extractedStoreName = seller['store_name'] as String?;
      extractedStoreLogo = seller['store_logo'] as String?;
    } else {
      // Fallback to flat structure
      extractedSellerName = json['seller_name'] as String?;
      extractedStoreName = json['store_name'] as String?;
      extractedStoreLogo = json['store_logo'] as String?;
    }

    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      description: json['description'],
      price: (json['price'] ?? 0.0).toDouble(),
      salePrice: json['sale_price']?.toDouble(),
      imageUrl: json['image'] ?? json['image_url'],
      images: json['gallery'] != null
          ? List<String>.from((json['gallery'] as List).map((img) {
              // Handle gallery items which might be strings or objects
              if (img is String) return img;
              if (img is Map && img['url'] != null) return img['url'] as String;
              return '';
            }).where((img) => img.isNotEmpty))
          : json['images'] != null
              ? List<String>.from(json['images'])
              : null,
      videos: json['videos'] != null
          ? List<String>.from(json['videos'])
          : null,
      category: json['category'] ?? '',
      subcategory: json['subcategory'],
      stock: json['stock'] ?? 0,
      rating: (json['rating'] ?? 0.0).toDouble(),
      reviewCount: json['review_count'] ?? 0,
      reviews: json['reviews'] != null
          ? List<Map<String, dynamic>>.from(
              (json['reviews'] as List).map((r) => r as Map<String, dynamic>))
          : null,
      isActive: json['is_active'] ?? true,
      sellerId: json['seller_id'] ?? 0,
      sellerName: extractedSellerName,
      storeName: extractedStoreName,
      storeLogo: extractedStoreLogo,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'sale_price': salePrice,
      'image_url': imageUrl,
      'images': images,
      'videos': videos,
      'category': category,
      'subcategory': subcategory,
      'stock': stock,
      'rating': rating,
      'review_count': reviewCount,
      'reviews': reviews,
      'is_active': isActive,
      'seller_id': sellerId,
      'seller_name': sellerName,
      'store_name': storeName,
      'store_logo': storeLogo,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  /// Get display price (sale price if available, otherwise regular price)
  double get displayPrice => salePrice ?? price;

  /// Check if product is on sale
  bool get isOnSale => salePrice != null && salePrice! < price;

  /// Calculate discount percentage
  int? get discountPercent {
    if (!isOnSale) return null;
    return ((price - salePrice!) / price * 100).round();
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is Product &&
        other.id == id &&
        other.name == name &&
        other.price == price &&
        other.salePrice == salePrice &&
        other.stock == stock &&
        other.rating == rating &&
        other.reviewCount == reviewCount &&
        other.storeName == storeName &&
        other.imageUrl == imageUrl;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        name.hashCode ^
        price.hashCode ^
        (salePrice?.hashCode ?? 0) ^
        stock.hashCode ^
        rating.hashCode ^
        reviewCount.hashCode ^
        (storeName?.hashCode ?? 0) ^
        (imageUrl?.hashCode ?? 0);
  }
}
