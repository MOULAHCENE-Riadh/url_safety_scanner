import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:scanner_safe_flutter/screens/result_screen.dart';
import 'package:scanner_safe_flutter/services/url_checker_service.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController controller = MobileScannerController();
  bool isProcessing = false;
  bool isCameraInitialized = false;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Code'),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: ValueListenableBuilder(
              valueListenable: controller.torchState,
              builder: (context, state, child) {
                switch (state) {
                  case TorchState.off:
                    return const Icon(Icons.flash_off, color: Colors.white);
                  case TorchState.on:
                    return const Icon(Icons.flash_on, color: Colors.yellow);
                }
              },
            ),
            onPressed: () => controller.toggleTorch(),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 5,
            child: Stack(
              alignment: Alignment.center,
              children: [
                MobileScanner(
                  controller: controller,
                  onDetect: _onDetect,
                  // Overlay to show scanning area
                  overlay: CustomPaint(
                    painter: ScannerOverlay(),
                    child: Container(),
                  ),
                ),
                if (isProcessing)
                  Container(
                    width: double.infinity,
                    height: double.infinity,
                    color: Colors.black.withOpacity(0.5),
                    child: const Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),
              ],
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              alignment: Alignment.center,
              padding: const EdgeInsets.all(16.0),
              child: const Text(
                'Position the QR code within the frame to scan',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _onDetect(BarcodeCapture capture) async {
    if (isProcessing || capture.barcodes.isEmpty) return;

    final barcode = capture.barcodes.first;
    if (barcode.rawValue == null) return;

    setState(() {
      isProcessing = true;
    });

    try {
      final code = barcode.rawValue!;
      print('Scanned QR code: $code');
      
      // Make sure we have a proper URL
      String url = code;
      if (!url.toLowerCase().startsWith('http://') && 
          !url.toLowerCase().startsWith('https://')) {
        // Check if it looks like a domain
        if (url.contains('.') && !url.contains(' ') && !url.contains('\n')) {
          url = 'https://$url';
          print('Formatted as URL: $url');
        }
      }
      
      final result = await UrlCheckerService().checkUrlSafety(url);

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(
            url: url,
            originalQrCode: code != url ? code : null,
            isSafe: result.safe,
            message: result.message,
            isOfflineResult: result.isOfflineResult,
          ),
        ),
      );
    } catch (e) {
      print('Error processing QR code: $e');
      if (!mounted) return;
      
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(
            url: 'Error scanning URL',
            isSafe: false,
            message: 'Failed to process QR code. Please try again. Error: ${e.toString()}',
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          isProcessing = false;
        });
      }
    }
  }
}

// Custom painter for scanner overlay
class ScannerOverlay extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final double boxWidth = size.width * 0.8;
    final double boxHeight = size.width * 0.8;
    final double left = (size.width - boxWidth) / 2;
    final double top = (size.height - boxHeight) / 2;
    final double right = left + boxWidth;
    final double bottom = top + boxHeight;

    final Paint borderPaint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5.0;

    // Draw outer rectangle
    canvas.drawRect(
      Rect.fromLTRB(left, top, right, bottom),
      borderPaint,
    );

    // Draw corner lines
    final double cornerSize = 30.0;
    
    // Top left
    canvas.drawLine(Offset(left, top + cornerSize), Offset(left, top), borderPaint);
    canvas.drawLine(Offset(left, top), Offset(left + cornerSize, top), borderPaint);
    
    // Top right
    canvas.drawLine(Offset(right - cornerSize, top), Offset(right, top), borderPaint);
    canvas.drawLine(Offset(right, top), Offset(right, top + cornerSize), borderPaint);
    
    // Bottom left
    canvas.drawLine(Offset(left, bottom - cornerSize), Offset(left, bottom), borderPaint);
    canvas.drawLine(Offset(left, bottom), Offset(left + cornerSize, bottom), borderPaint);
    
    // Bottom right
    canvas.drawLine(Offset(right - cornerSize, bottom), Offset(right, bottom), borderPaint);
    canvas.drawLine(Offset(right, bottom), Offset(right, bottom - cornerSize), borderPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
} 