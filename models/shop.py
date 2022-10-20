from .db import db
from .user import user
from operator import add

class Shop():
    def __init__(self) -> None:
        self.shop_items = db.table('item')
        self.transactions = db.table('transaction')

    def new_transaction(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount, transaction_type):
        user.find_or_create_user(discord_name=received_by, discord_id=received_by_discord_id)
        user.set_new_balance(discord_name=received_by, discord_id=received_by_discord_id, price=amount, operation=add)
        
        self.transactions.insert({
                "transaction_type": transaction_type, 
                "amount" : amount, 
                "sent_by": sent_by, 
                "sent_by_discord_id": sent_by_discord_id,
                "received_by": received_by,
                "received_by_discord_id": received_by_discord_id
        }).execute()
    
    def insert_welcome_gift_transaction(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount):
        
        if self.user_got_welcome_gift(
            received_by=received_by, 
            received_by_discord_id=received_by_discord_id
        ):
            print('This user has already got his welcome gift before.')
        else:
            self.new_transaction(
                sent_by=sent_by, 
                received_by=received_by, 
                sent_by_discord_id=sent_by_discord_id, 
                received_by_discord_id=received_by_discord_id, 
                amount=amount, 
                transaction_type="welcome_gift"
            )

    def insert_promo_reward_transaction(self, sent_by, received_by, sent_by_discord_id, received_by_discord_id, amount, transaction_type):
        self.new_transaction(
            sent_by=sent_by, 
            received_by=received_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type=transaction_type
        )

    def insert_play_reward(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount, transaction_type):
        self.new_transaction(
            sent_by=sent_by, 
            received_by=received_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type=transaction_type
        )

    def insert_item_buy(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount, transaction_type):
        self.new_transaction(
            sent_by=sent_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by=received_by, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type=transaction_type
        )

    def insert_gift_transaction(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount):
        self.new_transaction(
            sent_by=sent_by, 
            received_by=received_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type="gift"
        )

    def insert_frame_transaction(self, sent_by, received_by, sent_by_discord_id, received_by_discord_id, amount):
        self.new_transaction(
            sent_by=sent_by, 
            received_by=received_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type="frame_buy"
        )
    
    def insert_portrait_transaction(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount):
        self.new_transaction(
            sent_by=sent_by, 
            sent_by_discord_id=sent_by_discord_id,
            received_by=received_by, 
            received_by_discord_id=received_by_discord_id,
            amount=amount, 
            transaction_type="portrait_buy"
        )
    
    def insert_daily_transaction(self, sent_by, sent_by_discord_id, received_by, received_by_discord_id, amount):
        self.new_transaction(
            sent_by=sent_by, 
            received_by=received_by, 
            sent_by_discord_id=sent_by_discord_id, 
            received_by_discord_id=received_by_discord_id, 
            amount=amount, 
            transaction_type="daily_reward"
        )
    
    def user_got_welcome_gift(self, received_by, received_by_discord_id):
        already_has_welcome_gift = None        
        find_by_id = self.transactions.select("*").match({
            "transaction_type": "welcome_gift", 
            "received_by_discord_id": received_by_discord_id
        }).execute()

        if len(find_by_id.data) > 0:
            already_has_welcome_gift = True
        else:
            print('find by name')
            find_by_name = self.transactions.select("*").match({
                "transaction_type": "welcome_gift", 
                "received_by": received_by
            }).execute()

            if len(find_by_name.data) > 0:
                already_has_welcome_gift = True 
            else:
                already_has_welcome_gift = False
        return already_has_welcome_gift

    def get_store_items(self):
        return self.shop_items.select("*").execute()

    def create_new_store_item(self, payload):
        self.shop_items.insert(payload).execute()

shop = Shop()