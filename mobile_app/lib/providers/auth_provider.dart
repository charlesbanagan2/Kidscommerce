import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart' hide ApiException;
import '../services/api_service.dart';
import 'dart:convert';

/// AuthProvider manages authentication state across the app
/// Handles login, registration, token management, and role-based access
class AuthProvider with ChangeNotifier {
  User? _user;
  AuthTokens? _tokens;
  bool _isLoading = false;
  String? _errorMessage;
  bool _isAuthenticated = false;
  bool _pendingApproval = false;
  String? _pendingApprovalMessage;
  bool _requiresAddressSetup = false;

  // Getters
  User? get user => _user;
  AuthTokens? get tokens => _tokens;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _isAuthenticated;
  bool get pendingApproval => _pendingApproval;
  String? get pendingApprovalMessage => _pendingApprovalMessage;
  bool get requiresAddressSetup => _requiresAddressSetup;

  // Role checks
  bool get isBuyer => _user?.role == 'buyer';
  bool get isSeller => _user?.role == 'seller';
  bool get isAdmin => _user?.role == 'admin';
  bool get isRider => _user?.role == 'rider';

  // SharedPreferences keys
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userKey = 'user_data';

  /// Initialize provider by checking stored tokens
  Future<void> initialize() async {
    try {
      await _loadStoredData();
      if (_tokens != null) {
        _isAuthenticated = true;
        ApiService.setTokens(_tokens!.accessToken, _tokens!.refreshToken);

        // Refresh user data from backend to ensure latest profile image and info
        try {
          await refreshUser();
        } catch (e) {
          debugPrint('Failed to refresh user on init: $e');
          // Continue with stored data if refresh fails
        }
      }
    } catch (e) {
      debugPrint('Auth initialization error: $e');
      await _clearStoredData();
    } finally {
      notifyListeners();
    }
  }

  /// Load stored data from SharedPreferences
  Future<void> _loadStoredData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accessToken = prefs.getString(_accessTokenKey);
      final refreshToken = prefs.getString(_refreshTokenKey);
      final userJson = prefs.getString(_userKey);

      if (accessToken != null && refreshToken != null) {
        _tokens = AuthTokens(
          accessToken: accessToken,
          refreshToken: refreshToken,
          expiresIn: prefs.getInt('token_expires_in') ?? 86400,
          issuedAt: DateTime.parse(prefs.getString('token_issued_at') ??
              DateTime.now().toIso8601String()),
        );

        if (userJson != null) {
          final userMap = jsonDecode(userJson) as Map<String, dynamic>;
          _user = User.fromJson(userMap);
          _isAuthenticated = true;
        }
      }
    } catch (e) {
      debugPrint('Error loading stored data: $e');
    }
  }

  /// Login user with email and password
  Future<bool> login(String email, String password) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await ApiService.login(email, password);
      debugPrint('=== LOGIN RESPONSE ===');
      debugPrint('Full result: $result');

      // Get tokens from response (handles both nested and flat formats)
      final tokensData = result['tokens'] as Map<String, dynamic>?;
      debugPrint('Tokens data: $tokensData');

      if (tokensData != null) {
        // New format: tokens are nested in 'tokens' object
        if (tokensData['access_token'] != null &&
            tokensData['refresh_token'] != null) {
          _tokens = AuthTokens(
            accessToken: tokensData['access_token'],
            refreshToken: tokensData['refresh_token'],
            expiresIn: tokensData['expires_in'] ?? 86400,
            issuedAt: DateTime.now(),
          );
          debugPrint('✅ Tokens created from nested format (login)');
        }
      } else if (result['access_token'] != null &&
          result['refresh_token'] != null) {
        // Old format: tokens at top level
        _tokens = AuthTokens(
          accessToken: result['access_token'],
          refreshToken: result['refresh_token'],
          expiresIn: result['expires_in'] ?? 86400,
          issuedAt: DateTime.now(),
        );
        debugPrint('✅ Tokens created from flat format (login)');
      } else {
        debugPrint('âš ï¸ WARNING: No tokens found in response!');
      }

      // Extract user data directly from login response
      // Backend returns user object in the 'user' key
      final userData = result['user'] ?? result;
      debugPrint('User data: $userData');

      if (userData is Map<String, dynamic>) {
        _user = User.fromJson(userData);
        debugPrint(
            'âœ… User created: ${_user?.fullName}, Role: ${_user?.role}, Authenticated: $_isAuthenticated');
      }

      _isAuthenticated = true;
      _pendingApproval = false;
      _pendingApprovalMessage = null;

      // CRITICAL: Save to preferences BEFORE setting tokens in ApiService
      // This ensures tokens are persisted before any API calls are made
      await _saveData();
      
      // Now set tokens in ApiService after they're saved
      if (_tokens != null) {
        ApiService.setTokens(_tokens!.accessToken, _tokens!.refreshToken);
        debugPrint('✅ Tokens set in ApiService after saving to storage (login)');
      }

      await _checkAddressSetup();
      
      // Clear loading state before notifying
      _isLoading = false;
      
      notifyListeners();
      debugPrint('=== LOGIN COMPLETE ===');
      return true;
    } on ApiException catch (e) {
      debugPrint('âŒ API Exception: ${e.message}');
      if (_isPendingApprovalError(e)) {
        _setPendingApproval(e.message);
        return false;
      }
      _setErrorMessage(e.message);
      return false;
    } catch (e) {
      debugPrint('âŒ Exception: $e');
      _setErrorMessage('Login failed: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Login with Google credentials
  Future<bool> loginWithGoogle(String accessToken, String idToken) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await ApiService.loginWithGoogle(accessToken, idToken);
      debugPrint('=== GOOGLE LOGIN RESPONSE ===');
      debugPrint('Full result: $result');

      // Get tokens from response (handles both nested and flat formats)
      final tokensData = result['tokens'] as Map<String, dynamic>?;
      debugPrint('Tokens data: $tokensData');

      if (tokensData != null) {
        // New format: tokens are nested in 'tokens' object
        if (tokensData['access_token'] != null &&
            tokensData['refresh_token'] != null) {
          _tokens = AuthTokens(
            accessToken: tokensData['access_token'],
            refreshToken: tokensData['refresh_token'],
            expiresIn: tokensData['expires_in'] ?? 86400,
            issuedAt: DateTime.now(),
          );
          debugPrint('✅ Tokens set from nested format (Google)');
        }
      } else if (result['access_token'] != null &&
          result['refresh_token'] != null) {
        // Old format: tokens at top level
        _tokens = AuthTokens(
          accessToken: result['access_token'],
          refreshToken: result['refresh_token'],
          expiresIn: result['expires_in'] ?? 86400,
          issuedAt: DateTime.now(),
        );
        debugPrint('✅ Tokens set from flat format (Google)');
      }

      // Extract user data directly from login response
      final userData = result['user'] ?? result;
      debugPrint('User data: $userData');

      if (userData is Map<String, dynamic>) {
        _user = User.fromJson(userData);
      }

      _isAuthenticated = true;
      _pendingApproval = false;
      _pendingApprovalMessage = null;
      
      debugPrint(
          '✅ User created: ${_user?.fullName}, Role: ${_user?.role}, Authenticated: $_isAuthenticated');

      // CRITICAL: Save to preferences BEFORE setting tokens in ApiService
      // This ensures tokens are persisted before any API calls are made
      await _saveData();
      
      // Now set tokens in ApiService after they're saved
      if (_tokens != null) {
        ApiService.setTokens(_tokens!.accessToken, _tokens!.refreshToken);
        debugPrint('✅ Tokens set in ApiService after saving to storage');
      }

      await _checkAddressSetup();
      notifyListeners();
      debugPrint('=== GOOGLE LOGIN COMPLETE ===');
      return true;
    } on ApiException catch (e) {
      debugPrint('❌ Google Login API Exception: ${e.message}');
      if (_isPendingApprovalError(e)) {
        _setPendingApproval(e.message);
        return false;
      }
      _setErrorMessage(e.message);
      return false;
    } catch (e) {
      debugPrint('❌ Google Login Exception: $e');
      _setErrorMessage('Google sign-in failed: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Register new user
  Future<bool> register(Map<String, dynamic> request) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await ApiService.register(request);

      // After registration, the user is pending approval.
      // We don't log them in automatically.
      // The API returns a success message.
      if (result['message'] != null) {
        // Optionally, you can store the email to pre-fill the login form
        // final prefs = await SharedPreferences.getInstance();
        // await prefs.setString('last_registered_email', request.email);

        _setErrorMessage(result['message'] ??
            'Registration successful. Please wait for admin approval.');
        notifyListeners();
        return true; // Indicates the registration API call was successful
      }

      // Fallback for unexpected responses
      _setErrorMessage(
          result['error'] ?? 'An unknown registration error occurred.');
      return false;
    } on ApiException catch (e) {
      debugPrint('Registration API Exception: ${e.message}');
      _setErrorMessage(e.message);
      return false;
    } catch (e) {
      debugPrint('Registration Exception: $e');
      _setErrorMessage('An unexpected error occurred during registration.');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Logout user
  Future<void> logout() async {
    _setLoading(true);

    try {
      await ApiService.logout();
    } catch (e) {
      debugPrint('Logout error: $e');
    }

    // Clear all data
    await _clearStoredData();
    _clearAllData();
    _setLoading(false);
    notifyListeners();
  }

  /// Refresh user profile from API (includes latest profile photo).
  Future<void> refreshUser() async {
    if (!_isAuthenticated) return;
    try {
      _user = await ApiService.getUserProfile();
      await _saveData();
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to refresh user profile: $e');
    }
  }

  /// Update user profile
  Future<bool> updateProfile(Map<String, dynamic> updates) async {
    _setLoading(true);
    _clearError();

    try {
      _user = await ApiService.updateUserProfile(updates);
      await _saveData();
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _setErrorMessage(e.message);
      return false;
    } catch (e) {
      _setErrorMessage('Profile update failed: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Save data to SharedPreferences
  Future<void> _saveData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      if (_tokens != null) {
        await prefs.setString(_accessTokenKey, _tokens!.accessToken);
        await prefs.setString(_refreshTokenKey, _tokens!.refreshToken);
        await prefs.setInt('token_expires_in', _tokens!.expiresIn);
        await prefs.setString(
            'token_issued_at', _tokens!.issuedAt.toIso8601String());
      }

      if (_user != null) {
        await prefs.setString(_userKey, jsonEncode(_user!.toJson()));
      }
    } catch (e) {
      debugPrint('Error saving data: $e');
    }
  }

  /// Clear all stored data
  Future<void> _clearStoredData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
      await prefs.remove(_userKey);
      await prefs.remove('token_expires_in');
      await prefs.remove('token_issued_at');
    } catch (e) {
      debugPrint('Error clearing stored data: $e');
    }
  }

  /// Clear all auth data
  void _clearAllData() {
    _user = null;
    _tokens = null;
    _isAuthenticated = false;
    _pendingApproval = false;
    _pendingApprovalMessage = null;
    _requiresAddressSetup = false;
    ApiService.clearTokens();
    _clearError();
  }

  /// Set loading state
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// Set error message
  void _setErrorMessage(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  /// Clear error message
  void _clearError() {
    _errorMessage = null;
    _pendingApproval = false;
    _pendingApprovalMessage = null;
  }

  bool _isPendingApprovalError(ApiException e) {
    final message = e.message.toLowerCase();
    return e.statusCode == 403 &&
        (message.contains('pending') || message.contains('approval'));
  }

  void _setPendingApproval(String message) {
    _pendingApproval = true;
    _pendingApprovalMessage = message;
    _user = null;
    _tokens = null;
    _isAuthenticated = false;
    _requiresAddressSetup = false;
    ApiService.clearTokens();
    notifyListeners();
  }

  Future<void> _checkAddressSetup() async {
    _requiresAddressSetup = false;
    if (_user?.role != 'buyer') return;
    try {
      final result = await ApiService.request('GET', '/api/v1/buyer/addresses');
      if (result is Map<String, dynamic>) {
        final addresses = result['addresses'];
        if (addresses is List && addresses.isEmpty) {
          _requiresAddressSetup = true;
        }
      }
    } catch (e) {
      debugPrint('Failed to check address setup: $e');
    }
  }

  /// Get access token
  String? get accessToken => _tokens?.accessToken;

  /// Get user display name
  String get displayName => _user?.fullName ?? 'Guest';

  /// Debug method
  void debugPrintState() {
    debugPrint('AuthProvider State:');
    debugPrint('  Is Authenticated: $isAuthenticated');
    debugPrint('  User: ${_user?.fullName}');
    debugPrint('  Role: ${_user?.role}');
    debugPrint('  Is Loading: $_isLoading');
    debugPrint('  Error: $_errorMessage');
  }
}
