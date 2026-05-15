import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';

class ModernSnackBar {
  static void show(
    BuildContext context, {
    required String message,
    bool isSuccess = true,
    Duration duration = const Duration(seconds: 3),
    VoidCallback? onActionPressed,
    String? actionLabel,
    bool showAtTop = false,
  }) {
    final snackBar = SnackBar(
      content: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              isSuccess ? LucideIcons.checkCircle2 : LucideIcons.alertCircle,
              color: Colors.white,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
      backgroundColor: isSuccess
          ? const Color(0xFF10B981)
          : const Color(0xFFEF4444),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      margin: showAtTop
          ? const EdgeInsets.only(top: 60, left: 16, right: 16)
          : const EdgeInsets.all(16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      duration: duration,
      dismissDirection: showAtTop ? DismissDirection.up : DismissDirection.down,
      action: actionLabel != null
          ? SnackBarAction(
              label: actionLabel,
              textColor: Colors.white,
              onPressed: onActionPressed ?? () {},
            )
          : null,
    );

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(snackBar);
  }

  static void showSuccess(
    BuildContext context,
    String message, {
    VoidCallback? onActionPressed,
    String? actionLabel,
  }) {
    show(
      context,
      message: message,
      isSuccess: true,
      onActionPressed: onActionPressed,
      actionLabel: actionLabel,
    );
  }

  static void showError(
    BuildContext context,
    String message,
  ) {
    show(
      context,
      message: message,
      isSuccess: false,
    );
  }

  static void showCartSuccess(
    BuildContext context,
    String productName, {
    VoidCallback? onViewCart,
  }) {
    final overlay = Overlay.of(context);
    final overlayEntry = OverlayEntry(
      builder: (context) => _CartSuccessOverlay(
        productName: productName,
        onViewCart: onViewCart,
      ),
    );
    overlay.insert(overlayEntry);
    Future.delayed(const Duration(seconds: 3), () {
      overlayEntry.remove();
    });
  }
}

class _CartSuccessOverlay extends StatefulWidget {
  final String productName;
  final VoidCallback? onViewCart;

  const _CartSuccessOverlay({
    required this.productName,
    this.onViewCart,
  });

  @override
  State<_CartSuccessOverlay> createState() => _CartSuccessOverlayState();
}

class _CartSuccessOverlayState extends State<_CartSuccessOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    ));
    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(_controller);
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 16,
      left: 16,
      right: 16,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Material(
            color: Colors.transparent,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      LucideIcons.checkCircle2,
                      color: Color(0xFF10B981),
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          'Added to cart',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          widget.productName,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  if (widget.onViewCart != null)
                    TextButton(
                      onPressed: widget.onViewCart,
                      style: TextButton.styleFrom(
                        foregroundColor: const Color(0xFF1e4db7),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                      ),
                      child: const Text(
                        'VIEW',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
