import google.generativeai as genai

# Yahan apni wahi Key dalein jo main.py mein hai
API_KEY = "AIzaSyBYdSP4G7xvg7fLDvNnfSi2J0yqBVme9YU"

genai.configure(api_key=API_KEY)

print("🔍 Checking available models for your Key...\n")

try:
    models = genai.list_models()
    found = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
            found = True
    
    if not found:
        print("❌ No models found! (Shayad API Key me issue hai)")

except Exception as e:
    print(f"❌ Error: {e}")