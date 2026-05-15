import 'dart:io';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:image_picker/image_picker.dart';
import '../../services/api_service.dart';

/// Return & Refund Screen
class ReturnRefundScreen extends StatefulWidget {
  final dynamic order;

  const ReturnRefundScreen({super.key, required this.order});

  @override
  State<ReturnRefundScreen> createState() => _ReturnRefundScreenState();
}

class _ReturnRefundScreenState extends State<ReturnRefundScreen>
    with SingleTickerProviderStateMixin {
  // Step controller
  int _currentStep = 0; // 0 = Select Items, 1 = Reason & Evidence, 2 = Review

  // Form state
  final List<_ReturnItem> _returnItems = [];
  String? _selectedReason;
  String _additionalDetails = '';
  final List<File> _evidencePhotos = [];
  String _refundMethod = 'original';
  bool _isSubmitting = false;
  bool _isSubmitted = false;

  final TextEditingController _detailsController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  final List<String> _returnReasons = [
    'Item damaged or defective',
    'Wrong item received',
    'Item not as described',
    'Missing parts or accessories',
    'Changed my mind',
    'Item arrived too late',
    'Duplicate order',
    'Other',
  ];

  @override
  void initState() {
    super.initState();
    // Initialize return items from order
    for (var item in widget.order.items) {
      _returnItems.add(_ReturnItem(
        item: item,
        isSelected: false,
        quantity: 1,
      ));
    }
  }

  @override
  void dispose() {
    _detailsController.dispose();
    super.dispose();
  }

  int get _selectedItemCount => _returnItems.where((i) => i.isSelected).length;

  bool get _canProceedStep0 => _selectedItemCount > 0;

  bool get _canProceedStep1 =>
      _selectedReason != null && _selectedReason!.isNotEmpty;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      body: Column(
        children: [
          _buildHeader(),
          if (!_isSubmitted) _buildStepIndicator(),
          Expanded(
            child: _isSubmitted ? _buildSuccessView() : _buildStepContent(),
          ),
          if (!_isSubmitted) _buildBottomBar(),
        ],
      ),
    );
  }

  // ─────────────────────────── HEADER ───────────────────────────

  Widget _buildHeader() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
        ),
      ),
      padding: EdgeInsets.fromLTRB(
        12,
        MediaQuery.of(context).padding.top + 8,
        12,
        16,
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(LucideIcons.arrowLeft, color: Colors.white),
            onPressed: () {
              if (_currentStep > 0 && !_isSubmitted) {
                setState(() => _currentStep--);
              } else {
                Navigator.pop(context);
              }
            },
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
            iconSize: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Return & Refund',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Order #${widget.order.id}',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                const Icon(LucideIcons.shieldCheck,
                    color: Colors.white, size: 13),
                const SizedBox(width: 5),
                Text(
                  'Protected',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.9),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────── STEP INDICATOR ───────────────────────────

  Widget _buildStepIndicator() {
    final steps = ['Select Items', 'Reason', 'Review'];
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        children: steps.asMap().entries.map((entry) {
          final idx = entry.key;
          final label = entry.value;
          final isCompleted = idx < _currentStep;
          final isActive = idx == _currentStep;
          final isLast = idx == steps.length - 1;

          return Expanded(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isCompleted
                              ? const Color(0xFF1e4db7)
                              : isActive
                                  ? const Color(0xFF1e4db7)
                                  : Colors.grey.shade200,
                          boxShadow: isActive
                              ? [
                                  BoxShadow(
                                    color: const Color(0xFF1e4db7)
                                        .withValues(alpha: 0.3),
                                    blurRadius: 8,
                                    spreadRadius: 1,
                                  )
                                ]
                              : null,
                        ),
                        child: Center(
                          child: isCompleted
                              ? const Icon(LucideIcons.check,
                                  size: 14, color: Colors.white)
                              : Text(
                                  '${idx + 1}',
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                    color: isActive
                                        ? Colors.white
                                        : Colors.grey.shade400,
                                  ),
                                ),
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        label,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight:
                              isActive ? FontWeight.bold : FontWeight.normal,
                          color: isActive
                              ? const Color(0xFF1e4db7)
                              : isCompleted
                                  ? const Color(0xFF1e4db7)
                                  : Colors.grey.shade400,
                        ),
                      ),
                    ],
                  ),
                ),
                if (!isLast)
                  Expanded(
                    child: Container(
                      height: 2,
                      margin: const EdgeInsets.only(bottom: 18),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(2),
                        color: idx < _currentStep
                            ? const Color(0xFF1e4db7)
                            : Colors.grey.shade200,
                      ),
                    ),
                  ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  // ─────────────────────────── STEP CONTENT ───────────────────────────

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return _buildStep0SelectItems();
      case 1:
        return _buildStep1ReasonEvidence();
      case 2:
        return _buildStep2Review();
      default:
        return const SizedBox();
    }
  }

  // ── STEP 0: SELECT ITEMS ──

  Widget _buildStep0SelectItems() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionCard(
            icon: LucideIcons.packageSearch,
            title: 'Select Items to Return',
            subtitle: 'Choose the items you want to return',
            child: Column(
              children: _returnItems.asMap().entries.map((entry) {
                final idx = entry.key;
                final returnItem = entry.value;
                return _buildItemSelector(returnItem, idx);
              }).toList(),
            ),
          ),
          const SizedBox(height: 16),
          _buildReturnPolicyCard(),
        ],
      ),
    );
  }

  Widget _buildItemSelector(_ReturnItem returnItem, int index) {
    final item = returnItem.item;
    final isSelected = returnItem.isSelected;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isSelected ? const Color(0xFF1e4db7) : Colors.grey.shade200,
          width: isSelected ? 2 : 1,
        ),
        color: isSelected
            ? const Color(0xFF1e4db7).withValues(alpha: 0.04)
            : Colors.white,
      ),
      child: InkWell(
        onTap: () {
          setState(() {
            _returnItems[index].isSelected = !isSelected;
          });
        },
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color:
                      isSelected ? const Color(0xFF1e4db7) : Colors.transparent,
                  border: Border.all(
                    color: isSelected
                        ? const Color(0xFF1e4db7)
                        : Colors.grey.shade300,
                    width: 2,
                  ),
                ),
                child: isSelected
                    ? const Icon(Icons.check, size: 13, color: Colors.white)
                    : null,
              ),
              const SizedBox(width: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Container(
                  width: 54,
                  height: 54,
                  color: Colors.grey.shade100,
                  child: const Icon(Icons.image, color: Colors.grey, size: 22),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.productName,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: isSelected
                            ? const Color(0xFF1e4db7)
                            : const Color(0xFF1F2937),
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 3),
                    Text(
                      '₱${item.price.toStringAsFixed(2)}  ×  ${item.quantity}',
                      style:
                          TextStyle(color: Colors.grey.shade500, fontSize: 11),
                    ),
                  ],
                ),
              ),
              if (isSelected) ...[
                const SizedBox(width: 8),
                _buildQuantitySelector(returnItem, index),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuantitySelector(_ReturnItem returnItem, int index) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _qtyButton(
            LucideIcons.minus,
            () {
              if (_returnItems[index].quantity > 1) {
                setState(() => _returnItems[index].quantity--);
              }
            },
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Text(
              '${returnItem.quantity}',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 13,
                color: Color(0xFF1e4db7),
              ),
            ),
          ),
          _qtyButton(
            LucideIcons.plus,
            () {
              if (_returnItems[index].quantity < returnItem.item.quantity) {
                setState(() => _returnItems[index].quantity++);
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _qtyButton(IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(6),
        child: Icon(icon, size: 14, color: const Color(0xFF1e4db7)),
      ),
    );
  }

  Widget _buildReturnPolicyCard() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1e4db7).withValues(alpha: 0.06),
            const Color(0xFF1a2f6b).withValues(alpha: 0.03),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border:
            Border.all(color: const Color(0xFF1e4db7).withValues(alpha: 0.15)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(7),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e4db7).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(LucideIcons.info,
                    color: Color(0xFF1e4db7), size: 15),
              ),
              const SizedBox(width: 10),
              const Text(
                'Return Policy',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  color: Color(0xFF1a2f6b),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...[
            'Returns accepted within 7 days of delivery.',
            'Item must be unused and in original packaging.',
            'Refunds processed within 3–5 business days.',
          ].map(
            (text) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(LucideIcons.checkCircle2,
                      size: 13, color: Color(0xFF1e4db7)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      text,
                      style:
                          TextStyle(fontSize: 12, color: Colors.grey.shade700),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── STEP 1: REASON & EVIDENCE ──

  Widget _buildStep1ReasonEvidence() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildSectionCard(
            icon: LucideIcons.messageSquare,
            title: 'Return Reason',
            subtitle: 'Tell us why you\'re returning this item',
            child: Column(
              children: _returnReasons.map((reason) {
                final isSelected = _selectedReason == reason;
                return GestureDetector(
                  onTap: () => setState(() => _selectedReason = reason),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 14, vertical: 12),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected
                            ? const Color(0xFF1e4db7)
                            : Colors.grey.shade200,
                        width: isSelected ? 2 : 1,
                      ),
                      color: isSelected
                          ? const Color(0xFF1e4db7).withValues(alpha: 0.05)
                          : Colors.white,
                    ),
                    child: Row(
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 18,
                          height: 18,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: isSelected
                                ? const Color(0xFF1e4db7)
                                : Colors.transparent,
                            border: Border.all(
                              color: isSelected
                                  ? const Color(0xFF1e4db7)
                                  : Colors.grey.shade400,
                              width: 2,
                            ),
                          ),
                          child: isSelected
                              ? const Icon(Icons.check,
                                  size: 10, color: Colors.white)
                              : null,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            reason,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: isSelected
                                  ? FontWeight.w600
                                  : FontWeight.normal,
                              color: isSelected
                                  ? const Color(0xFF1e4db7)
                                  : const Color(0xFF1F2937),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 16),
          _buildSectionCard(
            icon: LucideIcons.fileText,
            title: 'Additional Details',
            subtitle: 'Describe the issue in more detail (optional)',
            child: TextField(
              controller: _detailsController,
              maxLines: 4,
              onChanged: (v) => _additionalDetails = v,
              decoration: InputDecoration(
                hintText:
                    'e.g. The item arrived with a crack on the left side...',
                hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                filled: true,
                fillColor: const Color(0xFFF8FAFF),
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
                  borderSide: const BorderSide(color: Color(0xFF1e4db7)),
                ),
                contentPadding: const EdgeInsets.all(14),
              ),
              style: const TextStyle(fontSize: 13),
            ),
          ),
          const SizedBox(height: 16),
          _buildSectionCard(
            icon: LucideIcons.camera,
            title: 'Evidence Photos',
            subtitle: 'Upload photos to support your return (optional, max 5)',
            child: Column(
              children: [
                if (_evidencePhotos.isNotEmpty) ...[
                  SizedBox(
                    height: 90,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _evidencePhotos.length,
                      itemBuilder: (ctx, i) {
                        return Stack(
                          children: [
                            Container(
                              margin: const EdgeInsets.only(right: 8),
                              width: 84,
                              height: 84,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(10),
                                image: DecorationImage(
                                  image: FileImage(_evidencePhotos[i]),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                            Positioned(
                              top: 4,
                              right: 12,
                              child: GestureDetector(
                                onTap: () =>
                                    setState(() => _evidencePhotos.removeAt(i)),
                                child: Container(
                                  width: 20,
                                  height: 20,
                                  decoration: const BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: Colors.red,
                                  ),
                                  child: const Icon(Icons.close,
                                      size: 12, color: Colors.white),
                                ),
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
                if (_evidencePhotos.length < 5)
                  InkWell(
                    onTap: _pickImage,
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 20),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: const Color(0xFF1e4db7).withValues(alpha: 0.3),
                          style: BorderStyle.solid,
                          width: 1.5,
                        ),
                        color: const Color(0xFF1e4db7).withValues(alpha: 0.03),
                      ),
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1e4db7)
                                  .withValues(alpha: 0.08),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(LucideIcons.imagePlus,
                                color: Color(0xFF1e4db7), size: 22),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Tap to upload photo',
                            style: TextStyle(
                              color: Color(0xFF1e4db7),
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'JPG, PNG up to 10MB',
                            style: TextStyle(
                                color: Colors.grey.shade500, fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _buildRefundMethodCard(),
        ],
      ),
    );
  }

  Widget _buildRefundMethodCard() {
    final methods = [
      (
        'original',
        LucideIcons.creditCard,
        'Original Payment Method',
        '3–5 business days'
      ),
      ('wallet', LucideIcons.wallet, 'Store Wallet', 'Instant refund'),
    ];

    return _buildSectionCard(
      icon: LucideIcons.refreshCcw,
      title: 'Refund Method',
      subtitle: 'Choose how you\'d like to receive your refund',
      child: Column(
        children: methods.map((method) {
          final isSelected = _refundMethod == method.$1;
          return GestureDetector(
            onTap: () => setState(() => _refundMethod = method.$1),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isSelected
                      ? const Color(0xFF1e4db7)
                      : Colors.grey.shade200,
                  width: isSelected ? 2 : 1,
                ),
                color: isSelected
                    ? const Color(0xFF1e4db7).withValues(alpha: 0.05)
                    : Colors.white,
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(9),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? const Color(0xFF1e4db7)
                          : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      method.$2,
                      size: 18,
                      color: isSelected ? Colors.white : Colors.grey.shade500,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          method.$3,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                            color: isSelected
                                ? const Color(0xFF1e4db7)
                                : const Color(0xFF1F2937),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          method.$4,
                          style: TextStyle(
                              fontSize: 11, color: Colors.grey.shade500),
                        ),
                      ],
                    ),
                  ),
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 20,
                    height: 20,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isSelected
                          ? const Color(0xFF1e4db7)
                          : Colors.transparent,
                      border: Border.all(
                        color: isSelected
                            ? const Color(0xFF1e4db7)
                            : Colors.grey.shade300,
                        width: 2,
                      ),
                    ),
                    child: isSelected
                        ? const Icon(Icons.check, size: 11, color: Colors.white)
                        : null,
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── STEP 2: REVIEW ──

  Widget _buildStep2Review() {
    final selectedItems = _returnItems.where((i) => i.isSelected).toList();
    final totalRefund = selectedItems.fold<double>(
      0,
      (sum, i) => sum + (i.item.price * i.quantity),
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Summary banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(LucideIcons.packageSearch,
                      color: Colors.white, size: 24),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Return Summary',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        '${selectedItems.length} item${selectedItems.length > 1 ? 's' : ''} · ₱${totalRefund.toStringAsFixed(2)} estimated refund',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Items being returned
          _buildSectionCard(
            icon: LucideIcons.shoppingBag,
            title: 'Items to Return',
            child: Column(
              children: selectedItems.map((ri) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Container(
                          width: 44,
                          height: 44,
                          color: Colors.grey.shade100,
                          child: const Icon(Icons.image,
                              size: 18, color: Colors.grey),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              ri.item.productName,
                              style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                  color: Color(0xFF1F2937)),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              'Qty: ${ri.quantity}',
                              style: TextStyle(
                                  fontSize: 11, color: Colors.grey.shade500),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        '₱${(ri.item.price * ri.quantity).toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                          color: Color(0xFF1e4db7),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 16),

          // Reason
          _buildSectionCard(
            icon: LucideIcons.messageSquare,
            title: 'Return Reason',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1e4db7).withValues(alpha: 0.07),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _selectedReason ?? '',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF1e4db7),
                    ),
                  ),
                ),
                if (_additionalDetails.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    _additionalDetails,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Refund method
          _buildSectionCard(
            icon: LucideIcons.refreshCcw,
            title: 'Refund Details',
            child: Column(
              children: [
                _reviewRow(
                    'Refund Method',
                    _refundMethod == 'original'
                        ? 'Original Payment Method'
                        : 'Store Wallet'),
                const SizedBox(height: 8),
                _reviewRow(
                    'Processing Time',
                    _refundMethod == 'original'
                        ? '3–5 business days'
                        : 'Instant'),
                const Divider(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Estimated Refund',
                      style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: Color(0xFF1F2937)),
                    ),
                    Text(
                      '₱${totalRefund.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                        color: Color(0xFF1e4db7),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Evidence photos count
          if (_evidencePhotos.isNotEmpty)
            _buildSectionCard(
              icon: LucideIcons.image,
              title: 'Evidence Photos',
              child: Row(
                children: [
                  ..._evidencePhotos.take(3).map(
                        (f) => Container(
                          margin: const EdgeInsets.only(right: 8),
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            image: DecorationImage(
                              image: FileImage(f),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      ),
                  if (_evidencePhotos.length > 3)
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                      ),
                      child: Center(
                        child: Text(
                          '+${_evidencePhotos.length - 3}',
                          style: const TextStyle(
                            color: Color(0xFF1e4db7),
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),

          const SizedBox(height: 8),

          // Disclaimer
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.amber.withValues(alpha: 0.3)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(LucideIcons.alertTriangle,
                    size: 15, color: Colors.amber),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'By submitting, you confirm that the information provided is accurate. False claims may result in account suspension.',
                    style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _reviewRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
        Text(value,
            style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: Color(0xFF1F2937))),
      ],
    );
  }

  // ─────────────────────────── SUCCESS VIEW ───────────────────────────

  Widget _buildSuccessView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: const Duration(milliseconds: 600),
              curve: Curves.elasticOut,
              builder: (ctx, v, child) =>
                  Transform.scale(scale: v, child: child),
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: const LinearGradient(
                    colors: [Color(0xFF43a047), Color(0xFF1b5e20)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.green.withValues(alpha: 0.3),
                      blurRadius: 24,
                      spreadRadius: 4,
                    ),
                  ],
                ),
                child: const Icon(LucideIcons.checkCircle2,
                    color: Colors.white, size: 48),
              ),
            ),
            const SizedBox(height: 28),
            const Text(
              'Request Submitted!',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Your return & refund request has been submitted successfully. Our team will review it within 1–2 business days.',
              style: TextStyle(
                  fontSize: 14, color: Colors.grey.shade600, height: 1.6),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 8,
                  ),
                ],
              ),
              child: Column(
                children: [
                  _successInfoRow(LucideIcons.hash, 'Request ID',
                      'RET-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}'),
                  const Divider(height: 20),
                  _successInfoRow(LucideIcons.clock, 'Status', 'Under Review'),
                  const Divider(height: 20),
                  _successInfoRow(LucideIcons.calendar, 'Expected Resolution',
                      '${DateTime.now().add(const Duration(days: 2)).toString().split(' ')[0]}'),
                ],
              ),
            ),
            const SizedBox(height: 28),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(LucideIcons.home, size: 18),
                label: const Text(
                  'Back to Order',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1e4db7),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 0,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _successInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
            color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 14, color: const Color(0xFF1e4db7)),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(label,
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
        ),
        Text(
          value,
          style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937)),
        ),
      ],
    );
  }

  // ─────────────────────────── BOTTOM BAR ───────────────────────────

  Widget _buildBottomBar() {
    final canProceed = _currentStep == 0
        ? _canProceedStep0
        : _currentStep == 1
            ? _canProceedStep1
            : true;

    final isLastStep = _currentStep == 2;

    return Container(
      padding: EdgeInsets.fromLTRB(
          16, 12, 16, MediaQuery.of(context).padding.bottom + 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 12,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Row(
        children: [
          if (_currentStep > 0) ...[
            OutlinedButton(
              onPressed: () => setState(() => _currentStep--),
              style: OutlinedButton.styleFrom(
                padding:
                    const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
                side: BorderSide(color: Colors.grey.shade300),
                foregroundColor: Colors.grey.shade700,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: const Text('Back',
                  style: TextStyle(fontWeight: FontWeight.w600)),
            ),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: ElevatedButton(
              onPressed: canProceed
                  ? () {
                      if (isLastStep) {
                        _submitRequest();
                      } else {
                        setState(() => _currentStep++);
                      }
                    }
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1e4db7),
                disabledBackgroundColor: Colors.grey.shade200,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
                elevation: 0,
              ),
              child: _isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          isLastStep ? 'Submit Request' : 'Continue',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        const SizedBox(width: 6),
                        Icon(
                          isLastStep
                              ? LucideIcons.send
                              : LucideIcons.arrowRight,
                          size: 16,
                        ),
                      ],
                    ),
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────── HELPERS ───────────────────────────

  Widget _buildSectionCard({
    required IconData icon,
    required String title,
    String? subtitle,
    required Widget child,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: const Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    if (subtitle != null)
                      Text(
                        subtitle,
                        style: TextStyle(
                            fontSize: 11, color: Colors.grey.shade500),
                      ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }

  Future<void> _pickImage() async {
    final picked = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 80,
    );
    if (picked != null) {
      setState(() => _evidencePhotos.add(File(picked.path)));
    }
  }

  Future<void> _submitRequest() async {
    setState(() => _isSubmitting = true);

    try {
      final selectedItems = _returnItems.where((i) => i.isSelected).toList();
      
      // Upload images first
      List<String> uploadedImageUrls = [];
      if (_evidencePhotos.isNotEmpty) {
        for (var photo in _evidencePhotos) {
          final url = await ApiService.uploadReturnEvidence(photo);
          if (url != null) {
            uploadedImageUrls.add(url);
          }
        }
      }
      
      // Prepare request data
      final requestData = {
        'items': selectedItems.map((ri) => {
          'order_item_id': ri.item.id,
          'quantity': ri.quantity,
          'reason': _selectedReason,
        }).toList(),
        'reason': _selectedReason,
        'additional_details': _additionalDetails,
        'refund_method': _refundMethod,
        'images': uploadedImageUrls,
      };

      // Call API
      final response = await ApiService.createReturnRequest(
        widget.order.id,
        requestData,
      );

      if (mounted) {
        if (response['success'] == true) {
          setState(() {
            _isSubmitting = false;
            _isSubmitted = true;
          });
        } else {
          setState(() => _isSubmitting = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(response['error'] ?? 'Failed to submit request'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}

// ─────────────────────────── MODEL ───────────────────────────

class _ReturnItem {
  final dynamic item;
  bool isSelected;
  int quantity;

  _ReturnItem({
    required this.item,
    required this.isSelected,
    required this.quantity,
  });
}
