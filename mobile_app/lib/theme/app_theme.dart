import 'package:flutter/material.dart';

/// Kids Commerce Flutter Theme
/// Synchronized with backend web design colors and typography
///
/// Color Palette (extracted from CSS):
/// - Primary: #60a5fa (Sky Blue)
/// - Secondary: #f472b6 (Bubblegum Pink)
/// - Warning: #facc15 (Sunshine Yellow)
/// - Danger: #fb7185 (Coral Red)
/// - Dark: #334155 (Slate)
/// - Light: #f8fafc (Very Light)
class AppTheme {
  // Color Constants
  static const Color primaryColor = Color(0xFF60a5fa); // Sky Blue
  static const Color secondaryColor = Color(0xFFf472b6); // Bubblegum Pink
  static const Color warningColor = Color(0xFFfacc15); // Sunshine Yellow
  static const Color dangerColor = Color(0xFFfb7185); // Coral Red
  static const Color darkColor = Color(0xFF334155); // Slate
  static const Color lightColor = Color(0xFFf8fafc); // Very Light

  // Semantic Colors
  static const Color successColor = Color(0xFF10b981); // Emerald
  static const Color errorColor = dangerColor;
  static const Color backgroundColor = Color(0xFFfafafa); // Off-white
  static const Color surfaceColor = Colors.white;
  static const Color borderColor = Color(0xFFe5e7eb); // Light Gray

  // Text Colors
  static const Color textPrimaryColor = Color(0xFF111827); // Near-black
  static const Color textSecondaryColor = Color(0xFF6b7280); // Gray
  static const Color textLightColor = Color(0xFF9ca3af); // Light Gray

  // Light Theme
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,

      // Color Scheme
      colorScheme: const ColorScheme.light(
        primary: primaryColor,
        secondary: secondaryColor,
        error: errorColor,
        surface: surfaceColor,
      ),

      // Scaffold Background
      scaffoldBackgroundColor: backgroundColor,

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        elevation: 2,
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        titleTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(color: Colors.white),
      ),

      // Text Theme
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.w800,
          color: textPrimaryColor,
        ),
        displayMedium: TextStyle(
          fontSize: 28,
          fontWeight: FontWeight.w700,
          color: textPrimaryColor,
        ),
        headlineSmall: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: textPrimaryColor,
        ),
        titleLarge: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: textPrimaryColor,
        ),
        titleMedium: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          color: textPrimaryColor,
        ),
        bodyLarge: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: textPrimaryColor,
        ),
        bodyMedium: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: textSecondaryColor,
        ),
        labelSmall: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: textSecondaryColor,
        ),
      ),

      // Button Themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          side: const BorderSide(color: primaryColor, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        ),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        color: surfaceColor,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: borderColor, width: 1),
        ),
      ),

      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: lightColor,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: borderColor),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: borderColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primaryColor, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorColor),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorColor, width: 2),
        ),
        labelStyle: const TextStyle(color: textSecondaryColor),
        hintStyle: const TextStyle(color: textLightColor),
      ),

      // Chip Theme
      chipTheme: const ChipThemeData(
        backgroundColor: lightColor,
        selectedColor: primaryColor,
        labelStyle: TextStyle(color: textPrimaryColor),
        side: BorderSide(color: borderColor),
      ),

      // Divider Theme
      dividerTheme: const DividerThemeData(
        color: borderColor,
        thickness: 1,
      ),

      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surfaceColor,
        elevation: 8,
        selectedItemColor: primaryColor,
        unselectedItemColor: textSecondaryColor,
      ),

      // Progress Indicator Theme
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: primaryColor,
      ),
    );
  }

  /// Gradient from primary to secondary color
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryColor, secondaryColor],
  );

  /// Radial gradient for card backgrounds
  static const RadialGradient cardGradient = RadialGradient(
    center: Alignment(-0.8, -0.8),
    radius: 1.5,
    colors: [Color(0xFFF0F7FF), Color(0xFFFFFFFF)],
    stops: [0.0, 0.6],
  );
}
