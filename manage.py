from flask import session
from flask_script import Shell, Manager, Server
from flask_migrate import MigrateCommand, Migrate
from app.models import User, UserQuestion, Question
from app import create_app, db
import os
from datetime import timedelta

app = create_app(config_name=os.environ.get('FLASK_CONFIG') or 'default')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Question=Question, UserQuestion=UserQuestion)

migrate = Migrate()
migrate.init_app(app, db)

port = int(os.environ.get("PORT", 5000))
server = Server(host='0.0.0.0', port=port)

manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', server)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()


