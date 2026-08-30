import os
from google import genai

# Best practice: Set your key as an environment variable in your terminal first
# Mac/Linux: export GEMINI_API_KEY="your_api_key_here"
# Windows: set GEMINI_API_KEY="your_api_key_here"
# Or for a quick test, you can paste it directly below:

API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Jgk7wo4DYOZ-Vd9BAg_47pVvFVrGEkYoRgMNaG2IpLzQ")

# Initialize the client
client = genai.Client(api_key=API_KEY)

# Make a test request to Gemini 1.5 Flash
response = client.models.generate_content(
    model='gemini-3.7-flash',
    contents='Respond with a quick confirmation that my API key is working!'
)

print(response.text)

