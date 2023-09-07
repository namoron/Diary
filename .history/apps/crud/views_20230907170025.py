from flask import Blueprint,render_template
#dbをimportする
from apps.app import db
#Userクラスをimportする
from apps.crud.models import User

# Blueprintでcrudアプリを生成する
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)

# indexエンドポイントを作成しindex.htmlを返す
@crud.route("/")
def index():
    return render_template("crud/index.html")  

@crud.route("/sql")
def sql():
    db.session.query(User).all()
    return "コンソールログを確認してください"