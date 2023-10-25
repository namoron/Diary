from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms import DateField,TextAreaField,StringField, SubmitField
from wtforms.validators import DataRequired


class UploadDiaryForm(FlaskForm):
    # ファイルフィールドに必要なバリデーションを設定する
    # 日付フィールドを追加
    date = DateField("日付")
    diary_text = TextAreaField("日記の文章", validators=[DataRequired()])
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

class SearchDiaryForm(FlaskForm):
    search_term = StringField('Search Diary', validators=[DataRequired()])
    submit = SubmitField('Search')