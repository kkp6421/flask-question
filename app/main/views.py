from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from app.models import User, Question, UserQuestion
from . import main
from .. import db

@main.route("/")
def index():
    return render_template('index.html')


#送った質問一覧表示
@main.route("/send")
def show_send():
    user = current_user
    if user.is_authenticated:
        all_questions_send = Question.query.filter_by(send_id=user.id).all() #送った全ての質問
        questions_send_answered = [] #答えられたして質問
        questions_send_not_answered = [] #答えられてない質問
        for q in all_questions_send:
            for i in range(len(q.user_question)):
                if q.user_question[i].answer_body is None:
                    questions_send_not_answered.append(q)
                    break
                elif q.user_question[i].answer_body is not None:
                    questions_send_answered.append(q)
                    break
                else:
                    pass
        questions_send_answered = list(reversed(questions_send_answered))
        questions_send_not_answered = list(reversed(questions_send_not_answered))
        return render_template('show_send.html',
                                   profile_user=current_user,
                                   questions_send_not_answered=questions_send_not_answered,
                                   questions_send_answered=questions_send_answered
                               )
    else:
        flash("ログインしてください。", "warning")
        return redirect(url_for('main.index'))

@main.route("/recieved")
def show_recieved():
    user = current_user
    if user.is_authenticated:
        all_questions_recieved = Question.query.filter_by(recieve_id=user.id).all() #受け取った全ての質問
        questions_recieved_answered = [] #答えられたして質問
        questions_recieved_not_answered = [] #答えられてない質問
        for q in all_questions_recieved:
            for i in range(len(q.user_question)):
                if q.user_question[i].answer_body is None and q.user_question[i].user_id == user.id:
                    questions_recieved_not_answered.append(q)
                elif q.user_question[i].answer_body is not None and q.user_question[i].user_id == user.id:
                    questions_recieved_answered.append(q)
                else:
                    pass
        questions_recieved_answered = list(reversed(questions_recieved_answered))
        questions_recieved_not_answered = list(reversed(questions_recieved_not_answered))
        return render_template('show_recieve.html',
                                   user=current_user,
                                   questions_recieved_not_answered=questions_recieved_not_answered,
                                   questions_recieved_answered=questions_recieved_answered
                                )
    else:
        flash("ログインしてください。", "warning")
        return redirect(url_for('main.index'))

"""自分宛以外の質問にも答えられるがそれは宛られたUserが答えてから可能となる
未回答の質問は公開されないので"""

#質問の詳細表示
@main.route("/question/<question_id>")
def show_question(question_id):
    user = current_user
    if user.is_authenticated:
        users_answered = []
        users_answered_body = []
        question = Question.query.filter_by(id=int(question_id)).first()
        for user_question in question.user_question:
            if user_question.answer_body is not None:
                user = User.query.filter_by(id=user_question.user_id).first()
                users_answered.append(user)
                users_answered_body.append(user_question.answer_body)
        users_answered_body = list(reversed(users_answered_body))
        users_answered = list(reversed(users_answered))
        return render_template('show_question.html',
                               question=question,
                               users_answered_body=users_answered_body,
                               users_answered=users_answered
                               )
    else:
        flash("ログインしてください", "warning")
        return redirect(url_for('main.index'))


#userの詳細表示
#userが受取った質問も表示
@main.route("/user/<screen_name>")
def show_user(screen_name):
    user = current_user
    if user.is_authenticated:
        profile_user = User.query.filter_by(screen_name=screen_name).first()
        if profile_user is None:
            return render_template('error/404.html')
        else:
            all_questions = Question.query.all() #全ての質問
            questions_recieved_answered = [] #自分宛じゃない質問も含めた答えた質問

            questions_answers = []
            for q in all_questions:
                for i in range(len(q.user_question)):
                    if q.user_question[i].answer_body is not None and q.user_question[i].user_id == profile_user.id:
                        questions_answers.append(q.user_question[i].answer_body)
                        questions_recieved_answered.append(q)
                        break
                    else:
                        pass
            questions_answers = list(reversed(questions_answers))
            questions_recieved_answered = list(reversed(questions_recieved_answered))
            return render_template('show_user.html',
                                    profile_user=profile_user,
                                    questions_recieved_answered=questions_recieved_answered,
                                    questions_answers=questions_answers
                                    )
    else:
        flash("ログインしてください", "warning")
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
            return redirect(url_for("main.show_send"))
        else:
            pass
    else:
        flash("ログインしてください", "warning")
        return redirect(url_for('main.index'))

@main.route("/answer_question", methods=['POST'])
def answer_question():
    user = current_user
    if user.is_authenticated:
        if request.form['answer_body']:
            question_id = request.form['question_id']
            q = Question.query.filter_by(id=question_id).first()
            user_id = request.form['answer_user_id']
            u = User.query.filter_by(id=user_id).first()
            if not u in q.users:
                    user_question = UserQuestion()
                    user_question.question = q
                    u.user_question.append(user_question)
                    db.session.add(u)
                    db.session.commit()

            for i in range(len(u.user_question)):
                if u.user_question[i].question_id == q.id and u.user_question[i].answer_body is None:
                    u.user_question[i].answer_body = request.form['answer_body']
                    db.session.add(u)
                    db.session.commit()
                    return redirect(url_for('main.show_user', screen_name=user.screen_name))
            flash("申し訳ありません。この質問は回答済みです。", "warning")
            return redirect(url_for("main.show_question", question_id=q.id))

    else:
        flash("ログインしてください", "warning")
        return redirect(url_for('main.index'))

