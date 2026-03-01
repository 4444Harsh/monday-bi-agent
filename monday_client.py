import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
MONDAY_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "API-Version": "2024-01",
    "Content-Type": "application/json"
}

def get_board_schema(board_id: str) -> dict:
    """Fetches the columns of the board so the LLM knows the data structure."""
    query = """
    query ($board_id: [ID!]) {
      boards (ids: $board_id) {
        name
        columns {
          id
          title
          type
        }
      }
    }
    """
    variables = {"board_id": board_id}
    response = requests.post(MONDAY_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()['data']['boards'][0]
    else:
        raise Exception(f"Failed to fetch schema: {response.text}")

def get_board_data(board_id: str) -> list:
    """Fetches the actual items (rows) and their column values from the board."""
    query = """
    query ($board_id: [ID!]) {
      boards (ids: $board_id) {
        items_page (limit: 500) {
          items {
            id
            name
            column_values {
              id
              text
              column {
                title
              }
            }
          }
        }
      }
    }
    """
    variables = {"board_id": [board_id]} 
    response = requests.post(MONDAY_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    
    if response.status_code == 200:
        res_json = response.json()
        
        if "errors" in res_json:
            raise Exception(f"GraphQL Error from Monday.com: {json.dumps(res_json['errors'], indent=2)}")
            
        items = res_json['data']['boards'][0]['items_page']['items']
        
        cleaned_data = []
        for item in items:
            row = {"Item Name": item["name"], "Item ID": item["id"]}
            for col in item["column_values"]:
                # The latest API nests the title inside the 'column' object
                col_title = col["column"]["title"] if col.get("column") else col["id"]
                row[col_title] = col["text"] 
            cleaned_data.append(row)
            
        return cleaned_data
    else:
        raise Exception(f"Failed to fetch data: {response.text}")

# --- QUICK TEST ---
if __name__ == "__main__":
    # Replace these with your actual IDs just for testing
    TEST_BOARD_ID = "5026904073" 
    
    print("Fetching Schema...")
    schema = get_board_schema(TEST_BOARD_ID)
    print(json.dumps(schema['columns'][:3], indent=2)) # Print first 3 columns
    
    print("\nFetching Data...")
    data = get_board_data(TEST_BOARD_ID)
    print(f"Retrieved {len(data)} rows. First row:")
    print(json.dumps(data[0], indent=2))