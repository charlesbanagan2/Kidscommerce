import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

/// Admin Dashboard Screen
/// Manages store operations, users, orders, and analytics
class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  // Brand colors
  static const Color primaryColor = Color(0xFF007bff);
  static const Color backgroundColor = Color(0xFFf8f9fa);
  static const Color cardBackground = Colors.white;
  static const Color textPrimary = Color(0xFF212529);
  static const Color textSecondary = Color(0xFF6c757d);
  static const Color borderColor = Color(0xFFdee2e6);

  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title: const Text('Admin Dashboard'),
        backgroundColor: primaryColor,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () {
              _showProfileMenu();
            },
          ),
        ],
      ),
      body: _buildContent(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        type: BottomNavigationBarType.fixed,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_bag_outlined),
            label: 'Orders',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people_outline),
            label: 'Users',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics_outlined),
            label: 'Analytics',
          ),
        ],
        onTap: _onItemTapped,
      ),
    );
  }

  Widget _buildContent() {
    switch (_selectedIndex) {
      case 0:
        return _buildDashboard();
      case 1:
        return _buildOrders();
      case 2:
        return _buildUsers();
      case 3:
        return _buildAnalytics();
      default:
        return _buildDashboard();
    }
  }

  Widget _buildDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Welcome to Admin Dashboard',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: textPrimary,
            ),
          ),
          const SizedBox(height: 24),

          // Stats Grid
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 1.5,
            children: [
              _buildStatCard(
                'Users',
                '1,256',
                Icons.people_outline,
                Colors.blue,
              ),
              _buildStatCard(
                'Orders',
                '342',
                Icons.shopping_bag_outlined,
                Colors.green,
              ),
              _buildStatCard(
                'Revenue',
                'â‚±45,230',
                Icons.trending_up_outlined,
                Colors.orange,
              ),
              _buildStatCard(
                'Riders',
                '89',
                Icons.motorcycle_outlined,
                Colors.purple,
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Recent Activity
          Container(
            decoration: BoxDecoration(
              color: cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Recent Orders',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                _buildOrderItem(
                    'Order #001', 'John Doe', 'â‚±2,500', 'Pending'),
                const Divider(),
                _buildOrderItem(
                    'Order #002', 'Jane Smith', 'â‚±3,200', 'Completed'),
                const Divider(),
                _buildOrderItem(
                    'Order #003', 'Bob Johnson', 'â‚±1,800', 'Shipped'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
      String title, String value, IconData icon, Color color) {
    return Container(
      decoration: BoxDecoration(
        color: cardBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Icon(icon, color: color, size: 32),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: textPrimary,
                ),
              ),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 12,
                  color: textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrderItem(
      String orderID, String customer, String amount, String status) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                orderID,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: textPrimary,
                ),
              ),
              Text(
                customer,
                style: const TextStyle(
                  fontSize: 12,
                  color: textSecondary,
                ),
              ),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                amount,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: status == 'Pending'
                      ? Colors.orange.withValues(alpha: 0.1)
                      : status == 'Completed'
                          ? Colors.green.withValues(alpha: 0.1)
                          : Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  status,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: status == 'Pending'
                        ? Colors.orange
                        : status == 'Completed'
                            ? Colors.green
                            : Colors.blue,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrders() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Orders Management',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            decoration: BoxDecoration(
              color: cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _buildOrderItem(
                    'Order #001', 'John Doe', 'â‚±2,500', 'Pending'),
                const Divider(),
                _buildOrderItem(
                    'Order #002', 'Jane Smith', 'â‚±3,200', 'Completed'),
                const Divider(),
                _buildOrderItem(
                    'Order #003', 'Bob Johnson', 'â‚±1,800', 'Shipped'),
                const Divider(),
                _buildOrderItem(
                    'Order #004', 'Alice Brown', 'â‚±4,100', 'Pending'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUsers() {
    return Center(
      child: ElevatedButton(
        onPressed: () {
          Navigator.pushNamed(context, '/admin/approve-users');
        },
        child: const Text('Approve New Users'),
      ),
    );
  }

  Widget _buildAnalytics() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Analytics & Reports',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: textPrimary,
            ),
          ),
          const SizedBox(height: 24),
          Container(
            decoration: BoxDecoration(
              color: cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Monthly Revenue',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  height: 200,
                  decoration: BoxDecoration(
                    color: backgroundColor,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Center(
                    child: Text(
                      'Chart Placeholder\nRevenue data will be displayed here',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: textSecondary),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Container(
            decoration: BoxDecoration(
              color: cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Key Metrics',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                _buildMetricRow('Average Order Value', 'â‚±3,450'),
                _buildMetricRow('Total Transactions', '1,234'),
                _buildMetricRow('Conversion Rate', '12.5%'),
                _buildMetricRow('Customer Satisfaction', '4.8/5'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: textSecondary),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: primaryColor,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  void _showProfileMenu() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('Profile'),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Settings'),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: () {
                Navigator.pop(context);
                _logout();
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _logout() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.logout();
    if (mounted) {
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    }
  }
}
