// pending_approval_screen.dart
// ─────────────────────────────────────────────────────────────────────────────
// UNIFIED POST-REGISTRATION SCREEN — Kids Kingdom
//
// Replaces RegistrationSuccessScreen entirely.
// Handles: Manual Email/Password registration + Google Sign-In first-time users.
// Users are LOCKED here until admin approves their account in the database.
// ─────────────────────────────────────────────────────────────────────────────

import 'package:flutter/material.dart';

class PendingApprovalScreen extends StatefulWidget {
  /// The registered email (from form or Google auth response).
  final String? email;

  /// Optional role label: 'buyer' | 'rider' | null
  final String? role;

  /// Optional custom message override.
  final String? message;

  const PendingApprovalScreen({
    super.key,
    this.email,
    this.role,
    this.message,
  });

  @override
  State<PendingApprovalScreen> createState() => _PendingApprovalScreenState();
}

class _PendingApprovalScreenState extends State<PendingApprovalScreen>
    with TickerProviderStateMixin {
  // ── Animation controllers ────────────────────────────────────────────────
  late final AnimationController _fadeCtrl;
  late final AnimationController _floatCtrl;
  late final AnimationController _pulseCtrl;
  late final AnimationController _slideCtrl;

  late final Animation<double> _fadeAnim;
  late final Animation<double> _floatAnim;
  late final Animation<double> _pulseAnim;
  late final Animation<Offset> _slideAnim;

  // ── Brand palette (shared with login / register screens) ─────────────────
  static const Color _primaryBlue = Color(0xFF1A2980);
  static const Color _gold = Color(0xFFFFD700);
  static const Color _goldDark = Color(0xFFFFA500);
  static const Color _white = Color(0xFFFFFFFF);
  static const Color _white70 = Color(0xB3FFFFFF);
  static const Color _white08 = Color(0x14FFFFFF);

  // ── Gradient stops (same as other screens) ───────────────────────────────
  static const List<Color> _bgGradient = [
    Color(0xFF0F1C45),
    Color(0xFF1A2980),
    Color(0xFF16356B),
    Color(0xFF0D1B3E),
  ];

  @override
  void initState() {
    super.initState();

    _fadeCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    )..forward();

    _floatCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);

    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat(reverse: true);

    _slideCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..forward();

    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);

    _floatAnim = Tween<double>(begin: -7.0, end: 7.0).animate(
      CurvedAnimation(parent: _floatCtrl, curve: Curves.easeInOut),
    );

    _pulseAnim = Tween<double>(begin: 0.92, end: 1.08).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );

    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.18),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _slideCtrl, curve: Curves.easeOutCubic));
  }

  @override
  void dispose() {
    _fadeCtrl.dispose();
    _floatCtrl.dispose();
    _pulseCtrl.dispose();
    _slideCtrl.dispose();
    super.dispose();
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  bool get _isRider => widget.role?.toLowerCase() == 'rider';

  String get _roleLabel => _isRider ? 'Rider Account' : 'Buyer Account';

  String get _roleEmoji => _isRider ? '🛵' : '🛍️';

  List<Color> get _roleBadgeColors => _isRider
      ? [const Color(0xFF11998E), const Color(0xFF38EF7D)]
      : [const Color(0xFF4776E6), const Color(0xFF8E54E9)];

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return PopScope(
      // Prevent hardware back — user must not bypass this screen
      canPop: false,
      child: Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: _bgGradient,
              stops: [0.0, 0.35, 0.65, 1.0],
            ),
          ),
          child: Stack(
            children: [
              // ── Decorative ambient circles ─────────────────────────────
              _ambientCircle(
                top: -60,
                right: -60,
                size: 220,
                color: Colors.white.withValues(alpha: 0.04),
              ),
              _ambientCircle(
                bottom: 80,
                left: -80,
                size: 260,
                color: Colors.white.withValues(alpha: 0.03),
              ),
              _ambientCircle(
                top: 200,
                left: -40,
                size: 130,
                color: _gold.withValues(alpha: 0.04),
              ),

              // ── Main content ───────────────────────────────────────────
              SafeArea(
                child: FadeTransition(
                  opacity: _fadeAnim,
                  child: SlideTransition(
                    position: _slideAnim,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 24, vertical: 20),
                      child: Column(
                        children: [
                          _buildHeader(),
                          const SizedBox(height: 10),
                          _buildAccentBar(),
                          const SizedBox(height: 36),
                          _buildMainCard(),
                          const SizedBox(height: 32),
                          _buildFooter(),
                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Sections ──────────────────────────────────────────────────────────────

  Widget _buildHeader() {
    return const Column(
      children: [
        Text(
          'KIDS KINGDOM',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w900,
            color: _white,
            letterSpacing: 2,
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('✦ ', style: TextStyle(color: _gold, fontSize: 10)),
            Text(
              'Shop for Kids',
              style: TextStyle(
                fontSize: 12,
                color: _gold,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.2,
              ),
            ),
            Text(' ✦', style: TextStyle(color: _gold, fontSize: 10)),
          ],
        ),
      ],
    );
  }

  Widget _buildAccentBar() {
    return Padding(
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
    );
  }

  Widget _buildMainCard() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: _white08,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.35),
            blurRadius: 32,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 36),
      child: Column(
        children: [
          // Animated hourglass icon
          _buildHourglassIcon(),
          const SizedBox(height: 24),

          // Title
          const Text(
            'Waiting for Admin\nApproval',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 26,
              fontWeight: FontWeight.w900,
              color: _white,
              letterSpacing: 0.3,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 10),

          // Subtitle
          Text(
            widget.message ??
                'Your account has been created successfully and is now pending review. '
                    'An admin will verify your details before granting access.',
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 13,
              color: _white70,
              height: 1.65,
            ),
          ),
          const SizedBox(height: 22),

          // Role badge (only if role is provided)
          if (widget.role != null) ...[
            _buildRoleBadge(),
            const SizedBox(height: 22),
          ],

          // Email card
          if (widget.email != null && widget.email!.isNotEmpty) ...[
            _buildEmailCard(),
            const SizedBox(height: 16),
          ],

          // Status timeline
          _buildStatusTimeline(),
          const SizedBox(height: 28),

          // Notice box
          _buildNoticeBox(),
          const SizedBox(height: 28),

          // Back to Login button
          _buildLoginButton(context),
        ],
      ),
    );
  }

  // ── Sub-widgets ───────────────────────────────────────────────────────────

  Widget _buildHourglassIcon() {
    return AnimatedBuilder(
      animation: Listenable.merge([_floatAnim, _pulseAnim]),
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _floatAnim.value),
          child: Transform.scale(
            scale: _pulseAnim.value,
            child: child,
          ),
        );
      },
      child: Container(
        width: 110,
        height: 110,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [_goldDark, _gold],
          ),
          boxShadow: [
            BoxShadow(
              color: _gold.withValues(alpha: 0.50),
              blurRadius: 28,
              spreadRadius: 4,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: const Center(
          child: Icon(
            Icons.hourglass_top_rounded,
            color: _primaryBlue,
            size: 52,
          ),
        ),
      ),
    );
  }

  Widget _buildRoleBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: _roleBadgeColors),
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: _roleBadgeColors.first.withValues(alpha: 0.40),
            blurRadius: 14,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(_roleEmoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 8),
          Text(
            _roleLabel,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: Colors.white,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmailCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: _gold.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.email_outlined, color: _gold, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Registered Email',
                  style: TextStyle(
                    fontSize: 11,
                    color: _white70,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  widget.email!,
                  style: const TextStyle(
                    fontSize: 14,
                    color: _white,
                    fontWeight: FontWeight.w600,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusTimeline() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Account Status',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: _gold,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 14),
          _timelineStep(
            icon: '✅',
            label: 'Account created successfully',
            state: _StepState.done,
          ),
          _timelineLine(),
          _timelineStep(
            icon: '🔍',
            label: 'Under admin review',
            state: _StepState.active,
          ),
          _timelineLine(),
          _timelineStep(
            icon: _isRider ? '🛵' : '🛍️',
            label: _isRider
                ? 'Start delivering once approved'
                : 'Start shopping once approved',
            state: _StepState.pending,
          ),
        ],
      ),
    );
  }

  Widget _buildNoticeBox() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: _gold.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _gold.withValues(alpha: 0.25)),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline_rounded, color: _gold, size: 18),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'You will receive an email notification once your account is approved or rejected by the admin.',
              style: TextStyle(
                fontSize: 12,
                color: _white70,
                height: 1.6,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoginButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
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
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        child: Ink(
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [_goldDark, _gold]),
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: _gold.withValues(alpha: 0.40),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: const Center(
            child: Text(
              '← Back to Sign In',
              style: TextStyle(
                color: _primaryBlue,
                fontWeight: FontWeight.w800,
                fontSize: 15,
                letterSpacing: 0.3,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFooter() {
    return Text(
      'We\'ll let you know as soon as you\'re approved. 👑',
      style: TextStyle(
        fontSize: 13,
        color: Colors.white.withValues(alpha: 0.45),
        fontStyle: FontStyle.italic,
      ),
      textAlign: TextAlign.center,
    );
  }

  // ── Timeline helpers ──────────────────────────────────────────────────────

  Widget _timelineStep({
    required String icon,
    required String label,
    required _StepState state,
  }) {
    final Color dotColor;
    final Color labelColor;
    final Widget? badge;

    switch (state) {
      case _StepState.done:
        dotColor = const Color(0xFF38EF7D);
        labelColor = _white;
        badge = _chip('Done', const Color(0xFF38EF7D));
        break;
      case _StepState.active:
        dotColor = _gold;
        labelColor = _gold;
        badge = _chip('In Progress', _gold);
        break;
      case _StepState.pending:
        dotColor = Colors.white24;
        labelColor = _white70;
        badge = null;
        break;
    }

    return Row(
      children: [
        // Dot
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: dotColor,
            boxShadow: state != _StepState.pending
                ? [
                    BoxShadow(
                        color: dotColor.withValues(alpha: 0.5), blurRadius: 8)
                  ]
                : null,
          ),
        ),
        const SizedBox(width: 12),
        Text(icon, style: const TextStyle(fontSize: 15)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 13,
              color: labelColor,
              fontWeight: state == _StepState.active
                  ? FontWeight.w600
                  : FontWeight.w400,
            ),
          ),
        ),
        if (badge != null) badge,
      ],
    );
  }

  Widget _timelineLine() {
    return Padding(
      padding: const EdgeInsets.only(left: 4, top: 4, bottom: 4),
      child: Container(
        width: 2,
        height: 20,
        color: Colors.white12,
      ),
    );
  }

  Widget _chip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  // ── Generic helpers ───────────────────────────────────────────────────────

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

  Widget _ambientCircle({
    double? top,
    double? bottom,
    double? left,
    double? right,
    required double size,
    required Color color,
  }) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      ),
    );
  }
}

// ── Step state enum ───────────────────────────────────────────────────────────
enum _StepState { done, active, pending }

// =============================================================================
// INTEGRATION GUIDE
// =============================================================================
//
// MANUAL REGISTRATION (email/password):
// ─────────────────────────────────────
// After your registration logic succeeds, replace:
//
//   Navigator.pushReplacement(context, MaterialPageRoute(
//     builder: (_) => RegistrationSuccessScreen(email: email, role: role),
//   ));
//
// With:
//
//   Navigator.pushAndRemoveUntil(
//     context,
//     MaterialPageRoute(
//       builder: (_) => PendingApprovalScreen(
//         email: email,        // from your form controller
//         role: selectedRole,  // 'buyer' | 'rider'
//       ),
//     ),
//     (route) => false,        // clears entire back stack
//   );
//
//
// GOOGLE SIGN-IN (first-time user):
// ──────────────────────────────────
// After confirming the Google user is new (no existing DB record), replace any
// navigation to home/register-success with:
//
//   final googleUser = await GoogleSignIn().signIn();
//   if (googleUser != null) {
//     // ... create user record in DB with status: 'pending' ...
//     Navigator.pushAndRemoveUntil(
//       context,
//       MaterialPageRoute(
//         builder: (_) => PendingApprovalScreen(
//           email: googleUser.email,
//           role: 'buyer', // or determine from your flow
//         ),
//       ),
//       (route) => false,
//     );
//   }
//
//
// ENFORCE APPROVAL GATE (login check):
// ──────────────────────────────────────
// In your login / auth-state handler, after fetching the user record:
//
//   if (userRecord.status == 'pending') {
//     Navigator.pushAndRemoveUntil(
//       context,
//       MaterialPageRoute(
//         builder: (_) => PendingApprovalScreen(
//           email: userRecord.email,
//           role: userRecord.role,
//         ),
//       ),
//       (route) => false,
//     );
//     return; // stop further navigation
//   }
//
//   if (userRecord.status == 'rejected') {
//     // show rejection dialog or navigate to a rejection screen
//     return;
//   }
//
//   // Only reaches here if status == 'approved'
//   Navigator.pushReplacementNamed(context, '/home');
//
//
// PopScope (canPop: false) prevents the hardware back button from bypassing
// this screen. The only exit is the "Back to Sign In" button which clears
// the route stack entirely, ensuring the user cannot navigate to /home.
// =============================================================================
