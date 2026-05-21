import 'package:flutter/material.dart';

import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/cart_provider.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import 'wishlist_screen.dart';
import 'coupons_screen.dart';

import 'buyer_edit_profile_screen.dart';

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
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  bool _isLoadingWishlist = true;
  int _wishlistCount = 0;

  // PSGC API data
  List<Map<String, dynamic>> _regionsCache = [];
  Map<String, List<Map<String, dynamic>>> _provincesCache = {};
  Map<String, List<Map<String, dynamic>>> _citiesCache = {};
  Map<String, List<Map<String, dynamic>>> _barangaysCache = {};

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
    // Refresh user profile from backend to get latest profile image
    final authProvider = context.read<AuthProvider>();
    await authProvider.refreshUser();
    
    final buyerProvider = context.read<BuyerProvider>();
    buyerProvider.fetchProfile();
    await _fetchAddresses();
    await _fetchWishlistCount();

    if (widget.showAddressSetup && _addresses.isEmpty && mounted) {
      _showSnackBar('Please add your delivery address to continue.');
      await _showAddAddressSheet();
    }
  }

  Future<void> _fetchWishlistCount() async {
    setState(() => _isLoadingWishlist = true);
    try {
      final buyerProvider = context.read<BuyerProvider>();
      await buyerProvider.fetchWishlist();
      if (mounted) {
        setState(() {
          _wishlistCount = buyerProvider.wishlistProducts.length;
          _isLoadingWishlist = false;
        });
      }
    } catch (e) {
      debugPrint('Error fetching wishlist: $e');
      if (mounted) setState(() => _isLoadingWishlist = false);
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
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

  void _showSnackBar(String message, {bool isSuccess = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isSuccess ? Icons.check_circle : Icons.error,
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

    // PSGC selections
    String? selectedRegion;
    String? selectedProvince;
    String? selectedCity;
    String? selectedBarangay;

    // Steps: 0=Region, 1=Province, 2=City, 3=Barangay, 4=Details
    int currentStep = 0;

    List<dynamic> regions = [];
    List<dynamic> provinces = [];
    List<dynamic> cities = [];
    List<dynamic> barangays = [];

    bool isLoadingRegions = true;
    bool isLoadingProvinces = false;
    bool isLoadingCities = false;
    bool isLoadingBarangays = false;

    const tabLabels = ['Region', 'Province', 'City', 'Barangay', 'Details'];

    Future<void> fetchRegions() async {
      try {
        if (_regionsCache.isEmpty) {
          final response =
              await ApiService.request('GET', '/api/regions', auth: false);
          if (response != null && response['result'] != null) {
            _regionsCache = List<Map<String, dynamic>>.from(response['result']);
          }
        }
        regions = _regionsCache;
      } catch (e) {
        debugPrint('Error fetching regions: $e');
      }
    }

    Future<void> fetchProvinces(String regionCode) async {
      try {
        if (_provincesCache.containsKey(regionCode)) {
          provinces = _provincesCache[regionCode]!;
        } else {
          final response = await ApiService.request(
              'GET', '/api/provinces?region_code=$regionCode',
              auth: false);
          if (response != null && response['result'] != null) {
            final list = List<Map<String, dynamic>>.from(response['result']);
            _provincesCache[regionCode] = list;
            provinces = list;
          }
        }
      } catch (e) {
        debugPrint('Error fetching provinces: $e');
      }
    }

    Future<void> fetchCities(String provinceCode) async {
      try {
        if (_citiesCache.containsKey(provinceCode)) {
          cities = _citiesCache[provinceCode]!;
        } else {
          final response = await ApiService.request(
              'GET', '/api/cities?province_code=$provinceCode',
              auth: false);
          if (response != null && response['result'] != null) {
            final list = List<Map<String, dynamic>>.from(response['result']);
            _citiesCache[provinceCode] = list;
            cities = list;
          }
        }
      } catch (e) {
        debugPrint('Error fetching cities: $e');
      }
    }

    Future<void> fetchBarangays(String cityCode) async {
      try {
        if (_barangaysCache.containsKey(cityCode)) {
          barangays = _barangaysCache[cityCode]!;
        } else {
          final response = await ApiService.request(
              'GET', '/api/barangays?city_code=$cityCode',
              auth: false);
          if (response != null && response['result'] != null) {
            final list = List<Map<String, dynamic>>.from(response['result']);
            _barangaysCache[cityCode] = list;
            barangays = list;
          } else {
            barangays = [];
          }
        }
      } catch (e) {
        debugPrint('Error fetching barangays: $e');
        barangays = [];
      }
    }

    if (!mounted) return;

    await fetchRegions();
    isLoadingRegions = false;

    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      isDismissible: true,
      enableDrag: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) => StatefulBuilder(
        builder: (ctx, setSheetState) {
          // ── Empty state helper (MUST BE FIRST) ───────────────────────
          Widget _buildEmptyStateWidget(String message, IconData icon) {
            return SizedBox(
              height: 200,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Icon(icon, size: 24, color: Colors.grey.shade400),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      message,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey.shade400,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          }

          // ── Reusable list row (MUST BE BEFORE _buildRegionList) ──────
          Widget _buildListRowWidget({
            required String label,
            required int index,
            required bool isSelected,
            required VoidCallback onTap,
          }) {
            return InkWell(
              onTap: onTap,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                color: isSelected
                    ? _primary.withValues(alpha: 0.06)
                    : Colors.transparent,
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
                child: Row(
                  children: [
                    // Number badge
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 150),
                      width: 34,
                      height: 34,
                      decoration: BoxDecoration(
                        color: isSelected
                            ? _primary.withValues(alpha: 0.14)
                            : Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(
                        child: Text(
                          (index + 1).toString().padLeft(2, '0'),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: isSelected ? _primary : _textMid,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        label,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight:
                              isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected ? _primary : _textDark,
                        ),
                      ),
                    ),
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 200),
                      child: isSelected
                          ? Container(
                              key: const ValueKey('checked'),
                              width: 22,
                              height: 22,
                              decoration: const BoxDecoration(
                                color: _primary,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.check,
                                  size: 12, color: Colors.white),
                            )
                          : Container(
                              key: const ValueKey('arrow'),
                              width: 22,
                              height: 22,
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                shape: BoxShape.circle,
                              ),
                              child: Icon(Icons.chevron_right,
                                  size: 11, color: Colors.grey.shade400),
                            ),
                    ),
                  ],
                ),
              ),
            );
          }

          // ── Section label (MUST BE BEFORE _buildDetailsStep) ──────────
          Widget _buildSectionLabelWidget(String text) {
            return Text(
              text,
              style: const TextStyle(
                fontSize: 9.5,
                fontWeight: FontWeight.w800,
                color: _textMid,
                letterSpacing: 1.3,
              ),
            );
          }

          // ── Helpers ───────────────────────────────────────────────────
          String _stepTitle() {
            switch (currentStep) {
              case 0:
                return 'Select Region';
              case 1:
                return 'Select Province';
              case 2:
                return 'Select City';
              case 3:
                return 'Select Barangay';
              case 4:
                return 'Address Details';
              default:
                return '';
            }
          }

          String _stepSubtitle() {
            switch (currentStep) {
              case 0:
                return 'Philippines — choose your region';
              case 1:
                return selectedRegion ?? '';
              case 2:
                return selectedProvince ?? '';
              case 3:
                return selectedCity ?? '';
              case 4:
                final parts = [selectedBarangay, selectedCity]
                    .where((e) => e != null && e.isNotEmpty)
                    .join(', ');
                return parts;
              default:
                return '';
            }
          }

          // ── Shimmer skeleton row ──────────────────────────────────────
          Widget _shimmerRow() {
            return Container(
              height: 56,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          height: 13,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Container(
                          height: 10,
                          width: 100,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }

          Widget _buildSkeletonList() {
            return Column(
              children: List.generate(
                7,
                (i) => Column(
                  children: [
                    _shimmerRow(),
                    if (i < 6) Divider(height: 1, color: Colors.grey.shade100),
                  ],
                ),
              ),
            );
          }

          // ── Shimmer skeleton chip ─────────────────────────────────────
          Widget _buildSkeletonGrid() {
            return Wrap(
              spacing: 8,
              runSpacing: 8,
              children: List.generate(
                10,
                (_) => Container(
                  width: (MediaQuery.of(ctx).size.width - 56) / 2,
                  height: 44,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            );
          }

          // ── Step progress tabs ────────────────────────────────────────
          Widget _buildStepTabs() {
            return Row(
              children: List.generate(tabLabels.length, (i) {
                final isActive = i == currentStep;
                final isDone = i < currentStep;
                final isClickable = isDone;
                return Expanded(
                  child: GestureDetector(
                    onTap: isClickable
                        ? () => setSheetState(() => currentStep = i)
                        : null,
                    behavior: HitTestBehavior.opaque,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Progress line
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          height: 3,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            color: (isDone || isActive)
                                ? _primary
                                : Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                        const SizedBox(height: 6),
                        // Step dot + label
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            if (isDone)
                              Container(
                                width: 12,
                                height: 12,
                                decoration: const BoxDecoration(
                                  color: _primary,
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.check,
                                  size: 8,
                                  color: Colors.white,
                                ),
                              )
                            else
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 250),
                                width: 12,
                                height: 12,
                                decoration: BoxDecoration(
                                  color: isActive
                                      ? _primary
                                      : Colors.grey.shade200,
                                  shape: BoxShape.circle,
                                ),
                              ),
                            const SizedBox(width: 3),
                            Flexible(
                              child: Text(
                                tabLabels[i],
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: isActive
                                      ? FontWeight.w800
                                      : FontWeight.w500,
                                  color: isActive
                                      ? _primary
                                      : isDone
                                          ? _primary.withValues(alpha: 0.6)
                                          : Colors.grey.shade400,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              }),
            );
          }

          // ── Region list ───────────────────────────────────────────────
          Widget _buildRegionList() {
            if (isLoadingRegions) return _buildSkeletonList();
            if (regions.isEmpty) {
              return _buildEmptyStateWidget(
                  'No regions found', Icons.public);
            }
            return ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: regions.length,
              separatorBuilder: (_, __) =>
                  Divider(height: 1, color: Colors.grey.shade100),
              itemBuilder: (context, index) {
                final item = regions[index] as Map<String, dynamic>;
                final name = item['name'] ?? '';
                final isSelected = selectedRegion == name;
                return _buildListRowWidget(
                  label: name,
                  index: index,
                  isSelected: isSelected,
                  onTap: () async {
                    final code = item['psgc_code'] ?? item['code'] ?? '';
                    setSheetState(() {
                      selectedRegion = name;
                      selectedProvince = null;
                      selectedCity = null;
                      selectedBarangay = null;
                      provinces = [];
                      cities = [];
                      barangays = [];
                      isLoadingProvinces = true;
                      currentStep = 1;
                    });
                    await fetchProvinces(code);
                    setSheetState(() => isLoadingProvinces = false);
                  },
                );
              },
            );
          }



          // ── Province list ─────────────────────────────────────────
          Widget _buildProvinceList() {
            if (isLoadingProvinces) return _buildSkeletonList();
            if (provinces.isEmpty) {
              return _buildEmptyStateWidget(
                selectedRegion == null
                    ? 'Select a region first'
                    : 'No provinces found',
                Icons.location_on,
              );
            }
            return ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: provinces.length,
              separatorBuilder: (_, __) =>
                  Divider(height: 1, color: Colors.grey.shade100),
              itemBuilder: (context, index) {
                final item = provinces[index] as Map<String, dynamic>;
                final name = item['name'] ?? '';
                final isSelected = selectedProvince == name;
                return _buildListRowWidget(
                  label: name,
                  index: index,
                  isSelected: isSelected,
                  onTap: () async {
                    final code = item['psgc_code'] ?? item['code'] ?? '';
                    setSheetState(() {
                      selectedProvince = name;
                      selectedCity = null;
                      selectedBarangay = null;
                      cities = [];
                      barangays = [];
                      isLoadingCities = true;
                      currentStep = 2;
                    });
                    await fetchCities(code);
                    setSheetState(() => isLoadingCities = false);
                  },
                );
              },
            );
          }

          // ── City list ─────────────────────────────────────────────────
          Widget _buildCityList() {
            if (isLoadingCities) return _buildSkeletonList();
            if (cities.isEmpty) {
              return _buildEmptyStateWidget(
                selectedProvince == null
                    ? 'Select a province first'
                    : 'No cities found',
                Icons.location_on,
              );
            }
            return ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: cities.length,
              separatorBuilder: (_, __) =>
                  Divider(height: 1, color: Colors.grey.shade100),
              itemBuilder: (context, index) {
                final item = cities[index] as Map<String, dynamic>;
                final name = item['name'] ?? '';
                final isSelected = selectedCity == name;
                return _buildListRowWidget(
                  label: name,
                  index: index,
                  isSelected: isSelected,
                  onTap: () async {
                    final code = item['psgc_code'] ?? item['code'] ?? '';
                    setSheetState(() {
                      selectedCity = name;
                      selectedBarangay = null;
                      barangays = [];
                      isLoadingBarangays = true;
                      currentStep = 3;
                    });
                    await fetchBarangays(code);
                    setSheetState(() => isLoadingBarangays = false);
                  },
                );
              },
            );
          }



          // ── Chip grid (province / city) ───────────────────────────────
          Widget _buildChipGrid({
            required List<dynamic> items,
            required bool isLoading,
            required String? selectedValue,
            required String emptyHint,
            required Future<void> Function(Map<String, dynamic>) onSelect,
          }) {
            if (isLoading) return _buildSkeletonGrid();
            if (items.isEmpty) {
              return _buildEmptyStateWidget(emptyHint, Icons.location_on);
            }

            return Wrap(
              spacing: 8,
              runSpacing: 8,
              children: items.map((raw) {
                final item = raw as Map<String, dynamic>;
                final name = item['name'] ?? '';
                final isSelected = selectedValue == name;
                return GestureDetector(
                  onTap: () => onSelect(item),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    width: (MediaQuery.of(ctx).size.width - 56) / 2,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 11),
                    decoration: BoxDecoration(
                      color: isSelected ? _primary : Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected ? _primary : Colors.grey.shade200,
                        width: isSelected ? 1.5 : 1,
                      ),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: _primary.withValues(alpha: 0.22),
                                blurRadius: 8,
                                offset: const Offset(0, 3),
                              )
                            ]
                          : [],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            name,
                            style: TextStyle(
                              fontSize: 11.5,
                              fontWeight: isSelected
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              color: isSelected ? Colors.white : _textDark,
                            ),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                        if (isSelected) ...[
                          const SizedBox(width: 4),
                          const Icon(Icons.check_circle,
                              size: 13, color: Colors.white),
                        ],
                      ],
                    ),
                  ),
                );
              }).toList(),
            );
          }

          // ── Barangay list ─────────────────────────────────────────────
          Widget _buildBarangayList() {
            if (isLoadingBarangays) return _buildSkeletonList();
            if (barangays.isEmpty) {
              return _buildEmptyStateWidget(
                selectedCity == null
                    ? 'Select a city first'
                    : 'No barangays found',
                Icons.location_on,
              );
            }
            return ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: barangays.length,
              separatorBuilder: (_, __) =>
                  Divider(height: 1, color: Colors.grey.shade100),
              itemBuilder: (context, index) {
                final item = barangays[index] as Map<String, dynamic>;
                final name = item['name'] ?? '';
                final isSelected = selectedBarangay == name;
                return _buildListRowWidget(
                  label: name,
                  index: index,
                  isSelected: isSelected,
                  onTap: () {
                    setSheetState(() {
                      selectedBarangay = name;
                      currentStep = 4;
                    });
                  },
                );
              },
            );
          }



          // ── Details step ──────────────────────────────────────────────
          Widget _buildDetailsStep() {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Location summary card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: _primary.withValues(alpha: 0.04),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: _primary.withValues(alpha: 0.14)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [_primaryDark, _primary],
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.location_on,
                            size: 16, color: Colors.white),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '$selectedBarangay, $selectedCity',
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: _textDark,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 2),
                            Text(
                              '$selectedProvince · $selectedRegion',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.grey.shade500,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      GestureDetector(
                        onTap: () => setSheetState(() => currentStep = 0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: _primary,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'Edit',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Label section
                _buildSectionLabelWidget('ADDRESS LABEL'),
                const SizedBox(height: 10),
                Row(
                  children: [
                    {'label': 'Home', 'icon': Icons.home},
                    {'label': 'Work', 'icon': Icons.work},
                    {'label': 'Office', 'icon': Icons.business},
                    {'label': 'Other', 'icon': Icons.location_on},
                  ].map((opt) {
                    final label = opt['label'] as String;
                    final icon = opt['icon'] as IconData;
                    final isSelected = selectedLabel == label;
                    return Expanded(
                      child: GestureDetector(
                        onTap: () => setSheetState(() => selectedLabel = label),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 150),
                          margin: const EdgeInsets.only(right: 7),
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: isSelected ? _primary : Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color:
                                  isSelected ? _primary : Colors.grey.shade200,
                            ),
                            boxShadow: isSelected
                                ? [
                                    BoxShadow(
                                      color: _primary.withValues(alpha: 0.25),
                                      blurRadius: 8,
                                      offset: const Offset(0, 3),
                                    )
                                  ]
                                : [],
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                icon,
                                size: 15,
                                color: isSelected ? Colors.white : _textMid,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                label,
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                  color: isSelected ? Colors.white : _textDark,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
                if (selectedLabel == 'Other') ...[
                  const SizedBox(height: 12),
                  _buildTextField(
                    controller: customLabelController,
                    label: 'Custom Label',
                    hint: 'e.g., Vacation Home, Gym...',
                    icon: Icons.local_offer,
                  ),
                ],
                const SizedBox(height: 20),

                // Street address
                _buildSectionLabelWidget('STREET ADDRESS'),
                const SizedBox(height: 10),
                _buildTextField(
                  controller: streetController,
                  label: 'House / Unit / Building No.',
                  hint: 'e.g., Unit 4B, 123 Rizal Ave',
                  icon: Icons.home,
                  maxLines: 2,
                ),
                const SizedBox(height: 16),

                // Default toggle
                GestureDetector(
                  onTap: () => setSheetState(() => isDefault = !isDefault),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isDefault
                          ? _primary.withValues(alpha: 0.06)
                          : Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: isDefault
                            ? _primary.withValues(alpha: 0.4)
                            : Colors.grey.shade200,
                      ),
                    ),
                    child: Row(
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 20,
                          height: 20,
                          decoration: BoxDecoration(
                            color: isDefault ? _primary : Colors.transparent,
                            border: Border.all(
                              color:
                                  isDefault ? _primary : Colors.grey.shade300,
                              width: 1.5,
                            ),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: isDefault
                              ? const Icon(Icons.check,
                                  size: 13, color: Colors.white)
                              : null,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Set as default address',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: isDefault ? _primary : _textDark,
                                ),
                              ),
                              const SizedBox(height: 1),
                              Text(
                                'Used automatically at checkout',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          isDefault
                              ? Icons.check_circle
                              : Icons.circle_outlined,
                          size: 16,
                          color: isDefault ? _primary : Colors.grey.shade300,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          }



          // ── Can proceed? ──────────────────────────────────────────────
          bool canProceed() {
            switch (currentStep) {
              case 0:
                return selectedRegion != null;
              case 1:
                return selectedProvince != null;
              case 2:
                return selectedCity != null;
              case 3:
                return selectedBarangay != null;
              case 4:
                if (selectedLabel == null) return false;
                if (selectedLabel == 'Other' &&
                    customLabelController.text.trim().isEmpty) return false;
                return streetController.text.trim().isNotEmpty;
              default:
                return false;
            }
          }

          // ── Bottom navigation ─────────────────────────────────────────
          Widget _buildNavBar() {
            final isLast = currentStep == 4;
            return Row(
              children: [
                if (currentStep > 0) ...[
                  SizedBox(
                    height: 50,
                    width: 50,
                    child: OutlinedButton(
                      onPressed: () => setSheetState(() => currentStep--),
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.zero,
                        foregroundColor: _textDark,
                        side: BorderSide(color: Colors.grey.shade300),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: const Icon(Icons.chevron_left, size: 18),
                    ),
                  ),
                  const SizedBox(width: 10),
                ],
                Expanded(
                  child: SizedBox(
                    height: 50,
                    child: ElevatedButton(
                      onPressed: canProceed()
                          ? () {
                              if (isLast) {
                                Navigator.pop(ctx, true);
                              } else {
                                setSheetState(() => currentStep++);
                              }
                            }
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _primary,
                        disabledBackgroundColor: Colors.grey.shade200,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          if (isLast) ...[
                            const Icon(Icons.check,
                                size: 15, color: Colors.white),
                            const SizedBox(width: 6),
                          ],
                          Text(
                            isLast ? 'Save Address' : 'Continue',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: canProceed()
                                  ? Colors.white
                                  : Colors.grey.shade400,
                            ),
                          ),
                          if (!isLast) ...[
                            const SizedBox(width: 6),
                            Icon(
                              Icons.chevron_right,
                              size: 15,
                              color: canProceed()
                                  ? Colors.white
                                  : Colors.grey.shade400,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            );
          }


          Widget _buildBody() {
            switch (currentStep) {
              case 0:
                return _buildRegionList();
              case 1:
                return _buildProvinceList();
              case 2:
                return _buildCityList();
              case 3:
                return _buildBarangayList();
              case 4:
                return _buildDetailsStep();
              default:
                return const SizedBox();
            }
          }

          // ── Sheet UI ──────────────────────────────────────────────────
          final screenHeight = MediaQuery.of(ctx).size.height;
          final bottomInset = MediaQuery.of(ctx).viewInsets.bottom;

          return Container(
            // Fixed height: 82% of screen so it never resizes between tabs
            height: screenHeight * 0.82,
            decoration: const BoxDecoration(
              color: _cardColor,
              borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
            ),
            child: Column(
              children: [
                // ── Drag handle ───────────────────────────────────────
                Center(
                  child: Container(
                    margin: const EdgeInsets.only(top: 12, bottom: 6),
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),

                // ── Header ────────────────────────────────────────────
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
                  child: Row(
                    children: [
                      // Icon badge
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [_primaryDark, _primary],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: const Icon(Icons.location_on,
                            color: Colors.white, size: 20),
                      ),
                      const SizedBox(width: 12),
                      // Title + subtitle
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            AnimatedSwitcher(
                              duration: const Duration(milliseconds: 200),
                              child: Text(
                                _stepTitle(),
                                key: ValueKey(_stepTitle()),
                                style: const TextStyle(
                                  fontSize: 17,
                                  fontWeight: FontWeight.w800,
                                  color: _textDark,
                                ),
                              ),
                            ),
                            if (_stepSubtitle().isNotEmpty) ...[
                              const SizedBox(height: 2),
                              AnimatedSwitcher(
                                duration: const Duration(milliseconds: 200),
                                child: Text(
                                  _stepSubtitle(),
                                  key: ValueKey(_stepSubtitle()),
                                  style: TextStyle(
                                    fontSize: 11.5,
                                    color: Colors.grey.shade500,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Close button
                      GestureDetector(
                        onTap: () => Navigator.pop(ctx, false),
                        child: Container(
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(Icons.close,
                              size: 16, color: _textMid),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Step tabs ─────────────────────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildStepTabs(),
                ),

                const SizedBox(height: 4),

                // ── Thin divider ──────────────────────────────────────
                Divider(height: 1, color: Colors.grey.shade100),

                // ── Scrollable content — fills remaining space ────────
                Expanded(
                  child: SingleChildScrollView(
                    padding: EdgeInsets.fromLTRB(16, 14, 16, 8 + bottomInset),
                    physics: const BouncingScrollPhysics(),
                    child: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 220),
                      transitionBuilder: (child, anim) =>
                          FadeTransition(opacity: anim, child: child),
                      child: KeyedSubtree(
                        key: ValueKey(currentStep),
                        child: _buildBody(),
                      ),
                    ),
                  ),
                ),

                // ── Divider above nav ─────────────────────────────────
                Divider(height: 1, color: Colors.grey.shade100),

                // ── Navigation bar ────────────────────────────────────
                Padding(
                  padding: EdgeInsets.fromLTRB(
                    16,
                    12,
                    16,
                    bottomInset > 0 ? bottomInset + 8 : 24,
                  ),
                  child: _buildNavBar(),
                ),
              ],
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
        street: streetController.text.trim(),
        city: selectedCity ?? '',
        province: selectedProvince ?? '',
        region: selectedRegion ?? '',
        barangay: selectedBarangay,
        zip: '',
        isDefault: isDefault,
      );
    }

    streetController.dispose();
    customLabelController.dispose();
  }

  Widget _buildTextField({
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
            fontSize: 11,
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
            fontSize: 13,
            color: _textDark,
            fontWeight: FontWeight.w500,
          ),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 12,
              fontWeight: FontWeight.w400,
            ),
            prefixIcon: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Icon(icon, size: 16, color: _primary),
            ),
            prefixIconConstraints:
                const BoxConstraints(minWidth: 44, minHeight: 44),
            filled: true,
            fillColor: Colors.grey.shade50,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade200),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade200),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
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
    required String region,
    String? barangay,
    required String zip,
    required bool isDefault,
  }) async {
    try {
      final trimmedBarangay = (barangay ?? '').trim();
      final fullAddress =
          '$street, ${trimmedBarangay.isNotEmpty ? '$trimmedBarangay, ' : ''}$city, $province, $region${zip.isNotEmpty ? ', $zip' : ''}';

      final response =
          await ApiService.request('POST', '/api/v1/buyer/addresses', body: {
        'label': label,
        'full_address': fullAddress,
        'street_address': street,
        'city': city,
        'province': province,
        'region': region,
        'barangay': trimmedBarangay,
        'zip_code': zip,
        'is_default': isDefault ? 1 : 0,
      });

      if (response['success'] == true && mounted) {
        _showSnackBar('✓ Address added successfully', isSuccess: true);
        await _fetchAddresses();

        if (isDefault) {
          final authProvider = context.read<AuthProvider>();
          final buyerProvider = context.read<BuyerProvider>();
          await authProvider.refreshUser();
          await buyerProvider.fetchProfile();
        }
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
                          Icons.inventory_2_outlined,
                          "My Orders",
                          "View your orders",
                          Colors.blue,
                          () {},
                        ),
                        _MenuItem(
                          Icons.local_offer_outlined,
                          "My Coupons",
                          "View available coupons",
                          Colors.orange,
                          () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const CouponsScreen(),
                              ),
                            );
                          },
                        ),
                        _MenuItem(
                          Icons.favorite,
                          "Wishlist",
                          _isLoadingWishlist
                              ? "Loading..."
                              : "$_wishlistCount items",
                          Colors.red,
                          () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const WishlistScreen(),
                              ),
                            );
                          },
                        ),
                        _MenuItem(
                          Icons.credit_card,
                          "Payment Methods",
                          "Manage cards",
                          Colors.green,
                          () {},
                        ),
                      ]),
                      _buildAddressesSection(),
                      _buildMenuSection("Preferences", [
                        _MenuItem(
                          Icons.notifications_outlined,
                          "Notifications",
                          "Manage alerts",
                          Colors.purple,
                          () {},
                        ),
                        _MenuItem(
                          Icons.shield,
                          "Privacy & Security",
                          "Keep safe",
                          Colors.indigo,
                          () {},
                        ),
                      ]),
                      _buildMenuSection("Support", [
                        _MenuItem(
                          Icons.help_outline,
                          "Help Center",
                          "FAQs & support",
                          Colors.teal,
                          () {},
                        ),
                        _MenuItem(
                          Icons.star,
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
                  Icons.account_circle,
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
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.25)),
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
              const SizedBox(width: 8),
              GestureDetector(
                onTap: () async {
                  final updated = await Navigator.push<bool>(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const BuyerEditProfileScreen(),
                    ),
                  );
                  if (updated == true && mounted) {
                    await authProvider.refreshUser();
                    buyerProvider.fetchProfile();
                    setState(() {});
                  }
                },
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.3),
                    ),
                  ),
                  child: const Icon(
                    Icons.edit,
                    size: 18,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              _buildStat("Orders", "View", Icons.inventory_2_outlined),
              const SizedBox(width: 8),
              _buildStat("Reviews", "Share", Icons.star),
              const SizedBox(width: 8),
              _buildStat("Points", "Earn", Icons.flash_on),
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
                                Icons.chevron_right,
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
                      Icons.logout,
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
            Icon(Icons.logout, size: 18, color: Colors.red),
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

  // ─── Addresses Section ────────────────────────────────────────────────────

  Widget _buildAddressesSection() {
    // Sort addresses: default first, then by ID
    final sortedAddresses = List<dynamic>.from(_addresses);
    sortedAddresses.sort((a, b) {
      final aIsDefault = a['is_default'] == true ? 1 : 0;
      final bIsDefault = b['is_default'] == true ? 1 : 0;
      // Default addresses first (1 - 0 = 1, so b comes before a)
      final defaultCompare = bIsDefault.compareTo(aIsDefault);
      if (defaultCompare != 0) return defaultCompare;
      // Then sort by ID (newest first if you want, or oldest first)
      return (a['id'] ?? 0).compareTo(b['id'] ?? 0);
    });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10, top: 20),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'DELIVERY ADDRESSES',
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
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [_primaryDark, _primary],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: _primary.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.add, size: 12, color: Colors.white),
                      SizedBox(width: 5),
                      Text(
                        'Add New',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        if (_addresses.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 20),
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
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(Icons.location_on,
                      size: 26, color: Colors.orange),
                ),
                const SizedBox(height: 14),
                const Text(
                  'No addresses yet',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: _textDark,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Add your delivery address for faster checkout',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade500,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                GestureDetector(
                  onTap: _showAddAddressSheet,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 10),
                    decoration: BoxDecoration(
                      color: _primary.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _primary.withValues(alpha: 0.2),
                      ),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.add, size: 13, color: _primary),
                        SizedBox(width: 6),
                        Text(
                          'Add Address',
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
          )
        else
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
              itemCount: sortedAddresses.length,
              separatorBuilder: (context, index) => Divider(
                height: 1,
                color: Colors.grey.withValues(alpha: 0.08),
                indent: 16,
                endIndent: 16,
              ),
              itemBuilder: (context, index) {
                final address = sortedAddresses[index];
                final isDefault = address['is_default'] == true;
                final label = address['label'] ?? 'Address';

                IconData addressIcon;
                Color iconColor;
                switch (label.toLowerCase()) {
                  case 'home':
                    addressIcon = Icons.home;
                    iconColor = Colors.blue;
                    break;
                  case 'work':
                    addressIcon = Icons.work;
                    iconColor = Colors.green;
                    break;
                  case 'office':
                    addressIcon = Icons.business;
                    iconColor = Colors.indigo;
                    break;
                  default:
                    addressIcon = Icons.location_on;
                    iconColor = Colors.orange;
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
                          color: iconColor.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Icon(addressIcon, size: 20, color: iconColor),
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
                            Icons.delete_outline,
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

