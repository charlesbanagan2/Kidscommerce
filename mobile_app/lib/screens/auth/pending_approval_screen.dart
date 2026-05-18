import 'package:flutter/material.dart';

/// Waiting for Admin Approval Screen
/// Matches the modern style of login/register screens
class PendingApprovalScreen extends StatefulWidget {
  final String? email;
  final String? message;

  const PendingApprovalScreen({super.key, this.email, this.message});

  @override
  State<PendingApprovalScreen> createState() => _PendingApprovalScreenState();
}

class _PendingApprovalScreenState extends State<PendingApprovalScreen>
    with TickerProviderStateMixin {
  late final AnimationController _fadeController;
  late final AnimationController _floatController;
  late final Animation<double> _fadeAnimation;
  late final Animation<double> _floatAnimation;

  static const Color primaryBlue = Color(0xFF1A2980);
  static const Color goldColor = Color(0xFFFFD700);
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textWhite70 = Color(0xB3FFFFFF);

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..forward();
    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat(reverse: true);

    _fadeAnimation =
        CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut);
    _floatAnimation = Tween<double>(begin: -6.0, end: 6.0).animate(
      CurvedAnimation(parent: _floatController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _floatController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final infoMessage = widget.message ??
        'Your account is pending admin approval. We will notify you by email once a decision is made.';
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF0F1C45),
              Color(0xFF1A2980),
              Color(0xFF16356B),
              Color(0xFF0D1B3E),
            ],
            stops: [0.0, 0.35, 0.65, 1.0],
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: -60,
              right: -60,
              child: Container(
                width: 220,
                height: 220,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.04),
                ),
              ),
            ),
            Positioned(
              bottom: 80,
              left: -80,
              child: Container(
                width: 260,
                height: 260,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.03),
                ),
              ),
            ),
            SafeArea(
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SingleChildScrollView(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                  child: Column(
                    children: [
                      const Text(
                        'KIDS KINGDOM',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                          color: Colors.white,
                          letterSpacing: 2,
                        ),
                      ),
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text('✦ ',
                              style: TextStyle(color: goldColor, fontSize: 10)),
                          Text(
                            'Shop for Kids',
                            style: TextStyle(
                              fontSize: 12,
                              color: goldColor,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 1.2,
                            ),
                          ),
                          Text(' ✦',
                              style: TextStyle(color: goldColor, fontSize: 10)),
                        ],
                      ),
                      const SizedBox(height: 36),
                      AnimatedBuilder(
                        animation: _floatAnimation,
                        builder: (context, child) {
                          return Transform.translate(
                            offset: Offset(0, _floatAnimation.value),
                            child: child,
                          );
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 20, vertical: 24),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.08),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: Colors.white.withValues(alpha: 0.15),
                            ),
                          ),
                          child: Column(
                            children: [
                              Container(
                                width: 64,
                                height: 64,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white.withValues(alpha: 0.12),
                                ),
                                child: const Icon(
                                  Icons.hourglass_top_rounded,
                                  color: goldColor,
                                  size: 36,
                                ),
                              ),
                              const SizedBox(height: 18),
                              const Text(
                                'Waiting for Admin Approval',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w800,
                                  color: textWhite,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                infoMessage,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: textWhite70,
                                  height: 1.6,
                                ),
                              ),
                              if (widget.email != null &&
                                  widget.email!.isNotEmpty) ...[
                                const SizedBox(height: 10),
                                Text(
                                  widget.email!,
                                  style: const TextStyle(
                                    color: goldColor,
                                    fontWeight: FontWeight.w700,
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                              const SizedBox(height: 18),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.08),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Text(
                                  'We will send you an email once your account is approved or rejected.',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: textWhite70,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 20),
                              SizedBox(
                                width: double.infinity,
                                height: 44,
                                child: ElevatedButton(
                                  onPressed: () =>
                                      Navigator.of(context).pop(),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: primaryBlue,
                                    foregroundColor: Colors.white,
                                    elevation: 0,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                  child: const Text(
                                    'Back to Login',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w700,
                                      fontSize: 13,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
