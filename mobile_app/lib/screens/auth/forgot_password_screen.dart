// forgot_password_screen.dart
import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import 'reset_password_screen.dart';

/// Kids Kingdom - Forgot Password Screen
/// Matches the login screen design exactly
class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen>
    with TickerProviderStateMixin {
  // ─── Controllers ────────────────────────────────────────────────────────────
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();

  late final AnimationController _shakeController;
  late final Animation<double> _shakeAnimation;
  late final AnimationController _floatController;
  late final Animation<double> _floatAnimation;
  late final AnimationController _successController;
  late final Animation<double> _successAnimation;

  // ─── State ──────────────────────────────────────────────────────────────────
  bool _isLoading = false;
  String? _message;
  bool _isError = false;
  bool _isSuccess = false;
  String? _emailError;
  bool _emailTouched = false;

  // ─── Design Tokens (same as login screen) ───────────────────────────────────
  static const Color navyDark = Color(0xFF0B1628);
  static const Color navyMid = Color(0xFF142240);
  static const Color navyLight = Color(0xFF1E3561);
  static const Color goldPrimary = Color(0xFFFFA726);
  static const Color goldLight = Color(0xFFFFBF4D);
  static const Color errorColor = Color(0xFFEF5350);
  static const Color successColor = Color(0xFF66BB6A);
  static const Color white70 = Color(0xB3FFFFFF);
  static const Color white40 = Color(0x66FFFFFF);
  static const Color white14 = Color(0x24FFFFFF);

  static const List<Color> rainbowColors = [
    Color(0xFFFFA726),
    Color(0xFFAB47BC),
    Color(0xFF29B6F6),
    Color(0xFFEF5350),
    Color(0xFF66BB6A),
  ];

  static const List<Map<String, dynamic>> floatingItems = [
    {'emoji': '🌟', 'top': 0.14, 'left': 0.06},
    {'emoji': '⭐', 'top': 0.10, 'left': 0.82},
    {'emoji': '🎈', 'top': 0.70, 'left': 0.07},
    {'emoji': '🎀', 'top': 0.76, 'left': 0.87},
    {'emoji': '🧸', 'top': 0.86, 'left': 0.18},
    {'emoji': '🪀', 'top': 0.58, 'left': 0.90},
  ];

  // ─── Lifecycle ──────────────────────────────────────────────────────────────
  @override
  void initState() {
    super.initState();

    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _shakeAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0, end: -8), weight: 1),
      TweenSequenceItem(tween: Tween(begin: -8, end: 8), weight: 2),
      TweenSequenceItem(tween: Tween(begin: 8, end: -6), weight: 2),
      TweenSequenceItem(tween: Tween(begin: -6, end: 6), weight: 2),
      TweenSequenceItem(tween: Tween(begin: 6, end: 0), weight: 1),
    ]).animate(
        CurvedAnimation(parent: _shakeController, curve: Curves.easeInOut));

    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
    _floatAnimation = Tween<double>(begin: -10, end: 10).animate(
        CurvedAnimation(parent: _floatController, curve: Curves.easeInOut));

    _successController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _successAnimation = CurvedAnimation(
      parent: _successController,
      curve: Curves.elasticOut,
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _shakeController.dispose();
    _floatController.dispose();
    _successController.dispose();
    super.dispose();
  }

  // ─── Validation ─────────────────────────────────────────────────────────────
  String? _validateEmailValue(String value) {
    final t = value.trim();
    if (t.isEmpty) return 'Email is required';
    if (!t.contains('@') || !t.contains('.'))
      return 'Please enter a valid email address';
    if (t.length < 5) return 'Email is too short';
    return null;
  }

  void _handleEmailChanged(String value) {
    _emailTouched = true;
    final err = _validateEmailValue(value);
    if (err != _emailError || _message != null) {
      setState(() {
        _emailError = err;
        _message = null;
      });
    }
  }

  void _triggerShake() {
    _shakeController.reset();
    _shakeController.forward();
  }

  // ─── Send Reset Code ─────────────────────────────────────────────────────────
  Future<void> _sendResetCode() async {
    setState(() {
      _emailTouched = true;
      _emailError = _validateEmailValue(_emailController.text);
    });

    if (_emailError != null) {
      _triggerShake();
      return;
    }

    setState(() {
      _isLoading = true;
      _message = null;
      _isError = false;
    });

    try {
      final result = await ApiService.request(
        'POST',
        '/api/v1/auth/forgot-password',
        body: {'email': _emailController.text.trim()},
        auth: false,
      );

      if (result['success'] == true) {
        setState(() {
          _message = 'Reset code sent! Check your email.';
          _isError = false;
          _isSuccess = true;
          _isLoading = false;
        });
        _successController.forward();

        Future.delayed(const Duration(seconds: 1), () {
          if (mounted) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ResetPasswordScreen(
                  email: _emailController.text.trim(),
                ),
              ),
            );
          }
        });
      } else {
        setState(() {
          _message = result['error'] ?? 'Failed to send reset code';
          _isError = true;
          _isLoading = false;
        });
        _triggerShake();
      }
    } catch (e) {
      setState(() {
        _message = 'Connection error. Please try again.';
        _isError = true;
        _isLoading = false;
      });
      _triggerShake();
    }
  }

  // ─── Build ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: [
          // ── Background gradient (identical to login) ──────────────────────────
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [navyDark, navyMid, navyLight],
              ),
            ),
          ),

          // ── Gold glow orb top-right ───────────────────────────────────────────
          Positioned(
            top: -80,
            right: -80,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: goldPrimary.withValues(alpha: 0.18),
              ),
            ),
          ),

          // ── Purple glow orb left ──────────────────────────────────────────────
          Positioned(
            top: size.height * 0.2,
            left: -60,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFFAB47BC).withValues(alpha: 0.12),
              ),
            ),
          ),

          // ── Blue glow orb bottom ──────────────────────────────────────────────
          Positioned(
            bottom: -90,
            left: size.width * 0.25,
            child: Container(
              width: 240,
              height: 240,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF29B6F6).withValues(alpha: 0.14),
              ),
            ),
          ),

          // ── Twinkling stars ───────────────────────────────────────────────────
          ..._buildStars(size),

          // ── Floating emoji items ──────────────────────────────────────────────
          ..._buildFloatingItems(size),

          // ── Main content ──────────────────────────────────────────────────────
          SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) => SingleChildScrollView(
                padding: EdgeInsets.only(
                  bottom: MediaQuery.of(context).viewInsets.bottom + 20,
                ),
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: constraints.maxHeight),
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const SizedBox(height: 40),
                          _buildHeader(),
                          const SizedBox(height: 24),
                          AnimatedBuilder(
                            animation: _shakeAnimation,
                            builder: (_, child) => Transform.translate(
                              offset: Offset(_shakeAnimation.value, 0),
                              child: child,
                            ),
                            child: _buildCard(),
                          ),
                          const SizedBox(height: 20),
                          _buildBackToLoginRow(),
                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Stars ─────────────────────────────────────────────────────────────────
  List<Widget> _buildStars(Size size) {
    final positions = [
      [0.08, 0.12],
      [0.15, 0.78],
      [0.05, 0.55],
      [0.25, 0.90],
      [0.70, 0.05],
      [0.80, 0.85],
      [0.90, 0.40],
      [0.55, 0.92],
      [0.42, 0.03],
    ];
    return positions
        .map((p) => Positioned(
              top: p[0] * size.height,
              left: p[1] * size.width,
              child: _TwinklingStar(size: 10 + (p[0] * 8)),
            ))
        .toList();
  }

  // ── Floating emojis ───────────────────────────────────────────────────────
  List<Widget> _buildFloatingItems(Size size) {
    return floatingItems
        .map((item) => Positioned(
              top: (item['top'] as double) * size.height,
              left: (item['left'] as double) * size.width,
              child: AnimatedBuilder(
                animation: _floatAnimation,
                builder: (_, __) => Transform.translate(
                  offset: Offset(0, _floatAnimation.value * 0.5),
                  child: Opacity(
                    opacity: 0.55,
                    child: Text(item['emoji'] as String,
                        style: const TextStyle(fontSize: 22)),
                  ),
                ),
              ),
            ))
        .toList();
  }

  // ── Header (identical structure to login) ─────────────────────────────────
  Widget _buildHeader() {
    return Column(
      children: [
        // Icon badge
        Container(
          width: 88,
          height: 88,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [goldLight, goldPrimary],
            ),
            boxShadow: [
              BoxShadow(
                  color: goldPrimary.withValues(alpha: 0.45),
                  blurRadius: 24,
                  offset: const Offset(0, 8)),
              BoxShadow(
                  color: goldPrimary.withValues(alpha: 0.15),
                  blurRadius: 0,
                  spreadRadius: 4),
            ],
          ),
          child: const Icon(Icons.workspace_premium_rounded,
              color: Colors.white, size: 48),
        ),
        const SizedBox(height: 14),

        // KIDS KINGDOM
        RichText(
          text: const TextSpan(
            style: TextStyle(
                fontSize: 26, fontWeight: FontWeight.w900, letterSpacing: 3),
            children: [
              TextSpan(text: 'KIDS ', style: TextStyle(color: Colors.white)),
              TextSpan(text: 'KINGDOM', style: TextStyle(color: goldLight)),
            ],
          ),
        ),
        const SizedBox(height: 6),

        // ✦ Shop for Kids ✦
        const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('✦ ', style: TextStyle(color: white40, fontSize: 12)),
            Text('Shop for Kids',
                style: TextStyle(
                    color: goldLight,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.5)),
            Text(' ✦', style: TextStyle(color: white40, fontSize: 12)),
          ],
        ),
      ],
    );
  }

  // ── Glass card ────────────────────────────────────────────────────────────
  Widget _buildCard() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        color: Colors.white.withValues(alpha: 0.08),
        border: Border.all(color: white14, width: 1.5),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.35),
              blurRadius: 48,
              offset: const Offset(0, 16)),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Card header ──────────────────────────────────────────────────
              Center(
                child: Column(
                  children: [
                    // Animated lock icon — switches to checkmark on success
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 400),
                      child: _isSuccess
                          ? ScaleTransition(
                              scale: _successAnimation,
                              child: Container(
                                key: const ValueKey('success_icon'),
                                width: 56,
                                height: 56,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: successColor.withValues(alpha: 0.2),
                                  border: Border.all(
                                      color:
                                          successColor.withValues(alpha: 0.5),
                                      width: 2),
                                ),
                                child: const Icon(Icons.check_rounded,
                                    color: successColor, size: 30),
                              ),
                            )
                          : Container(
                              key: const ValueKey('lock_icon'),
                              width: 56,
                              height: 56,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: goldPrimary.withValues(alpha: 0.15),
                                border: Border.all(
                                    color: goldPrimary.withValues(alpha: 0.35),
                                    width: 2),
                              ),
                              child: const Icon(Icons.lock_reset_rounded,
                                  color: goldLight, size: 28),
                            ),
                    ),
                    const SizedBox(height: 12),
                    const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('🔑 ', style: TextStyle(fontSize: 18)),
                        Text('Reset Password',
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: 20,
                                fontWeight: FontWeight.w900)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      "Enter your email and we'll send you a reset code",
                      style: TextStyle(color: white40, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Rainbow accent bar (identical to login) ──────────────────────
              Row(
                children: rainbowColors
                    .map((c) => Expanded(
                          child: Container(
                            height: 4,
                            margin: const EdgeInsets.symmetric(horizontal: 2),
                            decoration: BoxDecoration(
                                color: c,
                                borderRadius: BorderRadius.circular(4)),
                          ),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 20),

              // ── Message banner ───────────────────────────────────────────────
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: _message == null
                    ? const SizedBox.shrink()
                    : Container(
                        key: ValueKey(_message),
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 10),
                        margin: const EdgeInsets.only(bottom: 16),
                        decoration: BoxDecoration(
                          color: _isError
                              ? errorColor.withValues(alpha: 0.15)
                              : successColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _isError
                                ? errorColor.withValues(alpha: 0.3)
                                : successColor.withValues(alpha: 0.3),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _isError
                                  ? Icons.warning_amber_rounded
                                  : Icons.check_circle_outline_rounded,
                              color: _isError ? errorColor : successColor,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _message!,
                                style: TextStyle(
                                  color: _isError ? errorColor : successColor,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
              ),

              // ── Email label ──────────────────────────────────────────────────
              _buildLabel('Email Address'),
              const SizedBox(height: 4),
              _buildTextField(
                controller: _emailController,
                hint: 'your@email.com',
                icon: Icons.email_outlined,
                error: _emailTouched ? _emailError : null,
                onChanged: _handleEmailChanged,
                keyboardType: TextInputType.emailAddress,
                enabled: !_isSuccess,
              ),
              _buildFieldError(_emailTouched ? _emailError : null),

              const SizedBox(height: 24),

              // ── Send Reset Code button ───────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: (_isLoading || _isSuccess) ? null : _sendResetCode,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isSuccess ? successColor : goldPrimary,
                    disabledBackgroundColor: _isSuccess
                        ? successColor.withValues(alpha: 0.7)
                        : goldPrimary.withValues(alpha: 0.5),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                    elevation: 0,
                    shadowColor: goldPrimary.withValues(alpha: 0.4),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              _isSuccess
                                  ? Icons.check_rounded
                                  : Icons.send_rounded,
                              color: Colors.white,
                              size: 18,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _isSuccess ? 'Code Sent!' : 'Send Reset Code',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w900,
                                fontSize: 16,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ],
                        ),
                ),
              ),

              const SizedBox(height: 16),

              // ── Divider ──────────────────────────────────────────────────────
              Row(
                children: [
                  Expanded(
                      child: Divider(
                          color: Colors.white.withValues(alpha: 0.1),
                          thickness: 1)),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 12),
                    child: Text('or',
                        style: TextStyle(color: white40, fontSize: 11)),
                  ),
                  Expanded(
                      child: Divider(
                          color: Colors.white.withValues(alpha: 0.1),
                          thickness: 1)),
                ],
              ),

              const SizedBox(height: 14),

              // ── Back to Login button ─────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 46,
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(
                        color: Colors.white.withValues(alpha: 0.15),
                        width: 1.5),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14)),
                    backgroundColor: Colors.white.withValues(alpha: 0.06),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.arrow_back_ios_new_rounded,
                          color: white70, size: 14),
                      SizedBox(width: 8),
                      Text('Back to Login',
                          style: TextStyle(
                              color: white70,
                              fontWeight: FontWeight.w600,
                              fontSize: 13)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Back to login row (below card) ────────────────────────────────────────
  Widget _buildBackToLoginRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Text('Remembered your password? ',
            style: TextStyle(color: white70, fontSize: 13)),
        GestureDetector(
          onTap: () => Navigator.pop(context),
          child: const Text('Sign in 🚀',
              style: TextStyle(
                  color: goldLight,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  decoration: TextDecoration.underline,
                  decorationColor: goldLight)),
        ),
      ],
    );
  }

  // ── Shared helpers (identical to login screen) ────────────────────────────
  Widget _buildLabel(String text) => Text(text,
      style: const TextStyle(
          color: white70, fontSize: 11, fontWeight: FontWeight.w600));

  Widget _buildFieldError(String? error) => AnimatedSwitcher(
        duration: const Duration(milliseconds: 180),
        child: error == null
            ? const SizedBox(height: 0)
            : Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded,
                        size: 13, color: errorColor),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(error,
                          style: const TextStyle(
                              fontSize: 10,
                              color: errorColor,
                              fontWeight: FontWeight.w500),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis),
                    ),
                  ],
                ),
              ),
      );

  Widget _buildTextField({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    required String? error,
    required ValueChanged<String> onChanged,
    TextInputType keyboardType = TextInputType.text,
    bool enabled = true,
  }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      onChanged: onChanged,
      enabled: enabled,
      style: TextStyle(color: enabled ? Colors.white : white40, fontSize: 13),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: white40, fontSize: 12),
        prefixIcon:
            Icon(icon, size: 18, color: error != null ? errorColor : white40),
        filled: true,
        fillColor: error != null
            ? errorColor.withValues(alpha: 0.10)
            : enabled
                ? Colors.white.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.04),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        isDense: true,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
              color: error != null ? errorColor : white14, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: error != null ? errorColor.withValues(alpha: 0.7) : white14,
            width: 1.5,
          ),
        ),
        disabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.white10, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: error != null ? errorColor : goldPrimary,
            width: 1.5,
          ),
        ),
      ),
    );
  }
}

// ─── Twinkling star widget (same as login screen) ─────────────────────────────
class _TwinklingStar extends StatefulWidget {
  final double size;
  const _TwinklingStar({required this.size});

  @override
  State<_TwinklingStar> createState() => _TwinklingStarState();
}

class _TwinklingStarState extends State<_TwinklingStar>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1800))
      ..repeat(reverse: true);
    _anim = Tween<double>(begin: 0.2, end: 0.8)
        .animate(CurvedAnimation(parent: _c, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => FadeTransition(
        opacity: _anim,
        child: Icon(Icons.star_rounded, color: Colors.white, size: widget.size),
      );
}
