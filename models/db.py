from operator import eq, add
from dotenv import load_dotenv
from supabase.client import Client, create_client
import os
import sys

url = os.getenv("url")
key = os.getenv("public")
        
def create_db():
    supabase: Client = create_client(url, key)
    return supabase

db = create_db()