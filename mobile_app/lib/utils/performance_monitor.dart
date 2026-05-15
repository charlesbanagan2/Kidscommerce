import 'package:flutter/foundation.dart';

/// Performance monitor to track loading times
class PerformanceMonitor {
  static final Map<String, DateTime> _startTimes = {};
  static final Map<String, Duration> _durations = {};
  static bool enabled = true;

  /// Start timing an operation
  static void start(String operation) {
    if (!enabled) return;
    _startTimes[operation] = DateTime.now();
    debugPrint('⏱️ START: $operation');
  }

  /// End timing an operation and log the duration
  static Duration? end(String operation) {
    if (!enabled) return null;
    
    final startTime = _startTimes[operation];
    if (startTime == null) {
      debugPrint('⚠️ No start time found for: $operation');
      return null;
    }

    final duration = DateTime.now().difference(startTime);
    _durations[operation] = duration;
    _startTimes.remove(operation);

    final seconds = duration.inMilliseconds / 1000;
    final emoji = _getEmoji(duration);
    
    debugPrint('⏱️ END: $operation - ${seconds.toStringAsFixed(2)}s $emoji');
    
    return duration;
  }

  /// Get emoji based on duration
  static String _getEmoji(Duration duration) {
    final ms = duration.inMilliseconds;
    if (ms < 500) return '⚡'; // Very fast
    if (ms < 1000) return '✅'; // Fast
    if (ms < 2000) return '🟡'; // Moderate
    if (ms < 5000) return '🟠'; // Slow
    return '🔴'; // Very slow
  }

  /// Get the duration of a completed operation
  static Duration? getDuration(String operation) {
    return _durations[operation];
  }

  /// Get formatted duration string
  static String getFormattedDuration(String operation) {
    final duration = _durations[operation];
    if (duration == null) return 'N/A';
    
    final seconds = duration.inMilliseconds / 1000;
    return '${seconds.toStringAsFixed(2)}s';
  }

  /// Clear all recorded durations
  static void clear() {
    _startTimes.clear();
    _durations.clear();
  }

  /// Get all durations
  static Map<String, Duration> getAllDurations() {
    return Map.from(_durations);
  }

  /// Print summary of all operations
  static void printSummary() {
    if (_durations.isEmpty) {
      debugPrint('📊 No operations recorded');
      return;
    }

    debugPrint('📊 Performance Summary:');
    debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    final sorted = _durations.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    for (var entry in sorted) {
      final seconds = entry.value.inMilliseconds / 1000;
      final emoji = _getEmoji(entry.value);
      debugPrint('  ${entry.key}: ${seconds.toStringAsFixed(2)}s $emoji');
    }
    
    debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  }

  /// Measure a future operation
  static Future<T> measure<T>(
    String operation,
    Future<T> Function() function,
  ) async {
    start(operation);
    try {
      final result = await function();
      end(operation);
      return result;
    } catch (e) {
      end(operation);
      rethrow;
    }
  }
}
