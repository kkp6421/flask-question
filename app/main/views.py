from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required
from app.models import User, Question
from . import main
from .. import db

@main.route("/")
def index():
    return render_template('index.html')

"""
User.questions[0].users[0]の[0]が質問者,[1]が自分宛ての質問、[2:]が自分宛でない質問となる。
question_recievedは質問の送り主に直接指定された質問
"""
@main.route("/recieved")
@login_required
def recieved():
    user = current_user
    if user:
        all_questions = user.questions
        questions_recieved = []
        for q in all_questions:
            if q.users[1].id == user.id:
                questions_recieved.append(q)
            else:
                pass
        return render_template('recieved.html',
                               user=user,
                               questions_recieved=questions_recieved
                               )
    else:
        return render_template('error.html')


@main.route("/send")
@login_required
def questions():
    user = current_user
    if user:
        all_questions = user.questions
        questions_send = []
        for q in all_questions:
            if q.users[0].id == user.id:
                questions_send.append(q)
            else:
                pass
        return render_template('send.html', questions_send=questions_send)
    else:
        return render_template('error.html')

@main.route("/user/<id>")
@login_required
def question(id):
    user = User.query.get(int(id))
    if request.form['body']:
        newQuestion = Question(
            body=request.form['body'],
            profile_image_url=current_user.image_url,
            user_id=current_user.id,
            answer_image_url=user.user_image_url,
            answer_id=user.id
        )
        db.session.add(newQuestion)
        db.session.commit()
        return render_template('index.html')
    else:
        return render_template('error.html')
