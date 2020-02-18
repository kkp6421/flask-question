from flask import render_template, redirect, request, url_for, flash
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

#受け取った質問一覧表示
@main.route("/recieved")
def show_recieved():
    user = current_user
    if user.is_authenticated:
        all_questions = user.questions
        questions_recieved = []
        for q in all_questions:
            if q.users[1].id == user.id:
                questions_recieved.append(q)
            else:
                pass
        return render_template('show_recieved.html',
                               user=user,
                               questions_recieved=questions_recieved
                               )
    else:
        flash("ログインしてください。", "danger")
        return redirect(url_for('main.index'))

"""自分宛以外の質問にも答えられるがそれは宛られたUserが答えてから可能となる"""

#送った質問一覧表示
@main.route("/send")
def show_send():
    user = current_user
    if user.is_authenticated:
        all_questions = user.questions
        questions_send = []
        for q in all_questions:
            if q.users[0].id == user.id:
                questions_send.append(q)
            else:
                pass
        return render_template('show_send.html', questions_send=questions_send)
    else:
        flash("ログインしてください。", "danger")
        return redirect(url_for('main.index'))

#質問の詳細表示
@main.route("/question/<id>")
def show_question(id):
    user = current_user
    if user.is_authenticated:
        question = Question.filter_by(id=int(id)).first()
        return render_template('show_question.html')
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))



#userの詳細表示
@main.route("/user/<username>")
def question(username):
    user = current_user
    if user.is_authenticated:
        profile_user = User.query.filter_by(twitter_id=username).first()
        if profile_user is None:
            return render_template('404.html')
        else:
            return render_template('show_user.html', profile_user=profile_user)
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

#質問を送る処理
@main.route("/user/<username>/send_question", methods=['GET', 'POST'])
def send_question(username):
    send_user = current_user
    if send_user.is_authenticated:
        recieve_user = User.query.filter_by(username=username).first()
        if recieve_user is None:
            return render_template('404.html')
        if request.form['body']:
            new_question = Question(body=request.form['body'])
            new_question.users.append(send_user)
            new_question.users.append(recieve_user)
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for(main.index))
        else:
            render_template('send_question.html', send_user=send_user, recieve_user=recieve_user)
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

