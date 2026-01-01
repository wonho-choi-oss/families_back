from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # 해싱된 비밀번호 저장
    email = db.Column(db.String(120), unique=True, nullable=False)

    # 실무 포인트: DB 레벨에서 리프레시 토큰 관리
    # 토큰 자체가 길 수 있으므로 Text 타입을 사용하거나 넉넉한 String 사용
    refresh_token = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 가족들과의 관계 설정 (1:N)
    families = db.relationship('FamilyMember', backref='owner', lazy=True)

    # 비밀번호 설정 (암호화)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 비밀번호 확인 (비교)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FamilyMember(db.Model):
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    relationship = db.Column(db.String(50))  # 예: 아빠, 엄마, 동생
    birthday = db.Column(db.Date, nullable=True)

    # 외래키 (어떤 유저의 가족인가?)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class GptUser(db.Model):
    __tablename__ = 'gpt_user'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    chat_list = db.relationship('GptBot', backref='owner', lazy=True)


class GptBot(db.Model):
    __tablename__ = 'gpt_bot'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    worksheet_id = db.Column(db.Integer, db.ForeignKey('gpt_user.id'), nullable=False)


# class GptList(db.Model):
#     __tablename__ = 'gpt_list'
#
#     id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
#     content = db.Column(db.Text, nullable=False)
#     role = db.Column(db.String(50), nullable=False)
#     timestamp = db.Column(db.String(50), nullable=True)
#     worksheet_id = db.Column(db.Integer, db.ForeignKey('gpt_user.id'), nullable=False)

