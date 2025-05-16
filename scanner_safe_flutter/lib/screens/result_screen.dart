import 'package:flutter/material.dart';
import 'package:scanner_safe_flutter/helpers/url_helper.dart';

class ResultScreen extends StatelessWidget {
  final String url;
  final bool isSafe;
  final String message;
  final String? originalQrCode;
  final bool isOfflineResult;

  const ResultScreen({
    required this.url,
    required this.isSafe,
    required this.message,
    this.originalQrCode,
    this.isOfflineResult = false,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Result'),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: isSafe ? Colors.green.shade50 : Colors.red.shade50,
                  borderRadius: BorderRadius.circular(60),
                ),
                child: Icon(
                  isSafe ? Icons.check_circle : Icons.error,
                  size: 80,
                  color: isSafe ? Colors.green : Colors.red,
                ),
              ),
              const SizedBox(height: 32),
              Wrap(
                alignment: WrapAlignment.center,
                crossAxisAlignment: WrapCrossAlignment.center,
                spacing: 8,
                children: [
                  Text(
                    isSafe ? 'Safe to Visit' : 'WARNING: Potentially Unsafe',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: isSafe ? Colors.green : Colors.red,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  if (isOfflineResult)
                    Tooltip(
                      message: 'Offline analysis with limited accuracy',
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade200,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.offline_bolt, size: 16, color: Colors.grey.shade700),
                            const SizedBox(width: 4),
                            Text(
                              'OFFLINE',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.grey.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.black87,
                ),
              ),
              if (isOfflineResult) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.amber.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.amber.shade800),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'This analysis was performed offline with limited accuracy. For more reliable results, connect to the server.',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.amber.shade900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 32),
              const Text(
                'URL',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  url,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Colors.black87,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              
              if (originalQrCode != null) ...[
                const SizedBox(height: 24),
                const Text(
                  'Original QR Code Content',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    originalQrCode!,
                    style: const TextStyle(
                      fontSize: 14,
                      fontFamily: 'monospace',
                      color: Colors.black87,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
              
              const Spacer(),
              
              // Conditional buttons based on safety
              if (isSafe) ...[
                ElevatedButton.icon(
                  onPressed: () {
                    UrlHelper.openUrl(context, url);
                  },
                  icon: const Icon(Icons.open_in_browser),
                  label: const Text('Visit Website'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                    textStyle: const TextStyle(fontSize: 18),
                    minimumSize: const Size(double.infinity, 50),
                  ),
                ),
                const SizedBox(height: 16),
              ] else if (url != 'Error scanning URL') ...[
                ElevatedButton.icon(
                  onPressed: () {
                    UrlHelper.openUrlWithWarning(context, url);
                  },
                  icon: const Icon(Icons.warning),
                  label: const Text('Proceed at Your Own Risk'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                    textStyle: const TextStyle(fontSize: 18),
                    minimumSize: const Size(double.infinity, 50),
                  ),
                ),
                const SizedBox(height: 16),
              ],
              
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).popUntil((route) => route.isFirst);
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  textStyle: const TextStyle(fontSize: 18),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text('Back to Home'),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
} 