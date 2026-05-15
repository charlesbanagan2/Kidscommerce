// rider_edit_profile_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class RiderEditProfileScreen extends StatefulWidget {
  const RiderEditProfileScreen({super.key});
  @override
  State<RiderEditProfileScreen> createState() => _RiderEditProfileScreenState();
}

class _RiderEditProfileScreenState extends State<RiderEditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  bool _saving = false;

  static const Color _primary = Color(0xFFFA6B02);
  static const Color _bg = Color(0xFFF4F5F9);
  static const Color _border = Color(0xFFE8EAF0);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSub = Color(0xFF64748B);

  @override
  void initState() {
    super.initState();
    final user = Provider.of<AuthProvider>(context, listen: false).user;
    _name.text = user?.fullName ?? '';
    _email.text = user?.email ?? '';
    _phone.text = user?.phone ?? '';
  }

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final nameParts = _name.text.trim().split(' ');
      final firstName = nameParts.isNotEmpty ? nameParts[0] : '';
      final lastName =
          nameParts.length > 1 ? nameParts.sublist(1).join(' ') : '';

      final updates = {
        'first_name': firstName,
        'last_name': lastName,
        'email': _email.text.trim(),
        'phone': _phone.text.trim(),
      };

      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final success = await authProvider.updateProfile(updates);

      if (!mounted) return;

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: const Text('Profile updated successfully'),
          backgroundColor: const Color(0xFF059669),
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          margin: const EdgeInsets.all(16),
        ));
        Navigator.pop(context, true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content:
              Text('Error: ${authProvider.errorMessage ?? "Update failed"}'),
          backgroundColor: Colors.red.shade600,
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          margin: const EdgeInsets.all(16),
        ));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Error: $e'),
        backgroundColor: Colors.red.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        margin: const EdgeInsets.all(16),
      ));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        surfaceTintColor: Colors.transparent,
        title: const Text('Edit Profile',
            style: TextStyle(
                color: _textPrimary,
                fontWeight: FontWeight.w800,
                fontSize: 17)),
        iconTheme: const IconThemeData(color: _textPrimary),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
            children: [
              _avatarSection(),
              const SizedBox(height: 22),
              _sectionLabel('Personal Information'),
              _field(_name, 'Full Name', Icons.person_rounded,
                  validator: _required),
              _field(_email, 'Email', Icons.email_rounded,
                  keyboard: TextInputType.emailAddress,
                  validator: (v) => (v == null || !v.contains('@'))
                      ? 'Enter a valid email'
                      : null),
              _field(_phone, 'Phone Number', Icons.phone_rounded,
                  keyboard: TextInputType.phone, validator: _required),
              const SizedBox(height: 28),
              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: _saving ? null : _save,
                  style: ElevatedButton.styleFrom(
                      backgroundColor: _primary,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14))),
                  child: _saving
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2.4))
                      : const Text('Save Changes',
                          style: TextStyle(
                              fontSize: 15, fontWeight: FontWeight.w800)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _required(String? v) =>
      (v == null || v.trim().isEmpty) ? 'This field is required' : null;

  Widget _sectionLabel(String text) => Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 10),
        child: Text(text.toUpperCase(),
            style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: _textSub,
                letterSpacing: 1.2)),
      );

  Widget _field(TextEditingController c, String label, IconData icon,
      {TextInputType keyboard = TextInputType.text,
      String? Function(String?)? validator}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: c,
        keyboardType: keyboard,
        validator: validator,
        style: const TextStyle(
            fontSize: 14, fontWeight: FontWeight.w600, color: _textPrimary),
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.white,
          prefixIcon: Icon(icon, size: 19, color: _primary),
          labelText: label,
          labelStyle: const TextStyle(
              color: _textSub, fontSize: 13, fontWeight: FontWeight.w600),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          enabledBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: _border),
              borderRadius: BorderRadius.circular(14)),
          focusedBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: _primary, width: 1.5),
              borderRadius: BorderRadius.circular(14)),
          errorBorder: OutlineInputBorder(
              borderSide: BorderSide(color: Colors.red.shade400),
              borderRadius: BorderRadius.circular(14)),
          focusedErrorBorder: OutlineInputBorder(
              borderSide: BorderSide(color: Colors.red.shade400, width: 1.5),
              borderRadius: BorderRadius.circular(14)),
        ),
      ),
    );
  }

  Widget _avatarSection() {
    final initial = _name.text.isNotEmpty ? _name.text[0].toUpperCase() : 'R';
    return Center(
      child: Stack(children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: [Color(0xFFFA6B02), Color(0xFFFF9A3C)]),
            borderRadius: BorderRadius.circular(28),
          ),
          child: Center(
              child: Text(initial,
                  style: const TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.w800,
                      color: Colors.white))),
        ),
        Positioned(
          bottom: 0,
          right: 0,
          child: GestureDetector(
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                  content:
                      Text('Photo upload — connect to image_picker package'),
                  behavior: SnackBarBehavior.floating));
            },
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                  color: _primary,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 3)),
              child: const Icon(Icons.camera_alt_rounded,
                  color: Colors.white, size: 16),
            ),
          ),
        ),
      ]),
    );
  }
}
