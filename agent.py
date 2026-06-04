# agent.py
# It handles: loading the API key, configuring Gemini, 
# sending the prompt + transcript, and parsing the response.

from google import genai  
from dotenv import load_dotenv  
import os  
import json  
from prompts import SYSTEM_PROMPT  

# --- Setup ---

load_dotenv()  

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  
# This creates the Gemini client using the API key.

# --- The Core Function ---

def run_agent(transcript: str) -> dict:
    """
    Takes a raw meeting transcript as a string.
    Returns a Python dictionary with the structured content output.
    
    A 'dict' (dictionary) in Python is the same concept as JSON —
    key-value pairs. {"name": "Ahmed", "role": "Founder"}
    """
    
    # This is the user message — the actual transcript.
    # We label it clearly so the AI understands what it's receiving.
    user_message = f"""
Here is the meeting transcript. Produce the three content assets 
as specified in your instructions.

TRANSCRIPT:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_message}"
    )
    
    
    raw_text = response.text.strip()
    
    if raw_text.startswith("```"):
        #
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])
    
   
    try:
        result = json.loads(raw_text)
        return result
    except json.JSONDecodeError as e:
        
        return {
            "error": "Failed to parse JSON response",
            "raw_response": raw_text,
            "detail": str(e)
        }


# --- Test Runner ---
# This block only runs when you execute this file directly.

if __name__ == "__main__":
    
    # Read the sample transcript from the file we created.
    # "r" means read mode. 
    # encoding="utf-8" handles special characters safely.
    with open("sample_input.txt", "r", encoding="utf-8") as f:
        transcript = f.read()
    
    print("Running agent on sample transcript...")
    print("-" * 50)
    
    # Call the agent function with the transcript.
    result = run_agent(transcript)
    
    # json.dumps() converts a Python dictionary back to a 
    # nicely formatted JSON string.
    # ensure_ascii=False preserves non-English characters.
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Also save the output to a file for reference.
    with open("sample_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print("Output saved to sample_output.json")
