import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../utils/profile_photo_helper.dart';
import '../../providers/auth_provider.dart';
import '../../providers/cart_provider.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import 'liked_products_screen.dart';

/// Buyer Profile Screen
class ProfileScreen extends StatefulWidget {
  final bool showAddressSetup;
  const ProfileScreen({super.key, this.showAddressSetup = false});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen>
    with SingleTickerProviderStateMixin {
  List<dynamic> _addresses = [];
  bool _isUploadingImage = false;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // Theme colors
  static const Color _primaryDark = Color(0xFF1a2f6b);
  static const Color _primary = Color(0xFF1e4db7);
  static const Color _primaryLight = Color(0xFF3B6FE0);
  static const Color _bgColor = Color(0xFFF4F6FC);
  static const Color _cardColor = Colors.white;
  static const Color _textDark = Color(0xFF1A1F36);
  static const Color _textMid = Color(0xFF6B7280);

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    );
    _animationController.forward();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _loadProfile();
    });
  }

  Future<void> _loadProfile() async {
    final buyerProvider = context.read<BuyerProvider>();
    buyerProvider.fetchProfile();
    await _fetchAddresses();

    if (widget.showAddressSetup && _addresses.isEmpty && mounted) {
      _showSnackBar(
        'Please add your delivery address to continue.',
      );
      await _showAddAddressSheet();
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Profile data is accessed from context.watch<BuyerProvider>()
    // No local controller needed as profile is display-only
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _fetchAddresses() async {
    try {
      final response =
          await ApiService.request('GET', '/api/v1/buyer/addresses');
      if (response['success'] == true) {
        setState(() {
          _addresses = response['addresses'] ?? [];
        });
      }
    } catch (e) {
      debugPrint('Error fetching addresses: $e');
    }
  }

  Future<void> _pickAndUploadImage() async {
    setState(() => _isUploadingImage = true);
    try {
      final imageUrl =
          await ProfilePhotoHelper.pickAndUploadProfilePhoto(context);
      if (imageUrl == null) return;

      if (mounted) {
        _showSnackBar('Profile image updated successfully', isSuccess: true);
        await context.read<AuthProvider>().refreshUser();
        context.read<BuyerProvider>().fetchProfile();
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Failed to upload image: $e');
      }
    } finally {
      if (mounted) {
        setState(() => _isUploadingImage = false);
      }
    }
  }

  void _showSnackBar(String message, {bool isSuccess = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isSuccess ? LucideIcons.checkCircle : LucideIcons.alertCircle,
              color: Colors.white,
              size: 16,
            ),
            const SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor:
            isSuccess ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  // ─── Add Address Bottom Sheet ───────────────────────────────────────────────

  Future<void> _showAddAddressSheet() async {
    final streetController = TextEditingController();
    final customLabelController = TextEditingController();
    bool isDefault = false;
    String? selectedLabel;
    String? selectedProvince;
    String? selectedProvinceCode;
    String? selectedCity;
    String? selectedCityCode;
    String? selectedBarangay;

    List<dynamic> provinces = [];
    List<dynamic> cities = [];
    List<dynamic> barangays = [];
    bool isLoadingProvinces = true;
    bool isLoadingCities = false;
    bool isLoadingBarangays = false;

    final labelOptions = ['Home', 'Work', 'Office', 'Other'];

    // Fetch provinces on init
    Future<void> fetchProvinces() async {
      try {
        final response = await ApiService.request('GET', '/api/provinces');
        if (response != null && response['result'] != null) {
          provinces = response['result'] as List<dynamic>;
        }
      } catch (e) {
        debugPrint('Error fetching provinces: $e');
      }
    }

    Future<void> fetchCities(String provinceCode) async {
      try {
        final response = await ApiService.request(
          'GET',
          '/api/cities?province_code=$provinceCode',
        );
        if (response != null && response['result'] != null) {
          cities = response['result'] as List<dynamic>;
        }
      } catch (e) {
        debugPrint('Error fetching cities: $e');
      }
    }

    Future<void> fetchBarangays(String cityCode) async {
      try {
        final response = await ApiService.request(
          'GET',
          '/api/barangays?city_code=$cityCode',
        );
        if (response != null && response['result'] != null) {
          barangays = response['result'] as List<dynamic>;
        }
      } catch (e) {
        debugPrint('Error fetching barangays: $e');
      }
    }

    if (!mounted) return;

    await fetchProvinces();
    isLoadingProvinces = false;

    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) {
          return Container(
            decoration: const BoxDecoration(
              color: _cardColor,
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            ),
            padding: EdgeInsets.only(
              left: 16,
              right: 16,
              top: 0,
              bottom: MediaQuery.of(context).viewInsets.bottom + 20,
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Handle bar
                  Center(
                    child: Container(
                      margin: const EdgeInsets.only(top: 12, bottom: 14),
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade300,
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),

                  // Title row - More compact
                  Row(
                    children: [
                      Container(
                        width: 38,
                        height: 38,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [_primaryDark, _primary],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          LucideIcons.mapPin,
                          color: Colors.white,
                          size: 18,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Add New Address',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: _textDark,
                              ),
                            ),
                            Text(
                              'Select location from PSGC',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.grey.shade500,
                              ),
                            ),
                          ],
                        ),
                      ),
                      GestureDetector(
                        onTap: () => Navigator.pop(context, false),
                        child: Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(LucideIcons.x,
                              size: 16, color: _textMid),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 18),

                  // Quick label chips
                  const Text(
                    'Address Type',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _textMid,
                      letterSpacing: 0.4,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: labelOptions.map((label) {
                      final isSelected = selectedLabel == label;
                      return FilterChip(
                        label: Text(label),
                        selected: isSelected,
                        onSelected: (selected) {
                          setSheetState(() {
                            selectedLabel = selected ? label : null;
                          });
                        },
                        backgroundColor: Colors.grey.shade100,
                        selectedColor: _primary.withValues(alpha: 0.15),
                        labelStyle: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: isSelected ? _primary : _textMid,
                        ),
                        side: BorderSide(
                          color: isSelected ? _primary : Colors.transparent,
                          width: 1,
                        ),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 12),

                  // Custom label if "Other"
                  if (selectedLabel == 'Other') ...[
                    _buildInputField(
                      controller: customLabelController,
                      label: 'Custom Label',
                      hint: 'e.g., Vacation Home',
                      icon: LucideIcons.tag,
                    ),
                    const SizedBox(height: 12),
                  ],

                  // Province Dropdown
                  const Text(
                    'Province',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _textMid,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    constraints: const BoxConstraints(maxHeight: 160),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade200),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: isLoadingProvinces
                        ? const Center(
                            child: Padding(
                              padding: EdgeInsets.all(12.0),
                              child: SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              ),
                            ),
                          )
                        : ListView.builder(
                            shrinkWrap: true,
                            itemCount: provinces.length,
                            itemBuilder: (context, index) {
                              final province = provinces[index];
                              final pName = province['name'] ?? '';
                              final pCode = province['psgc_code'] ?? '';
                              final isSelected = selectedProvinceCode == pCode;

                              return Material(
                                child: InkWell(
                                  onTap: () async {
                                    setSheetState(() {
                                      selectedProvince = pName;
                                      selectedProvinceCode = pCode;
                                      selectedCity = null;
                                      selectedCityCode = null;
                                      selectedBarangay = null;
                                      cities = [];
                                      barangays = [];
                                      isLoadingCities = true;
                                    });
                                    await fetchCities(pCode);
                                    if (mounted) {
                                      setSheetState(() {
                                        isLoadingCities = false;
                                      });
                                    }
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 10,
                                      vertical: 8,
                                    ),
                                    color: isSelected
                                        ? _primary.withValues(alpha: 0.08)
                                        : Colors.transparent,
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            pName,
                                            style: TextStyle(
                                              fontSize: 12,
                                              fontWeight: isSelected
                                                  ? FontWeight.w600
                                                  : FontWeight.w500,
                                              color: isSelected
                                                  ? _primary
                                                  : _textDark,
                                            ),
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                        if (isSelected)
                                          const Icon(
                                            Icons.check,
                                            color: _primary,
                                            size: 16,
                                          ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                  const SizedBox(height: 12),

                  // City Dropdown
                  const Text(
                    'City / Municipality',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _textMid,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    constraints: const BoxConstraints(maxHeight: 160),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade200),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: selectedProvinceCode == null
                        ? Center(
                            child: Padding(
                              padding: const EdgeInsets.all(12.0),
                              child: Text(
                                'Select province first',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ),
                          )
                        : isLoadingCities
                            ? const Center(
                                child: Padding(
                                  padding: EdgeInsets.all(12.0),
                                  child: SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  ),
                                ),
                              )
                            : ListView.builder(
                                shrinkWrap: true,
                                itemCount: cities.length,
                                itemBuilder: (context, index) {
                                  final city = cities[index];
                                  final cName = city['name'] ?? '';
                                  final cCode = city['psgc_code'] ?? '';
                                  final isSelected = selectedCityCode == cCode;

                                  return Material(
                                    child: InkWell(
                                      onTap: () async {
                                        setSheetState(() {
                                          selectedCity = cName;
                                          selectedCityCode = cCode;
                                          selectedBarangay = null;
                                          barangays = [];
                                          isLoadingBarangays = true;
                                        });
                                        await fetchBarangays(cCode);
                                        if (mounted) {
                                          setSheetState(() {
                                            isLoadingBarangays = false;
                                          });
                                        }
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 10,
                                          vertical: 8,
                                        ),
                                        color: isSelected
                                            ? _primary.withValues(alpha: 0.08)
                                            : Colors.transparent,
                                        child: Row(
                                          children: [
                                            Expanded(
                                              child: Text(
                                                cName,
                                                style: TextStyle(
                                                  fontSize: 12,
                                                  fontWeight: isSelected
                                                      ? FontWeight.w600
                                                      : FontWeight.w500,
                                                  color: isSelected
                                                      ? _primary
                                                      : _textDark,
                                                ),
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                            if (isSelected)
                                              const Icon(
                                                Icons.check,
                                                color: _primary,
                                                size: 16,
                                              ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),
                  ),
                  const SizedBox(height: 12),

                  // Barangay Dropdown
                  const Text(
                    'Barangay',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _textMid,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    constraints: const BoxConstraints(maxHeight: 160),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade200),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: selectedCityCode == null
                        ? Center(
                            child: Padding(
                              padding: const EdgeInsets.all(12.0),
                              child: Text(
                                'Select city first',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ),
                          )
                        : isLoadingBarangays
                            ? const Center(
                                child: Padding(
                                  padding: EdgeInsets.all(12.0),
                                  child: SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  ),
                                ),
                              )
                            : ListView.builder(
                                shrinkWrap: true,
                                itemCount: barangays.length,
                                itemBuilder: (context, index) {
                                  final barangay = barangays[index];
                                  final bName = barangay['name'] ?? '';
                                  final isSelected = selectedBarangay == bName;

                                  return Material(
                                    child: InkWell(
                                      onTap: () {
                                        setSheetState(() {
                                          selectedBarangay = bName;
                                        });
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 10,
                                          vertical: 8,
                                        ),
                                        color: isSelected
                                            ? _primary.withValues(alpha: 0.08)
                                            : Colors.transparent,
                                        child: Row(
                                          children: [
                                            Expanded(
                                              child: Text(
                                                bName,
                                                style: TextStyle(
                                                  fontSize: 12,
                                                  fontWeight: isSelected
                                                      ? FontWeight.w600
                                                      : FontWeight.w500,
                                                  color: isSelected
                                                      ? _primary
                                                      : _textDark,
                                                ),
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                            if (isSelected)
                                              const Icon(
                                                Icons.check,
                                                color: _primary,
                                                size: 16,
                                              ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),
                  ),
                  const SizedBox(height: 12),

                  // Street
                  _buildInputField(
                    controller: streetController,
                    label: 'Street / Building / Unit No.',
                    hint: 'e.g., 123 Main St, Unit 4B',
                    icon: LucideIcons.navigation,
                    maxLines: 2,
                  ),
                  const SizedBox(height: 14),

                  // Default toggle - Compact
                  GestureDetector(
                    onTap: () {
                      setSheetState(() {
                        isDefault = !isDefault;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: isDefault
                            ? _primary.withValues(alpha: 0.08)
                            : Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: isDefault ? _primary : Colors.grey.shade200,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 18,
                            height: 18,
                            decoration: BoxDecoration(
                              color: isDefault ? _primary : Colors.transparent,
                              border: Border.all(
                                color:
                                    isDefault ? _primary : Colors.grey.shade300,
                              ),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: isDefault
                                ? const Icon(Icons.check,
                                    size: 12, color: Colors.white)
                                : null,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Set as default address',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: isDefault ? _primary : _textDark,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Save button
                  SizedBox(
                    width: double.infinity,
                    height: 44,
                    child: ElevatedButton(
                      onPressed: selectedLabel != null &&
                              (selectedLabel != 'Other' ||
                                  customLabelController.text.trim().isNotEmpty) &&
                              selectedProvince != null &&
                              selectedCity != null &&
                              selectedBarangay != null &&
                              streetController.text.isNotEmpty
                          ? () => Navigator.pop(context, true)
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _primary,
                        disabledBackgroundColor: Colors.grey.shade300,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: const Text(
                        'Save Address',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );

    if (result == true && mounted) {
      final finalLabel = selectedLabel == 'Other'
          ? customLabelController.text.trim()
          : selectedLabel ?? '';

      await _addAddress(
        label: finalLabel,
        street: streetController.text,
        city: selectedCity ?? '',
        province: selectedProvince ?? '',
        barangay: selectedBarangay,
        zip: '',
        isDefault: isDefault,
      );
    }

    streetController.dispose();
    customLabelController.dispose();
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    int maxLines = 1,
    TextInputType? keyboardType,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: _textMid,
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          maxLines: maxLines,
          keyboardType: keyboardType,
          style: const TextStyle(
            fontSize: 14,
            color: _textDark,
            fontWeight: FontWeight.w500,
          ),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 13,
              fontWeight: FontWeight.w400,
            ),
            prefixIcon: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Icon(icon, size: 18, color: _primary),
            ),
            prefixIconConstraints:
                const BoxConstraints(minWidth: 48, minHeight: 48),
            filled: true,
            fillColor: Colors.grey.shade50,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: BorderSide(color: Colors.grey.shade200),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: BorderSide(color: Colors.grey.shade200),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: const BorderSide(color: _primary, width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _addAddress({
    required String label,
    required String street,
    required String city,
    required String province,
    String? barangay,
    required String zip,
    required bool isDefault,
  }) async {
    try {
      final trimmedBarangay = (barangay ?? '').trim();
      final fullAddress =
          '$street, ${trimmedBarangay.isNotEmpty ? '$trimmedBarangay, ' : ''}$city, $province${zip.isNotEmpty ? ', $zip' : ''}';

      final response =
          await ApiService.request('POST', '/api/v1/buyer/addresses', body: {
        'label': label,
        'full_address': fullAddress,
        'street_address': street,
        'city': city,
        'province': province,
        'barangay': trimmedBarangay,
        'zip_code': zip,
        'is_default': isDefault,
      });

      if (response['success'] == true && mounted) {
        _showSnackBar('Address added successfully', isSuccess: true);
        _fetchAddresses();
      } else if (mounted) {
        _showSnackBar(response['message'] ?? 'Failed to add address');
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error adding address: $e');
      }
    }
  }

  Future<void> _performLogout(AuthProvider authProvider) async {
    try {
      final buyerProvider = context.read<BuyerProvider>();
      buyerProvider.cleanup();
      final cartProvider = context.read<CartProvider>();
      cartProvider.clearCart();
      await authProvider.logout();

      if (mounted) {
        Navigator.of(context).pushNamedAndRemoveUntil(
          '/home',
          (route) => false,
        );
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error logging out');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final buyerProvider = context.watch<BuyerProvider>();

    if (!authProvider.isAuthenticated) {
      return _buildGuestView();
    }

    return Scaffold(
      backgroundColor: _bgColor,
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: Column(
          children: [
            _buildHeader(context, authProvider, buyerProvider),
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Column(
                    children: [
                      const SizedBox(height: 12),
                      _buildMenuSection("My Account", [
                        _MenuItem(
                          LucideIcons.package,
                          "My Orders",
                          "View your orders",
                          Colors.blue,
                          () {},
                        ),
                        _MenuItem(
                          LucideIcons.heart,
                          "Liked Products",
                          "Saved items",
                          Colors.red,
                          () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    const LikedProductsScreen(),
                              ),
                            );
                          },
                        ),
                        _MenuItem(
                          LucideIcons.creditCard,
                          "Payment Methods",
                          "Manage cards",
                          Colors.green,
                          () {},
                        ),
                        _MenuItem(
                          LucideIcons.mapPin,
                          "Addresses",
                          _addresses.isNotEmpty
                              ? '${_addresses.length} saved'
                              : "Add address",
                          Colors.orange,
                          _showAddAddressSheet,
                        ),
                      ]),
                      if (_addresses.isNotEmpty) ...[
                        _buildAddressesSection(),
                      ],
                      _buildMenuSection("Preferences", [
                        _MenuItem(
                          LucideIcons.bell,
                          "Notifications",
                          "Manage alerts",
                          Colors.purple,
                          () {},
                        ),
                        _MenuItem(
                          LucideIcons.shield,
                          "Privacy & Security",
                          "Keep safe",
                          Colors.indigo,
                          () {},
                        ),
                      ]),
                      _buildMenuSection("Support", [
                        _MenuItem(
                          LucideIcons.helpCircle,
                          "Help Center",
                          "FAQs & support",
                          Colors.teal,
                          () {},
                        ),
                        _MenuItem(
                          LucideIcons.star,
                          "Rate the App",
                          "Share feedback",
                          Colors.yellow.shade700,
                          () {},
                        ),
                      ]),
                      const SizedBox(height: 16),
                      _buildLogoutButton(context, authProvider),
                      const SizedBox(height: 32),
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

  Widget _buildGuestView() {
    return Scaffold(
      backgroundColor: _bgColor,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      _primary.withValues(alpha: 0.12),
                      _primaryLight.withValues(alpha: 0.08),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(28),
                ),
                child: const Icon(
                  LucideIcons.userCircle2,
                  size: 48,
                  color: _primary,
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'You\'re not logged in',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: _textDark,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Log in or create an account to access your full profile and orders.',
                style: TextStyle(fontSize: 14, color: _textMid, height: 1.5),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 36),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, '/login'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _primary,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Log In',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton(
                  onPressed: () => Navigator.pushNamed(context, '/register'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: _primary,
                    side: const BorderSide(color: _primary, width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Create Account',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, AuthProvider authProvider,
      BuyerProvider buyerProvider) {
    final fullName = authProvider.user?.fullName ?? '';
    final nameInitial = fullName.isNotEmpty ? fullName[0].toUpperCase() : 'U';

    return Container(
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top + 24,
        left: 20,
        right: 20,
        bottom: 28,
      ),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [_primaryDark, _primary, _primaryLight],
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Avatar
              GestureDetector(
                onTap: _pickAndUploadImage,
                child: Stack(
                  children: [
                    Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(
                          color: Colors.white.withValues(alpha: 0.4),
                          width: 2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.2),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: authProvider.user?.profileImage != null &&
                              authProvider.user!.profileImage!.isNotEmpty
                          ? ClipRRect(
                              borderRadius: BorderRadius.circular(20),
                              child: Image.network(
                                UrlConfig.toAbsoluteImageUrl(
                                    authProvider.user!.profileImage!),
                                fit: BoxFit.cover,
                                errorBuilder: (c, e, s) => Center(
                                  child: Text(
                                    nameInitial,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 28,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            )
                          : Center(
                              child: Text(
                                nameInitial,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                    ),
                    if (_isUploadingImage)
                      Positioned.fill(
                        child: Container(
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.45),
                            borderRadius: BorderRadius.circular(22),
                          ),
                          child: const Center(
                            child: SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            ),
                          ),
                        ),
                      ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        width: 26,
                        height: 26,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          border: Border.all(
                              color: _primary.withValues(alpha: 0.3), width: 1),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.15),
                              blurRadius: 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: const Icon(
                          LucideIcons.camera,
                          size: 13,
                          color: _primary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      authProvider.user?.fullName ?? 'User',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 19,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      authProvider.user?.email ?? '',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.75),
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.18),
                        borderRadius: BorderRadius.circular(20),
                        border:
                            Border.all(color: Colors.white.withValues(alpha: 0.25)),
                      ),
                      child: const Text(
                        "⭐  Member",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.2,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Stats row
          Row(
            children: [
              _buildStat("Orders", "View", LucideIcons.package),
              const SizedBox(width: 8),
              _buildStat("Reviews", "Share", LucideIcons.star),
              const SizedBox(width: 8),
              _buildStat("Points", "Earn", LucideIcons.zap),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStat(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 16, color: Colors.white.withValues(alpha: 0.9)),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.w800,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.55),
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuSection(String title, List<_MenuItem> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10, top: 20),
          child: Text(
            title.toUpperCase(),
            style: const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              color: _textMid,
              letterSpacing: 1.4,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: _cardColor,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: items.asMap().entries.map((entry) {
              int idx = entry.key;
              _MenuItem item = entry.value;
              return Column(
                children: [
                  Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: item.onTap,
                      borderRadius: BorderRadius.vertical(
                        top: idx == 0 ? const Radius.circular(20) : Radius.zero,
                        bottom: idx == items.length - 1
                            ? const Radius.circular(20)
                            : Radius.zero,
                      ),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        child: Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: item.color.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(
                                item.icon,
                                size: 18,
                                color: item.color,
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item.label,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w700,
                                      color: _textDark,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    item.sub,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: _textMid,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              width: 28,
                              height: 28,
                              decoration: BoxDecoration(
                                color: Colors.grey.shade50,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(
                                LucideIcons.chevronRight,
                                size: 14,
                                color: _textMid,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  if (idx != items.length - 1)
                    Divider(
                      height: 1,
                      color: Colors.grey.withValues(alpha: 0.08),
                      indent: 16,
                      endIndent: 16,
                    ),
                ],
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildLogoutButton(BuildContext context, AuthProvider authProvider) {
    return GestureDetector(
      onTap: () {
        showDialog(
          context: context,
          barrierColor: Colors.black.withValues(alpha: 0.4),
          builder: (context) => Dialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
            ),
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _cardColor,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(
                      LucideIcons.logOut,
                      color: Colors.red,
                      size: 28,
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Sign Out?',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: _textDark,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'You will be logged out of your account. You can log back in anytime.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      color: _textMid,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 28),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => Navigator.pop(context),
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: Colors.grey.shade300,
                              width: 1.5,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          child: const Text(
                            'Cancel',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _textDark,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pop(context);
                            _performLogout(authProvider);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          child: const Text(
                            'Sign Out',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.red.withValues(alpha: 0.06),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.red.withValues(alpha: 0.15)),
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(LucideIcons.logOut, size: 18, color: Colors.red),
            SizedBox(width: 8),
            Text(
              "Sign Out",
              style: TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.w700,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAddressesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10, top: 20),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'SAVED ADDRESSES',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  color: _textMid,
                  letterSpacing: 1.4,
                ),
              ),
              GestureDetector(
                onTap: _showAddAddressSheet,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    children: [
                      Icon(LucideIcons.plus, size: 12, color: _primary),
                      SizedBox(width: 4),
                      Text(
                        'Add New',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: _primary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: _cardColor,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _addresses.length,
            separatorBuilder: (context, index) => Divider(
              height: 1,
              color: Colors.grey.withValues(alpha: 0.08),
              indent: 16,
              endIndent: 16,
            ),
            itemBuilder: (context, index) {
              final address = _addresses[index];
              final isDefault = address['is_default'] == true;
              final label = address['label'] ?? 'Address';

              IconData addressIcon;
              switch (label.toLowerCase()) {
                case 'home':
                  addressIcon = LucideIcons.home;
                  break;
                case 'work':
                  addressIcon = LucideIcons.briefcase;
                  break;
                case 'office':
                  addressIcon = LucideIcons.building2;
                  break;
                default:
                  addressIcon = LucideIcons.mapPin;
              }

              return Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: Colors.orange.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(addressIcon, size: 20, color: Colors.orange),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                label,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                  color: _textDark,
                                ),
                              ),
                              if (isDefault) ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: _primary,
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Text(
                                    'Default',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            address['full_address'] ?? '',
                            style: const TextStyle(
                              fontSize: 12,
                              color: _textMid,
                              height: 1.4,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      onTap: () => _deleteAddress(address['id']),
                      child: Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          color: Colors.red.withValues(alpha: 0.07),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          LucideIcons.trash2,
                          size: 15,
                          color: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Future<void> _deleteAddress(int? addressId) async {
    if (addressId == null) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Text(
          'Delete Address',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        content: const Text(
          'Are you sure you want to remove this address?',
          style: TextStyle(color: _textMid),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel', style: TextStyle(color: _textMid)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      try {
        final response = await ApiService.request(
          'DELETE',
          '/api/v1/buyer/addresses/$addressId',
        );

        if (response['success'] == true && mounted) {
          _showSnackBar('Address deleted', isSuccess: true);
          _fetchAddresses();
        } else if (mounted) {
          _showSnackBar(response['message'] ?? 'Failed to delete address');
        }
      } catch (e) {
        if (mounted) {
          _showSnackBar('Error deleting address: $e');
        }
      }
    }
  }
}

class _MenuItem {
  final IconData icon;
  final String label;
  final String sub;
  final Color color;
  final VoidCallback onTap;

  _MenuItem(this.icon, this.label, this.sub, this.color, this.onTap);
}
