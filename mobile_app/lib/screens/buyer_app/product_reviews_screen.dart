import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import '../../services/api_service.dart';
import '../../config/url_config.dart';
import '../../widgets/skeleton_loader.dart';

class ProductReviewsScreen extends StatefulWidget {
  final int productId;
  final String productName;

  const ProductReviewsScreen({
    required this.productId,
    required this.productName,
    super.key,
  });

  @override
  State<ProductReviewsScreen> createState() => _ProductReviewsScreenState();
}

class _ProductReviewsScreenState extends State<ProductReviewsScreen> {
  bool _isLoading = true;
  String? _error;
  double _averageRating = 0.0;
  int _reviewCount = 0;
  List<Map<String, dynamic>> _reviews = const [];
  int? _filterRating;

  static const _primaryBlue = Color(0xFF1e4db7);
  static const _bgColor = Color(0xFFF0F4FB);

  @override
  void initState() {
    super.initState();
    _loadReviews();
  }

  Future<void> _loadReviews() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await ApiService.getProductReviews(widget.productId);
      final reviews = (result['reviews'] as List? ?? <dynamic>[])
          .map((e) => (e as Map).cast<String, dynamic>())
          .toList(growable: false);

      if (!mounted) return;
      setState(() {
        _averageRating = ((result['average_rating'] as num?) ?? 0).toDouble();
        _reviewCount =
            (result['review_count'] as num?)?.toInt() ?? reviews.length;
        _reviews = reviews;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final filteredReviews = _filterRating == null
        ? _reviews
        : _reviews
            .where((r) => (r['rating'] as num?)?.toInt() == _filterRating)
            .toList();

    return Scaffold(
      backgroundColor: _bgColor,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        leading: GestureDetector(
          onTap: () => Navigator.pop(context),
          child: Container(
            margin: const EdgeInsets.all(8),
            decoration: const BoxDecoration(
              color: _bgColor,
              shape: BoxShape.circle,
            ),
            child:
                const Icon(Icons.arrow_back, color: Colors.black87, size: 20),
          ),
        ),
        title: const Text(
          'Ratings & Reviews',
          style: TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.w700,
            fontSize: 16,
          ),
        ),
        centerTitle: false,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: Colors.grey.shade100),
        ),
      ),
      body: _isLoading
          ? const ListSkeletonLoader(
              itemSkeleton: ReviewCardSkeleton(),
              itemCount: 5,
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 20),
            )
          : _error != null
              ? _buildErrorState()
              : RefreshIndicator(
                  color: _primaryBlue,
                  onRefresh: _loadReviews,
                  child: ListView(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 20),
                    children: [
                      _buildSummaryCard(),
                      const SizedBox(height: 16),
                      _buildFilterChips(),
                      const SizedBox(height: 16),
                      if (filteredReviews.isEmpty)
                        _buildEmptyState()
                      else
                        ...filteredReviews.map(_buildReviewCard),
                      const SizedBox(height: 20),
                    ],
                  ),
                ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.error_outline,
                  size: 48, color: Colors.red.shade300),
            ),
            const SizedBox(height: 16),
            const Text(
              'Failed to load reviews',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Colors.black87),
            ),
            const SizedBox(height: 8),
            Text(
              _error ?? '',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _loadReviews,
              icon: const Icon(Icons.refresh, size: 16),
              label: const Text('Try Again'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _primaryBlue,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 60),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.rate_review_outlined,
                size: 48, color: Colors.grey.shade400),
          ),
          const SizedBox(height: 16),
          Text(
            _filterRating != null
                ? 'No $_filterRating-star reviews yet'
                : 'No reviews yet',
            style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Colors.black54),
          ),
          const SizedBox(height: 6),
          Text(
            _filterRating != null
                ? 'Try a different filter'
                : 'Be the first to review this product',
            style: TextStyle(fontSize: 13, color: Colors.grey.shade400),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Filter by Rating',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.black54,
              letterSpacing: 0.3,
            ),
          ),
          const SizedBox(height: 10),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _filterChip(
                    label: 'All',
                    selected: _filterRating == null,
                    onTap: () => setState(() => _filterRating = null)),
                const SizedBox(width: 8),
                ...List.generate(5, (i) {
                  final rating = 5 - i;
                  final count = _reviews
                      .where((r) => (r['rating'] as num?)?.toInt() == rating)
                      .length;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: _filterChip(
                      label: '$rating ★',
                      count: count,
                      selected: _filterRating == rating,
                      onTap: () => setState(() => _filterRating = rating),
                    ),
                  );
                }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _filterChip({
    required String label,
    required bool selected,
    required VoidCallback onTap,
    int? count,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? _primaryBlue : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: selected ? Colors.white : Colors.black54,
              ),
            ),
            if (count != null && count > 0) ...[
              const SizedBox(width: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                decoration: BoxDecoration(
                  color: selected
                      ? Colors.white.withValues(alpha: 0.3)
                      : Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: selected ? Colors.white : Colors.black54,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.productName,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Colors.black87,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Big score
              Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  ShaderMask(
                    shaderCallback: (bounds) => const LinearGradient(
                      colors: [Color(0xFF1a2f6b), _primaryBlue],
                    ).createShader(bounds),
                    child: Text(
                      _averageRating.toStringAsFixed(1),
                      style: const TextStyle(
                        fontSize: 52,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        height: 1,
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  _stars(_averageRating.round()),
                  const SizedBox(height: 4),
                  Text(
                    '$_reviewCount ${_reviewCount == 1 ? "review" : "reviews"}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 24),
              // Rating bars
              Expanded(
                child: Column(
                  children: List.generate(5, (i) {
                    final starVal = 5 - i;
                    final count = _reviews
                        .where((r) => (r['rating'] as num?)?.toInt() == starVal)
                        .length;
                    final ratio = _reviewCount > 0 ? count / _reviewCount : 0.0;
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 3),
                      child: Row(
                        children: [
                          Text(
                            '$starVal',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(width: 4),
                          const Icon(Icons.star, size: 11, color: Colors.amber),
                          const SizedBox(width: 8),
                          Expanded(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: ratio,
                                minHeight: 7,
                                backgroundColor: Colors.grey.shade100,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  ratio > 0
                                      ? _primaryBlue
                                      : Colors.grey.shade200,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          SizedBox(
                            width: 20,
                            child: Text(
                              '$count',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.grey.shade500,
                              ),
                              textAlign: TextAlign.right,
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildReviewCard(Map<String, dynamic> review) {
    final media = (review['media'] as List? ?? <dynamic>[])
        .map((e) => (e as Map).cast<String, dynamic>())
        .toList(growable: false);

    // Extract user info - use multiple possible field names and fallback to user_id if empty
    String userName = (review['buyer_name'] ??
            review['user_name'] ??
            review['name'] ??
            review['username'] ??
            '')
        .toString();
    if (userName.isEmpty) {
      // If name is empty, use user_id to create a default name
      final userId = (review['user_id'] ?? '').toString();
      userName = userId.isNotEmpty ? 'User $userId' : 'Anonymous';
    }

    final userAvatar =
        (review['buyer_avatar'] ?? review['user_avatar'] ?? review['avatar'])
            ?.toString();
    final categoryRatings = review['category_ratings'] as String?;
    final rating = (review['rating'] as num?)?.toInt() ?? 0;
    final title = (review['title'] ?? '').toString();
    final content = (review['content'] ?? '').toString();
    final date = (review['created_at'] ?? '').toString().split('T').first;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildAvatar(userName, userAvatar, size: 44),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        userName,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        date,
                        style: TextStyle(
                            fontSize: 11, color: Colors.grey.shade400),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          _stars(rating),
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: rating >= 4
                                  ? Colors.green.shade50
                                  : rating >= 3
                                      ? Colors.orange.shade50
                                      : Colors.red.shade50,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              rating >= 4
                                  ? 'Positive'
                                  : rating >= 3
                                      ? 'Neutral'
                                      : 'Critical',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                                color: rating >= 4
                                    ? Colors.green.shade600
                                    : rating >= 3
                                        ? Colors.orange.shade600
                                        : Colors.red.shade600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),

            // Category ratings
            if (categoryRatings != null && categoryRatings.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0F4FB),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.blue.shade50),
                ),
                child: Text(
                  categoryRatings,
                  style: TextStyle(
                      fontSize: 11,
                      color: Colors.blueGrey.shade600,
                      height: 1.5),
                ),
              ),
            ],

            // Title
            if (title.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 14,
                  color: Colors.black87,
                ),
              ),
            ],

            // Content
            if (content.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                content,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade700,
                  height: 1.55,
                ),
              ),
            ],

            // Media
            if (media.isNotEmpty) ...[
              const SizedBox(height: 14),
              SizedBox(
                height: 90,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: media.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final item = media[index];
                    final type = (item['type'] ?? '').toString().toLowerCase();
                    final path = (item['path'] ?? '').toString();
                    if (path.isEmpty) return const SizedBox.shrink();
                    if (type == 'video') return _videoTile(path);
                    return _imageTile(path);
                  },
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAvatar(String userName, String? userAvatar, {double size = 44}) {
    if (userAvatar != null && userAvatar.isNotEmpty) {
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: _primaryBlue, width: 2),
        ),
        child: ClipOval(
          child: Image.network(
            userAvatar.startsWith('http')
                ? userAvatar
                : '${UrlConfig.baseUrl}$userAvatar',
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) =>
                _avatarFallback(userName, size),
          ),
        ),
      );
    }
    return _avatarFallback(userName, size);
  }

  Widget _avatarFallback(String userName, double size) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF1a2f6b), _primaryBlue],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          userName.isNotEmpty ? userName[0].toUpperCase() : 'A',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: size * 0.38,
          ),
        ),
      ),
    );
  }

  Widget _imageTile(String url) {
    final absoluteUrl =
        url.startsWith('http') ? url : '${UrlConfig.baseUrl}$url';
    return GestureDetector(
      onTap: () => _openPhotoViewer(absoluteUrl),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Image.network(
          absoluteUrl,
          width: 90,
          height: 90,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) => Container(
            width: 90,
            height: 90,
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.broken_image, color: Colors.grey.shade400),
          ),
        ),
      ),
    );
  }

  Widget _videoTile(String url) {
    final absoluteUrl =
        url.startsWith('http') ? url : '${UrlConfig.baseUrl}$url';
    return GestureDetector(
      onTap: () => _openVideoPlayer(absoluteUrl),
      child: Container(
        width: 90,
        height: 90,
        decoration: BoxDecoration(
          color: Colors.grey.shade200,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Stack(
          children: [
            // Video thumbnail placeholder
            Container(
              width: 90,
              height: 90,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(12),
              ),
              child:
                  const Icon(Icons.video_library, color: Colors.grey, size: 32),
            ),
            // Play button overlay
            const Center(
              child:
                  Icon(Icons.play_circle_fill, color: Colors.black54, size: 36),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _openVideoPlayer(String url) async {
    await Navigator.of(context).push(
      MaterialPageRoute(
          builder: (_) => _VideoReviewPlayerScreen(videoUrl: url)),
    );
  }

  Future<void> _openPhotoViewer(String url) async {
    await Navigator.of(context).push(
      MaterialPageRoute(
          builder: (_) => _PhotoReviewViewerScreen(imageUrl: url)),
    );
  }

  Widget _stars(int filled) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(
        5,
        (index) => Icon(
          index < filled ? Icons.star_rounded : Icons.star_border_rounded,
          color: index < filled ? Colors.amber : Colors.grey.shade300,
          size: 16,
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  Video Player Screen
// ─────────────────────────────────────────────────────────────

class _VideoReviewPlayerScreen extends StatefulWidget {
  final String videoUrl;

  const _VideoReviewPlayerScreen({required this.videoUrl});

  @override
  State<_VideoReviewPlayerScreen> createState() =>
      _VideoReviewPlayerScreenState();
}

class _VideoReviewPlayerScreenState extends State<_VideoReviewPlayerScreen> {
  late final VideoPlayerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(Uri.parse(widget.videoUrl))
      ..initialize().then((_) {
        if (mounted) setState(() {});
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
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: GestureDetector(
          onTap: () => Navigator.pop(context),
          child: Container(
            margin: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.arrow_back, color: Colors.white, size: 20),
          ),
        ),
        title: const Text(
          'Review Video',
          style: TextStyle(
              color: Colors.white, fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      body: Center(
        child: _controller.value.isInitialized
            ? SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ConstrainedBox(
                      constraints: BoxConstraints(
                        maxHeight: MediaQuery.of(context).size.height * 0.55,
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: AspectRatio(
                          aspectRatio: _controller.value.aspectRatio,
                          child: VideoPlayer(_controller),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: VideoProgressIndicator(
                        _controller,
                        allowScrubbing: true,
                        colors: const VideoProgressColors(
                          playedColor: Color(0xFF1e4db7),
                          bufferedColor: Colors.white24,
                          backgroundColor: Colors.white10,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          if (_controller.value.isPlaying) {
                            _controller.pause();
                          } else {
                            _controller.play();
                          }
                        });
                      },
                      child: Container(
                        width: 64,
                        height: 64,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Color(0xFF1a2f6b), Color(0xFF1e4db7)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          _controller.value.isPlaying
                              ? Icons.pause_rounded
                              : Icons.play_arrow_rounded,
                          color: Colors.white,
                          size: 34,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : const CircularProgressIndicator(
                color: Color(0xFF1e4db7),
                strokeWidth: 3,
              ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  Photo Viewer Screen
// ─────────────────────────────────────────────────────────────

class _PhotoReviewViewerScreen extends StatefulWidget {
  final String imageUrl;

  const _PhotoReviewViewerScreen({required this.imageUrl});

  @override
  State<_PhotoReviewViewerScreen> createState() =>
      _PhotoReviewViewerScreenState();
}

class _PhotoReviewViewerScreenState extends State<_PhotoReviewViewerScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: GestureDetector(
          onTap: () => Navigator.pop(context),
          child: Container(
            margin: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.arrow_back, color: Colors.white, size: 20),
          ),
        ),
      ),
      body: InteractiveViewer(
        minScale: 0.5,
        maxScale: 4.0,
        child: Center(
          child: Image.network(
            widget.imageUrl,
            fit: BoxFit.contain,
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return const CircularProgressIndicator(
                color: Color(0xFF1e4db7),
              );
            },
            errorBuilder: (context, error, stackTrace) => const Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.broken_image, color: Colors.white70, size: 64),
                SizedBox(height: 12),
                Text(
                  'Failed to load image',
                  style: TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
