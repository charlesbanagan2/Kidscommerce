// registration_success_screen.dart
import 'package:flutter/material.dart';

/// Kids Kingdom - Registration Success Screen
/// Matches the deep blue gradient, gold branding design
class RegistrationSuccessScreen extends StatefulWidget {
  final String email;
  final String role;

  const RegistrationSuccessScreen({
    super.key,
    required this.email,
    required this.role,
  });

  @override
  State<RegistrationSuccessScreen> createState() =>
      _RegistrationSuccessScreenState();
}

class _RegistrationSuccessScreenState extends State<RegistrationSuccessScreen>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _fadeController;
  late AnimationController _floatController;

  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<double> _floatAnimation;

  // Brand colors — same as register/login screen
  static const Color primaryBlue = Color(0xFF1A2980);
  static const Color goldColor = Color(0xFFFFD700);
  static const Color goldDark = Color(0xFFFFA500);
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textWhite70 = Color(0xB3FFFFFF);

  @override
  void initState() {
    super.initState();

    _scaleController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat(reverse: true);

    _scaleAnimation = CurvedAnimation(
      parent: _scaleController,
      curve: Curves.elasticOut,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    );
    _floatAnimation = Tween<double>(begin: -6.0, end: 6.0).animate(
      CurvedAnimation(parent: _floatController, curve: Curves.easeInOut),
    );

    // Stagger animations
    Future.delayed(const Duration(milliseconds: 100), () {
      if (mounted) _scaleController.forward();
    });
    Future.delayed(const Duration(milliseconds: 300), () {
      if (mounted) _fadeController.forward();
    });
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _fadeController.dispose();
    _floatController.dispose();
    super.dispose();
  }

  bool get _isBuyer => widget.role == 'buyer';

  @override
  Widget build(BuildContext context) {
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
            // Decorative circles (same as other screens)
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
            Positioned(
              top: 200,
              left: -40,
              child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: goldColor.withValues(alpha: 0.04),
                ),
              ),
            ),

            SafeArea(
              child: SingleChildScrollView(
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                child: Column(
                  children: [
                    // Header
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
                    const SizedBox(height: 10),

                    // Colorful accent bar
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 40),
                      child: Row(
                        children: [
                          _bar(Colors.yellow),
                          const SizedBox(width: 4),
                          _bar(Colors.pink),
                          const SizedBox(width: 4),
                          _bar(Colors.cyan),
                          const SizedBox(width: 4),
                          _bar(Colors.red),
                          const SizedBox(width: 4),
                          _bar(Colors.green),
                        ],
                      ),
                    ),

                    const SizedBox(height: 36),

                    // Main glass card
                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(28),
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.15)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.3),
                            blurRadius: 30,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 28, vertical: 36),
                      child: FadeTransition(
                        opacity: _fadeAnimation,
                        child: Column(
                          children: [
                            // Animated success icon
                            AnimatedBuilder(
                              animation: _floatAnimation,
                              builder: (context, child) {
                                return Transform.translate(
                                  offset: Offset(0, _floatAnimation.value),
                                  child: child,
                                );
                              },
                              child: ScaleTransition(
                                scale: _scaleAnimation,
                                child: Container(
                                  width: 110,
                                  height: 110,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: const LinearGradient(
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                      colors: [goldDark, goldColor],
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: goldColor.withValues(alpha: 0.5),
                                        blurRadius: 24,
                                        spreadRadius: 4,
                                        offset: const Offset(0, 6),
                                      ),
                                    ],
                                  ),
                                  child: const Center(
                                    child: Text(
                                      '🎉',
                                      style: TextStyle(fontSize: 48),
                                    ),
                                  ),
                                ),
                              ),
                            ),

                            const SizedBox(height: 28),

                            // Title
                            const Text(
                              'You\'re In!',
                              style: TextStyle(
                                fontSize: 30,
                                fontWeight: FontWeight.w900,
                                color: textWhite,
                                letterSpacing: 0.5,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _isBuyer
                                  ? 'Your buyer account has been created successfully.'
                                  : 'Your rider account has been created successfully.',
                              style: const TextStyle(
                                fontSize: 14,
                                color: textWhite70,
                                height: 1.5,
                              ),
                              textAlign: TextAlign.center,
                            ),

                            const SizedBox(height: 28),

                            // Role badge
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 20, vertical: 10),
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: _isBuyer
                                      ? [
                                          const Color(0xFF4776E6),
                                          const Color(0xFF8E54E9)
                                        ]
                                      : [
                                          const Color(0xFF11998E),
                                          const Color(0xFF38EF7D)
                                        ],
                                ),
                                borderRadius: BorderRadius.circular(30),
                                boxShadow: [
                                  BoxShadow(
                                    color: (_isBuyer
                                            ? const Color(0xFF4776E6)
                                            : const Color(0xFF11998E))
                                        .withValues(alpha: 0.4),
                                    blurRadius: 12,
                                    offset: const Offset(0, 4),
                                  ),
                                ],
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    _isBuyer ? '🛍️' : '🛵',
                                    style: const TextStyle(fontSize: 18),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    _isBuyer
                                        ? 'Buyer Account'
                                        : 'Rider Account',
                                    style: const TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w700,
                                      color: Colors.white,
                                      letterSpacing: 0.3,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            const SizedBox(height: 28),

                            // Email info card
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.07),
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                    color:
                                        Colors.white.withValues(alpha: 0.15)),
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: goldColor.withValues(alpha: 0.15),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: const Icon(
                                      Icons.email_outlined,
                                      color: goldColor,
                                      size: 20,
                                    ),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'Registered Email',
                                          style: TextStyle(
                                            fontSize: 11,
                                            color: textWhite70,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                        const SizedBox(height: 2),
                                        Text(
                                          widget.email,
                                          style: const TextStyle(
                                            fontSize: 14,
                                            color: textWhite,
                                            fontWeight: FontWeight.w600,
                                          ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            const SizedBox(height: 16),

                            // What's next card
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.07),
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                    color:
                                        Colors.white.withValues(alpha: 0.15)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'What\'s next?',
                                    style: TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w700,
                                      color: goldColor,
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  if (_isBuyer) ...[
                                    _buildNextStep(
                                      icon: '✅',
                                      text: 'Account created successfully',
                                      done: true,
                                    ),
                                    const SizedBox(height: 10),
                                    _buildNextStep(
                                      icon: '🔐',
                                      text: 'Sign in with your credentials',
                                      done: false,
                                    ),
                                    const SizedBox(height: 10),
                                    _buildNextStep(
                                      icon: '🛍️',
                                      text: 'Start shopping for kids products',
                                      done: false,
                                    ),
                                  ] else ...[
                                    _buildNextStep(
                                      icon: '✅',
                                      text: 'Account created successfully',
                                      done: true,
                                    ),
                                    const SizedBox(height: 10),
                                    _buildNextStep(
                                      icon: '🔍',
                                      text:
                                          'Account pending admin verification',
                                      done: false,
                                    ),
                                    const SizedBox(height: 10),
                                    _buildNextStep(
                                      icon: '🛵',
                                      text: 'Start delivering once approved',
                                      done: false,
                                    ),
                                  ],
                                ],
                              ),
                            ),

                            const SizedBox(height: 32),

                            // Go to Login button
                            SizedBox(
                              width: double.infinity,
                              height: 54,
                              child: ElevatedButton(
                                onPressed: () {
                                  Navigator.pushNamedAndRemoveUntil(
                                    context,
                                    '/login',
                                    (route) => false,
                                  );
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.transparent,
                                  shadowColor: Colors.transparent,
                                  padding: EdgeInsets.zero,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                ),
                                child: Ink(
                                  decoration: BoxDecoration(
                                    gradient: const LinearGradient(
                                      colors: [goldDark, goldColor],
                                    ),
                                    borderRadius: BorderRadius.circular(14),
                                    boxShadow: [
                                      BoxShadow(
                                        color:
                                            goldColor.withValues(alpha: 0.45),
                                        blurRadius: 14,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Center(
                                    child: Text(
                                      '🚀  Go to Sign In',
                                      style: TextStyle(
                                        color: primaryBlue,
                                        fontWeight: FontWeight.w800,
                                        fontSize: 16,
                                        letterSpacing: 0.4,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ),

                            const SizedBox(height: 14),

                            // Explore button (outline)
                            SizedBox(
                              width: double.infinity,
                              height: 50,
                              child: OutlinedButton(
                                onPressed: () {
                                  Navigator.pushNamedAndRemoveUntil(
                                    context,
                                    '/home',
                                    (route) => false,
                                  );
                                },
                                style: OutlinedButton.styleFrom(
                                  side: BorderSide(
                                    color: Colors.white.withValues(alpha: 0.3),
                                    width: 1.5,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                ),
                                child: const Text(
                                  'Explore Kids Kingdom  →',
                                  style: TextStyle(
                                    color: textWhite70,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 32),

                    // Footer
                    Text(
                      'Welcome to the Kids Kingdom family! 👑',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.white.withValues(alpha: 0.5),
                        fontStyle: FontStyle.italic,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _bar(Color color) {
    return Expanded(
      child: Container(
        height: 3,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(2),
        ),
      ),
    );
  }

  Widget _buildNextStep({
    required String icon,
    required String text,
    required bool done,
  }) {
    return Row(
      children: [
        Text(icon, style: const TextStyle(fontSize: 16)),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: TextStyle(
              fontSize: 13,
              color: done ? Colors.white : textWhite70,
              fontWeight: done ? FontWeight.w600 : FontWeight.w400,
              decoration: done ? TextDecoration.none : TextDecoration.none,
            ),
          ),
        ),
        if (done)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: const Color(0xFF38EF7D).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'Done',
              style: TextStyle(
                fontSize: 10,
                color: Color(0xFF38EF7D),
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
      ],
    );
  }
}
