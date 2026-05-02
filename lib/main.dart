import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class GithubService {
  // আপনার রিপোজিটরি পাথ ঠিক আছে
  final String repoUrl = 'https://api.github.com/repos/Wasim421/Termux/dispatches';

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
          'Authorization': 'Bearer $token', // 'token $token' এর বদলে 'Bearer $token' বেশি স্ট্যান্ডার্ড
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

      // GitHub Dispatch সফল হলে ২০৪ স্ট্যাটাস কোড দেয়
      if (response.statusCode == 204) {
        print("✅ বিল্ড রিকোয়েস্ট সফলভাবে পাঠানো হয়েছে!");
      } else {
        print("❌ এরর: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      print("❌ নেটওয়ার্ক এরর: $e");
    }
  }

  // রান স্ট্যাটাস চেক করার ফাংশন
  Future<void> checkBuildStatus(String token, String runId, Function(int) updateProgress) async {
    final statusUrl = 'https://api.github.com/repos/Wasim421/Termux/actions/runs/$runId';
    
    try {
      var response = await http.get(
        Uri.parse(statusUrl),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);
        String status = data['status'];
        String conclusion = data['conclusion'] ?? "";
        
        if (status == 'queued') {
          updateProgress(10);
        } else if (status == 'in_progress') {
          updateProgress(50);
        } else if (status == 'completed') {
          if (conclusion == 'success') {
            updateProgress(100);
          } else {
            print("❌ বিল্ড ফেল করেছে।");
          }
        }
      }
    } catch (e) {
      print("❌ স্ট্যাটাস চেক এরর: $e");
    }
  }
}

// --- UI Helper Function ---

void showAISuggestionDialog(BuildContext context, String fileName, Function(String) onPromptSelected) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      title: Row(
        children: const [
          Icon(Icons.auto_awesome, color: Colors.blue),
          SizedBox(width: 10),
          Text("AI Customizer ✨"),
        ],
      ),
      content: Text("আপনি '$fileName' দিয়ে কী তৈরি করতে চান?"),
      actions: [
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
  );
}

Widget _buildDialogOption(BuildContext context, String label, IconData icon, VoidCallback action) {
  return ListTile(
    leading: Icon(icon, color: Colors.blueAccent),
    title: Text(label),
    onTap: () {
      action();
      Navigator.pop(context); // ডায়ালগ বন্ধ করা
    },
  );
}
