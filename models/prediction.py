from .db import db
from .shop import shop

class Prediction():
    def __init__(self) -> None:
        self.predictions = db.table('prediction')
        self.prediction_picks = db.table('prediction_pick')
        pass

    def set_prediction_correct_answer(self, winner, prediction_id):
        self.predictions.update({"winner": winner }).eq("id", prediction_id).execute()  

    def create_users_prediction_pick(self, prediction_id, pick, user):
        return self.prediction_picks.insert({"prediction": prediction_id, "pick": pick, "user": user}).execute()
    
    def user_has_already_picked(self, user: str, prediction_id: int):
        query = self.prediction_picks.select("*").match({"user": user, "prediction": int(prediction_id)}).execute()
        print(f'Searching user: {user}, prediction_id: {type(prediction_id)}')
        print(query.data)
        print(len(query.data) > 0)
        return len(query.data) > 0
    
    def create_new_prediction(self, text, option0, option1, prize):
        data = self.predictions.insert({"text": text, "option0": option0, "option1": option1, "prize": prize}).execute()
        return data.data

    def set_prediction_transaction(self, transaction_type, amount, sent_by, received_by):
        shop.new_transaction(transaction_type=transaction_type, amount=amount, sent_by=sent_by, received_by=received_by)
    
    def create_prediction_entry_transaction(self, sent_by, received_by, amount, transaction_type):
        shop.new_transaction(sent_by=sent_by, received_by=received_by, amount=amount, transaction_type=transaction_type)
    
    def get_predictors(self, prediction_id: int, pick: int ):
        query = self.prediction_picks.select("*").match({"prediction": prediction_id, "pick": pick}).execute()
        print(query.data)
        return query.data

prediction = Prediction()