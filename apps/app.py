from pathlib import Path
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config
#SQLAlchemy  をインスタンス化する
db = SQLAlchemy()
csrf = CSRFProtect()
# create_app 関数を作成する
def create_app(config_key):
    # Flaskインスタンス生成
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    #SQLAlchemyとアプリ連携をする
    db.init_app(app)
    # Migrateとアプリを連携する
    Migrate(app,db)

    csrf.init_app(app)
    # crud パッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud,url_prefix="/crud")

    return app
