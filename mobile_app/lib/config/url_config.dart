/// URL configuration helper for API and asset URLs
class UrlConfig {
  // Backend server configuration
  // Use localhost for web/browser access, 172.20.10.12 for mobile devices
  static const String backendHost = '172.20.10.12';
  static const int backendPort = 5000;
  static const String backendScheme = 'http';

  /// Get base backend URL
  static String get baseUrl => '$backendScheme://$backendHost:$backendPort';

  /// Convert relative image URL to absolute URL
  /// Handles various image path formats:
  /// - /static/uploads/image.png → http://192.168.1.20:5000/static/uploads/image.png
  /// - image.png → http://192.168.1.20:5000/static/uploads/image.png
  /// - http://... → http://... (returns as-is)
  static String toAbsoluteImageUrl(String? relativeUrl) {
    if (relativeUrl == null || relativeUrl.isEmpty) {
      return '$baseUrl/static/uploads/placeholder.png';
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
