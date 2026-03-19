import google.generativeai as genai

API_KEY = "AIzaSyBKlF9w4bItCI8YMja_krsPHtpFpZvM8yQ"

genai.configure(api_key=API_KEY)

print("🔍 Checking available models...\n")

try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")