import google.generativeai as genai
import os
import sys
import collections
from PIL import Image
import warnings

# Depreciation ওয়ার্নিং বন্ধ রাখা যাতে লগ পরিষ্কার থাকে
warnings.filterwarnings("ignore", category=FutureWarning)

# API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

genai.configure(api_key=api_key)

# সঠিক মডেল নেম
model = genai.GenerativeModel('gemini-1.5-flash')


def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করার ফিচারটি অক্ষুণ্ণ রাখা হয়েছে"""
    try:
        if not os.path.isfile(image_path):
            return '#6200EE' # ডিফল্ট পার্পল
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            # আলফা চ্যানেল থাকলে তা বাদ দিয়ে RGB নেওয়া
            r, g, b = color[:3]
            # খুব অন্ধকার বা খুব উজ্জ্বল কালার এড়ানো
            if 30 < (r+g+b)/3 < 220:
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except Exception:
        return '#6200EE'

def generate_ai_app(prompt, asset_name):
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    
    # সিস্টেম প্রম্পট (আপনার ফিচারের মূল লজিক)
    system_prompt = f"""
    You are an expert Flutter Developer. Create a single self-contained main.dart file.
    - Application Theme: Dark Mode with Material 3.
    - Primary Color: {hex_color}.
    - Background Image: 'assets/{asset_name}' (Use BoxFit.cover).
    - Design Style: Glassmorphism (BackdropFilter) for all UI cards.
    - Requirements: "{prompt}".
    
    RULES:
    1. Return ONLY pure Dart code.
    2. Do NOT use markdown like ```dart or ```.
    3. Ensure all necessary imports like 'dart:ui' are included for Glassmorphism.
    4. Code must be error-free and ready to run.
    """

    try:
        # এপিআই কল
        response = model.generate_content(system_prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini")
            
        code = response.text.strip()
        
        # যদি জেমিনাই ভুল করে ব্যাকটিক (```) দিয়ে দেয়, তবে তা ফিল্টার করা
        if "```" in code:
            code = code.split("```")[-2] # কোড ব্লক অংশটি নেওয়া
            if code.startswith("dart"):
                code = code[4:].strip()
                
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # এরর হলে একটি ডিফল্ট ফেইল-সেফ কোড রিটার্ন করা যাতে অ্যাপ ক্রাশ না করে
        return f"""
import 'package:flutter/material.dart';
void main() => runApp(MaterialApp(
  home: Scaffold(
    backgroundColor: Colors.black,
    body: Center(
      child: Text('AI Build Error: Check API Logs\\n{str(e)[:50]}', 
      style: TextStyle(color: Colors.white), textAlign: TextAlign.center),
    ),
  ),
));
"""

if __name__ == "__main__":
    # কমান্ড লাইন আর্গুমেন্ট হ্যান্ডলিং (আপনার গিটহাব অ্যাকশন থেকে আসা)
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern E-book Reader UI"
    raw_asset = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    # অ্যাসেট ফাইল পাথ ক্লিনআপ
    asset_file = os.path.basename(raw_asset)
    
    print(f"🛠️ Starting AI Build Engine...")
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # লিভ ডিরেক্টরি নিশ্চিত করা এবং ফাইল লেখা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
        
    print("✅ lib/main.dart updated successfully with AI code!")
    
