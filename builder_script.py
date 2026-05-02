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

# জেমিনাই ১.৫ ফ্ল্যাশ-লেটেস্ট মডেল ব্যবহার (সবচেয়ে দ্রুত এবং স্ট্যাবল)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_dominant_color(image_path):
    """ইমেজ থেকে ডমিন্যান্ট কালার বের করে হেক্স কোড রিটার্ন করবে"""
    try:
        # ফাইল না থাকলে বা পাথটি ডিরেক্টরি হলে ডিফল্ট পার্পল দিবে
        if not os.path.isfile(image_path):
            print(f"⚠️ Color Detection: {image_path} not found or is a directory. Using default.")
            return '#6200EE'
            
        img = Image.open(image_path).copy()
        img.thumbnail((50, 50)) 
        pixels = list(img.getdata())
        
        most_common = collections.Counter(pixels).most_common(10)
        for color, count in most_common:
            r, g, b = color[:3]
            # খুব বেশি উজ্জ্বল বা খুব বেশি কালচে রঙ এড়ানোর জন্য লজিক
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
    
    # প্রম্পট খালি থাকলে ডিফল্ট প্রিমিয়াম ডিজাইন ইনস্ট্রাকশন
    if not prompt or prompt.strip() == "":
        prompt = "Create a modern, clean Flutter UI with a glassmorphism effect and smooth animations."

    # দুটি ভার্সন থেকে মার্জ করা সেরা সিস্টেম প্রম্পট
    system_prompt = f"""
    You are an expert Flutter Developer. Task: Create a high-quality main.dart file.
    
    Context:
    - Primary Color Detected from asset: {hex_color}
    - Background Asset: 'assets/{asset_name}'
    - Asset Type: {'Animated GIF' if is_gif else 'Static Image'}
    
    Requirements:
    1. Visuals: Use Material 3, Dark Mode, and Primary Color {hex_color}.
    2. Background: Implement 'assets/{asset_name}' as the main background using BoxFit.cover.
    3. Glassmorphism: Add BackdropFilter (blur sigma 10-15) over the background for a premium look.
    4. Customization: Incorporate this user request: "{prompt}".
    5. Clean Code: Return ONLY the code for 'main.dart'. No markdown (```), no comments, no extra text.
    """

    try:
        response = model.generate_content(system_prompt)
        # কোড থেকে অপ্রয়োজনীয় অংশ ক্লিন করা
        code = response.text.replace('```dart', '').replace('```', '').strip()
        return code
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # GitHub Action থেকে আর্গুমেন্ট গ্রহণ: খালি থাকলে ডিফল্ট ভ্যালু
    user_prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else "Modern Glassmorphism UI"
    asset_file = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() != "" else "background.png"
    
    print(f"🛠️ Starting AI Build with Gemini 1.5 Flash...")
    
    # কোড জেনারেট করা
    final_dart_code = generate_ai_app(user_prompt, asset_file)
    
    # lib ফোল্ডারে সেভ করা
    os.makedirs("lib", exist_ok=True)
    with open("lib/main.dart", "w") as f:
        f.write(final_dart_code)
    
    print("✅ lib/main.dart has been updated successfully!")
    
