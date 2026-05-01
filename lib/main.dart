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
