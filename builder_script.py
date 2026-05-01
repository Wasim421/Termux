import sys
import os
def best_ai_coder(prompt, file_name):
    # AI logic ja best flutter code generate korbe
    is_gif = file_name.endswith('.gif')
    
    # Advanced AI-generated template
    code = f"""
import 'package:flutter/material.dart';
import 'dart:ui'; // Glassmorphism er jonno

void main() => runApp(MaterialApp(
  debugShowCheckedModeBanner: false,
  theme: ThemeData(useMaterial3: true, brightness: Brightness.dark),
  home: MyAIApp(),
));

class MyAIApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      body: Stack(
        children: [
          // Background (GIF thakle choloman, nahole image)
          Positioned.fill(
            child: {f"Image.asset('assets/{file_name}', fit: BoxFit.cover, repeat: ImageRepeat.repeat)" if is_gif else "Container(color: Colors.black)"},
          ),
          // Glassmorphism Overlay
          Center(
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
              child: Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white.withOpacity(0.2)),
                ),
                child: Text(
                  "{prompt}",
                  style: TextStyle(color: Colors.white, fontSize: 18),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }}
}}
"""
    return code
    
    def check_code_safety(dart_code):
    # কোডে কোনো ব্র্যাকেট মিসিং আছে কিনা বা ইমপোর্ট ভুল আছে কিনা তা চেক করবে
    if "MaterialApp" not in dart_code:
        print("Error: Invalid Flutter Structure!")
        return False
    return True
    

def generate_flutter_code(prompt, file_name):
    # GIF বা সাধারণ ইমেজের জন্য ডাইনামিক উইজেট লজিক
    if file_name.endswith('.gif'):
        # GIF এর জন্য চলমান কোড
        asset_widget = f"Image.asset('assets/{file_name}', repeat: ImageRepeat.repeat, fit: BoxFit.cover)"
    else:
        # সাধারণ ইমেজের জন্য কোড
        asset_widget = f"Image.asset('assets/{file_name}', fit: BoxFit.contain)"

    # এবার এই 'asset_widget' টি আপনার মূল ডার্ট কোডে ইনজেক্ট হবে
    dart_code = f"""
import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('AI GIF Builder')),
        body: Center(
          child: Container(
            child: {asset_widget}, // এখানে অটোমেটিক GIF বা ইমেজ বসে যাবে
          ),
        ),
      ),
    );
  }}
}}
"""
    with open(f"lib/main.dart", "w") as f:
        f.write(dart_code)

if __name__ == "__main__":
    user_prompt = sys.argv[1]
    app_file_name = sys.argv[2]
    generate_flutter_code(user_prompt, app_file_name)
    
def handle_customization(prompt, image_name):
    if "background" in prompt:
        return f"Stack(children: [Image.asset('assets/{image_name}', fit: BoxFit.cover, width: double.infinity, height: double.infinity), Container(color: Colors.black.withOpacity(0.4))])"
    
    elif "splash" in prompt:
        return f"Center(child: Image.asset('assets/{image_name}', width: 200).animate().fadeIn(duration: 500.ms))"
    
    elif "button" in prompt:
        return f"ElevatedButton(onPressed: (){{}}, child: Image.asset('assets/{image_name}', height: 30))"

    # অন্য সব ক্ষেত্রে ডিফল্ট ডিজাইন
    return f"Image.asset('assets/{image_name}')"
    
def generate_asset_widget(file_name, prompt):
    # GIF হলে এনিমেশন লজিক
    if file_name.endswith('.gif'):
        return f"""
        Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            image: DecorationImage(
              image: AssetImage('assets/{file_name}'),
              fit: BoxFit.cover,
            ),
          ),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5), // মনের মতো গ্লাস ইফেক্ট
            child: Container(color: Colors.black.withOpacity(0.1)),
          ),
        )"""

    # ইমেজ এবং স্মার্ট শেপ ক্রপার (Prompt অনুযায়ী)
    radius = "0"
    if "round" in prompt.lower(): radius = "50"
    elif "button" in prompt.lower(): radius = "15"

    return f"""
    ClipRRect(
      borderRadius: BorderRadius.circular({radius}),
      child: Image.asset('assets/{file_name}', fit: BoxFit.contain),
    )"""
    
from PIL import Image
import collections
def generate_ai_widget(image_name, prompt_type):
    if "button" in prompt_type.lower():
        return f"""
        GestureDetector(
          onTap: () => print('Button Tapped!'),
          child: Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle, // প্রম্পট অনুযায়ী শেপ বদলাবে
              image: DecorationImage(
                image: AssetImage('assets/{image_name}'),
                fit: BoxFit.cover,
              ),
            ),
            width: 100, height: 100,
          ),
        )"""
    elif "background" in prompt_type.lower():
        return f"Image.asset('assets/{image_name}', fit: BoxFit.cover)"
    # আরও কাস্টম উইজেট এখানে যোগ হবে


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
  
