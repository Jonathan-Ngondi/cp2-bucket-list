import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
# from app.v1 import models

app = create_app(config_name=os.getenv('APP_SETTINGS'))
manager = Manager(app)

    

@manager.command
def create_db(name):
    """Creates database with tables"""
    os.system('createdb {}'.format(name))
    db.create_all()
    db.session.commit()

@manager.command
def drop_db(name):
    """Deletes a database"""
    os.system('dropdb {}'.format(name))


migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
