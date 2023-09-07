from flask import Flask

# create_app 関数を作成する
def create_app ():
    # flask インスタンス作成
    app = Flask(__name__)
    # crud パッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud,url_prefix="/crud")

    return app