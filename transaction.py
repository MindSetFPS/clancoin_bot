from dotenv import load_dotenv
from supabase.client import Client, create_client
import os

load_dotenv()
url = os.getenv("url")
key = os.getenv("public")

supabase: Client = create_client(url, key)