from .db import db

class User():
    def __init__(self) -> None:
        self.users = db.table('discord_user')
        self.transactions = db.table('transaction')

    def set_new_balance(self, discord_name, discord_id, price, operation):
        data = self.get_user_coins(discord_name=discord_name, discord_id=discord_id)
        balance = data.data[0]["coins"]        
        new_balance = operation(balance, price)
        self.users.update({"coins": int(new_balance)}).eq(column="discordUser", value=discord_name).execute()
    
    def find_or_create_user(self, discord_id, discord_name):

        data = self.users.select("*").eq("discord_id", discord_id).execute()

        user_exists_and_has_id = len(data.data) > 0
        
        if user_exists_and_has_id:
            print("User has a discord_user and discord_Id")
            return
        else:
            data = self.users.select("*").eq("discordUser", discord_name).execute()
            user_exists_but_has_no_id = len(data.data) > 0
            
            if user_exists_but_has_no_id:
                print("Inserting dicord id to existing user.")
                self.users.update({"discord_id": discord_id}).eq("discordUser", discord_name).execute()
                return
            else:
                self.users.insert({"discord_id": discord_id, "discordUser": discord_name}).execute()
    
    def get_user_coins(self, discord_name, discord_id):
        self.find_or_create_user(discord_name=discord_name, discord_id=discord_id)
        coins = self.users.select("coins").eq("discordUser", discord_name).execute()
        return coins

    def get_user_promos(self, discord_id, discord_name):
        self.find_or_create_user(discord_id=discord_id, discord_name=discord_name )
        return self.transactions.select("*").like(column='transaction_type', pattern='promo_%').eq(column='received_by', value=user).execute()
    
user = User()