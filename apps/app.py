from pathlib import Path
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config
from flask_login import LoginManager
#SQLAlchemy  をインスタンス化する
db = SQLAlchemy()
csrf = CSRFProtect()
#LoginManagerをインスタンス化
login_manager = LoginManager()
# login_view属性に未ログイン時にリダイレクトするエンドポイントを指定する
login_manager.login_view = "auth.signup"
#login_message属性にログイン後に表示するメッセージを指定する
# ここでは何も表示しないよう空を指定する
login_manager.login_message = ""
# create_app 関数を作成する
def create_app(config_key):
    # Flaskインスタンス生成
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    #SQLAlchemyとアプリ連携をする
    db.init_app(app)
    # Migrateとアプリを連携する
    Migrate(app,db)
    # login_managerをアプリケーションと連携する
    login_manager.init_app(app)
    
    csrf.init_app(app)
    # crud パッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud,url_prefix="/crud")

    #これから作成するauthパッケージからviewsをimportする
    from apps.auth import views as auth_views

    # resister_blueprint を使いviewsのauth をアプリへ登録する
    app.register_blueprint(auth_views.auth,url_prefix="/auth")

    return app
