import os
import google.generativeai as genai
from scripts.ai_summary_free import translate_to_korean_summary_gemini

# Test if API key is set
api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key first 10 chars: {api_key[:10]}...")

# Test direct Gemini API
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello in Korean")
        print(f"\nDirect API test result: {response.text if response else 'No response'}")
    except Exception as e:
        print(f"\nDirect API test error: {e}")

# Test the summary function
print("\nTesting Korean summary function:")
test_title = "Singapore government announces new housing policy"
test_content = "The Singapore government today announced a new policy aimed at making housing more affordable for young families. The policy includes increased grants and subsidies."

result = translate_to_korean_summary_gemini(test_title, test_content)
print(f"Summary result: {result}")