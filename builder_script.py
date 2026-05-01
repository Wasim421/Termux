import google.generativeai as genai
import os
import sys
import collections
from PIL import Image

# ১. Gemini API কনফিগারেশন
# GitHub Secrets থেকে 'GEMINI_API_KEY' এটি রিড করবে
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
        img.thumbnail((50, 50)) # প্রসেসিং স্পিড বাড়াতে ছোট করা হয়েছে
        pixels = list(img.getdata())
        
        # পিক্সেল থেকে সবচেয়ে কমন রঙ খুঁজে বের করা
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            # শুধু RGB ডাটা নেওয়া (যদি RGBA থাকে তবে আলফা বাদ যাবে)
            r, g, b = color[:3]
            # খুব কালো বা খুব সাদা রঙ এড়িয়ে চলা
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
    5. Clean Code: Return ONLY the code for 'main.dart'. No markdown, no comments, no extra text.
    """

    try:
        response = model.generate_content(system_prompt)
        # জেমিনাই অনেক সময় কোড ব্লক (```dart) সহ দেয়, সেগুলো ক্লিন করা
        code = response.text.replace('```dart', '').replace('```', '').strip()
        return code
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # GitHub Action থেকে আর্গুমেন্ট রিসিভ করা
    if len(sys.argv) < 2:
        print("❌ Error: No prompt provided!")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    # যদি ইমেজ নাম না পাঠানো হয় তবে ডিফল্ট background.png ধরে নেবে
    asset_file = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    print(f"🛠️ Starting AI Build...")
    print(f"🎨 Detected Theme Color: {get_dominant_color(f'assets/{asset_file}')}")
    
    # কোড জেনারেট করা
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # lib ফোল্ডার না থাকলে তৈরি করা এবং main.dart এ সেভ করা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_dart_code)
    
    print("✅ lib/main.dart has been updated successfully!")
    5. Clean Code: Give ONLY the Dart code. No explanations.
    """

    response = model.generate_content(system_instruction)
    dart_code = response.text.replace('```dart', '').replace('```', '').strip()
    return dart_code

if __name__ == "__main__":
    # GitHub Action থেকে আর্গুমেন্ট গ্রহণ
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Beautiful UI"
    asset_file = sys.argv[2] if len(sys.argv) > 2 else "background.png"
    
    print(f"🚀 AI is building with Color: {get_dominant_color(f'assets/{asset_file}')}")
    
    final_code = generate_ai_app(user_prompt, asset_file)
    
    # কোডটি lib/main.dart এ লিখে ফেলা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_code)
    
    print("✅ Gemini 1.5 Pro has generated your advanced Flutter app!")
    
