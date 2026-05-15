import 'dart:io';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../providers/buyer_provider.dart';
import '../../widgets/modern_snackbar.dart';

class SubmitReviewScreen extends StatefulWidget {
  final int productId;
  final String productName;
  final String? productImage;

  const SubmitReviewScreen({
    required this.productId,
    required this.productName,
    this.productImage,
    super.key,
  });

  @override
  State<SubmitReviewScreen> createState() => _SubmitReviewScreenState();
}

class _SubmitReviewScreenState extends State<SubmitReviewScreen> {
  int _rating = 5;
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  final List<File> _mediaFiles = [];
  bool _isSubmitting = false;
  final _picker = ImagePicker();

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _pickMedia() async {
    if (_mediaFiles.length >= 6) {
      ModernSnackBar.showError(context, 'Maximum 6 files allowed');
      return;
    }

    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(LucideIcons.image),
              title: const Text('Choose Photo'),
              onTap: () async {
                Navigator.pop(context);
                final pickedFile = await _picker.pickImage(
                  source: ImageSource.gallery,
                  maxWidth: 1920,
                  maxHeight: 1920,
                  imageQuality: 85,
                );
                if (pickedFile != null) {
                  setState(() => _mediaFiles.add(File(pickedFile.path)));
                }
              },
            ),
            ListTile(
              leading: const Icon(LucideIcons.camera),
              title: const Text('Take Photo'),
              onTap: () async {
                Navigator.pop(context);
                final pickedFile = await _picker.pickImage(
                  source: ImageSource.camera,
                  maxWidth: 1920,
                  maxHeight: 1920,
                  imageQuality: 85,
                );
                if (pickedFile != null) {
                  setState(() => _mediaFiles.add(File(pickedFile.path)));
                }
              },
            ),
            ListTile(
              leading: const Icon(LucideIcons.video),
              title: const Text('Choose Video'),
              onTap: () async {
                Navigator.pop(context);
                final pickedFile = await _picker.pickVideo(
                  source: ImageSource.gallery,
                  maxDuration: const Duration(seconds: 30),
                );
                if (pickedFile != null) {
                  setState(() => _mediaFiles.add(File(pickedFile.path)));
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _removeMedia(int index) {
    setState(() => _mediaFiles.removeAt(index));
  }

  Future<void> _submitReview() async {
    if (_rating == 0) {
      ModernSnackBar.showError(context, 'Please select a rating');
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final fields = {
        'product_id': widget.productId.toString(),
        'rating': _rating.toString(),
        'title': _titleController.text.trim(),
        'content': _contentController.text.trim(),
      };

      final files = <String, File>{};
      for (int i = 0; i < _mediaFiles.length; i++) {
        files['media[$i]'] = _mediaFiles[i];
      }

      final result = await ApiService.uploadMultipart(
        'POST',
        '/api/reviews',
        fields: fields,
        files: files.isNotEmpty ? files : null,
        auth: true,
      );

      if (!mounted) return;

      if (result['success'] == true) {
        // Refresh products to update ratings
        await context.read<BuyerProvider>().fetchProducts();

        if (!mounted) return;

        // Show success overlay
        _showSuccessOverlay();

        // Navigate back after delay
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.pop(context, true);
          }
        });
      } else {
        ModernSnackBar.showError(
          context,
          result['message'] ?? 'Failed to submit review',
        );
      }
    } catch (e) {
      if (!mounted) return;
      ModernSnackBar.showError(
        context,
        'Failed to submit review: ${e.toString()}',
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  void _showSuccessOverlay() {
    final overlay = Overlay.of(context);
    final overlayEntry = OverlayEntry(
      builder: (context) => _ReviewSuccessOverlay(
        productName: widget.productName,
        rating: _rating,
      ),
    );
    overlay.insert(overlayEntry);
    Future.delayed(const Duration(seconds: 2), () {
      overlayEntry.remove();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FB),
      appBar: AppBar(
        title: const Text('Write a Review'),
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(LucideIcons.arrowLeft),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product Info
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  if (widget.productImage != null)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.network(
                        widget.productImage!,
                        width: 60,
                        height: 60,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          width: 60,
                          height: 60,
                          color: Colors.grey.shade200,
                          child: const Icon(LucideIcons.image),
                        ),
                      ),
                    ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      widget.productName,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Rating
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Your Rating',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(5, (index) {
                      return GestureDetector(
                        onTap: () => setState(() => _rating = index + 1),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          child: Icon(
                            LucideIcons.star,
                            size: 40,
                            color: index < _rating
                                ? Colors.amber
                                : Colors.grey.shade300,
                            fill: index < _rating ? 0.8 : 0,
                          ),
                        ),
                      );
                    }),
                  ),
                  const SizedBox(height: 8),
                  Center(
                    child: Text(
                      _getRatingText(_rating),
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Title
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Review Title (Optional)',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _titleController,
                    decoration: InputDecoration(
                      hintText: 'Summarize your experience',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      contentPadding: const EdgeInsets.all(12),
                    ),
                    maxLength: 100,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Content
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Your Review (Optional)',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _contentController,
                    decoration: InputDecoration(
                      hintText: 'Share your experience with this product...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      contentPadding: const EdgeInsets.all(12),
                    ),
                    maxLines: 5,
                    maxLength: 800,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Media Upload
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Add Photos/Videos (Optional)',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Up to 6 files • JPG, PNG, MP4, MOV',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ..._mediaFiles.asMap().entries.map((entry) {
                        final index = entry.key;
                        final file = entry.value;
                        final isVideo =
                            file.path.toLowerCase().endsWith('.mp4') ||
                                file.path.toLowerCase().endsWith('.mov');

                        return Stack(
                          children: [
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.grey.shade300),
                              ),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: isVideo
                                    ? Container(
                                        color: Colors.black87,
                                        child: const Icon(
                                          LucideIcons.video,
                                          color: Colors.white,
                                          size: 32,
                                        ),
                                      )
                                    : Image.file(
                                        file,
                                        fit: BoxFit.cover,
                                      ),
                              ),
                            ),
                            Positioned(
                              top: 4,
                              right: 4,
                              child: GestureDetector(
                                onTap: () => _removeMedia(index),
                                child: Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(
                                    color: Colors.red,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    LucideIcons.x,
                                    size: 14,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        );
                      }),
                      if (_mediaFiles.length < 6)
                        GestureDetector(
                          onTap: _pickMedia,
                          child: Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: const Color(0xFF1e4db7),
                                width: 2,
                                style: BorderStyle.solid,
                              ),
                            ),
                            child: const Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  LucideIcons.plus,
                                  color: Color(0xFF1e4db7),
                                  size: 24,
                                ),
                                SizedBox(height: 4),
                                Text(
                                  'Add',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Color(0xFF1e4db7),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitReview,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1e4db7),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        'Submit Review',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getRatingText(int rating) {
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
        return 'Excellent';
      default:
        return '';
    }
  }
}

class _ReviewSuccessOverlay extends StatefulWidget {
  final String productName;
  final int rating;

  const _ReviewSuccessOverlay({
    required this.productName,
    required this.rating,
  });

  @override
  State<_ReviewSuccessOverlay> createState() => _ReviewSuccessOverlayState();
}

class _ReviewSuccessOverlayState extends State<_ReviewSuccessOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<double> _checkAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.elasticOut),
      ),
    );
    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.3, curve: Curves.easeIn),
      ),
    );
    _checkAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.3, 0.8, curve: Curves.elasticOut),
      ),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withValues(alpha: 0.6),
      child: Center(
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: ScaleTransition(
            scale: _scaleAnimation,
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 40),
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.2),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Animated Check Icon
                  ScaleTransition(
                    scale: _checkAnimation,
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF10B981),
                            Color(0xFF059669),
                          ],
                        ),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color:
                                const Color(0xFF10B981).withValues(alpha: 0.3),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ],
                      ),
                      child: const Icon(
                        LucideIcons.checkCircle2,
                        color: Colors.white,
                        size: 56,
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Success Text
                  const Text(
                    'Review Submitted!',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Salamat sa iyong ${widget.rating}-star review!',
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  // Star Rating Display
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      widget.rating,
                      (index) => Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 2),
                        child: TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: Duration(milliseconds: 300 + (index * 100)),
                          curve: Curves.elasticOut,
                          builder: (context, value, child) {
                            return Transform.scale(
                              scale: value,
                              child: const Icon(
                                LucideIcons.star,
                                color: Color(0xFFFCD34D),
                                size: 24,
                                fill: 0.9,
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  // Info Text
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          LucideIcons.info,
                          size: 16,
                          color: Color(0xFF059669),
                        ),
                        SizedBox(width: 8),
                        Flexible(
                          child: Text(
                            'Makikita na ng lahat ang iyong review',
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(0xFF059669),
                              fontWeight: FontWeight.w600,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ],
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
}
