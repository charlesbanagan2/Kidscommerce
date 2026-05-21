/// Google OAuth Configuration
class GoogleOAuthConfig {
  // Android Client ID
  static const String androidClientId = '19725108081-d03cnmvghsfr3tpevj05pnn2upr55vds.apps.googleusercontent.com';
  
  // Web Client ID (also used for iOS)
  static const String webClientId = '19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com';
  
  // Get client ID based on platform
  static String getClientId() {
    // For Flutter, google_sign_in package handles platform detection
    // We just need to provide the web client ID in the plugin initialization
    return webClientId;
  }
}
