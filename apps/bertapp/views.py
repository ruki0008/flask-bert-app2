from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for, flash
from flask_cors import CORS
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_required
from apps.app import db
from apps.crud.models import User
from apps.bertapp.models import UserAnswer
from apps.bertapp.forms import ItemForm, RegisterForm, SearchForm
from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, losses, models, util
import pandas as pd
from torch.utils.data import DataLoader
import torch
import psutil
import os
import random
import string
from flask_socketio import emit
from fuzzywuzzy import fuzz
from apps.app import gv_socketio

bertapp = Blueprint('bertapp', __name__, template_folder='templates', static_folder='static')

MODEL_NAME = 'apps/bertapp/sbert2'
bert = models.Transformer(MODEL_NAME)
pooling = models.Pooling(bert.get_word_embedding_dimension())
model = SentenceTransformer(modules=[bert, pooling])

answers = []
answer = ''
corpus_embeddings = None
input_text = ''

@bertapp.route('/')
@login_required
def index():
    return render_template('bertapp/index.html')

@bertapp.route('/questions/<user_path>')
@login_required
def questions(user_path):
    user_answers = UserAnswer.query.filter_by(user_id=current_user.id)
    return render_template('bertapp/questions.html', user_answers=user_answers)

@bertapp.route('/edit/<user_path>/<answer_id>', methods=['GET', 'POST'])
@login_required
def edit_answer(answer_id, user_path):
    form = RegisterForm()
    answer_edit = UserAnswer.query.filter_by(id=answer_id).first()
    return render_template('bertapp/edit.html', answer_edit=answer_edit, form=form)

@bertapp.route('/edit/<user_path>/<answer_id>/delete', methods=['POST'])
@login_required
def delete_answer(answer_id, user_path):
    answer_del = UserAnswer.query.filter_by(id=answer_id).first()
    db.session.delete(answer_del)
    db.session.commit()
    return redirect(url_for('bertapp.questions', user_path=user_path))

@bertapp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    print(form.answer_id.data)
    if form.validate_on_submit():
        print(form.answer_id.data)
        global input_text
        input_text = form.answer_id.data
        return redirect(url_for('bertapp.question'))
    return render_template('bertapp/search.html', form=form)

@bertapp.route('/question', methods=['GET', 'POST'])
def question():
    if input_text == '' or not UserAnswer.query.filter_by(answer_id=input_text):
        flash('正しいお題のIDを入力してください')
        return redirect(url_for('bertapp.search'))
    useranswer = UserAnswer.query.filter_by(answer_id=input_text).first()
    global answers
    answers = useranswer.q_answers.split(',')
    print(answers)
    global corpus_embeddings
    corpus_embeddings = model.encode(answers, convert_to_tensor=True)
    theme = useranswer.theme
    global answer
    answer = useranswer.answer
    return render_template('bertapp/question.html', theme=theme)

@gv_socketio.on('send_message')
def handle_message(data):
    message = data['message']
    print(f'Received message: {message}')
    response1, score = cos_calc(message)
    response = response1 + ':' + str(score)
    emit('receive_message', {'message': message, 'response': response})

@gv_socketio.on('send_answer')
def handle_answer(data):
    answer_text = data['answer']
    print(f'Received message: {answer_text}')
    prob = name_sim(answer_text, answer)
    if prob >= 75:
        result = f'正解!! 答えは{answer}でした。'
    else:
        result = '不正解です。'
    emit('receive_result', {'answer': answer_text, 'result': result})

def cos_calc(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)
    top_results =  torch.topk(cos_scores, k=1)
    idx = top_results[1][0]
    prob = top_results[0][0].item()
    prob = round(prob, 4)
    if prob >= 0.35:
        res_answer = answers[idx]
    elif prob >= 0.3:
        res_answer = '間違っているかもしれませんが、' + answers[idx]
    elif prob >= 0.2:
        res_answer = 'わかりません。'
    else:
        res_answer = 'まったくわかりません。'
    return res_answer, prob

def name_sim(str1, str2):
    similarity_ratio = fuzz.partial_ratio(str1, str2)
    return similarity_ratio

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
@login_required
def register():
    data_list = []
    form = RegisterForm()
    if form.validate_on_submit():
        theme = form.theme.data
        answer = form.answer.data
        data_list = [item_form.item.data for item_form in form.items]
        data_text = ','.join(data_list)
        answer_id = generate_random_string()
        while True:
            if not UserAnswer.query.filter_by(answer_id=answer_id).first():
                break
            answer_id = generate_random_string

        user_answer = UserAnswer(user_id=current_user.id, theme=theme, q_answers=data_text, answer=answer, answer_id=answer_id)
        db.session.add(user_answer)
        db.session.commit()

        return redirect(url_for('bertapp.questions', user_path=current_user.user_path))
    return render_template('bertapp/register.html', form=form, data_list=data_list)

def generate_random_string(length=15):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
