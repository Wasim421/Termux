import google.generativeai as genai
import os
import sys
import collections
from PIL import Image
import warnings

# অপ্রয়োজনীয় ওয়ার্নিং বন্ধ রাখা
warnings.filterwarnings("ignore")

# ১. API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

genai.configure(api_key=api_key)

# ২. মডেল সেটিংস (একদম ডিফল্ট পদ্ধতি)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_dominant_color(image_path):
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
    
    system_prompt = f"""
    You are an expert Flutter Developer. Create a single main.dart file.
    - Theme: Material 3, Dark Mode.
    - Primary Color: {hex_color}.
    - Background: 'assets/{asset_name}' with Glassmorphism (BackdropFilter).
    - Requirements: "{prompt}".
    - RULES: Return ONLY the code. No markdown backticks (```).
    """

    try:
        # কোনো বাড়তি RequestOptions ছাড়া সরাসরি কল
        response = model.generate_content(system_prompt)
        code = response.text.strip()
        
        # যদি তবুও ব্যাকটিক দিয়ে দেয় তবে তা ক্লিন করা
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import " in part and "void main" in part:
                    code = part.replace("dart", "", 1).strip()
                    break
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # ব্যাকআপ কোড যেন বিল্ড ফেইল না করে
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Build Error')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern Reader UI"
    asset_file = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Building with Gemini AI...")
    final_dart_code = generate_ai_app(user_prompt, os.path.basename(asset_file))
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
    print("✅ lib/main.dart updated!")
    
