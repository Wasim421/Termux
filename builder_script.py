import google.generativeai as genai
import os
import sys
import collections
from PIL import Image

# ১. API ও মডেল সেটআপ
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path).copy()
        img.thumbnail((100, 100))
        pixels = list(img.getdata())
        most_common = collections.Counter(pixels).most_common(1)
        r, g, b = most_common[0][0][:3]
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except:
        return '#6200EE' # ডিফল্ট পার্পল কালার

def generate_ai_app(prompt, asset_name):
    # কালার এবং ফাইল টাইপ ডিটেকশন
    hex_color = get_dominant_color(f"assets/{asset_name}")
    is_gif = asset_name.lower().endswith('.gif')
    
    # Gemini-র জন্য বিশেষ ইনস্ট্রাকশন (আপনার সব ফিচারসহ)
    system_instruction = f"""
    You are an expert Flutter Developer. Create a professional main.dart code.
    Requirements:
    1. Theme: Material 3, Dark Mode, Primary Color: {hex_color}.
    2. Background: Use 'assets/{asset_name}' as a background. {'It is a GIF, so play it in a loop.' if is_gif else 'It is a static image.'}
    3. UI Style: Use Glassmorphism (BackdropFilter blur), Rounded corners (borderRadius: 20), and smooth animations.
    4. Features: Include the user request: "{prompt}".
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
    
