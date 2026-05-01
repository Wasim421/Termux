import sys
import os
from PIL import Image
import collections

def get_dominant_color(image_path):
    img = Image.open(image_path)
    img = img.copy()
    img.thumbnail((100, 100)) # স্পিড বাড়ানোর জন্য ছোট করে নেয়া
    pixels = list(img.getdata())
    most_common = collections.Counter(pixels).most_common(1)
    r, g, b = most_common[0][0]
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

# এই হেক্স কোডটি এখন ডার্ট কোডের PrimaryColor এ বসবে:
# color: Color(int.parse("0xff{hex_code[1:]}"))
def check_sdk_compatibility(target_sdk):
    compatibility_map = {
        35: "3.24.0", # Android 15
        36: "3.27.0", # Android 16 (Hypothetical)
        37: "4.0.0"   # Android 17 (Hypothetical)
    }
    
    current_flutter = "3.24.0" # এটি অটোমেটিক রিড করা যাবে
    if target_sdk in compatibility_map:
        if current_flutter < compatibility_map[target_sdk]:
            print(f"ALERT: AI detect করেছে Android {target_sdk} এর জন্য আপনার Flutter আপডেট করা প্রয়োজন!")
            return False
    return True
    
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
  
