import requests
from google import genai
from google.genai import types

# ১. আপনার API Key এখানে দিন
client = genai.Client(api_key="AIzaSyCzhwHb0Hm6DQVN384C89qPUmkt1VILtkY")

def verify_image_ai(image_url):
    try:
        # ২. ইমেজ ডাউনলোড করা
        response = requests.get(image_url)
        if response.status_code != 200:
            return "Error: Image link is invalid or unreachable."
        
        image_bytes = response.content

        # ৩. লেটেস্ট মডেল ব্যবহার (gemini-2.0-flash)
        # যদি 2.0 তেও সমস্যা হয় তবে 'gemini-1.5-flash' ব্যবহার করবেন
        response = client.models.generate_content(
            model="gemini-1.5-flash-8b", 
            contents=[
                "Analyze this image carefully. Is it AI-generated? "
                "Look for distorted textures, weird hands/fingers, or AI watermarks. "
                "Provide a clear 'Yes' or 'No' and a short explanation.",
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                )
            ]
        )
        
        return response.text

    except Exception as e:
        return f"An error occurred: {str(e)}"

# ৪. আপনার ImgBB ডিরেক্ট লিঙ্ক দিন
img_link = "https://i.ibb.co/k2XPCjbV/1000076588.jpg" 
print("\n--- AI Analysis Result ---")
print(verify_image_ai(img_link))