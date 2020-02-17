from flask_script import Shell, Manager, Server
from flask_migrate import MigrateCommand, Migrate
from app.models import User, UserQuestion, Question
from app import create_app, db
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app()

manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Question=Question, UserQuestion=UserQuestion)

migrate = Migrate(app, db)

port = int(os.environ.get("PORT", 5000))
server = Server(host='0.0.0.0', port=port)

manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', server)

if __name__ == "__main__":
    manager.run()


