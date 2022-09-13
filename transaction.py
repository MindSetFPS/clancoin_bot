from dotenv import load_dotenv
from supabase.client import Client, create_client
import os

load_dotenv()
url = os.getenv("url")
key = os.getenv("public")

supabase: Client = create_client(url, key)

def new_transaction(sent_by, received_by, amount, transaction_type):
    supabase.table("transaction").insert({
            "transaction_type": transaction_type, 
            "amount" : amount, 
            "sent_by": sent_by, 
            "received_by": received_by
    }).execute()

def insert_welcome_gift_transaction(sent_by, received_by, amount):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="welcome_gift")

def insert_promo_reward_transaction(sent_by, received_by, amount, transaction_type):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

def insert_play_reward(sent_by, received_by, amount, transaction_type):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

def insert_item_buy(sent_by, received_by, amount, transaction_type):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

def get_store_items():
    return supabase.table("item").select("*").execute()

def get_user_coins(user):
    coins = supabase.table("discord_user").select("coins").eq("discordUser", user).execute()
    return coins
