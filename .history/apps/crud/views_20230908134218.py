from flask import Blueprint,render_template,redirect,url_for
#dbをimportする
from apps.app import db
#Userクラスをimportする
from apps.crud.models import User
from apps.crud.forms import UserForm
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