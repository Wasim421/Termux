import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class GithubService {
  final String repoUrl = 'https://api.github.com/repos/Wasim421/termux_app/dispatches';

  Future<void> sendBuildRequest({
    required String token, 
    required String prompt,
    required String packageName,
    required String assetName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(repoUrl),
        headers: {
          // 'token' বা 'Bearer' উভয়ই কাজ করে, তবে GitHub API-র জন্য 'Bearer' এখন রিকমেন্ডেড
          'Authorization': 'Bearer $token', 
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          "event_type": "build-event",
          "client_payload": {
            "prompt": prompt,
            "package_name": packageName,
            "asset_name": assetName,
            "target_sdk": "35"
          }
        }),
      );

      if (response.statusCode == 204) {
        debugPrint("✅ বিল্ড রিকোয়েস্ট সফলভাবে পাঠানো হয়েছে!");
      } else {
        debugPrint("❌ এরর: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      debugPrint("❌ নেটওয়ার্ক এরর: $e");
    }
  }

  // রান স্ট্যাটাস চেক করার উন্নত ফাংশন
  Future<void> checkBuildStatus(String token, String runId, Function(int) updateProgress) async {
    final statusUrl = 'https://api.github.com/repos/Wasim421/termux_app/actions/runs/$runId';
    
    try {
      final response = await http.get(
        Uri.parse(statusUrl),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        String status = data['status']; // queued, in_progress, completed
        String? conclusion = data['conclusion']; // success, failure, cancelled
        
        if (status == 'queued') {
          updateProgress(15);
        } else if (status == 'in_progress') {
          updateProgress(50);
        } else if (status == 'completed') {
          updateProgress(conclusion == 'success' ? 100 : -1); // -1 মানে ফেল
        }
      }
    } catch (e) {
      debugPrint("❌ স্ট্যাটাস চেক এরর: $e");
    }
  }
}

// --- UI Helper Function (Fixed & Improved) ---

void showAISuggestionDialog(BuildContext context, String fileName, Function(String) onPromptSelected) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      title: Row(
        children: const [
          Icon(Icons.auto_awesome, color: Colors.amber),
          SizedBox(width: 10),
          Text("AI Customizer ✨", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text("আপনি '$fileName' দিয়ে কী তৈরি করতে চান?", style: const TextStyle(fontSize: 14)),
          const SizedBox(height: 15),
          _buildDialogOption(context, "বাটন (Button)", Icons.smart_button, () {
             onPromptSelected("Convert $fileName into a stylish button with glass effect and ripple animation");
          }),
          _buildDialogOption(context, "ব্যাকগ্রাউন্ড (Background)", Icons.wallpaper, () {
             onPromptSelected("Set $fileName as the full-screen background with slight blur and dark overlay");
          }),
          _buildDialogOption(context, "স্প্ল্যাশ স্ক্রিন (Splash)", Icons.flash_on, () {
             onPromptSelected("Create a splash screen using $fileName centered with a fade-in animation");
          }),
          _buildDialogOption(context, "অ্যাপ লোগো (Logo)", Icons.category, () {
             onPromptSelected("Place $fileName as the top-center logo with a nice shadow effect");
          }),
        ],
      ),
    ),
  );
}

Widget _buildDialogOption(BuildContext context, String label, IconData icon, VoidCallback action) {
  return Card(
    elevation: 0,
    color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
    margin: const EdgeInsets.only(bottom: 8),
    child: ListTile(
      leading: Icon(icon, color: Colors.blueAccent),
      title: Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
      trailing: const Icon(Icons.chevron_right, size: 18),
      onTap: () {
        Navigator.pop(context); // আগে ডায়ালগ বন্ধ হবে
        action(); // তারপর অ্যাকশন ট্রিগার হবে
      },
    ),
  );
}
