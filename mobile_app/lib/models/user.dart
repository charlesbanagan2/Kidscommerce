/// User model matching Flask backend structure
/// Synchronized with database schema for seamless API integration
class User {
  final int id;
  final String firstName;
  final String lastName;
  final String email;
  final String phone;
  final String address;
  final String role; // buyer, seller, admin, rider
  final String status; // active, pending, rejected
  final String? validId;
  final String? profileImage;
  final DateTime createdAt;
  final bool emailVerified;
  final bool twoFactorEnabled;

  User({
    required this.id,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.phone,
    required this.address,
    required this.role,
    required this.status,
    this.validId,
    this.profileImage,
    required this.createdAt,
    this.emailVerified = false,
    this.twoFactorEnabled = false,
  });

  /// Create User from JSON response from Flask backend
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      address: json['address'] ?? '',
      role: json['role'] ?? 'buyer',
      status: json['status'] ?? 'active',
      validId: json['valid_id'],
      profileImage: json['profile_image'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      emailVerified: json['email_verified'] ?? false,
      twoFactorEnabled: json['two_factor_enabled'] ?? false,
    );
  }

  /// Convert User to JSON for API requests
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
      'address': address,
      'role': role,
      'status': status,
      'valid_id': validId,
      'profile_image': profileImage,
      'created_at': createdAt.toIso8601String(),
      'email_verified': emailVerified,
      'two_factor_enabled': twoFactorEnabled,
    };
  }

  /// Get full name
  String get fullName => '$firstName $lastName';

  /// Check if user is admin
  bool get isAdmin => role == 'admin';

  /// Check if user is seller
  bool get isSeller => role == 'seller';

  /// Check if user is buyer
  bool get isBuyer => role == 'buyer';

  /// Check if user is rider
  bool get isRider => role == 'rider';

  /// Check if account is verified
  bool get isVerified => status == 'active';

  /// Get profile image (snake_case alias for profileImage)
  String? get profile_image => profileImage;
}

/// Authentication tokens for JWT-based auth
class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final DateTime issuedAt;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    required this.issuedAt,
  });

  /// Create tokens from Flask backend response
  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      expiresIn: json['expires_in'] ?? 86400,
      issuedAt: DateTime.now(),
    );
  }

  /// Check if access token is expired
  bool get isExpired {
    final expirationTime = issuedAt.add(Duration(seconds: expiresIn));
    return DateTime.now()
        .isAfter(expirationTime.subtract(const Duration(minutes: 5)));
  }

  /// Get remaining time before expiration
  Duration get timeRemaining {
    final expirationTime = issuedAt.add(Duration(seconds: expiresIn));
    return expirationTime.difference(DateTime.now());
  }
}

/// Login request model
class LoginRequest {
  final String email;
  final String password;

  LoginRequest({
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
      };
}

/// Registration request model
/// Used for both Buyer and Rider registration with unified flow
class RegistrationRequest {
  final String firstName;
  final String lastName;
  final String email;
  final String password;
  final String phone;
  final String role; // buyer or rider
  final String address;

  RegistrationRequest({
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.password,
    required this.phone,
    required this.role,
    this.address = '',
  });

  Map<String, dynamic> toJson() => {
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'password': password,
        'phone': phone,
        'address': address,
        'role': role,
      };
}

/// API exception for error handling
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalException;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalException,
  });

  @override
  String toString() => 'ApiException: $message (Code: $statusCode)';
}
