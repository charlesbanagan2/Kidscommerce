import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/api_service.dart';
import 'login_screen.dart';

/// Verify Email Screen - Enter 6-digit verification code
class VerifyEmailScreen extends StatefulWidget {
  final String email;

  const VerifyEmailScreen({
    super.key,
    required this.email,
  });

  @override
  State<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends State<VerifyEmailScreen> {
  final _formKey = GlobalKey<FormState>();
  final _codeController = TextEditingController();
  bool _isLoading = false;
  bool _isResending = false;
  String? _message;
  bool _isError = false;

  static const Color primaryColor = Color(0xFF0b63a8);
  static const Color textDark = Color(0xFF343a40);
  static const Color textMuted = Color(0xFF6c757d);
  static const Color borderColor = Color(0xFFdee2e6);

  Future<void> _verifyEmail() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _message = null;
      _isError = false;
    });

    try {
      final result = await ApiService.request(
        'POST',
        '/api/v1/auth/verify-email',
        body: {
          'email': widget.email,
          'code': _codeController.text.trim(),
        },
        auth: false,
      );

      if (result['success'] == true) {
        setState(() {
          _message = 'Email verified successfully!';
          _isError = false;
          _isLoading = false;
        });

        // Navigate to login after success
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(
                builder: (context) => const WebStyleLoginScreen(),
              ),
              (route) => false,
            );
          }
        });
      } else {
        setState(() {
          _message = result['error'] ?? 'Invalid verification code';
          _isError = true;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Connection error. Please try again.';
        _isError = true;
        _isLoading = false;
      });
    }
  }

  Future<void> _resendCode() async {
    setState(() {
      _isResending = true;
      _message = null;
    });

    try {
      final result = await ApiService.request(
        'POST',
        '/api/v1/auth/resend-verification',
        body: {'email': widget.email},
        auth: false,
      );

      if (result['success'] == true) {
        setState(() {
          _message = 'New code sent! Check your email.';
          _isError = false;
        });
      } else {
        setState(() {
          _message = result['error'] ?? 'Failed to resend code';
          _isError = true;
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Connection error. Please try again.';
        _isError = true;
      });
    } finally {
      setState(() {
        _isResending = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFf8f9fa),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textDark),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 500),
              child: Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Header
                        const Icon(
                          Icons.mark_email_read_outlined,
                          size: 64,
                          color: primaryColor,
                        ),
                        const SizedBox(height: 24),
                        const Text(
                          'Verify Your Email',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: textDark,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'A 6-digit code was sent to ${widget.email}',
                          style: const TextStyle(
                            fontSize: 14,
                            color: textMuted,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const Text(
                          'Enter it below:',
                          style: TextStyle(
                            fontSize: 14,
                            color: textMuted,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 32),

                        // Message
                        if (_message != null)
                          Container(
                            padding: const EdgeInsets.all(12),
                            margin: const EdgeInsets.only(bottom: 20),
                            decoration: BoxDecoration(
                              color: _isError
                                  ? Colors.red.shade50
                                  : Colors.green.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: _isError
                                    ? Colors.red.shade200
                                    : Colors.green.shade200,
                              ),
                            ),
                            child: Text(
                              _message!,
                              style: TextStyle(
                                color: _isError
                                    ? Colors.red.shade700
                                    : Colors.green.shade700,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),

                        // Code Field
                        TextFormField(
                          controller: _codeController,
                          keyboardType: TextInputType.number,
                          maxLength: 6,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 8,
                          ),
                          decoration: InputDecoration(
                            labelText: 'Verification Code',
                            hintText: '000000',
                            counterText: '',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(color: borderColor),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(
                                color: primaryColor,
                                width: 2,
                              ),
                            ),
                          ),
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(6),
                          ],
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Please enter the verification code';
                            }
                            if (value.length != 6) {
                              return 'Code must be 6 digits';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 24),

                        // Verify Button
                        SizedBox(
                          height: 48,
                          child: ElevatedButton(
                            onPressed: _isLoading ? null : _verifyEmail,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: primaryColor,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: _isLoading
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white,
                                      ),
                                    ),
                                  )
                                : const Text(
                                    'Verify',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Resend Code Button
                        TextButton(
                          onPressed: _isResending ? null : _resendCode,
                          child: _isResending
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Text('Resend Code'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
