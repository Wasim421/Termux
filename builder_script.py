import google.generativeai as genai
import os
import sys
import collections
from PIL import Image
import warnings

# অপ্রয়োজনীয় ওয়ার্নিং এবং ডিক্লারেশন বন্ধ রাখা
warnings.filterwarnings("ignore")

# ১. Gemini API কনফিগারেশন
# তোমার দেওয়া কি-টি গিটহাব সিক্রেটে (GEMINI_API_KEY) সেভ করে নিও
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in Environment!")
    sys.exit(1)

# সঠিক কনফিগারেশন
genai.configure(api_key=api_key)

# সঠিক মডেল নেম (models/ প্রিফিক্স ছাড়া ব্যবহার করাই বর্তমানে বেশি স্টেবল)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করার লজিক"""
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
    
    # ইনস্ট্রাকশন যা জেমিনাইকে ভুল করা থেকে আটকাবে
    system_prompt = f"""
    You are a Flutter Expert. Generate a single 'main.dart' file.
    - Style: Material 3, Dark Mode, Glassmorphism.
    - Primary Color: {hex_color}.
    - Background: Use 'assets/{asset_name}' with BoxFit.cover.
    - Specific Task: "{prompt}".
    
    CRITICAL RULES:
    1. Output ONLY the raw Dart code. 
    2. Do NOT use markdown code blocks or any triple backticks (```).
    3. Include 'dart:ui' import for BackdropFilter.
    """

    try:
        # জেমিনাই থেকে রেসপন্স নেওয়া
        response = model.generate_content(system_prompt)
        
        if not response.text:
            raise ValueError("Empty response from AI")
            
        code = response.text.strip()
        
        # অ্যাডভান্সড ক্লিনআপ (যদি জেমিনাই নিয়ম ভেঙে ব্যাকটিক দেয়)
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import" in part and "void main" in part:
                    code = part.replace("dart", "", 1).strip()
                    break
        
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # ফেইল-সেফ কোড
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
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else "GAI Reader Pro UI"
    raw_asset = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() else "background.png"
    
    asset_file = os.path.basename(raw_asset)
    
    print(f"🛠️ Starting AI Build Engine (Gemini 1.5 Flash)...")
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
        
    print("✅ lib/main.dart has been successfully updated!")
    
