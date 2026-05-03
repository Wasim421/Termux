import google.generativeai as genai
import os
import sys
import collections
from PIL import Image
import warnings

# ১. সেটিংস ও ওয়ার্নিং বন্ধ রাখা
warnings.filterwarnings("ignore")

# ২. API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

# ৩. লাইব্রেরি কনফিগারেশন - সরাসরি v1 ভার্সন নিশ্চিত করা
genai.configure(api_key=api_key, transport='rest') # REST ব্যবহার করলে ভার্সন কন্ট্রোল সহজ হয়

def get_dominant_color(image_path):
    """ইমেজ থেকে থিম কালার এক্সট্রাকশন"""
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
    - RULES: Return ONLY raw Dart code. NO markdown formatting.
    """

    try:
        # এখানে সরাসরি v1 এন্ডপয়েন্ট কল করার জন্য GenerativeModel ডিফাইন করা
        # 'models/' প্রিফিক্স ছাড়া শুধু নাম ব্যবহার করলে v1 কল হওয়ার সম্ভাবনা বেশি থাকে
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # জেনারেশন কল
        response = model.generate_content(system_prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini")
            
        code = response.text.strip()
        
        # ব্যাকটিক ক্লিনআপ (যদি ভুল করে দিয়ে ফেলে)
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import " in part and "void main" in part:
                    code = part.replace("dart", "", 1).strip()
                    break
        return code.strip()
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        # যদি ৪.৪ এরর তবুও আসে, তবে gemini-1.0-pro ট্রাই করার অপশন রাখা যেতে পারে
        return f"import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('Error: {str(e)[:50]}')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Modern Reader UI"
    asset_file = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Starting AI Build Engine (Targeting v1 Stable)...")
    final_dart_code = generate_ai_app(user_prompt, os.path.basename(asset_file))
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_dart_code)
    print("✅ lib/main.dart updated successfully!")
