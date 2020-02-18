from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from app.models import User, Question
from . import main
from .. import db

@main.route("/")
def index():
    return render_template('index.html')


#受け取った質問一覧表示
@main.route("/recieved")
def show_recieved():
    user = current_user
    if user.is_authenticated:
        all_questions = user.questions
        questions_recieved = []
        for q in all_questions:
            if q.recieve_id == user.id:
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

"""自分宛以外の質問にも答えられるがそれは宛られたUserが答えてから可能となる
未回答の質問は公開されないので"""

#送った質問一覧表示
@main.route("/send")
def show_send():
    user = current_user
    if user.is_authenticated:
        all_questions = user.questions
        questions_send = []
        for q in all_questions:
            if q.send_id == user.id:
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
@main.route("/user/<user_id>")
def question(user_id):
    user = current_user
    if user.is_authenticated:
        profile_user = User.query.filter_by(user_id=user_id).first()
        if profile_user is None:
            return render_template('error/404.html')
        else:
            return render_template('show_user.html', profile_user=profile_user)
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

#質問を送る処理
@main.route("/send_question", methods=['POST'])
def send_question():
    send_user = current_user
    if send_user.is_authenticated:
        if request.form['body']:

            recieve_user_id = request.form['recieve_user_id']
            recieve_user = User.query.filter_by(id=recieve_user_id).first()

            new_question = Question(body=request.form['body'])
            new_question.send_id = send_user.id
            new_question.users.append(send_user)
            new_question.recieve_id = recieve_user.id
            new_question.users.append(recieve_user)
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for('main.show_send'))
        else:
            pass
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

