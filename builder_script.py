import os
import sys
import json
import requests
import collections
from PIL import Image

# ১. কনফিগারেশন
API_KEY = os.getenv("GEMINI_API_KEY")
# সরাসরি v1 (Stable) ইউআরএল ব্যবহার করছি
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

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
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Expert Flutter Dev: Write one main.dart file. Dark Mode, Primary: {hex_color}, BG: assets/{asset_name} (Glassmorphism). Task: {prompt}. RULES: Output ONLY code, NO markdown, NO ```."
            }]
        }]
    }

    try:
        # সরাসরি HTTP POST রিকোয়েস্ট
        response = requests.post(API_URL, json=payload, headers={'Content-Type': 'application/json'})
        result = response.json()
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {result.get('error', {}).get('message')}")

        code = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # ব্যাকটিক বা 'dart' লেখা থাকলে তা মুছে ফেলা
        if "```" in code:
            code = code.split("```")[-2]
            if code.startswith("dart"): code = code[4:]
            
        return code.strip()
    except Exception as e:
        print(f"❌ Error: {e}")
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Error')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern E-book UI"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Direct Build Engine Starting...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Completed!")
    
