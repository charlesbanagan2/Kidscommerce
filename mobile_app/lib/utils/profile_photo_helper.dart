import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

/// Pick a profile photo from camera or gallery, upload to backend, return image URL.
class ProfilePhotoHelper {
  static final ImagePicker _picker = ImagePicker();

  /// Shows camera / gallery chooser, then uploads. Returns public image URL or null.
  static Future<String?> pickAndUploadProfilePhoto(BuildContext context) async {
    final source = await _chooseImageSource(context);
    if (source == null) return null;

    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
        preferredCameraDevice: CameraDevice.front,
      );
      if (image == null) return null;

      if (kIsWeb) {
        return await ApiService.uploadProfilePicture(File(image.path));
      }

      final file = File(image.path);
      if (!file.existsSync()) {
        throw Exception('Selected image file was not found');
      }

      return await ApiService.uploadProfilePicture(file);
    } catch (e) {
      debugPrint('Profile photo upload failed: $e');
      rethrow;
    }
  }

  static Future<ImageSource?> _chooseImageSource(BuildContext context) async {
    if (kIsWeb) {
      return ImageSource.gallery;
    }

    return showModalBottomSheet<ImageSource>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(8, 8, 8, 12),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const Text(
                  'Update profile photo',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                ListTile(
                  leading: const Icon(Icons.photo_camera_outlined),
                  title: const Text('Take Photo'),
                  subtitle: const Text('Use your camera'),
                  onTap: () =>
                      Navigator.pop(sheetContext, ImageSource.camera),
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library_outlined),
                  title: const Text('Choose from Gallery'),
                  subtitle: const Text('Pick from your photos'),
                  onTap: () =>
                      Navigator.pop(sheetContext, ImageSource.gallery),
                ),
                const SizedBox(height: 4),
                TextButton(
                  onPressed: () => Navigator.pop(sheetContext),
                  child: const Text('Cancel'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
