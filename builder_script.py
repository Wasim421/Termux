import os
import sys
import json
import requests
import collections
from PIL import Image

# ১. কনফিগারেশন
API_KEY = os.getenv("GEMINI_API_KEY")
# স্টেবল v1 এন্ডপয়েন্ট
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={API_KEY}"

def get_dominant_color(image_path):
    try:
        if not os.path.isfile(image_path): return '#1A1A1A'
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50))
        pixels = list(img.getdata())
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            r, g, b = color[:3]
            if 30 < (r+g+b)/3 < 220: return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except: return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    hex_color = get_dominant_color(f"assets/{asset_name}")
    
    # gemini-1.0-pro এর জন্য রিকোয়েস্ট ফরম্যাট
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Expert Flutter Developer. Write a single main.dart file. Dark Mode, Primary Color: {hex_color}, Background: assets/{asset_name} with Glassmorphism. Task: {prompt}. RULES: Output ONLY code, NO markdown, NO triple backticks."
            }]
        }]
    }

    try:
        response = requests.post(API_URL, json=payload, headers={'Content-Type': 'application/json'})
        result = response.json()
        
        if response.status_code != 200:
            # যদি ১.০ প্রো-তেও এরর দেয় তবে ভেরিয়েবল চেক করুন
            raise Exception(f"API Error {response.status_code}: {result.get('error', {}).get('message')}")

        # আউটপুট এক্সট্রাকশন
        code = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # ক্লিনআপ লজিক
        if "```" in code:
            code = code.split("```")[-2]
            if code.startswith("dart"): code = code[4:]
            
        return code.strip()
    except Exception as e:
        print(f"❌ Error Detail: {e}")
        # ফেইল-সেফ কোড
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Build Error: Model Not Found')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern E-book UI"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Starting Stable Build Engine (Gemini 1.0 Pro)...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Completed successfully!")
    
