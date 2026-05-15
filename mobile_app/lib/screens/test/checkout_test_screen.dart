import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';
import '../../providers/auth_provider.dart';

class CheckoutTestScreen extends StatefulWidget {
  const CheckoutTestScreen({Key? key}) : super(key: key);

  @override
  State<CheckoutTestScreen> createState() => _CheckoutTestScreenState();
}

class _CheckoutTestScreenState extends State<CheckoutTestScreen> {
  final List<String> _testLogs = [];
  bool _isRunning = false;
  bool _testPassed = false;

  void _log(String message) {
    setState(() {
      _testLogs.add(message);
    });
    debugPrint(message);
  }

  Future<void> _runCheckoutTest() async {
    setState(() {
      _testLogs.clear();
      _isRunning = true;
      _testPassed = false;
    });

    final buyerProvider = context.read<BuyerProvider>();
    final authProvider = context.read<AuthProvider>();

    try {
      _log('============================================');
      _log('CHECKOUT TEST STARTED');
      _log('============================================\n');

      _log('1. Checking authentication...');
      if (!authProvider.isAuthenticated) {
        _log('❌ Not authenticated');
        throw Exception('Please login first');
      }
      _log('✅ User authenticated');
      _log('   User ID: ${authProvider.user?.id}');
      _log('   Email: ${authProvider.user?.email}\n');

      _log('2. Fetching cart...');
      await buyerProvider.fetchCart();
      
      if (buyerProvider.cartItems.isEmpty) {
        _log('❌ Cart is empty');
        throw Exception('Please add items to cart first');
      }
      
      _log('✅ Cart fetched successfully');
      _log('   Items: ${buyerProvider.cartItems.length}');
      for (var i = 0; i < buyerProvider.cartItems.length; i++) {
        final item = buyerProvider.cartItems[i];
        _log('   Item ${i + 1}: ${item.name} x${item.quantity} @ ₱${item.price}');
      }
      _log('   Total: ₱${buyerProvider.cartTotal.toStringAsFixed(2)}\n');

      _log('3. Preparing checkout data...');
      final selectedItemIds = buyerProvider.cartItems.map((item) => item.id).toList();
      
      _log('   Selected items: $selectedItemIds\n');

      _log('4. Performing checkout...');
      final order = await buyerProvider.checkout(
        recipientName: 'Test User',
        recipientPhone: '09123456789',
        shippingAddress: 'Test Address, Test City, Test Province',
        paymentMethod: 'cod',
        notes: 'Test order from checkout test screen',
        selectedItemIds: selectedItemIds,
        shippingFee: 10.0,
      );

      if (order == null) {
        _log('❌ Checkout failed');
        _log('   Error: ${buyerProvider.errorMessage ?? "Unknown error"}');
        throw Exception(buyerProvider.errorMessage ?? 'Checkout failed');
      }

      _log('✅ Checkout successful!\n');
      _log('5. Validating order...');
      _log('   Order ID: ${order.id}');
      _log('   Status: ${order.status}');
      _log('   Total: ₱${order.totalAmount.toStringAsFixed(2)}');
      _log('   Payment: ${order.paymentMethod}');
      _log('   Items: ${order.items.length}');
      
      for (var i = 0; i < order.items.length; i++) {
        final item = order.items[i];
        _log('   Item ${i + 1}: ${item.productName} x${item.quantity}');
      }

      if (order.id <= 0) throw Exception('Invalid order ID');
      if (order.status.isEmpty) throw Exception('Missing order status');
      if (order.totalAmount <= 0) throw Exception('Invalid total amount');
      if (order.items.isEmpty) throw Exception('Order has no items');

      _log('\n✅ All validations passed!');
      _log('\n============================================');
      _log('✅ CHECKOUT TEST PASSED!');
      _log('============================================');

      setState(() {
        _testPassed = true;
      });

    } catch (e) {
      _log('\n❌ TEST FAILED!');
      _log('Error: $e');
      _log('\n============================================');
      _log('❌ CHECKOUT TEST FAILED!');
      _log('============================================');
    } finally {
      setState(() {
        _isRunning = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Checkout Test'),
        backgroundColor: Colors.blue,
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey[100],
            child: Column(
              children: [
                ElevatedButton.icon(
                  onPressed: _isRunning ? null : _runCheckoutTest,
                  icon: _isRunning
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Icon(Icons.play_arrow),
                  label: Text(_isRunning ? 'Running Test...' : 'Run Checkout Test'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 50),
                  ),
                ),
                if (_testLogs.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _testPassed ? '✅ Test Passed' : (_isRunning ? '⏳ Running...' : '❌ Test Failed'),
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _testPassed ? Colors.green : (_isRunning ? Colors.orange : Colors.red),
                        ),
                      ),
                      TextButton.icon(
                        onPressed: () {
                          setState(() {
                            _testLogs.clear();
                          });
                        },
                        icon: const Icon(Icons.clear, size: 16),
                        label: const Text('Clear'),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
          Expanded(
            child: _testLogs.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.science, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          'Press "Run Checkout Test" to start',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Make sure you have items in your cart',
                          style: TextStyle(color: Colors.grey[500], fontSize: 12),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _testLogs.length,
                    itemBuilder: (context, index) {
                      final log = _testLogs[index];
                      final isError = log.contains('❌');
                      final isSuccess = log.contains('✅');
                      final isWarning = log.contains('⚠️');
                      final isHeader = log.contains('====');
                      
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text(
                          log,
                          style: TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 12,
                            color: isError
                                ? Colors.red[700]
                                : isSuccess
                                    ? Colors.green[700]
                                    : isWarning
                                        ? Colors.orange[700]
                                        : isHeader
                                            ? Colors.blue[700]
                                            : Colors.black87,
                            fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
