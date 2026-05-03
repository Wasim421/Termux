import os
import sys
import collections
from PIL import Image
from huggingface_hub import InferenceClient

# ১. কনফিগারেশন (উন্নত মার্জড ভার্সন)
HF_TOKEN = os.getenv("HF_TOKEN")
# Zephyr 7B ফ্রি ইনফারেন্স এপিআই-তে অনেক বেশি স্ট্যাবল এবং 404 এরর দেয় না
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta" 

# ইনফারেন্স ক্লায়েন্ট সেটআপ
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def get_dominant_color(image_path):
    """ইমেজ থেকে কালার বের করার উন্নত ও ওয়ার্নিং-মুক্ত পদ্ধতি"""
    try:
        if not os.path.isfile(image_path): return '#1A1A1A'
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((50, 50))
        
        # Pillow 10+ এবং পরবর্তী ভার্সনের জন্য নিরাপদ (Deprecation Fix)
        pixels = img.getcolors(img.size[0] * img.size[1])
        if not pixels: return '#1A1A1A'
        
        # পিক্সেল কাউন্ট অনুযায়ী সর্ট করে ডমিন্যান্ট কালার বের করা
        most_common = sorted(pixels, key=lambda x: x[0], reverse=True)
        
        # অতিরিক্ত ব্রাইট বা ডার্ক কালার এড়ানোর চেষ্টা
        for count, color in most_common[:5]:
            r, g, b = color[:3]
            if 30 < (r+g+b)/3 < 220: 
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][1][:3])
    except Exception as e:
        print(f"⚠️ Color Extraction Error: {e}")
        return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    """Hub Client ব্যবহার করে উন্নত কোড জেনারেশন ও পার্সিং"""
    hex_color = get_dominant_color(f"assets/{asset_name}")
    
    # প্রম্পটটি আরও স্পেসিফিক করা হয়েছে
    prompt_text = (
        f"<|system|>\nExpert Flutter Developer. Write ONLY a single main.dart file. "
        f"Use Dark Mode, Primary Color: {hex_color}, and Glassmorphism with assets/{asset_name}.<|endoftext|>\n"
        f"<|user|>\nTask: {prompt}. Return ONLY raw code, no explanation, no backticks.<|endoftext|>\n"
        f"<|assistant|>\n"
    )

    try:
        print(f"📡 Requesting Hugging Face via Hub Client ({MODEL_ID})...")
        # টেক্সট জেনারেশন
        response = client.text_generation(
            prompt_text, 
            max_new_tokens=1500, 
            temperature=0.3,
            stop_sequences=["<|endoftext|>"]
        )
        
        code = response.strip()
        
        # ব্যাকটিক বা টেক্সট ক্লিনআপ (মার্জড লজিক)
        if "```" in code:
            parts = code.split("```")
            # কোড ব্লক খুঁজে বের করা
            for part in parts:
                if "import 'package:flutter" in part or "void main" in part:
                    code = part
                    break
            if code.startswith("dart"): code = code[4:]
        
        # যদি এআই কোডের শুরুতে বা শেষে ফালতু কথা লিখে দেয় তা বাদ দেওয়া
        if "import 'package:flutter" in code:
            code = code[code.find("import 'package:flutter"):]
            
        return code.strip()

    except Exception as e:
        print(f"❌ Error Detail: {e}")
        # সেফটি কোড (যদি এপিআই ফেইল করে)
        return (
            "import 'package:flutter/material.dart';\n\n"
            "void main() => runApp(MaterialApp(\n"
            "  home: Scaffold(body: Center(child: Text('AI Build Error: " + str(e)[:40] + "'))),\n"
            "));"
        )

if __name__ == "__main__":
    # টার্মাক্স/গিটহাব আর্গুমেন্ট হ্যান্ডেল
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern E-book UI Design"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    print(f"🛠️ Starting Merged AI Build Engine...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    # lib/main.dart ফাইলে কোড সেভ করা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    
    print("✅ Build Process Finished Successfully!")
    
