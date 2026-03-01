import streamlit as st
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import monday_client

# Load environment variables
load_dotenv()

# Configure Native Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Configuration ---
# REPLACE THESE WITH YOUR ACTUAL BOARD IDs
DEALS_BOARD_ID = "5026904073"
WORK_ORDERS_BOARD_ID = "5026904079"

# --- Define the Tool ---
# With Gemini, we just write a normal Python function and give it to the AI!
def get_monday_data(board_name: str) -> str:
    """Fetches data from a specific Monday.com board. Use this to get Deals or Work Orders data to answer business questions."""
    
    # Satisfies the "Visible Trace" requirement in Streamlit!
    st.info(f"**Agent Action:** Making live API call for the `{board_name}` board...")
    
    board_id = DEALS_BOARD_ID if board_name == "deals" else WORK_ORDERS_BOARD_ID
    try:
        raw_data = monday_client.get_board_data(board_id)
        st.success(f" Successfully fetched {len(raw_data)} rows. Passing to Gemini for analysis...")
        return json.dumps(raw_data)
    except Exception as e:
        return f"Error: {e}"

# --- App UI Setup ---
st.set_page_config(page_title="Executive BI Agent", page_icon=" ")
st.title(" Monday.com BI Agent")
st.markdown("Ask founder-level questions about Deals and Work Orders.")

with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History"):
        if "messages" in st.session_state:
            st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state["chat_session"]
        st.rerun()

# Initialize Gemini Model & Chat Session
if "chat_session" not in st.session_state:
    system_instruction = """You are an elite Business Intelligence AI agent for company founders. 
    Your job is to answer queries about pipeline health, revenue, and sector performance using live data from Monday.com.
    
    CRITICAL INSTRUCTIONS:
    1. The data is messy. You must handle null values, missing dates, and inconsistent text casing gracefully BEFORE calculating your answers.
    2. If a user asks about revenue or pipelines, fetch the 'deals' board. 
    3. If they ask about execution or billing, fetch the 'work_orders' board. 
    4. If the query requires both, fetch both.
    5. Explain any caveats in the data (e.g., 'Note: 3 deals were missing close dates')."""
    
    # Initialize the model with the tool and instructions
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[get_monday_data], # Pass the tool directly!
        system_instruction=system_instruction
    )
    # Automatic function calling handles the entire AI reasoning loop for us!
    st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
# --- Chat Input ---
if prompt := st.chat_input("Ask a question (e.g., 'How many deals are in the Railways sector?')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. The Status Box (Only for the "Thinking" and Tool actions)
        with st.status("🧠 Gemini is thinking...", expanded=True) as status:
            try:
                response = st.session_state.chat_session.send_message(prompt)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Error Occurred", state="error")
                st.error(f"API Error: {e}")
                st.stop() # Stops the code here if there's an error
        
        # 2. The Final Answer (Placed OUTSIDE the status box so it is directly visible!)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})