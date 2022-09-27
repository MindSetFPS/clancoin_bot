from ast import operator
from operator import eq, add
from dotenv import load_dotenv
from supabase.client import Client, create_client
import os
import sys

if sys.argv[1] == "dev":
    load_dotenv('.env.development')
elif sys.argv[1] == "prod":
    load_dotenv('.env.production')

url = os.getenv("url")
key = os.getenv("public")

supabase: Client = create_client(url, key)

def find_or_create_user(user):
    data = supabase.table("discord_user").select("*").eq("discordUser", user).execute()
    user_exists = len(data.data) > 0

    if user_exists:
        return
    else:
        supabase.table("discord_user").insert({"discordUser": user}).execute()
        
def set_new_balance(user, price, operation):
    data = get_user_coins(user)
    balance = data.data[0]["coins"]

    print("old balance", balance)
    print("price ", price)
    new_balance = operation(balance, price)
    print("new balance: ", new_balance)
    supabase.table("discord_user").update({"coins": int(new_balance)}).eq(column="discordUser", value=user).execute()

def new_transaction(sent_by, received_by, amount, transaction_type):
    find_or_create_user(user=received_by)
    supabase.table("transaction").insert({"transaction_type": transaction_type, "amount" : amount, "sent_by": sent_by, "received_by": received_by}).execute()
    set_new_balance(user=received_by, price=amount, operation=add)

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
    find_or_create_user(user=user)
    coins = supabase.table("discord_user").select("coins").eq("discordUser", user).execute()
    return coins

def create_new_store_item(payload):
    supabase.table("item").insert(payload).execute()

def create_new_prediction(text, option0, option1, prize):
    data = supabase.table("prediction").insert({"text": text, "option0": option0, "option1": option1, "prize": prize}).execute()
    return data.data

def create_users_prediction_pick(prediction_id, pick, user):
    return supabase.table("prediction_pick").insert({"prediction": prediction_id, "pick": pick, "user": user}).execute()

def set_prediction_correct_answer(winner, id):
    supabase.table("prediction").update({"winner": winner }).eq("id", id).execute()

def user_has_already_picked(user: str, prediction_id: int):
    query = supabase.table("prediction_pick").select("*").match({"user": user, "prediction": int(prediction_id)}).execute()
    print(f'Searching user: {user}, prediction_id: {type(prediction_id)}')
    print(query.data)
    print(len(query.data) > 0)
    return len(query.data) > 0

def get_predictors(prediction_id: int, pick: int ):
    query = supabase.table("prediction_pick").select("*").match({"prediction": prediction_id, "pick": pick}).execute()
    print(query.data)
    return query.data

def set_prediction_transaction(transaction_type, amount, sent_by, received_by):
    supabase.table("transaction").insert({"transaction_type": transaction_type, "amount": amount, "sent_by": sent_by, "received_by": received_by}).execute()

def create_prediction_entry_transaction(sent_by, received_by, amount, transaction_type):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

def insert_daily_transaction(sent_by, received_by, amount):
    new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="daily_reward")