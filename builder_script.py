import google.generativeai as genai
import os
import sys
import collections
from PIL import Image
import warnings

# অপ্রয়োজনীয় ওয়ার্নিং বন্ধ রাখা যাতে লগ পরিষ্কার থাকে
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore")

# ১. Gemini API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in Environment Variables!")
    sys.exit(1)

genai.configure(api_key=api_key)

# মডেল হিসেবে লেটেস্ট স্টেবল 'gemini-1.5-flash' ব্যবহার করা হয়েছে
model = genai.GenerativeModel('gemini-1.5-flash')

def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করার সবচেয়ে আধুনিক লজিক"""
    try:
        if not os.path.isfile(image_path):
            return '#1A1A1A' # ডিফল্ট ডার্ক গ্রে
        
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        
        # পিক্সেল কাউন্টিং
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            # RGB ভ্যালু চেক (আলফা থাকলে বাদ দিয়ে)
            r, g, b = color[:3]
            # খুব অন্ধকার বা খুব উজ্জ্বল কালার এড়িয়ে মাঝারি ভাইব্রেন্ট কালার নেওয়া
            if 30 < (r+g+b)/3 < 220:
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except Exception:
        return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    """AI এর মাধ্যমে কোড জেনারেশন এবং ক্লিনআপ লজিক"""
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    
    # ইনস্ট্রাকশন প্রম্পট (আপনার সব ফিচারসহ)
    system_prompt = f"""
    Act as a Senior Flutter Developer. Create a single self-contained main.dart file.
    - Application Theme: Dark Mode with Material 3.
    - Primary Color: {hex_color}.
    - Background: Use 'assets/{asset_name}' (BoxFit.cover) with glassmorphism (BackdropFilter).
    - Features to Implement: "{prompt}".
    
    RULES:
    1. Output ONLY pure Dart code. 
    2. NEVER include explanations, markdown code blocks (```) or triple backticks.
    3. Include all necessary imports like 'dart:ui' for BackdropFilter.
    4. Ensure the code is production-ready and error-free.
    """

    try:
        # জেমিনাই এপিআই কল
        response = model.generate_content(system_prompt)
        
        if not response.text:
            raise ValueError("Gemini returned an empty response.")
            
        code = response.text.strip()
        
        # অ্যাডভান্সড কোড ক্লিনআপ (যদি জেমিনাই ভুল করে ব্যাকটিক দিয়ে দেয়)
        if "```" in code:
            # কোড ব্লকের ভেতর থেকে শুধু ডার্ট কোডটুকু বের করা
            parts = code.split("```")
            for part in parts:
                if "import " in part and "void main" in part:
                    code = part.replace("dart", "", 1).strip()
                    break
                    
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # ফেইল-সেফ এরর স্ক্রিন কোড (যাতে অ্যাপ ক্রাশ না করে)
        return f"""
import 'package:flutter/material.dart';
import 'dart:ui';

void main() => runApp(MaterialApp(
  theme: ThemeData.dark(useMaterial3: true),
  home: Scaffold(
    backgroundColor: Colors.black,
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Text('AI BUILD ERROR:\\n{str(e)[:100]}', 
        style: TextStyle(color: Colors.redAccent, fontSize: 16), textAlign: TextAlign.center),
      ),
    ),
  ),
));
"""

if __name__ == "__main__":
    # কমান্ড লাইন থেকে ডাটা নেওয়া
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern E-book Reader UI"
    raw_asset = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    # অ্যাসেট ফাইলের নাম ক্লিন করা
    asset_file = os.path.basename(raw_asset)
    
    print(f"🛠️ Building GAI Reader Pro Engine with Gemini...")
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # lib/main.dart ফাইলে কোড রাইটিং
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
        
    print("✅ lib/main.dart updated successfully!")
    
