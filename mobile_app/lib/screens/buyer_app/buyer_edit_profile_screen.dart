import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../config/url_config.dart';
import '../../utils/profile_photo_helper.dart';

class BuyerEditProfileScreen extends StatefulWidget {
  const BuyerEditProfileScreen({super.key});
  @override
  State<BuyerEditProfileScreen> createState() => _BuyerEditProfileScreenState();
}

class _BuyerEditProfileScreenState extends State<BuyerEditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  bool _saving = false;
  bool _uploadingImage = false;
  String? _profileImageUrl;

  static const Color _primaryDark = Color(0xFF1a2f6b);
  static const Color _primary = Color(0xFF1e4db7);
  static const Color _bgColor = Color(0xFFF4F6FC);
  static const Color _cardColor = Colors.white;
  static const Color _textDark = Color(0xFF1A1F36);
  static const Color _textMid = Color(0xFF6B7280);
  static const Color _border = Color(0xFFE5E7EB);

  @override
  void initState() {
    super.initState();
    final user = Provider.of<AuthProvider>(context, listen: false).user;
    _name.text = user?.fullName ?? '';
    _email.text = user?.email ?? '';
    _phone.text = user?.phone ?? '';
    _profileImageUrl = user?.profileImage;
  }

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _pickAndUploadImage() async {
    setState(() => _uploadingImage = true);
    try {
      final imageUrl =
          await ProfilePhotoHelper.pickAndUploadProfilePhoto(context);
      if (imageUrl == null) return;

      await Provider.of<AuthProvider>(context, listen: false).refreshUser();

      if (!mounted) return;
      setState(() => _profileImageUrl = imageUrl);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Profile photo updated'),
        backgroundColor: Color(0xFF16A34A),
        behavior: SnackBarBehavior.floating,
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Failed to upload photo: $e'),
        backgroundColor: const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
      ));
    } finally {
      if (mounted) setState(() => _uploadingImage = false);
    }
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
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Profile updated successfully'),
          backgroundColor: Color(0xFF16A34A),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(12))),
          margin: EdgeInsets.all(16),
        ));
        Navigator.pop(context, true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content:
              Text('Error: ${authProvider.errorMessage ?? "Update failed"}'),
          backgroundColor: const Color(0xFFDC2626),
          behavior: SnackBarBehavior.floating,
        ));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Error: $e'),
        backgroundColor: const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
      ));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgColor,
      appBar: AppBar(
        backgroundColor: _cardColor,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        surfaceTintColor: Colors.transparent,
        title: const Text('Edit Profile',
            style: TextStyle(
                color: _textDark,
                fontWeight: FontWeight.w800,
                fontSize: 17)),
        iconTheme: const IconThemeData(color: _textDark),
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
                color: _textMid,
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
            fontSize: 14, fontWeight: FontWeight.w600, color: _textDark),
        decoration: InputDecoration(
          filled: true,
          fillColor: _cardColor,
          prefixIcon: Icon(icon, size: 19, color: _primary),
          labelText: label,
          labelStyle: const TextStyle(
              color: _textMid, fontSize: 13, fontWeight: FontWeight.w600),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          enabledBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: _border),
              borderRadius: BorderRadius.circular(14)),
          focusedBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: _primary, width: 1.5),
              borderRadius: BorderRadius.circular(14)),
          errorBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: Color(0xFFDC2626)),
              borderRadius: BorderRadius.circular(14)),
          focusedErrorBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: Color(0xFFDC2626), width: 1.5),
              borderRadius: BorderRadius.circular(14)),
        ),
      ),
    );
  }

  Widget _avatarSection() {
    final initial = _name.text.isNotEmpty ? _name.text[0].toUpperCase() : 'B';
    final imageUrl = _profileImageUrl;

    return Center(
      child: Stack(children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            gradient: imageUrl == null || imageUrl.isEmpty
                ? const LinearGradient(
                    colors: [_primaryDark, _primary],
                  )
                : null,
            borderRadius: BorderRadius.circular(28),
          ),
          child: imageUrl != null && imageUrl.isNotEmpty
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(28),
                  child: Image.network(
                    UrlConfig.toAbsoluteImageUrl(imageUrl),
                    width: 100,
                    height: 100,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Center(
                      child: Text(initial,
                          style: const TextStyle(
                              fontSize: 42,
                              fontWeight: FontWeight.w800,
                              color: Colors.white)),
                    ),
                  ),
                )
              : Center(
                  child: Text(initial,
                      style: const TextStyle(
                          fontSize: 42,
                          fontWeight: FontWeight.w800,
                          color: Colors.white)),
                ),
        ),
        if (_uploadingImage)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black45,
                borderRadius: BorderRadius.circular(28),
              ),
              child: const Center(
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2.5,
                ),
              ),
            ),
          ),
        Positioned(
          bottom: 0,
          right: 0,
          child: GestureDetector(
            onTap: _uploadingImage ? null : _pickAndUploadImage,
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
