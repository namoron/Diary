from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms import DateField,TextAreaField


class UploadDiaryForm(FlaskForm):
    # ファイルフィールドに必要なバリデーションを設定する
    # 日付フィールドを追加
    date = DateField("日付")
    diary_text = TextAreaField("日記の文章")
    image = FileField(
        validators=[
            FileRequired("画像ファイルを指定してください。"),
            FileAllowed(["png", "jpg", "jpeg"], "サポートされていない画像形式です。"),
        ]
    )
    submit = SubmitField("アップロード")
