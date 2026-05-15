// EXAMPLE: How to use Delivery Fee Service in your screens

import 'package:flutter/material.dart';
import '../services/delivery_fee_service.dart';
import '../providers/cart_provider.dart';
import '../providers/buyer_provider.dart';
import 'package:provider/provider.dart';

// ============================================
// EXAMPLE 1: Cart Screen
// ============================================
class CartScreenExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final cartProvider = context.watch<CartProvider>();
    final buyerProvider = context.watch<BuyerProvider>();

    // Get buyer's address
    final buyerAddress = buyerProvider.buyer?.address;

    // Extract province from address
    final province =
        DeliveryFeeService.extractProvinceFromAddress(buyerAddress);

    // Calculate delivery fee
    final deliveryFee = cartProvider.getDeliveryFee(province);
    final grandTotal = cartProvider.getGrandTotal(province);

    return Column(
      children: [
        // Subtotal
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Subtotal'),
            Text('₱${cartProvider.subtotal.toStringAsFixed(2)}'),
          ],
        ),

        // Tax
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Tax (12%)'),
            Text('₱${cartProvider.tax.toStringAsFixed(2)}'),
          ],
        ),

        // Delivery Fee
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
                'Delivery Fee (${cartProvider.items.length} items to ${province ?? "Laguna"})'),
            Text('₱${deliveryFee.toStringAsFixed(2)}'),
          ],
        ),

        const Divider(),

        // Grand Total
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Total', style: TextStyle(fontWeight: FontWeight.bold)),
            Text('₱${grandTotal.toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ],
    );
  }
}

// ============================================
// EXAMPLE 2: Checkout Screen
// ============================================
class CheckoutScreenExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final cartProvider = context.watch<CartProvider>();
    final buyerProvider = context.watch<BuyerProvider>();

    final buyerAddress = buyerProvider.buyer?.address ?? '';
    final province =
        DeliveryFeeService.extractProvinceFromAddress(buyerAddress);
    final deliveryFee = cartProvider.getDeliveryFee(province);

    return Column(
      children: [
        // Delivery Address Display
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Delivery Address',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(buyerAddress),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Province: ${province ?? "Not detected (using Laguna rate)"}',
                  style: TextStyle(fontSize: 12, color: Colors.blue.shade700),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Delivery Fee Info
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              const Icon(Icons.local_shipping, color: Colors.blue),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Delivery Fee',
                        style: TextStyle(fontWeight: FontWeight.w600)),
                    Text(
                      '${cartProvider.items.length} items × ₱${(deliveryFee / cartProvider.items.length).toStringAsFixed(0)} = ₱${deliveryFee.toStringAsFixed(2)}',
                      style:
                          TextStyle(fontSize: 12, color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ============================================
// EXAMPLE 3: Direct Calculation
// ============================================
void directCalculationExample() {
  const address1 = "123 Main St, Biñan, Laguna";
  const address2 = "456 Ortigas Ave, Pasig, Rizal";

  final province1 = DeliveryFeeService.extractProvinceFromAddress(address1);
  final province2 = DeliveryFeeService.extractProvinceFromAddress(address2);

  // ignore: avoid_print
  print('Province 1: $province1'); // Laguna
  // ignore: avoid_print
  print('Province 2: $province2'); // Rizal

  final fee1 = DeliveryFeeService.calculateDeliveryFee(province1!);
  final fee2 = DeliveryFeeService.calculateDeliveryFee(province2!);

  // ignore: avoid_print
  print('Fee 1: ₱$fee1'); // ₱36.0
  // ignore: avoid_print
  print('Fee 2: ₱$fee2'); // ₱72.0
}
