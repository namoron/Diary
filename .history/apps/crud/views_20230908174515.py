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

@crud.route("/users/new",methods=["GET","POST"])
def create_user():
    #UserForm をインスタンス化
    form = UserForm()
    #フォーム値をバリデート
    if form.validate_on_submit():
        # ユーザーを作成する
        user = User(
            username = form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        # ユーザーを追加してコミットする
        db.session.add(user)
        db.session.commit()
        #ユーザーの一覧画面へリダイレクト
        return redirect(url_for("crud.users"))

    return render_template("crud/create.html",form=form)

@crud.route("/users")
def users():
    """ユーザーの一覧を取得する"""
    users = User.query.all()
    return render_template("crud/index.html",users=users)

# methodにGETとPOSTを指定する
@crud.route("/users/</user_id>",method=["GET","POST"])
def edit_user(user_id):
    form =UserForm()

    #Userモデルを利用してユーザーを取得する
    user=User.query.filter_by(id=user_id).first()

    #formからサブミットされた場合はユーザーを更新しユーザーの一覧画面へリダイレクト
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.user"))

    # GETの場合はHTMLを返す
    return render_template ("crud/edit.html",user=user,form=form)