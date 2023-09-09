from flask import Blueprint,render_template

# template_folderを指定する(static は指定しない
dt = Blueprint("detector",__name__,template_folder="templates")

#dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
def index():
    return render_template("detector/index.html")