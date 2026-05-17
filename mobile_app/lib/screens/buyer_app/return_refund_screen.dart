import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_player/video_player.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import '../../config/url_config.dart';
import '../../models/order.dart';
import '../../providers/buyer_provider.dart';
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
  final List<File> _evidenceVideos = [];
  final Map<String, Uint8List> _videoThumbnails = {};
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
    final orderItems = widget.order.items;
    if (orderItems is Iterable) {
      for (final item in orderItems) {
        _returnItems.add(_ReturnItem(
          item: item,
          isSelected: false,
          quantity: 1,
        ));
      }
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
      _selectedReason != null &&
      _selectedReason!.isNotEmpty &&
      _evidencePhotos.isNotEmpty &&
      _evidenceVideos.isNotEmpty;

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
    final productName = _getItemProductName(item);
    final productImageUrl = _getItemImageUrl(item);

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
                child: productImageUrl != null && productImageUrl.isNotEmpty
                    ? Image.network(
                        productImageUrl,
                        width: 54,
                        height: 54,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          width: 54,
                          height: 54,
                          color: Colors.grey.shade100,
                          child: const Icon(Icons.image,
                              color: Colors.grey, size: 22),
                        ),
                      )
                    : Container(
                        width: 54,
                        height: 54,
                        color: Colors.grey.shade100,
                        child: const Icon(Icons.image,
                            color: Colors.grey, size: 22),
                      ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      productName,
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
            title: 'Evidence Photos & Videos',
            subtitle: 'Upload at least 1 photo and 1 video (required)',
            child: Column(
              children: [
                // Photos section
                if (_evidencePhotos.isNotEmpty) ...[
                  Row(
                    children: [
                      const Icon(LucideIcons.image,
                          size: 14, color: Color(0xFF1e4db7)),
                      const SizedBox(width: 6),
                      Text(
                        'Photos (${_evidencePhotos.length})',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1e4db7),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 90,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _evidencePhotos.length,
                      itemBuilder: (ctx, i) {
                        final photo = _evidencePhotos[i];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Stack(
                            children: [
                              _buildImageThumbnail(
                                file: photo,
                                size: 84,
                                onTap: () => _openImagePreview(photo),
                              ),
                              Positioned(
                                top: 4,
                                right: 4,
                                child: GestureDetector(
                                  onTap: () => setState(
                                      () => _evidencePhotos.removeAt(i)),
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
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                // Videos section
                if (_evidenceVideos.isNotEmpty) ...[
                  Row(
                    children: [
                      const Icon(LucideIcons.video,
                          size: 14, color: Color(0xFF1e4db7)),
                      const SizedBox(width: 6),
                      Text(
                        'Videos (${_evidenceVideos.length})',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1e4db7),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 90,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _evidenceVideos.length,
                      itemBuilder: (ctx, i) {
                        final video = _evidenceVideos[i];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Stack(
                            children: [
                              _buildVideoThumbnail(
                                file: video,
                                size: 84,
                                onTap: () => _openVideoPreview(video),
                              ),
                              Positioned(
                                top: 4,
                                right: 4,
                                child: GestureDetector(
                                  onTap: () => setState(() {
                                    final removed = _evidenceVideos.removeAt(i);
                                    _videoThumbnails.remove(removed.path);
                                  }),
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
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                // Upload buttons
                Row(
                  children: [
                    if (_evidencePhotos.length < 5)
                      Expanded(
                        child: InkWell(
                          onTap: _showImageSourceSheet,
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: _evidencePhotos.isEmpty
                                    ? Colors.red.withValues(alpha: 0.5)
                                    : const Color(0xFF1e4db7)
                                        .withValues(alpha: 0.3),
                                width: 1.5,
                              ),
                              color: const Color(0xFF1e4db7)
                                  .withValues(alpha: 0.03),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  LucideIcons.imagePlus,
                                  color: _evidencePhotos.isEmpty
                                      ? Colors.red
                                      : const Color(0xFF1e4db7),
                                  size: 20,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _evidencePhotos.isEmpty
                                      ? 'Photo *'
                                      : 'Add Photo',
                                  style: TextStyle(
                                    color: _evidencePhotos.isEmpty
                                        ? Colors.red
                                        : const Color(0xFF1e4db7),
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    if (_evidencePhotos.length < 5 &&
                        _evidenceVideos.length < 3)
                      const SizedBox(width: 8),
                    if (_evidenceVideos.length < 3)
                      Expanded(
                        child: InkWell(
                          onTap: _showVideoSourceSheet,
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: _evidenceVideos.isEmpty
                                    ? Colors.red.withValues(alpha: 0.5)
                                    : const Color(0xFF1e4db7)
                                        .withValues(alpha: 0.3),
                                width: 1.5,
                              ),
                              color: const Color(0xFF1e4db7)
                                  .withValues(alpha: 0.03),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  LucideIcons.video,
                                  color: _evidenceVideos.isEmpty
                                      ? Colors.red
                                      : const Color(0xFF1e4db7),
                                  size: 20,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _evidenceVideos.isEmpty
                                      ? 'Video *'
                                      : 'Add Video',
                                  style: TextStyle(
                                    color: _evidenceVideos.isEmpty
                                        ? Colors.red
                                        : const Color(0xFF1e4db7),
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'At least 1 photo and 1 video required',
                  style: TextStyle(
                    fontSize: 10,
                    color: (_evidencePhotos.isEmpty || _evidenceVideos.isEmpty)
                        ? Colors.red
                        : Colors.grey.shade500,
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
                final productName = _getItemProductName(ri.item);
                final productImageUrl = _getItemImageUrl(ri.item);
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: productImageUrl != null &&
                                productImageUrl.isNotEmpty
                            ? Image.network(
                                productImageUrl,
                                width: 44,
                                height: 44,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => Container(
                                  width: 44,
                                  height: 44,
                                  color: Colors.grey.shade100,
                                  child: const Icon(Icons.image,
                                      size: 18, color: Colors.grey),
                                ),
                              )
                            : Container(
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
                              productName,
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

          // Evidence photos and videos
          if (_evidencePhotos.isNotEmpty || _evidenceVideos.isNotEmpty)
            _buildSectionCard(
              icon: LucideIcons.image,
              title: 'Evidence',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_evidencePhotos.isNotEmpty) ...[
                    const Text(
                      'Photos',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1e4db7),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _evidencePhotos
                          .take(6)
                          .map(
                            (f) => _buildImageThumbnail(
                              file: f,
                              onTap: () => _openImagePreview(f),
                              size: 56,
                            ),
                          )
                          .toList(),
                    ),
                  ],
                  if (_evidencePhotos.isNotEmpty && _evidenceVideos.isNotEmpty)
                    const SizedBox(height: 12),
                  if (_evidenceVideos.isNotEmpty) ...[
                    const Text(
                      'Videos',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1e4db7),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _evidenceVideos
                          .take(3)
                          .map(
                            (f) => _buildVideoThumbnail(
                              file: f,
                              onTap: () => _openVideoPreview(f),
                              size: 56,
                            ),
                          )
                          .toList(),
                    ),
                  ],
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

  String _getItemProductName(dynamic item) {
    if (item is OrderItem) {
      return item.productName;
    }
    if (item is Map<String, dynamic>) {
      return (item['product_name'] ?? item['name'] ?? '').toString();
    }
    try {
      final value = item.productName;
      return value?.toString() ?? 'Item';
    } catch (_) {
      return 'Item';
    }
  }

  String? _getItemImageUrl(dynamic item) {
    if (item is OrderItem) {
      return UrlConfig.toAbsoluteImageUrl(item.productImage);
    }
    if (item is Map<String, dynamic>) {
      final value = item['product_image'] ?? item['image_url'] ?? item['image'];
      return UrlConfig.toAbsoluteImageUrl(value?.toString());
    }
    try {
      final value = item.productImage;
      return UrlConfig.toAbsoluteImageUrl(value?.toString());
    } catch (_) {
      return null;
    }
  }

  Widget _buildImageThumbnail({
    required File file,
    required VoidCallback onTap,
    double size = 56,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: SizedBox(
          width: size,
          height: size,
          child: kIsWeb
              ? Image.network(
                  file.path,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    color: Colors.grey.shade100,
                    child:
                        const Icon(Icons.image, color: Colors.grey, size: 22),
                  ),
                )
              : Image.file(
                  file,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    color: Colors.grey.shade100,
                    child:
                        const Icon(Icons.image, color: Colors.grey, size: 22),
                  ),
                ),
        ),
      ),
    );
  }

  Widget _buildVideoThumbnail({
    required File file,
    required VoidCallback onTap,
    double size = 56,
  }) {
    final thumb = _videoThumbnails[file.path];

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(8),
          color: const Color(0xFF1e4db7).withValues(alpha: 0.08),
        ),
        child: Stack(
          children: [
            Positioned.fill(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: thumb != null && !kIsWeb
                    ? Image.memory(
                        thumb,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          color: Colors.black.withValues(alpha: 0.05),
                          child: const Icon(
                            LucideIcons.video,
                            color: Color(0xFF1e4db7),
                            size: 24,
                          ),
                        ),
                      )
                    : Container(
                        color: Colors.black.withValues(alpha: 0.05),
                        child: const Icon(
                          LucideIcons.video,
                          color: Color(0xFF1e4db7),
                          size: 24,
                        ),
                      ),
              ),
            ),
            if (thumb != null && !kIsWeb)
              Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black.withValues(alpha: 0.25),
                      ],
                    ),
                  ),
                ),
              ),
            Positioned.fill(
              child: Align(
                alignment: Alignment.bottomRight,
                child: Container(
                  margin: const EdgeInsets.all(6),
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.55),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.play_arrow,
                      size: 12, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _openImagePreview(File file) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return Dialog(
          backgroundColor: Colors.black,
          insetPadding: const EdgeInsets.all(16),
          child: Stack(
            children: [
              InteractiveViewer(
                child: kIsWeb
                    ? Image.network(file.path, fit: BoxFit.contain)
                    : Image.file(file, fit: BoxFit.contain),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close, color: Colors.white),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _openVideoPreview(File file) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => _LocalVideoPreviewScreen(videoFile: file),
      ),
    );
  }

  void _showImageSourceSheet() {
    if (kIsWeb) {
      _pickImageFromSource(ImageSource.gallery);
      return;
    }

    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.photo_camera),
                title: const Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImageFromSource(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('Choose from Gallery'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImageFromSource(ImageSource.gallery);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showVideoSourceSheet() {
    if (kIsWeb) {
      _pickVideoFromSource(ImageSource.gallery);
      return;
    }

    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.videocam),
                title: const Text('Record Video'),
                onTap: () {
                  Navigator.pop(context);
                  _pickVideoFromSource(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.video_library),
                title: const Text('Choose from Gallery'),
                onTap: () {
                  Navigator.pop(context);
                  _pickVideoFromSource(ImageSource.gallery);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _pickImageFromSource(ImageSource source) async {
    final picked = await _picker.pickImage(
      source: source,
      imageQuality: 80,
    );
    if (picked != null) {
      setState(() => _evidencePhotos.add(File(picked.path)));
    }
  }

  Future<void> _pickVideoFromSource(ImageSource source) async {
    final picked = await _picker.pickVideo(
      source: source,
      maxDuration: const Duration(minutes: 2),
    );
    if (picked != null) {
      final file = File(picked.path);
      setState(() => _evidenceVideos.add(file));
      _generateVideoThumbnail(file);
    }
  }

  Future<void> _generateVideoThumbnail(File file) async {
    if (kIsWeb) return;

    try {
      final thumb = await VideoThumbnail.thumbnailData(
        video: file.path,
        imageFormat: ImageFormat.JPEG,
        maxWidth: 256,
        quality: 60,
      );

      if (!mounted || thumb == null) return;
      setState(() {
        _videoThumbnails[file.path] = thumb;
      });
    } catch (_) {
      // Keep icon fallback when thumbnail generation fails.
    }
  }

  Future<void> _submitRequest() async {
    setState(() => _isSubmitting = true);

    try {
      final selectedItems = _returnItems.where((i) => i.isSelected).toList();

      // Upload images and videos
      List<String> uploadedImageUrls = [];
      List<String> uploadedVideoUrls = [];

      // Upload photos
      for (var photo in _evidencePhotos) {
        try {
          final url = await ApiService.uploadReturnEvidence(photo);
          if (url != null) {
            uploadedImageUrls.add(url);
          }
        } catch (e) {
          debugPrint('Photo upload failed: $e');
        }
      }

      // Upload videos
      for (var video in _evidenceVideos) {
        try {
          final url = await ApiService.uploadReturnEvidence(video);
          if (url != null) {
            uploadedVideoUrls.add(url);
          }
        } catch (e) {
          debugPrint('Video upload failed: $e');
        }
      }

      // Prepare request data
      final requestData = {
        'items': selectedItems
            .map((ri) => {
                  'order_item_id': ri.item.id,
                  'quantity': ri.quantity,
                  'reason': _selectedReason,
                })
            .toList(),
        'reason': _selectedReason,
        'additional_details': _additionalDetails,
        'refund_method': _refundMethod,
        'images': uploadedImageUrls,
        'videos': uploadedVideoUrls,
      };

      // Call API with timeout
      final response = await ApiService.createReturnRequest(
        widget.order.id,
        requestData,
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () => throw TimeoutException('Request timeout'),
      );

      if (mounted) {
        if (response['success'] == true) {
          try {
            await context.read<BuyerProvider>().fetchOrdersByStatus();
            await context.read<BuyerProvider>().selectOrder(widget.order.id);
          } catch (e) {
            debugPrint('Return request submitted, but order refresh failed: $e');
          }

          setState(() {
            _isSubmitting = false;
            _isSubmitted = true;
          });
        } else {
          setState(() => _isSubmitting = false);
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(response['error'] ?? 'Failed to submit request'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } on TimeoutException {
      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
                'Request timeout. Please check your connection and try again.'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 5),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
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

class _LocalVideoPreviewScreen extends StatefulWidget {
  final File videoFile;

  const _LocalVideoPreviewScreen({required this.videoFile});

  @override
  State<_LocalVideoPreviewScreen> createState() =>
      _LocalVideoPreviewScreenState();
}

class _LocalVideoPreviewScreenState extends State<_LocalVideoPreviewScreen> {
  late final VideoPlayerController _controller;
  bool _initialized = false;

  @override
  void initState() {
    super.initState();
    _controller = kIsWeb
        ? VideoPlayerController.networkUrl(Uri.parse(widget.videoFile.path))
        : VideoPlayerController.file(widget.videoFile)
      ..initialize().then((_) {
        if (!mounted) return;
        setState(() => _initialized = true);
        _controller.play();
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Center(
        child: _initialized && _controller.value.isInitialized
            ? AspectRatio(
                aspectRatio: _controller.value.aspectRatio,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    VideoPlayer(_controller),
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          _controller.value.isPlaying
                              ? _controller.pause()
                              : _controller.play();
                        });
                      },
                      child: Container(
                        color: Colors.transparent,
                        child: AnimatedOpacity(
                          opacity: _controller.value.isPlaying ? 0.0 : 1.0,
                          duration: const Duration(milliseconds: 150),
                          child: Container(
                            padding: const EdgeInsets.all(18),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.5),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.play_arrow,
                              color: Colors.white,
                              size: 42,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : const CircularProgressIndicator(color: Colors.white),
      ),
      floatingActionButton: _initialized
          ? FloatingActionButton(
              backgroundColor: Colors.white,
              foregroundColor: Colors.black,
              onPressed: () {
                setState(() {
                  _controller.value.isPlaying
                      ? _controller.pause()
                      : _controller.play();
                });
              },
              child: Icon(
                _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
              ),
            )
          : null,
    );
  }
}
