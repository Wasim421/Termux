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

# সব ভার্সনে কাজ করার জন্য মডেল নাম 'gemini-1.5-flash' রাখা হয়েছে
model = genai.GenerativeModel('gemini-pro')

def get_dominant_color(image_path):
    """ছবি থেকে কালার বের করবে, না পেলে ডিফল্ট পার্পল দিবে"""
    try:
        if not os.path.isfile(image_path):
            return '#6200EE'
            
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            # RGB ভ্যালু আলাদা করা
            r, g, b = color[:3]
            # খুব বেশি হালকা বা খুব গাঢ় রঙ বাদ দেওয়ার ফিল্টার
            if 30 < (r+g+b)/3 < 220:
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except Exception:
        return '#6200EE'

def generate_ai_app(prompt, asset_name):
    """জেমিনাই দিয়ে ফ্লাটার কোড তৈরি"""
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    is_gif = asset_name.lower().endswith('.gif')
    
    if not prompt or prompt.strip() == "":
        prompt = "Create a modern Flutter UI with glassmorphism effect."

    # প্রিমিয়াম ডিজাইন প্রম্পট
    system_prompt = f"""
    You are an expert Flutter Developer. Task: Create a high-quality main.dart file.
    
    Context:
    - Primary Color: {hex_color}
    - Background Asset: 'assets/{asset_name}'
    - Asset Type: {'Animated GIF' if is_gif else 'Static Image'}
    
    Requirements:
    1. Use Material 3, Dark Mode, and Primary Color {hex_color}.
    2. Set 'assets/{asset_name}' as background (BoxFit.cover).
    3. Add BackdropFilter (blur sigma 10) for glassmorphism.
    4. Implement user request: "{prompt}".
    5. Return ONLY 'main.dart' code. No markdown (```), no comments.
    """

    try:
        response = model.generate_content(system_prompt)
        code = response.text
        
        # কোড থেকে বাড়তি টেক্সট বা ব্যাকটিক (```) পরিষ্কার করার শক্তিশালী লজিক
        if "```dart" in code:
            code = code.split("```dart")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
            
        return code.strip()
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        # জেমিনাই ফেইল করলে একটি সেফ কোড রিটার্ন করা
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Build Complete')))));"

if __name__ == "__main__":
    # আর্গুমেন্ট রিসিভ করা (খালি থাকলে ডিফল্ট ভ্যালু)
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern AI UI"
    
    # এসেট নেম চেক করা (শুধু 'assets/' আসলে সেটি বাদ দেওয়া)
    raw_asset = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    asset_file = "background.png" if raw_asset.strip() in ["", "assets/"] else raw_asset
    
    print(f"🛠️ Starting AI Build with Gemini...")
    
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_dart_code)
    
    print("✅ lib/main.dart updated successfully!")
    
