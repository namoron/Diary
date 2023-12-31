import logging
# ログの出力名を設定（1）
logger = logging.getLogger('LoggingTest')

# ログをコンソール出力するための設定（2）
sh = logging.StreamHandler()
logger.addHandler(sh)

# log関数でログ出力処理（3）
# logger.log(20, 'info')
# logger.log(30, 'warning')
# logger.log(100, 'test')
import uuid,os
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
import time

# login_required, current_userをimportする
from flask_login import current_user, login_required

# template_folderを指定する（staticは指定しない）
dt = Blueprint("diary", __name__, template_folder="templates")
#今日の日付
current_date = datetime.now().strftime('%Y-%m-%d')
#今日の曜日
current_day = datetime.now().strftime('%a')

#投稿順にソートする
def sort_upload():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id) # ユーザーIDが一致するものを結合
        .filter(User.id == current_user.id)# ログインユーザーのみの日記を表示
        .order_by(desc(UserImage.created_at))  # 投稿順にソート
        .all()
    )
     # 日記データに曜日を追加
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  # 曜日を計算して追加
    return diaries
#編集順にソートする
def sort_update():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id) # ユーザーIDが一致するものを結合
        .filter(User.id == current_user.id)# ログインユーザーのみの日記を表示
        .order_by(desc(UserImage.updated_at))  # 投稿順にソート
        .all()
    )
     # 日記データに曜日を追加
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  # 曜日を計算して追加
    return diaries
#降順にソートする
def sort_diary():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id) # ユーザーIDが一致するものを結合
        .filter(User.id == current_user.id)# ログインユーザーのみの日記を表示
        .order_by(desc(UserImage.date))  # 降順にソート
        .all()
    )
     # 日記データに曜日を追加
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  # 曜日を計算して追加
    return diaries

#昇順にソートする
def sort_diary_ascending():
    diaries = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .filter(User.id == current_user.id)
        .order_by(asc(UserImage.date))  # 昇順にソート
        .all()
    )
    for diary in diaries:
        if diary.UserImage.date:
            diary.UserImage.day_of_week = diary.UserImage.date.strftime('%a')  
    return diaries

# すべての日付を返す
def get_existent_dates():
    exist_dates =[]
    diaries = (
        db.session.query(UserImage.date)
        .filter(User.id == UserImage.user_id)
        .filter(User.id == current_user.id)
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
        .filter(User.id == UserImage.user_id)       
        .filter(User.id == current_user.id)
        .order_by(UserImage.date.desc())  # 降順に並べ替える
        .first()
    )
    if latest_date:
        latest_date = latest_date[0]  # latest_dateを日付オブジェクトに変換
        next_date = latest_date + timedelta(days=1)  # 1日を加算
        return next_date
    else:
        return None

def getAll():
    diaries = sort_diary()
    diaries_by_year_and_month = {}
    for diary in diaries:
        year = diary.UserImage.date.year
        month = diary.UserImage.date.month
        diaries_by_year_and_month.setdefault(year, {}).setdefault(month, []).append(diary)

    year_days = {year: sum(len(month_diaries) for month_diaries in months.values()) for year, months in diaries_by_year_and_month.items()}
    return (diaries_by_year_and_month, year_days)
def getAllas():
    diaries = sort_diary_ascending()
    diaries_by_year_and_month = {}
    for diary in diaries:
        year = diary.UserImage.date.year
        month = diary.UserImage.date.month
        diaries_by_year_and_month.setdefault(year, {}).setdefault(month, []).append(diary)

    year_days = {year: sum(len(month_diaries) for month_diaries in months.values()) for year, months in diaries_by_year_and_month.items()}
    return (diaries_by_year_and_month, year_days)
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
#ログインが必要
@login_required
def index():
    # UserとUserImageをJoinして画像一覧を取得する
    form = UploadDiaryForm()
    diaries = sort_diary()
    return render_template("diary/index.html",current_date=current_date,current_day=current_day ,diaries=diaries,form=form)

#画像を表示するルート
@dt.route("/images/<path:filename>")
@login_required
def image_file(filename):
    user_id = current_user.id 
    user_directory = os.path.join(current_app.config["UPLOAD_FOLDER"], str(user_id))
    return send_from_directory(user_directory, filename)

#日記をアップロードするルート
@dt.route("/upload", methods=["GET", "POST"])
@login_required
#日記をアップロード
def upload_diary():
    form = UploadDiaryForm()
    exist_dates = get_existent_dates()
    latest_date = get_latest_date()
    date = form.date.data
    diary_text = form.diary_text.data

    if form.validate_on_submit():
        if date in exist_dates:
            flash('その日付の日記は既に存在します', 'error')
            return  redirect(url_for("diary.edit_diary",date= date))
        else:
            if form.image.data is not None:
                # 画像がアップロードされている場合の処理
                user_directory = os.path.join(current_app.config["UPLOAD_FOLDER"], str(current_user.id))
                os.makedirs(user_directory, exist_ok=True)
                file = form.image.data
                ext = Path(file.filename).suffix
                image_uuid_file_name = str(uuid.uuid4()) + ext
                image_path = os.path.join(user_directory, image_uuid_file_name)
                file.save(image_path)

                # DBに保存する
                diary = UserImage(user_id=current_user.id, image_path=image_uuid_file_name, date=date, diary_text=diary_text)
            else:
                # 画像がアップロードされていない場合の処理
                diary = UserImage(user_id=current_user.id, image_path=None, date=date, diary_text=diary_text)

            db.session.add(diary)
            db.session.commit()
            return redirect(url_for("diary.all_diary"))
    return render_template("diary/upload.html", form=form, exist_dates=exist_dates, latest_date=latest_date)

#日付を降順にして表示するルート
@dt.route("/all")
@login_required
def all_diary():
    diaries = sort_update()
    # 日記の総数を取得
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
        # SQLiteデータベースから日記を検索するクエリを実行
        diaries = (
            db.session.query(User, UserImage)
            .join(UserImage)
            .filter(User.id == UserImage.user_id)
            .filter(User.id == current_user.id)
            .order_by(desc(UserImage.date))
        )
        search_term = request.form.get("search_term")
        search_date_str = request.form.get("search_date")
        if not search_date_str or search_term:
            flash("どちらかを選択してください", "danger")
            return redirect(url_for("diary.search_diary"))
        if search_date_str:
            try:
                search_date = datetime.strptime(search_date_str, "%Y-%m-%d").date()
                diaries = diaries.filter(UserImage.date == search_date)
            except ValueError:
                return redirect(url_for("search_diary"))
        if search_term:
            diaries = diaries.filter(UserImage.diary_text.like(f"%{search_term}%"))
        diaries = diaries.order_by(desc(UserImage.date)).all()
        return render_template("diary/search.html", current_date=current_date, current_day=current_day, diaries=diaries, search_term=search_term,form=form,search_date=search_date)
    return render_template("diary/search.html", current_date=None, current_day=None, diaries=None, search_term=None,form=form)

@dt.route("/table")
@login_required
def table_diary():
    diaries_by_year_and_month, year_days = getAll()
    return render_template('diary/table.html', diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)

@dt.route("/table/full")
@login_required
def full_diary():
    diaries_by_year_and_month, year_days = getAllas()
    return render_template("diary/full.html", diaries_by_year_and_month=diaries_by_year_and_month,
    year_days=year_days)

@dt.route("/table/<int:date_year>")
@login_required
def tableY_diary(date_year):
    diaries_by_year_and_month, year_days = getAllas()
    return render_template('diary/tableY.html', date_year=date_year, diaries_by_year_and_month=diaries_by_year_and_month, year_days=year_days)

@dt.route("/diaries/<string:date>")
@login_required
def view_diaries(date):
    target_date = datetime.strptime(date, "%Y-%m-%d").date()  # 文字列から日付オブジェクトに変換
    diary = (
            db.session.query(User, UserImage)
            .join(UserImage)
            .filter(User.id == UserImage.user_id)
            .filter(User.id == current_user.id)
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
        .filter(User.id == current_user.id)
        .filter(target_date == UserImage.date)
        .first()
    )
    if request.method == 'POST':
        if form.delete.data:
            # 削除ボタンがクリックされた場合、日記を削除する
            db.session.delete(diary.UserImage)
            db.session.commit()
            return redirect(url_for('diary.index'))
        # フォームから新しいテキストと日付を取得
        new_diary_text = form.diary_text.data
        new_date = form.date.data
    
        # 日記の属性を更新
        diary.UserImage.diary_text = new_diary_text
        diary.UserImage.date = new_date
        diary.UserImage.updated_at = datetime.now()

        # アップロードされた画像ファイルを取得する
        file = form.image.data
        if file:
            # ファイルのファイル名と拡張子を取得し、ファイル名をuuidに変換する
            ext = Path(file.filename).suffix
            image_uuid_file_name = str(uuid.uuid4()) + ext
            # 画像を保存する
            user_directory = os.path.join(current_app.config["UPLOAD_FOLDER"], str(current_user.id))
            os.makedirs(user_directory, exist_ok=True)
            image_path = os.path.join(user_directory, image_uuid_file_name)
            file.save(image_path)
            diary.UserImage.image_path = image_uuid_file_name
        # データベースを更新
        db.session.commit()
    
        return redirect(url_for('diary.view_diaries', date=new_date)) # 日記一覧ページにリダイレクト
    

    return render_template('diary/edit.html', diary=diary, form=form)  # 日記編集フォームを表示

@dt.route("/diaries/<string:date>/delete", methods=["GET"])
@login_required
def delete_diary(date):
    # UserImageを日付を使って取得する
    diary = UserImage.query.filter_by(date=date).first()

    if diary:
        # ユーザーが日記を所有しているか確認
        if diary.user_id == str(current_user.id):
            try:
                # 削除処理
                db.session.delete(diary)
                db.session.commit()
                flash('日記が削除されました')
            except Exception as e:
                db.session.rollback()
                flash('日記の削除中にエラーが発生しました')
                logger.error('削除エラー: %s', str(e))
        else:
            flash('この日記を削除する権限がありません')
    else:
        flash('指定された日記が見つかりません')
    return redirect(url_for("diary.index"))
    
@dt.route("/flash")
@login_required
def crudFlash():
    return render_template("diary/flash.html")