import 'package:flutter/material.dart';
import 'dart:async';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../providers/auth_provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/cart_provider.dart';
import '../buyer_app/buyer_home_screen.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';
import 'pending_approval_screen.dart';

class WebStyleLoginScreen extends StatefulWidget {
  const WebStyleLoginScreen({super.key});

  @override
  State<WebStyleLoginScreen> createState() => _WebStyleLoginScreenState();
}

class _WebStyleLoginScreenState extends State<WebStyleLoginScreen>
    with TickerProviderStateMixin {
  // ─── Keys ───────────────────────────────────────────────────────────────────
  static const String _rememberMeKey = 'remember_me';
  static const String _rememberedEmailKey = 'remembered_email';
  static const String _rememberedPasswordKey = 'remembered_password';

  // ─── Controllers ────────────────────────────────────────────────────────────
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  late final AnimationController _shakeController;
  late final Animation<double> _shakeAnimation;
  late final AnimationController _floatController;
  late final Animation<double> _floatAnimation;

  // ─── State ──────────────────────────────────────────────────────────────────
  bool _obscurePassword = true;
  bool _rememberMe = false;
  bool _isLoading = false;
  String? _errorMessage;
  String? _emailError;
  String? _passwordError;
  bool _hasSubmitted = false;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId:
        '668360708226-q79n83ttq956po4cj3pd5qig0thiqp6c.apps.googleusercontent.com',
  );

  // ─── Design Tokens ──────────────────────────────────────────────────────────
  static const Color navyDark = Color(0xFF0B1628);
  static const Color navyMid = Color(0xFF142240);
  static const Color navyLight = Color(0xFF1E3561);
  static const Color goldPrimary = Color(0xFFFFA726);
  static const Color goldLight = Color(0xFFFFBF4D);
  static const Color errorColor = Color(0xFFEF5350);
  static const Color white70 = Color(0xB3FFFFFF);
  static const Color white40 = Color(0x66FFFFFF);
  static const Color white10 = Color(0x1AFFFFFF);
  static const Color white14 = Color(0x24FFFFFF);

  static const List<Color> rainbowColors = [
    Color(0xFFFFA726),
    Color(0xFFAB47BC),
    Color(0xFF29B6F6),
    Color(0xFFEF5350),
    Color(0xFF66BB6A),
  ];

  static const List<Map<String, dynamic>> floatingItems = [
    {'emoji': '🌟', 'top': 0.18, 'left': 0.06},
    {'emoji': '⭐', 'top': 0.12, 'left': 0.82},
    {'emoji': '🎈', 'top': 0.72, 'left': 0.08},
    {'emoji': '🎀', 'top': 0.78, 'left': 0.88},
    {'emoji': '🧸', 'top': 0.88, 'left': 0.20},
    {'emoji': '🪀', 'top': 0.60, 'left': 0.90},
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

    _loadRememberedCredentials();
  }

  Future<void> _loadRememberedCredentials() async {
    final prefs = await SharedPreferences.getInstance();
    final rememberMe = prefs.getBool(_rememberMeKey) ?? false;
    if (rememberMe) {
      setState(() {
        _rememberMe = true;
        _emailController.text = prefs.getString(_rememberedEmailKey) ?? '';
        _passwordController.text =
            prefs.getString(_rememberedPasswordKey) ?? '';
      });
    }
  }

  @override
  void dispose() {
    _shakeController.dispose();
    _floatController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
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

  String? _validatePasswordValue(String value) {
    if (value.isEmpty) return 'Password is required';
    if (value.length < 6) return 'Password must be at least 6 characters';
    return null;
  }

  void _handleEmailChanged(String value) {
    if (_errorMessage != null || (_hasSubmitted && _emailError != null)) {
      setState(() {
        if (_hasSubmitted) _emailError = _validateEmailValue(value);
        _errorMessage = null;
      });
    }
  }

  void _handlePasswordChanged(String value) {
    if (_errorMessage != null || (_hasSubmitted && _passwordError != null)) {
      setState(() {
        if (_hasSubmitted) _passwordError = _validatePasswordValue(value);
        _errorMessage = null;
      });
    }
  }

  void _markFieldsAsTouched() {
    setState(() {
      _hasSubmitted = true;
      _emailError = _validateEmailValue(_emailController.text);
      _passwordError = _validatePasswordValue(_passwordController.text);
    });
  }

  void _triggerShake() {
    if (!_shakeController.isAnimating) _shakeController.forward(from: 0);
  }

  // ─── Login ──────────────────────────────────────────────────────────────────
  Future<void> _login() async {
    final prefs = await SharedPreferences.getInstance();
    if (_rememberMe) {
      await prefs.setBool(_rememberMeKey, true);
      await prefs.setString(_rememberedEmailKey, _emailController.text.trim());
      await prefs.setString(_rememberedPasswordKey, _passwordController.text);
    } else {
      await prefs.setBool(_rememberMeKey, false);
      await prefs.remove(_rememberedEmailKey);
      await prefs.remove(_rememberedPasswordKey);
    }

    _markFieldsAsTouched();
    if (_emailError != null || _passwordError != null) {
      _triggerShake();
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final authProvider = context.read<AuthProvider>();
      await authProvider.login(
        _emailController.text.trim(),
        _passwordController.text,
      );

      if (!mounted) return;

      if (authProvider.isAuthenticated && authProvider.user != null) {
        final userRole = authProvider.user!.role.toLowerCase();
        if (userRole == 'buyer' || userRole == 'rider') {
          // Refresh data after login
          if (userRole == 'buyer') {
            final buyerProvider = context.read<BuyerProvider>();
            final cartProvider = context.read<CartProvider>();
            await buyerProvider.fetchOrders();
            await cartProvider.loadCart();
          }
          if (mounted) {
            // Navigate to appropriate screen based on role
            if (userRole == 'rider') {
              Navigator.pushNamedAndRemoveUntil(
                context,
                '/rider-dashboard',
                (route) => false,
              );
            } else {
              await _navigateToBuyerHome(
                showAddressSetup: authProvider.requiresAddressSetup,
              );
            }
          }
        } else {
          await authProvider.logout();
          if (mounted)
            setState(() {
              _errorMessage =
                  'This account is not authorized to access the mobile app. Only Buyer and Rider accounts can log in.';
              _isLoading = false;
            });
        }
      } else {
        if (authProvider.pendingApproval) {
          if (mounted) {
            setState(() {
              _isLoading = false;
              _errorMessage = null;
            });
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => PendingApprovalScreen(
                  email: _emailController.text.trim(),
                  message: authProvider.pendingApprovalMessage,
                ),
              ),
            );
          }
          return;
        }
        setState(() {
          _errorMessage = authProvider.errorMessage ??
              'Invalid credentials. Please try again.';
          _isLoading = false;
        });
        _triggerShake();
      }
    } on TimeoutException {
      if (mounted)
        setState(() {
          _errorMessage =
              'Connection timeout. Backend server is not responding.';
          _isLoading = false;
        });
      _triggerShake();
    } catch (e) {
      if (mounted) {
        final msg = e.toString();
        setState(() {
          _errorMessage = msg.contains('Connection') ||
                  msg.contains('Socket') ||
                  msg.contains('Network') ||
                  msg.contains('Failed host lookup')
              ? 'Network error. Check your connection.'
              : msg.contains('Connection refused')
                  ? 'Cannot connect to server.'
                  : 'Invalid credentials. Please try again.';
          _isLoading = false;
        });
        _triggerShake();
      }
    }
  }

  // ─── Build ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: [
          // ── Background gradient ──────────────────────────────────────────────
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [navyDark, navyMid, navyLight],
              ),
            ),
          ),

          // ── Gold glow orb top-right ──────────────────────────────────────────
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

          // ── Purple glow orb left ─────────────────────────────────────────────
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

          // ── Blue glow orb bottom ─────────────────────────────────────────────
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

          // ── Twinkling star dots ──────────────────────────────────────────────
          ..._buildStars(size),

          // ── Floating emoji items ─────────────────────────────────────────────
          ..._buildFloatingItems(size),

          // ── Main content ─────────────────────────────────────────────────────
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
                          _buildSignUpRow(),
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

  // ── Twinkling stars helper ─────────────────────────────────────────────────
  List<Widget> _buildStars(Size size) {
    final starPositions = [
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
    return starPositions
        .map((p) => Positioned(
              top: p[0] * size.height,
              left: p[1] * size.width,
              child: _TwinklingStar(size: 10 + (p[0] * 8)),
            ))
        .toList();
  }

  // ── Floating emojis helper ─────────────────────────────────────────────────
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

  // ── Header: crown logo + title ─────────────────────────────────────────────
  Widget _buildHeader() {
    return Column(
      children: [
        // Crown logo
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
              offset: const Offset(0, 16))
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome header
              const Center(
                child: Column(
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Welcome back!',
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: 20,
                                fontWeight: FontWeight.w900)),
                      ],
                    ),
                    SizedBox(height: 4),
                    Text('Sign in to continue your adventure',
                        style: TextStyle(color: white40, fontSize: 12)),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Rainbow accent bar
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

              // Email field
              _buildLabel('Email'),
              const SizedBox(height: 4),
              _buildTextField(
                controller: _emailController,
                hint: 'your@email.com',
                icon: Icons.email_outlined,
                error: _emailError,
                onChanged: _handleEmailChanged,
                keyboardType: TextInputType.emailAddress,
              ),
              _buildFieldError(_emailError),

              const SizedBox(height: 14),

              // Password field
              _buildLabel('Password'),
              const SizedBox(height: 4),
              _buildTextField(
                controller: _passwordController,
                hint: '••••••••',
                icon: Icons.lock_outline,
                error: _passwordError,
                onChanged: _handlePasswordChanged,
                obscureText: _obscurePassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscurePassword
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    color: white40,
                    size: 18,
                  ),
                  onPressed: () =>
                      setState(() => _obscurePassword = !_obscurePassword),
                  padding: EdgeInsets.zero,
                  constraints:
                      const BoxConstraints(minWidth: 36, minHeight: 36),
                ),
              ),
              _buildFieldError(_passwordError),

              const SizedBox(height: 14),

              // Remember me + Forgot password
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      GestureDetector(
                        onTap: () => setState(() => _rememberMe = !_rememberMe),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 18,
                          height: 18,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(5),
                            color: _rememberMe ? goldPrimary : white10,
                            border: Border.all(
                                color: white40.withValues(alpha: 0.4)),
                            boxShadow: _rememberMe
                                ? [
                                    BoxShadow(
                                        color:
                                            goldPrimary.withValues(alpha: 0.4),
                                        blurRadius: 8)
                                  ]
                                : [],
                          ),
                          child: _rememberMe
                              ? const Icon(Icons.check,
                                  color: Colors.white, size: 12)
                              : null,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Text('Remember me',
                          style: TextStyle(color: white70, fontSize: 12)),
                    ],
                  ),
                  GestureDetector(
                    onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (_) => const ForgotPasswordScreen())),
                    child: const Text('Forgot password?',
                        style: TextStyle(
                            color: goldLight,
                            fontSize: 12,
                            fontWeight: FontWeight.bold)),
                  ),
                ],
              ),

              // Error banner
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: _errorMessage == null
                    ? const SizedBox.shrink()
                    : Container(
                        key: const ValueKey('error'),
                        margin: const EdgeInsets.only(top: 12),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 10),
                        decoration: BoxDecoration(
                          color: errorColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                              color: errorColor.withValues(alpha: 0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.warning_amber_rounded,
                                color: errorColor, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(_errorMessage!,
                                  style: const TextStyle(
                                      color: errorColor,
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600)),
                            ),
                          ],
                        ),
                      ),
              ),

              const SizedBox(height: 20),

              // Login button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: goldPrimary,
                    disabledBackgroundColor: goldPrimary.withValues(alpha: 0.5),
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
                                  AlwaysStoppedAnimation<Color>(Colors.white)),
                        )
                      : const Text('Login',
                          style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w900,
                              fontSize: 16,
                              letterSpacing: 0.5)),
                ),
              ),

              const SizedBox(height: 16),

              // Divider
              Row(
                children: [
                  Expanded(
                      child: Divider(
                          color: Colors.white.withValues(alpha: 0.1),
                          thickness: 1)),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 12),
                    child: Text('or continue with',
                        style: TextStyle(color: white40, fontSize: 11)),
                  ),
                  Expanded(
                      child: Divider(
                          color: Colors.white.withValues(alpha: 0.1),
                          thickness: 1)),
                ],
              ),

              const SizedBox(height: 14),

              // Google button
              SizedBox(
                width: double.infinity,
                height: 46,
                child: OutlinedButton(
                  onPressed: _isLoading ? null : _handleGoogleSignIn,
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(
                        color: Colors.white.withValues(alpha: 0.15),
                        width: 1.5),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14)),
                    backgroundColor: Colors.white.withValues(alpha: 0.06),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Image.network(
                        'https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg',
                        width: 18,
                        height: 18,
                        errorBuilder: (context, error, stackTrace) =>
                            const Icon(
                          Icons.g_mobiledata,
                          size: 18,
                          color: white70,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text('Sign in with Google',
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

  // ── Sign up row ────────────────────────────────────────────────────────────
  Widget _buildSignUpRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Text('No account? ',
            style: TextStyle(color: white70, fontSize: 13)),
        GestureDetector(
          onTap: () => Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (_) => const WebStyleRegisterScreen())),
          child: const Text('Sign up',
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

  // ── Shared helpers ─────────────────────────────────────────────────────────
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
                            overflow: TextOverflow.ellipsis)),
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
    bool obscureText = false,
    Widget? suffixIcon,
  }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      onChanged: onChanged,
      style: const TextStyle(color: Colors.white, fontSize: 13),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: white40, fontSize: 12),
        prefixIcon:
            Icon(icon, size: 18, color: error != null ? errorColor : white40),
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: error != null
            ? errorColor.withValues(alpha: 0.10)
            : Colors.white.withValues(alpha: 0.08),
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

// ─── Twinkling star widget ────────────────────────────────────────────────────
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
