import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../providers/buyer_provider.dart';
import '../../config/url_config.dart';
import 'buyer_home_screen.dart';

class RatingScreen extends StatefulWidget {
  final dynamic order;

  const RatingScreen({super.key, required this.order});

  @override
  State<RatingScreen> createState() => _RatingScreenState();
}

class _RatingScreenState extends State<RatingScreen>
    with SingleTickerProviderStateMixin {
  int _rating = 0;
  final TextEditingController _commentController = TextEditingController();
  bool _isSubmitting = false;
  bool _isSubmitted = false;

  // Category ratings
  final Map<String, int> _categoryRatings = {
    'Product Quality': 0,
    'Delivery Speed': 0,
    'Packaging': 0,
    'Rider Service': 0,
  };

  final Map<String, IconData> _categoryIcons = {
    'Product Quality': LucideIcons.shoppingBag,
    'Delivery Speed': LucideIcons.zap,
    'Packaging': LucideIcons.package,
    'Rider Service': LucideIcons.bike,
  };

  // Quick tags
  final List<String> _positiveTags = [
    '👍 Great quality',
    '⚡ Fast delivery',
    '📦 Well packaged',
    '😊 Friendly rider',
    '✅ As described',
    '💯 Worth it',
  ];

  final List<String> _negativeTags = [
    '👎 Poor quality',
    '🐢 Slow delivery',
    '📦 Bad packaging',
    '😞 Rude rider',
    '❌ Not as described',
    '💸 Overpriced',
  ];

  final Set<String> _selectedTags = {};
  final List<File> _selectedMedia = [];
  final ImagePicker _picker = ImagePicker();

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  List<String> get _activeTags =>
      _rating >= 4 ? _positiveTags : (_rating > 0 ? _negativeTags : []);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      body: Column(
        children: [
          _buildHeader(),
          Expanded(
            child: _isSubmitted
                ? _buildSuccessView()
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _buildOrderInfoCard(),
                        const SizedBox(height: 16),
                        _buildMainRatingCard(),
                        const SizedBox(height: 16),
                        if (_rating > 0) ...[
                          _buildCategoryRatings(),
                          const SizedBox(height: 16),
                          _buildQuickTags(),
                          const SizedBox(height: 16),
                        ],
                        _buildCommentCard(),
                        const SizedBox(height: 16),
                        _buildMediaUploadCard(),
                        const SizedBox(height: 16),
                        _buildSubmitButton(),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────── HEADER ───────────────────────

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
            onPressed: () => Navigator.pop(context),
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
                  'Rate Your Order',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  'Share your experience with us',
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
                const Icon(LucideIcons.star, color: Colors.amber, size: 13),
                const SizedBox(width: 5),
                Text(
                  'Review',
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

  // ─────────────────────── ORDER INFO ───────────────────────

  Widget _buildOrderInfoCard() {
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
                child: const Icon(LucideIcons.clipboardList,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Order #${widget.order.id}',
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  Text(
                    'Delivered · ${widget.order.orderDate.toString().split(' ')[0]}',
                    style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                  ),
                ],
              ),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Row(
                  children: [
                    Icon(LucideIcons.checkCircle2,
                        size: 12, color: Colors.green),
                    SizedBox(width: 5),
                    Text(
                      'Completed',
                      style: TextStyle(
                          fontSize: 11,
                          color: Colors.green,
                          fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(height: 1, color: Color(0xFFF0F4FB)),
          const SizedBox(height: 14),
          if (widget.order.items.isNotEmpty)
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    width: 58,
                    height: 58,
                    color: Colors.grey.shade100,
                    child: _buildProductImage(widget.order.items.first),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.order.items.first.productName,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: Color(0xFF1F2937),
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      if (widget.order.items.length > 1)
                        Text(
                          '+${widget.order.items.length - 1} more item${widget.order.items.length > 2 ? 's' : ''}',
                          style: TextStyle(
                            color: Colors.grey.shade500,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                ),
                Text(
                  '₱${widget.order.totalAmount.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Color(0xFF1e4db7),
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildProductImage(dynamic item) {
    String? productImage;
    if (item is Map) {
      productImage = item['product_image'] ??
          item['productImage'] ??
          item['image_url'] ??
          item['image'];
    } else {
      try {
        productImage = item.productImage;
      } catch (_) {
        productImage = null;
      }
    }

    final imageUrl = productImage != null && productImage.isNotEmpty
        ? UrlConfig.toAbsoluteImageUrl(productImage)
        : null;

    return imageUrl != null
        ? Image.network(
            imageUrl,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) =>
                Icon(Icons.image_not_supported, color: Colors.grey.shade400),
          )
        : Icon(Icons.image, color: Colors.grey.shade400);
  }

  // ─────────────────────── MAIN STAR RATING ───────────────────────

  Widget _buildMainRatingCard() {
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
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          // Animated emoji
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            transitionBuilder: (child, anim) =>
                ScaleTransition(scale: anim, child: child),
            child: Text(
              _getRatingEmoji(_rating),
              key: ValueKey(_rating),
              style: const TextStyle(fontSize: 52),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            'How was your overall experience?',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          Text(
            'Tap a star to rate this order',
            style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
          ),
          const SizedBox(height: 22),

          // Stars
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (index) {
              final filled = index < _rating;
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _rating = index + 1;
                    _selectedTags.clear();
                  });
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 5),
                  child: AnimatedScale(
                    scale: filled ? 1.15 : 1.0,
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.elasticOut,
                    child: Icon(
                      LucideIcons.star,
                      size: 42,
                      color: filled ? Colors.amber : Colors.grey.shade200,
                    ),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 14),

          // Rating label
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            child: _rating > 0
                ? Container(
                    key: ValueKey(_rating),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    decoration: BoxDecoration(
                      color: _getRatingColor(_rating).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      _getRatingLabel(_rating),
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: _getRatingColor(_rating),
                      ),
                    ),
                  )
                : Container(
                    key: const ValueKey('empty'),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Select a rating',
                      style:
                          TextStyle(fontSize: 14, color: Colors.grey.shade400),
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────── CATEGORY RATINGS ───────────────────────

  Widget _buildCategoryRatings() {
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
                child: const Icon(LucideIcons.layoutGrid,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Rate by Category',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text('Optional detailed feedback',
                      style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          ..._categoryRatings.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _categoryIcons[entry.key]!,
                      size: 15,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(width: 10),
                  SizedBox(
                    width: 100,
                    child: Text(
                      entry.key,
                      style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF1F2937)),
                    ),
                  ),
                  Expanded(
                    child: Row(
                      children: List.generate(5, (i) {
                        final filled = i < entry.value;
                        return GestureDetector(
                          onTap: () => setState(() {
                            _categoryRatings[entry.key] = i + 1;
                          }),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 2),
                            child: Icon(
                              LucideIcons.star,
                              size: 22,
                              color:
                                  filled ? Colors.amber : Colors.grey.shade200,
                            ),
                          ),
                        );
                      }),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  // ─────────────────────── QUICK TAGS ───────────────────────

  Widget _buildQuickTags() {
    if (_activeTags.isEmpty) return const SizedBox();

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
                child: const Icon(LucideIcons.tag,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('What stood out?',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text('Select all that apply',
                      style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _activeTags.map((tag) {
              final isSelected = _selectedTags.contains(tag);
              return GestureDetector(
                onTap: () {
                  setState(() {
                    if (isSelected) {
                      _selectedTags.remove(tag);
                    } else {
                      _selectedTags.add(tag);
                    }
                  });
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFF1e4db7)
                        : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF1e4db7)
                          : Colors.grey.shade200,
                    ),
                  ),
                  child: Text(
                    tag,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight:
                          isSelected ? FontWeight.bold : FontWeight.normal,
                      color: isSelected ? Colors.white : Colors.grey.shade700,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // ─────────────────────── COMMENT ───────────────────────

  Widget _buildCommentCard() {
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
                child: const Icon(LucideIcons.messageSquare,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Write a Review',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text('Optional — help others know more',
                      style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _commentController,
            maxLines: 4,
            maxLength: 500,
            decoration: InputDecoration(
              hintText: 'Tell us about your experience...',
              hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 13),
              filled: true,
              fillColor: const Color(0xFFF8FAFF),
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
                borderSide:
                    const BorderSide(color: Color(0xFF1e4db7), width: 1.5),
              ),
              contentPadding: const EdgeInsets.all(14),
              counterStyle:
                  TextStyle(color: Colors.grey.shade400, fontSize: 11),
            ),
            style: const TextStyle(fontSize: 13),
          ),
        ],
      ),
    );
  }

  // ─────────────────────── MEDIA UPLOAD ───────────────────────

  Widget _buildMediaUploadCard() {
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
                child: const Icon(LucideIcons.camera,
                    color: Color(0xFF1e4db7), size: 18),
              ),
              const SizedBox(width: 10),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Add Photos & Videos',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text('Optional — up to 5 files',
                      style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
              const Spacer(),
              Text(
                '${_selectedMedia.length}/5',
                style: TextStyle(
                  fontSize: 12,
                  color: _selectedMedia.length >= 5
                      ? Colors.red
                      : Colors.grey.shade600,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Media grid
          if (_selectedMedia.isNotEmpty)
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
                childAspectRatio: 1,
              ),
              itemCount: _selectedMedia.length,
              itemBuilder: (context, index) {
                final file = _selectedMedia[index];
                final isVideo = _isVideoFile(file.path);

                return Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        width: double.infinity,
                        height: double.infinity,
                        color: Colors.grey.shade100,
                        child: isVideo
                            ? Stack(
                                fit: StackFit.expand,
                                children: [
                                  Container(
                                    color: Colors.black12,
                                    child: const Icon(
                                      LucideIcons.play,
                                      color: Colors.white,
                                      size: 32,
                                    ),
                                  ),
                                  Positioned(
                                    bottom: 4,
                                    left: 4,
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: Colors.black54,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: const Text(
                                        'VIDEO',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 8,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ),
                                ],
                              )
                            : Image.file(
                                file,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) =>
                                    Icon(Icons.broken_image,
                                        color: Colors.grey.shade400),
                              ),
                      ),
                    ),
                    Positioned(
                      top: 4,
                      right: 4,
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedMedia.removeAt(index);
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            LucideIcons.x,
                            color: Colors.white,
                            size: 12,
                          ),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),

          if (_selectedMedia.isNotEmpty) const SizedBox(height: 12),

          // Upload buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _selectedMedia.length >= 5 ? null : _pickImages,
                  icon: const Icon(LucideIcons.image, size: 16),
                  label: const Text(
                    'Gallery',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    side: BorderSide(
                      color: _selectedMedia.length >= 5
                          ? Colors.grey.shade300
                          : const Color(0xFF1e4db7),
                    ),
                    foregroundColor: _selectedMedia.length >= 5
                        ? Colors.grey.shade400
                        : const Color(0xFF1e4db7),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _selectedMedia.length >= 5 ? null : _captureCamera,
                  icon: const Icon(LucideIcons.camera, size: 16),
                  label: const Text(
                    'Camera',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    side: BorderSide(
                      color: _selectedMedia.length >= 5
                          ? Colors.grey.shade300
                          : const Color(0xFF1e4db7),
                    ),
                    foregroundColor: _selectedMedia.length >= 5
                        ? Colors.grey.shade400
                        : const Color(0xFF1e4db7),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _selectedMedia.length >= 5 ? null : _pickVideo,
                  icon: const Icon(LucideIcons.video, size: 16),
                  label: const Text(
                    'Video',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    side: BorderSide(
                      color: _selectedMedia.length >= 5
                          ? Colors.grey.shade300
                          : const Color(0xFF1e4db7),
                    ),
                    foregroundColor: _selectedMedia.length >= 5
                        ? Colors.grey.shade400
                        : const Color(0xFF1e4db7),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),

          if (_selectedMedia.length >= 5) const SizedBox(height: 8),
          if (_selectedMedia.length >= 5)
            Text(
              'Maximum 5 files allowed',
              style: TextStyle(
                fontSize: 11,
                color: Colors.red.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
        ],
      ),
    );
  }

  bool _isVideoFile(String path) {
    final videoExtensions = [
      '.mp4',
      '.mov',
      '.avi',
      '.mkv',
      '.wmv',
      '.flv',
      '.webm'
    ];
    return videoExtensions.any((ext) => path.toLowerCase().endsWith(ext));
  }

  Future<void> _pickImages() async {
    if (_selectedMedia.length >= 5) return;

    try {
      final List<XFile> images = await _picker.pickMultipleMedia(
        limit: 5 - _selectedMedia.length,
      );

      if (images.isNotEmpty) {
        setState(() {
          for (final image in images) {
            if (_selectedMedia.length < 5) {
              _selectedMedia.add(File(image.path));
            }
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error picking images: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _pickVideo() async {
    if (_selectedMedia.length >= 5) return;

    try {
      final XFile? video = await _picker.pickVideo(
        source: ImageSource.gallery,
        maxDuration: const Duration(minutes: 2), // 2 minute limit
      );

      if (video != null) {
        setState(() {
          _selectedMedia.add(File(video.path));
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error picking video: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _captureCamera() async {
    if (_selectedMedia.length >= 5) return;

    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85, // Compress to 85% quality
      );

      if (photo != null) {
        setState(() {
          _selectedMedia.add(File(photo.path));
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error capturing photo: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  // ─────────────────────── SUBMIT BUTTON ───────────────────────

  Widget _buildSubmitButton() {
    final canSubmit = _rating > 0 && !_isSubmitting;

    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: canSubmit ? _submitRating : null,
            icon: _isSubmitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(LucideIcons.send, size: 18),
            label: Text(
              _isSubmitting ? 'Submitting...' : 'Submit Rating',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1e4db7),
              disabledBackgroundColor: Colors.grey.shade200,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              elevation: 0,
            ),
          ),
        ),
        if (_rating == 0) ...[
          const SizedBox(height: 8),
          Text(
            'Please select a star rating to continue',
            style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
          ),
        ],
      ],
    );
  }

  // ─────────────────────── SUBMIT RATING ───────────────────────

  Future<void> _submitRating() async {
    if (_rating == 0) return;

    setState(() => _isSubmitting = true);

    try {
      final buyerProvider = context.read<BuyerProvider>();
      
      // Build full comment with tags and category ratings
      String fullComment = _commentController.text.trim();
      if (_selectedTags.isNotEmpty) {
        final tagsText = _selectedTags.join(', ');
        fullComment = fullComment.isEmpty ? tagsText : '$fullComment\n\nTags: $tagsText';
      }

      final categoryRatingsText = _categoryRatings.entries
          .where((e) => e.value > 0)
          .map((e) => '${e.key}: ${e.value}★')
          .join(', ');
      if (categoryRatingsText.isNotEmpty) {
        fullComment = fullComment.isEmpty
            ? categoryRatingsText
            : '$fullComment\n\n$categoryRatingsText';
      }

      // Submit rating with or without media
      bool success;
      if (_selectedMedia.isNotEmpty) {
        success = await buyerProvider.submitOrderRatingWithMedia(
          widget.order.id,
          _rating,
          fullComment,
          _selectedMedia,
        );
      } else {
        success = await buyerProvider.submitOrderRating(
          widget.order.id,
          _rating,
          fullComment,
        );
      }

      if (!mounted) return;

      if (success) {
        setState(() {
          _isSubmitted = true;
          _isSubmitting = false;
        });

        // Force refresh products to get updated ratings
        debugPrint('✅ Rating submitted, refreshing products...');
        await Future.wait([
          buyerProvider.fetchProducts(bustCache: true),
          buyerProvider.fetchOrdersByStatus(),
        ]);
        debugPrint('✅ Products and orders refreshed');

        // Navigate back after showing success
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (context) => const BuyerHomeScreen(
                  initialTab: 1,
                  ordersInitialFilter: 'completed',
                ),
              ),
            );
          }
        });
      } else {
        setState(() => _isSubmitting = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(buyerProvider.errorMessage ?? 'Failed to submit rating'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      setState(() => _isSubmitting = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  // ─────────────────────── SUCCESS VIEW ───────────────────────

  Widget _buildSuccessView() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Stack(
          children: [
            // Confetti/celebration background
            Positioned.fill(
              child: CustomPaint(
                painter: _ConfettiPainter(),
              ),
            ),
            // Main content
            SingleChildScrollView(
              padding: const EdgeInsets.all(32),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Animated success icon with pulse effect
                    TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0.0, end: 1.0),
                      duration: const Duration(milliseconds: 600),
                      curve: Curves.elasticOut,
                      builder: (ctx, v, child) => Transform.scale(
                        scale: v,
                        child: child,
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // Pulsing circle background
                          TweenAnimationBuilder<double>(
                            tween: Tween(begin: 0.8, end: 1.2),
                            duration: const Duration(milliseconds: 1000),
                            curve: Curves.easeInOut,
                            builder: (ctx, scale, child) => Transform.scale(
                              scale: scale,
                              child: Container(
                                width: 140,
                                height: 140,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  gradient: LinearGradient(
                                    colors: [
                                      const Color(0xFFFF6B35).withValues(alpha: 0.2),
                                      const Color(0xFFFF8C42).withValues(alpha: 0.1),
                    ],
                                    begin: Alignment.topLeft,
                                    end: Alignment.bottomRight,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          // Main success circle
                          Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: const LinearGradient(
                                colors: [
                                  Color(0xFFFF6B35),
                                  Color(0xFFFF8C42),
                                ],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFFFF6B35).withValues(alpha: 0.4),
                                  blurRadius: 30,
                                  spreadRadius: 8,
                                ),
                              ],
                            ),
                            child: const Icon(
                              LucideIcons.checkCircle2,
                              color: Colors.white,
                              size: 60,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Success text with fade-in
                    TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0.0, end: 1.0),
                      duration: const Duration(milliseconds: 800),
                      curve: Curves.easeOut,
                      builder: (ctx, opacity, child) => Opacity(
                        opacity: opacity,
                        child: child,
                      ),
                      child: Column(
                        children: [
                          Text(
                            _rating >= 4 ? '🎉 Salamat!' : 'Nareceive na!',
                            style: const TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1F2937),
                              letterSpacing: -0.5,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _rating >= 4
                                ? 'Masaya kami na nag-enjoy ka sa iyong order!'
                                : 'Salamat sa iyong feedback. Makakatulong ito sa amin na mag-improve.',
                            style: TextStyle(
                              fontSize: 15,
                              color: Colors.grey.shade600,
                              height: 1.5,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Rating summary card with slide-up animation
                    TweenAnimationBuilder<Offset>(
                      tween: Tween(
                        begin: const Offset(0, 0.3),
                        end: Offset.zero,
                      ),
                      duration: const Duration(milliseconds: 600),
                      curve: Curves.easeOut,
                      builder: (ctx, offset, child) => Transform.translate(
                        offset: Offset(0, offset.dy * 100),
                        child: child,
                      ),
                      child: Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.06),
                              blurRadius: 20,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            // Animated stars
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: List.generate(5, (i) {
                                return TweenAnimationBuilder<double>(
                                  tween: Tween(begin: 0.0, end: 1.0),
                                  duration: Duration(
                                    milliseconds: 400 + (i * 100),
                                  ),
                                  curve: Curves.elasticOut,
                                  builder: (ctx, scale, child) =>
                                      Transform.scale(
                                    scale: scale,
                                    child: Transform.rotate(
                                      angle: (1 - scale) * 0.5,
                                      child: Icon(
                                        LucideIcons.star,
                                        size: 32,
                                        color: i < _rating
                                            ? const Color(0xFFFCD34D)
                                            : Colors.grey.shade200,
                                      ),
                                    ),
                                  ),
                                );
                              }),
                            ),
                            const SizedBox(height: 12),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 18,
                                vertical: 8,
                              ),
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    _getRatingColor(_rating).withValues(alpha: 0.15),
                                    _getRatingColor(_rating).withValues(alpha: 0.08),
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                _getRatingLabel(_rating),
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: _getRatingColor(_rating),
                                ),
                              ),
                            ),
                            if (_selectedTags.isNotEmpty) ...[
                              const SizedBox(height: 16),
                              const Divider(height: 1),
                              const SizedBox(height: 16),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                alignment: WrapAlignment.center,
                                children: _selectedTags
                                    .map(
                                      (tag) => Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 6,
                                        ),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF1e4db7)
                                              .withValues(alpha: 0.08),
                                          borderRadius: BorderRadius.circular(12),
                                          border: Border.all(
                                            color: const Color(0xFF1e4db7)
                                                .withValues(alpha: 0.2),
                                          ),
                                        ),
                                        child: Text(
                                          tag,
                                          style: const TextStyle(
                                            fontSize: 12,
                                            color: Color(0xFF1e4db7),
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    )
                                    .toList(),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    
                    // Info message
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFF6B35).withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: const Color(0xFFFF6B35).withValues(alpha: 0.2),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            LucideIcons.sparkles,
                            size: 20,
                            color: Color(0xFFFF6B35),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Redirecting to your completed orders...',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade700,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  // ─────────────────────── HELPERS ───────────────────────

  String _getRatingEmoji(int rating) {
    switch (rating) {
      case 1:
        return '😞';
      case 2:
        return '😕';
      case 3:
        return '😐';
      case 4:
        return '😊';
      case 5:
        return '🤩';
      default:
        return '⭐';
    }
  }

  String _getRatingLabel(int rating) {
    switch (rating) {
      case 1:
        return 'Poor';
      case 2:
        return 'Fair';
      case 3:
        return 'Good';
      case 4:
        return 'Very Good';
      case 5:
        return 'Excellent!';
      default:
        return 'Rate this order';
    }
  }

  Color _getRatingColor(int rating) {
    switch (rating) {
      case 1:
        return Colors.red;
      case 2:
        return Colors.deepOrange;
      case 3:
        return Colors.orange;
      case 4:
        return Colors.lightGreen;
      case 5:
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}

// Confetti painter for celebration effect
class _ConfettiPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    final random = DateTime.now().millisecondsSinceEpoch;
    
    // Draw confetti pieces
    final colors = [
      const Color(0xFFFF6B35),
      const Color(0xFFFFD93D),
      const Color(0xFF6BCF7F),
      const Color(0xFF4D96FF),
      const Color(0xFFFF6B9D),
    ];
    
    for (int i = 0; i < 30; i++) {
      final x = (random * (i + 1) * 7) % size.width;
      final y = (random * (i + 1) * 11) % size.height;
      final colorIndex = i % colors.length;
      
      paint.color = colors[colorIndex].withValues(alpha: 0.3);
      
      // Draw different shapes
      if (i % 3 == 0) {
        // Circle
        canvas.drawCircle(Offset(x, y), 4, paint);
      } else if (i % 3 == 1) {
        // Square
        canvas.drawRect(
          Rect.fromCenter(center: Offset(x, y), width: 6, height: 6),
          paint,
        );
      } else {
        // Triangle
        final path = Path()
          ..moveTo(x, y - 4)
          ..lineTo(x - 3, y + 2)
          ..lineTo(x + 3, y + 2)
          ..close();
        canvas.drawPath(path, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
