import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from apps.app import db
from apps.crud.models import User
from sqlalchemy import desc, asc
# UploadDiaryFormをimportする
from apps.diary.forms import UploadDiaryForm,UpdateDiaryForm,SearchDiaryForm
from apps.diary.models import UserImage
from datetime import datetime, timedelta
from flask_paginate import Pagination, get_page_parameter
from flask import (
    Flask,
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
    flash
)

# login_required, current_userをimportする
from flask_login import current_user, login_required

# template_folderを指定する（staticは指定しない）
dt = Blueprint("diary", __name__, template_folder="templates")
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
     # 日記データに曜日を追加
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  # 曜日を計算して追加
    return diaries

def sort_diary_ascending():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .order_by(asc(UserImage.date))  # ここで日付が昇順にソート
        .all()
    )
     # 日記データに曜日を追加
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  # 曜日を計算して追加
    return diaries

# すべての日付を返す
def get_existent_dates():
    exist_dates =[]
    diaries = (
        db.session.query(UserImage.date)
        .join(User)
        .order_by(UserImage.date)
    )
    exist_dates = [date[0] for date in diaries.distinct()]
    return exist_dates
# 最新の日付を返す
def get_latest_date():
    latest_date = (
        db.session.query(UserImage.date)
        .join(User)
        .order_by(UserImage.date.desc())  # 降順に並べ替える
        .first()
    )
    if latest_date:
        latest_date = latest_date[0]  # latest_dateを日付オブジェクトに変換
        next_date = latest_date + timedelta(days=1)  # 1日を加算
        return next_date
    else:
        return None

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新しいものが先に来るように修正
    form = UploadDiaryForm()
    diaries = sort_diary()
    return render_template("diary/index.html",current_date=current_date,current_day=current_day ,diaries=diaries,form=form)


@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@dt.route("/upload", methods=["GET", "POST"])
# ログイン必須とする
@login_required
def upload_image():

    # UploadDiaryFormを利用してバリデーションをする
    form = UploadDiaryForm()
    exist_dates = get_existent_dates()
    latest_date = get_latest_date()
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
        return redirect(url_for("diary.index"))
    return render_template("diary/upload.html", form=form,exist_dates=exist_dates,latest_date=latest_date)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/all")
@login_required
def all_diary():
    # UserとUserImageをJoinして画像一覧を取得する
    # ソート順を日付が新    しいものが先に来るように修正
    diaries = sort_diary()
    length = len(diaries)
    # ページネーション
    ## 現在のページ番号を取得
    page = int(request.args.get(get_page_parameter(), 1))
    ## ページごとの表示件数
    per_page = 18
    ## ページネーションオブジェクトを作成
    pagination = Pagination(page=page, per_page=per_page, total=length)
    # 表示するデータを取得
    start = (page - 1) * per_page
    end = start + per_page
    displayed_menu = diaries[start:end]
    return render_template("diary/all.html",current_date=current_date,length=length, diaries=displayed_menu, pagination=pagination)


@dt.errorhandler(404)
def page_not_found(e):
    return render_template("diary/404.html"),404


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
        return render_template("diary/search.html", current_date=current_date, current_day=current_day, diaries=diaries, search_term=search_term,form=form)
    return render_template("diary/search.html", current_date=None, current_day=None, diaries=None, search_term=None,form=form)

# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/table/full")
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

    return render_template("diary/full.html", current_date=current_date, current_day=current_day, diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)

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
    return render_template('diary/table.html',date_year=date_year, current_date=current_date, current_day=current_day, diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)

@dt.route("/diaries/<string:date>")
@login_required
def view_diaries(date):
    target_date = datetime.strptime(date, "%Y-%m-%d").date()  # 文字列から日付オブジェクトに変換
    diary = (
            db.session.query(User, UserImage)
            .join(UserImage)
            .filter(User.id == UserImage.user_id)
            .filter(target_date == UserImage.date)
            .order_by(desc(UserImage.date))
            .first()
        )
    return render_template('diary/single.html',diary=diary)


@dt.route("/diaries/<string:date>/edit", methods=["GET", "POST"])
@login_required
def edit_diary(date):
    target_date = datetime.strptime(date, "%Y-%m-%d").date()

    form = UpdateDiaryForm()

    # GETリクエストの場合、データベースから日記データを取得
    diary = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .filter(target_date == UserImage.date)
        .first()
    )
    if request.method == 'POST':
        # フォームから新しいテキストと日付を取得
        new_diary_text = form.diary_text.data
        new_date = form.date.data
    
        # 日記の属性を更新
        diary.UserImage.diary_text = new_diary_text
        diary.UserImage.date = new_date

        # アップロードされた画像ファイルを取得する
        file = form.image.data
        if file:
            # ファイルのファイル名と拡張子を取得し、ファイル名をuuidに変換する
            ext = Path(file.filename).suffix
            image_uuid_file_name = str(uuid.uuid4()) + ext

            # 画像を保存する
            image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
            file.save(image_path)

            diary.UserImage.image_path = image_uuid_file_name
        
        # データベースを更新
        db.session.commit()
    
        return redirect(url_for('diary.view_diaries', date=new_date)) # 日記一覧ページにリダイレクト
    

    return render_template('diary/edit.html', diary=diary, form=form)  # 日記編集フォームを表示
