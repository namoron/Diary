from datetime import datetime

from apps.app import db


class UserImage(db.Model):
    __tablename__ = "diaries"
    id = db.Column(db.Integer, primary_key=True)
    # user_idはusersテーブルのidカラムを外部キーとして設定する
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    image_path = db.Column(db.String)
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # 新しい日付カラムを追加
    date = db.Column(db.Date, nullable=True)  # 日付データを保存するためにDate型を使用
    # 日記の文章を保存する
    diary_text = db.Column(db.String, nullable=True)
    # 日記の文章のバリデーションを実施する
    def validate_diary_text(self, diary_text):
        if len(diary_text) < 10:
            raise ValidationError("日記の文章は10文字以上で入力してください。")
    def __repr__(self):
        return f"<UserImage {self.id}>"