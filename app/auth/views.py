from rauth import OAuth1Service
from flask import redirect, session, request, url_for, current_app
from flask_login import logout_user, current_user, login_user
import tweepy
import os
from datetime import timedelta
from app.models import User, db
from . import auth

service = OAuth1Service(
    name='twitter',
    consumer_key=os.environ.get("consumer_key"),
    consumer_secret=os.environ.get("consumer_secret"),
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    base_url='https://api.twitter.com/1.1/'
)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/oauth/twitter')
def oauth_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    else:
        request_token = service.get_request_token(
            params={'oauth_callback': 'https://kkp6421-flask-question.herokuapp.com/oauth/twitter/callback?provider=twitter'}
        )
        session['request_token'] = request_token
        return redirect(service.get_authorize_url(request_token[0]))


friends_ids = []
@auth.route('/oauth/twitter/callback')
def oauth_callback():
    request_token = session.pop('request_token')
    oauth_session = service.get_auth_session(
        request_token[0],
        request_token[1],
        data={'oauth_verifier': request.args['oauth_verifier']}
    )
    profile = oauth_session.get('account/verify_credentials.json').json()
    twitter_id = str(profile.get('id'))
    screen_name = str(profile.get('screen_name'))
    username = str(profile.get('name'))
    description = str(profile.get('description'))
    profile_image_url = str(profile.get('profile_image_url')).replace("normal", "bigger")
    user = db.session.query(User).filter(User.twitter_id == twitter_id).first()
    if user:
        user.twitter_id = twitter_id
        user.username = username
        user.user_image_url = profile_image_url
    else:
        user = User(screen_name=screen_name, twitter_id=twitter_id, username=username, description=description, user_image_url=profile_image_url)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    auth_list = tweepy.OAuthHandler(
        os.environ.get('consumer_key'),
        os.environ.get('consumer_secret')
    )
    auth_list.set_access_token(
        os.environ.get('access_key'),
        os.environ.get('access_secret')
    )
    global friends_ids
    api = tweepy.API(auth_list)
    friends = tweepy.Cursor(api.friends_ids, screen_name=current_user.screen_name, count=4000).pages
    for f in friends():
        friends_ids.extend(f)
    return redirect(url_for('main.index'))
