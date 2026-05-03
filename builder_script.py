import os
import sys
import collections
from PIL import Image
from huggingface_hub import InferenceClient

# ১. কনফিগারেশন
HF_TOKEN = os.getenv("HF_TOKEN")
# এই মডেলটি conversational টাস্কে খুব ভালো কাজ করে
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta" 

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def get_dominant_color(image_path):
    try:
        if not os.path.isfile(image_path): return '#1A1A1A'
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((50, 50))
        # Pillow 10+ নিরাপদ পদ্ধতি
        pixels = img.getcolors(img.size[0] * img.size[1])
        if not pixels: return '#1A1A1A'
        most_common = sorted(pixels, key=lambda x: x[0], reverse=True)
        r, g, b = most_common[0][1][:3]
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    hex_color = get_dominant_color(f"assets/{asset_name}")
    
    # এরর এড়াতে conversational ফরম্যাটে মেসেজ তৈরি
    messages = [
        {"role": "system", "content": f"You are an expert Flutter developer. Write ONLY a single main.dart file. Dark Mode, Primary Color: {hex_color}, Background: assets/{asset_name}."},
        {"role": "user", "content": f"Task: {prompt}. Return ONLY the raw Dart code. No markdown, no triple backticks, no explanation."}
    ]

    try:
        print(f"📡 Requesting Hugging Face via Chat Completion...")
        # text_generation এর বদলে chat_completion ব্যবহার করা হয়েছে
        response = client.chat_completion(
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        
        code = response.choices[0].message.content.strip()
        
        # ব্যাকটিক বা টেক্সট ক্লিনআপ
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if "import 'package:flutter" in part:
                    code = part
                    break
            if code.startswith("dart"): code = code[4:]
        
        return code.strip()

    except Exception as e:
        print(f"❌ Error Detail: {e}")
        return f"import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Error: {str(e)[:50]}')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern E-book UI"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    print(f"🛠️ Starting Fixed AI Build Engine...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Process Finished!")
    
