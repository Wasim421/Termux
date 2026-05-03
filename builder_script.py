import os
import sys
import collections
from PIL import Image
from huggingface_hub import InferenceClient

# ১. কনফিগারেশন আপডেট
HF_TOKEN = os.getenv("HF_TOKEN")

# কোডিংয়ের জন্য এই মডেলটি বর্তমানে হাগিং ফেসের সবচেয়ে শক্তিশালী এবং স্ট্যাবল এপিআই মডেল
MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct" 

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def get_dominant_color(image_path):
    try:
        if not os.path.isfile(image_path): return '#1A1A1A'
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((50, 50))
        pixels = img.getcolors(img.size[0] * img.size[1])
        if not pixels: return '#1A1A1A'
        most_common = sorted(pixels, key=lambda x: x[0], reverse=True)
        r, g, b = most_common[0][1][:3]
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    hex_color = get_dominant_color(f"assets/{asset_name}")
    
    # ইনস্ট্রাকশন
    messages = [
        {"role": "system", "content": f"You are an expert Flutter developer. Write ONLY a single main.dart file. Dark Mode, Primary Color: {hex_color}, Background: assets/{asset_name}."},
        {"role": "user", "content": f"Task: {prompt}. Return ONLY the raw Dart code. No explanation."}
    ]

    try:
        print(f"📡 Requesting Hugging Face via Qwen-Coder API...")
        # chat_completion মেথডটিই সবচেয়ে স্ট্যাবল
        response = client.chat_completion(
            messages=messages,
            max_tokens=1800,
            temperature=0.2
        )
        
        code = response.choices[0].message.content.strip()
        
        # পিওর কোড এক্সট্রাক্ট করা (ব্যাকটিক ক্লিনআপ)
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import 'package:flutter" in part:
                    code = part
                    break
            if code.startswith("dart"): code = code[4:]
        
        # অতিরিক্ত সেফটি ক্লিনআপ
        if "import 'package:flutter" in code:
            code = code[code.find("import 'package:flutter"):]
            
        return code.strip()

    except Exception as e:
        print(f"❌ Error Detail: {e}")
        # যদি এই মডেলটিও এরর দেয়, তবে একটি মিনিমাল অ্যাপ রিটার্ন করবে যাতে বিল্ড ফেইল না হয়
        return (
            "import 'package:flutter/material.dart';\n\n"
            "void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Engine Error: Check API Connection')))));"
        )

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern UI Design"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    print(f"🛠️ Starting Build Engine with Qwen-Coder...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Process Finished!")
    
