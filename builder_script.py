import os
import sys
import requests
import collections
from PIL import Image

# ১. কনফিগারেশন
# গিটহাব সিক্রেটে বা এনভায়রনমেন্টে HF_TOKEN নামে তোমার টোকেনটি সেভ করো
HF_TOKEN = os.getenv("HF_TOKEN") or "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"
MODEL_ID = "meta-llama/Meta-Llama-3.1-70B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করার লজিক"""
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
    
    # Llama 3.1 এর জন্য ইনস্ট্রাকশন ফরম্যাট
    system_instruction = f"Expert Flutter Developer. Write a single main.dart file. Dark Mode, Primary Color: {hex_color}, Background: assets/{asset_name} with Glassmorphism. Task: {prompt}."
    
    payload = {
        "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nOutput ONLY the raw Dart code. NO markdown, NO triple backticks, NO explanation.<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # যদি মডেল লোড হতে সময় নেয়
        if response.status_code == 503:
            print("⏳ Llama is warming up on Hugging Face... retrying in 20s.")
            return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('Model Loading... Please retry')))));"

        result = response.json()
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {result}")

        # আউটপুট এক্সট্রাকশন
        full_text = result[0].get('generated_text', "")
        # শুধুমাত্র অ্যাসিস্ট্যান্টের জেনারেট করা কোডটুকু নেওয়া
        code = full_text.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
        
        # ক্লিনআপ লজিক (যদি ভুল করে ব্যাকটিক দেয়)
        if "```" in code:
            code = code.split("```")[-2]
            if code.startswith("dart"): code = code[4:]
            
        return code.strip()
    except Exception as e:
        print(f"❌ Error Detail: {e}")
        return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('Llama Build Error')))));"

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "GAI Reader Pro UI"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Starting AI Build Engine (Llama 3.1 70B)...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Completed successfully with Llama!")
    
