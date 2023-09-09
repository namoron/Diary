from flask import Blueprint,render_template
from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage

# template_folderを指定する(static は指定しない
dt = Blueprint("detector",__name__,template_folder="templates")

#dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
def index():
    # UserとUserImageをjoinして画像を取得する
    user_images = ( 
        db.session.query(User,UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )
    return render_template("detector/index.html",user_images=user_images)