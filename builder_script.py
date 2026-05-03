import google.generativeai as genai
import os
import sys
import collections
from PIL import Image

# ১. Gemini API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

genai.configure(api_key=api_key)

# মডেল নাম আপডেট করা হয়েছে যা বর্তমানে স্টেবল
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_dominant_color(image_path):
    try:
        if not os.path.isfile(image_path):
            return '#6200EE'
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
        return '#6200EE'

def generate_ai_app(prompt, asset_name):
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    is_gif = asset_name.lower().endswith('.gif')
    
    system_prompt = f"""
    You are an expert Flutter Developer. Create a single main.dart file.
    - Primary Color: {hex_color}, Background: 'assets/{asset_name}'.
    - Use Glassmorphism (BackdropFilter), Material 3, and Dark Theme.
    - Feature to implement: "{prompt}".
    - Return ONLY the dart code. No markdown, no triple backticks (```).
    """

    try:
        response = model.generate_content(system_prompt)
        code = response.text.strip()
        # জেমিনাই যদি ভুল করে ব্যাকটিক দেয় তবে তা মুছে ফেলা
        if code.startswith("```"):
            code = code.replace("```dart", "").replace("```", "")
        return code.strip()
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Build Error')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern UI"
    raw_asset = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    asset_file = "background.png" if "assets/" in raw_asset and len(raw_asset) < 8 else raw_asset
    
    print(f"🛠️ Starting AI Build...")
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_dart_code)
    print("✅ lib/main.dart updated!")
    
