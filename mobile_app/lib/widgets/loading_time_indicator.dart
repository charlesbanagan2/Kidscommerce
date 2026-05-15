import 'package:flutter/material.dart';
import '../utils/performance_monitor.dart';

/// Widget that displays loading time on screen
class LoadingTimeIndicator extends StatelessWidget {
  final String operation;
  final bool show;

  const LoadingTimeIndicator({
    super.key,
    required this.operation,
    this.show = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!show) return const SizedBox.shrink();

    final duration = PerformanceMonitor.getDuration(operation);
    if (duration == null) return const SizedBox.shrink();

    final seconds = duration.inMilliseconds / 1000;
    final emoji = _getEmoji(duration);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getColor(duration).withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            emoji,
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(width: 6),
          Text(
            '${seconds.toStringAsFixed(2)}s',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  String _getEmoji(Duration duration) {
    final ms = duration.inMilliseconds;
    if (ms < 500) return '⚡';
    if (ms < 1000) return '✅';
    if (ms < 2000) return '🟡';
    if (ms < 5000) return '🟠';
    return '🔴';
  }

  Color _getColor(Duration duration) {
    final ms = duration.inMilliseconds;
    if (ms < 500) return Colors.green;
    if (ms < 1000) return Colors.lightGreen;
    if (ms < 2000) return Colors.orange;
    if (ms < 5000) return Colors.deepOrange;
    return Colors.red;
  }
}

/// Snackbar that shows loading time
class LoadingTimeSnackbar {
  static void show(BuildContext context, String operation) {
    final duration = PerformanceMonitor.getDuration(operation);
    if (duration == null) return;

    final seconds = duration.inMilliseconds / 1000;
    final emoji = _getEmoji(duration);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 16)),
            const SizedBox(width: 8),
            Text('$operation: ${seconds.toStringAsFixed(2)}s'),
          ],
        ),
        backgroundColor: _getColor(duration),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }

  static String _getEmoji(Duration duration) {
    final ms = duration.inMilliseconds;
    if (ms < 500) return '⚡';
    if (ms < 1000) return '✅';
    if (ms < 2000) return '🟡';
    if (ms < 5000) return '🟠';
    return '🔴';
  }

  static Color _getColor(Duration duration) {
    final ms = duration.inMilliseconds;
    if (ms < 500) return Colors.green;
    if (ms < 1000) return Colors.lightGreen;
    if (ms < 2000) return Colors.orange;
    if (ms < 5000) return Colors.deepOrange;
    return Colors.red;
  }
}
