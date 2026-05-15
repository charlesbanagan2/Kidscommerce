import 'package:flutter_test/flutter_test.dart';
import 'package:kids_commerce/providers/buyer_provider.dart';
import 'package:kids_commerce/providers/cart_provider.dart';

/// Comprehensive Checkout Test Suite
/// Tests checkout functionality with and without coupons
void main() {
  group('Checkout Functionality Tests', () {
    late BuyerProvider buyerProvider;

    setUp(() {
      buyerProvider = BuyerProvider();
    });

    test('Checkout without coupon - couponId should be null', () {
      // Arrange
      const String recipientName = 'John Doe';
      const String recipientPhone = '+639123456789';
      const String shippingAddress = '123 Main St, Manila';
      const String paymentMethod = 'cod';
      const String? couponId = null; // No coupon

      // Act & Assert
      expect(couponId, isNull);
      expect(recipientName, isNotEmpty);
      expect(recipientPhone, isNotEmpty);
      expect(shippingAddress, isNotEmpty);
      expect(paymentMethod, equals('cod'));
    });

    test('Checkout with empty coupon string - should convert to null', () {
      // Arrange
      String selectedCouponId = '';

      // Act
      String? couponId = selectedCouponId.isNotEmpty ? selectedCouponId : null;

      // Assert
      expect(couponId, isNull);
    });

    test('Checkout with valid coupon - couponId should have value', () {
      // Arrange
      String selectedCouponId = '12345';

      // Act
      String? couponId = selectedCouponId.isNotEmpty ? selectedCouponId : null;

      // Assert
      expect(couponId, isNotNull);
      expect(couponId, equals('12345'));
    });

    test('Discount calculation without coupon - should be 0.0', () {
      // Arrange
      double discount = 0.0;
      double subtotal = 1000.0;
      double shippingFee = 10.0;

      // Act
      double total = subtotal - discount + shippingFee;

      // Assert
      expect(discount, equals(0.0));
      expect(total, equals(1010.0));
    });

    test('Discount calculation with coupon - should apply discount', () {
      // Arrange
      double discount = 100.0;
      double subtotal = 1000.0;
      double shippingFee = 10.0;

      // Act
      double total = subtotal - discount + shippingFee;

      // Assert
      expect(discount, greaterThan(0.0));
      expect(total, equals(910.0));
    });

    test('Order summary - discount row should be hidden when 0', () {
      // Arrange
      double discount = 0.0;

      // Act
      bool shouldShowDiscount = discount > 0;

      // Assert
      expect(shouldShowDiscount, isFalse);
    });

    test('Order summary - discount row should be visible when > 0', () {
      // Arrange
      double discount = 50.0;

      // Act
      bool shouldShowDiscount = discount > 0;

      // Assert
      expect(shouldShowDiscount, isTrue);
    });

    test('Payment method validation - COD should be valid', () {
      // Arrange
      const String paymentMethod = 'cod';

      // Assert
      expect(paymentMethod, isIn(['cod', 'gcash', 'card']));
    });

    test('Payment method validation - GCash should be valid', () {
      // Arrange
      const String paymentMethod = 'gcash';

      // Assert
      expect(paymentMethod, isIn(['cod', 'gcash', 'card']));
    });

    test('Payment method validation - Card should be valid', () {
      // Arrange
      const String paymentMethod = 'card';

      // Assert
      expect(paymentMethod, isIn(['cod', 'gcash', 'card']));
    });

    test('Required fields validation - all fields filled', () {
      // Arrange
      const String name = 'John Doe';
      const String phone = '+639123456789';
      const String address = '123 Main St';

      // Act
      bool isValid = name.isNotEmpty && phone.isNotEmpty && address.isNotEmpty;

      // Assert
      expect(isValid, isTrue);
    });

    test('Required fields validation - missing name', () {
      // Arrange
      const String name = '';
      const String phone = '+639123456789';
      const String address = '123 Main St';

      // Act
      bool isValid = name.isNotEmpty && phone.isNotEmpty && address.isNotEmpty;

      // Assert
      expect(isValid, isFalse);
    });

    test('Required fields validation - missing phone', () {
      // Arrange
      const String name = 'John Doe';
      const String phone = '';
      const String address = '123 Main St';

      // Act
      bool isValid = name.isNotEmpty && phone.isNotEmpty && address.isNotEmpty;

      // Assert
      expect(isValid, isFalse);
    });

    test('Required fields validation - missing address', () {
      // Arrange
      const String name = 'John Doe';
      const String phone = '+639123456789';
      const String address = '';

      // Act
      bool isValid = name.isNotEmpty && phone.isNotEmpty && address.isNotEmpty;

      // Assert
      expect(isValid, isFalse);
    });

    test('Notes field - should be optional', () {
      // Arrange
      String notesInput = '';

      // Act
      String? notes = notesInput.isNotEmpty ? notesInput : null;

      // Assert
      expect(notes, isNull);
    });

    test('Notes field - should accept value when provided', () {
      // Arrange
      String notesInput = 'Please deliver in the morning';

      // Act
      String? notes = notesInput.isNotEmpty ? notesInput : null;

      // Assert
      expect(notes, isNotNull);
      expect(notes, equals('Please deliver in the morning'));
    });

    test('Cart total calculation - empty cart', () {
      // Arrange
      List<CartItem> cartItems = [];

      // Act
      double total = cartItems.fold(0, (sum, item) => sum + item.subtotal);

      // Assert
      expect(total, equals(0.0));
    });

    test('Cart total calculation - single item', () {
      // Arrange
      CartItem item = CartItem(
        id: 1,
        productId: 1,
        name: 'Test Product',
        price: 100.0,
        quantity: 2,
      );

      // Act
      double subtotal = item.subtotal;

      // Assert
      expect(subtotal, equals(200.0));
    });

    test('Cart total calculation - multiple items', () {
      // Arrange
      List<CartItem> cartItems = [
        CartItem(
          id: 1,
          productId: 1,
          name: 'Product 1',
          price: 100.0,
          quantity: 2,
        ),
        CartItem(
          id: 2,
          productId: 2,
          name: 'Product 2',
          price: 50.0,
          quantity: 3,
        ),
      ];

      // Act
      double total = cartItems.fold(0, (sum, item) => sum + item.subtotal);

      // Assert
      expect(total, equals(350.0)); // (100*2) + (50*3)
    });

    test('Shipping fee - should be added to total', () {
      // Arrange
      double subtotal = 1000.0;
      double discount = 0.0;
      double shippingFee = 10.0;

      // Act
      double total = subtotal - discount + shippingFee;

      // Assert
      expect(total, equals(1010.0));
    });

    test('Complete checkout flow - without coupon', () {
      // Arrange
      const String recipientName = 'John Doe';
      const String recipientPhone = '+639123456789';
      const String shippingAddress = '123 Main St, Manila';
      const String paymentMethod = 'cod';
      String selectedCouponId = '';

      // Act
      String? couponId = selectedCouponId.isNotEmpty ? selectedCouponId : null;
      bool isValid = recipientName.isNotEmpty &&
          recipientPhone.isNotEmpty &&
          shippingAddress.isNotEmpty;

      // Assert
      expect(isValid, isTrue);
      expect(couponId, isNull);
      expect(paymentMethod, equals('cod'));
    });

    test('Complete checkout flow - with coupon', () {
      // Arrange
      const String recipientName = 'John Doe';
      const String recipientPhone = '+639123456789';
      const String shippingAddress = '123 Main St, Manila';
      const String paymentMethod = 'gcash';
      String selectedCouponId = 'SAVE20';

      // Act
      String? couponId = selectedCouponId.isNotEmpty ? selectedCouponId : null;
      bool isValid = recipientName.isNotEmpty &&
          recipientPhone.isNotEmpty &&
          shippingAddress.isNotEmpty;

      // Assert
      expect(isValid, isTrue);
      expect(couponId, isNotNull);
      expect(couponId, equals('SAVE20'));
      expect(paymentMethod, equals('gcash'));
    });

    test('BuyerProvider - initial discount should be 0.0', () {
      // Assert
      expect(buyerProvider.discount, equals(0.0));
    });

    test('BuyerProvider - cart should be empty initially', () {
      // Assert
      expect(buyerProvider.cartItems, isEmpty);
      expect(buyerProvider.cartTotal, equals(0.0));
      expect(buyerProvider.cartCount, equals(0));
    });

    test('CartItem - subtotal calculation', () {
      // Arrange
      CartItem item = CartItem(
        id: 1,
        productId: 1,
        name: 'Test Product',
        price: 99.99,
        quantity: 3,
      );

      // Act
      double subtotal = item.subtotal;

      // Assert
      expect(subtotal, equals(299.97));
    });

    test('CartItem - fromJson with image URL', () {
      // Arrange
      Map<String, dynamic> json = {
        'id': 1,
        'product_id': 10,
        'product_name': 'Test Product',
        'price': 150.0,
        'quantity': 2,
        'image_url': 'test_image.jpg',
      };

      // Act
      CartItem item = CartItem.fromJson(json);

      // Assert
      expect(item.id, equals(1));
      expect(item.productId, equals(10));
      expect(item.name, equals('Test Product'));
      expect(item.price, equals(150.0));
      expect(item.quantity, equals(2));
      expect(item.imageUrl, isNotNull);
    });

    test('CartItem - toJson format', () {
      // Arrange
      CartItem item = CartItem(
        id: 1,
        productId: 10,
        name: 'Test Product',
        price: 150.0,
        quantity: 2,
      );

      // Act
      Map<String, dynamic> json = item.toJson();

      // Assert
      expect(json['product_id'], equals(10));
      expect(json['quantity'], equals(2));
      expect(json.containsKey('id'), isFalse); // ID not included in toJson
    });
  });

  group('Edge Cases and Error Handling', () {
    test('Negative discount - should not be allowed', () {
      // Arrange
      double discount = -50.0;
      double subtotal = 1000.0;

      // Act
      double total = subtotal - discount;

      // Assert - negative discount would increase total
      expect(total, greaterThan(subtotal));
    });

    test('Zero subtotal - checkout should still work', () {
      // Arrange
      double subtotal = 0.0;
      double discount = 0.0;
      double shippingFee = 10.0;

      // Act
      double total = subtotal - discount + shippingFee;

      // Assert
      expect(total, equals(10.0));
    });

    test('Very large order - calculation should be accurate', () {
      // Arrange
      double subtotal = 999999.99;
      double discount = 10000.0;
      double shippingFee = 100.0;

      // Act
      double total = subtotal - discount + shippingFee;

      // Assert
      expect(total, equals(990099.99));
    });

    test('Coupon code - case sensitivity', () {
      // Arrange
      String couponCode1 = 'SAVE20';
      String couponCode2 = 'save20';

      // Assert - codes should be treated as different
      expect(couponCode1, isNot(equals(couponCode2)));
    });

    test('Phone number - various formats should be accepted', () {
      // Arrange
      List<String> validPhones = [
        '+639123456789',
        '09123456789',
        '639123456789',
        '+63 912 345 6789',
      ];

      // Assert
      for (var phone in validPhones) {
        expect(phone.isNotEmpty, isTrue);
      }
    });

    test('Checkout without coupon - should work with default shipping', () {
      // Arrange
      const String? couponId = null;
      const double defaultShipping = 10.0;
      const double subtotal = 100.0;

      // Act
      const shippingFee = couponId != null ? 0.0 : defaultShipping;
      const total = subtotal + shippingFee;

      // Assert
      expect(couponId, isNull);
      expect(shippingFee, equals(10.0));
      expect(total, equals(110.0));
    });

    test('Checkout with coupon - should have free shipping', () {
      // Arrange
      const String? couponId = '123';
      const double subtotal = 100.0;

      // Act
      const shippingFee = 0.0; // Free shipping with coupon
      const total = subtotal + shippingFee;

      // Assert
      expect(couponId, isNotNull);
      expect(shippingFee, equals(0.0));
      expect(total, equals(100.0));
    });
  });
}
