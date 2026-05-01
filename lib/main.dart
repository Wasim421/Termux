void _showAISuggestionDialog(BuildContext context, String fileName) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: Row(
        children: [
          Icon(Icons.auto_awesome, color: Colors.blue),
          SizedBox(width: 10),
          Text("AI Customizer ✨"),
        ],
      ),
      content: Text("আপনি '$fileName' দিয়ে কী তৈরি করতে চান?"),
      actions: [
        // ১. বাটন অপশন
        _buildDialogOption(context, "বাটন", Icons.smart_button, () {
           setAIPrompt("Convert $fileName into a stylish button with glass effect and ripple animation");
        }),
        
        // ২. ব্যাকগ্রাউন্ড অপশন
        _buildDialogOption(context, "ব্যাকগ্রাউন্ড", Icons.wallpaper, () {
           setAIPrompt("Set $fileName as the full-screen background with slight blur and dark overlay");
        }),
        
        // ৩. স্প্ল্যাশ স্ক্রিন (অ্যাপ ওপেনিং ইমেজ)
        _buildDialogOption(context, "স্প্ল্যাশ স্ক্রিন", Icons.flash_on, () {
           setAIPrompt("Create a splash screen using $fileName centered with a fade-in animation");
        }),

        // ৪. লোগো বা আইকন
        _buildDialogOption(context, "অ্যাপ লোগো", Icons.category, () {
           setAIPrompt("Place $fileName as the top-center logo with a nice shadow effect");
        }),
      ],
    ),
  );
}

// অপশনগুলোর জন্য একটি সুন্দর উইজেট বিল্ডার
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


// এটি একটি স্যাম্পল লজিক যা আপনার স্ক্রিনে পার্সেন্টেজ দেখাবে
void checkBuildStatus(String runId) async {
  var response = await http.get(
    Uri.parse('https://api.github.com/repos/YOUR_USER/YOUR_REPO/actions/runs/$runId'),
    headers: {'Authorization': 'token YOUR_PAT_TOKEN'},
  );
  
  if (response.statusCode == 200) {
    var data = jsonDecode(response.body);
    String status = data['status']; // queued, in_progress, completed
    
    if(status == 'queued') updateProgress(10);
    if(status == 'in_progress') updateProgress(50);
    if(status == 'completed') updateProgress(100);
  }
}
