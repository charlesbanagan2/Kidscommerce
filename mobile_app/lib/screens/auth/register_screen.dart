// register_screen.dart
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import '../../services/api_service.dart';
import 'pending_approval_screen.dart';

/// Kids Kingdom - Enhanced Modern Register Screen
class WebStyleRegisterScreen extends StatefulWidget {
  const WebStyleRegisterScreen({super.key});

  @override
  State<WebStyleRegisterScreen> createState() => _WebStyleRegisterScreenState();
}

class _PsgcOption {
  final String code;
  final String name;

  const _PsgcOption({required this.code, required this.name});

  factory _PsgcOption.fromJson(Map<String, dynamic> json) {
    return _PsgcOption(
      code: json['code']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
    );
  }
}

class _WebStyleRegisterScreenState extends State<WebStyleRegisterScreen>
    with TickerProviderStateMixin {
  int _currentStep = 1;
  final int _totalSteps = 3;
  String _selectedRole = 'buyer';
  bool _isLoading = false;
  String? _errorMessage;
  int _passwordStrength = 0;
  bool _showPassword = false;
  bool _showConfirmPassword = false;
  bool _isVerifyingEmail = false;
  String? _emailVerificationError;
  final ScrollController _scrollController = ScrollController();
  final ScrollController _buyerTermsController = ScrollController();
  final ScrollController _riderTermsController = ScrollController();

  bool _buyerTermsAccepted = false;
  bool _riderTermsAccepted = false;
  bool _buyerTermsRead = false;
  bool _riderTermsRead = false;

  bool _isLoadingRegions = false;
  List<_PsgcOption> _regions = [];
  final Map<String, List<_PsgcOption>> _provinceCache = {};
  final Map<String, List<_PsgcOption>> _cityCache = {};
  final Map<String, List<_PsgcOption>> _barangayCache = {};

  String? _selectedRegionCode;
  String? _selectedProvinceCode;
  String? _selectedCityCode;
  String? _selectedBarangayCode;

  String? _selectedRiderRegionCode;
  String? _selectedRiderProvinceCode;
  String? _selectedRiderCityCode;
  String? _selectedRiderBarangayCode;

  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  final Map<String, String?> _fieldErrors = {
    'firstName': null,
    'lastName': null,
    'email': null,
    'phone': null,
    'password': null,
    'confirmPassword': null,
  };

  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _streetAddressController = TextEditingController();
  final _cityController = TextEditingController();
  final _provinceController = TextEditingController();
  final _vehicleTypeController = TextEditingController();
  final _vehicleNumberController = TextEditingController();
  final _driversLicenseController = TextEditingController();
  final _validIdController = TextEditingController();
  final _riderValidIdController = TextEditingController();

  // Brand colors
  static const Color primaryBlue = Color(0xFF1A2980);
  static const Color goldColor = Color(0xFFFFD700);
  static const Color goldDark = Color(0xFFFFA500);
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textWhite70 = Color(0xB3FFFFFF);
  static const Color errorRed = Color(0xFFFF6B6B);

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _fadeAnimation =
        CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut);
    _fadeController.forward();

    _phoneController.text = '09';
    _phoneController.addListener(() {
      if (!_phoneController.text.startsWith('09')) {
        _phoneController.text =
            '09' + _phoneController.text.replaceFirst(RegExp(r'^0+'), '');
        _phoneController.selection = TextSelection.fromPosition(
          TextPosition(offset: _phoneController.text.length),
        );
      }
    });
    _passwordController.addListener(() {
      setState(() {
        _passwordStrength =
            _calculatePasswordStrength(_passwordController.text);
      });
    });

    _emailController.addListener(_onEmailChanged);
    _buyerTermsController.addListener(() {
      if (_buyerTermsController.hasClients) {
        final position = _buyerTermsController.position;
        if (position.maxScrollExtent > 0 &&
            position.pixels >= position.maxScrollExtent - 4) {
          if (!_buyerTermsRead) {
            setState(() => _buyerTermsRead = true);
          }
        }
      }
    });
    _riderTermsController.addListener(() {
      if (_riderTermsController.hasClients) {
        final position = _riderTermsController.position;
        if (position.maxScrollExtent > 0 &&
            position.pixels >= position.maxScrollExtent - 4) {
          if (!_riderTermsRead) {
            setState(() => _riderTermsRead = true);
          }
        }
      }
    });
    _loadRegions();
  }

  int _calculatePasswordStrength(String password) {
    if (password.isEmpty) return 0;
    int strength = 0;
    if (password.length >= 10) strength++;
    if (RegExp(r'[A-Z]').hasMatch(password)) strength++;
    if (RegExp(r'[a-z]').hasMatch(password)) strength++;
    if (RegExp(r'[0-9]').hasMatch(password)) strength++;
    if (RegExp('[!@#\$%^&*()_+\\-=\\[\\]{};:\'",.<>/?|]').hasMatch(password))
      strength++;
    return strength;
  }

  Timer? _emailDebounceTimer;

  void _onEmailChanged() {
    _emailDebounceTimer?.cancel();
    if (_emailVerificationError != null) {
      setState(() => _emailVerificationError = null);
    }
    final email = _emailController.text.trim();
    if (email.isEmpty || !email.contains('@')) return;
    _emailDebounceTimer = Timer(const Duration(seconds: 1), () {
      _verifyEmailAddress(email);
    });
  }

  Future<void> _verifyEmailAddress(String email) async {
    final emailRegex =
        RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    if (!emailRegex.hasMatch(email)) return;

    setState(() {
      _isVerifyingEmail = true;
      _emailVerificationError = null;
    });

    try {
      final response = await http
          .post(
            Uri.parse('${ApiService.baseUrl}/api/check-email'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'email': email}),
          )
          .timeout(const Duration(seconds: 10));

      if (!mounted) return;
      final data = jsonDecode(response.body);

      setState(() {
        _isVerifyingEmail = false;
        if (response.statusCode == 200) {
          if (data['ok'] == false) {
            String errorMsg = data['message'] ?? 'Invalid email address';
            String status = data['status'] ?? '';
            if (status == 'pending') {
              _emailVerificationError =
                  'This email is waiting for admin approval. Please wait or contact support.';
            } else if (errorMsg.toLowerCase().contains('already') ||
                errorMsg.toLowerCase().contains('registered') ||
                errorMsg.toLowerCase().contains('exist')) {
              _emailVerificationError =
                  'This email is already registered. Please use a different email or login.';
            } else if (errorMsg.toLowerCase().contains('waiting') ||
                errorMsg.toLowerCase().contains('approval')) {
              _emailVerificationError =
                  'This email is waiting for admin approval. Please wait or contact support.';
            } else {
              _emailVerificationError = errorMsg;
            }
            _fieldErrors['email'] = _emailVerificationError;
          } else {
            _emailVerificationError = null;
            _fieldErrors['email'] = null;
          }
        } else {
          _emailVerificationError = null;
        }
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _isVerifyingEmail = false;
          _emailVerificationError = null;
        });
      }
    }
  }

  @override
  void dispose() {
    _emailDebounceTimer?.cancel();
    _fadeController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _streetAddressController.dispose();
    _cityController.dispose();
    _provinceController.dispose();
    _vehicleTypeController.dispose();
    _vehicleNumberController.dispose();
    _driversLicenseController.dispose();
    _validIdController.dispose();
    _riderValidIdController.dispose();
    _buyerTermsController.dispose();
    _riderTermsController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _selectRole(String role) {
    setState(() {
      _selectedRole = role;
      if (_currentStep == 1) {
        Future.delayed(const Duration(milliseconds: 300), _nextStep);
      }
    });
  }

  void _goToStep(int step) {
    _fadeController.reset();
    setState(() {
      _currentStep = step;
      _errorMessage = null;
    });
    _fadeController.forward();
    _scrollToTop();
  }

  void _scrollToTop() {
    _scrollController.animateTo(
      0,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  void _nextStep() {
    if (_validateCurrentStep()) {
      if (_currentStep < _totalSteps) {
        _goToStep(_currentStep + 1);
      }
    } else {
      _scrollToTop();
    }
  }

  void _previousStep() {
    if (_currentStep > 1) {
      _goToStep(_currentStep - 1);
    }
  }

  String? _validateEmail(String email) {
    email = email.trim();
    if (email.isEmpty) return 'Email is required';
    final emailRegex =
        RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    if (!emailRegex.hasMatch(email)) return 'Please enter a valid email';
    return null;
  }

  String? _validatePhone(String phone) {
    phone = phone.trim();
    if (phone.isEmpty) return 'Phone number is required';
    if (phone.length != 11) return 'Phone must be exactly 11 digits';
    if (!phone.startsWith('09')) return 'Phone must start with 09';
    if (!RegExp(r'^\d+$').hasMatch(phone))
      return 'Phone must contain only digits';
    return null;
  }

  String? _validatePassword(String password) {
    if (password.isEmpty) return 'Password is required';
    if (password.length < 6) return 'Password must be at least 6 characters';
    if (password.length > 50) return 'Password must be less than 50 characters';
    return null;
  }

  String? _validateName(String name, String fieldName) {
    name = name.trim();
    if (name.isEmpty) return '$fieldName is required';
    if (name.length < 2) return '$fieldName must be at least 2 characters';
    if (name.length > 50) return '$fieldName must be less than 50 characters';
    if (!RegExp(r"^[a-zA-Z '-]+$").hasMatch(name)) {
      return '$fieldName can only contain letters, spaces, hyphens, and apostrophes';
    }
    return null;
  }

  Future<List<_PsgcOption>> _fetchPsgcList(String url) async {
    final response = await http.get(Uri.parse(url));
    if (response.statusCode != 200) {
      throw Exception('Failed to load address list');
    }
    final data = jsonDecode(response.body);
    if (data is! List) return [];
    return data
        .whereType<Map<String, dynamic>>()
        .map(_PsgcOption.fromJson)
        .where((item) => item.code.isNotEmpty && item.name.isNotEmpty)
        .toList();
  }

  Future<void> _loadRegions() async {
    if (_isLoadingRegions) return;
    setState(() => _isLoadingRegions = true);
    try {
      const url = 'https://psgc.gitlab.io/api/regions/';
      final regions = await _fetchPsgcList(url);
      setState(() => _regions = regions);
    } catch (_) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Unable to load regions. Please try again.';
        });
      }
    } finally {
      if (mounted) setState(() => _isLoadingRegions = false);
    }
  }

  Future<List<_PsgcOption>> _loadProvinces(String regionCode) async {
    if (_provinceCache.containsKey(regionCode))
      return _provinceCache[regionCode] ?? [];
    final url =
        'https://psgc.gitlab.io/api/regions/${Uri.encodeComponent(regionCode)}/provinces/';
    final provinces = await _fetchPsgcList(url);
    _provinceCache[regionCode] = provinces;
    return provinces;
  }

  Future<List<_PsgcOption>> _loadCities(String provinceCode) async {
    if (_cityCache.containsKey(provinceCode))
      return _cityCache[provinceCode] ?? [];
    final url =
        'https://psgc.gitlab.io/api/provinces/${Uri.encodeComponent(provinceCode)}/cities-municipalities/';
    final cities = await _fetchPsgcList(url);
    _cityCache[provinceCode] = cities;
    return cities;
  }

  Future<List<_PsgcOption>> _loadBarangays(String cityCode) async {
    if (_barangayCache.containsKey(cityCode))
      return _barangayCache[cityCode] ?? [];
    final url =
        'https://psgc.gitlab.io/api/cities-municipalities/${Uri.encodeComponent(cityCode)}/barangays/';
    final barangays = await _fetchPsgcList(url);
    _barangayCache[cityCode] = barangays;
    return barangays;
  }

  bool _validateCurrentStep() {
    setState(() => _errorMessage = null);
    switch (_currentStep) {
      case 1:
        return true;
      case 2:
        _fieldErrors.updateAll((key, value) => null);
        bool hasErrors = false;
        final firstNameError =
            _validateName(_firstNameController.text, 'First name');
        if (firstNameError != null) {
          _fieldErrors['firstName'] = firstNameError;
          hasErrors = true;
        }
        final lastNameError =
            _validateName(_lastNameController.text, 'Last name');
        if (lastNameError != null) {
          _fieldErrors['lastName'] = lastNameError;
          hasErrors = true;
        }
        final emailError = _validateEmail(_emailController.text);
        if (emailError != null) {
          _fieldErrors['email'] = emailError;
          hasErrors = true;
        }
        if (_emailVerificationError != null) {
          _fieldErrors['email'] = _emailVerificationError;
          hasErrors = true;
        }
        final phoneError = _validatePhone(_phoneController.text);
        if (phoneError != null) {
          _fieldErrors['phone'] = phoneError;
          hasErrors = true;
        }
        final passwordError = _validatePassword(_passwordController.text);
        if (passwordError != null) {
          _fieldErrors['password'] = passwordError;
          hasErrors = true;
        }
        if (_confirmPasswordController.text.isEmpty) {
          _fieldErrors['confirmPassword'] = 'Please confirm your password';
          hasErrors = true;
        } else if (_passwordController.text !=
            _confirmPasswordController.text) {
          _fieldErrors['confirmPassword'] = 'Passwords do not match';
          hasErrors = true;
        }
        if (hasErrors) {
          setState(() {});
          return false;
        }
        return true;
      case 3:
        if (_streetAddressController.text.trim().isEmpty) {
          setState(() => _errorMessage = 'Street address is required');
          return false;
        }
        if (_selectedRole == 'buyer') {
          if (_selectedRegionCode == null ||
              _selectedProvinceCode == null ||
              _selectedCityCode == null ||
              _selectedBarangayCode == null) {
            setState(() => _errorMessage = 'Complete your address selection');
            return false;
          }
          if (!_buyerTermsAccepted) {
            setState(() => _errorMessage = 'Please accept the buyer terms');
            return false;
          }
          return true;
        }
        if (_vehicleTypeController.text.isEmpty) {
          setState(() => _errorMessage = 'Vehicle type is required');
          return false;
        }
        if (_vehicleNumberController.text.isEmpty) {
          setState(() => _errorMessage = 'Vehicle plate number is required');
          return false;
        }
        if (_selectedRiderRegionCode == null ||
            _selectedRiderProvinceCode == null ||
            _selectedRiderCityCode == null ||
            _selectedRiderBarangayCode == null) {
          setState(() => _errorMessage = 'Complete your address selection');
          return false;
        }
        if (!_riderTermsAccepted) {
          setState(() => _errorMessage = 'Please accept the rider terms');
          return false;
        }
        return true;
      default:
        return false;
    }
  }

  Future<void> _submitRegistration() async {
    if (!_validateCurrentStep()) {
      _scrollToTop();
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      String nameByCode(List<_PsgcOption> options, String? code) {
        if (code == null) return '';
        for (final option in options) {
          if (option.code == code) return option.name;
        }
        return '';
      }

      final isBuyer = _selectedRole == 'buyer';
      final selectedRegionCode =
          isBuyer ? _selectedRegionCode : _selectedRiderRegionCode;
      final selectedProvinceCode =
          isBuyer ? _selectedProvinceCode : _selectedRiderProvinceCode;
      final selectedCityCode =
          isBuyer ? _selectedCityCode : _selectedRiderCityCode;
      final selectedBarangayCode =
          isBuyer ? _selectedBarangayCode : _selectedRiderBarangayCode;

      final selectedRegionName = nameByCode(_regions, selectedRegionCode);
      final provinceOptions = selectedRegionCode == null
          ? <_PsgcOption>[]
          : (_provinceCache[selectedRegionCode] ?? <_PsgcOption>[]);
      final selectedProvinceName =
          nameByCode(provinceOptions, selectedProvinceCode);
      final cityOptions = selectedProvinceCode == null
          ? <_PsgcOption>[]
          : (_cityCache[selectedProvinceCode] ?? <_PsgcOption>[]);
      final selectedCityName = nameByCode(cityOptions, selectedCityCode);
      final barangayOptions = selectedCityCode == null
          ? <_PsgcOption>[]
          : (_barangayCache[selectedCityCode] ?? <_PsgcOption>[]);
      final selectedBarangayName =
          nameByCode(barangayOptions, selectedBarangayCode);

      final addressParts = <String>[
        _streetAddressController.text.trim(),
        selectedBarangayName,
        selectedCityName,
        selectedProvinceName,
        selectedRegionName,
      ].where((part) => part.isNotEmpty).toList();

      final body = {
        'first_name': _firstNameController.text.trim(),
        'last_name': _lastNameController.text.trim(),
        'email': _emailController.text.trim(),
        'phone': _phoneController.text.trim(),
        'password': _passwordController.text,
        'role': _selectedRole,
        'street_address': _streetAddressController.text.trim(),
        'barangay': selectedBarangayName,
        'city': selectedCityName,
        'province': selectedProvinceName,
        'region': selectedRegionName,
        'address': addressParts.join(', '),
      };

      if (_selectedRole == 'rider') {
        body['vehicle_type'] = _vehicleTypeController.text.trim();
        body['vehicle_number'] = _vehicleNumberController.text.trim();
      }

      final result = await ApiService.register(body);
      if (mounted) {
        if (result['message'] != null) {
          Navigator.pushAndRemoveUntil(
            context,
            MaterialPageRoute(
              builder: (context) => PendingApprovalScreen(
                email: _emailController.text.trim(),
                role: _selectedRole,
              ),
            ),
            (route) => false,
          );
        } else {
          setState(() {
            _errorMessage = result['error'] ?? 'Registration failed';
            _isLoading = false;
          });
          _scrollToTop();
        }
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().contains('ApiException')
            ? e.toString().replaceFirst('ApiException: ', '')
            : 'Connection error. Please try again.';
        _isLoading = false;
      });
      _scrollToTop();
    }
  }

  // ─── UI WIDGETS ───────────────────────────────────────────────────────────

  Widget _buildStepIndicator() {
    final labels = ['Role', 'Info', 'Details'];
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(_totalSteps, (index) {
        final step = index + 1;
        final isCompleted = step < _currentStep;
        final isActive = step == _currentStep;

        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (index > 0)
              Container(
                width: 36,
                height: 2,
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isCompleted
                        ? [goldColor, goldColor]
                        : [Colors.white24, Colors.white12],
                  ),
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
            GestureDetector(
              onTap: isCompleted ? () => _goToStep(step) : null,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isCompleted
                          ? goldColor
                          : isActive
                              ? Colors.white
                              : Colors.white.withValues(alpha: 0.15),
                      border: Border.all(
                        color: isActive ? goldColor : Colors.transparent,
                        width: 2,
                      ),
                      boxShadow: isActive
                          ? [
                              BoxShadow(
                                color: goldColor.withValues(alpha: 0.5),
                                blurRadius: 8,
                                spreadRadius: 1,
                              )
                            ]
                          : null,
                    ),
                    child: Center(
                      child: isCompleted
                          ? const Icon(Icons.check,
                              color: primaryBlue, size: 15)
                          : Text(
                              '$step',
                              style: TextStyle(
                                color: isActive
                                    ? primaryBlue
                                    : Colors.white.withValues(alpha: 0.5),
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    labels[index],
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                      color: isActive
                          ? goldColor
                          : isCompleted
                              ? Colors.white70
                              : Colors.white38,
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      }),
    );
  }

  // ─── STEP 1: ROLE SELECTION ───────────────────────────────────────────────
  Widget _buildStep1RoleSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStepIndicator(),
        const SizedBox(height: 20),
        const Text(
          'Choose Your Role',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: textWhite,
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'How will you use Kids Kingdom?',
          style: TextStyle(fontSize: 12, color: textWhite70),
        ),
        const SizedBox(height: 16),
        // Taller side-by-side role cards
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _buildRoleCard(
                emoji: '🛍️',
                icon: Icons.shopping_bag_outlined,
                title: 'Buyer',
                description: 'Shop amazing\nkids products',
                isSelected: _selectedRole == 'buyer',
                gradientColors: [
                  const Color(0xFF4776E6),
                  const Color(0xFF8E54E9)
                ],
                onTap: () => _selectRole('buyer'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildRoleCard(
                emoji: '🛵',
                icon: Icons.delivery_dining,
                title: 'Rider',
                description: 'Deliver orders\nand earn more',
                isSelected: _selectedRole == 'rider',
                gradientColors: [
                  const Color(0xFF11998E),
                  const Color(0xFF38EF7D)
                ],
                onTap: () => _selectRole('rider'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRoleCard({
    required String emoji,
    required IconData icon,
    required String title,
    required String description,
    required bool isSelected,
    required VoidCallback onTap,
    required List<Color> gradientColors,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        height: 175,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
        decoration: BoxDecoration(
          gradient: isSelected
              ? LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: gradientColors,
                )
              : null,
          color: isSelected ? null : Colors.white.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: isSelected
                ? Colors.white.withValues(alpha: 0.5)
                : Colors.white.withValues(alpha: 0.18),
            width: isSelected ? 2 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: gradientColors[0].withValues(alpha: 0.45),
                    blurRadius: 18,
                    offset: const Offset(0, 6),
                  ),
                ]
              : [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.15),
                    blurRadius: 8,
                    offset: const Offset(0, 3),
                  ),
                ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Emoji with subtle background circle
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isSelected
                    ? Colors.white.withValues(alpha: 0.2)
                    : Colors.white.withValues(alpha: 0.07),
              ),
              child: Center(
                child: Text(emoji, style: const TextStyle(fontSize: 28)),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: isSelected ? Colors.white : textWhite70,
                letterSpacing: 0.3,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              description,
              style: TextStyle(
                fontSize: 11,
                color: isSelected
                    ? Colors.white.withValues(alpha: 0.85)
                    : Colors.white38,
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            // Selection indicator dot
            AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              width: isSelected ? 24 : 8,
              height: 4,
              decoration: BoxDecoration(
                color: isSelected
                    ? Colors.white.withValues(alpha: 0.9)
                    : Colors.white.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── STEP 2: PERSONAL INFO ────────────────────────────────────────────────
  Widget _buildStep2PersonalInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Role badge
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: _selectedRole == 'buyer'
                  ? [const Color(0xFF4776E6), const Color(0xFF8E54E9)]
                  : [const Color(0xFF11998E), const Color(0xFF38EF7D)],
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _selectedRole == 'buyer' ? '🛍️' : '🛵',
                style: const TextStyle(fontSize: 12),
              ),
              const SizedBox(width: 5),
              Text(
                _selectedRole == 'buyer' ? 'Buyer' : 'Rider',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        const Text(
          'Personal Information',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: textWhite,
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 2),
        const Text(
          'Tell us a bit about yourself',
          style: TextStyle(fontSize: 11, color: textWhite70),
        ),
        const SizedBox(height: 14),
        Row(
          children: [
            Expanded(
              child: _buildTextField(
                label: 'First Name',
                hint: 'John',
                controller: _firstNameController,
                fieldErrorKey: 'firstName',
                prefixIcon: Icons.person_outline,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildTextField(
                label: 'Last Name',
                hint: 'Doe',
                controller: _lastNameController,
                fieldErrorKey: 'lastName',
                prefixIcon: Icons.person_outline,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        _buildEmailField(),
        const SizedBox(height: 10),
        _buildTextField(
          label: 'Phone Number',
          hint: '09123456789',
          controller: _phoneController,
          fieldErrorKey: 'phone',
          keyboardType: TextInputType.phone,
          prefixIcon: Icons.phone_outlined,
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
            LengthLimitingTextInputFormatter(11),
          ],
          onChanged: (value) {
            if (!value.startsWith('09') && value.isNotEmpty) {
              _phoneController.text =
                  '09' + value.replaceFirst(RegExp(r'^0+'), '');
              _phoneController.selection = TextSelection.fromPosition(
                TextPosition(offset: _phoneController.text.length),
              );
            }
          },
        ),
        const SizedBox(height: 2),
        const Padding(
          padding: EdgeInsets.only(left: 4),
          child: Text(
            'Must start with 09 and be 11 digits',
            style: TextStyle(fontSize: 9, color: Colors.white38),
          ),
        ),
        const SizedBox(height: 10),
        _buildPasswordField(
          label: 'Password',
          hint: 'Create a strong password',
          controller: _passwordController,
          fieldErrorKey: 'password',
          isPasswordField: true,
        ),
        _buildPasswordStrengthIndicator(),
        const SizedBox(height: 10),
        _buildPasswordField(
          label: 'Confirm Password',
          hint: 'Re-enter your password',
          controller: _confirmPasswordController,
          fieldErrorKey: 'confirmPassword',
          isPasswordField: false,
        ),
      ],
    );
  }

  // ─── STEP 3: COMPLETE DETAILS ─────────────────────────────────────────────
  Widget _buildStep3CompleteDetails() {
    final buyerProvinces = _selectedRegionCode == null
        ? <_PsgcOption>[]
        : _provinceCache[_selectedRegionCode!] ?? <_PsgcOption>[];
    final buyerCities = _selectedProvinceCode == null
        ? <_PsgcOption>[]
        : _cityCache[_selectedProvinceCode!] ?? <_PsgcOption>[];
    final buyerBarangays = _selectedCityCode == null
        ? <_PsgcOption>[]
        : _barangayCache[_selectedCityCode!] ?? <_PsgcOption>[];

    final riderProvinces = _selectedRiderRegionCode == null
        ? <_PsgcOption>[]
        : _provinceCache[_selectedRiderRegionCode!] ?? <_PsgcOption>[];
    final riderCities = _selectedRiderProvinceCode == null
        ? <_PsgcOption>[]
        : _cityCache[_selectedRiderProvinceCode!] ?? <_PsgcOption>[];
    final riderBarangays = _selectedRiderCityCode == null
        ? <_PsgcOption>[]
        : _barangayCache[_selectedRiderCityCode!] ?? <_PsgcOption>[];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Complete Your Details',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: textWhite,
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 2),
        const Text(
          'Almost there! Fill in your address info.',
          style: TextStyle(fontSize: 11, color: textWhite70),
        ),
        const SizedBox(height: 10),
        _buildSectionLabel('📍 Address Information'),
        const SizedBox(height: 8),
        if (_isLoadingRegions)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: const LinearProgressIndicator(
                backgroundColor: Colors.white24,
                valueColor: AlwaysStoppedAnimation<Color>(goldColor),
              ),
            ),
          ),
        _buildDropdown(
          label: 'Region',
          value: _selectedRole == 'buyer'
              ? _selectedRegionCode
              : _selectedRiderRegionCode,
          options: _regions,
          onChanged: (value) async {
            if (_selectedRole == 'buyer') {
              setState(() {
                _selectedRegionCode = value;
                _selectedProvinceCode = null;
                _selectedCityCode = null;
                _selectedBarangayCode = null;
                _provinceController.text = '';
                _cityController.text = '';
              });
              if (value != null) await _loadProvinces(value);
            } else {
              setState(() {
                _selectedRiderRegionCode = value;
                _selectedRiderProvinceCode = null;
                _selectedRiderCityCode = null;
                _selectedRiderBarangayCode = null;
                _provinceController.text = '';
                _cityController.text = '';
              });
              if (value != null) await _loadProvinces(value);
            }
            if (mounted) setState(() {});
          },
        ),
        const SizedBox(height: 10),
        _buildDropdown(
          label: 'Province',
          value: _selectedRole == 'buyer'
              ? _selectedProvinceCode
              : _selectedRiderProvinceCode,
          options: _selectedRole == 'buyer' ? buyerProvinces : riderProvinces,
          enabled: (_selectedRole == 'buyer'
                  ? _selectedRegionCode
                  : _selectedRiderRegionCode) !=
              null,
          onChanged: (value) async {
            if (_selectedRole == 'buyer') {
              setState(() {
                _selectedProvinceCode = value;
                _selectedCityCode = null;
                _selectedBarangayCode = null;
                _cityController.text = '';
              });
              if (value != null) {
                final selected = buyerProvinces.firstWhere(
                  (opt) => opt.code == value,
                  orElse: () => const _PsgcOption(code: '', name: ''),
                );
                if (selected.name.isNotEmpty)
                  _provinceController.text = selected.name;
                await _loadCities(value);
              }
            } else {
              setState(() {
                _selectedRiderProvinceCode = value;
                _selectedRiderCityCode = null;
                _selectedRiderBarangayCode = null;
                _cityController.text = '';
              });
              if (value != null) {
                final selected = riderProvinces.firstWhere(
                  (opt) => opt.code == value,
                  orElse: () => const _PsgcOption(code: '', name: ''),
                );
                if (selected.name.isNotEmpty)
                  _provinceController.text = selected.name;
                await _loadCities(value);
              }
            }
            if (mounted) setState(() {});
          },
        ),
        const SizedBox(height: 10),
        _buildDropdown(
          label: 'City / Municipality',
          value: _selectedRole == 'buyer'
              ? _selectedCityCode
              : _selectedRiderCityCode,
          options: _selectedRole == 'buyer' ? buyerCities : riderCities,
          enabled: (_selectedRole == 'buyer'
                  ? _selectedProvinceCode
                  : _selectedRiderProvinceCode) !=
              null,
          onChanged: (value) async {
            if (_selectedRole == 'buyer') {
              setState(() {
                _selectedCityCode = value;
                _selectedBarangayCode = null;
              });
              if (value != null) {
                final selected = buyerCities.firstWhere(
                  (opt) => opt.code == value,
                  orElse: () => const _PsgcOption(code: '', name: ''),
                );
                if (selected.name.isNotEmpty)
                  _cityController.text = selected.name;
                await _loadBarangays(value);
              }
            } else {
              setState(() {
                _selectedRiderCityCode = value;
                _selectedRiderBarangayCode = null;
              });
              if (value != null) {
                final selected = riderCities.firstWhere(
                  (opt) => opt.code == value,
                  orElse: () => const _PsgcOption(code: '', name: ''),
                );
                if (selected.name.isNotEmpty)
                  _cityController.text = selected.name;
                await _loadBarangays(value);
              }
            }
            if (mounted) setState(() {});
          },
        ),
        const SizedBox(height: 10),
        _buildDropdown(
          label: 'Barangay',
          value: _selectedRole == 'buyer'
              ? _selectedBarangayCode
              : _selectedRiderBarangayCode,
          options: _selectedRole == 'buyer' ? buyerBarangays : riderBarangays,
          enabled: (_selectedRole == 'buyer'
                  ? _selectedCityCode
                  : _selectedRiderCityCode) !=
              null,
          onChanged: (value) {
            setState(() {
              if (_selectedRole == 'buyer') {
                _selectedBarangayCode = value;
              } else {
                _selectedRiderBarangayCode = value;
              }
            });
          },
        ),
        const SizedBox(height: 10),
        _buildTextField(
          label: 'Street Address',
          hint: 'House number, street name',
          controller: _streetAddressController,
          prefixIcon: Icons.home_outlined,
        ),
        if (_selectedRole == 'buyer') ...[
          const SizedBox(height: 14),
          _buildSectionLabel('🪪 Verification Information'),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.07),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildTextField(
                  label: 'Valid ID Type',
                  hint: 'e.g. Passport, Driver License',
                  controller: _validIdController,
                  prefixIcon: Icons.badge_outlined,
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(10),
                    border:
                        Border.all(color: Colors.white.withValues(alpha: 0.15)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.upload_file, color: Colors.white38, size: 18),
                      SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Upload Valid ID (Not available on mobile)',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.white38,
                            fontStyle: FontStyle.italic,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 2,
                          softWrap: true,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _buildTermsSection(
            title: 'Buyer Terms and Conditions',
            controller: _buyerTermsController,
            isRead: _buyerTermsRead,
            isAccepted: _buyerTermsAccepted,
            onChanged: (value) {
              setState(() => _buyerTermsAccepted = value ?? false);
            },
            body:
                'By creating a buyer account, you agree to provide accurate information, '
                'keep your account secure, and use the platform responsibly. Orders placed '
                'are subject to availability and delivery schedules. Returns and refunds '
                'follow Kids Kingdom policies. You also agree to receive service updates '
                'related to your orders and account.',
          ),
        ],
        if (_selectedRole == 'rider') ...[
          const SizedBox(height: 14),
          _buildSectionLabel('🛵 Vehicle Information'),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.07),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildDropdown(
                  label: 'Vehicle Type',
                  value: _vehicleTypeController.text.isEmpty
                      ? null
                      : _vehicleTypeController.text,
                  options: const [
                    _PsgcOption(code: 'Motorcycle', name: 'Motorcycle'),
                    _PsgcOption(code: 'Car', name: 'Car'),
                    _PsgcOption(code: 'Van', name: 'Van'),
                    _PsgcOption(code: 'Truck', name: 'Truck'),
                  ],
                  onChanged: (value) {
                    setState(() => _vehicleTypeController.text = value ?? '');
                  },
                ),
                const SizedBox(height: 8),
                _buildTextField(
                  label: 'Plate Number',
                  hint: 'ABC-123',
                  controller: _vehicleNumberController,
                  prefixIcon: Icons.directions_car_outlined,
                ),
                const SizedBox(height: 8),
                _buildTextField(
                  label: "Driver's License",
                  hint: 'License number',
                  controller: _driversLicenseController,
                  prefixIcon: Icons.credit_card_outlined,
                ),
                const SizedBox(height: 8),
                _buildTextField(
                  label: 'Valid Government ID Type',
                  hint: 'e.g. UMID, Passport',
                  controller: _riderValidIdController,
                  prefixIcon: Icons.badge_outlined,
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(10),
                    border:
                        Border.all(color: Colors.white.withValues(alpha: 0.15)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.upload_file, color: Colors.white38, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Upload Government ID (Not available on mobile)',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white38,
                            fontStyle: FontStyle.italic,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 2,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _buildTermsSection(
            title: 'Rider Terms and Conditions',
            controller: _riderTermsController,
            isRead: _riderTermsRead,
            isAccepted: _riderTermsAccepted,
            onChanged: (value) {
              setState(() => _riderTermsAccepted = value ?? false);
            },
            body:
                'By registering as a rider, you confirm you have a valid license and '
                'will follow all delivery guidelines. You agree to keep your vehicle '
                'in safe condition, deliver orders promptly, and protect customer data. '
                'Violations may result in suspension. You also agree to receive service '
                'updates related to assignments and account status.',
          ),
        ],
      ],
    );
  }

  Widget _buildSectionLabel(String text) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 13,
        fontWeight: FontWeight.w700,
        color: textWhite,
        letterSpacing: 0.2,
      ),
    );
  }

  Widget _buildEmailField() {
    final hasError =
        _fieldErrors['email'] != null || _emailVerificationError != null;
    final errorMessage = _fieldErrors['email'] ?? _emailVerificationError;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Email Address',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: textWhite70,
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            hintText: 'your@email.com',
            hintStyle: const TextStyle(color: Colors.white38, fontSize: 13),
            prefixIcon: Icon(
              Icons.email_outlined,
              color: hasError ? errorRed : Colors.white54,
              size: 19,
            ),
            suffixIcon: _isVerifyingEmail
                ? const Padding(
                    padding: EdgeInsets.all(12),
                    child: SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(goldColor),
                      ),
                    ),
                  )
                : hasError
                    ? const Icon(Icons.error_outline, color: errorRed, size: 19)
                    : (_emailController.text.isNotEmpty &&
                            _emailVerificationError == null &&
                            _fieldErrors['email'] == null)
                        ? const Icon(Icons.check_circle,
                            color: Color(0xFF38EF7D), size: 19)
                        : null,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : Colors.white24,
                width: hasError ? 1.5 : 1,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : Colors.white24,
                width: hasError ? 1.5 : 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : goldColor,
                width: 1.5,
              ),
            ),
            filled: true,
            fillColor: hasError
                ? errorRed.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.08),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
        ),
        if (hasError) ...[
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 4),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: errorRed, size: 12),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    errorMessage ?? '',
                    style: const TextStyle(
                      fontSize: 10,
                      color: errorRed,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ] else if (_isVerifyingEmail) ...[
          const SizedBox(height: 4),
          const Padding(
            padding: EdgeInsets.only(left: 4),
            child: Row(
              children: [
                Icon(Icons.hourglass_empty, color: goldColor, size: 12),
                SizedBox(width: 4),
                Text(
                  'Verifying email address...',
                  style: TextStyle(
                    fontSize: 10,
                    color: goldColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildTextField({
    required String label,
    required String hint,
    required TextEditingController controller,
    String? fieldErrorKey,
    IconData? prefixIcon,
    TextInputType? keyboardType,
    List<TextInputFormatter>? inputFormatters,
    Function(String)? onChanged,
  }) {
    final hasError =
        fieldErrorKey != null && _fieldErrors[fieldErrorKey] != null;
    final errorMessage =
        fieldErrorKey != null ? _fieldErrors[fieldErrorKey] : null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: textWhite70,
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          inputFormatters: inputFormatters,
          onChanged: onChanged,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: Colors.white38, fontSize: 13),
            prefixIcon: prefixIcon != null
                ? Icon(prefixIcon,
                    color: hasError ? errorRed : Colors.white54, size: 19)
                : null,
            suffixIcon: hasError
                ? const Icon(Icons.error_outline, color: errorRed, size: 19)
                : null,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : Colors.white24,
                width: hasError ? 1.5 : 1,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : Colors.white24,
                width: hasError ? 1.5 : 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError ? errorRed : goldColor,
                width: 1.5,
              ),
            ),
            filled: true,
            fillColor: hasError
                ? errorRed.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.08),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
        ),
        if (hasError) ...[
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 4),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: errorRed, size: 12),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    errorMessage ?? '',
                    style: const TextStyle(
                      fontSize: 10,
                      color: errorRed,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildPasswordField({
    required String label,
    required String hint,
    required TextEditingController controller,
    String? fieldErrorKey,
    bool? isPasswordField,
  }) {
    final hasError =
        fieldErrorKey != null && _fieldErrors[fieldErrorKey] != null;
    final errorMessage =
        fieldErrorKey != null ? _fieldErrors[fieldErrorKey] : null;
    final bool showPassword = (isPasswordField == true)
        ? _showPassword
        : (isPasswordField == false)
            ? _showConfirmPassword
            : _showPassword;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: textWhite70,
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          obscureText: !showPassword,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: Colors.white38, fontSize: 13),
            prefixIcon: Icon(Icons.lock_outline,
                color: hasError ? errorRed : Colors.white54, size: 19),
            suffixIcon: GestureDetector(
              onTap: () {
                setState(() {
                  if (isPasswordField == true) {
                    _showPassword = !_showPassword;
                  } else if (isPasswordField == false) {
                    _showConfirmPassword = !_showConfirmPassword;
                  }
                });
              },
              child: Icon(
                showPassword ? Icons.visibility : Icons.visibility_off,
                color: Colors.white38,
                size: 19,
              ),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                  color: hasError ? errorRed : Colors.white24,
                  width: hasError ? 1.5 : 1),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                  color: hasError ? errorRed : Colors.white24,
                  width: hasError ? 1.5 : 1),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                  color: hasError ? errorRed : goldColor, width: 1.5),
            ),
            filled: true,
            fillColor: hasError
                ? errorRed.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.08),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
        ),
        if (hasError) ...[
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 4),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: errorRed, size: 12),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    errorMessage ?? '',
                    style: const TextStyle(
                      fontSize: 10,
                      color: errorRed,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildPasswordStrengthIndicator() {
    Color barColor;
    String strengthText;
    if (_passwordStrength == 0) {
      barColor = Colors.transparent;
      strengthText = '';
    } else if (_passwordStrength < 5) {
      barColor = errorRed;
      strengthText = 'Password must meet all requirements';
    } else {
      barColor = const Color(0xFF38EF7D);
      strengthText = '';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 5),
        ClipRRect(
          borderRadius: BorderRadius.circular(3),
          child: Container(
            height: 3,
            width: double.infinity,
            color: Colors.white12,
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: _passwordStrength / 5,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                color: barColor,
              ),
            ),
          ),
        ),
        const SizedBox(height: 3),
        const Text(
          'At least 10 chars with uppercase, lowercase, number & special character',
          style: TextStyle(fontSize: 9, color: Colors.white38),
        ),
        if (strengthText.isNotEmpty) ...[
          const SizedBox(height: 2),
          Row(
            children: [
              const Icon(Icons.warning_amber_rounded,
                  color: errorRed, size: 11),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  strengthText,
                  style: const TextStyle(
                    fontSize: 9,
                    color: errorRed,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildDropdown({
    required String label,
    required String? value,
    required List<_PsgcOption> options,
    required ValueChanged<String?> onChanged,
    bool enabled = true,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: textWhite70,
          ),
        ),
        const SizedBox(height: 6),
        DropdownButtonFormField<String>(
          initialValue: value,
          isExpanded: true,
          dropdownColor: const Color(0xFF1E3A6E),
          style: const TextStyle(color: Colors.white, fontSize: 14),
          icon: const Icon(Icons.keyboard_arrow_down, color: Colors.white54),
          items: options
              .map(
                (opt) => DropdownMenuItem<String>(
                  value: opt.code,
                  child: Text(opt.name,
                      style: const TextStyle(color: Colors.white)),
                ),
              )
              .toList(),
          onChanged: enabled ? onChanged : null,
          decoration: InputDecoration(
            hintText: 'Select $label',
            hintStyle: const TextStyle(color: Colors.white38, fontSize: 13),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.white24),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.white24),
            ),
            disabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.white12),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: goldColor, width: 1.5),
            ),
            filled: true,
            fillColor: enabled
                ? Colors.white.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.03),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildTermsSection({
    required String title,
    required ScrollController controller,
    required bool isRead,
    required bool isAccepted,
    required ValueChanged<bool?> onChanged,
    required String body,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: textWhite,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            height: 90,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.white12),
            ),
            child: SingleChildScrollView(
              controller: controller,
              child: Text(
                body,
                style: const TextStyle(
                  fontSize: 11,
                  color: textWhite70,
                  height: 1.4,
                ),
              ),
            ),
          ),
          if (!isRead) ...[
            const SizedBox(height: 4),
            const Row(
              children: [
                Icon(Icons.arrow_downward, color: Colors.white38, size: 11),
                SizedBox(width: 4),
                Expanded(
                  child: Text(
                    'Scroll to the bottom to enable the checkbox',
                    style: TextStyle(fontSize: 9, color: Colors.white38),
                  ),
                ),
              ],
            ),
          ],
          Theme(
            data: ThemeData(
              checkboxTheme: CheckboxThemeData(
                fillColor: WidgetStateProperty.resolveWith((states) {
                  if (states.contains(WidgetState.selected)) return goldColor;
                  return Colors.transparent;
                }),
                checkColor: WidgetStateProperty.all(primaryBlue),
                side: const BorderSide(color: Colors.white38),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
            child: CheckboxListTile(
              value: isAccepted,
              onChanged: isRead ? onChanged : null,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              title: Text(
                'I agree to the terms and conditions',
                style: TextStyle(
                  fontSize: 11,
                  color: isRead ? textWhite : Colors.white38,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─── CONTINUE BUTTON ──────────────────────────────────────────────────────
  Widget _buildContinueButton() {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton(
        onPressed: _isLoading
            ? null
            : (_currentStep == _totalSteps ? _submitRegistration : _nextStep),
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
                color: goldColor.withValues(alpha: 0.35),
                blurRadius: 14,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Container(
            alignment: Alignment.center,
            child: _isLoading
                ? const SizedBox(
                    height: 22,
                    width: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      valueColor: AlwaysStoppedAnimation<Color>(primaryBlue),
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _currentStep == _totalSteps
                            ? '🎉  Complete Registration'
                            : 'Continue',
                        style: const TextStyle(
                          color: primaryBlue,
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                          letterSpacing: 0.5,
                        ),
                      ),
                      if (_currentStep != _totalSteps) ...[
                        const SizedBox(width: 6),
                        const Icon(Icons.arrow_forward_rounded,
                            color: primaryBlue, size: 18),
                      ],
                    ],
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildSignInLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Text(
          'Already have an account? ',
          style: TextStyle(color: Colors.white60, fontSize: 13),
        ),
        GestureDetector(
          onTap: () => Navigator.pushReplacementNamed(context, '/login'),
          child: const Text(
            'Sign In 🚀',
            style: TextStyle(
              color: goldColor,
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
          ),
        ),
      ],
    );
  }

  // ─── HEADER ───────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
          child: Row(
            children: [
              if (_currentStep > 1)
                GestureDetector(
                  onTap: _previousStep,
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                          color: Colors.white.withValues(alpha: 0.2)),
                    ),
                    child: const Icon(Icons.arrow_back_ios_new,
                        color: Colors.white, size: 16),
                  ),
                ),
              Expanded(
                child: Column(
                  children: [
                    SizedBox(
                      height: 88,
                      child: Image.asset(
                        'assets/images/logo_ulit.png',
                        fit: BoxFit.contain,
                        errorBuilder: (context, error, stackTrace) {
                          return const Text(
                            'KIDS KINGDOM',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                              letterSpacing: 2,
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 2),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('✦ ',
                            style: TextStyle(color: goldColor, fontSize: 9)),
                        Text(
                          'Create Account',
                          style: TextStyle(
                            fontSize: 11,
                            color: goldColor,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1.2,
                          ),
                        ),
                        Text(' ✦',
                            style: TextStyle(color: goldColor, fontSize: 9)),
                      ],
                    ),
                  ],
                ),
              ),
              if (_currentStep > 1) const SizedBox(width: 40),
            ],
          ),
        ),
        // Colorful accent bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Row(
            children: [
              Expanded(
                  child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                          color: Colors.yellow,
                          borderRadius: BorderRadius.circular(2)))),
              const SizedBox(width: 4),
              Expanded(
                  child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                          color: Colors.pink,
                          borderRadius: BorderRadius.circular(2)))),
              const SizedBox(width: 4),
              Expanded(
                  child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                          color: Colors.cyan,
                          borderRadius: BorderRadius.circular(2)))),
              const SizedBox(width: 4),
              Expanded(
                  child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(2)))),
              const SizedBox(width: 4),
              Expanded(
                  child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                          color: Colors.green,
                          borderRadius: BorderRadius.circular(2)))),
            ],
          ),
        ),
      ],
    );
  }

  // ─── MAIN BUILD ──────────────────────────────────────────────────────────

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
            // Decorative circles
            Positioned(
              top: -60,
              right: -60,
              child: Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.04),
                ),
              ),
            ),
            Positioned(
              bottom: 100,
              left: -80,
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.03),
                ),
              ),
            ),
            SafeArea(
              child: Column(
                children: [
                  _buildHeader(),
                  const SizedBox(height: 8),

                  // ── STEP 1: Fixed layout, not scrollable ──────────────
                  if (_currentStep == 1)
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          children: [
                            Expanded(
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.08),
                                  borderRadius: BorderRadius.circular(24),
                                  border: Border.all(
                                      color:
                                          Colors.white.withValues(alpha: 0.15)),
                                  boxShadow: [
                                    BoxShadow(
                                      color:
                                          Colors.black.withValues(alpha: 0.3),
                                      blurRadius: 30,
                                      offset: const Offset(0, 10),
                                    ),
                                  ],
                                ),
                                padding: const EdgeInsets.all(18),
                                child: FadeTransition(
                                  opacity: _fadeAnimation,
                                  child: _buildStep1RoleSelection(),
                                ),
                              ),
                            ),
                            const SizedBox(height: 10),
                            _buildSignInLink(),
                            const SizedBox(height: 10),
                          ],
                        ),
                      ),
                    ),

                  // ── STEPS 2 & 3: Scrollable ───────────────────────────
                  if (_currentStep > 1)
                    Expanded(
                      child: SingleChildScrollView(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 4),
                        child: Column(
                          children: [
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.08),
                                borderRadius: BorderRadius.circular(24),
                                border: Border.all(
                                    color:
                                        Colors.white.withValues(alpha: 0.15)),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withValues(alpha: 0.3),
                                    blurRadius: 30,
                                    offset: const Offset(0, 10),
                                  ),
                                ],
                              ),
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Error message
                                  if (_errorMessage != null) ...[
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 12, vertical: 10),
                                      decoration: BoxDecoration(
                                        color: errorRed.withValues(alpha: 0.15),
                                        borderRadius: BorderRadius.circular(10),
                                        border: Border.all(
                                            color: errorRed.withValues(
                                                alpha: 0.4)),
                                      ),
                                      child: Row(
                                        children: [
                                          const Icon(Icons.error_outline,
                                              color: errorRed, size: 16),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(
                                              _errorMessage!,
                                              style: const TextStyle(
                                                  color: errorRed,
                                                  fontSize: 12),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    const SizedBox(height: 10),
                                  ],

                                  // Step indicator
                                  _buildStepIndicator(),
                                  const SizedBox(height: 14),

                                  // Step content — conditional, no IndexedStack
                                  FadeTransition(
                                    opacity: _fadeAnimation,
                                    child: _currentStep == 2
                                        ? _buildStep2PersonalInfo()
                                        : _buildStep3CompleteDetails(),
                                  ),

                                  const SizedBox(height: 16),
                                  _buildContinueButton(),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                            _buildSignInLink(),
                            const SizedBox(height: 10),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
