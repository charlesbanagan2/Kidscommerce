import 'package:flutter/material.dart';

class SkeletonLoader extends StatefulWidget {
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;

  const SkeletonLoader({
    super.key,
    this.width,
    this.height,
    this.borderRadius,
  });

  @override
  State<SkeletonLoader> createState() => _SkeletonLoaderState();
}

class _SkeletonLoaderState extends State<SkeletonLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
    _animation = Tween<double>(begin: -1.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: const [
                Color(0xFFE0E0E0),
                Color(0xFFF5F5F5),
                Color(0xFFE0E0E0),
              ],
              stops: [
                _animation.value - 0.3,
                _animation.value,
                _animation.value + 0.3,
              ].map((e) => e.clamp(0.0, 1.0)).toList(),
            ),
          ),
        );
      },
    );
  }
}

class ProductCardSkeleton extends StatelessWidget {
  const ProductCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SkeletonLoader(
            height: 155,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
          ),
          Padding(
            padding: const EdgeInsets.all(10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 12, width: double.infinity),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 16,
                    width: 80,
                    borderRadius: BorderRadius.circular(4)),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 10,
                    width: 60,
                    borderRadius: BorderRadius.circular(4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class OrderCardSkeleton extends StatelessWidget {
  const OrderCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          SkeletonLoader(
            width: 64,
            height: 64,
            borderRadius: BorderRadius.circular(12),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 12, width: double.infinity),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 10,
                    width: 100,
                    borderRadius: BorderRadius.circular(4)),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    SkeletonLoader(
                        height: 20,
                        width: 80,
                        borderRadius: BorderRadius.circular(8)),
                    SkeletonLoader(
                        height: 14,
                        width: 60,
                        borderRadius: BorderRadius.circular(4)),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class CartItemSkeleton extends StatelessWidget {
  const CartItemSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          SkeletonLoader(
              width: 24, height: 24, borderRadius: BorderRadius.circular(4)),
          const SizedBox(width: 12),
          SkeletonLoader(
              width: 70, height: 70, borderRadius: BorderRadius.circular(12)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 12, width: double.infinity),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 14,
                    width: 60,
                    borderRadius: BorderRadius.circular(4)),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 10,
                    width: 80,
                    borderRadius: BorderRadius.circular(4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ChatConversationSkeleton extends StatelessWidget {
  const ChatConversationSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          SkeletonLoader(
              width: 52, height: 52, borderRadius: BorderRadius.circular(26)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 14, width: 120),
                const SizedBox(height: 6),
                SkeletonLoader(
                    height: 12,
                    width: double.infinity,
                    borderRadius: BorderRadius.circular(4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class NotificationSkeleton extends StatelessWidget {
  const NotificationSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonLoader(
              width: 46, height: 46, borderRadius: BorderRadius.circular(14)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 14, width: 150),
                const SizedBox(height: 6),
                const SkeletonLoader(height: 12, width: double.infinity),
                const SizedBox(height: 4),
                SkeletonLoader(
                    height: 12,
                    width: 200,
                    borderRadius: BorderRadius.circular(4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ReviewCardSkeleton extends StatelessWidget {
  const ReviewCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SkeletonLoader(
                  width: 44,
                  height: 44,
                  borderRadius: BorderRadius.circular(22)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SkeletonLoader(height: 14, width: 100),
                    const SizedBox(height: 6),
                    SkeletonLoader(
                        height: 12,
                        width: 80,
                        borderRadius: BorderRadius.circular(4)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const SkeletonLoader(height: 12, width: double.infinity),
          const SizedBox(height: 6),
          SkeletonLoader(
              height: 12, width: 250, borderRadius: BorderRadius.circular(4)),
        ],
      ),
    );
  }
}

class ProductDetailSkeleton extends StatelessWidget {
  const ProductDetailSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          const SkeletonLoader(height: 400, width: double.infinity),
          const SizedBox(height: 12),
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
                color: Colors.white, borderRadius: BorderRadius.circular(20)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonLoader(height: 26, width: 120),
                const SizedBox(height: 10),
                const SkeletonLoader(height: 16, width: double.infinity),
                const SizedBox(height: 12),
                Row(
                  children: [
                    SkeletonLoader(
                        height: 15,
                        width: 80,
                        borderRadius: BorderRadius.circular(4)),
                    const SizedBox(width: 8),
                    SkeletonLoader(
                        height: 12,
                        width: 100,
                        borderRadius: BorderRadius.circular(4)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
                color: Colors.white, borderRadius: BorderRadius.circular(20)),
            child: Row(
              children: [
                SkeletonLoader(
                    width: 48,
                    height: 48,
                    borderRadius: BorderRadius.circular(24)),
                const SizedBox(width: 12),
                const Expanded(
                    child: SkeletonLoader(height: 14, width: double.infinity)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class OrderDetailSkeleton extends StatelessWidget {
  const OrderDetailSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
                color: Colors.white, borderRadius: BorderRadius.circular(20)),
            child: Column(
              children: [
                Row(
                  children: [
                    SkeletonLoader(
                        width: 38,
                        height: 38,
                        borderRadius: BorderRadius.circular(11)),
                    const SizedBox(width: 10),
                    const Expanded(
                        child:
                            SkeletonLoader(height: 15, width: double.infinity)),
                    SkeletonLoader(
                        width: 80,
                        height: 28,
                        borderRadius: BorderRadius.circular(20)),
                  ],
                ),
                const SizedBox(height: 18),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: List.generate(
                      4,
                      (i) => SkeletonLoader(
                          width: 38,
                          height: 38,
                          borderRadius: BorderRadius.circular(19))),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
                color: Colors.white, borderRadius: BorderRadius.circular(20)),
            child: Column(
              children: [
                const SkeletonLoader(height: 15, width: 100),
                const SizedBox(height: 16),
                Row(
                  children: [
                    SkeletonLoader(
                        width: 68,
                        height: 68,
                        borderRadius: BorderRadius.circular(12)),
                    const SizedBox(width: 14),
                    const Expanded(
                        child:
                            SkeletonLoader(height: 14, width: double.infinity)),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ListSkeletonLoader extends StatelessWidget {
  final Widget itemSkeleton;
  final int itemCount;
  final EdgeInsets? padding;

  const ListSkeletonLoader({
    super.key,
    required this.itemSkeleton,
    this.itemCount = 5,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: padding ?? const EdgeInsets.all(16),
      itemCount: itemCount,
      itemBuilder: (context, index) => itemSkeleton,
    );
  }
}

class GridSkeletonLoader extends StatelessWidget {
  final int crossAxisCount;
  final double childAspectRatio;
  final int itemCount;
  final EdgeInsets? padding;

  const GridSkeletonLoader({
    super.key,
    this.crossAxisCount = 2,
    this.childAspectRatio = 0.64,
    this.itemCount = 6,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: padding ?? const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: itemCount,
      itemBuilder: (context, index) => const ProductCardSkeleton(),
    );
  }
}

class StoreDetailSkeleton extends StatelessWidget {
  const StoreDetailSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SkeletonLoader(height: 260, width: double.infinity),
        const SizedBox(height: 16),
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: Colors.white, borderRadius: BorderRadius.circular(20)),
          child: Row(
            children: [
              Expanded(
                  child: SkeletonLoader(
                      height: 44, borderRadius: BorderRadius.circular(14))),
              const SizedBox(width: 10),
              Expanded(
                  child: SkeletonLoader(
                      height: 44, borderRadius: BorderRadius.circular(14))),
            ],
          ),
        ),
      ],
    );
  }
}
