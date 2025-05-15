import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:scanner_safe_flutter/models/url_safety_result.dart';
import 'dart:async';

class UrlCheckerService {
  // Cache successfully connected URL
  static String? _cachedWorkingUrl;
  
  // Backend URLs based on platform
  static List<String> get serverUrls {
    final List<String> urls = [];
    
    if (kIsWeb) {
      // For web
      urls.add('http://localhost:8000');
    } else if (Platform.isAndroid) {
      // For Android - try all possible connections in order
      urls.add('http://10.0.2.2:8000');        // Android emulator special IP
      urls.add('http://192.168.1.89:8000');    // Specific computer IP 
      
      // Common subnet IPs to try (192.168.1.x)
      for (int i = 1; i <= 10; i++) {
        urls.add('http://192.168.1.$i:8000');
      }
      
      // Alternative common subnet (192.168.0.x)
      for (int i = 1; i <= 10; i++) {
        urls.add('http://192.168.0.$i:8000');
      }
      
      urls.add('http://localhost:8000');      // Local test
      urls.add('http://127.0.0.1:8000');      // Explicit loopback
    } else {
      // Default fallback for iOS or other platforms
      urls.add('http://localhost:8000');
    }
    
    return urls;
  }
  
  // Check URL safety with auto-server discovery
  Future<UrlSafetyResult> checkUrlSafety(String url) async {
    print('Checking URL safety: $url');
    
    // Use cached working URL if available
    String? serverUrl = await _discoverServer();
    
    if (serverUrl == null) {
      print('WARNING: Could not connect to any server, using fallback check');
      return _performLocalFallbackCheck(url);
    }
    
    print('Using server: $serverUrl');
    final apiUrl = '$serverUrl/api/v1/check-url';
    
    try {
      final payload = {'url': url};
      print('Request payload: $payload');
      
      print('Sending POST request to: $apiUrl');
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 10));
      
      print('Response status code: ${response.statusCode}');
      print('Response headers: ${response.headers}');
      print('Response body: ${response.body}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return UrlSafetyResult(
          url: url,
          isSafe: data['is_safe'] ?? false,
          confidence: data['confidence'] ?? 0.0,
          details: data['details'] ?? '',
          timestamp: DateTime.now(),
        );
      } else {
        print('API error: Status ${response.statusCode}');
        // Fallback to local check if server request fails
        return _performLocalFallbackCheck(url);
      }
    } catch (e) {
      print('API error: $e');
      // Fallback to local check if server request fails
      return _performLocalFallbackCheck(url);
    }
  }

  // Server discovery - tries all possible servers and returns the first one that works
  Future<String?> _discoverServer() async {
    // If we already have a cached working URL, try it first
    if (_cachedWorkingUrl != null) {
      print('Using cached working URL: $_cachedWorkingUrl');
      if (await _isServerReachable(_cachedWorkingUrl!)) {
        return _cachedWorkingUrl;
      } else {
        print('Cached URL no longer works, trying alternatives');
        _cachedWorkingUrl = null;
      }
    }
    
    print('Discovering server...');
    print('Trying ${serverUrls.length} possible server URLs');
    
    // Try all servers concurrently
    final futures = <Future<_ServerCheckResult>>[];
    for (final url in serverUrls) {
      futures.add(_checkServer(url));
    }
    
    // Wait for the first successful result or all failures
    try {
      final results = await Future.wait(futures);
      final workingServers = results.where((r) => r.isReachable).toList();
      
      if (workingServers.isNotEmpty) {
        // Sort by response time (fastest first)
        workingServers.sort((a, b) => a.responseTime.compareTo(b.responseTime));
        final fastest = workingServers.first;
        
        print('Found ${workingServers.length} working servers. Using fastest: ${fastest.url} (${fastest.responseTime}ms)');
        _cachedWorkingUrl = fastest.url;
        return fastest.url;
      }
    } catch (e) {
      print('Error during server discovery: $e');
    }
    
    print('No working servers found');
    return null;
  }
  
  // Check if a specific server is reachable
  Future<_ServerCheckResult> _checkServer(String serverUrl) async {
    final startTime = DateTime.now().millisecondsSinceEpoch;
    final isReachable = await _isServerReachable(serverUrl);
    final endTime = DateTime.now().millisecondsSinceEpoch;
    final responseTime = endTime - startTime;
    
    return _ServerCheckResult(
      url: serverUrl,
      isReachable: isReachable,
      responseTime: responseTime,
    );
  }
  
  // Check if server is reachable
  Future<bool> _isServerReachable(String serverUrl) async {
    try {
      print('Testing server: $serverUrl/api/ping');
      final response = await http.get(
        Uri.parse('$serverUrl/api/ping'),
        headers: {'Accept': 'application/json'},
      ).timeout(const Duration(seconds: 2));
      
      print('Server $serverUrl responded with status: ${response.statusCode}');
      return response.statusCode == 200;
    } catch (e) {
      print('Server $serverUrl is not reachable: $e');
      return false;
    }
  }

  UrlSafetyResult _performLocalFallbackCheck(String url) {
    print('Performing local fallback check for: $url');
    
    // Simple checks for potentially unsafe patterns
    final lowercaseUrl = url.toLowerCase();
    
    // Check for common phishing or malicious patterns
    final suspiciousPatterns = [
      'login', 'verify', 'account', 'secure', 'banking', 'paypal', 
      'ebay', 'amazon', 'microsoft', 'apple', 'netflix', 'facebook',
      'google', 'update', 'password', 'credential', 'prize', 'winner',
      'free', 'offer', 'limited', 'urgent', 'suspended', 'unusual',
      'activity', 'confirm', 'access', 'click', 'hack', 'crack',
      'warez', 'keygen', 'torrent', 'pirate', 'illegal', 'pharma',
      'pill', 'med', 'casino', 'gamble', 'bet', 'win'
    ];
    
    // Simple URL structure checks
    bool isSuspiciousStructure = false;
    try {
      final uri = Uri.parse(url);
      
      // Check for suspicious TLDs (top-level domains)
      final suspiciousTlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.info', '.online'];
      if (suspiciousTlds.any((tld) => uri.host.toLowerCase().endsWith(tld))) {
        isSuspiciousStructure = true;
      }
      
      // Check for IP address instead of domain name
      final ipPattern = RegExp(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$');
      if (ipPattern.hasMatch(uri.host)) {
        isSuspiciousStructure = true;
      }
      
      // Check for excessive subdomains
      if (uri.host.split('.').length > 3) {
        isSuspiciousStructure = true;
      }
      
      // Detect unusual port numbers
      if (uri.port != 0 && uri.port != 80 && uri.port != 443) {
        isSuspiciousStructure = true;
      }
      
      // Check for very long URLs
      if (url.length > 100) {
        isSuspiciousStructure = true;
      }
    } catch (e) {
      print('Error parsing URL in fallback check: $e');
      // If we can't parse the URL at all, consider it suspicious
      isSuspiciousStructure = true;
    }
    
    // Count matches of suspicious patterns
    int patternMatches = 0;
    for (final pattern in suspiciousPatterns) {
      if (lowercaseUrl.contains(pattern)) {
        patternMatches++;
      }
    }
    
    // Determine safety based on combined factors
    bool isSafe = true;
    double confidence = 0.5;  // Start with neutral confidence
    String details = "Fallback check result: ";
    
    if (isSuspiciousStructure) {
      confidence -= 0.2;
      details += "URL has suspicious structure. ";
    }
    
    if (patternMatches >= 3) {
      confidence -= 0.3;
      details += "URL contains multiple suspicious keywords. ";
    }
    
    if (confidence < 0.5) {
      isSafe = false;
      details += "Considered potentially unsafe.";
    } else {
      details += "No obvious threats detected, but this is a less accurate fallback check.";
    }
    
    print('Fallback safety result: $isSafe (confidence: $confidence)');
    print('Fallback details: $details');
    
    return UrlSafetyResult(
      url: url,
      isSafe: isSafe,
      confidence: confidence,
      details: details,
      timestamp: DateTime.now(),
    );
  }
}

// Helper class for server discovery
class _ServerCheckResult {
  final String url;
  final bool isReachable;
  final int responseTime;
  
  _ServerCheckResult({
    required this.url,
    required this.isReachable,
    required this.responseTime,
  });
} 