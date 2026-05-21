/// URL configuration helper for API and asset URLs
class UrlConfig {
  // ✅ I-UPDATE MO ITO: Palitan ng totoong Render URL ng app mo (Wala dapat "/" sa dulo)
  static const String _renderUrl = 'https://kidscommerce-backend.onrender.com';

  // Mga lumang variables na iniwan nating blangko o fixed para hindi mag-error ang ibang code mo
  static const String _emulatorHost = 'onrender.com';
  static const String _wifiHost = 'onrender.com';
  static const String _hotspotHost = 'onrender.com';
  static const String _localhostHost = 'onrender.com';
  static const int backendPort = 443; // Standard port para sa HTTPS
  static const String backendScheme = 'https';

  static String _preferredHost = 'onrender.com';

  /// Default host used when no working backend has been discovered yet.
  static String get defaultBackendHost => 'onrender.com';

  /// Automatically detect which host to use based on network
  static String get backendHost => 'onrender.com';

  /// Update the preferred backend host after a successful request.
  static void setPreferredBackendHost(String host) {}

  /// ✅ BASE URL: Direkta nang kumokonekta sa iyong Live Render Server gamit ang HTTPS
  static String get baseUrl => _renderUrl;

  /// ✅ FALLBACK URLS: Dahil iisa na lang ang server natin sa internet, Render URL na rin ang fallback
  static List<String> get fallbackUrls => [
        _renderUrl,
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
