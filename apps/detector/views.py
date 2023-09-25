import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from apps.app import db
from apps.crud.models import User
from sqlalchemy import desc, asc
# UploadDiaryFormをimportする
from apps.detector.forms import UploadDiaryForm,SearchDiaryForm
from apps.detector.models import UserImage
from datetime import datetime  # 日付フィールドを扱うためにdatetimeモジュールをインポート
from flask import (
    Flask,
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
)

# login_required, current_userをimportする
from flask_login import current_user, login_required

# template_folderを指定する（staticは指定しない）
dt = Blueprint("detector", __name__, template_folder="templates")
#今日の日付
current_date = datetime.now().strftime('%Y-%m-%d')
#今日の曜日
current_day = datetime.now().strftime('%a')
def sort_diary():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .order_by(desc(UserImage.date))  # ここで日付が新しいものが先に来るようにソート
        .all()
    )
    return diaries

def sort_diary_ascending():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .order_by(asc(UserImage.date))  # ここで日付が昇順にソート
        .all()
    )
    return diaries



# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新しいものが先に来るように修正
    form = UploadDiaryForm()
    diaries = sort_diary()
    return render_template("detector/index.html",current_date=current_date,current_day=current_day ,diaries=diaries,form=form)


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

        # ファイルのファイル名と拡張子を取得し、ファイル名をuuidに変換する
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext

        # 日付データをフォームから取得
        date = form.date.data

        # 日記の文章を取得する
        diary_text = form.diary_text.data

        # # 日付をファイル名に追加する（拡張子を含む）
        # formatted_date = date.strftime('%Y%m%d')
        # image_uuid_file_name = f"{formatted_date}{ext}"

        # 画像を保存する
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        # DBに保存する
        diary = UserImage(user_id=current_user.id, image_path=image_uuid_file_name,date=date,diary_text=diary_text)
        db.session.add(diary)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/all")
@login_required
def all_diary():
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新しいものが先に来るように修正
    diaries = sort_diary()
    return render_template("detector/all.html",current_date=current_date,current_day=current_day ,diaries=diaries)


@dt.errorhandler(404)
def page_not_found(e):
    return render_template("detector/404.html"),404


# 検索ページと検索結果を表示するルート
@dt.route("/", methods=["GET", "POST"])
@login_required
def search_diary():
    form = SearchDiaryForm()
    if request.method == "POST":
        search_term = request.form.get("search_term")
        # SQLiteデータベースから日記を検索するクエリを実行
        diaries = (
            db.session.query(User, UserImage)
            .join(UserImage)
            .filter(User.id == UserImage.user_id)
            .filter(UserImage.diary_text.like(f"%{search_term}%"))  # テキストを検索
            .order_by(desc(UserImage.date))
            .all()
        )
        return render_template("detector/search.html", current_date=current_date, current_day=current_day, diaries=diaries, search_term=search_term,form=form)
    return render_template("detector/search.html", current_date=None, current_day=None, diaries=None, search_term=None,form=form)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/edit/<string:date>", methods=["GET", "POST"])
@login_required
def edit_diary(date):
    form = UploadDiaryForm()
    diaries = (
            db.session.query(User, UserImage)
            .join(UserImage)
            .filter(User.id == UserImage.user_id)
            .filter(date == UserImage.date)
            .all()
        )
    return render_template('detector/edit.html',diaries=diaries,form=form)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/full")
@login_required
def full_diary():
    # UserとUserImageをJoinして画像一覧を取得し、ソート
    diaries = sort_diary_ascending()
    
    # 年ごと、月ごとに日記をグループ化した辞書を作成
    diaries_by_year_and_month = {}
    for diary in diaries:
        year = diary.UserImage.date.year
        month = diary.UserImage.date.month
        if year not in diaries_by_year_and_month:
            diaries_by_year_and_month[year] = {}
        if month not in diaries_by_year_and_month[year]:
            diaries_by_year_and_month[year][month] = []
        diaries_by_year_and_month[year][month].append(diary)

    # 年ごとの日数を計算し、テンプレートに渡す
    year_days = {}
    for year, months in diaries_by_year_and_month.items():
        total_days = 0
        for month, diaries in months.items():
            # 各月の日数を計算して合計に加える
            total_days += len(diaries)
        year_days[year] = total_days

    return render_template("detector/full.html", current_date=current_date, current_day=current_day, diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/table/<int:date_year>")
@login_required
def table_diary(date_year):
    # UserとUserImageをJoinして画像一覧を取得し、ソート
    diaries = sort_diary_ascending()
    
    # 年ごと、月ごとに日記をグループ化した辞書を作成
    diaries_by_year_and_month = {}
    for diary in diaries:
        year = diary.UserImage.date.year
        month = diary.UserImage.date.month
        if year not in diaries_by_year_and_month:
            diaries_by_year_and_month[year] = {}
        if month not in diaries_by_year_and_month[year]:
            diaries_by_year_and_month[year][month] = []
        diaries_by_year_and_month[year][month].append(diary)

    # 年ごとの日数を計算し、テンプレートに渡す
    year_days = {}
    for year, months in diaries_by_year_and_month.items():
        total_days = 0
        for month, diaries in months.items():
            # 各月の日数を計算して合計に加える
            total_days += len(diaries)
        year_days[year] = total_days
    return render_template('detector/table.html',date_year=date_year, current_date=current_date, current_day=current_day, diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)