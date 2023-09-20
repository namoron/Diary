import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from apps.app import db
from apps.crud.models import User
from sqlalchemy import desc  # 追加
# UploadDiaryFormをimportする
from apps.detector.forms import UploadDiaryForm
from apps.detector.models import UserImage
from datetime import datetime  # 日付フィールドを扱うためにdatetimeモジュールをインポート
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

# login_required, current_userをimportする
from flask_login import current_user, login_required

# template_folderを指定する（staticは指定しない）
dt = Blueprint("detector", __name__, template_folder="templates")


# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    #今日の日付
    current_date = datetime.now().strftime('%Y-%m-%d')
    #今日の曜日
    current_day = datetime.now().strftime('%a')
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新しいものが先に来るように修正
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .order_by(desc(UserImage.date))  # ここで日付が新しいものが先に来るようにソート
        .all()
    )
    return render_template("detector/index.html",current_date=current_date,current_day=current_day ,diaries=diaries)


@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@dt.route("/upload", methods=["GET", "POST"])
# ログイン必須とする
@login_required
def upload_image():

    # UploadDiaryFormを利用してバリデーションをする
    form = UploadDiaryForm()
    if form.validate_on_submit():
        # アップロードされた画像ファイルを取得する
        file = form.image.data

        # アップロードされた画像ファイル名から拡張子を取得
        original_filename = secure_filename(file.filename)
        ext = Path(original_filename).suffix

        # 日付データをフォームから取得
        date = form.date.data

        # 日記の文章を取得する
        diary_text = form.diary_text.data

        # 日付をファイル名に追加する（拡張子を含む）
        formatted_date = date.strftime('%Y%m%d')
        image_uuid_file_name = f"{formatted_date}{ext}"

        # 画像を保存する
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        # DBに保存する
        diary = UserImage(user_id=current_user.id, date=date, diary_text=diary_text, image_path=image_uuid_file_name)
        db.session.add(diary)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/all")
@login_required
def all_diary():
    #今日の日付
    current_date = datetime.now().strftime('%Y-%m-%d')
    #今日の曜日
    current_day = datetime.now().strftime('%a')
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新しいものが先に来るように修正
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .order_by(desc(UserImage.date))  # ここで日付が新しいものが先に来るようにソート
        .all()
    )
    return render_template("detector/all.html",current_date=current_date,current_day=current_day ,diaries=diaries)


@dt.errorhandler(404)
def page_not_found(e):
    return render_template("detector/404.html"),404