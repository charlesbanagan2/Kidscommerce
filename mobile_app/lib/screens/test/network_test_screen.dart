import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:io';

class NetworkTestScreen extends StatefulWidget {
  const NetworkTestScreen({super.key});

  @override
  State<NetworkTestScreen> createState() => _NetworkTestScreenState();
}

class _NetworkTestScreenState extends State<NetworkTestScreen> {
  final List<String> _logs = [];
  bool _testing = false;

  void _addLog(String message) {
    setState(() {
      _logs.add('${DateTime.now().toString().substring(11, 19)} - $message');
    });
    debugPrint('🔍 $message');
  }

  Future<void> _runTests() async {
    setState(() {
      _testing = true;
      _logs.clear();
    });

    _addLog('=== NETWORK TEST STARTED ===');

    // Test 1: Check internet connectivity
    _addLog('Test 1: Checking internet...');
    try {
      final result = await InternetAddress.lookup('google.com');
      if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
        _addLog('✅ Internet: Connected');
      }
    } catch (e) {
      _addLog('❌ Internet: No connection - $e');
    }

    // Test 2: Check backend IP reachability
    _addLog('Test 2: Checking backend IP 192.168.1.26...');
    try {
      final socket = await Socket.connect('192.168.1.26', 5000,
          timeout: const Duration(seconds: 5));
      _addLog('✅ Backend IP: Reachable');
      socket.destroy();
    } catch (e) {
      _addLog('❌ Backend IP: Cannot reach - $e');
    }

    // Test 3: HTTP request to backend
    _addLog('Test 3: HTTP GET to backend...');
    try {
      final response = await http
          .get(
            Uri.parse('http://192.168.1.26:5000/api/health'),
          )
          .timeout(const Duration(seconds: 10));
      _addLog('✅ HTTP: Status ${response.statusCode}');
      _addLog('   Response: ${response.body}');
    } catch (e) {
      _addLog('❌ HTTP: Failed - $e');
    }

    // Test 4: Products endpoint
    _addLog('Test 4: Products endpoint...');
    try {
      final response = await http
          .get(
            Uri.parse(
                'http://192.168.1.26:5000/api/v1/products?page=1&per_page=3'),
          )
          .timeout(const Duration(seconds: 10));
      _addLog('✅ Products: Status ${response.statusCode}');
      _addLog('   Response: ${response.body.substring(0, 100)}...');
    } catch (e) {
      _addLog('❌ Products: Failed - $e');
    }

    _addLog('=== TEST COMPLETED ===');
    setState(() {
      _testing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Network Test'),
        backgroundColor: Colors.orange,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: _testing ? null : _runTests,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                minimumSize: const Size(double.infinity, 50),
              ),
              child: _testing
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('RUN NETWORK TESTS',
                      style: TextStyle(fontSize: 16)),
            ),
          ),
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListView.builder(
                itemCount: _logs.length,
                itemBuilder: (context, index) {
                  final log = _logs[index];
                  Color color = Colors.white;
                  if (log.contains('✅')) color = Colors.green;
                  if (log.contains('❌')) color = Colors.red;
                  if (log.contains('===')) color = Colors.yellow;

                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Text(
                      log,
                      style: TextStyle(
                        color: color,
                        fontFamily: 'monospace',
                        fontSize: 12,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
