// reset_password_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import '../../services/api_service.dart';
import 'login_screen.dart';

/// Kids Kingdom - Reset Password Screen
/// Modern error handling with visual feedback
class ResetPasswordScreen extends StatefulWidget {
  final String email;

  const ResetPasswordScreen({
    super.key,
    required this.email,
  });

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen>
    with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _codeController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late final AnimationController _shakeController;
  late final Animation<double> _shakeAnimation;
  late final AnimationController _floatController;
  late final AnimationController _successController;
  late final Animation<double> _successAnimation;
  late final AnimationController _errorPulseController;
  late final Animation<double> _errorPulseAnimation;

  bool _obscurePassword = true;
  bool _obscureConfirm = true;
  bool _isLoading = false;
  String? _message;
  bool _isError = false;
  bool _isSuccess = false;
  int _codeAttempts = 0;
  bool _codeFieldHasError = false;
  bool _isShaking = false; // Add shake state flag

  String? _codeError;
  String? _passwordError;
  String? _confirmError;
  bool _codeTouched = false;
  bool _passwordTouched = false;
  bool _confirmTouched = false;

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

  @override
  void initState() {
    super.initState();

    // Simplified shake animation
    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    
    _shakeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _shakeController,
      curve: Curves.elasticIn,
    ));

    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);

    _successController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _successAnimation = CurvedAnimation(
      parent: _successController,
      curve: Curves.elasticOut,
    );

    _errorPulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _errorPulseAnimation = Tween<double>(begin: 1.0, end: 1.03).animate(
      CurvedAnimation(parent: _errorPulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _shakeController.dispose();
    _floatController.dispose();
    _successController.dispose();
    _errorPulseController.dispose();
    _codeController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String? _validateCode(String value) {
    if (value.isEmpty) return 'Reset code is required';
    if (value.length != 6) return 'Code must be exactly 6 digits';
    if (!RegExp(r'^\d+$').hasMatch(value))
      return 'Code must contain only numbers';
    return null;
  }

  String? _validatePassword(String value) {
    if (value.isEmpty) return 'Password is required';
    if (value.length < 8 || value.length > 12) {
      return 'Password must be 8-12 characters';
    }
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'Must contain uppercase letter';
    }
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'Must contain lowercase letter';
    }
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return 'Must contain a number';
    }
    if (!RegExp(r'[!@#\$%^&*\-_]').hasMatch(value)) {
      return 'Must contain special char (!@#\$%^&*-_)';
    }
    return null;
  }

  String? _validateConfirm(String value) {
    if (value.isEmpty) return 'Please confirm your password';
    if (value != _newPasswordController.text) return 'Passwords do not match';
    return null;
  }

  void _triggerShake() {
    if (!mounted) return;
    
    setState(() => _isShaking = true);
    
    if (_shakeController.isAnimating) {
      _shakeController.stop();
    }
    
    _shakeController.reset();
    _shakeController.forward().then((_) {
      if (mounted) {
        _shakeController.reverse().then((_) {
          if (mounted) {
            setState(() => _isShaking = false);
          }
        });
      }
    });
  }

  void _triggerErrorPulse() {
    if (!mounted || _errorPulseController.isAnimating) return;
    
    _errorPulseController.forward().then((_) {
      if (mounted) {
        _errorPulseController.reverse();
      }
    });
  }

  Future<void> _resetPassword() async {
    // Prevent multiple simultaneous requests
    if (_isLoading) return;
    
    setState(() {
      _codeTouched = true;
      _passwordTouched = true;
      _confirmTouched = true;
      _codeError = _validateCode(_codeController.text.trim());
      _passwordError = _validatePassword(_newPasswordController.text);
      _confirmError = _validateConfirm(_confirmPasswordController.text);
    });

    if (_codeError != null || _passwordError != null || _confirmError != null) {
      _triggerShake();
      return;
    }

    setState(() {
      _isLoading = true;
      _message = null;
      _isError = false;
      _codeFieldHasError = false;
    });

    try {
      final result = await ApiService.request(
        'POST',
        '/api/v1/auth/reset-password',
        body: {
          'email': widget.email,
          'code': _codeController.text.trim(),
          'new_password': _newPasswordController.text,
        },
        auth: false,
      );

      if (!mounted) return;
      
      setState(() => _isLoading = false);

      // Check if result is null or has error
      if (result == null) {
        if (!mounted) return;
        setState(() {
          _message = '📡 Connection error. Please check your internet and try again.';
          _isError = true;
        });
        return;
      }

      if (result['success'] == true) {
        if (!mounted) return;
        setState(() {
          _message = '✓ Password reset successful!';
          _isError = false;
          _isSuccess = true;
          _codeAttempts = 0;
        });
        _successController.forward();

        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(
                  builder: (context) => const WebStyleLoginScreen()),
              (route) => false,
            );
          }
        });
      } else {
        // Handle error response
        final errorMsg = result['error'] ?? result['message'] ?? 'Failed to reset password';
        final errorType = result['error_type'] ?? '';
        final attempts = result['attempts'] ?? 0;
        final remainingAttempts = result['remaining_attempts'] ?? 0;
        
        String displayMessage = errorMsg;
        bool isCodeError = false;

        // Handle specific error types from backend
        if (errorType == 'invalid_code') {
          isCodeError = true;
          _codeAttempts = attempts;
          
          if (remainingAttempts > 0) {
            displayMessage = '❌ Invalid verification code. $remainingAttempts attempt(s) remaining.';
          } else if (_codeAttempts == 1) {
            displayMessage = '❌ Invalid verification code. Please check your email and try again.';
          } else if (_codeAttempts == 2) {
            displayMessage = '❌ Invalid code. Attempt $_codeAttempts of 3. Double-check your email.';
          } else if (_codeAttempts >= 3) {
            displayMessage = '🚫 Too many failed attempts. Please request a new code.';
          }
        } else if (errorType == 'expired_code') {
          displayMessage = '⏰ Code has expired. Please request a new one.';
          isCodeError = true;
        } else if (errorType == 'too_many_attempts') {
          displayMessage = '🚫 Too many failed attempts. Please request a new code.';
          isCodeError = true;
        } else if (errorType == 'user_not_found') {
          displayMessage = '❌ User account not found. Please try again.';
          isCodeError = false;
        } else if (errorType == 'server_error') {
          displayMessage = '📡 Server error. Please try again later.';
          isCodeError = false;
        } else {
          // Fallback: check error message content
          final errorLower = errorMsg.toLowerCase();
          
          if (errorLower.contains('invalid') && errorLower.contains('code')) {
            isCodeError = true;
            _codeAttempts++;
            if (_codeAttempts == 1) {
              displayMessage = '❌ Invalid verification code. Please check your email and try again.';
            } else if (_codeAttempts == 2) {
              displayMessage = '❌ Invalid code. Attempt $_codeAttempts of 3. Double-check your email.';
            } else if (_codeAttempts >= 3) {
              displayMessage = '🚫 Too many failed attempts. Please request a new code.';
            }
          } else if (errorLower.contains('expired')) {
            displayMessage = '⏰ Code has expired. Please request a new one.';
            isCodeError = true;
          } else if (errorLower.contains('not found') || errorLower.contains('incorrect')) {
            displayMessage = '❌ Invalid verification code. Please try again.';
            isCodeError = true;
            _codeAttempts++;
          } else if (errorLower.contains('password')) {
            displayMessage = '🔒 $errorMsg';
          } else {
            // Generic error
            displayMessage = '❌ $errorMsg';
            isCodeError = true;
          }
        }

        if (!mounted) return;
        setState(() {
          _message = displayMessage;
          _isError = true;
          _codeFieldHasError = isCodeError;
        });

        _triggerShake();
        _triggerErrorPulse();

        if (isCodeError) {
          _codeController.clear();
          _codeTouched = false;
        }
      }
    } on ApiException catch (e) {
      if (!mounted) return;
      
      // Handle API errors (400, 401, etc.)
      String displayMessage;
      bool isCodeError = false;
      
      if (e.statusCode == 400) {
        // This is likely an invalid_code error
        displayMessage = e.message;
        if (displayMessage.toLowerCase().contains('invalid') && 
            displayMessage.toLowerCase().contains('code')) {
          isCodeError = true;
          _codeAttempts++;
        }
      } else if (e.statusCode == 404) {
        displayMessage = '❌ User account not found. Please try again.';
      } else {
        displayMessage = '📡 ${e.message}';
      }
      
      setState(() {
        _message = displayMessage;
        _isError = true;
        _isLoading = false;
        _codeFieldHasError = isCodeError;
      });
      
      _triggerShake();
      _triggerErrorPulse();
      
      if (isCodeError) {
        _codeController.clear();
        _codeTouched = false;
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _message = '📡 Connection error. Please check your internet and try again.';
        _isError = true;
        _isLoading = false;
      });
      _triggerShake();
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: [
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [navyDark, navyMid, navyLight],
              ),
            ),
          ),
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
                            builder: (_, child) {
                              // Simple sine wave shake
                              double offset = 0.0;
                              if (_isShaking && _shakeController.isAnimating) {
                                offset = math.sin(_shakeAnimation.value * math.pi * 2) * 8.0;
                              }
                              return Transform.translate(
                                offset: Offset(offset, 0),
                                child: child,
                              );
                            },
                            child: _buildCard(),
                          ),
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

  Widget _buildHeader() {
    return Column(
      children: [
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
            ],
          ),
          child: const Icon(Icons.workspace_premium_rounded,
              color: Colors.white, size: 48),
        ),
        const SizedBox(height: 14),
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
      ],
    );
  }

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
              Center(
                child: Column(
                  children: [
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 400),
                      child: _isSuccess
                          ? ScaleTransition(
                              scale: _successAnimation,
                              child: Container(
                                key: const ValueKey('success'),
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
                              key: const ValueKey('crown'),
                              width: 56,
                              height: 56,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: goldPrimary.withValues(alpha: 0.15),
                                border: Border.all(
                                    color: goldPrimary.withValues(alpha: 0.35),
                                    width: 2),
                              ),
                              child: const Icon(Icons.workspace_premium_rounded,
                                  color: goldLight, size: 28),
                            ),
                    ),
                    const SizedBox(height: 12),
                    const Text('🔐 Reset Password',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w900)),
                    const SizedBox(height: 4),
                    Text(
                      'Enter code sent to ${widget.email}',
                      style: const TextStyle(color: white40, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
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
              if (_message != null)
                AnimatedBuilder(
                  animation: _errorPulseAnimation,
                  builder: (context, child) {
                    final scale = _isError && _errorPulseController.isAnimating
                        ? _errorPulseAnimation.value
                        : 1.0;
                    return Transform.scale(
                      scale: scale,
                      child: child,
                    );
                  },
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: _isError
                          ? errorColor.withValues(alpha: 0.15)
                          : successColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: _isError
                            ? errorColor.withValues(alpha: 0.4)
                            : successColor.withValues(alpha: 0.4),
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: _isError
                              ? errorColor.withValues(alpha: 0.2)
                              : successColor.withValues(alpha: 0.2),
                          blurRadius: 8,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            _message!,
                            style: TextStyle(
                              color: _isError ? errorColor : successColor,
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              const Text('Reset Code',
                  style: TextStyle(
                      color: white70,
                      fontSize: 11,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              TextField(
                controller: _codeController,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(6),
                ],
                enabled: !_isSuccess,
                onChanged: (v) {
                  setState(() {
                    _codeTouched = true;
                    _codeError = _validateCode(v);
                    _message = null;
                    _codeFieldHasError = false;
                    _isError = false;
                  });
                },
                style: const TextStyle(
                    color: Colors.white, fontSize: 15, letterSpacing: 2),
                textAlign: TextAlign.center,
                decoration: InputDecoration(
                  hintText: '• • • • • •',
                  hintStyle: const TextStyle(color: white40, fontSize: 18),
                  prefixIcon: Icon(Icons.confirmation_number_outlined,
                      size: 18,
                      color: _codeFieldHasError ? errorColor : white40),
                  filled: true,
                  fillColor: _codeFieldHasError
                      ? errorColor.withValues(alpha: 0.1)
                      : Colors.white.withValues(alpha: 0.08),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                  isDense: true,
                  counterText: '',
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(
                          color: _codeFieldHasError ? errorColor : white14,
                          width: 2)),
                  enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(
                          color: _codeFieldHasError ? errorColor : white14,
                          width: 2)),
                  focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(
                          color: _codeFieldHasError ? errorColor : goldPrimary,
                          width: 2)),
                ),
              ),
              if (_codeTouched && _codeError != null)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline,
                          size: 14, color: errorColor),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(_codeError!,
                            style: const TextStyle(
                                fontSize: 11,
                                color: errorColor,
                                fontWeight: FontWeight.w600)),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 6),
              const Row(
                children: [
                  Icon(Icons.info_outline, size: 12, color: white40),
                  SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      'Check your email for the 6-digit code',
                      style: TextStyle(fontSize: 10, color: white40),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text('New Password',
                  style: TextStyle(
                      color: white70,
                      fontSize: 11,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              TextField(
                controller: _newPasswordController,
                obscureText: _obscurePassword,
                enabled: !_isSuccess,
                onChanged: (v) {
                  _passwordTouched = true;
                  setState(() {
                    _passwordError = _validatePassword(v);
                    _message = null;
                    if (_confirmTouched) {
                      _confirmError =
                          _validateConfirm(_confirmPasswordController.text);
                    }
                  });
                },
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  hintText: 'Enter new password',
                  hintStyle: const TextStyle(color: white40, fontSize: 12),
                  prefixIcon:
                      const Icon(Icons.lock_outline, size: 18, color: white40),
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
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.08),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  isDense: true,
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: white14, width: 1.5)),
                  enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: white14, width: 1.5)),
                  focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide:
                          const BorderSide(color: goldPrimary, width: 1.5)),
                ),
              ),
              if (_passwordTouched && _passwordError != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(_passwordError!,
                      style: const TextStyle(
                          fontSize: 10,
                          color: errorColor,
                          fontWeight: FontWeight.w500)),
                ),
              const SizedBox(height: 14),
              const Text('Confirm Password',
                  style: TextStyle(
                      color: white70,
                      fontSize: 11,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              TextField(
                controller: _confirmPasswordController,
                obscureText: _obscureConfirm,
                enabled: !_isSuccess,
                onChanged: (v) {
                  _confirmTouched = true;
                  setState(() {
                    _confirmError = _validateConfirm(v);
                    _message = null;
                  });
                },
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  hintText: 'Re-enter new password',
                  hintStyle: const TextStyle(color: white40, fontSize: 12),
                  prefixIcon:
                      const Icon(Icons.lock_outline, size: 18, color: white40),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureConfirm
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      color: white40,
                      size: 18,
                    ),
                    onPressed: () =>
                        setState(() => _obscureConfirm = !_obscureConfirm),
                    padding: EdgeInsets.zero,
                    constraints:
                        const BoxConstraints(minWidth: 36, minHeight: 36),
                  ),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.08),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  isDense: true,
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: white14, width: 1.5)),
                  enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: white14, width: 1.5)),
                  focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide:
                          const BorderSide(color: goldPrimary, width: 1.5)),
                ),
              ),
              if (_confirmTouched && _confirmError != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(_confirmError!,
                      style: const TextStyle(
                          fontSize: 10,
                          color: errorColor,
                          fontWeight: FontWeight.w500)),
                ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: (_isLoading || _isSuccess) ? null : _resetPassword,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isSuccess ? successColor : goldPrimary,
                    disabledBackgroundColor: _isSuccess
                        ? successColor.withValues(alpha: 0.7)
                        : goldPrimary.withValues(alpha: 0.5),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                    elevation: 0,
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
                      : Text(
                          _isSuccess ? '✓ Password Reset!' : 'Reset Password',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                            fontSize: 16,
                            letterSpacing: 0.5,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 46,
                child: OutlinedButton(
                  onPressed: () => Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(
                        builder: (_) => const WebStyleLoginScreen()),
                    (route) => false,
                  ),
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(
                        color: Colors.white.withValues(alpha: 0.15),
                        width: 1.5),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14)),
                    backgroundColor: Colors.white.withValues(alpha: 0.06),
                  ),
                  child: const Text('Back to Login',
                      style: TextStyle(
                          color: white70,
                          fontWeight: FontWeight.w600,
                          fontSize: 13)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
