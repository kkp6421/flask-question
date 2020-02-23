from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from app.models import User, Question, UserQuestion
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
        all_questions_recieved = Question.query.filter_by(recieve_id=user.id).all() #受け取った全ての質問
        questions_recieved_answered = [] #答えた質問
        questions_recieved_not_answered = [] #答えてない質問
        for q in all_questions_recieved:
            for i in range(len(q.user_question)):
                if q.user_question[i].answer_body is None and q.user_question[i].user_id == user.id:
                    questions_recieved_not_answered.append(q)
                elif q.user_question[i].answer_body is not None and q.user.question[i].user_id == user.id:
                    questions_recieved_answered.append(q)
                else:
                    pass
        return render_template('show_recieved.html',
                               user=user,
                               questions_recieved_answered=questions_recieved_answered,
                               questions_recieved_not_answered=questions_recieved_not_answered
                               )
    else:
        flash("ログインしてください。", "danger")
        return redirect(url_for('main.index'))

"""自分宛以外の質問にも答えられるがそれは宛られたUserが答えてから可能となる
未回答の質問は公開されないので"""

#質問の詳細表示
@main.route("/question/<id>")
def show_question(id):
    user = current_user
    if user.is_authenticated:
        question = Question.filter_by(id=int(id)).first()
        return render_template('show_question.html', question=question)
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))


#userの詳細表示
@main.route("/user/<screen_name>")
def show_user(screen_name):
    user = current_user
    if user.is_authenticated:
        profile_user = User.query.filter_by(screen_name=screen_name).first()
        if profile_user is None:
            return render_template('error/404.html')
        else:
            all_questions_send = Question.query.filter_by(send_id=profile_user.id).all() #送った全ての質問
            questions_send_answered = [] #答えられたして質問
            questions_send_not_answered = [] #答えられてない質問
            for q in all_questions_send:
                for i in range(len(q.user_question)):
                    if q.user_question[i].answer_body is None:
                        questions_send_not_answered.append(q)
                    elif q.user_question[i].answer_body is not None:
                        questions_send_answered.append(q)
                    else:
                        pass
            return render_template('show_user.html',
                                   profile_user=profile_user,
                                   questions_send_not_answered=questions_send_not_answered,
                                   questions_send_answered=questions_send_answered)
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

#質問を送る処理
#recive_userだけQuestionとrelationする。
@main.route("/send_question", methods=['POST'])
def send_question():
    send_user = current_user
    if send_user.is_authenticated:
        if request.form['body']:
            recieve_user_id = request.form['recieve_user_id']
            recieve_user = User.query.filter_by(id=recieve_user_id).first()
            new_question = Question(body=request.form['body'])
            new_question.send_id = send_user.id
            new_question.recieve_id = recieve_user.id
            #リレーション開始
            user_question = UserQuestion()
            user_question.question = new_question
            recieve_user.user_question.append(user_question)
            db.session.add(recieve_user)
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for("main.show_user", screen_name=send_user.screen_name))
        else:
            pass
    else:
        flash("ログインしてください", "danger")
        return redirect(url_for('main.index'))

