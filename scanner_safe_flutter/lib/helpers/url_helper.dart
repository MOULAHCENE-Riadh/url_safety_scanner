import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/material.dart';

class UrlHelper {
  /// Normalizes a URL string to ensure it has a proper scheme before launching
  static String normalizeUrl(String url) {
    if (url.isEmpty) {
      return '';
    }
    
    // If URL doesn't start with a scheme, add https://
    if (!url.toLowerCase().startsWith('http://') && 
        !url.toLowerCase().startsWith('https://')) {
      return 'https://$url';
    }
    
    return url;
  }
  
  /// Attempts to launch a URL, showing an error dialog if it fails
  static Future<bool> openUrl(BuildContext context, String url) async {
    final normalizedUrl = normalizeUrl(url);
    
    if (normalizedUrl.isEmpty) {
      return false;
    }
    
    try {
      final Uri uri = Uri.parse(normalizedUrl);
      final result = await launchUrl(
        uri, 
        mode: LaunchMode.externalApplication,
      );
      
      return result;
    } catch (e) {
      // Show error dialog
      if (context.mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Error'),
            content: Text('Could not open link: $url\n\nError: ${e.toString()}'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
      return false;
    }
  }
  
  /// Shows a confirmation dialog before launching a potentially unsafe URL
  static Future<void> openUrlWithWarning(BuildContext context, String url) async {
    final normalizedUrl = normalizeUrl(url);
    
    if (normalizedUrl.isEmpty) {
      return;
    }
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Warning!'),
        content: const Text(
          'This website has been flagged as potentially unsafe. '
          'Proceeding may put your device or data at risk. '
          'Are you sure you want to continue?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              openUrl(context, normalizedUrl);
            },
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: const Text('Proceed Anyway'),
          ),
        ],
      ),
    );
  }
} 