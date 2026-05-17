// rider_active_delivery_screen.dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import '../../services/api_service.dart';
import '../../services/delivery_fee_service.dart';
import '../../models/order.dart';
import '../../widgets/skeleton_loader.dart';

class RiderActiveDeliveryScreen extends StatefulWidget {
  const RiderActiveDeliveryScreen({super.key});

  @override
  State<RiderActiveDeliveryScreen> createState() =>
      _RiderActiveDeliveryScreenState();
}

class _RiderActiveDeliveryScreenState extends State<RiderActiveDeliveryScreen>
    with SingleTickerProviderStateMixin {
  List<Order> _activeOrders = [];
  Order? _selectedOrder;
  bool _isLoading = true;
  bool _isUpdating = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnim;

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _surface = Color(0xFFFFFFFF);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _green = Color(0xFF059669);
  static const Color _amber = Color(0xFFD97706);
  static const Color _blue = Color(0xFF2563EB);
  static const Color _violet = Color(0xFF7C3AED);

  // Step definitions
  static const List<_DeliveryStep> _steps = [
    _DeliveryStep(
        'to_ship', 'Order Accepted', Icons.check_circle_rounded, _violet),
    _DeliveryStep(
        'out_for_delivery', 'On the Way', Icons.two_wheeler_rounded, _primary),
    _DeliveryStep('delivered', 'Delivered!', Icons.celebration_rounded, _green),
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    _fetchActive();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _fetchActive() async {
    if (!mounted) return;
    setState(() => _isLoading = true);
    try {
      final data = await ApiService.getRiderOrders();
      debugPrint('📦 Fetched ${data.length} orders');
      final orders = data
          .map((j) => Order.fromJson(j))
          .where((o) =>
              o.status == 'to_ship' ||
              o.status == 'picked_up' ||
              o.status == 'out_for_delivery' ||
              o.status == 'in_transit')
          .toList();
      if (mounted) {
        setState(() {
          _activeOrders = orders;
          // Only auto-select if no order is currently selected or if selected order is no longer active
          if (_selectedOrder == null ||
              !orders.any((o) => o.id == _selectedOrder!.id)) {
            _selectedOrder = orders.isNotEmpty ? orders.first : null;
          } else {
            // Update the selected order with fresh data from API
            _selectedOrder = orders.firstWhere(
              (o) => o.id == _selectedOrder!.id,
              orElse: () => _selectedOrder!,
            );
          }
          if (_selectedOrder != null) {
            debugPrint(
                '✅ Selected order #${_selectedOrder!.id}, status: ${_selectedOrder!.status}, riderId: ${_selectedOrder!.riderId}');
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('❌ Error fetching orders: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  int get _currentStepIndex {
    if (_selectedOrder == null) return 0;
    if (_selectedOrder!.status == 'delivered') return 2;
    if (_selectedOrder!.status == 'out_for_delivery' ||
        _selectedOrder!.status == 'in_transit') return 1;
    if (_selectedOrder!.status == 'to_ship') return 0;
    return 0;
  }

  Future<void> _advanceStep() async {
    if (_selectedOrder == null || _isUpdating) return;
    HapticFeedback.mediumImpact();

    final current = _selectedOrder!.status;

    // Determine next action based on current status
    if (current == 'to_ship') {
      // Order accepted - show photo proof dialog for delivery
      _showPhotoProofDialog();
    } else if (current == 'out_for_delivery' || current == 'in_transit') {
      // Rider is at delivery location - show photo proof dialog
      _showPhotoProofDialog();
    }
  }

  Future<void> _showPhotoProofDialog() async {
    final ImagePicker picker = ImagePicker();
    File? proofPhoto;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Container(
          decoration: const BoxDecoration(
            color: _surface,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: _green.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.camera_alt_rounded,
                            color: _green, size: 24),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Delivery Proof',
                                style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w800,
                                    color: _textPrimary)),
                            Text('Take a photo of the delivered items',
                                style:
                                    TextStyle(fontSize: 13, color: _textSub)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  if (proofPhoto != null)
                    Container(
                      height: 200,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: _border),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: Image.file(proofPhoto!, fit: BoxFit.cover),
                      ),
                    )
                  else
                    Container(
                      height: 200,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: _bg,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: _border, width: 2),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo_rounded,
                              size: 48, color: _textSub.withValues(alpha: 0.5)),
                          const SizedBox(height: 12),
                          const Text('No photo selected',
                              style: TextStyle(
                                  color: _textSub,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500)),
                        ],
                      ),
                    ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () async {
                        final photo = await picker.pickImage(
                            source: ImageSource.camera, imageQuality: 80);
                        if (photo != null) {
                          setModalState(() {
                            proofPhoto = File(photo.path);
                          });
                        }
                      },
                      icon: const Icon(Icons.camera_alt_rounded, size: 20),
                      label: const Text('Take Photo',
                          style: TextStyle(fontWeight: FontWeight.w700)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _primary,
                        side: const BorderSide(color: _primary, width: 1.5),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: proofPhoto == null
                          ? null
                          : () {
                              final photo = proofPhoto!;
                              Navigator.pop(context);
                              _submitDeliveryWithProof(photo);
                            },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _green,
                        foregroundColor: Colors.white,
                        disabledBackgroundColor: _green.withValues(alpha: 0.5),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle_rounded, size: 20),
                          SizedBox(width: 10),
                          Text('Confirm Delivery',
                              style: TextStyle(
                                  fontSize: 15, fontWeight: FontWeight.w800)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submitDeliveryWithProof(File proofPhoto) async {
    if (_selectedOrder == null || _isUpdating) return;

    debugPrint('📦 Submitting delivery for order #${_selectedOrder!.id}');
    setState(() => _isUpdating = true);
    try {
      // Upload proof photo
      debugPrint('📷 Uploading proof photo...');
      await ApiService.uploadDeliveryProof(
        orderId: _selectedOrder!.id,
        file: proofPhoto,
      );
      debugPrint('✅ Photo uploaded successfully');

      // Mark as delivered
      debugPrint('🚚 Marking order as delivered...');
      final result = await ApiService.markOrderAsDelivered(_selectedOrder!.id);
      debugPrint('📤 Result: $result');
      if (result['success'] != true) {
        throw Exception(result['error'] ?? 'Failed to mark as delivered');
      }

      if (!mounted) return;
      _showSnack('🎉 Delivered successfully!', _green);

      // Clear selected order and refresh list
      setState(() {
        _selectedOrder = null;
      });
      await _fetchActive();
    } on ApiException catch (e) {
      debugPrint('❌ ApiException: ${e.message} (${e.statusCode})');
      if (mounted) {
        _showSnack('Error: ${e.message}', Colors.red.shade600);
      }
    } catch (e) {
      debugPrint('❌ Error: $e');
      if (mounted) _showSnack('Error: $e', Colors.red.shade600);
    } finally {
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  void _showSnack(String msg, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
      backgroundColor: color,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      margin: const EdgeInsets.all(16),
      duration: const Duration(seconds: 3),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: _isLoading
          ? _buildSkeletonLoader()
          : _activeOrders.isEmpty
              ? _buildEmpty()
              : _buildDeliveryFlow(),
    );
  }

  // ── Skeleton Loading ─────────────────────────
  Widget _buildSkeletonLoader() {
    return Column(
      children: [
        // App bar skeleton
        Container(
          color: _surface,
          padding: EdgeInsets.only(
            top: MediaQuery.of(context).padding.top + 12,
            bottom: 12,
            left: 16,
            right: 14,
          ),
          child: Row(
            children: [
              SkeletonLoader(
                width: 38,
                height: 38,
                borderRadius: BorderRadius.circular(12),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SkeletonLoader(
                      height: 18,
                      width: 140,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    const SizedBox(height: 4),
                    SkeletonLoader(
                      height: 11,
                      width: 160,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ],
                ),
              ),
              SkeletonLoader(
                width: 36,
                height: 36,
                borderRadius: BorderRadius.circular(12),
              ),
            ],
          ),
        ),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
            child: Column(
              children: [
                // Status hero card skeleton
                SkeletonLoader(
                  height: 160,
                  borderRadius: BorderRadius.circular(24),
                ),
                const SizedBox(height: 20),
                // Step tracker skeleton
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: _surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _border),
                  ),
                  child: Column(
                    children: List.generate(5, (i) {
                      return Column(
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Column(
                                children: [
                                  SkeletonLoader(
                                    width: 40,
                                    height: 40,
                                    borderRadius: BorderRadius.circular(13),
                                  ),
                                  if (i < 4)
                                    Container(
                                      width: 2,
                                      height: 28,
                                      color: _border,
                                    ),
                                ],
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Padding(
                                  padding: EdgeInsets.only(
                                    top: 8,
                                    bottom: i < 4 ? 24 : 0,
                                  ),
                                  child: Row(
                                    children: [
                                      SkeletonLoader(
                                        height: 13,
                                        width: 100,
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      const Spacer(),
                                      SkeletonLoader(
                                        height: 20,
                                        width: 50,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      );
                    }),
                  ),
                ),
                const SizedBox(height: 20),
                // Order details skeleton
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: _surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          SkeletonLoader(
                            width: 15,
                            height: 15,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          const SizedBox(width: 7),
                          SkeletonLoader(
                            height: 14,
                            width: 100,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      SkeletonLoader(
                        height: 80,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      const SizedBox(height: 14),
                      SkeletonLoader(
                        height: 100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          SkeletonLoader(
                            width: 28,
                            height: 28,
                            borderRadius: BorderRadius.circular(9),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                SkeletonLoader(
                                  height: 10,
                                  width: 60,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                const SizedBox(height: 4),
                                SkeletonLoader(
                                  height: 13,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                // Route card skeleton
                SkeletonLoader(
                  height: 180,
                  borderRadius: BorderRadius.circular(20),
                ),
                const SizedBox(height: 24),
                // Action button skeleton
                SkeletonLoader(
                  height: 56,
                  borderRadius: BorderRadius.circular(16),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ── Empty ────────────────────────────────────
  Widget _buildEmpty() {
    return Center(
        child: Padding(
      padding: const EdgeInsets.all(40),
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: 1),
          duration: const Duration(milliseconds: 600),
          curve: Curves.elasticOut,
          builder: (_, v, child) => Transform.scale(scale: v, child: child),
          child: Container(
            width: 110,
            height: 110,
            decoration: BoxDecoration(
                color: _surface,
                borderRadius: BorderRadius.circular(32),
                border: Border.all(color: _border),
                boxShadow: [
                  BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 24,
                      offset: const Offset(0, 8))
                ]),
            child: const Icon(Icons.two_wheeler_rounded,
                size: 52, color: Color(0xFFCBD5E1)),
          ),
        ),
        const SizedBox(height: 28),
        const Text('No Active Delivery',
            style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: _textPrimary,
                letterSpacing: -0.4)),
        const SizedBox(height: 10),
        const Text(
          'Accept an order from the Orders tab\nto start your delivery journey.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 14, color: _textSub, height: 1.6),
        ),
        const SizedBox(height: 32),
        SizedBox(
          height: 50,
          child: ElevatedButton.icon(
            onPressed: _fetchActive,
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: const Text('Refresh',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
            style: ElevatedButton.styleFrom(
                backgroundColor: _primary,
                foregroundColor: Colors.white,
                elevation: 0,
                padding: const EdgeInsets.symmetric(horizontal: 32),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14))),
          ),
        ),
      ]),
    ));
  }

  // ── Main Delivery Flow ───────────────────────
  Widget _buildDeliveryFlow() {
    final order = _selectedOrder!;
    return CustomScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      slivers: [
        _buildAppBar(),
        SliverToBoxAdapter(
            child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
          child: Column(children: [
            // Multiple orders selector
            if (_activeOrders.length > 1) ...[
              _buildOrderSelector(),
              const SizedBox(height: 16),
            ],

            // Live status hero card
            _buildStatusHero(order),
            const SizedBox(height: 20),

            // Step tracker
            _buildStepTracker(),
            const SizedBox(height: 20),

            // Order details card
            _buildOrderDetails(order),
            const SizedBox(height: 20),

            // Route card
            _buildRouteCard(order),
            const SizedBox(height: 24),

            // CTA Button
            _buildActionButton(order),
          ]),
        )),
      ],
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      floating: true,
      snap: true,
      backgroundColor: _surface,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      shadowColor: Colors.black.withValues(alpha: 0.08),
      surfaceTintColor: Colors.transparent,
      toolbarHeight: 64,
      title: Row(children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                  color: _primary.withValues(alpha: 0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 3))
            ],
          ),
          child: const Icon(Icons.navigation_rounded,
              color: Colors.white, size: 19),
        ),
        const SizedBox(width: 12),
        const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Active Delivery',
              style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4)),
          Text('Track your current delivery',
              style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.w500)),
        ]),
      ]),
      actions: [
        GestureDetector(
          onTap: _fetchActive,
          child: Container(
            padding: const EdgeInsets.all(9),
            margin: const EdgeInsets.only(right: 14),
            decoration: BoxDecoration(
                color: _bg,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _border)),
            child: const Icon(Icons.refresh_rounded,
                size: 19, color: Color(0xFF475569)),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderSelector() {
    return SizedBox(
      height: 40,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _activeOrders.length,
        itemBuilder: (_, i) {
          final o = _activeOrders[i];
          final isSelected = o.id == _selectedOrder?.id;
          return GestureDetector(
            onTap: () => setState(() => _selectedOrder = o),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin:
                  EdgeInsets.only(right: i < _activeOrders.length - 1 ? 8 : 0),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                  color: isSelected ? _primary : _surface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                      color: isSelected ? _primary : _border, width: 1.5)),
              child: Center(
                  child: Text('Order #${o.id}',
                      style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: isSelected ? Colors.white : _textSub))),
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatusHero(Order order) {
    final stepIdx = _currentStepIndex;
    final step = _steps[stepIdx.clamp(0, _steps.length - 1)];
    final isDelivered = order.status == 'delivered';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDelivered
              ? [const Color(0xFF059669), const Color(0xFF10B981)]
              : [const Color(0xFFFA6B02), const Color(0xFFFF8534)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
              color: (isDelivered ? _green : _primary).withValues(alpha: 0.4),
              blurRadius: 28,
              offset: const Offset(0, 10))
        ],
      ),
      child: Stack(clipBehavior: Clip.none, children: [
        // BG circles
        Positioned(
            top: -30,
            right: -30,
            child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.07),
                    shape: BoxShape.circle))),
        Positioned(
            bottom: -40,
            right: 40,
            child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.04),
                    shape: BoxShape.circle))),

        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            AnimatedBuilder(
              animation: _pulseAnim,
              builder: (_, child) => Transform.scale(
                  scale: isDelivered ? 1.0 : _pulseAnim.value, child: child),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(18),
                    border:
                        Border.all(color: Colors.white.withValues(alpha: 0.3))),
                child: Icon(step.icon, color: Colors.white, size: 28),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Text('Order #${order.id}',
                      style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: 12,
                          fontWeight: FontWeight.w600)),
                  const SizedBox(height: 3),
                  Text(step.label,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.5)),
                ])),
          ]),

          const SizedBox(height: 20),

          // Mini progress bar
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Text('Progress',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.7),
                      fontSize: 11,
                      fontWeight: FontWeight.w600)),
              const Spacer(),
              Text('${(((stepIdx + 1) / _steps.length) * 100).round()}%',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w800)),
            ]),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: (stepIdx + 1) / _steps.length,
                backgroundColor: Colors.white.withValues(alpha: 0.2),
                valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                minHeight: 7,
              ),
            ),
          ]),
        ]),
      ]),
    );
  }

  Widget _buildStepTracker() {
    final currentIdx = _currentStepIndex;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 6))
          ]),
      child: Column(
        children: List.generate(_steps.length, (i) {
          final step = _steps[i];
          final isDone = i < currentIdx;
          final isCurrent = i == currentIdx;
          final isPending = i > currentIdx;
          final isLast = i == _steps.length - 1;

          return Column(children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              // Icon column
              Column(children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 350),
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: isDone
                        ? step.color
                        : isCurrent
                            ? step.color.withValues(alpha: 0.12)
                            : _bg,
                    borderRadius: BorderRadius.circular(13),
                    border: Border.all(
                      color: isDone
                          ? step.color
                          : isCurrent
                              ? step.color
                              : _border,
                      width: isCurrent ? 2 : 1,
                    ),
                  ),
                  child: Icon(
                    isDone ? Icons.check_rounded : step.icon,
                    size: 18,
                    color: isDone
                        ? Colors.white
                        : isCurrent
                            ? step.color
                            : _textSub.withValues(alpha: 0.4),
                  ),
                ),
                if (!isLast)
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 350),
                    width: 2,
                    height: 28,
                    color: isDone ? step.color.withValues(alpha: 0.4) : _border,
                  ),
              ]),
              const SizedBox(width: 14),

              // Text
              Expanded(
                  child: Padding(
                padding: EdgeInsets.only(top: 8, bottom: isLast ? 0 : 24),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(children: [
                        Text(step.label,
                            style: TextStyle(
                              fontSize: 13.5,
                              fontWeight:
                                  isCurrent ? FontWeight.w800 : FontWeight.w600,
                              color: isPending
                                  ? _textSub.withValues(alpha: 0.5)
                                  : _textPrimary,
                            )),
                        const Spacer(),
                        if (isDone)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                                color: step.color.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(8)),
                            child: Text('Done',
                                style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: step.color)),
                          )
                        else if (isCurrent)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                                color: step.color.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                    color: step.color.withValues(alpha: 0.2))),
                            child:
                                Row(mainAxisSize: MainAxisSize.min, children: [
                              Container(
                                  width: 5,
                                  height: 5,
                                  decoration: BoxDecoration(
                                      color: step.color,
                                      shape: BoxShape.circle)),
                              const SizedBox(width: 4),
                              Text('Now',
                                  style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                      color: step.color)),
                            ]),
                          ),
                      ]),
                    ]),
              )),
            ]),
          ]);
        }),
      ),
    );
  }

  Widget _buildOrderDetails(Order order) {
    // Use delivery fee from backend if available, otherwise calculate from address
    final deliveryFee = order.deliveryFee ??
        DeliveryFeeService.calculateDeliveryFeeFromAddress(
            order.shippingAddress);

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 6))
          ]),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _rowLabel('Order Details', Icons.receipt_long_rounded),
        const SizedBox(height: 14),

        // Seller Store Info
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _amber.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _amber.withValues(alpha: 0.15)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: _amber,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.store_rounded,
                        size: 14, color: Colors.white),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'SELLER STORE',
                          style: TextStyle(
                            fontSize: 9,
                            color: _textSub,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          order.sellerName ?? 'N/A',
                          style: const TextStyle(
                            fontSize: 14,
                            color: _textPrimary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              if (order.sellerAddress != null &&
                  order.sellerAddress!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.location_on_rounded,
                        size: 13, color: _amber),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        order.sellerAddress!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: _textSub,
                          fontWeight: FontWeight.w500,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),

        const SizedBox(height: 14),

        // Items List
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _blue.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _blue.withValues(alpha: 0.12)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: _blue,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.inventory_2_rounded,
                        size: 14, color: Colors.white),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'ITEMS TO DELIVER',
                    style: TextStyle(
                      fontSize: 9,
                      color: _textSub,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: _blue,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${order.items.length} ${order.items.length == 1 ? 'item' : 'items'}',
                      style: const TextStyle(
                        fontSize: 10,
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              ...order.items.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;
                return Column(
                  children: [
                    if (index > 0) ...[
                      const SizedBox(height: 8),
                      const Divider(height: 1, color: Color(0xFFE8EAF0)),
                      const SizedBox(height: 8),
                    ],
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 18,
                          height: 18,
                          decoration: BoxDecoration(
                            color: _blue.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(5),
                          ),
                          child: Center(
                            child: Text(
                              '${index + 1}',
                              style: const TextStyle(
                                fontSize: 10,
                                color: _blue,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.productName,
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: _textPrimary,
                                  fontWeight: FontWeight.w600,
                                  height: 1.3,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  if (item.size != null ||
                                      item.color != null) ...[
                                    Text(
                                      [
                                        if (item.size != null) item.size,
                                        if (item.color != null) item.color
                                      ].where((e) => e != null).join(', '),
                                      style: const TextStyle(
                                        fontSize: 11,
                                        color: _textSub,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Container(
                                      width: 3,
                                      height: 3,
                                      decoration: const BoxDecoration(
                                        color: _textSub,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                  ],
                                  Text(
                                    'Qty: ${item.quantity}',
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: _textPrimary,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    '₱${item.totalPrice.toStringAsFixed(2)}',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: _textPrimary,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              }).toList(),
            ],
          ),
        ),

        const SizedBox(height: 14),

        // Customer Info
        _infoRow(
            Icons.person_rounded, 'Customer', order.buyerName ?? 'N/A', _green),
        if (order.buyerPhone != null && order.buyerPhone!.isNotEmpty) ...[
          const SizedBox(height: 10),
          _infoRow(Icons.phone_rounded, 'Phone', order.buyerPhone!, _green),
        ],

        const SizedBox(height: 14),
        const Divider(height: 1, color: Color(0xFFF1F3F8)),
        const SizedBox(height: 14),
        Row(children: [
          Expanded(
              child: _miniStat('Order Total',
                  '₱${order.totalAmount.toStringAsFixed(2)}', _textPrimary)),
          Container(width: 1, height: 36, color: _border),
          Expanded(
            child: Column(
              children: [
                Text(
                  '₱${deliveryFee.toStringAsFixed(0)}',
                  style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: _green,
                      letterSpacing: -0.4),
                ),
                const SizedBox(height: 2),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Delivery Fee',
                        style: TextStyle(
                            fontSize: 11,
                            color: _textSub,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ],
            ),
          ),
        ]),
      ]),
    );
  }

  Widget _buildRouteCard(Order order) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _border),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 6))
          ]),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _rowLabel('Route', Icons.route_rounded),
        const SizedBox(height: 16),

        // Pickup
        _addressBlock(
          icon: Icons.store_rounded,
          label: 'PICKUP',
          address: order.sellerAddress ?? 'Not specified',
          color: _amber,
          bg: const Color(0xFFFFFBEB),
        ),

        // Dotted connector
        Padding(
          padding: const EdgeInsets.only(left: 16, top: 4, bottom: 4),
          child: Column(
              children: List.generate(
                  5,
                  (i) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Container(
                            width: 2,
                            height: 4,
                            color: i % 2 == 0
                                ? _textSub.withValues(alpha: 0.25)
                                : Colors.transparent),
                      ))),
        ),

        // Drop-off
        _addressBlock(
          icon: Icons.location_on_rounded,
          label: 'DROP-OFF',
          address: order.shippingAddress,
          color: _green,
          bg: const Color(0xFFECFDF5),
        ),
      ]),
    );
  }

  Widget _buildActionButton(Order order) {
    if (order.status == 'delivered') {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
            color: _green.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: _green.withValues(alpha: 0.2))),
        child: Column(children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
                color: _green,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                      color: _green.withValues(alpha: 0.4),
                      blurRadius: 16,
                      offset: const Offset(0, 6))
                ]),
            child: const Icon(Icons.celebration_rounded,
                color: Colors.white, size: 32),
          ),
          const SizedBox(height: 14),
          const Text('Delivery Complete! 🎉',
              style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: _green,
                  letterSpacing: -0.3)),
          const SizedBox(height: 6),
          const Text('Great job! The customer has been notified.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: _textSub, height: 1.5)),
        ]),
      );
    }

    String btnLabel;
    IconData btnIcon;
    Color btnColor;
    String hintText;

    if (order.status == 'to_ship') {
      btnLabel = 'Mark as Delivered';
      btnIcon = Icons.check_circle_rounded;
      btnColor = _green;
      hintText = 'Tap below to mark as delivered and upload proof photo.';
    } else {
      btnLabel = 'Mark as Delivered';
      btnIcon = Icons.check_circle_rounded;
      btnColor = _green;
      hintText = 'Tap below once you have handed the items to the customer.';
    }

    return Column(children: [
      // Hint text
      Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
            color: btnColor.withValues(alpha: 0.07),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: btnColor.withValues(alpha: 0.15))),
        child: Row(children: [
          Icon(Icons.info_outline_rounded, size: 15, color: btnColor),
          const SizedBox(width: 8),
          Expanded(
              child: Text(
            hintText,
            style: TextStyle(
                fontSize: 12,
                color: btnColor,
                fontWeight: FontWeight.w500,
                height: 1.4),
          )),
        ]),
      ),

      SizedBox(
        width: double.infinity,
        height: 56,
        child: ElevatedButton(
          onPressed: _isUpdating ? null : _advanceStep,
          style: ElevatedButton.styleFrom(
              backgroundColor: btnColor,
              foregroundColor: Colors.white,
              disabledBackgroundColor: btnColor.withValues(alpha: 0.5),
              elevation: 0,
              shadowColor: Colors.transparent,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16))),
          child: _isUpdating
              ? const SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(
                      color: Colors.white, strokeWidth: 2.4))
              : Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(btnIcon, size: 20),
                  const SizedBox(width: 10),
                  Text(btnLabel,
                      style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.1)),
                ]),
        ),
      ),
    ]);
  }

  // ── Helpers ──────────────────────────────────

  Widget _rowLabel(String title, IconData icon) {
    return Row(children: [
      Icon(icon, size: 15, color: _primary),
      const SizedBox(width: 7),
      Text(title,
          style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: _textPrimary,
              letterSpacing: -0.2)),
    ]);
  }

  Widget _infoRow(IconData icon, String label, String value, Color color) {
    return Row(children: [
      Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(9)),
          child: Icon(icon, size: 14, color: color)),
      const SizedBox(width: 10),
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label,
            style: const TextStyle(
                fontSize: 10,
                color: _textSub,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.3)),
        Text(value,
            style: const TextStyle(
                fontSize: 13,
                color: _textPrimary,
                fontWeight: FontWeight.w600)),
      ]),
    ]);
  }

  Widget _miniStat(String label, String value, Color valueColor) {
    return Column(children: [
      Text(value,
          style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: valueColor,
              letterSpacing: -0.4)),
      const SizedBox(height: 2),
      Text(label,
          style: const TextStyle(
              fontSize: 11, color: _textSub, fontWeight: FontWeight.w600)),
    ]);
  }

  Widget _addressBlock({
    required IconData icon,
    required String label,
    required String address,
    required Color color,
    required Color bg,
  }) {
    return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Container(
          padding: const EdgeInsets.all(9),
          decoration:
              BoxDecoration(color: bg, borderRadius: BorderRadius.circular(11)),
          child: Icon(icon, size: 16, color: color)),
      const SizedBox(width: 12),
      Expanded(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label,
            style: TextStyle(
                fontSize: 9,
                color: color,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.8)),
        const SizedBox(height: 3),
        Text(address,
            style: const TextStyle(
                fontSize: 13,
                color: _textPrimary,
                fontWeight: FontWeight.w500,
                height: 1.35),
            maxLines: 2,
            overflow: TextOverflow.ellipsis),
      ])),
    ]);
  }
}

class _DeliveryStep {
  final String status;
  final String label;
  final IconData icon;
  final Color color;
  const _DeliveryStep(this.status, this.label, this.icon, this.color);
}
