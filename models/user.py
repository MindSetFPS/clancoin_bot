from .db import db

class User():
    def __init__(self) -> None:
        self.users = db.table('discord_user')
        self.transactions = db.table('transaction')

    def set_new_balance(self, user, price, operation):
        data = self.get_user_coins(user)
        balance = data.data[0]["coins"]
        
        print("old balance", balance)
        print("price ", price)
        new_balance = operation(balance, price)
        print("new balance: ", new_balance)
        self.users.update({"coins": int(new_balance)}).eq(column="discordUser", value=user).execute()
    
    def find_or_create_user(self, user):
        data = self.users.select("*").eq("discordUser", user).execute()
        user_exists = len(data.data) > 0
        if user_exists:
            return
        else:
            self.users.insert({"discordUser": user}).execute()
    
    def get_user_coins(self, user):
        self.find_or_create_user(user=user)
        coins = self.users.select("coins").eq("discordUser", user).execute()
        return coins

    def get_user_promos(self, user):
        return self.transactions.select("*").like(column='transaction_type', pattern='promo_%').eq(column='received_by', value=user).execute()
    
user = User()