# agent.py
# This is the brain of the agent.
# It handles: loading the API key, configuring Gemini, 
# sending the prompt + transcript, and parsing the response.

from google import genai  
# This imports the Gemini library we installed earlier.
# 'genai' is just a short alias — we'll type genai.something to use it.

from dotenv import load_dotenv  
# This imports the function that reads our .env file.

import os  
# os is a built-in Python library for interacting with the operating system.
# We use it here to read environment variables (like our API key).

import json  
# json is a built-in Python library for working with JSON.
# We'll use it to parse the AI's text response into a Python dictionary.

from prompts import SYSTEM_PROMPT  
# This imports the system prompt we wrote in prompts.py.
# Note: we're importing it as a variable, not a function.

# --- Setup ---

load_dotenv()  
# This reads the .env file and loads GEMINI_API_KEY into the environment.
# Must be called before os.getenv() or the key won't be found.

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
    # The f"" syntax is an f-string — it lets you embed variables 
    # inside a string using curly braces {like_this}.
    # {transcript} gets replaced with the actual transcript text.
    
    # Send the message to Gemini and wait for a response.
    # generate_content() is a blocking call — the code pauses here
    # until Gemini responds. For a demo this is fine.
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_message}"
    )
    
    # response.text is the raw text the AI returned.
    # We expect it to be a JSON string, but it might have 
    # extra characters we need to clean up.
    raw_text = response.text.strip()
    # .strip() removes any leading or trailing whitespace/newlines.
    
    # Safety net: sometimes AI models wrap JSON in markdown code blocks
    # like ```json { ... } ``` even when told not to.
    # This removes those wrappers if present.
    if raw_text.startswith("```"):
        # Split by newlines, remove the first and last lines (the ``` markers)
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])
    
    # json.loads() converts a JSON string into a Python dictionary.
    # If the AI returned valid JSON, this works perfectly.
    # If not, it raises an error — we'll handle that.
    try:
        result = json.loads(raw_text)
        return result
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a helpful error dictionary
        # instead of crashing completely.
        # This is called "graceful error handling."
        return {
            "error": "Failed to parse JSON response",
            "raw_response": raw_text,
            "detail": str(e)
        }


# --- Test Runner ---
# This block only runs when you execute this file directly.
# It does NOT run when another file imports agent.py.
# This is a Python convention: if __name__ == "__main__"

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
    # indent=2 means each level is indented by 2 spaces.
    # ensure_ascii=False preserves non-English characters.
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Also save the output to a file for reference.
    with open("sample_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print("Output saved to sample_output.json")