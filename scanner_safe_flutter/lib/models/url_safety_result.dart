class UrlSafetyResult {
  final String url;
  final bool isSafe;
  final double confidence;
  final String details;
  final DateTime timestamp;
  final String? finalUrl; // Store the final URL after redirects
  final bool isOfflineResult; // Indicates if the result was generated offline

  UrlSafetyResult({
    required this.url,
    required this.isSafe, 
    required this.confidence,
    required this.details,
    required this.timestamp,
    this.finalUrl,
    this.isOfflineResult = false, // Default to false (server result)
  });

  // For backward compatibility
  bool get safe => isSafe;
  String get message => details;

  factory UrlSafetyResult.fromJson(Map<String, dynamic> json) {
    return UrlSafetyResult(
      url: json['url'] as String,
      isSafe: json['is_safe'] as bool,
      confidence: (json['confidence'] as num).toDouble(),
      details: json['details'] as String,
      timestamp: DateTime.now(),
      finalUrl: json['final_url'] as String?,
      isOfflineResult: false, // Server results are not offline
    );
  }
} 