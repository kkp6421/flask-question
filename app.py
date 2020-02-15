from flask import Flask, render_template, redirect, url_for, session, request
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rauth import OAuth1Service
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.secret_key = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(base_dir, 'data.sqlite')
csrf = CSRFProtect(app)
port = int(os.environ.get("PORT", 5000))
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

service = OAuth1Service(
    name='twitter',
    consumer_key=os.environ.get("consumer_key"),
    consumer_secret=os.environ.get("consumer_secret"),
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    base_url='https://api.twitter.com/1.1/'
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    description = db.Column(db.String(1024))
    user_image_url = db.Column(db.String(1024))
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    twitter_id = db.Column(db.String(64), nullable=False, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()


@app.route("/")
def index():
    msg = {"name": "Tomohiro", "age": 17}
    return render_template('index.html')

@app.route("/help")
def help():
    return render_template('help.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/oauth/twitter')
def oauth_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    else:
        request_token = service.get_request_token(
            params={'oauth_callback': url_for('oauth_callback', provider='twitter',
                                              _external=True)}
        )
        session['request_token'] = request_token
        return redirect(service.get_authorize_url(request_token[0]))

@app.route('/oauth/twitter/callback')
def oauth_callback():
    request_token = session.pop('request_token')
    oauth_session = service.get_auth_session(
        request_token[0],
        request_token[1],
        data={'oauth_verifier': request.args['oauth_verifier']}
    )
    profile = oauth_session.get('account/verify_credentials.json').json()
    twitter_id = str(profile.get('id'))
    username = str(profile.get('name'))
    description = str(profile.get('description'))
    profile_image_url = str(profile.get('profile_image_url'))
    user = db.session.query(User).filter(User.twitter_id == twitter_id).first()
    if user:
        user.twitter_id = twitter_id
        user.username = username
    else:
        user = User(twitter_id=twitter_id,
                    username=username,
                    description=description,
                    user_image_url=profile_image_url)
    db.session.add(user)
    db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)


