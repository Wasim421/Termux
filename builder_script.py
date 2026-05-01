import google.generativeai as genai
import os
import sys
import collections
from PIL import Image

# ১. Gemini API কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment variables!")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করে হেক্স কোড রিটার্ন করবে"""
    try:
        if not os.path.exists(image_path):
            return '#6200EE' # ফাইল না থাকলে ডিফল্ট পার্পল
            
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            r, g, b = color[:3]
            if 30 < (r+g+b)/3 < 220:
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        return '#{:02x}{:02x}{:02x}'.format(*most_common[0][0][:3])
    except Exception as e:
        print(f"⚠️ Color Detection Warning: {e}")
        return '#6200EE'

def generate_ai_app(prompt, asset_name):
    """জেমিনাই ব্যবহার করে ফ্লাটার কোড জেনারেট করবে"""
    asset_path = f"assets/{asset_name}"
    hex_color = get_dominant_color(asset_path)
    is_gif = asset_name.lower().endswith('.gif')
    
    # জেমিনাইকে দেওয়া চূড়ান্ত ইনস্ট্রাকশন
    system_prompt = f"""
    You are an expert Flutter Developer. Task: Create a high-quality main.dart file.
    
    Context:
    - Primary Color Detected from asset: {hex_color}
    - Background Asset: 'assets/{asset_name}'
    - Asset Type: {'Animated GIF' if is_gif else 'Static Image'}
    
    Requirements:
    1. Visuals: Use Material 3, Dark Mode, and Primary Color {hex_color}.
    2. Background: Implement 'assets/{asset_name}' as the main background. Use BoxFit.cover.
    3. Glassmorphism: Add BackdropFilter (blur sigma 10-15) over the background for a premium look.
    4. Customization: Incorporate this user request: "{prompt}".
    5. Clean Code: Return ONLY the code for 'main.dart'. No markdown (```), no comments, no extra text.
    """

    try:
        response = model.generate_content(system_prompt)
        # কোড ক্লিন করা
        code = response.text.replace('```dart', '').replace('```', '').strip()
        return code
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # GitHub Action থেকে আর্গুমেন্ট গ্রহণ
    if len(sys.argv) < 2:
        print("❌ Error: No prompt provided!")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    asset_file = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Starting AI Build with Gemini 1.5 Pro...")
    print(f"🎨 Detected Theme Color: {get_dominant_color(f'assets/{asset_file}')}")
    
    # কোড জেনারেট করা
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # lib ফোল্ডারে সেভ করা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_dart_code)
    
    print("✅ lib/main.dart has been updated successfully!")
