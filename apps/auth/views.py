from flask import Blueprint,render_template

# Blueprint を使ってauthを作成する
auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static"
)

#index エンドポイントを作成する
@auth.route("/")
def index():
    return render_template("auth/index.html")