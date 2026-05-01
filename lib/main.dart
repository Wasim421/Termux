import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class GithubService {
  // ১. আপনার গিটহাব কনফিগ
  final String repoUrl = 'https://api.github.com/repos/Wasim421/Termux/dispatches';
  final String token = "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"; 

  // ২. বিল্ড রিকোয়েস্ট পাঠানোর মেইন ফাংশন
  Future<void> sendBuildRequest({
    required String prompt,
    required String packageName,
    required String assetName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(repoUrl),
        headers: {
          'Authorization': 'token $token',
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          "event_type": "build-event",
          "client_payload": {
            "prompt": prompt,
            "package_name": packageName,
            "asset_name": assetName, // পাইথন স্ক্রিপ্টের জন্য এটি জরুরি
            "target_sdk": "35"
          }
        }),
      );

      if (response.statusCode == 204) {
        print("✅ বিল্ড শুরু হয়েছে!");
      } else {
        print("❌ এরর: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      print("❌ নেটওয়ার্ক এরর: $e");
    }
  }

  // ৩. বিল্ড স্ট্যাটাস চেক করার ফাংশন (Progress Bar এর জন্য)
  Future<void> checkBuildStatus(String runId, Function(int) updateProgress) async {
    final statusUrl = 'https://api.github.com/repos/Wasim421/Termux/actions/runs/$runId';
    
    var response = await http.get(
      Uri.parse(statusUrl),
      headers: {'Authorization': 'token $token'},
    );
    
    if (response.statusCode == 200) {
      var data = jsonDecode(response.body);
      String status = data['status']; // queued, in_progress, completed
      
      if(status == 'queued') updateProgress(10);
      else if(status == 'in_progress') updateProgress(50);
      else if(status == 'completed') updateProgress(100);
    }
  }
}

// ৪. AI কাস্টমাইজার ডায়ালগ উইজেট
void showAISuggestionDialog(BuildContext context, String fileName, Function(String) onPromptSelected) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      title: Row(
        children: [
          Icon(Icons.auto_awesome, color: Colors.blue),
          SizedBox(width: 10),
          Text("AI Customizer ✨"),
        ],
      ),
      content: Text("আপনি '$fileName' দিয়ে কী তৈরি করতে চান?"),
      actions: [
        _buildDialogOption(context, "বাটন", Icons.smart_button, () {
           onPromptSelected("Convert $fileName into a stylish button with glass effect and ripple animation");
        }),
        _buildDialogOption(context, "ব্যাকগ্রাউন্ড", Icons.wallpaper, () {
           onPromptSelected("Set $fileName as the full-screen background with slight blur and dark overlay");
        }),
        _buildDialogOption(context, "স্প্ল্যাশ স্ক্রিন", Icons.flash_on, () {
           onPromptSelected("Create a splash screen using $fileName centered with a fade-in animation");
        }),
        _buildDialogOption(context, "অ্যাপ লোগো", Icons.category, () {
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
      Navigator.pop(context);
    },
  );
}
