import os
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
print(NOTION_API_TOKEN)  # This will print your token if it's loaded correctly