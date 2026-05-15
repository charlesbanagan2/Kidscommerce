import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/buyer_provider.dart';
import 'providers/cart_provider.dart';
import 'providers/order_provider.dart';
import 'services/api_service.dart';
import 'theme/app_theme.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/buyer_app/buyer_home_screen.dart';
import 'screens/buyer_app/cart_screen.dart';
import 'screens/buyer_app/checkout_screen.dart';
import 'screens/buyer_app/orders_screen.dart';
import 'screens/buyer_app/profile_screen.dart';
// import 'screens/chat/chat_screen.dart'; // Removed: ChatScreen now requires parameters
import 'screens/rider/rider_home_screen.dart';
import 'screens/admin/admin_dashboard_screen.dart';

/// Kids Commerce Mobile App
/// Unified platform for Buyers, Riders, and Admins
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  ApiService.initializeBaseUrl();
  ApiService.logBuildMarker();
  await ApiService.bootstrapFromStorage();
  runApp(const KidsCommerceApp());
}

class KidsCommerceApp extends StatelessWidget {
  const KidsCommerceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => BuyerProvider()),
        ChangeNotifierProvider(create: (_) => CartProvider()),
        ChangeNotifierProvider(create: (_) => OrderProvider()),
      ],
      child: MaterialApp(
        title: 'Kids & Baby Store',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const AuthWrapper(),
        routes: {
          '/login': (context) => const WebStyleLoginScreen(),
          '/register': (context) => const WebStyleRegisterScreen(),
          '/home': (context) => const BuyerHomeScreen(),
          '/cart': (context) => const CartScreen(),
          '/checkout': (context) => const CheckoutScreen(),
          '/orders': (context) => const OrdersScreen(),
          '/profile': (context) => const ProfileScreen(),
          // '/messages': (context) => const ChatScreen(), // Removed: ChatScreen now requires parameters
          '/rider-dashboard': (context) => const RiderHomeScreen(),
          '/admin-dashboard': (context) => const AdminDashboardScreen(),
        },
      ),
    );
  }
}

/// AuthWrapper handles role-based routing
/// Routes users to appropriate dashboard based on role
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  late Future<void> _initializationFuture;

  @override
  void initState() {
    super.initState();
    _initializationFuture = _initializeApp();
  }

  Future<void> _initializeApp() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final buyerProvider = Provider.of<BuyerProvider>(context, listen: false);

    // Only initialize auth if not already initialized
    if (!authProvider.isAuthenticated && authProvider.tokens == null) {
      await authProvider.initialize();
    }

    // Only start auto-refresh if user is authenticated
    if (authProvider.isAuthenticated) {
      buyerProvider.startAutoRefresh();
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: _initializationFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading Kids Commerce...'),
                ],
              ),
            ),
          );
        }

        if (snapshot.hasError) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Error loading app'),
                  const SizedBox(height: 16),
                  Text(snapshot.error.toString()),
                ],
              ),
            ),
          );
        }

        return Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            // Always show BuyerHomeScreen as landing page
            // Users can browse products without login
            // Login required only for cart, checkout, and orders

            // If authenticated, route based on role
            if (authProvider.isAuthenticated) {
              final role = authProvider.user?.role ?? 'buyer';

              switch (role.toLowerCase()) {
                case 'admin':
                  return const AdminDashboardScreen();
                case 'seller':
                  return const BuyerHomeScreen(key: ValueKey('seller-home'));
                case 'rider':
                  return const RiderHomeScreen();
                case 'buyer':
                default:
                  return const BuyerHomeScreen(key: ValueKey('buyer-home'));
              }
            }

            // Not authenticated - show BuyerHomeScreen (guest mode)
            return const BuyerHomeScreen(key: ValueKey('guest-home'));
          },
        );
      },
    );
  }
}
