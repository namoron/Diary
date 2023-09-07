from datetime import datetime

from apps.app import db
from werkzeug.security import generate_password_hash

# db.Modelを継承したUserクラスを作成
class User(db.Model):
    # テーブル名を指定する
    __tablename__ = "users"
    # カラムを定義する