/// URL configuration helper for API and asset URLs
class UrlConfig {
  // ========================================
  // 🔧 CONFIGURATION: Change this to switch between local and cloud
  // ========================================
  
  /// Set to true for LOCAL development (hotspot)
  /// Set to false for CLOUD/Production (Render.com)
  static const bool USE_LOCAL = false;  // 👈 CHANGE THIS!
  
  // ========================================
  // URL Definitions
  // ========================================
  
  /// Local development URL (your computer via hotspot)
  static const String _localUrl = 'http://172.20.10.12:5000';
  
  /// Production/Cloud URL (Render.com)
  static const String _renderUrl = 'https://kids-kingdom.onrender.com';

  // ========================================
  // Active Configuration (Auto-selected based on USE_LOCAL)
  // ========================================
  
  static const String _emulatorHost = USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';
  static const String _wifiHost = USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';
  static const String _hotspotHost = USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';
  static const String _localhostHost = USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';
  static const int backendPort = USE_LOCAL ? 5000 : 443;
  static const String backendScheme = USE_LOCAL ? 'http' : 'https';

  static String _preferredHost = USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';

  /// Default host used when no working backend has been discovered yet.
  static String get defaultBackendHost => USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';

  /// Automatically detect which host to use based on network
  static String get backendHost => USE_LOCAL ? '172.20.10.12' : 'kids-kingdom.onrender.com';

  /// Update the preferred backend host after a successful request.
  static void setPreferredBackendHost(String host) {}

  /// ✅ BASE URL: Automatically selected based on USE_LOCAL setting
  static String get baseUrl => USE_LOCAL ? _localUrl : _renderUrl;

  /// ✅ FALLBACK URLS: Automatically selected based on USE_LOCAL setting
  static List<String> get fallbackUrls => [
        USE_LOCAL ? _localUrl : _renderUrl,
      ];

  /// Convert relative image URL to absolute URL
  /// Handles various image path formats and points them to the live Render storage:
  /// - /static/uploads/image.png → https://[your-app].onrender.com/static/uploads/image.png
  /// - image.png → https://[your-app].onrender.com/static/uploads/image.png
  /// - https://... → https://... (returns as-is)
  static String toAbsoluteImageUrl(String? relativeUrl) {
    // Return empty string instead of placeholder.png to avoid 404
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
