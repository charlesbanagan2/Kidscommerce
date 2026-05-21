/// URL configuration helper for API and asset URLs
class UrlConfig {
  // Backend server configuration
  // Multiple IP addresses for different network scenarios:
  static const String _emulatorHost =
      '10.0.2.2'; // Android emulator host machine
  static const String _wifiHost = '192.168.1.26'; // WiFi network
  static const String _hotspotHost = '172.20.10.12'; // Mobile Hotspot
  static const String _localhostHost = 'localhost'; // Emulator/Web
  static const int backendPort = 5000;
  static const String backendScheme = 'http';

  static String _preferredHost = _wifiHost;

  /// Default host used when no working backend has been discovered yet.
  static String get defaultBackendHost => _wifiHost;

  /// Automatically detect which host to use based on network
  static String get backendHost {
    return _preferredHost;
  }

  /// Update the preferred backend host after a successful request.
  static void setPreferredBackendHost(String host) {
    final normalizedHost = host.trim();
    if (normalizedHost.isNotEmpty) {
      _preferredHost = normalizedHost;
    }
  }

  /// Get base backend URL
  static String get baseUrl => '$backendScheme://$backendHost:$backendPort';

  /// Get alternative URLs to try if primary fails
  static List<String> get fallbackUrls => [
        '$backendScheme://$_wifiHost:$backendPort', // Try WiFi first
        '$backendScheme://$_hotspotHost:$backendPort', // Then hotspot
        '$backendScheme://$_emulatorHost:$backendPort', // Android emulator host machine
        '$backendScheme://$_localhostHost:$backendPort', // Then localhost
      ];

  /// Convert relative image URL to absolute URL
  /// Handles various image path formats:
  /// - /static/uploads/image.png → http://192.168.1.20:5000/static/uploads/image.png
  /// - image.png → http://192.168.1.20:5000/static/uploads/image.png
  /// - http://... → http://... (returns as-is)
  static String toAbsoluteImageUrl(String? relativeUrl) {
    // ✅ FIX: Return empty string instead of placeholder.png to avoid 404
    if (relativeUrl == null ||
        relativeUrl.isEmpty ||
        relativeUrl == 'placeholder.png') {
      return '';
    }

    // Already absolute URL
    if (relativeUrl.startsWith('http://') ||
        relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }

    // Already has /static/ prefix
    if (relativeUrl.startsWith('/static/')) {
      return '$baseUrl$relativeUrl';
    }

    // Relative path - assume it's in uploads
    if (relativeUrl.startsWith('/')) {
      return '$baseUrl$relativeUrl';
    }

    // Plain filename
    return '$baseUrl/static/uploads/$relativeUrl';
  }

  /// Convert multiple relative URLs to absolute
  static List<String> toAbsoluteImageUrls(List<dynamic>? urls) {
    if (urls == null || urls.isEmpty) {
      return [];
    }

    return urls.map((url) => toAbsoluteImageUrl(url as String?)).toList();
  }
}
