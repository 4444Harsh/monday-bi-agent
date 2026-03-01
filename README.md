# Monday.com Business Intelligence Agent

## Overview
This is a conversational AI Business Intelligence Agent designed for executives. It connects directly to Monday.com via live API calls to answer founder-level queries regarding Deals and Work Orders. 

## Features
- **Conversational UI:** Built with Streamlit for a seamless chat experience.
- **Live Tool Calling:** Powered by Google's Gemini 2.5 Flash native function-calling. No data is cached or preloaded; all queries trigger live GraphQL API requests to Monday.com.
- **Data Resilience:** The LLM is explicitly instructed to handle missing dates, null values, and inconsistent text casing in memory prior to calculating insights, communicating any data caveats directly to the user.
- **Visible Action Traces:** The UI exposes the agent's thought process and API executions in real-time.

## Setup Instructions (Local Testing)
If you wish to run this locally instead of using the provided live hosted link:

1. Clone or extract the repository.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add your keys:
   `GEMINI_API_KEY="your_gemini_key"`
   `MONDAY_API_KEY="your_monday_personal_token"`
4. Run the app:
   `streamlit run app.py`

## Project Structure
- `app.py`: Main Streamlit UI and Gemini tool-calling loop.
- `monday_client.py`: Custom GraphQL wrapper to bypass Monday.com complexity budgets.
- `requirements.txt`: Python dependencies.