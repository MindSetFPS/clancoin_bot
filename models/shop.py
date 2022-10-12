from .db import db
from .user import user
from operator import add

class Shop():
    def __init__(self) -> None:
        self.shop_items = db.table('item')
        self.transactions = db.table('transaction')

    def new_transaction(self, sent_by, received_by, amount, transaction_type):
        user.find_or_create_user(user=received_by)
        user.set_new_balance(user=received_by, price=amount, operation=add)
        self.transactions.insert({"transaction_type": transaction_type, "amount" : amount, "sent_by": sent_by, "received_by": received_by}).execute()
    
    def insert_welcome_gift_transaction(self, sent_by, received_by, amount):
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="welcome_gift")

    def insert_promo_reward_transaction(self, sent_by, received_by, amount, transaction_type):
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

    def insert_play_reward(self, sent_by, received_by, amount, transaction_type):
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

    def insert_item_buy(self, sent_by, received_by, amount, transaction_type):
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)

    def get_store_items(self):
        return self.shop_items.select("*").execute()

    def create_new_store_item(self, payload):
        self.shop_items.insert(payload).execute()

    def insert_gift_transaction(self, sent_by, received_by, amount):
        #do not get cofused with insert_gift_transaction, which gives the user a welcome goodie
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="gift")

    def insert_frame_transaction(self, sent_by, received_by, amount):
        #do not get cofused with insert_gift_transaction, which gives the user a welcome goodie
        self.new_transaction(self, sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="frame_buy")
    
    def insert_portrait_transaction(self, sent_by, received_by, amount):
        #do not get cofused with insert_gift_transaction, which gives the user a welcome goodie
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="portrait_buy")
    
    def insert_daily_transaction(self, sent_by, received_by, amount):
        self.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type="daily_reward")
    
    def user_got_welcome_gift(self, received_by):
        return self.transactions.select("*").match({"transaction_type": "welcome_gift", "received_by": received_by}).execute()

shop = Shop()