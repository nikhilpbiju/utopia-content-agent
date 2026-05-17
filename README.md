# Utopia Studio · Content Agent

Transforms a Granola meeting transcript into a LinkedIn post, 
follow-up email, and press angle — in structured JSON a downstream 
agent can consume directly.

Built for the Utopia Studio Agentic Operator Internship assignment.
Track: Marketing & Events · M7 Go-to-Market.

---

## What it does

The studio's marketing team receives a Granola transcript after every 
meeting. Before this agent, they read the full transcript manually and 
wrote three content assets from scratch — taking 45–60 minutes per meeting.

This agent does that in under 30 seconds:

- Extracts the key attendee, topic, and most interesting moment
- Generates a LinkedIn post in Utopia Studio's voice, mapped to the LAUNCH framework
- Generates a personalised follow-up email referencing a specific moment from the call
- Generates a one-sentence press angle written as a journalist would pitch it
- Returns everything as structured JSON for downstream agent consumption
- Posts the LinkedIn draft to a Slack channel via webhook
- Runs automatically every morning at 09:00 Doha time (UTC+3)

---

## How to run it

**Requirements:** Python 3.9+, a Gemini API key

**1. Clone the repo and enter the folder**

git clone https://github.com/YOUR_USERNAME/utopia-content-agent.git
cd utopia-content-agent

**2. Create and activate a virtual environment**

python -m venv venv

# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

**3. Install dependencies**

pip install -r requirements.txt

**4. Set up your environment variables**

Create a file called .env in the project root:

GEMINI_API_KEY=your_gemini_api_key_here

**5. Run the Streamlit app**

streamlit run app.py

The app opens in your browser at http://localhost:8501.
Paste a transcript or upload a .txt file, click Generate Content.

**6. (Optional) Send output to Slack**

Paste a Slack Incoming Webhook URL into the Slack field in the UI.
Create one at: your-workspace.slack.com → Settings → Integrations → Incoming Webhooks

**7. (Optional) Run the daily scheduler**

python scheduler.py

Runs the agent automatically every day at 09:00 Doha time (UTC+3).
Keep the terminal window open. Uses sample_input.txt as the default transcript.

---

## File structure

utopia-content-agent/

├── agent.py            # Core logic: Gemini API call, JSON parsing

├── app.py              # Streamlit UI: input, output display, Slack send

├── prompts.py          # System prompt: studio voice, LAUNCH framework, output format

├── slack_sender.py     # Slack webhook integration

├── scheduler.py        # Daily automated run at 09:00 Doha time

├── sample_input.txt    # The exact transcript used in the Loom demo

├── sample_output.json  # The exact output produced in the Loom demo

├── requirements.txt    # Python dependencies

└── README.md           # This file

---

## The prompt

The system prompt lives in prompts.py. It encodes:

- Utopia Studio's voice rules (declarative, specific, no hedging)
- Negative examples of what NOT to write (no "Excited to share...", 
  no "operational efficiencies")
- The LAUNCH framework (Lead, Amplify, Unify, Nurture, Convert, Harvest)
  with definitions — the LinkedIn post is classified against this
- Exact output format: a JSON schema the model must follow
- Hard constraints: word counts, no hashtags, no emoji, 
  specific rules for opening and closing lines

The prompt is kept in a separate file because it is the product — 
it should be readable, editable, and improvable independently of the code.

---

## APIs and tools used

- **Gemini API** (google-generativeai) — content generation
- **Streamlit** — UI layer for the demo
- **Slack Incoming Webhooks** — posts LinkedIn draft to a studio channel
- **schedule** (Python library) — daily automated run
- **python-dotenv** — environment variable management

---

## Sample input

See sample_input.txt — a realistic Granola-style transcript from a 
venture discovery call between Utopia Studio's Fellowships Lead and 
Ahmed Al-Mansoori, founder of LogiQ.

---

## Sample output

See sample_output.json — the exact JSON the agent produced on the 
sample input. Pasted verbatim in the writeup.

---

## Design decisions

**Single API call, not three:** One structured prompt returning all 
three outputs is faster, cheaper, and simpler than three sequential 
calls. Output quality is equivalent.

**JSON wrapping human-readable content:** Each output is a key in a 
JSON object. A human reads the values. Another agent reads the keys. 
Both use cases are served without extra work.

**No LinkedIn auto-posting:** LinkedIn's API for auto-posting requires 
OAuth2 and partner approval — days of setup for marginal gain. The 
agent produces the post; a human publishes it. That is the correct 
human-in-the-loop boundary for content that represents the studio publicly.

**Gemini over Claude API:** Generous free tier for development. 
The architecture is API-agnostic — swapping to Claude requires 
changing one function in agent.py.

---

## What I would build next

1. Granola API integration — fetch the latest transcript automatically 
   instead of requiring a paste
2. Gmail draft creation — auto-draft the follow-up email in the 
   sender's Gmail via SMTP
3. Google Sheets logging — append every run to a Sheet so the team 
   has a searchable content archive
4. Second-agent handoff — a downstream Slack bot that presents the 
   three outputs with Approve / Edit buttons, then routes approved 
   content to the right destination
