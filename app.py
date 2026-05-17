# app.py
# This is the UI layer — it wraps agent.py in a visual interface.
# Run it with: streamlit run app.py
# Streamlit will open a browser tab automatically.

import streamlit as st
import json
import os
from datetime import datetime
from agent import run_agent

# --- Page Configuration ---
# This must be the FIRST Streamlit command in the file.
st.set_page_config(
    page_title="Utopia Studio · Content Agent",
    page_icon="✦",
    layout="wide"
)

# --- Session State Initialization ---
# Session state persists across Streamlit reruns.
# Without this, every widget interaction resets the page
# and wipes the generated output.
if "result" not in st.session_state:
    st.session_state.result = None

if "post_text" not in st.session_state:
    st.session_state.post_text = ""

if "launch_stage" not in st.session_state:
    st.session_state.launch_stage = ""

if "ctx" not in st.session_state:
    st.session_state.ctx = {}

if "output_filename" not in st.session_state:
    st.session_state.output_filename = ""

# --- Header ---
st.title("Utopia Studio · Content Agent")
st.caption("Transforms a Granola meeting transcript into a LinkedIn post, follow-up email, and press angle.")

st.divider()

# --- Input Section ---
st.subheader("Input")

uploaded_file = st.file_uploader(
    "Upload a transcript (.txt)",
    type=["txt"]
)

pasted_text = st.text_area(
    "Or paste transcript here",
    height=200,
    placeholder="[09:12] Sara: Ahmed, thanks for making the time..."
)

transcript = None

if uploaded_file is not None:
    transcript = uploaded_file.read().decode("utf-8")
    st.success(f"File loaded: {uploaded_file.name}")

elif pasted_text.strip():
    transcript = pasted_text

# --- Run Button ---
st.divider()

run_button = st.button(
    "Generate Content ✦",
    type="primary",
    use_container_width=True
)

# --- Agent Execution ---
# When the button is clicked, run the agent and store
# everything important in session state.
# Session state survives the reruns caused by other widgets.

if run_button:
    if not transcript:
        st.error("Please provide a transcript — either upload a file or paste text.")
    else:
        with st.spinner("Reading transcript and generating content..."):
            result = run_agent(transcript)

        if "error" in result:
            st.error(f"Agent error: {result['error']}")
            st.code(result.get("raw_response", "No response captured"))
        else:
            # Store everything in session state so it survives
            # future widget interactions (like pasting the Slack URL)
            st.session_state.result = result
            st.session_state.ctx = result.get("extracted_context", {})
            st.session_state.post_text = result.get("linkedin_post", {}).get("text", "")
            st.session_state.launch_stage = result.get("linkedin_post", {}).get("launch_stage", "")

            # Auto-save to JSON — do this once at generation time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.output_filename = f"output_{timestamp}.json"
            with open(st.session_state.output_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

# --- Output Display ---
# This block runs on every rerun — but only shows content
# if session state has a result stored.
# This is the key fix: display is decoupled from the button click.

if st.session_state.result is not None:
    result = st.session_state.result
    # Pull from session state into a local variable for clean access.
    # Every reference below uses this local 'result' —
    # no other changes needed in the display code.

    st.success("Content generated.")
    st.divider()

    # --- Extracted Context ---
    ctx = st.session_state.ctx

    with st.expander("What the agent understood about this meeting"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Attendee:** {ctx.get('key_attendee_name', 'Unknown')}")
            st.markdown(f"**Role:** {ctx.get('key_attendee_role', 'Unknown')}")
        with col2:
            st.markdown(f"**Topic:** {ctx.get('topic', 'Unknown')}")
            st.markdown(f"**Key moment:** {ctx.get('most_interesting_moment', 'Unknown')}")

    st.divider()
    st.subheader("Generated Content")

    col_li, col_email, col_press = st.columns(3)

    # -- LinkedIn Post --
    with col_li:
        st.markdown("#### LinkedIn Post")

        li = result.get("linkedin_post", {})
        launch_stage = li.get("launch_stage", "")
        word_count = li.get("word_count", "")
        st.caption(f"LAUNCH stage: **{launch_stage}** · {word_count} words")

        post_text = li.get("text", "")
        st.text_area(
            "Post text",
            value=post_text,
            height=300,
            key="li_output"
        )

        first_line = li.get("first_line", "")
        if first_line:
            st.caption(f"**Opening line:** {first_line}")

    # -- Follow-up Email --
    with col_email:
        st.markdown("#### Follow-up Email")

        email = result.get("follow_up_email", {})
        subject = email.get("subject", "")
        body = email.get("body", "")
        hook = email.get("personalization_hook", "")

        st.markdown(f"**Subject:** {subject}")
        st.text_area(
            "Email body",
            value=body,
            height=300,
            key="email_output"
        )
        if hook:
            st.caption(f"**Personalization:** {hook}")

    # -- Press Angle --
    with col_press:
        st.markdown("#### Press Angle")

        press = result.get("press_angle", {})
        angle_type = press.get("angle_type", "")
        sentence = press.get("sentence", "")

        st.caption(f"Angle type: **{angle_type}**")
        st.text_area(
            "Press angle",
            value=sentence,
            height=300,
            key="press_output"
        )
        st.caption("One sentence · for journalist pitch")

    st.divider()

    # --- Download Button ---
    st.caption(f"Output auto-saved to `{st.session_state.output_filename}`")
    st.download_button(
        label="Download JSON output",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name=st.session_state.output_filename,
        mime="application/json"
    )

    # --- Raw JSON Expander ---
    with st.expander("Raw JSON output (for agent handoff)"):
        st.json(result)

    # --- Slack Integration ---
    # Placed outside the run_button block so it always renders
    # when output exists — pasting the URL won't wipe the output.
    st.divider()
    st.subheader("Send to Slack")

    slack_webhook = st.text_input(
        "Slack Webhook URL (optional)",
        type="password",
        placeholder="https://hooks.slack.com/services/...",
        help="Paste your Slack Incoming Webhook URL to post the LinkedIn draft to a channel."
    )

    if slack_webhook:
        if st.button("Send LinkedIn post to Slack"):
            from slack_sender import send_to_slack
            success = send_to_slack(
                webhook_url=slack_webhook,
                post_text=st.session_state.post_text,
                launch_stage=st.session_state.launch_stage,
                attendee=st.session_state.ctx.get("key_attendee_name", "Unknown"),
                topic=st.session_state.ctx.get("topic", "Unknown")
            )
            if success:
                st.success("Posted to Slack.")
            else:
                st.error("Slack post failed. Check your webhook URL.")