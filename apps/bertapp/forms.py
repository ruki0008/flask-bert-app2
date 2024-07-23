from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length

class SearchForm(FlaskForm):
    answer_id = StringField(
        'お題ID',
        validators=[
            DataRequired('お題IDを入力してください。')
    ])
    submit = SubmitField('検索')

class ItemForm(FlaskForm):
    item = StringField('Item', validators=[
        DataRequired(),
        Length(1, 50, '50文字以内で入力してください。')])

class RegisterForm(FlaskForm):
    theme = StringField(
        'お題',
        validators=[
            DataRequired('お題は必須です。'),
            Length(1, 30, '30文字以内で入力してください。')
        ]
    )
    answer = StringField(
        'お題の答え',
        validators=[
            DataRequired('お題の答えは必須です。'),
            Length(1, 30, '30文字以内で入力してください。')
        ]
    )
    items = FieldList(FormField(ItemForm), min_entries=1, max_entries=50)
    submit = SubmitField('登録')