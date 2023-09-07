from pathlib import Path
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

#SQLAlchemy  をインスタンス化する
db = SQLAlchemy()

# create_app 関数を作成する
def create_app ():
    # flask インスタンス作成
    app = Flask(__name__)
    # アプリ設定をする
    app.config.from_mapping(

SECRET_KEY = "2AZSHss3p5QPbcY2hBsy",

SQLALCHEMY_DATABASE_URI=

f"sqlite:///{Path(_file_).parent.parent/local.sqlite SQLALCHEMY_TRACK_MODIFICATIONS=False

')",

)
    # crud パッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud,url_prefix="/crud")

    return app