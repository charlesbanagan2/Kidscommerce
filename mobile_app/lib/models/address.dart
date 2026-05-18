/// Address model for buyer addresses
class Address {
  final int? id;
  final int userId;
  final String label;
  final String fullAddress;
  final String? street;
  final String? city;
  final String? province;
  final String? barangay;
  final String? region;
  final String? zipCode;
  final bool isDefault;
  final double? latitude;
  final double? longitude;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Address({
    this.id,
    required this.userId,
    required this.label,
    required this.fullAddress,
    this.street,
    this.city,
    this.province,
    this.barangay,
    this.region,
    this.zipCode,
    this.isDefault = false,
    this.latitude,
    this.longitude,
    DateTime? createdAt,
    this.updatedAt,
  }) : createdAt = createdAt ?? DateTime.now();

  /// Convert to JSON for API requests
  Map<String, dynamic> toJson() {
    return {
      'label': label,
      'full_address': fullAddress,
      'street_address': street,
      'city': city,
      'province': province,
      'barangay': barangay,
      'region': region,
      'zip_code': zipCode,
      'is_default': isDefault,
      'latitude': latitude,
      'longitude': longitude,
    };
  }

  /// Create from JSON response
  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] as int?,
      userId: json['user_id'] as int? ?? 0,
      label: json['label'] as String? ?? 'Home',
      fullAddress: json['full_address'] as String? ?? '',
      street: json['street_address'] as String?,
      city: json['city'] as String?,
      province: json['province'] as String?,
      barangay: json['barangay'] as String?,
      region: json['region'] as String?,
      zipCode: json['zip_code'] as String?,
      isDefault: json['is_default'] as bool? ?? false,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  /// Copy with updated fields
  Address copyWith({
    int? id,
    int? userId,
    String? label,
    String? fullAddress,
    String? street,
    String? city,
    String? province,
    String? barangay,
    String? region,
    String? zipCode,
    bool? isDefault,
    double? latitude,
    double? longitude,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Address(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      label: label ?? this.label,
      fullAddress: fullAddress ?? this.fullAddress,
      street: street ?? this.street,
      city: city ?? this.city,
      province: province ?? this.province,
      barangay: barangay ?? this.barangay,
      region: region ?? this.region,
      zipCode: zipCode ?? this.zipCode,
      isDefault: isDefault ?? this.isDefault,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Address(id: $id, label: $label, address: $fullAddress, isDefault: $isDefault)';
  }
}
