from datetime import datetime
from apps.app import db

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    theme = db.Column(db.String)
    q_answers = db.Column(db.String, nullable=False)
    answer = db.Column(db.String)
    answer_id = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)