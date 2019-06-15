from app import create_app

flask_app = create_app('dev')
with flask_app.app_context():
    flask_app.run()