from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms import DateField,TextAreaField,StringField, SubmitField
from wtforms.validators import DataRequired


class UploadDiaryForm(FlaskForm):
    # ファイルフィールドに必要なバリデーションを設定する
    # 日付フィールドを追加
    date = DateField("日付")
    diary_text = TextAreaField("日記の文章", validators=[DataRequired("投稿内容は  必須  です")],default="ここに初期テキストを入れる")
    image = FileField(
        validators=[
            FileAllowed(["png", "jpg", "jpeg"], "サポートされていない画像形式です。"),
        ]
    )
    submit = SubmitField("アップロード")
class UpdateDiaryForm(FlaskForm):
    # ファイルフィールドに必要なバリデーションを設定する
    # 日付フィールドを追加
    date = DateField("日付")
    diary_text = TextAreaField("日記の文章")
    image = FileField(
        validators=[
            FileAllowed(["png", "jpg", "jpeg"], "サポートされていない画像形式です。"),
        ]
    )
    submit = SubmitField("アップデート")
    delete = SubmitField("画像を削除")

class SearchDiaryForm(FlaskForm):
    search_term = StringField('Keyword Search', validators=[DataRequired()])
    search_date = DateField('Date Search',format='%Y-%m-%d')
    submit = SubmitField('Search')