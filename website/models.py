from flask_login import UserMixin
from bson import ObjectId

class Note:
    def __init__(self, data, date, user_id):
        self.id = ObjectId()
        self.data = data
        self.date = date
        self.user_id = user_id

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.password = user_data['password']
        self.first_name = user_data['first_name']
        self.notes = [Note(**note) for note in user_data.get('notes', [])]
    def get_id(self):
        return self.id