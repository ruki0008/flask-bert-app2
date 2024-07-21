from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, losses, models, util
import pandas as pd
from torch.utils.data import DataLoader
import torch
import psutil
import os

bertapp = Blueprint(
    'bertapp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

MODEL_NAME = 'apps/bertapp/sbert2'
bert = models.Transformer(MODEL_NAME)
pooling = models.Pooling(bert.get_word_embedding_dimension())
model = SentenceTransformer(modules=[bert, pooling])

answers = ['35歳です。', 'ハンバーガーです。',
           'チェルシーに所属していました。', 'スペインの料理は特に美味しいです。', '右利きです。',
           'レアルマドリードではベンチにいました。', 'ハンバーガー屋さんをやりたいです。', '体重は教えられません。']
corpus_embeddings = model.encode(answers, convert_to_tensor=True)

messages = []

class ItemForm(FlaskForm):
    item = StringField('Item', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    items = FieldList(FormField(ItemForm), min_entries=1, max_entries=20)
    submit = SubmitField('登録')

@bertapp.route('/')
def index():
    return render_template('bertapp/index.html')

@bertapp.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    messages.append(message)
    result = cos_calc(message)
    messages.append(result)
    return jsonify({'status': 'Message received'})

@bertapp.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@bertapp.route('/response_messages', methods=['GET'])
def response_messages():
    return jsonify(messages)

def cos_calc(query):
  query_embedding = model.encode(query, convert_to_tensor=True)
  cos_scores = util.cos_sim(query_embedding, corpus_embeddings)
  top_results =  torch.topk(cos_scores, k=1)
  idx = top_results[1][0]
  return answers[idx]

@bertapp.route('/memory')
def memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    rss_mb = memory_info.rss / 1024 / 1024
    vms_mb = memory_info.vms / 1024 / 1024
    return jsonify({
        'rss': rss_mb,
        'vms': vms_mb,
        'percent': process.memory_percent()
    })

@bertapp.route('/register', methods=['GET', 'POST'])
def register():
    data_list = []
    form = RegisterForm()
    if form.validate_on_submit():
        data_list = [item_form.item.data for item_form in form.items]
        return redirect(url_for('bertapp.index'))
    return render_template('bertapp/register.html', form=form, data_list=data_list)
