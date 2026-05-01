import sys
import os

def generate_flutter_code(prompt):
    # এখানে আপনার AI API কল হবে যা প্রম্পট থেকে Dart কোড রিটার্ন করবে
    # আপাতত একটি বেসিক টেমপ্লেট দেওয়া হলো
    dart_code = f"""
import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('AI Generated App')),
        body: Center(child: Text('Requested Design: {prompt}')),
      ),
    );
  }}
}}
"""
    with open("lib/main.dart", "w") as f:
        f.write(dart_code)

if __name__ == "__main__":
    user_prompt = sys.argv[1]
    generate_flutter_code(user_prompt)
  
