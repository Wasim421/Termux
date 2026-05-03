import os
import sys
import requests
import collections
from PIL import Image

# ১. কনফিগারেশন
HF_TOKEN = os.getenv("HF_TOKEN")
# Llama 3.1 70B মডেল
MODEL_ID = "meta-llama/Meta-Llama-3.1-70B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def get_dominant_color(image_path):
    try:
        if not os.path.isfile(image_path): return '#1A1A1A'
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((50, 50))
        
        # Pillow 10+ নিরাপদ পদ্ধতি (getdata() এর বদলে)
        pixels = list(img.getdata()) 
        
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            r, g, b = color[:3]
            if 30 < (r+g+b)/3 < 220: return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except: return '#1A1A1A'

def generate_ai_app(prompt, asset_name):
    hex_color = get_dominant_color(f"assets/{asset_name}")
    
    system_instruction = f"Expert Flutter Developer. Write a single main.dart file. Dark Mode, Primary Color: {hex_color}, Background: assets/{asset_name} with Glassmorphism. Task: {prompt}."
    
    payload = {
        "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nOutput ONLY the raw Dart code. NO markdown, NO triple backticks, NO explanation.<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "parameters": {"max_new_tokens": 1200, "temperature": 0.2}
    }

    try:
        print(f"📡 Sending request to Hugging Face ({MODEL_ID})...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
        # ১. রেসপন্স স্ট্যাটাস চেক (Status 200 না হলে এরর দেখাবে)
        if response.status_code != 200:
            print(f"⚠️ API Status: {response.status_code}")
            print(f"📝 Response Body: {response.text}") # এটি আসল সমস্যা ধরিয়ে দেবে
            
            if response.status_code == 503:
                return "import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('Model is loading... Please wait 60s')))));"
            raise Exception(f"Server Error {response.status_code}")

        # ২. রেসপন্স খালি কি না চেক
        if not response.text.strip():
            raise Exception("Empty response from Hugging Face.")

        # ৩. সাকসেসফুলি JSON পার্স করা
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            full_text = result[0].get('generated_text', "")
            # Llama 3.1 নির্দিষ্ট আউটপুট স্প্লিট
            if "<|start_header_id|>assistant<|end_header_id|>" in full_text:
                code = full_text.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
            else:
                code = full_text.strip()
            
            # ব্যাকটিক ক্লিনআপ
            if "```" in code:
                code = code.split("```")[-2]
                if code.startswith("dart"): code = code[4:]
            return code.strip()
        else:
            raise Exception(f"Unexpected JSON format: {result}")

    except Exception as e:
        print(f"❌ Error Detail: {e}")
        return f"import 'package:flutter/material.dart'; void main() => runApp(MaterialApp(home: Scaffold(body: Center(child: Text('AI Build Error: {str(e)[:50]}')))));"

if __name__ == "__main__":
    # টার্মাক্স বা গিটহাব অ্যাকশন থেকে আসা আর্গুমেন্ট হ্যান্ডেল করা
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern E-book UI"
    asset_file = os.path.basename(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    print(f"🛠️ Starting AI Build Engine (Llama 3.1 70B)...")
    final_code = generate_ai_app(user_prompt, asset_file)
    
    # ফাইল সেভ করা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ Build Process Finished!")
    
