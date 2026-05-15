import 'dart:async';
import 'package:flutter/material.dart';

/// Hero Slide Model - supports both simple URLs and rich slide data
class HeroSlide {
  final String image;
  final String? title;
  final String? subtitle;
  final String? cta;
  final List<Color>? gradientColors;

  HeroSlide({
    required this.image,
    this.title,
    this.subtitle,
    this.cta,
    this.gradientColors,
  });
}

/// Hero Carousel Widget with auto-rotation, gradient overlays, and text content
class HeroCarousel extends StatefulWidget {
  final List<String> imageUrls;
  final List<HeroSlide>? slides;
  final Duration autoScrollDuration;
  final double height;
  final VoidCallback? onTap;

  const HeroCarousel({
    this.imageUrls = const [],
    this.slides,
    this.autoScrollDuration = const Duration(milliseconds: 3500),
    this.height = 160,
    this.onTap,
    super.key,
  });

  @override
  State<HeroCarousel> createState() => _HeroCarouselState();
}

class _HeroCarouselState extends State<HeroCarousel>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  int _currentIndex = 0;
  late Timer _timer;

  late List<HeroSlide> _slides;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 700),
      vsync: this,
    );

    _initializeSlides();
    _startAutoScroll();
  }

  void _initializeSlides() {
    if (widget.slides != null && widget.slides!.isNotEmpty) {
      _slides = widget.slides!;
    } else if (widget.imageUrls.isNotEmpty) {
      _slides = widget.imageUrls
          .map((url) => HeroSlide(
                image: url,
                title: null,
                subtitle: null,
                cta: null,
                gradientColors: null,
              ))
          .toList();
    } else {
      _slides = [];
    }
  }

  void _startAutoScroll() {
    if (_slides.length <= 1) return;

    _timer = Timer.periodic(widget.autoScrollDuration, (_) {
      if (mounted) {
        _nextSlide();
      }
    });
  }

  void _nextSlide() {
    _fadeController.forward(from: 0.0).then((_) {
      setState(() {
        _currentIndex = (_currentIndex + 1) % _slides.length;
      });
      _fadeController.forward(from: 0.0);
    });
  }

  void _goToSlide(int index) {
    setState(() => _currentIndex = index);
    _fadeController.forward(from: 0.0);
  }

  @override
  void dispose() {
    _timer.cancel();
    _fadeController.dispose();
    super.dispose();
  }

  bool _isAsset(String path) => path.startsWith('assets/');

  @override
  Widget build(BuildContext context) {
    if (_slides.isEmpty) {
      return Container(
        height: widget.height,
        decoration: BoxDecoration(
          color: Colors.grey.shade300,
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Center(
          child: Text('No slides available'),
        ),
      );
    }

    final currentSlide = _slides[_currentIndex];
    final hasGradient = currentSlide.gradientColors != null &&
        currentSlide.gradientColors!.isNotEmpty;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Carousel Container
        GestureDetector(
          onTap: widget.onTap,
          child: Container(
            height: widget.height,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: Colors.grey.shade200,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.08),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Stack(
                children: [
                  // Background Image
                  SizedBox.expand(
                    child: _isAsset(currentSlide.image)
                        ? Image.asset(
                            currentSlide.image,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: Colors.grey.shade400,
                                child: const Icon(
                                  Icons.image_not_supported,
                                  size: 80,
                                  color: Colors.white70,
                                ),
                              );
                            },
                          )
                        : Image.network(
                            currentSlide.image,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: Colors.grey.shade400,
                                child: const Icon(
                                  Icons.image_not_supported,
                                  size: 80,
                                  color: Colors.white70,
                                ),
                              );
                            },
                          ),
                  ),

                  // Gradient Overlay
                  if (hasGradient)
                    SizedBox.expand(
                      child: Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.centerLeft,
                            end: Alignment.centerRight,
                            colors: currentSlide.gradientColors!,
                            stops: const [0.0, 1.0],
                          ),
                        ),
                        child: Opacity(
                          opacity: 0.75,
                          child: Container(),
                        ),
                      ),
                    ),

                  // Text Content Overlay
                  if (currentSlide.title != null ||
                      currentSlide.subtitle != null)
                    SizedBox.expand(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Limited Offer Label
                            Text(
                              'Limited Offer',
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.8),
                                fontSize: 8,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.5,
                              ),
                            ),
                            const SizedBox(height: 2),

                            // Title
                            if (currentSlide.title != null)
                              Text(
                                currentSlide.title!,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w900,
                                  fontSize: 18,
                                  height: 1.1,
                                ),
                              ),
                            const SizedBox(height: 2),

                            // Subtitle
                            if (currentSlide.subtitle != null)
                              Text(
                                currentSlide.subtitle!,
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: 0.8),
                                  fontSize: 10,
                                ),
                              ),
                            const SizedBox(height: 8),

                            // CTA Button
                            if (currentSlide.cta != null)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(20),
                                  boxShadow: [
                                    BoxShadow(
                                      color:
                                          Colors.black.withValues(alpha: 0.1),
                                      blurRadius: 4,
                                    ),
                                  ],
                                ),
                                child: Text(
                                  currentSlide.cta!,
                                  style: const TextStyle(
                                    color: Color(0xFF1e4db7),
                                    fontSize: 9,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),

        // Dot Indicators
        if (_slides.length > 1) ...[
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: List.generate(
              _slides.length,
              (index) {
                final isActive = _currentIndex == index;
                return GestureDetector(
                  onTap: () => _goToSlide(index),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    margin: const EdgeInsets.only(right: 6),
                    width: isActive ? 16 : 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: isActive
                          ? Colors.white
                          : Colors.white.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }
}
