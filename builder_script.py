import google.generativeai as genai
from google.generativeai.types import RequestOptions
import os
import sys
import collections
from PIL import Image
import warnings

# ১. সেটিংস ও ওয়ার্নিং ফিল্টার
warnings.filterwarnings("ignore")

# ২. API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

genai.configure(api_key=api_key)

# ৩. মডেল সেটিংস (এখানেই আসল ফিক্স)
# 'models/gemini-1.5-flash' এর বদলে শুধু নাম ব্যবহার এবং লেটেস্ট অপশন দেওয়া
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
)

def get_dominant_color(image_path):
    """ইমেজ থেকে থিম কালার বের করার লজিক"""
    try:
        if not os.path.isfile(image_path):
            return '#1A1A1A'
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            r, g, b = color[:3]
            if 30 < (r+g+b)/3 < 220:
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except Exception:
        return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    
    # ইনস্ট্রাকশন যা AI-কে ভুল করা থেকে বাঁচাবে
    system_prompt = f"""
    Act as a Senior Flutter Engineer. Create a single self-contained 'main.dart' file.
    - Style: Material 3, Dark Theme, Glassmorphism UI.
    - Primary Color: {hex_color}.
    - Background Asset: 'assets/{asset_name}' (BoxFit.cover).
    - Task: "{prompt}".
    
    CRITICAL RULES:
    1. Output ONLY pure Dart code. 
    2. NO markdown, NO triple backticks (```).
    3. Must include 'dart:ui' for BackdropFilter.
    """

    try:
        # জেনারেশন কল - এখানে RequestOptions দিয়ে v1 ভার্সন নিশ্চিত করা হয়েছে
        response = model.generate_content(
            system_prompt,
            request_options=RequestOptions(api_version='v1')
        )
        
        if not response.text:
            raise ValueError("Empty response from Gemini")
            
        code = response.text.strip()
        
        # ব্যাকটিক ক্লিনআপ লজিক
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import" in part and "void main" in part:
                    code = part.replace("dart", "", 1).strip()
                    break
        
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # ফেইল-সেফ কোড (যদি API ফেইল করে)
        return f"""
import 'package:flutter/material.dart';
void main() => runApp(MaterialApp(
  home: Scaffold(
    backgroundColor: Colors.black,
    body: Center(child: Text('AI Build Error:\\n{str(e)[:100]}', 
    style: TextStyle(color: Colors.white), textAlign: TextAlign.center)),
  ),
));
"""

if __name__ == "__main__":
    # আর্গুমেন্ট হ্যান্ডলিং
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else "GAI Reader Pro"
    raw_asset = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() else "background.png"
    
    asset_file = os.path.basename(raw_asset)
    
    print(f"🛠️ Starting AI Build Engine (Gemini 1.5 Flash)...")
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # ফাইল রাইটিং
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
        
    print("✅ lib/main.dart updated successfully!")
    
